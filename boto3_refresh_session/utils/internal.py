# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""This module defines the core building blocks used by `RefreshableSession`
and method-specific session classes. The intent is to separate registry
mechanics, credential refresh contracts, and boto3 session behavior so each
concern is clear and testable.

`Registry` is a lightweight class-level registry. Subclasses register
themselves by key at import time, enabling factory-style lookup without
hard-coded class references. This is how `RefreshableSession` discovers method
implementations.

`refreshable_session` is a decorator that wraps `__init__` and guarantees a
`__post_init__` hook runs after `boto3.Session` initialization. This allows
`BRSSession` to create refreshable credentials only after the boto3 Session is
set up, avoiding circular and ordering issues. It also prevents double
wrapping on repeated decoration.

`CredentialProvider` is a small abstract class that defines the contract for
refreshable sessions: implement `_get_credentials` (returns temporary creds)
and `get_identity` (describes the caller identity). The concrete refresh
methods (STS, IoT, custom) only need to satisfy this interface.

`BRSSession` is the concrete wrapper over `boto3.Session`. It owns refreshable
credential construction, wiring the botocore session to those credentials, and
client caching with normalized cache keys. It acts as the base implementation
for session mechanics.

Method-specific classes (STS, custom, IoT X.509) inherit directly from
`Registry`, `CredentialProvider`, and `BRSSession`, which keeps the hierarchy
shallow and the registration mechanics explicit.
"""

__all__ = [
    "BRSSession",
    "CredentialProvider",
    "Registry",
    "refreshable_session",
]

import importlib.util
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, ClassVar, Generic, TypeVar

from boto3.session import Session
from botocore.client import BaseClient
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)

from ..exceptions import BRSCacheError, BRSWarning
from .cache import ClientCache, ClientCacheKey
from .typing import (
    Identity,
    RefreshMethod,
    RegistryKey,
    TemporaryCredentials,
)


class CredentialProvider(ABC):
    """Defines the abstract surface every refreshable session must expose."""

    @abstractmethod
    def _get_credentials(self) -> TemporaryCredentials: ...

    @abstractmethod
    def get_identity(self) -> Identity: ...


T_Registry = TypeVar("T_Registry", bound="Registry[Any, Any]")


class Registry(Generic[RegistryKey, T_Registry]):
    """Lightweight class-level registry for mapping ``RefreshableSession``
    to refresh method implementations.

    Attributes
    ----------
    registry : ClassVar[dict[str, type[Any]]]
        The class-level registry mapping keys to classes.
    """

    registry: ClassVar[dict[str, type[Any]]] = {}

    def __init_subclass__(
        cls: type[T_Registry], *, registry_key: RegistryKey, **kwargs: Any
    ):
        super().__init_subclass__(**kwargs)

        if registry_key in cls.registry:
            BRSWarning.warn(
                f"{registry_key!r} already registered. Overwriting."
            )

        cls.registry[registry_key] = cls


# defining this here instead of utils to avoid circular imports lol
T_BRSSession = TypeVar("T_BRSSession", bound="BRSSession")

#: Type alias for a generic refreshable session type.
BRSSessionType = type[T_BRSSession]


def refreshable_session(
    cls: BRSSessionType,
) -> BRSSessionType:
    """Wraps cls.__init__ of subclasses so self.__post_init__ runs after init
    (if present).

    In plain English: this is essentially a post-initialization hook.

    Returns
    -------
    BRSSessionType
        The decorated class.
    """

    init = cls.__init__

    # avoiding double wrapping
    if getattr(init, "__post_init_wrapped__", False):
        return cls

    @wraps(init)
    def wrapper(self, *args, **kwargs):
        init(self, *args, **kwargs)
        post = getattr(self, "__post_init__", None)

        # calling __post_init__ if it exists
        if callable(post) and not getattr(self, "_post_inited", False):
            post()
            self._post_inited = True

    # flagging wrapper to avoid double wrapping
    wrapper.__post_init_wrapped__ = True  # type: ignore[attr-defined]

    # assigning the wrapper to __init__
    cls.__init__ = wrapper
    return cls


class BRSSession(Session):
    """Wrapper for boto3.session.Session.

    Parameters
    ----------
    refresh_method : RefreshMethod
        The method to use for refreshing temporary credentials.
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.
    advisory_timeout : int, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore will attempt to refresh credentials early according to
        this value (in seconds), but will continue using the existing
        credentials if refresh fails. Default is 15 minutes (900 seconds).
    mandatory_timeout : int, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore requires a successful refresh before continuing. If
        refresh fails in this window (in seconds), API calls may fail.
        Default is 10 minutes (600 seconds).
    cache_clients : bool, optional
        If ``True`` then clients created by this session will be cached and
        reused for subsequent calls to :meth:`client()` with the same
        parameter signatures. Due to the memory overhead of clients, the
        default is ``True`` in order to protect system resources.
    client_cache_max_size : int, optional
        The maximum number of clients to store in the client cache. Only
        applicable if ``cache_clients`` is ``True``. Defaults to 10.

    Attributes
    ----------
    client_cache : ClientCache
        The client cache used to store and retrieve cached clients.
    credentials : TemporaryCredentials
        The current temporary AWS security credentials.

    Methods
    -------
    client(*args, **kwargs) -> BaseClient
        Creates a low-level service client by name.
    get_identity() -> Identity
        Returns metadata about the identity assumed.
    refreshable_credentials() -> TemporaryCredentials
        The current temporary AWS security credentials.
    whoami() -> Identity
        Alias for :meth:`get_identity`.

    Other Parameters
    ----------------
    kwargs : Any
        Optional keyword arguments for initializing boto3.session.Session.
    """

    def __init__(
        self,
        refresh_method: RefreshMethod,
        defer_refresh: bool | None = None,
        advisory_timeout: int | None = None,
        mandatory_timeout: int | None = None,
        cache_clients: bool | None = None,
        client_cache_max_size: int | None = None,
        **kwargs,
    ):
        # initializing parameters
        self.refresh_method: RefreshMethod = refresh_method
        self.defer_refresh: bool = defer_refresh is not False
        self.advisory_timeout: int | None = advisory_timeout
        self.mandatory_timeout: int | None = mandatory_timeout
        self.cache_clients: bool | None = cache_clients is not False
        self.client_cache_max_size: int | None = client_cache_max_size

        # initializing Session
        super().__init__(**kwargs)

        # initializing client cache
        self.client_cache: ClientCache = ClientCache(
            max_size=self.client_cache_max_size
        )

    def __post_init__(self):
        if not self.defer_refresh:
            self._credentials = RefreshableCredentials.create_from_metadata(
                metadata=self._get_credentials(),  # type: ignore[arg-type]
                refresh_using=self._get_credentials,  # type: ignore[arg-type]
                method=self.refresh_method,
                advisory_timeout=self.advisory_timeout,
                mandatory_timeout=self.mandatory_timeout,
            )
        else:
            self._credentials = DeferredRefreshableCredentials(
                refresh_using=self._get_credentials,  # type: ignore[arg-type]
                method=self.refresh_method,  # type: ignore[arg-type]
            )

        # without this, boto3 won't use the refreshed credentials properly in
        # clients and resources, depending on how they were created
        self._session._credentials = self._credentials

    def client(self, *args, **kwargs) -> BaseClient:
        """Creates a low-level service client by name.

        Parameters
        ----------
        *args : Any
            Positional arguments for :meth:`boto3.session.Session.client`.
        **kwargs : Any
            Keyword arguments for :meth:`boto3.session.Session.client`.

        Returns
        -------
        BaseClient
            A low-level service client.

        Notes
        -----
        This method overrides the default
        :meth:`boto3.session.Session.client` method. If client caching is
        enabled, it will return a cached client instance for the given
        service and parameters. Else, it will create and return a new client
        instance.
        """

        # check if caching is enabled
        if self.cache_clients:
            # moving "service_name" to args if present in kwargs
            # helps normalize cache keys . . . very important!!!
            if "service_name" in kwargs:
                args = (kwargs.pop("service_name"),) + args

            # if client exists in cache, return it
            if (
                _cached_client := self.client_cache.get(
                    key := ClientCacheKey(*args, **kwargs)
                )
            ) is not None:
                return _cached_client

            # else initialize it
            client = super().client(*args, **kwargs)

            # attempting to cache and return the client
            try:
                self.client_cache[key] = client
                return client

            # if caching fails, return cached client if possible
            except BRSCacheError:
                return (
                    cached
                    if (cached := self.client_cache.get(key)) is not None
                    else client
                )

        # return a new client if caching is disabled
        else:
            return super().client(*args, **kwargs)

    def refreshable_credentials(self) -> TemporaryCredentials:
        """The current temporary AWS security credentials.

        Returns
        -------
        TemporaryCredentials
            Temporary AWS security credentials containing:
                access_key : str
                    AWS access key identifier.
                secret_key : str
                    AWS secret access key.
                token : str
                    AWS session token.
                expiry_time : str
                    Expiration timestamp in ISO 8601 format.
        """

        creds = (
            self._credentials
            if self._credentials is not None
            else self.get_credentials()
        )
        frozen_creds = creds.get_frozen_credentials()
        return {
            "access_key": frozen_creds.access_key,
            "secret_key": frozen_creds.secret_key,
            "token": frozen_creds.token,
            "expiry_time": creds._expiry_time.isoformat(),  # type: ignore[arg-type]
        }

    @property
    def credentials(self) -> TemporaryCredentials:
        """The current temporary AWS security credentials."""

        return self.refreshable_credentials()

    def whoami(self) -> Identity:
        """Returns metadata about the identity assumed.

        .. versionadded:: 7.2.15

        .. note::

            This method is an alternative to ``get_identity()``.

        Returns
        -------
        Identity
            Dict containing caller identity according to AWS STS.
        """

        return self.get_identity()  # type: ignore[arg-type]


# checking if iot extra is installed
if (
    importlib.util.find_spec("awscrt") is not None
    and importlib.util.find_spec("awsiot") is not None
):
    from awscrt.http import HttpHeaders

    __all__ += ["AWSCRTResponse"]

    class AWSCRTResponse:
        """Lightweight response collector for awscrt HTTP."""

        def __init__(self):
            """Initialize to default for when callbacks are called."""

            self.status_code = None
            self.headers = None
            self.body = bytearray()

        def on_response(self, http_stream, status_code, headers, **kwargs):
            """Process awscrt.io response."""

            self.status_code = status_code
            self.headers = HttpHeaders(headers)

        def on_body(self, http_stream, chunk, **kwargs):
            """Process awscrt.io body."""

            self.body.extend(chunk)
