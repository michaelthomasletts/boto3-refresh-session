from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    List,
    Literal,
    Mapping,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
    cast,
)

from boto3.session import Session
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)

from .exceptions import BRSWarning

try:
    from typing import NotRequired  # type: ignore[import]
except ImportError:
    from typing_extensions import NotRequired

#: Type alias for all currently available IoT authentication methods.
IoTAuthenticationMethod = Literal["certificate", "cognito", "__iot_sentinel__"]

#: Type alias for all currently available credential refresh methods.
Method = Literal[
    "sts",
    "ecs",
    "custom",
    "__sentinel__",
]  # TODO: Add iot when implemented

#: Type alias for all refresh method names.
RefreshMethod = Literal[
    "sts-assume-role",
    "ecs-container-metadata",
    "custom",
]  # Add iot-certificate and iot-cognito when iot implemented

#: Type alias for all currently registered credential refresh methods.
RegistryKey = TypeVar("RegistryKey", bound=str)

#: Type alias for a generic refreshable session type.
BRSSessionType = TypeVar("BRSSessionType", bound="BRSSession")


def refreshable_session(
    cls: type[BRSSessionType],
) -> type[BRSSessionType]:
    """Wraps cls.__init__ so self.__post_init__ runs after init (if present).

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


class Registry(Generic[RegistryKey]):
    """Gives any hierarchy a class-level registry."""

    registry: ClassVar[dict[str, type]] = {}

    def __init_subclass__(cls, *, registry_key: RegistryKey, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        if registry_key in cls.registry:
            BRSWarning(f"{registry_key!r} already registered. Overwriting.")

        if "sentinel" not in registry_key:
            cls.registry[registry_key] = cls

    @classmethod
    def items(cls) -> dict[str, type]:
        """Typed accessor for introspection / debugging."""

        return dict(cls.registry)


class TemporaryCredentials(TypedDict):
    """Temporary IAM credentials."""

    access_key: str
    secret_key: str
    token: str
    expiry_time: datetime | str


class _CustomCredentialsMethod(Protocol):
    def __call__(self, **kwargs: Any) -> TemporaryCredentials: ...


#: Type alias for custom credential retrieval methods.
CustomCredentialsMethod: TypeAlias = _CustomCredentialsMethod

#: Type alias for keyword arguments to pass to custom credential retrieval methods.
CustomCredentialsMethodArgs: TypeAlias = Mapping[str, Any]


class RefreshableTemporaryCredentials(TypedDict):
    """Refreshable IAM credentials.

    Parameters
    ----------
    AWS_ACCESS_KEY_ID : str
        AWS access key identifier.
    AWS_SECRET_ACCESS_KEY : str
        AWS secret access key.
    AWS_SESSION_TOKEN : str
        AWS session token.
    """

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str


class CredentialProvider(ABC):
    """Defines the abstract surface every refreshable session must expose."""

    @abstractmethod
    def _get_credentials(self) -> TemporaryCredentials: ...

    @abstractmethod
    def get_identity(self) -> dict[str, Any]: ...


class BRSSession(Session):
    """Wrapper for boto3.session.Session.

    Parameters
    ----------
    refresh_method : RefreshMethod
        The method to use for refreshing temporary credentials.
    defer_refresh : bool, default=True
        If True, the initial credential refresh is deferred until the
        credentials are first accessed. If False, the initial refresh

    Other Parameters
    ----------------
    kwargs : Any
        Optional keyword arguments for initializing boto3.session.Session.
    """

    def __init__(
        self,
        refresh_method: RefreshMethod,
        defer_refresh: bool | None = None,
        **kwargs,
    ):
        self.refresh_method: RefreshMethod = refresh_method
        self.defer_refresh: bool = defer_refresh is not False
        super().__init__(**kwargs)

    def __post_init__(self):
        if not self.defer_refresh:
            self._credentials = RefreshableCredentials.create_from_metadata(
                metadata=self._get_credentials(),
                refresh_using=self._get_credentials,
                method=self.refresh_method,
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


class Tag(TypedDict):
    Key: str
    Value: str


class PolicyDescriptorType(TypedDict):
    arn: str


class ProvidedContext(TypedDict):
    ProviderArn: str
    ContextAssertion: str


class AssumeRoleParams(TypedDict):
    RoleArn: str
    RoleSessionName: str
    PolicyArns: NotRequired[List[PolicyDescriptorType]]
    Policy: NotRequired[str]
    DurationSeconds: NotRequired[int]
    ExternalId: NotRequired[str]
    SerialNumber: NotRequired[str]
    TokenCode: NotRequired[str]
    Tags: NotRequired[List[Tag]]
    TransitiveTagKeys: NotRequired[List[str]]
    SourceIdentity: NotRequired[str]
    ProvidedContexts: NotRequired[List[ProvidedContext]]


class STSClientParams(TypedDict):
    region_name: NotRequired[str]
    api_version: NotRequired[str]
    use_ssl: NotRequired[bool]
    verify: NotRequired[bool | str]
    endpoint_url: NotRequired[str]
    aws_access_key_id: NotRequired[str]
    aws_secret_access_key: NotRequired[str]
    aws_session_token: NotRequired[str]
    config: NotRequired[Any]
    aws_account_id: NotRequired[str]


class PKCS11(TypedDict):
    pkcs11_loc: str
    user_pin: NotRequired[str]
    slot_id: NotRequired[int]
    token_label: NotRequired[str | None]
    private_key_label: NotRequired[str | None]
