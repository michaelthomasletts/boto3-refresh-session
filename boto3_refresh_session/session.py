from __future__ import annotations

__doc__ = """
Helper method for generating an automatically refreshing :class:`boto3.session.Session`
object.

.. warning::
    ``AutoRefreshableSession`` was not tested for manually passing hard-coded
    account credentials to the ``boto3.client`` object! There is an optional 
    ``client_kwargs`` parameter available for doing so, which *should* work; 
    however, that cannot be guaranteed as that functionality was not tested.
    Pass hard-coded credentials with the ``client_kwargs`` parameter at your
    own discretion.
"""
__all__ = ["AutoRefreshableSession"]

from logging import INFO, basicConfig, getLogger
from typing import Type

from attrs import define, field
from attrs.validators import ge, instance_of, optional
from boto3 import Session, client
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)
from botocore.session import get_session

# configuring logging
basicConfig(
    level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# creating logger
logger = getLogger(__name__)


@define
class AutoRefreshableSession:
    """Returns a :class:`boto3.session.Session` object which refreshes automatically, no extra
    steps required.

    This object is useful for long-running processes where temporary credentials
    may expire.

    Parameters
    ----------
    region : str
        AWS region name.
    role_arn : str
        AWS role ARN.
    session_name : str
        Name for session.
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed until
        they are explicitly needed. If ``False`` then temporary credentials refresh
        immediately upon expiration. Default is ``True``.
    ttl : int, optional
        Number of seconds until temporary credentials expire. Must be greater than or
        equal to 900 seconds. Default is 900.
    session_kwargs : dict, optional
        Optional keyword arguments for :class:`boto3.session.Session`.
    client_kwargs : dict, optional
        Optional keyword arguments for ``boto3.client``.

    Attributes
    ----------
    session
        Returns a :class:`boto3.session.Session` object with credentials which refresh
        automatically.

    Notes
    -----
    Check the :ref:`authorization documentation <authorization>` for additional
    information concerning how to authorize access to AWS.

    The default ``defer_refresh`` parameter value results in temporary credentials not
    being refreshed until they are explicitly requested; that is more efficient than
    refreshing expired temporary credentials automatically after they expire.

    Examples
    --------
    Here's how to initialize this object:

    >>> sess = brs.AutoRefreshableSession(
    >>>   region="us-east-1",
    >>>   role_arn="<your-arn>",
    >>>   session_name="test",
    >>> )
    >>> s3_client = sess.session.client(service_name="s3")
    """

    region: str = field(validator=instance_of(str))
    role_arn: str = field(validator=instance_of(str))
    session_name: str = field(validator=instance_of(str))
    defer_refresh: bool = field(default=True, validator=instance_of(bool))
    ttl: int = field(
        default=900, validator=optional([instance_of(int), ge(900)])
    )
    session_kwargs: dict = field(
        default={}, validator=optional(instance_of(dict))
    )
    client_kwargs: dict = field(
        default={}, validator=optional(instance_of(dict))
    )
    session: Type[Session] = field(init=False)
    _creds_already_fetched: int = field(init=False, default=0)

    def __attrs_post_init__(self):
        __session = get_session()

        logger.info("Fetching temporary AWS credentials.")

        if not self.defer_refresh:
            __credentials = RefreshableCredentials.create_from_metadata(
                metadata=self._get_credentials(),
                refresh_using=self._get_credentials,
                method="sts-assume-role",
            )
        else:
            __credentials = DeferredRefreshableCredentials(
                refresh_using=self._get_credentials, method="sts-assume-role"
            )

        __session._credentials = __credentials
        self.session = Session(
            botocore_session=__session, **self.session_kwargs
        )

    def _get_credentials(self) -> dict:
        """Returns temporary credentials via AWS STS.

        Returns
        -------
        dict
            AWS temporary credentials.
        """

        # being careful not to duplicate logs
        msg = "Refreshing temporary AWS credentials"
        if self.defer_refresh and self._creds_already_fetched:
            logger.info(msg)
        elif not self.defer_refresh and self._creds_already_fetched > 1:
            logger.info(msg)
        else:
            self._creds_already_fetched += 1

        __sts_client = client(
            service_name="sts", region_name=self.region, **self.client_kwargs
        )
        __temporary_credentials = __sts_client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=self.ttl,
        )["Credentials"]
        return {
            "access_key": __temporary_credentials.get("AccessKeyId"),
            "secret_key": __temporary_credentials.get("SecretAccessKey"),
            "token": __temporary_credentials.get("SessionToken"),
            "expiry_time": __temporary_credentials.get(
                "Expiration"
            ).isoformat(),
        }
