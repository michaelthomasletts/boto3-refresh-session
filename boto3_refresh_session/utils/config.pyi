# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Configurations for AWS STS AssumeRole and STS Client.

The following configuration classes do not validate most user inputs except
'TokenCode' in `AssumeRoleConfig` and `service_name` in `STSClientConfig`.
It is the user's responsibility to ensure that the provided values conform
to AWS and boto specifications. The purpose of these configurations is to
provide a structured way to manage parameters when working with AWS STS.

For additional information on AWS specifications, refer to the
[API Reference for AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html).
"""

from __future__ import annotations

__all__ = ["AssumeRoleConfig", "STSClientConfig"]

from abc import ABC, abstractmethod
from collections.abc import (
    Iterable,
    Iterator,
    ItemsView,
    KeysView,
    MutableMapping,
    ValuesView,
)
from typing import Any

from botocore.config import Config

from boto3_refresh_session.utils.typing import (
    PolicyDescriptorType,
    ProvidedContext,
    Tag,
)

class BaseConfig(ABC, MutableMapping[str, Any]):
    """Base configuration class."""

    def __init__(self, **kwargs: Any) -> None: ...
    def __contains__(self, key: object) -> bool: ...
    def __delitem__(self, key: str) -> None: ...
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    def __reversed__(self) -> Iterator[str]: ...
    def __or__(self, other: dict[str, Any]) -> dict[str, Any]: ...
    def __ror__(self, other: dict[str, Any]) -> dict[str, Any]: ...
    def __ior__(self, other: dict[str, Any]) -> BaseConfig: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def clear(self) -> None: ...
    def copy(self) -> dict[str, Any]: ...
    @classmethod
    def fromkeys(
        cls, iterable: Iterable[str], value: Any = ...
    ) -> dict[str, Any]: ...
    def get(self, key: str, default: Any = ...) -> Any: ...
    def items(self) -> ItemsView[str, Any]: ...
    def keys(self) -> KeysView[str]: ...
    def pop(self, key: str, default: Any = ...) -> Any: ...
    def popitem(self) -> tuple[str, Any]: ...
    def update(self, *args: Any, **kwargs: Any) -> None: ...
    def setdefault(self, key: str, default: Any = None) -> Any: ...
    def values(self) -> ValuesView[Any]: ...
    @abstractmethod
    def _validate(self, key: str, value: Any) -> None: ...

class AssumeRoleConfig(BaseConfig):
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
    Values can be accessed via dot-notation (e.g., `config.RoleArn`)
    or dictionary-style access (e.g., `config['RoleArn']`).

    Accessing a valid but unset attribute (e.g., `SerialNumber`) via
    dot-notation returns `None` instead of raising an error. While this
    behavior is convenient, it may surprise users accustomed to seeing
    `AttributeError` exceptions in similar contexts.

    For additional information on AWS specifications, refer to the
    [API Reference for AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html).
    """

    def __init__(
        self,
        *,
        RoleArn: str,
        RoleSessionName: str | None = None,
        PolicyArns: list[PolicyDescriptorType] | None = None,
        Policy: str | None = None,
        DurationSeconds: int | None = None,
        ExternalId: str | None = None,
        SerialNumber: str | None = None,
        TokenCode: str | None = None,
        Tags: list[Tag] | None = None,
        TransitiveTagKeys: list[str] | None = None,
        SourceIdentity: str | None = None,
        ProvidedContexts: list[ProvidedContext] | None = None,
    ) -> None: ...
    def _validate(self, key: str, value: Any) -> None: ...

class STSClientConfig(BaseConfig):
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

    Notes
    -----
    Values can be accessed via dot-notation (e.g., `config.RoleArn`)
    or dictionary-style access (e.g., `config['RoleArn']`).

    Accessing a valid but unset attribute (e.g., `SerialNumber`) via
    dot-notation returns `None` instead of raising an error. While this
    behavior is convenient, it may surprise users accustomed to seeing
    `AttributeError` exceptions in similar contexts.

    `service_name` is enforced to be 'sts'. If a different value is
    provided, it will be overridden to 'sts' with a warning.
    """

    def __init__(
        self,
        *,
        service_name: str | None = None,
        region_name: str | None = None,
        api_version: str | None = None,
        use_ssl: bool | None = None,
        verify: bool | str | None = None,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        config: Config | None = None,
        aws_account_id: str | None = None,
    ) -> None: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def _validate(self, key: str, value: Any) -> None: ...
