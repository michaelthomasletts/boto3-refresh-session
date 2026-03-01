# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Public factory for constructing refreshable boto3 sessions."""

from __future__ import annotations

__all__ = ["RefreshableSession"]

from typing import List, TypeAlias, get_args

from .exceptions import BRSValidationError
from .methods.custom import CustomRefreshableSession
from .methods.sts import STSRefreshableSession
from .utils import IOT_EXTRA_INSTALLED, Method, Registry

# defining this here instead of utils.typing to avoid circular imports
if not IOT_EXTRA_INSTALLED:
    RefreshableSessionType: TypeAlias = (  # type: ignore
        STSRefreshableSession | CustomRefreshableSession  # type: ignore
    )
else:
    from .methods.iot.x509 import IOTX509RefreshableSession

    RefreshableSessionType: TypeAlias = (  # type: ignore
        STSRefreshableSession  # type: ignore
        | CustomRefreshableSession  # type: ignore
        | IOTX509RefreshableSession
    )


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
    cache : SessionCache
        The client and resource cache used to store and retrieve cached
        clients.
    credentials : TemporaryCredentials
        The temporary AWS security credentials.

    Methods
    -------
    client(*args, eviction_policy: EvictionPolicy, max_size: int, **kwargs) -> BaseClient
        Creates a low-level service client by name.
    get_identity() -> Identity
        Returns metadata about the current caller identity.
    refreshable_credentials() -> TemporaryCredentials
        Returns the current temporary AWS security credentials.
    resource(*args, eviction_policy: EvictionPolicy, max_size: int, **kwargs) -> ServiceResource
        Creates a low-level service resource by name.
    whoami() -> Identity
        Alias for :meth:`get_identity`.

    Returns
    -------
    boto3_refresh_session.methods.sts.STSRefreshableSession
        If ``method="sts"`` (or not specified) then an instance of
        :class:`boto3_refresh_session.methods.sts.STSRefreshableSession`
        is returned.
    boto3_refresh_session.methods.custom.CustomRefreshableSession
        If ``method="custom"`` then an instance of
        :class:`boto3_refresh_session.methods.custom.CustomRefreshableSession`
        is returned.
    boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession
        If ``method="iot"`` then an instance of
        :class:`boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession`
        is returned.

    See Also
    --------
    boto3_refresh_session.methods.custom.CustomRefreshableSession
    boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession
    boto3_refresh_session.methods.sts.STSRefreshableSession
    boto3_refresh_session.utils.config.AssumeRoleConfig
    boto3_refresh_session.utils.config.STSClientConfig

    Notes
    -----
    .. note::

        For additional details on client and resource caching, refer to the
        :ref:`usage docs <cachedocs>`.

    .. note::

        For additional details on configuring MFA, refer to the
        :ref:`MFA usage docs <mfa>`.

    .. important::

        ``method="iot"`` requires the installation of the ``iot`` extra via
        pip:

        .. code-block:: bash

            pip install boto3-refresh-session[iot]

    Examples
    --------

    Basic initialization using STS AssumeRole (i.e. ``method="sts"``):

    >>> from boto3_refresh_session import (
    ...     AssumeRoleConfig, RefreshableSession
    ... )
    >>> session = RefreshableSession(
    ...     assume_role_kwargs=AssumeRoleConfig(
    ...         RoleArn="<your-role-arn>"
    ...     ),
    ... )
    >>> s3 = session.client("s3")
    >>> s3.list_buckets()

    Basic initialization using a custom credential callable
    (i.e. ``method="custom"``):

    >>> from boto3_refresh_session import RefreshableSession
    >>> def provider(...):
    ...     ...
    ...     return {"access_key": "...",
    ...             "secret_key": "...",
    ...             "token": "...",
    ...             "expiry_time": "..."}
    ...
    >>> session = RefreshableSession(
    ...     method="custom",
    ...     custom_credentials_method=provider,
    ...     custom_credentials_method_args={...},
    ... )
    >>> cloudwatch = session.client("logs")
    >>> cloudwatch.list_logs()

    Basic initialization using IoT X.509 (i.e. ``method="iot"``):

    >>> from boto3_refresh_session import RefreshableSession
    >>> session = RefreshableSession(
    ...     method="iot",
    ...     endpoint="<your-iot-endpoint>",
    ...     thing_name="<your-thing-name>",
    ...     role_alias="<your-role-alias>",
    ...     certificate="path/to/certificate.pem.crt",
    ...     private_key="path/to/private.pem.key",
    ... )
    >>> s3 = session.client("s3")
    >>> s3.list_buckets()
    """  # noqa: E501

    # actual implementation
    def __new__(
        cls, method: Method = "sts", **kwargs
    ) -> RefreshableSessionType:
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
