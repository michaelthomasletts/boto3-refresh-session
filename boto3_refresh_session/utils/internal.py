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
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)

from ..exceptions import BRSWarning
from .typing import (
    Identity,
    IoTAuthenticationMethod,
    Method,
    RefreshableTemporaryCredentials,
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
    defer_refresh : bool, default=True
        If True, the initial credential refresh is deferred until the
        credentials are first accessed. If False, the initial refresh
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
        **kwargs,
    ):
        self.refresh_method: RefreshMethod = refresh_method
        self.defer_refresh: bool = defer_refresh is not False
        self.advisory_timeout: int | None = advisory_timeout
        self.mandatory_timeout: int | None = mandatory_timeout
        super().__init__(**kwargs)

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

        creds = self.get_credentials().get_frozen_credentials()
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
