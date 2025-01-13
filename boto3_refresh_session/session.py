from __future__ import annotations

__all__ = ["AutoRefreshableSession"]

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
    **kwargs : dict
        Optional keyword arguments for initializing the boto3 `Session` object.

    Methods
    -------
    get_session
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

    def _get_credentials(self) -> dict:
        """Returns temporary credentials via AWS STS.

        Returns
        -------
        dict
            AWS temporary credentials.
        """

        _session = Session(region_name=self.region, **self.session_kwargs)
        _client = _session.client(
            service_name="sts", region_name=self.region, **self.client_kwargs
        )
        _response = _client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=self.ttl,
        )
        return {
            "access_key": _response.get("AccessKeyId"),
            "secret_key": _response.get("SecretAccessKey"),
            "token": _response.get("SessionToken"),
            "expiry_time": _response.get("Expiration").isoformat(),
        }

    @property
    def session(self) -> "Session":
        """Returns a boto3 `Session` object with credentials which refresh
        automatically.

        Returns
        -------
        Session
            boto3 `Session` object.
        """

        if not hasattr(self, "_session"):
            credentials = RefreshableCredentials.create_from_metadata(
                metadata=self._get_credentials(),
                refresh_using=self._get_credentials,
                method="sts-assume-role",
            )
            session = get_session()
            # https://github.com/boto/botocore/blob/f8a1dd0820b548a5e8dc05420b28b6f1c6e21154/botocore/session.py#L143
            session._credentials = credentials
            self._session = Session(botocore_session=session)

        return self._session
