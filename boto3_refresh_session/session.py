from __future__ import annotations

__doc__ = """
Helper method for generating an automatically refreshing :class:`boto3.session.Session`
object.

.. warning::
    ``AutoRefreshableSession`` was not tested for manually passing hard-coded
    account credentials to the :class:`boto3.session.Session` or ``boto3.client`` 
    objects! There are optional ``session_kwargs`` and ``client_kwargs``
    parameters available for passing hard-coded account credentials, which
    should work; however, that cannot be guaranteed! In any case, the ``boto3``
    documentation generally recommends against passing hard-coded account credentials
    as parameters; it is for that reason the documentation below, and everywhere
    else, only mentions ``~/.aws/config`` and ``~/.aws/credentials`` for 
    authorization. Since the ``session_kwargs`` and ``client_kwargs`` parameters 
    were not tested, you will need to use those parameters at your own discretion.
"""
__all__ = ["AutoRefreshableSession"]

from typing import Type

from attrs import define, field
from attrs.validators import instance_of, le, optional
from boto3 import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session


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
    ttl : int, optional
        Number of seconds until temporary credentials expire, default 900.
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

    Examples
    --------
    Here's how to initialize this object:

    >>> sess = AutoRefreshableSession(
    >>>   region="us-east-1",
    >>>   role_arn="<your-arn>",
    >>>   session_name="test",
    >>> )
    >>> s3_client = sess.session.client(service_name="s3")
    """

    region: str = field(validator=instance_of(str))
    role_arn: str = field(validator=instance_of(str))
    session_name: str = field(validator=instance_of(str))
    ttl: int = field(
        default=900, validator=optional([instance_of(int), le(900)])
    )
    session_kwargs: dict = field(
        default={}, validator=optional(instance_of(dict))
    )
    client_kwargs: dict = field(
        default={}, validator=optional(instance_of(dict))
    )
    session: Type[Session] = field(init=False)

    def __attrs_post_init__(self):
        __credentials = RefreshableCredentials.create_from_metadata(
            metadata=self._get_credentials(),
            refresh_using=self._get_credentials,
            method="sts-assume-role",
        )
        __session = get_session()
        # https://github.com/boto/botocore/blob/f8a1dd0820b548a5e8dc05420b28b6f1c6e21154/botocore/session.py#L143
        __session._credentials = __credentials
        self.session = Session(botocore_session=__session)

    def _get_credentials(self) -> dict:
        """Returns temporary credentials via AWS STS.

        Returns
        -------
        dict
            AWS temporary credentials.
        """

        __session = Session(region_name=self.region, **self.session_kwargs)
        __client = __session.client(
            service_name="sts", region_name=self.region, **self.client_kwargs
        )
        __temporary_credentials = __client.assume_role(
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
