# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""STS assume-role refreshable session implementation."""

from typing import Any, Callable, Dict, List

from boto3.session import Session
from botocore.client import BaseClient

from ..utils.cache import ClientCache
from ..utils.typing import Identity, TemporaryCredentials
from ..utils.config import AssumeRoleConfig, STSClientConfig

__all__ = ["STSRefreshableSession"]

class STSRefreshableSession(Session):
    client_cache: ClientCache

    def __init__(
        self,
        assume_role_kwargs: AssumeRoleConfig | Dict[str, Any],
        sts_client_kwargs: STSClientConfig | Dict[str, Any] | None = None,
        mfa_token_provider: Callable[[], str] | List[str] | str | None = None,
        defer_refresh: bool = True,
        advisory_timeout: int = 900,
        mandatory_timeout: int = 600,
        cache_clients: bool = True,
        client_cache_max_size: int = 10,
        **kwargs: Any,
    ) -> None: ...
    def client(self, *args: Any, **kwargs: Any) -> BaseClient: ...
    def refreshable_credentials(
        self,
    ) -> TemporaryCredentials: ...
    def get_identity(self) -> Identity: ...
    def whoami(self) -> Identity: ...
    @property
    def credentials(self) -> TemporaryCredentials: ...
    def _get_credentials(self) -> TemporaryCredentials: ...
