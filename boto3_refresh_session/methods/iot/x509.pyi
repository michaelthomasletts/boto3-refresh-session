# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Type stubs for IoT X.509 refreshable session."""

from typing import Any, Dict

from awscrt.io import LogLevel
from awscrt.mqtt import Connection
from boto3.session import Session
from botocore.client import BaseClient

from ...utils.cache import ClientCache
from ...utils.typing import Identity, TemporaryCredentials, PKCS11

__all__ = ["IOTX509RefreshableSession"]

class IOTX509RefreshableSession(Session):
    client_cache: ClientCache

    def __init__(
        self,
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
    def mqtt(
        self,
        client_id: str,
        clean_session: bool = False,
        reconnect_min_timeout_secs: int = 5,
        reconnect_max_timeout_secs: int = 60,
        keep_alive_secs: int = 1200,
        ping_timeout_ms: int = 3000,
        protocol_operation_timeout_ms: int = 0,
        will: Any | None = None,
        username: str | None = None,
        password: str | None = None,
        port: int = 8883,
        use_websocket: bool = False,
        websocket_handshake_transform: Any | None = None,
        websocket_proxy_options: Any | None = None,
        proxy_options: Any | None = None,
    ) -> Connection: ...
