# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IoT Core X.509 refreshable session implementation."""

from __future__ import annotations

__all__ = ["IOTX509RefreshableSession"]

from typing import Any, TYPE_CHECKING

from awscrt.io import LogLevel

if TYPE_CHECKING:
    from awscrt.mqtt import Connection
else:
    Connection = Any

from ...utils import (
    PKCS11,
    BRSSession,
    CredentialProvider,
    Identity,
    Registry,
    TemporaryCredentials,
    Transport,
)

class IOTX509RefreshableSession(
    Registry, BRSSession, CredentialProvider, registry_key="iot"
):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary credentials returned by the IoT Core credential provider.

    As of v7.2.0, ``boto3-refresh-session`` requires explicitly installing
    "iot" as an extra dependency in order to use IoT features, i.e.
    ``pip install boto3-refresh-session[iot]``.

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
    credentials : TemporaryCredentials
        The temporary AWS security credentials.

    Methods
    -------
    client(*args, **kwargs) -> boto3.client
        Creates a Boto3 client for the specified service.
    get_identity() -> Identity
        Returns metadata about the current caller identity.
    mqtt(...) -> awscrt.mqtt.Connection
        Establishes an MQTT connection using the specified parameters.
    refreshable_credentials() -> TemporaryCredentials
        Returns the current temporary AWS credentials.
    whoami() -> Identity
        Alias for :meth:`get_identity`.

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
        **kwargs: Any,
    ) -> None: ...
    def _get_credentials(self) -> TemporaryCredentials: ...
    def get_identity(self) -> Identity:
        """Returns metadata about the current caller identity.

        Returns
        -------
        Identity
            Dict containing information about the current calleridentity.
        """

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

        ...
