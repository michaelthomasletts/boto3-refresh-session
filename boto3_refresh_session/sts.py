from __future__ import annotations

__doc__ = """
boto3_refresh_session.sts
=========================

Implements the STS-based credential refresh strategy for use with 
:class:`boto3_refresh_session.session.RefreshableSession`.

This module defines the :class:`STSRefreshableSession` class, which uses 
IAM role assumption via STS to automatically refresh temporary credentials 
in the background.

.. versionadded:: 1.1.0

Examples
--------
>>> from boto3_refresh_session import RefreshableSession
>>> session = RefreshableSession(
...     method="sts",
...     assume_role_kwargs={
...         "RoleArn": "arn:aws:iam::123456789012:role/MyRole",
...         "RoleSessionName": "my-session"
...     },
...     region_name="us-east-1"
... )
>>> s3 = session.client("s3")
>>> s3.list_buckets()

.. seealso::
    :class:`boto3_refresh_session.session.RefreshableSession`

STS
---    

.. autosummary::
   :toctree: generated/
   :nosignatures:

   STSRefreshableSession
"""
__all__ = ["STSRefreshableSession"]

from typing import Any
from warnings import warn

from .session import BaseRefreshableSession


class STSRefreshableSession(BaseRefreshableSession, method="sts"):
    """A :class:`boto3.session.Session` object that automatically refreshes temporary AWS
    credentials using an IAM role that is assumed via STS.

    Parameters
    ----------
    assume_role_kwargs : dict
        Required keyword arguments for :meth:`STS.Client.assume_role` (i.e. boto3 STS client).
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed until
        they are explicitly needed. If ``False`` then temporary credentials refresh
        immediately upon expiration. It is highly recommended that you use ``True``.
        Default is ``True``.
    sts_client_kwargs : dict, optional
        Optional keyword arguments for the :class:`STS.Client` object. Do not provide
        values for ``service_name`` as they are unnecessary. Default is None.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments for the :class:`boto3.session.Session` object.
    """

    def __init__(
        self,
        assume_role_kwargs: dict,
        defer_refresh: bool = None,
        sts_client_kwargs: dict | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        defer_refresh = defer_refresh is not False
        self.assume_role_kwargs = assume_role_kwargs

        if sts_client_kwargs is not None:
            # overwriting 'service_name' in case it appears in sts_client_kwargs
            if "service_name" in sts_client_kwargs:
                warn(
                    "The sts_client_kwargs parameter cannot contain values for service_name. Reverting to service_name = 'sts'."
                )
                del sts_client_kwargs["service_name"]
            self._sts_client = self.client(
                service_name="sts", **sts_client_kwargs
            )
        else:
            self._sts_client = self.client(service_name="sts")

        # mounting refreshable credentials
        self._refresh_using(
            credentials_method=self._get_credentials,
            defer_refresh=defer_refresh,
            refresh_method="sts-assume-role",
        )

    def _get_credentials(self) -> dict[str, str]:
        temporary_credentials = self._sts_client.assume_role(
            **self.assume_role_kwargs
        )["Credentials"]
        return {
            "access_key": temporary_credentials.get("AccessKeyId"),
            "secret_key": temporary_credentials.get("SecretAccessKey"),
            "token": temporary_credentials.get("SessionToken"),
            "expiry_time": temporary_credentials.get("Expiration").isoformat(),
        }

    def get_identity(self) -> dict[str, Any]:
        """Returns metadata about the identity assumed.

        Returns
        -------
        dict[str, Any]
            Dict containing caller identity according to AWS STS.
        """

        return self._sts_client.get_caller_identity()
