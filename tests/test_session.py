from os import getenv

from boto3_refresh_session import AutoRefreshableSession


def test():
    """Tests whether AutoRefreshableSession can generate a session without errors."""

    session = AutoRefreshableSession(
        region="us-east-1",
        role_arn=getenv("ROLE_ARN"),
        session_name="test_boto3_refresh_session",
    ).session

    s3 = session.client(service_name="s3")
    response = s3.list_buckets()
