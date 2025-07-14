from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
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

RefreshMethod = Literal[
    "sts-assume-role",
    "ecs-container-metadata",
    "custom",
    "iot-certificate",
    "iot-cognito",
]
RegistryKey = TypeVar("RegistryKey", bound=str)


class Registry(Generic[RegistryKey]):
    """Gives any hierarchy a class-level registry."""

    registry: ClassVar[dict[RegistryKey, type]] = {}

    def __init_subclass__(cls, *, registry_key: RegistryKey, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if registry_key in cls.registry:
            BRSWarning(f"{registry_key!r} already registered. Overwriting.")

        if "sentinel" not in registry_key:
            cls.registry[registry_key] = cls

    @classmethod
    def items(cls) -> dict[RegistryKey, type]:
        """Typed accessor for introspection / debugging."""

        return dict(cls.registry)


class TemporaryCredentials(TypedDict):
    """Temporary IAM credentials."""

    access_key: str
    secret_key: str
    token: str
    expiry_time: datetime | str


class CredentialProvider(ABC):
    """Defines the abstract surface every refreshable session must expose."""

    @abstractmethod
    def _get_credentials(self) -> TemporaryCredentials: ...

    @abstractmethod
    def get_identity(self) -> dict[str, Any]: ...


class BRSSession(Session):
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

    def refreshable_credentials(self) -> dict[str, str]:
        """The current temporary AWS security credentials.

        Returns
        -------
        dict[str, str]
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
    def credentials(self) -> dict[str, str]:
        """The current temporary AWS security credentials."""

        return self.refreshable_credentials()
