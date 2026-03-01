# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Public factory for constructing refreshable boto3 sessions."""

from typing import Any, Callable, Dict, Literal, List, overload

from awscrt.io import LogLevel

from .methods.custom import CustomRefreshableSession
from .methods.iot.x509 import IOTX509RefreshableSession
from .methods.sts import STSRefreshableSession
from .utils.config import AssumeRoleConfig, STSClientConfig
from .utils.typing import PKCS11, TemporaryCredentials

__all__ = ["RefreshableSession"]

class RefreshableSession:
    # typing overload for method="sts" (default)
    @overload
    def __new__(
        cls,
        method: Literal["sts"] = "sts",
        *,
        assume_role_kwargs: AssumeRoleConfig | Dict[str, Any],
        sts_client_kwargs: STSClientConfig | Dict[str, Any] | None = None,
        mfa_token_provider: (
            Callable[..., str] | List[str] | str | None
        ) = None,
        mfa_token_provider_kwargs: Dict[str, Any] | None = None,
        defer_refresh: bool = True,
        advisory_timeout: int = 900,
        mandatory_timeout: int = 600,
        **kwargs: Any,
    ) -> STSRefreshableSession: ...

    # typing overload for method="custom"
    @overload
    def __new__(
        cls,
        method: Literal["custom"],
        *,
        custom_credentials_method: Callable[
            ..., TemporaryCredentials | Dict[str, str]
        ],
        custom_credentials_method_args: Dict[str, Any] | None = None,
        defer_refresh: bool = True,
        advisory_timeout: int = 900,
        mandatory_timeout: int = 600,
        **kwargs: Any,
    ) -> CustomRefreshableSession: ...

    # typing overload for method="iot"
    @overload
    def __new__(
        cls,
        method: Literal["iot"],
        *,
        endpoint: str,
        role_alias: str,
        certificate: str | bytes,
        thing_name: str | None = None,
        private_key: str | bytes | None = None,
        pkcs11: PKCS11 | Dict[str, Any] | None = None,
        ca: str | bytes | None = None,
        verify_peer: bool = True,
        timeout: float | int | None = None,
        duration_seconds: int | None = None,
        awscrt_log_level: LogLevel | None = None,
        defer_refresh: bool = True,
        advisory_timeout: int = 900,
        mandatory_timeout: int = 600,
        **kwargs: Any,
    ) -> IOTX509RefreshableSession: ...
    @classmethod
    def get_available_methods(cls) -> List[str]: ...
