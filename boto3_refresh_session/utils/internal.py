__all__ = [
    "AWSCRTResponse",
    "BaseIoTRefreshableSession",
    "BaseRefreshableSession",
    "BRSSession",
    "CredentialProvider",
    "Registry",
    "refreshable_session",
]

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, ClassVar, Generic, TypeVar, cast

from awscrt.http import HttpHeaders
from boto3.session import Session
from botocore.client import BaseClient
from botocore.config import Config
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)

from ..exceptions import BRSError, BRSWarning
from .cache import ClientCache
from .typing import (
    Identity,
    IoTAuthenticationMethod,
    Method,
    RefreshableTemporaryCredentials,
    RefreshMethod,
    RegistryKey,
    TemporaryCredentials,
)


def _freeze_value(value: Any) -> Any:
    """Recursively freezes a value for use in cache keys.

    Parameters
    ----------
    value : Any
        The value to freeze.
    """

    if isinstance(value, dict):
        return tuple(
            sorted((key, _freeze_value(val)) for key, val in value.items())
        )

    # checking for list, tuple, or set just to be safe
    if isinstance(value, (list, tuple, set)):
        return tuple(sorted(_freeze_value(item) for item in value))
    return value


def _config_cache_key(config: Config | None) -> Any:
    """Generates a cache key for a botocore.config.Config object.

    Parameters
    ----------
    config : Config | None
        The Config object to generate a cache key for.
    """

    if config is None:
        return None

    # checking for user-provided options first
    options = getattr(config, "_user_provided_options", None)
    if options is None:
        # __dict__ is pedantic but stable
        return _freeze_value(getattr(config, "__dict__", {}))
    return _freeze_value(options)


class CredentialProvider(ABC):
    """Defines the abstract surface every refreshable session must expose."""

    @abstractmethod
    def _get_credentials(self) -> TemporaryCredentials: ...

    @abstractmethod
    def get_identity(self) -> Identity: ...


