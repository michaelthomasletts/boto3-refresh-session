import pytest

from boto3_refresh_session.exceptions import BRSValidationError, BRSWarning
from boto3_refresh_session.utils import AssumeRoleConfig, STSClientConfig


def test_assume_role_config_behaves_like_dict():
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    assert config["RoleArn"] == "arn:aws:iam::123456789012:role/TestRole"
    assert config.RoleSessionName == "unit-test"
    assert config.SerialNumber is None
    assert "SerialNumber" not in config

    config["ExternalId"] = "external"
    assert config.ExternalId == "external"

    config.TokenCode = "123456"
    assert config["TokenCode"] == "123456"

    assert {**config} == {
        "RoleArn": "arn:aws:iam::123456789012:role/TestRole",
        "RoleSessionName": "unit-test",
        "ExternalId": "external",
        "TokenCode": "123456",
    }


def test_assume_role_config_validation():
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    with pytest.raises(BRSValidationError):
        config["NotAKey"] = "nope"

    with pytest.raises(BRSValidationError):
        config.TokenCode = "bad"

    with pytest.raises(AttributeError):
        _ = config.NotAKey


def test_assume_role_config_setdefault_validates():
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    assert config.setdefault("ExternalId", "external") == "external"
    assert config["ExternalId"] == "external"

    with pytest.raises(BRSValidationError):
        config.setdefault("NotAKey", "nope")


def test_sts_client_config_service_name_normalizes():
    config = STSClientConfig()
    assert config["service_name"] == "sts"

    with pytest.warns(BRSWarning):
        config["service_name"] = "ec2"
    assert config["service_name"] == "sts"

    with pytest.raises(BRSValidationError):
        config["service_name"] = 123
