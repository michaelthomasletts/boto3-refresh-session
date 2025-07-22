from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    List,
    Literal,
    TypedDict,
    TypeVar,
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
AuthenticationMethod = Literal["certificate", "cognito", "__iot_sentinel__"]

#: Type alias for all currently available credential refresh methods.
Method = Literal["sts", "ecs", "custom", "iot", "__sentinel__"]

#: Type alias for all refresh method names.
RefreshMethod = Literal[
    "sts-assume-role",
    "ecs-container-metadata",
    "custom",
    "iot-certificate",
    "iot-cognito",
]

#: Type alias for all currently registered credential refresh methods.
RegistryKey = TypeVar("RegistryKey", bound=str)


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

    Other Parameters
    ----------------
    kwargs : Any
        Optional keyword arguments for initializing boto3.session.Session."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def initialize(
        self,
        credentials_method: Callable,
        defer_refresh: bool,
        refresh_method: RefreshMethod,
    ):
        # determining how exactly to refresh expired temporary credentials
        if not defer_refresh:
            self._credentials = RefreshableCredentials.create_from_metadata(
                metadata=credentials_method(),
                refresh_using=credentials_method,
                method=refresh_method,
            )
        else:
            self._credentials = DeferredRefreshableCredentials(
                refresh_using=credentials_method, method=refresh_method
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