class Registry(Generic[RegistryKey]):
    """Gives any hierarchy a class-level registry."""

    registry: ClassVar[dict[str, type]] = {}

    def __init_subclass__(cls, *, registry_key: RegistryKey, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        if registry_key in cls.registry:
            BRSWarning.warn(
                f"{registry_key!r} already registered. Overwriting."
            )

        if "sentinel" not in registry_key:
            cls.registry[registry_key] = cls

    @classmethod
    def items(cls) -> dict[str, type]:
        """Typed accessor for introspection / debugging."""

        return dict(cls.registry)


# defining this here instead of utils to avoid circular imports lol
T_BRSSession = TypeVar("T_BRSSession", bound="BRSSession")

#: Type alias for a generic refreshable session type.
BRSSessionType = type[T_BRSSession]


def refreshable_session(
    cls: BRSSessionType,
) -> BRSSessionType:
    """Wraps cls.__init__ so self.__post_init__ runs after init (if present).

    In plain English: this is essentially a post-initialization hook.

    Returns
    -------
    BRSSessionType
        The decorated class.
    """

    init = getattr(cls, "__init__", None)

    # synthesize __init__ if undefined in the class
    if init in (None, object.__init__):

        def __init__(self, *args, **kwargs):
            super(cls, self).__init__(*args, **kwargs)
            post = getattr(self, "__post_init__", None)
            if callable(post) and not getattr(self, "_post_inited", False):
                post()
                setattr(self, "_post_inited", True)

        cls.__init__ = __init__  # type: ignore[assignment]
        return cls

    # avoids double wrapping
    if getattr(init, "__post_init_wrapped__", False):
        return cls

    @wraps(init)
    def wrapper(self, *args, **kwargs):
        init(self, *args, **kwargs)
        post = getattr(self, "__post_init__", None)
        if callable(post) and not getattr(self, "_post_inited", False):
            post()
            setattr(self, "_post_inited", True)

    wrapper.__post_init_wrapped__ = True  # type: ignore[attr-defined]
    cls.__init__ = cast(Callable[..., None], wrapper)
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
        **kwargs,
    ):
        # initializing parameters
        self.refresh_method: RefreshMethod = refresh_method
        self.defer_refresh: bool = defer_refresh is not False
        self.advisory_timeout: int | None = advisory_timeout
        self.mandatory_timeout: int | None = mandatory_timeout
        self.cache_clients: bool | None = cache_clients is not False

        # initializing Session
        super().__init__(**kwargs)

        # because the "client" namespace is already taken,
        # we must preserve the O.G.
        self._client: Callable = super().client

        # initializing client cache
        self._client_cache: ClientCache = ClientCache()

    def __post_init__(self):
        if not self.defer_refresh:
            self._credentials = RefreshableCredentials.create_from_metadata(
                metadata=self._get_credentials(),
                refresh_using=self._get_credentials,
                method=self.refresh_method,
                advisory_timeout=self.advisory_timeout,
                mandatory_timeout=self.mandatory_timeout,
            )
        else:
            self._credentials = DeferredRefreshableCredentials(
                refresh_using=self._get_credentials, method=self.refresh_method
            )
        self._session._credentials = self._credentials

    def client(self, *args, **kwargs) -> BaseClient:
        """Creates a low-level service client by name.

        Parameters
        ----------
        *args : Any
            Positional arguments for :class:`boto3.session.Session.client`.
        **kwargs : Any
            Keyword arguments for :class:`boto3.session.Session.client`.

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
            # checking if Config was passed as a positional arg
            _args = [
                _config_cache_key(arg) if isinstance(arg, Config) else arg
                for arg in args
            ]

            # popping trailing None values from args, preserving None in middle
            while _args and _args[-1] is None:
                _args.pop()
            _args = tuple(_args)

            # checking if Config was passed as a keyword arg
            _kwargs = kwargs.copy()
            if _kwargs.get("config") is not None:
                _kwargs["config"] = _config_cache_key(_kwargs["config"])

            # preemptively removing None values from kwargs
            _kwargs = {
                key: value
                for key, value in _kwargs.items()
                if value is not None
            }

            # creating a unique key for the client cache
            key = (_args, tuple(sorted(_kwargs.items())))

            # if client exists in cache, return it
            if (_cached_client := self._client_cache.get(key)) is not None:
                return _cached_client

            # else -- initialize, cache, and return it
            client = self._client(*args, **kwargs)

            # attempting to cache and return the client
            try:
                self._client_cache[key] = client
                return client

            # if caching fails, return cached client if possible
            except BRSError:
                return (
                    cached
                    if (cached := self._client_cache.get(key)) is not None
                    else client
                )

        # return a new client if caching is disabled
        else:
            return self._client(*args, **kwargs)

    def refreshable_credentials(self) -> RefreshableTemporaryCredentials:
        """The current temporary AWS security credentials.

        Returns
        -------
        RefreshableTemporaryCredentials
            Temporary AWS security credentials containing:
                AWS_ACCESS_KEY_ID : str
                    AWS access key identifier.
                AWS_SECRET_ACCESS_KEY : str
                    AWS secret access key.
                AWS_SESSION_TOKEN : str
                    AWS session token.
        """

        creds = (
            self._credentials
            if self._credentials is not None
            else self.get_credentials()
        ).get_frozen_credentials()
        return {
            "AWS_ACCESS_KEY_ID": creds.access_key,
            "AWS_SECRET_ACCESS_KEY": creds.secret_key,
            "AWS_SESSION_TOKEN": creds.token,
        }

    @property
    def credentials(self) -> RefreshableTemporaryCredentials:
        """The current temporary AWS security credentials."""

        return self.refreshable_credentials()


class BaseRefreshableSession(
    Registry[Method],
    CredentialProvider,
    BRSSession,
    registry_key="__sentinel__",
):
    """Abstract base class for implementing refreshable AWS sessions.

    Provides a common interface and factory registration mechanism
    for subclasses that generate temporary credentials using various
    AWS authentication methods (e.g., STS).

    Subclasses must implement ``_get_credentials()`` and ``get_identity()``.
    They should also register themselves using the ``method=...`` argument
    to ``__init_subclass__``.

    Parameters
    ----------
    registry : dict[str, type[BaseRefreshableSession]]
        Class-level registry mapping method names to registered session types.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseIoTRefreshableSession(
    Registry[IoTAuthenticationMethod],
    CredentialProvider,
    BRSSession,
    registry_key="__iot_sentinel__",
):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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
