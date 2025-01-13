from __future__ import annotations

__all__ = ["AutoRefreshableSession"]

from typing import Type

from attrs import define, field
from attrs.validators import instance_of, le, optional
from boto3 import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session


@define
class AutoRefreshableSession:
    """Returns a boto3 Session object which refreshes automatically, no extra
    steps required.

    This object is useful for long-running processes where temporary credentials
    may expire between iterations.

    To use this class, you must have `~/.aws/config` or `~/.aws/credentials`
    on your machine.

    Attributes
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
        Optional keyword arguments for `boto3.Session`.
    client_kwargs : dict, optional
        Optional keyword arguments for `boto3.Session.client`.

    Other Attributes
    ----------------
    session
        Returns a boto3 Session object with credentials which refresh
        automatically.

    Notes
    -----
    boto3 employs a variety of methods (in order) to identify credentials:

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    This class assumes that `~/.aws` exists with `/config` or `/credentials`!

    Examples
    --------
    Here's how to initialize the `boto3.Client.S3` object:

    >>> from boto3_refresh_session import AutoRefreshableSession
    >>> session = AutoRefreshableSession(
    >>>   region="us-east-1",
    >>>   role_arn="<your-arn>",
    >>>   session_name="test",
    >>> )
    >>> s3_client = session.session.client(service_name="s3")
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
        __response = __client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=self.ttl,
        )
        return {
            "access_key": __response.get("AccessKeyId"),
            "secret_key": __response.get("SecretAccessKey"),
            "token": __response.get("SessionToken"),
            "expiry_time": __response.get("Expiration").isoformat(),
        }
