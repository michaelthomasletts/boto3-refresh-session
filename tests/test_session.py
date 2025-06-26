import logging
from os import getenv

from boto3_refresh_session import RefreshableSession
import boto3

# configuring logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# creating logger
logger = logging.getLogger(__name__)


def custom_credentials_method() -> dict[str, str]:
    assume_role_kwargs = {
        "RoleArn": getenv("ROLE_ARN"),
        "RoleSessionName": "unit-testing-custom",
        "DurationSeconds": 900,
    }
    temporary_credentials = boto3.client(
        "sts", region_name="us-east-1"
    ).assume_role(**assume_role_kwargs)["Credentials"]
    return {
        "access_key": temporary_credentials.get("AccessKeyId"),
        "secret_key": temporary_credentials.get("SecretAccessKey"),
        "token": temporary_credentials.get("SessionToken"),
        "expiry_time": temporary_credentials.get("Expiration").isoformat(),
    }


def test_custom():
    region_name = "us-east-1"
    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name=region_name,
    )
    s3 = session.client(service_name="s3")


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
