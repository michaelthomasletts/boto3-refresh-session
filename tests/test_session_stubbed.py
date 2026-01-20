from datetime import datetime, timedelta, timezone
from threading import Barrier, Lock, Thread
from time import sleep

import boto3
import pytest
from botocore.config import Config
from botocore.stub import Stubber

from boto3_refresh_session import RefreshableSession
from boto3_refresh_session.exceptions import (
    BRSConfigurationError,
    BRSCredentialError,
    BRSValidationError,
)
from boto3_refresh_session.utils import AssumeRoleConfig
from boto3_refresh_session.methods.iot.x509 import IOTX509RefreshableSession


def _set_dummy_env(monkeypatch) -> None:
    """Dummy AWS env vars for tests."""

    monkeypatch.setenv("access_key", "test-access-key")
    monkeypatch.setenv("secret_key", "test-secret-key")
    monkeypatch.setenv("token", "test-session-token")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


def _stubbed_sts_client(monkeypatch):
    """Stubbed STS client for tests."""

    sts_client = boto3.client("sts", region_name="us-east-1")
    stubber = Stubber(sts_client)
    stubber.activate()

    original_client = boto3.session.Session.client

    def client_override(self, *args, **kwargs):
        service_name = args[0] if args else kwargs.get("service_name")
        if service_name == "sts":
            return sts_client
        return original_client(self, *args, **kwargs)

    monkeypatch.setattr(boto3.session.Session, "client", client_override)
    return stubber


def test_sts_refreshable_credentials_stubbed(monkeypatch):
    """Uses STS Stubber to return refreshable credentials."""

    _set_dummy_env(monkeypatch)
    assume_role_kwargs = {
        "RoleArn": "arn:aws:iam::123456789012:role/TestRole",
        "RoleSessionName": "unit-test",
    }

    stubber = _stubbed_sts_client(monkeypatch)
    stubber.add_response(
        "assume_role",
        {
            "Credentials": {
                "AccessKeyId": "AKIAEXAMPLE123456",
                "SecretAccessKey": "secret",
                "SessionToken": "token",
                "Expiration": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            "AssumedRoleUser": {
                "AssumedRoleId": "AROAEXAMPLE:unit-test",
                "Arn": "arn:aws:sts::123456789012:assumed-role/TestRole/unit-test",
            },
        },
        assume_role_kwargs,
    )
    session = RefreshableSession(
        method="sts",
        assume_role_kwargs=assume_role_kwargs,
        region_name="us-east-1",
        defer_refresh=True,
    )

    try:
        creds = session.refreshable_credentials()
        assert creds["access_key"] == "AKIAEXAMPLE123456"
        assert creds["secret_key"] == "secret"
        assert creds["token"] == "token"
        assert "expiry_time" in creds
    finally:
        stubber.deactivate()


def test_sts_get_identity_stubbed(monkeypatch):
    """Uses STS Stubber to return caller identity."""

    _set_dummy_env(monkeypatch)
    assume_role_kwargs = {
        "RoleArn": "arn:aws:iam::123456789012:role/TestRole",
        "RoleSessionName": "unit-test",
    }

    stubber = _stubbed_sts_client(monkeypatch)
    session = RefreshableSession(
        method="sts",
        assume_role_kwargs=assume_role_kwargs,
        region_name="us-east-1",
        defer_refresh=True,
    )

    stubber.add_response(
        "get_caller_identity",
        {
            "UserId": "AROAEXAMPLE:unit-test",
            "Account": "123456789012",
            "Arn": "arn:aws:sts::123456789012:assumed-role/TestRole/unit-test",
        },
        {},
    )
    try:
        identity = session.get_identity()
        assert identity["Account"] == "123456789012"
    finally:
        stubber.deactivate()


def test_refreshable_session_positional_assume_role_config_rejected():
    """Ensure positional AssumeRoleConfig is not accepted."""

    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    with pytest.raises(TypeError):
        RefreshableSession("sts", config)


def test_refreshable_session_positional_assume_role_config_without_method():
    """Ensure positional AssumeRoleConfig without method is not accepted."""

    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
    )

    with pytest.raises(BRSValidationError):
        RefreshableSession(config)


