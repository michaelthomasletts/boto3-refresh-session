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


def test_assume_role_config_setdefault_does_not_overwrite():
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    config["ExternalId"] = "original"
    assert config.setdefault("ExternalId", "new") == "original"
    assert config["ExternalId"] == "original"


def test_assume_role_config_none_removes_key():
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    config["ExternalId"] = "external"
    assert "ExternalId" in config
    config["ExternalId"] = None
    assert "ExternalId" not in config
    assert config.ExternalId is None


def test_assume_role_config_pop_and_popitem():
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    config["ExternalId"] = "external"
    config["SourceIdentity"] = "source"

    key, value = config.popitem()
    assert key in {"ExternalId", "SourceIdentity"}
    assert value in {"external", "source"}
    assert key not in config

    remaining = config.pop("ExternalId", None) or config.pop("SourceIdentity")
    assert remaining in {"external", "source"}


def test_sts_client_config_service_name_normalizes():
    config = STSClientConfig()
    assert config["service_name"] == "sts"

    with pytest.warns(BRSWarning):
        config["service_name"] = "ec2"
    assert config["service_name"] == "sts"

    with pytest.raises(BRSValidationError):
        config["service_name"] = 123


def test_sts_client_config_dot_notation_returns_none():
    config = STSClientConfig(region_name="us-east-1")

    assert config.region_name == "us-east-1"
    config.region_name = "us-west-2"
    assert config["region_name"] == "us-west-2"

    assert config.endpoint_url is None
    assert "endpoint_url" not in config
