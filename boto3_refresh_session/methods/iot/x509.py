__all__ = ["IOTX509RefreshableSession"]

import json
import re
from pathlib import Path
from typing import cast
from urllib.parse import ParseResult, urlparse

from awscrt.exceptions import AwsCrtError
from awscrt.http import HttpClientConnection, HttpRequest
from awscrt.io import (
    ClientBootstrap,
    ClientTlsContext,
    DefaultHostResolver,
    EventLoopGroup,
    Pkcs11Lib,
    TlsConnectionOptions,
    TlsContextOptions,
)

from ...exceptions import BRSError, BRSWarning
from ...utils import (
    PKCS11,
    AWSCRTResponse,
    Identity,
    TemporaryCredentials,
    refreshable_session,
)
from .core import BaseIoTRefreshableSession


@refreshable_session
class IOTX509RefreshableSession(
    BaseIoTRefreshableSession, registry_key="x509"
):
    def __init__(
        self,
        endpoint: str,
        role_alias: str,
        certificate: str | bytes,
        thing_name: str | None = None,
        private_key: str | bytes | None = None,
        pkcs11: PKCS11 | None = None,
        ca: bytes | None = None,
        verify_peer: bool = True,
        timeout: float | int | None = None,
        duration_seconds: int | None = None,
        **kwargs,
    ):
        self.endpoint = self._normalize_iot_credential_endpoint(
            endpoint=endpoint
        )
        self.role_alias = role_alias
        self.certificate = certificate
        self.thing_name = thing_name
        self.private_key = private_key
        self.pkcs11 = pkcs11
        self.ca = ca
        self.verify_peer = verify_peer
        self.timeout = 10.0 if timeout is None else timeout
        self.duration_seconds = duration_seconds

        # initializing BRSSession
        super().__init__(refresh_method="iot-x509", **kwargs)

        # loading X.509 certificate if presented as a string, which
        # is presumed to be the file path.
        # if presented as bytes then self.certificate is presumed to be
        # the actual certificate itself
        if self.certificate and isinstance(self.certificate, str):
            with open(
                Path(self.certificate).expanduser().resolve(), "rb"
            ) as cert_pem_file:
                self.certificate = cert_pem_file.read()

        # either private_key or pkcs11 must be provided
        if self.private_key is None and self.pkcs11 is None:
            raise BRSError(
                "Either 'private_key' or 'pkcs11' must be provided."
            )

        # . . . but both cannot be provided!
        if self.private_key is not None and self.pkcs11 is not None:
            raise BRSError(
                "Only one of 'private_key' or 'pkcs11' can be provided."
            )

        # if the provided private_key is bytes then it's presumed to be
        # the actual private key. but if it's string then it's presumed
        # to be the file path
        if self.private_key and isinstance(self.private_key, str):
            with open(
                Path(self.private_key).expanduser().resolve(), "rb"
            ) as private_key_pem_file:
                self.private_key = private_key_pem_file.read()

        # verifying PKCS#11 dict
        if self.pkcs11:
            self.pkcs11 = self._validate_pkcs11(pkcs11=self.pkcs11)

    def _get_credentials(self) -> TemporaryCredentials:
        url = urlparse(
            f"https://{self.endpoint}/role-aliases/{self.role_alias}/credentials"
        )
        request = HttpRequest("GET", url.path)
        request.headers.add("host", str(url.hostname))
        if self.thing_name:
            request.headers.add("x-amzn-iot-thingname", self.thing_name)
        if self.duration_seconds:
            request.headers.add(
                "x-amzn-iot-credential-duration-seconds",
                str(self.duration_seconds),
            )
        response = AWSCRTResponse()
        port = 443 if not url.port else url.port
        connection = (
            self._mtls_client_connection(url=url, port=port)
            if not self.pkcs11
            else self._mtls_pkcs11_client_connection(url=url, port=port)
        )
        stream = connection.request(
            request, response.on_response, response.on_body
        )
        stream.activate()
        stream_completion_result = stream.completion_future.result(10)
        if response.status_code == 200:
            credentials = json.loads(response.body.decode("utf-8"))[
                "credentials"
            ]
            return {
                "access_key": credentials["accessKeyId"],
                "secret_key": credentials["secretAccessKey"],
                "token": credentials["sessionToken"],
                "expiry_time": credentials["expiration"],
            }
        else:
            raise BRSError(
                f"Error '{stream_completion_result}' getting credentials: {json.loads(response.body.decode())}"
            )

    def _mtls_client_connection(
        self, url: ParseResult, port: int
    ) -> HttpClientConnection:
        event_loop_group: EventLoopGroup = EventLoopGroup()
        host_resolver: DefaultHostResolver = DefaultHostResolver(
            event_loop_group
        )
        bootstrap: ClientBootstrap = ClientBootstrap(
            event_loop_group, host_resolver
        )
        tls_ctx_opt = TlsContextOptions.create_client_with_mtls(
            cert_buffer=self.certificate, key_buffer=self.private_key
        )

        if self.ca:
            tls_ctx_opt.override_default_trust_store(self.ca)

        tls_ctx_opt.verify_peer = self.verify_peer
        tls_ctx = ClientTlsContext(tls_ctx_opt)
        tls_conn_opt: TlsConnectionOptions = cast(
            TlsConnectionOptions, tls_ctx.new_connection_options()
        )
        tls_conn_opt.set_server_name(str(url.hostname))

        try:
            connection_future = HttpClientConnection.new(
                host_name=str(url.hostname),
                port=port,
                bootstrap=bootstrap,
                tls_connection_options=tls_conn_opt,
            )
            return connection_future.result(self.timeout)
        except AwsCrtError as err:
            raise BRSError(
                f"Error completing mTLS connection to endpoint '{url.hostname}'"
            ) from err

    def _mtls_pkcs11_client_connection(
        self, url: ParseResult, port: int
    ) -> HttpClientConnection:
        event_loop_group: EventLoopGroup = EventLoopGroup()
        host_resolver: DefaultHostResolver = DefaultHostResolver(
            event_loop_group
        )
        bootstrap: ClientBootstrap = ClientBootstrap(
            event_loop_group, host_resolver
        )

        if not self.pkcs11:
            raise BRSError(
                "Attempting to establish mTLS connection using PKCS#11"
                "but 'pkcs11' parameter is 'None'!"
            )

        tls_ctx_opt = TlsContextOptions.create_client_with_mtls_pkcs11(
            pkcs11_lib=Pkcs11Lib(file=self.pkcs11["pkcs11_lib"]),
            user_pin=self.pkcs11["user_pin"],
            slot_id=self.pkcs11["slot_id"],
            token_label=self.pkcs11["token_label"],
            private_key_label=self.pkcs11["private_key_label"],
            cert_file_path=None,
            cert_file_contents=self.certificate,
        )
        if self.ca:
            tls_ctx_opt.override_default_trust_store(self.ca)
        tls_ctx_opt.verify_peer = self.verify_peer
        tls_ctx = ClientTlsContext(tls_ctx_opt)
        tls_conn_opt: TlsConnectionOptions = cast(
            TlsConnectionOptions, tls_ctx.new_connection_options()
        )
        tls_conn_opt.set_server_name(str(url.hostname))
        try:
            connection_future = HttpClientConnection.new(
                host_name=str(url.hostname),
                port=port,
                bootstrap=bootstrap,
                tls_connection_options=tls_conn_opt,
            )
            return connection_future.result(self.timeout)
        except AwsCrtError as err:
            raise BRSError(f"Error completing mTLS connection.") from err

    def get_identity(self) -> Identity: ...

    @staticmethod
    def _normalize_iot_credential_endpoint(endpoint: str) -> str:
        if ".credentials.iot." in endpoint:
            return endpoint

        if ".iot." in endpoint and "-ats." in endpoint:
            logged_data_endpoint = re.sub(r"^[^. -]+", "***", endpoint)
            logged_credential_endpoint = re.sub(
                r"^[^. -]+",
                "***",
                (endpoint := endpoint.replace("-ats.iot", ".credentials.iot")),
            )
            BRSWarning.warn(
                "The 'endpoint' parameter you provided represents the data "
                "endpoint for IoT not the credentials endpoint! The endpoint "
                f"you provided was therefore modified from '{logged_data_endpoint}' -> "
                f"'{logged_credential_endpoint}'"
            )
            return endpoint

        raise BRSError(
            "Invalid IoT endpoint provided for credentials provider. "
            "Expected '<id>.credentials.iot.<region>.amazonaws.com'"
        )

    @staticmethod
    def _validate_pkcs11(pkcs11: PKCS11):
        # verifying presence of pkcs11_lib in pkcs11
        if "pkcs11_lib" not in pkcs11:
            raise BRSError(
                "PKCS#11 library path must be provided as 'pkcs11_lib' in 'pkcs11'."
            )

        # verifying pkcs11_lib is a file path
        elif not Path(pkcs11["pkcs11_lib"]).expanduser().resolve().is_file():
            raise BRSError(
                f"'{pkcs11['pkcs11_lib']}' is not a valid file path for 'pkcs11_lib' in "
                "'pkcs11'."
            )

        # injecting None wherever a key is missing from pkcs11
        if "user_pin" not in pkcs11:
            pkcs11["user_pin"] = None
        if "slot_id" not in pkcs11:
            pkcs11["slot_id"] = None
        if "token_label" not in pkcs11:
            pkcs11["token_label"] = None
        if "private_key_label" not in pkcs11:
            pkcs11["private_key_label"] = None