def test_session_get_credentials_uses_refreshable(monkeypatch):
    """Ensures get_credentials resolves to refreshable credentials."""

    _set_dummy_env(monkeypatch)
    assume_role_kwargs = {
        "RoleArn": "arn:aws:iam::123456789012:role/TestRole",
        "RoleSessionName": "unit-test",
    }

    stubber = _stubbed_sts_client(monkeypatch)
    stubber.add_response(
        "assume_role",
        {
            "Credentials": {
                "AccessKeyId": "AKIAEXAMPLE123456",
                "SecretAccessKey": "secret",
                "SessionToken": "token",
                "Expiration": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            "AssumedRoleUser": {
                "AssumedRoleId": "AROAEXAMPLE:unit-test",
                "Arn": "arn:aws:sts::123456789012:assumed-role/TestRole/unit-test",
            },
        },
        assume_role_kwargs,
    )
    session = RefreshableSession(
        method="sts",
        assume_role_kwargs=assume_role_kwargs,
        region_name="us-east-1",
        defer_refresh=True,
    )

    try:
        frozen = session.get_credentials().get_frozen_credentials()
        assert frozen.access_key == "AKIAEXAMPLE123456"
        assert frozen.secret_key == "secret"
        assert frozen.token == "token"
    finally:
        stubber.deactivate()


def test_sts_refreshable_credentials_with_mfa_stubbed(monkeypatch):
    """Validates MFA token provider is used for STS refresh."""

    _set_dummy_env(monkeypatch)
    assume_role_kwargs = {
        "RoleArn": "arn:aws:iam::123456789012:role/TestRole",
        "RoleSessionName": "unit-test",
        "SerialNumber": "arn:aws:iam::123456789012:mfa/test-user",
    }

    def mfa_token_provider():
        return "123456"

    stubber = _stubbed_sts_client(monkeypatch)
    stubber.add_response(
        "assume_role",
        {
            "Credentials": {
                "AccessKeyId": "AKIAEXAMPLE123456",
                "SecretAccessKey": "secret",
                "SessionToken": "token",
                "Expiration": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            "AssumedRoleUser": {
                "AssumedRoleId": "AROAEXAMPLE:unit-test",
                "Arn": "arn:aws:sts::123456789012:assumed-role/TestRole/unit-test",
            },
        },
        {
            **assume_role_kwargs,
            "TokenCode": "123456",
        },
    )
    session = RefreshableSession(
        method="sts",
        assume_role_kwargs=assume_role_kwargs,
        mfa_token_provider=mfa_token_provider,
        region_name="us-east-1",
        defer_refresh=True,
    )

    try:
        creds = session.refreshable_credentials()
        assert creds["access_key"] == "AKIAEXAMPLE123456"
        assert creds["secret_key"] == "secret"
        assert creds["token"] == "token"
        assert "expiry_time" in creds
    finally:
        stubber.deactivate()


def test_iot_refreshable_credentials_stubbed(monkeypatch):
    """Returns IoT refreshable credentials via patched getter."""

    _set_dummy_env(monkeypatch)

    def fake_get_credentials(self):
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
            "token": "token",
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

    monkeypatch.setattr(
        IOTX509RefreshableSession, "_get_credentials", fake_get_credentials
    )

    session = RefreshableSession(
        method="iot",
        authentication_method="x509",
        endpoint="abc.credentials.iot.us-east-1.amazonaws.com",
        role_alias="TestRoleAlias",
        certificate=b"dummy-cert",
        private_key=b"dummy-key",
        region_name="us-east-1",
        defer_refresh=True,
    )

    creds = session.refreshable_credentials()
    assert creds["access_key"] == "AKIAEXAMPLE123456"
    assert creds["secret_key"] == "secret"
    assert creds["token"] == "token"
    assert "expiry_time" in creds


def test_custom_refreshable_credentials_stubbed(monkeypatch):
    """Returns custom refreshable credentials from user method."""

    _set_dummy_env(monkeypatch)

    def custom_credentials_method():
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
            "token": "token",
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=True,
    )

    creds = session.refreshable_credentials()
    assert creds["access_key"] == "AKIAEXAMPLE123456"
    assert creds["secret_key"] == "secret"
    assert creds["token"] == "token"
    assert "expiry_time" in creds


def test_client_cache_reuses_client(monkeypatch):
    """Reuses the same cached client for equivalent inputs."""

    _set_dummy_env(monkeypatch)

    def custom_credentials_method():
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
            "token": "token",
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=True,
    )
    client_a = session.client("sts")
    client_b = session.client("sts")
    assert client_a is client_b


def test_client_cache_distinguishes_config_id(monkeypatch):
    """Treats equivalent Config values as the same cache key."""

    _set_dummy_env(monkeypatch)

    def custom_credentials_method():
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
            "token": "token",
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=True,
    )
    config_a = Config(retries={"max_attempts": 2})
    config_b = Config(retries={"max_attempts": 2})
    client_a = session.client("sts", config=config_a)
    client_b = session.client("sts", config=config_b)
    assert client_a is client_b


