import logging
from os import getenv

from boto3_refresh_session import RefreshableSession

# configuring logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# creating logger
logger = logging.getLogger(__name__)


def test_defer_refresh():
    # initializing parameters
    region_name = "us-east-1"
    assume_role_kwargs = {
        "RoleArn": getenv("ROLE_ARN"),
        "RoleSessionName": "unit-testing",
        "DurationSeconds": 900,
    }
    sts_client_kwargs = {"region_name": region_name}

    # testing defer_refresh = True
    logger.info("Testing RefreshableSession with defer_refresh = True")
    session = RefreshableSession(
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name=region_name,
    )
    s3 = session.client(service_name="s3")
    s3.list_buckets()

    # testing defer_refresh = False
    logger.info("Testing RefreshableSession with defer_refresh = False")
    session = RefreshableSession(
        defer_refresh=False,
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name=region_name,
    )
    s3 = session.client(service_name="s3")
    s3.list_buckets()
