from __future__ import annotations

__all__ = [
    "AssumeRoleParams",
    "CustomCredentialsMethod",
    "CustomCredentialsMethodArgs",
    "Identity",
    "IoTAuthenticationMethod",
    "Method",
    "PKCS11",
    "RefreshMethod",
    "RegistryKey",
    "STSClientParams",
    "TemporaryCredentials",
    "RefreshableTemporaryCredentials",
    "Transport",
]

from datetime import datetime
from typing import (
    Any,
    List,
    Literal,
    Mapping,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
)

try:
    from typing import NotRequired  # type: ignore[import]
except ImportError:
    from typing_extensions import NotRequired

#: Type alias for all currently available IoT authentication methods.
IoTAuthenticationMethod = Literal["x509", "__iot_sentinel__"]

#: Type alias for all currently available credential refresh methods.
Method = Literal[
    "custom",
    "iot",
    "sts",
    "__sentinel__",
    "__iot_sentinel__",
]

#: Type alias for all refresh method names.
RefreshMethod = Literal[
    "custom",
    "iot-x509",
    "sts-assume-role",
]

#: Type alias for all currently registered credential refresh methods.
RegistryKey = TypeVar("RegistryKey", bound=str)

#: Type alias for values returned by get_identity
Identity: TypeAlias = dict[str, Any]

#: Type alias for acceptable transports
Transport: TypeAlias = Literal["x509", "ws"]


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

#: Type alias for custom credential method arguments.
CustomCredentialsMethodArgs: TypeAlias = Mapping[str, Any]


class RefreshableTemporaryCredentials(TypedDict):
    """Refreshable IAM credentials.

    Parameters
    ----------
    access_key : str
        AWS access key identifier.
    secret_key : str
        AWS secret access key.
    token : str
        AWS session token.
    expiry_time : str
        Expiration timestamp in ISO 8601 format.
    """

    access_key: str
    secret_key: str
    token: str
    expiry_time: str


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
    pkcs11_lib: str
    user_pin: NotRequired[str]
    slot_id: NotRequired[int]
    token_label: NotRequired[str | None]
    private_key_label: NotRequired[str | None]
