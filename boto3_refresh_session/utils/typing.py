# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Shared type definitions used across refreshable session modules."""

from __future__ import annotations

__all__ = [
    "AssumeRoleParams",
    "Identity",
    "Method",
    "PublicMethod",
    "RefreshMethod",
    "RegistryKey",
    "STSClientParams",
    "TemporaryCredentials",
]

import importlib.util
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Literal,
    TypeAlias,
    TypedDict,
    TypeVar,
)

try:
    from typing import NotRequired  # type: ignore[import]
except ImportError:
    from typing_extensions import NotRequired

from botocore.config import Config


def _iot_extra_installed() -> bool:
    """Determines whether the 'iot' extra is installed.

    Returns
    -------
    bool
        ``True`` if the 'iot' extra is installed, ``False`` otherwise.
    """

    return (
        importlib.util.find_spec("awscrt") is not None
        and importlib.util.find_spec("awsiot") is not None
    )


# checking whether 'iot' extra is installed or we're in a type-checking context
if _IOT_EXTRA_INSTALLED := True if TYPE_CHECKING else _iot_extra_installed():
    __all__ += [
        "IoTAuthenticationMethod",
        "PublicIoTAuthenticationMethod",
        "PKCS11",
        "Transport",
    ]

    #: Type alias for all currently available IoT authentication methods.
    IoTAuthenticationMethod: TypeAlias = Literal["x509", "__iot_sentinel__"]

    #: Public type alias for currently available IoT authentication methods.
    PublicIoTAuthenticationMethod: TypeAlias = Literal["x509"]

    #: Type alias for all currently available credential refresh methods.
    Method: TypeAlias = Literal[  # type: ignore[misc]
        "custom",
        "iot",
        "sts",
        "__sentinel__",
        "__iot_sentinel__",
    ]

    #: Public type alias for currently available credential refresh methods.
    PublicMethod: TypeAlias = Literal["custom", "iot", "sts"]  # type: ignore[misc]

    #: Type alias for all refresh method names.
    RefreshMethod: TypeAlias = Literal["custom", "iot-x509", "sts-assume-role"]  # type: ignore[misc]

    #: Type alias for acceptable transports
    Transport: TypeAlias = Literal["x509", "ws"]
else:
    #: Type alias for currently available credential refresh methods.
    Method: TypeAlias = Literal["custom", "sts", "__sentinel__"]  # type: ignore[misc]

    #: Public type alias for currently available credential refresh methods.
    PublicMethod: TypeAlias = Literal["custom", "sts"]  # type: ignore[misc]

    #: Type alias for all refresh method names.
    RefreshMethod: TypeAlias = Literal["custom", "sts-assume-role"]  # type: ignore[misc]

#: Type alias for all currently registered credential refresh methods.
RegistryKey = TypeVar("RegistryKey", bound=str)


class Identity(TypedDict, total=False):
    """Metadata for the current caller identity."""

    method: str
    source: str
    Account: NotRequired[str]
    Arn: NotRequired[str]
    UserId: NotRequired[str]
    ResponseMetadata: NotRequired[dict[str, Any]]


class TemporaryCredentials(TypedDict):
    """Temporary IAM credentials."""

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
    service_name: NotRequired[str]
    region_name: NotRequired[str]
    api_version: NotRequired[str]
    use_ssl: NotRequired[bool]
    verify: NotRequired[bool | str]
    endpoint_url: NotRequired[str]
    aws_access_key_id: NotRequired[str]
    aws_secret_access_key: NotRequired[str]
    aws_session_token: NotRequired[str]
    config: NotRequired[Config]
    aws_account_id: NotRequired[str]


if _IOT_EXTRA_INSTALLED:

    class PKCS11(TypedDict):
        pkcs11_lib: str
        user_pin: NotRequired[str]
        slot_id: NotRequired[int]
        token_label: NotRequired[str | None]
        private_key_label: NotRequired[str | None]
