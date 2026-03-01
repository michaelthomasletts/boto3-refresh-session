# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Custom refreshable session using a user-provided credential getter."""

from typing import Any, Callable, Dict

from boto3.resources.base import ServiceResource
from boto3_client_cache import Session, SessionCache
from boto3_client_cache import EvictionPolicy
from botocore.client import BaseClient

from ..utils.typing import Identity, TemporaryCredentials

__all__ = ["CustomRefreshableSession"]

class CustomRefreshableSession(Session):
    cache: SessionCache

    def __init__(
        self,
        custom_credentials_method: Callable[
            ..., TemporaryCredentials | Dict[str, str]
        ],
        custom_credentials_method_args: Dict[str, Any] | None = None,
        defer_refresh: bool = True,
        advisory_timeout: int = 900,
        mandatory_timeout: int = 600,
        **kwargs: Any,
    ) -> None: ...
    def client(
        self,
        *args: Any,
        eviction_policy: EvictionPolicy | None = None,
        max_size: int | None = None,
        **kwargs: Any,
    ) -> BaseClient: ...
    def resource(
        self,
        *args: Any,
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
