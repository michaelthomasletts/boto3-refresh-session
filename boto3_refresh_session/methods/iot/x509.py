# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IoT Core X.509 refreshable session implementation."""

__all__ = ["IOTX509RefreshableSession"]

import json
import re
from atexit import register
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast, get_args
from urllib.parse import ParseResult, urlparse

from awscrt import auth, io
from awscrt.exceptions import AwsCrtError
from awscrt.http import HttpClientConnection, HttpRequest
from awscrt.io import (
    ClientBootstrap,
    ClientTlsContext,
    DefaultHostResolver,
    EventLoopGroup,
    LogLevel,
    Pkcs11Lib,
    TlsConnectionOptions,
    TlsContextOptions,
    init_logging,
)
from awscrt.mqtt import Connection
from awsiot import mqtt_connection_builder

from ...exceptions import (
    BRSConfigurationError,
    BRSConnectionError,
    BRSRequestError,
    BRSValidationError,
    BRSWarning,
)
from ...utils import (
    PKCS11,
    AWSCRTResponse,
    Identity,
    TemporaryCredentials,
    Transport,
    refreshable_session,
)
from .core import BaseIoTRefreshableSession

_TEMP_PATHS: list[str] = []


@refreshable_session
class IOTX509RefreshableSession(
    BaseIoTRefreshableSession, registry_key="x509"
):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary credentials returned by the IoT Core credential provider.

    .. note::

        As of v7.2.0, ``boto3-refresh-session`` requires explicitly installing
        "iot" as an extra dependency in order to use IoT features, i.e.
        ``pip install boto3-refresh-session[iot]``.

    .. tip::

        For additional details on client caching, refer to the
        :ref:`client caching documentation <cachedocs>`.

    Parameters
    ----------
    endpoint : str
        The endpoint URL for the IoT Core credential provider. Must contain
        '.credentials.iot.'.
    role_alias : str
        The IAM role alias to use when requesting temporary credentials.
    certificate : str | bytes
        The X.509 certificate to use when requesting temporary credentials.
        ``str`` represents the file path to the certificate, while ``bytes``
        represents the actual certificate data.
    thing_name : str, optional
        The name of the IoT thing to use when requesting temporary
        credentials. Default is None.
    private_key : str | bytes | None, optional
        The private key to use when requesting temporary credentials. ``str``
        represents the file path to the private key, while ``bytes``
        represents the actual private key data. Optional only if ``pkcs11``
        is provided. Default is None.
    pkcs11 : PKCS11, optional
        The PKCS#11 library to use when requesting temporary credentials. If
        provided, ``private_key`` must be None.
    ca : str | bytes | None, optional
        The CA certificate to use when verifying the IoT Core endpoint. ``str``
        represents the file path to the CA certificate, while ``bytes``
        represents the actual CA certificate data. Default is None.
    verify_peer : bool, optional
        Whether to verify the CA certificate when establishing the TLS
        connection. Default is True.
    timeout : float | int | None, optional
        The timeout for the TLS connection in seconds. Default is 10.0.
    duration_seconds : int | None, optional
        The duration for which the temporary credentials are valid, in
        seconds. Cannot exceed the value declared in the IAM policy.
        Default is None.
    awscrt_log_level : awscrt.LogLevel | None, optional
        The logging level for the AWS CRT library, e.g.
        ``awscrt.LogLevel.INFO``. Default is None.
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.
    advisory_timeout : int, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore will attempt to refresh credentials early according to
        this value (in seconds), but will continue using the existing
        credentials if refresh fails. Default is 15 minutes (900 seconds).
    mandatory_timeout : int, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore requires a successful refresh before continuing. If
        refresh fails in this window (in seconds), API calls may fail.
        Default is 10 minutes (600 seconds).
    cache_clients : bool, optional
        If ``True`` then clients created by this session will be cached and
        reused for subsequent calls to :meth:`client()` with the same
        parameter signatures. Due to the memory overhead of clients, the
        default is ``True`` in order to protect system resources.
    client_cache_max_size : int, optional
        The maximum number of clients to store in the client cache. Only
        applicable if ``cache_clients`` is ``True``. Defaults to 10.

    Other Parameters
    ----------------
    kwargs : dict, optional
        Optional keyword arguments for the :class:`boto3.session.Session`
        object.

    Attributes
    ----------
    client_cache : ClientCache
        The client cache used to store and retrieve cached clients.

    Notes
    -----
    Gavin Adams at AWS was a major influence on this implementation.
    Thank you, Gavin!
    """

    def __init__(
        self,
        endpoint: str,
        role_alias: str,
        certificate: str | bytes,
        thing_name: str | None = None,
        private_key: str | bytes | None = None,
        pkcs11: PKCS11 | None = None,
        ca: str | bytes | None = None,
        verify_peer: bool = True,
        timeout: float | int | None = None,
        duration_seconds: int | None = None,
        awscrt_log_level: LogLevel | None = None,
        **kwargs,
    ):
        # initializing BRSSession
        super().__init__(refresh_method="iot-x509", **kwargs)

        # logging
        if awscrt_log_level:
            init_logging(log_level=awscrt_log_level, file_name="stdout")

        # initializing public attributes
        self.endpoint = self._normalize_iot_credential_endpoint(
            endpoint=endpoint
        )
        self.role_alias = role_alias
        self.certificate = self._read_maybe_path_to_bytes(
            certificate, fallback=None, name="certificate"
        )
        self.thing_name = thing_name
        self.private_key = self._read_maybe_path_to_bytes(
            private_key, fallback=None, name="private_key"
        )
        self.pkcs11 = self._validate_pkcs11(pkcs11) if pkcs11 else None
        self.ca = self._read_maybe_path_to_bytes(ca, fallback=None, name="ca")
        self.verify_peer = verify_peer
        self.timeout = 10.0 if timeout is None else timeout
        self.duration_seconds = duration_seconds

        # either private_key or pkcs11 must be provided
        if self.private_key is None and self.pkcs11 is None:
            raise BRSConfigurationError(
                "Either 'private_key' or 'pkcs11' must be provided.",
                param="private_key/pkcs11",
            )

        # . . . but both cannot be provided!
        if self.private_key is not None and self.pkcs11 is not None:
            raise BRSConfigurationError(
                "Only one of 'private_key' or 'pkcs11' can be provided.",
                param="private_key/pkcs11",
            )

    def _get_credentials(self) -> TemporaryCredentials:
        url = urlparse(
            f"https://{self.endpoint}/role-aliases/{self.role_alias}"
            "/credentials"
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

        try:
            stream = connection.request(
                request, response.on_response, response.on_body
            )
            stream.activate()
            stream.completion_future.result(float(self.timeout))
        finally:
            try:
                connection.close()
            except Exception:
                ...

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
            response_body = json.loads(response.body.decode())
            raise BRSRequestError(
                "Error getting credentials from IoT credential provider.",
                status_code=response.status_code,
                details=response_body,
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
            raise BRSConnectionError(
                "Error completing mTLS connection to endpoint "
                f"'{url.hostname}'",
                param="endpoint",
                value=str(url.hostname),
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
            raise BRSConfigurationError(
                "Attempting to establish mTLS connection using PKCS#11 "
                "but 'pkcs11' parameter is 'None'!",
                param="pkcs11",
            )

        tls_ctx_opt = TlsContextOptions.create_client_with_mtls_pkcs11(
            pkcs11_lib=Pkcs11Lib(file=self.pkcs11["pkcs11_lib"]),
            user_pin=self.pkcs11["user_pin"],
            slot_id=self.pkcs11["slot_id"],
            token_label=self.pkcs11["token_label"],
            private_key_label=self.pkcs11["private_key_label"],
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
            raise BRSConnectionError(
                "Error completing mTLS connection.",
                param="endpoint",
                value=str(url.hostname),
            ) from err

    def get_identity(self) -> Identity:
        """Returns metadata about the current caller identity.

        Returns
        -------
        Identity
            Dict containing information about the current calleridentity.
        """

        return self.client("sts").get_caller_identity()

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
                "you provided was therefore modified from "
                f"'{logged_data_endpoint}' -> '{logged_credential_endpoint}'"
            )
            return endpoint

        raise BRSValidationError(
            "Invalid IoT endpoint provided for credentials provider. "
            "Expected '<id>.credentials.iot.<region>.amazonaws.com'",
            param="endpoint",
            value=endpoint,
        )

    @staticmethod
    def _validate_pkcs11(pkcs11: PKCS11) -> PKCS11:
        if "pkcs11_lib" not in pkcs11:
            raise BRSConfigurationError(
                "PKCS#11 library path must be provided as 'pkcs11_lib'"
                " in 'pkcs11'.",
                param="pkcs11_lib",
            )
        elif not Path(pkcs11["pkcs11_lib"]).expanduser().resolve().is_file():
            raise BRSValidationError(
                f"'{pkcs11['pkcs11_lib']}' is not a valid file path for "
                "'pkcs11_lib' in 'pkcs11'.",
                param="pkcs11_lib",
                value=pkcs11.get("pkcs11_lib"),
            )
        pkcs11.setdefault("user_pin", None)
        pkcs11.setdefault("slot_id", None)
        pkcs11.setdefault("token_label", None)
        pkcs11.setdefault("private_key_label", None)
        return pkcs11

    @staticmethod
    def _read_maybe_path_to_bytes(
        v: str | bytes | None, fallback: bytes | None, name: str
    ) -> bytes | None:
        match v:
            case None:
                return fallback
            case bytes():
                return v
            case str() as p if Path(p).expanduser().resolve().is_file():
                return Path(p).expanduser().resolve().read_bytes()
            case _:
                value = type(v).__name__
                raise BRSValidationError(
                    f"Invalid {name} provided.",
                    param=name,
                    value=value,
                )

    @staticmethod
    def _bytes_to_tempfile(b: bytes, suffix: str = ".pem") -> str:
        f = NamedTemporaryFile("wb", suffix=suffix, delete=False)
        f.write(b)
        f.flush()
        f.close()
        _TEMP_PATHS.append(f.name)
        return f.name

    @staticmethod
    @register
    def _cleanup_tempfiles():
        for p in _TEMP_PATHS:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                ...

    def mqtt(
        self,
        *,
        endpoint: str,
        client_id: str,
        transport: Transport = "x509",
        certificate: str | bytes | None = None,
        private_key: str | bytes | None = None,
        ca: str | bytes | None = None,
        pkcs11: PKCS11 | None = None,
        region: str | None = None,
        keep_alive_secs: int = 60,
        clean_start: bool = True,
        port: int | None = None,
        use_alpn: bool = False,
    ) -> Connection:
        """Establishes an MQTT connection using the specified parameters.

        .. versionadded:: 5.1.0

        Parameters
        ----------
        endpoint: str
            The MQTT endpoint to connect to.
        client_id: str
            The client ID to use for the MQTT connection.
        transport: Transport
            The transport protocol to use (e.g., "x509" or "ws").
        certificate: str | bytes | None, optional
            The client certificate to use for the connection. Defaults to the
            session certificate.
        private_key: str | bytes | None, optional
            The private key to use for the connection. Defaults to the
            session private key.
        ca: str | bytes | None, optional
            The CA certificate to use for the connection. Defaults to the
            session CA certificate.
        pkcs11: PKCS11 | None, optional
            PKCS#11 configuration for hardware-backed keys. Defaults to the
            session PKCS#11 configuration.
        region: str | None, optional
            The AWS region to use for the connection. Defaults to the
            session region.
        keep_alive_secs: int, optional
            The keep-alive interval for the MQTT connection. Default is 60
            seconds.
        clean_start: bool, optional
            Whether to start a clean session. Default is True.
        port: int | None, optional
            The port to use for the MQTT connection. Default is 8883 if not
            using ALPN, otherwise 443.
        use_alpn: bool, optional
            Whether to use ALPN for the connection. Default is False.

        Returns
        -------
        awscrt.mqtt.Connection
            The established MQTT connection.
        """

        # Validate transport
        if transport not in list(get_args(Transport)):
            raise BRSValidationError(
                "Transport must be 'x509' or 'ws'",
                param="transport",
                value=transport,
            )

        # Region default (WS only)
        if region is None:
            region = self.region_name

        # Normalize inputs to bytes using session defaults
        cert_bytes = self._read_maybe_path_to_bytes(
            certificate, getattr(self, "certificate", None), "certificate"
        )
        key_bytes = self._read_maybe_path_to_bytes(
            private_key, getattr(self, "private_key", None), "private_key"
        )
        ca_bytes = self._read_maybe_path_to_bytes(
            ca, getattr(self, "ca", None), "ca"
        )

        # Validate PKCS#11
        match pkcs11:
            case None:
                pkcs11 = getattr(self, "pkcs11", None)
            case dict():
                pkcs11 = self._validate_pkcs11(pkcs11)
            case _:
                raise BRSValidationError(
                    "Invalid PKCS#11 configuration provided.",
                    param="pkcs11",
                    value=type(pkcs11).__name__,
                )

        # X.509 invariants
        if transport == "x509":
            has_key = key_bytes is not None
            has_hsm = pkcs11 is not None
            if not has_key and not has_hsm:
                raise BRSConfigurationError(
                    "For transport='x509', provide either 'private_key' "
                    "(bytes/path) or 'pkcs11'.",
                    param="private_key/pkcs11",
                )
            if has_key and has_hsm:
                raise BRSConfigurationError(
                    "Provide only one of 'private_key' or 'pkcs11' for "
                    "transport='x509'.",
                    param="private_key/pkcs11",
                )
            if cert_bytes is None:
                raise BRSConfigurationError(
                    "Certificate is required for transport='x509'",
                    param="certificate",
                )

        # CRT bootstrap
        event_loop = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop)
        bootstrap = io.ClientBootstrap(event_loop, host_resolver)

        # Build connection
        if transport == "x509":
            if pkcs11 is not None:
                # Cert must be a filepath for PKCS#11 builder → write temp
                cert_path = self._bytes_to_tempfile(
                    cast(bytes, cert_bytes), ".crt"
                )
                ca_path = (
                    self._bytes_to_tempfile(ca_bytes, ".pem")
                    if ca_bytes
                    else None
                )

                return mqtt_connection_builder.mtls_with_pkcs11(
                    endpoint=endpoint,
                    client_bootstrap=bootstrap,
                    pkcs11_lib=Pkcs11Lib(file=pkcs11["pkcs11_lib"]),
                    user_pin=pkcs11.get("user_pin"),
                    slot_id=pkcs11.get("slot_id"),
                    token_label=pkcs11.get("token_label"),
                    private_key_object=pkcs11.get("private_key_label"),
                    cert_filepath=cert_path,
                    ca_filepath=ca_path,
                    client_id=client_id,
                    clean_session=clean_start,
                    keep_alive_secs=keep_alive_secs,
                    port=port or (443 if use_alpn else 8883),
                    alpn_list=["x-amzn-mqtt-ca"] if use_alpn else None,
                )
            else:
                # pure mTLS with in-memory cert/key/CA
                return mqtt_connection_builder.mtls_from_bytes(
                    endpoint=endpoint,
                    cert_bytes=cert_bytes,
                    pri_key_bytes=key_bytes,
                    ca_bytes=ca_bytes,
                    client_bootstrap=bootstrap,
                    client_id=client_id,
                    clean_session=clean_start,
                    keep_alive_secs=keep_alive_secs,
                    port=port or (443 if use_alpn else 8883),
                    alpn_list=["x-amzn-mqtt-ca"] if use_alpn else None,
                )

        else:  # transport == "ws"
            # WebSockets + SigV4
            creds_provider = auth.AwsCredentialsProvider.new_delegate(
                self._credentials
            )
            ca_path = (
                self._bytes_to_tempfile(ca_bytes, ".pem") if ca_bytes else None
            )

            return mqtt_connection_builder.websockets_with_default_aws_signing(
                endpoint=endpoint,
                client_bootstrap=bootstrap,
                region=region,
                credentials_provider=creds_provider,
                client_id=client_id,
                clean_session=clean_start,
                keep_alive_secs=keep_alive_secs,
                ca_filepath=ca_path,
                port=port or 443,
            )
