from __future__ import annotations

__doc__ = """
A :class:`boto3.session.Session` object that automatically refreshes temporary
credentials.
"""
__all__ = ["RefreshableSession"]

from typing import Any, Dict
from warnings import warn

from boto3 import client
from boto3.session import Session
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)


class RefreshableSession(Session):
    """Returns a :class:`boto3.session.Session` object with temporary credentials
    that refresh automatically.

    Parameters
    ----------
    assume_role_kwargs : dict
        Required keyword arguments for the :meth:`STS.Client.assume_role` method.
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed until
        they are explicitly needed. If ``False`` then temporary credentials refresh
        immediately upon expiration. It is highly recommended that you use ``True``.
        Default is ``True``.
    sts_client_kwargs : dict, optional
        Optional keyword arguments for the :class:`STS.Client` object. Do not provide
        values for ``service_name``. Default is None.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments for the :class:`boto3.session.Session` object.

    Notes
    -----
    Check the :ref:`authorization documentation <authorization>` for additional
    information concerning how to authorize access to AWS.

    Check the `AWS documentation <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html>`_
    for additional information concerning temporary security credentials in IAM.

    Examples
    --------
    In order to use this object, you are required to configure parameters for the
    :meth:`STS.Client.assume_role` method.

    >>> assume_role_kwargs = {
    >>>     'RoleArn': '<your-role-arn>',
    >>>     'RoleSessionName': '<your-role-session-name>',
    >>>     'DurationSeconds': '<your-selection>',
    >>>     ...
    >>> }

    You may also want to provide optional parameters for the :class:`STS.Client` object.

    >>> sts_client_kwargs = {
    >>>     ...
    >>> }

    You may also provide optional parameters for the :class:`boto3.session.Session` object
    when initializing the ``RefreshableSession`` object. Below, we use the ``region_name``
    parameter for illustrative purposes.

    >>> session = boto3_refresh_session.RefreshableSession(
    >>>     assume_role_kwargs=assume_role_kwargs,
    >>>     sts_client_kwargs=sts_client_kwargs,
    >>>     region_name='us-east-1',
    >>> )

    Using the ``session`` variable that you just created, you can now use all of the methods
    available from the :class:`boto3.session.Session` object. In the below example, we
    initialize an S3 client and list all available buckets.

    >>> s3 = session.client(service_name='s3')
    >>> buckets = s3.list_buckets()

    There are two ways of refreshing temporary credentials automatically with the
    ``RefreshableSession`` object: refresh credentials the moment they expire, or wait until
    temporary credentials are explicitly needed. The latter is the default. The former must
    be configured using the ``defer_refresh`` parameter, as shown below.

    >>> session = boto3_refresh_session.RefreshableSession(
    >>>     defer_refresh=False,
    >>>     assume_role_kwargs=assume_role_kwargs,
    >>>     sts_client_kwargs=sts_client_kwargs,
    >>>     region_name='us-east-1',
    >>> )
    """

    def __init__(
        self,
        assume_role_kwargs: Dict[Any],
        defer_refresh: bool = True,
        sts_client_kwargs: Dict[Any] = None,
        **kwargs,
    ):
        # inheriting from boto3.session.Session
        super().__init__(**kwargs)

        # initializing custom parameters that are necessary outside of __init__
        self.assume_role_kwargs = assume_role_kwargs

        # initializing the STS client
        if sts_client_kwargs is not None:
            # overwriting 'service_name' in case it appears in sts_client_kwargs
            if "service_name" in sts_client_kwargs:
                warn(
                    "The sts_client_kwargs parameter cannot contain values for service_name. Reverting to service_name = 'sts'."
                )
                del sts_client_kwargs["service_name"]
            self._sts_client = client(service_name="sts", **sts_client_kwargs)
        else:
            self._sts_client = client(service_name="sts")

        # determining how exactly to refresh expired temporary credentials
        if not defer_refresh:
            self._session._credentials = (
                RefreshableCredentials.create_from_metadata(
                    metadata=self._get_credentials(),
                    refresh_using=self._get_credentials,
                    method="sts-assume-role",
                )
            )
        else:
            self._session._credentials = DeferredRefreshableCredentials(
                refresh_using=self._get_credentials, method="sts-assume-role"
            )

    def _get_credentials(self) -> Dict[Any]:
        """Returns temporary credentials via AWS STS.

        Returns
        -------
        dict
            AWS temporary credentials.
        """

        # fetching temporary credentials
        temporary_credentials = self._sts_client.assume_role(
            **self.assume_role_kwargs
        )["Credentials"]
        return {
            "access_key": temporary_credentials.get("AccessKeyId"),
            "secret_key": temporary_credentials.get("SecretAccessKey"),
            "token": temporary_credentials.get("SessionToken"),
            "expiry_time": temporary_credentials.get("Expiration").isoformat(),
        }
