# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Public factory for constructing refreshable boto3 sessions."""

from __future__ import annotations

__all__ = ["RefreshableSession"]

from typing import get_args

from .exceptions import BRSValidationError
from .utils import BaseRefreshableSession, PublicMethod


class RefreshableSession:
    """Factory class for constructing refreshable boto3 sessions using various
    authentication methods, e.g. STS.

    This class provides a unified interface for creating boto3 sessions whose
    credentials are automatically refreshed in the background.

    Use ``RefreshableSession(method="...")`` to construct an instance using
    the desired method.

    For additional information on required parameters, refer to the See Also
    section below.

    Parameters
    ----------
    method : PublicMethod
        The authentication and refresh method to use for the session. Must
        match a registered method name. Options include "sts", "custom", and
        "iot". Default is "sts".
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
    **kwargs : dict
        Additional keyword arguments forwarded to the constructor of the
        selected session class.

    Attributes
    ----------
    client_cache : ClientCache
        The client cache used to store and retrieve cached clients.

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
    ...     assume_role_kwargs=AssumeRoleConfig(RoleArn="<your-role-arn>"),
    ...     region_name="us-east-1"
    ... )
    >>> s3 = session.client("s3")
    """

    def __new__(
        cls, method: PublicMethod = "sts", **kwargs
    ) -> BaseRefreshableSession:
        if method not in (methods := cls.get_available_methods()):
            raise BRSValidationError(
                f"{method!r} is an invalid method parameter. "
                "Available methods are "
                f"{', '.join(repr(meth) for meth in methods)}.",
                param="method",
                value=method,
            )

        return BaseRefreshableSession.registry[method](**kwargs)

    @classmethod
    def get_available_methods(cls) -> list[str]:
        """Lists all currently available credential refresh methods.

        Returns
        -------
        list[str]
            A list of all currently available credential refresh methods,
            e.g. 'sts', 'custom'.
        """

        return list(get_args(PublicMethod))
