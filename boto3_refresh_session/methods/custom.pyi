# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Custom refreshable session using a user-provided credential getter."""

from typing import Any, Callable, Mapping

from boto3.session import Session
from botocore.client import BaseClient

from ..utils.cache import ClientCache
from ..utils.typing import Identity, TemporaryCredentials

__all__ = ["CustomRefreshableSession"]

class CustomRefreshableSession(Session):
    client_cache: ClientCache

    def __init__(
        self,
        custom_credentials_method: Callable[..., TemporaryCredentials],
        custom_credentials_method_args: Mapping[str, Any] | None = None,
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
    ) -> TemporaryCredentials | Mapping[str, str]: ...
    def get_identity(self) -> Identity | Mapping[str, Any]: ...
    def whoami(self) -> Identity | Mapping[str, Any]: ...
    @property
    def credentials(self) -> TemporaryCredentials | Mapping[str, str]: ...
    def _get_credentials(self) -> TemporaryCredentials | Mapping[str, str]: ...
