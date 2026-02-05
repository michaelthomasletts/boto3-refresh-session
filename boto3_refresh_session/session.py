# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Public factory for constructing refreshable boto3 sessions."""

from __future__ import annotations

from boto3_refresh_session.methods.custom import CustomRefreshableSession
from boto3_refresh_session.methods.iot.x509 import IOTX509RefreshableSession
from boto3_refresh_session.methods.sts import STSRefreshableSession

__all__ = ["RefreshableSession"]

from typing import List, get_args

from .exceptions import BRSValidationError
from .utils import Method, Registry


class RefreshableSession:
    """Factory class for configuring boto3 sessions with various different
    `automatic credential refresh methods <../index.html#refresh-strategies>`_.

    Parameters
    ----------
    method : Literal["sts", "custom", "iot"] = "sts", optional
        The automatic credential refresh method to use for the session. It must
        match a registered method name. Options include
        ``"sts" | "custom" | "iot"``. Default is ``"sts"``.
    defer_refresh : bool = True, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.
    advisory_timeout : int = 900, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore will attempt to refresh credentials early according to
        this value (in seconds), but will continue using the existing
        credentials if refresh fails. Default is 15 minutes (900 seconds).
    mandatory_timeout : int = 600, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore requires a successful refresh before continuing. If
        refresh fails in this window (in seconds), API calls may fail.
        Default is 10 minutes (600 seconds).
    cache_clients : bool = True, optional
        If ``True`` then clients created by this session will be cached and
        reused for subsequent calls to :meth:`client()` with the same
        parameter signatures. Due to the memory overhead of clients, the
        default is ``True`` in order to protect system resources.
    client_cache_max_size : int = 10, optional
        The maximum number of clients to store in the client cache. Only
        applicable if ``cache_clients`` is ``True``. Defaults to 10.

    Other Parameters
    ----------------
    **kwargs : Any, optional
        Refer to the
        `automatic credential refresh strategies docs
        <../index.html#refresh-strategies>`_
        for details on what arguments are accepted by each automatic
        credential refresh method.

        Refer to the :class:`boto3.session.Session`
        docs for additional information on configuring boto3 sessions.

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

    Notes
    -----
    For additional details on client caching, refer to the
    :ref:`usage docs <cachedocs>` or :ref:`API docs <cache>` for technical
    information.

    For additional details on configuring MFA, refer to the
    :ref:`MFA usage docs <mfa>`.

    ``method="iot"`` requires the installation of the ``iot`` extra via pip:

    .. code-block:: bash

        pip install boto3-refresh-session[iot]

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

    # actual implementation
    def __new__(  # type: ignore[reportIncompatibleMethodOverride]
        cls, method: Method = "sts", **kwargs
    ) -> (
        STSRefreshableSession
        | CustomRefreshableSession  # type: ignore
        | IOTX509RefreshableSession
    ):
        if method not in (methods := cls.get_available_methods()):
            raise BRSValidationError(
                f"{method!r} is an invalid method parameter. "
                "Available methods are "
                f"{', '.join(repr(meth) for meth in methods)}. "
                "If you are trying to use method='iot', ensure you have "
                "installed the 'iot' extra via pip install "
                "boto3-refresh-session[iot]",
                param="method",
                value=method,
            ) from None

        return Registry.registry[method](**kwargs)

    @classmethod
    def get_available_methods(cls) -> List[str]:
        """Lists all currently available credential refresh methods.

        Returns
        -------
        List[str]
            A list of all currently available credential refresh methods,
            e.g. 'sts', 'custom', etc.
        """

        return list(get_args(Method))
