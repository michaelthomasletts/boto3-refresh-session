from logging import INFO, getLogger
from os import getenv

from boto3_refresh_session import AutoRefreshableSession

logger = getLogger(__name__)


def test_defer_refresh():
    # testing defer_refresh = True
    logger.info("Testing AutoRefreshableSession with defer_refresh = True")
    session = AutoRefreshableSession(
        region="us-east-1",
        role_arn=getenv("ROLE_ARN"),
        session_name="test_boto3_refresh_session_1",
        defer_refresh=True,
    ).session
    s3 = session.client(service_name="s3")

    # testing defer_refresh = False
    logger.info("Testing AutoRefreshableSession with defer_refresh = False")
    session = AutoRefreshableSession(
        region="us-east-1",
        role_arn=getenv("ROLE_ARN"),
        session_name="test_boto3_refresh_session_2",
        defer_refresh=False,
    ).session
    s3 = session.client(service_name="s3")
