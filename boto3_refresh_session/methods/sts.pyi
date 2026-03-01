# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""STS assume-role refreshable session implementation."""

from typing import Any, Callable, Dict, List

from boto3.resources.base import ServiceResource
from boto3_client_cache import EvictionPolicy, Session, SessionCache
from botocore.client import BaseClient

from ..utils.config import AssumeRoleConfig, STSClientConfig
from ..utils.typing import Identity, TemporaryCredentials

__all__ = ["STSRefreshableSession"]

class STSRefreshableSession(Session):
    cache: SessionCache

    def __init__(
        self,
        assume_role_kwargs: AssumeRoleConfig | Dict[str, Any],
        sts_client_kwargs: STSClientConfig | Dict[str, Any] | None = None,
        mfa_token_provider: Callable[..., str] | List[str] | str | None = None,
        mfa_token_provider_kwargs: Dict[str, Any] | None = None,
        defer_refresh: bool = True,
        advisory_timeout: int = 900,
        mandatory_timeout: int = 600,
        **kwargs: Any,
    ) -> None: ...
    def client(
        self,
        *args,
        eviction_policy: EvictionPolicy | None = None,
        max_size: int | None = None,
        **kwargs: Any,
    ) -> BaseClient: ...
    def resource(
        self,
        *args,
        eviction_policy: EvictionPolicy | None = None,
        max_size: int | None = None,
        **kwargs: Any,
    ) -> ServiceResource: ...
    def refreshable_credentials(
        self,
    ) -> TemporaryCredentials: ...
    def get_identity(self) -> Identity: ...
    def whoami(self) -> Identity: ...
    @property
    def credentials(self) -> TemporaryCredentials: ...
    def _get_credentials(self) -> TemporaryCredentials: ...