def test_client_cache_thread_safe(monkeypatch):
    """Ensures concurrent client calls reuse a single cache entry."""

    _set_dummy_env(monkeypatch)

    def custom_credentials_method():
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
            "token": "token",
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=True,
    )
    results: list[object] = []

    def worker():
        results.append(session.client("sts"))

    threads = [Thread(target=worker) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len({id(client) for client in results}) == 1
    assert len(session._client_cache) == 1


def test_custom_refreshes_expired_credentials(monkeypatch):
    """Refreshes when the first custom credentials are expired."""

    _set_dummy_env(monkeypatch)
    call_count = {"count": 0}

    def custom_credentials_method():
        call_count["count"] += 1
        if call_count["count"] == 1:
            expiry = datetime.now(timezone.utc) - timedelta(minutes=5)
            access_key = "OLDKEY0000000000"
        else:
            expiry = datetime.now(timezone.utc) + timedelta(hours=1)
            access_key = "NEWKEY0000000000"
        return {
            "access_key": access_key,
            "secret_key": "secret",
            "token": "token",
            "expiry_time": expiry.isoformat(),
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=False,
    )

    creds = session.refreshable_credentials()
    assert creds["access_key"] == "NEWKEY0000000000"
    assert call_count["count"] >= 2


def test_sts_invalid_token_code_raises(monkeypatch):
    """Raises BRSValidationError when MFA TokenCode is invalid."""

    _set_dummy_env(monkeypatch)
    assume_role_kwargs = {
        "RoleArn": "arn:aws:iam::123456789012:role/TestRole",
        "RoleSessionName": "unit-test",
        "SerialNumber": "arn:aws:iam::123456789012:mfa/test-user",
        "TokenCode": "bad",
    }
    with pytest.raises(BRSValidationError):
        RefreshableSession(
            method="sts",
            assume_role_kwargs=assume_role_kwargs,
            region_name="us-east-1",
            defer_refresh=True,
        )


def test_iot_invalid_endpoint_raises(monkeypatch):
    """Rejects invalid IoT credential endpoint format."""

    _set_dummy_env(monkeypatch)
    with pytest.raises(BRSValidationError):
        RefreshableSession(
            method="iot",
            authentication_method="x509",
            endpoint="bad-endpoint",
            role_alias="TestRoleAlias",
            certificate=b"dummy-cert",
            private_key=b"dummy-key",
            region_name="us-east-1",
            defer_refresh=True,
        )


def test_iot_missing_private_key_raises(monkeypatch):
    """Requires either private_key or pkcs11 for IoT x509."""

    _set_dummy_env(monkeypatch)
    with pytest.raises(BRSConfigurationError):
        RefreshableSession(
            method="iot",
            authentication_method="x509",
            endpoint="abc.credentials.iot.us-east-1.amazonaws.com",
            role_alias="TestRoleAlias",
            certificate=b"dummy-cert",
            private_key=None,
            region_name="us-east-1",
            defer_refresh=True,
        )


def test_iot_invalid_certificate_path_raises(monkeypatch):
    """Rejects invalid certificate file paths."""

    _set_dummy_env(monkeypatch)
    with pytest.raises(BRSValidationError):
        RefreshableSession(
            method="iot",
            authentication_method="x509",
            endpoint="abc.credentials.iot.us-east-1.amazonaws.com",
            role_alias="TestRoleAlias",
            certificate="nope-cert.pem",
            private_key=b"dummy-key",
            region_name="us-east-1",
            defer_refresh=True,
        )


def test_custom_missing_keys_raises(monkeypatch):
    """Raises when custom credentials omit required keys."""

    _set_dummy_env(monkeypatch)

    def custom_credentials_method():
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=True,
    )
    with pytest.raises(BRSCredentialError):
        session.refreshable_credentials()


def test_refresh_lock_prevents_thread_stampede(monkeypatch):
    """Ensures refresh lock serializes concurrent refresh attempts."""

    _set_dummy_env(monkeypatch)
    counter = {"count": 0}
    counter_lock = Lock()
    thread_count = 10
    start = Barrier(thread_count)
    errors: list[Exception] = []

    def custom_credentials_method():
        with counter_lock:
            counter["count"] += 1
        sleep(0.05)
        return {
            "access_key": "AKIAEXAMPLE123456",
            "secret_key": "secret",
            "token": "token",
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

    session = RefreshableSession(
        method="custom",
        custom_credentials_method=custom_credentials_method,
        region_name="us-east-1",
        defer_refresh=True,
    )

    def worker():
        try:
            start.wait()
            session.refreshable_credentials()
        except Exception as exc:
            errors.append(exc)

    threads = [Thread(target=worker) for _ in range(thread_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert counter["count"] == 1
