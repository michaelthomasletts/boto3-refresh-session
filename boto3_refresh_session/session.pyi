# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Public factory for constructing refreshable boto3 sessions."""

from __future__ import annotations

__all__ = ["RefreshableSession"]

from typing import Any, Literal, overload

from botocore.client import BaseClient

from .methods.custom import CustomRefreshableSession
from .methods.iot import IOTX509RefreshableSession
from .methods.sts import STSRefreshableSession
from .utils import Method
from .utils.cache import ClientCache
from .utils.typing import Identity, TemporaryCredentials, Transport, PKCS11

class RefreshableSession:
    """Factory class for constructing refreshable boto3 sessions using various
    authentication methods, e.g. STS.

    For additional information on required and optional parameters for each
    ``method``, refer to the `refresh strategies documentation
    <https://michaelthomasletts.com/boto3-refresh-session/api/index.html#refresh-strategies>`_.
    For additional details on client caching, refer to the
    `client caching usage documentation <https://michaelthomasletts.com/boto3-refresh-session/usage.html#client-caching>`_
    or `API docs <https://michaelthomasletts.com/boto3-refresh-session/api/cache.html>`_ for technical information. For additional
    details on configuring MFA, refer to the
    `MFA usage documentation <https://michaelthomasletts.com/boto3-refresh-session/usage.html#mfa>`_.

    Parameters
    ----------
    method : Literal["sts", "custom", "iot"], optional
        The authentication and refresh method to use for the session. Must
        match a registered method name. Options include "sts", "custom", and
        "iot". "iot" requires explicitly installing the "iot" extra, i.e.
        ``pip install boto3-refresh-session[iot]``. Default is "sts".
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
    **kwargs : dict[str, Any], optional
        Additional keyword arguments forwarded to the constructor of the
        selected session class.

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
    refreshable_credentials() -> TemporaryCredentials
        Returns the current temporary AWS credentials.
    whoami() -> Identity
        Alias for :meth:`get_identity`.

    See Also
    --------
    boto3_refresh_session.methods.custom.CustomRefreshableSession
    boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession
    boto3_refresh_session.methods.sts.STSRefreshableSession
    boto3_refresh_session.utils.config.AssumeRoleConfig
    boto3_refresh_session.utils.config.STSClientConfig

    Examples
    --------

    Basic initialization using STS AssumeRole (i.e. ``method="sts"``):

    >>> from boto3_refresh_session import AssumeRoleConfig, RefreshableSession
    >>> session = RefreshableSession(
    ...     assume_role_kwargs=AssumeRoleConfig(RoleArn="<your-role-arn>")
    ... )

    Basic initialization using a custom credential callable
    (i.e. ``method="custom"``):

    >>> from boto3_refresh_session import AssumeRoleConfig, RefreshableSession
    >>> def custom_credential_provider(...):
    ...     ...
    ...     return {"AccessKeyId": "...",
    ...             "SecretAccessKey": "...",
    ...             "SessionToken": "...",
    ...             "Expiration": datetime.datetime(...)}
    ...
    >>> session = RefreshableSession(
    ...     method="custom",
    ...     custom_credentials_method=custom_credential_provider,
    ...     custom_credentials_method_args={...},
    ... )

    Basic initialization using IoT X.509 (i.e. ``method="iot"``):

    >>> from boto3_refresh_session import AssumeRoleConfig, RefreshableSession
    >>> session = RefreshableSession(
    ...     method="iot",
    ...     iot_endpoint="your-iot-endpoint",
    ...     thing_name="your-thing-name",
    ...     role_alias="your-role-alias",
    ...     certificate_path="path/to/certificate.pem.crt",
    ...     private_key_path="path/to/private.pem.key",
    ... )
    """

    client_cache: ClientCache
    """The client cache used to store and retrieve cached clients."""

    @property
    def credentials(self) -> TemporaryCredentials:
        """The current temporary AWS security credentials."""

        ...

    def client(self, *args: Any, **kwargs: Any) -> BaseClient:
        """Creates a low-level service client by name.

        Parameters
        ----------
        *args : Any
            Positional arguments for :meth:`boto3.session.Session.client`.
        **kwargs : Any
            Keyword arguments for :meth:`boto3.session.Session.client`.

        Returns
        -------
        BaseClient
            A low-level service client.

        Notes
        -----
        This method overrides the default
        :meth:`boto3.session.Session.client` method. If client caching is
        enabled, it will return a cached client instance for the given
        service and parameters. Else, it will create and return a new client
        instance.
        """

        ...

    def get_identity(self) -> Identity:
        """Returns metadata about the current caller identity.

        Returns
        -------
        Identity
            Dict containing caller identity metadata.
        """

        ...

    def refreshable_credentials(self) -> TemporaryCredentials:
        """The current temporary AWS security credentials.

        Returns
        -------
        TemporaryCredentials
            Temporary AWS security credentials containing:
                access_key : str
                    AWS access key identifier.
                secret_key : str
                    AWS secret access key.
                token : str
                    AWS session token.
                expiry_time : str
                    Expiration timestamp in ISO 8601 format.
        """

        ...

    def whoami(self) -> Identity:
        """Returns metadata about the identity assumed.

        .. versionadded:: 7.2.15

        .. note::

            This method is an alternative to ``get_identity()``.

        Returns
        -------
        Identity
            Dict containing caller identity according to AWS STS.
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
    ) -> Any:
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

    @classmethod
    def get_available_methods(cls) -> list[str]:
        """Lists all currently available credential refresh methods.

        Returns
        -------
        list[str]
            A list of all currently available credential refresh methods,
            e.g. 'sts', 'custom'.
        """

        ...

    def _get_credentials(self) -> TemporaryCredentials: ...
    @overload
    def __new__(
        cls, method: Literal["sts"] = "sts", **kwargs: Any
    ) -> STSRefreshableSession: ...
    @overload
    def __new__(
        cls, method: Literal["custom"], **kwargs: Any
    ) -> CustomRefreshableSession: ...
    @overload
    def __new__(
        cls, method: Literal["iot"], **kwargs: Any
    ) -> IOTX509RefreshableSession: ...
    @overload
    def __new__(
        cls, method: Method = "sts", **kwargs: Any
    ) -> STSRefreshableSession: ...
