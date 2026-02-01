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
`API Reference for AssumeRole <https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html>`_.
"""

__all__ = ["AssumeRoleConfig", "STSClientConfig"]

import re
from abc import ABC, abstractmethod
from typing import Any

from botocore.config import Config

from ..exceptions import BRSValidationError, BRSWarning
from .constants import (
    ASSUME_ROLE_CONFIG_PARAMETERS,
    STS_CLIENT_CONFIG_PARAMETERS,
)
from .typing import PolicyDescriptorType, ProvidedContext, Tag


class BaseConfig(dict, ABC):
    """Base configuration class."""

    def __init__(self, **kwargs):
        super().__init__()
        self.update(kwargs)

    def __setitem__(self, key: str, value: Any) -> None:
        self._validate(key, value)
        if value is None:
            if key in self:
                super().__delitem__(key)
            return
        super().__setitem__(key, value)

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            try:
                self._validate(name, None)
            except BRSValidationError as exc:
                raise AttributeError(
                    f"'{name}' is an unknown attribute."
                ) from exc
            return None

    def __setattr__(self, name: str, value: Any) -> None:
        self.__setitem__(name, value)

    def update(self, *args, **kwargs) -> None:
        for key, value in dict(*args, **kwargs).items():
            self.__setitem__(key, value)

    def setdefault(self, key: str, default: Any = None):
        if key in self:
            return super().setdefault(key, default)
        self._validate(key, default)
        return super().setdefault(key, default)

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
    Values can be accessed via dot-notation (e.g., ``config.RoleArn``)
    or dictionary-style access (e.g., ``config['RoleArn']``).

    Accessing a valid but unset attribute (e.g., ``SerialNumber``) via
    dot-notation returns ``None`` instead of raising an error. While this
    behavior is convenient, it may surprise users accustomed to seeing
    ``AttributeError`` exceptions in similar contexts.

    For additional information on AWS specifications, refer to the
    `API Reference for AssumeRole <https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html>`_.
    """

    def __init__(
        self,
        *,  # enforce keyword-only arguments
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
    ):
        super().__init__(
            RoleArn=RoleArn,
            RoleSessionName=RoleSessionName,
            PolicyArns=PolicyArns,
            Policy=Policy,
            DurationSeconds=DurationSeconds,
            ExternalId=ExternalId,
            SerialNumber=SerialNumber,
            TokenCode=TokenCode,
            Tags=Tags,
            TransitiveTagKeys=TransitiveTagKeys,
            SourceIdentity=SourceIdentity,
            ProvidedContexts=ProvidedContexts,
        )

    def _validate(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise BRSValidationError("Attribute name must be a string.")

        if key not in ASSUME_ROLE_CONFIG_PARAMETERS:
            raise BRSValidationError(
                f"'{key}' is not a valid attribute for AssumeRoleConfig."
            ) from None

        if key == "RoleArn":
            if not isinstance(value, str):
                raise BRSValidationError(
                    "'RoleArn' must be a string."
                ) from None
            if len(value) < 20:
                raise BRSValidationError(
                    "'RoleArn' must be at least 20 characters long."
                ) from None

        # ensuring TokenCode is a 6-digit numeric string
        if (
            key == "TokenCode"
            and value is not None
            and not (isinstance(value, str) and re.fullmatch(r"\d{6}", value))
        ):
            raise BRSValidationError(
                f"'{key}' must be a 6-digit numeric string."
            ) from None

        # ensuring RoleArn is at least a 20 characters long str
        if key == "RoleArn" and not (
            isinstance(value, str) and len(value) >= 20
        ):
            raise BRSValidationError(
                f"'{key}' must be a string with at least 20 characters."
            ) from None


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
    Values can be accessed via dot-notation (e.g., ``config.RoleArn``)
    or dictionary-style access (e.g., ``config['RoleArn']``).

    Accessing a valid but unset attribute (e.g., ``SerialNumber``) via
    dot-notation returns ``None`` instead of raising an error. While this
    behavior is convenient, it may surprise users accustomed to seeing
    ``AttributeError`` exceptions in similar contexts.

    ``service_name`` is enforced to be 'sts'. If a different value is
    provided, it will be overridden to 'sts' with a warning.
    """

    def __init__(
        self,
        *,  # enforce keyword-only arguments
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
    ):
        super().__init__(
            service_name=service_name,
            region_name=region_name,
            api_version=api_version,
            use_ssl=use_ssl,
            verify=verify,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            config=config,
            aws_account_id=aws_account_id,
        )

    def __setitem__(self, key: str, value: Any) -> None:
        """Override to enforce 'sts' as service_name."""

        if key == "service_name":
            if value is None:
                value = "sts"
            elif isinstance(value, str):
                if value != "sts":
                    BRSWarning.warn(
                        "The 'service_name' for STSClientConfig should be "
                        "'sts'. Overriding to 'sts'."
                    )
                    value = "sts"
            else:
                raise BRSValidationError(
                    "'service_name' must be a string."
                ) from None

        super().__setitem__(key, value)

    def _validate(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise BRSValidationError(
                "Attribute name must be a string."
            ) from None

        if key not in STS_CLIENT_CONFIG_PARAMETERS:
            raise BRSValidationError(
                f"'{key}' is not a valid attribute for STSClientConfig."
            ) from None
