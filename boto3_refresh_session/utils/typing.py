# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Shared type definitions used across refreshable session modules."""

from __future__ import annotations

__all__ = [
    "AssumeRoleParams",
    "Identity",
    "Method",
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
    __all__ += ["PKCS11", "Transport"]

    #: Type alias for all currently available credential refresh methods.
    Method: TypeAlias = Literal[  # type: ignore
        "custom", "iot", "sts"
    ]

    #: Type alias for all refresh method names.
    RefreshMethod: TypeAlias = Literal["custom", "iot-x509", "sts-assume-role"]  # type: ignore

    #: Type alias for acceptable transports
    Transport: TypeAlias = Literal["x509", "ws"]
else:
    #: Type alias for currently available credential refresh methods.
    Method: TypeAlias = Literal["custom", "sts"]  # type: ignore

    #: Type alias for all refresh method names.
    RefreshMethod: TypeAlias = Literal["custom", "sts-assume-role"]  # type: ignore

#: Type alias for all currently registered credential refresh methods.
RegistryKey = TypeVar("RegistryKey", bound=str)


class Identity(TypedDict, total=False):
    """Metadata for the current caller identity.

    Attributes
    ----------
    method : str
        The method used to obtain the identity.
    source : str
        The source from which the identity was obtained.
    Account : str, optional
        The AWS account ID associated with the identity.
    Arn : str, optional
        The Amazon Resource Name (ARN) of the identity.
    UserId : str, optional
        The unique identifier of the identity.
    ResponseMetadata : dict, optional
        Metadata about the response from the identity service.
    """

    method: str
    source: str
    Account: NotRequired[str]
    Arn: NotRequired[str]
    UserId: NotRequired[str]
    ResponseMetadata: NotRequired[dict[str, Any]]


class TemporaryCredentials(TypedDict):
    """Temporary IAM credentials.

    Attributes
    ----------
    access_key : str
        The temporary access key ID.
    secret_key : str
        The temporary secret access key.
    token : str
        The session token.
    expiry_time : str
        The expiration time of the temporary credentials in ISO 8601 format.
    """

    access_key: str
    secret_key: str
    token: str
    expiry_time: str


class Tag(TypedDict):
    """Structure for session tags.

    Attributes
    ----------
    Key : str
        The key of the tag.
    Value : str
        The value of the tag.
    """

    Key: str
    Value: str


class PolicyDescriptorType(TypedDict):
    """Structure for IAM managed policy ARNs.

    Attributes
    ----------
    Arn : str
        The Amazon Resource Name (ARN) of the IAM managed policy.
    """

    arn: str


class ProvidedContext(TypedDict):
    """Context key and value for AWS STS AssumeRole API.

    Attributes
    ----------
    ProviderArn : str
        The ARN of the context provider.
    ContextAssertion : str
        The context key and value in a stringified JSON format.
    """

    ProviderArn: str
    ContextAssertion: str


class AssumeRoleParams(TypedDict):
    """Configuration for AWS STS AssumeRole API.

    Attributes
    ----------
    RoleArn : str
        The Amazon Resource Name (ARN) of the role to assume.
    RoleSessionName : str, optional
        An identifier for the assumed role session.
    PolicyArns : list of PolicyDescriptorType, optional
        The Amazon Resource Names (ARNs) of the IAM managed policies to
        use as managed session policies.
    Policy : str, optional
        An IAM policy in JSON format to use as an inline session policy.
    DurationSeconds : int, optional
        The duration, in seconds, of the role session.
    ExternalId : str, optional
        A unique identifier that might be required when you assume a role
        in another account.
    SerialNumber : str, optional
        The identification number of the MFA device.
    TokenCode : str, optional
        The value provided by the MFA device. Must be a 6-digit numeric
        string.
    Tags : list of Tag, optional
        A list of session tags.
    TransitiveTagKeys : list of str, optional
        A list of keys for session tags that you want to pass to the role
        session.
    SourceIdentity : str, optional
        A unique identifier that is passed in the AssumeRole call.
    ProvidedContexts : list of ProvidedContext, optional
        A list of context keys and values for the session.

    Notes
    -----
    For additional information on AWS specifications, refer to the
    `API Reference for AssumeRole <https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html>`_.
    """

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
    """Configuration for boto3 STS Client.

    Attributes
    ----------
    service_name : str, optional
        The name of the AWS service. Defaults to 'sts'.
    region_name : str, optional
        The AWS region name.
    api_version : str, optional
        The API version to use.
    use_ssl : bool, optional
        Whether to use SSL.
    verify : bool or str, optional
        Whether to verify SSL certificates or a path to a CA bundle.
    endpoint_url : str, optional
        The complete URL to use for the constructed client.
    aws_access_key_id : str, optional
        The AWS access key ID.
    aws_secret_access_key : str, optional
        The AWS secret access key.
    aws_session_token : str, optional
        The AWS session token.
    config : botocore.config.Config, optional
        Advanced client configuration options.
    aws_account_id : str, optional
        The AWS account ID associated with the credentials.
    """

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
        """Configuration for PKCS#11 library.

        Attributes
        ----------
        pkcs11_lib : str
            The path to the PKCS#11 library.
        user_pin : str or None, optional
            The user PIN for the PKCS#11 token.
        slot_id : int or None, optional
            The slot ID of the PKCS#11 token.
        token_label : str or None, optional
            The label of the PKCS#11 token.
        private_key_label : str or None, optional
            The label of the private key on the PKCS#11 token.
        """

        pkcs11_lib: str
        user_pin: NotRequired[str | None]
        slot_id: NotRequired[int | None]
        token_label: NotRequired[str | None]
        private_key_label: NotRequired[str | None]
