import subprocess
from typing import cast

import pytest

import boto3_refresh_session.methods.sts as sts_module
from boto3_refresh_session.exceptions import (
    BRSConfigurationError,
    BRSValidationError,
)
from boto3_refresh_session.methods.sts import STSRefreshableSession
from boto3_refresh_session.utils import AssumeRoleConfig


def _session():
    session = cast(
        STSRefreshableSession, object.__new__(STSRefreshableSession)
    )
    return session


def _mock_run_with_stdout(monkeypatch, stdout, stderr=""):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], 0, stdout=stdout, stderr=stderr
        )

    monkeypatch.setattr(sts_module.subprocess, "run", fake_run)  # type: ignore


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        "abc",
        "12345",
        "1234567",
        "otp123456",
        "!!!",
    ],
)
def test_mfa_token_from_command_rejects_invalid_stdout(monkeypatch, stdout):
    """Rejects outputs that do not contain a valid 6-digit token."""
    session = _session()
    _mock_run_with_stdout(monkeypatch, stdout)

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo 123456")  # type: ignore


@pytest.mark.parametrize(
    "stdout, expected",
    [
        ("123456", "123456"),
        ("token: 123456\n", "123456"),
        ("first 111111 last 222222", "222222"),
        ("id=000123", "000123"),
    ],
)
def test_mfa_token_from_command_extracts_last_code(
    monkeypatch, stdout, expected
):
    """Extracts the last valid 6-digit token from stdout."""
    session = _session()
    _mock_run_with_stdout(monkeypatch, stdout)

    token = session._mfa_token_from_command(["echo", "123456"])  # type: ignore
    assert token == expected


def test_mfa_token_from_command_permission_denied(monkeypatch):
    """Surfaces permission errors as configuration errors."""
    session = _session()

    def fake_run(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(sts_module.subprocess, "run", fake_run)  # type: ignore

    with pytest.raises(BRSConfigurationError) as exc:
        session._mfa_token_from_command("echo 123456")  # type: ignore
    assert "Permission denied" in str(exc.value)


def test_mfa_token_from_command_os_error(monkeypatch):
    """Surfaces OS execution errors as configuration errors."""
    session = _session()

    def fake_run(*args, **kwargs):
        raise OSError(5, "boom")

    monkeypatch.setattr(sts_module.subprocess, "run", fake_run)  # type: ignore

    with pytest.raises(BRSConfigurationError) as exc:
        session._mfa_token_from_command("echo 123456")  # type: ignore
    assert "Error occurred" in str(exc.value)


def test_mfa_token_from_command_timeout(monkeypatch):
    """Raises configuration errors on command timeout."""
    session = _session()

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=args[0], timeout=1, output="out", stderr="err"
        )

    monkeypatch.setattr(sts_module.subprocess, "run", fake_run)  # type: ignore

    with pytest.raises(BRSConfigurationError) as exc:
        session._mfa_token_from_command("echo 123456")  # type: ignore
    assert "timed out" in str(exc.value)


def test_mfa_token_from_command_called_process_error(monkeypatch):
    """Raises configuration errors on non-zero exit codes."""
    session = _session()

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            2, args[0], output="out", stderr="err"
        )

    monkeypatch.setattr(sts_module.subprocess, "run", fake_run)  # type: ignore

    with pytest.raises(BRSConfigurationError) as exc:
        session._mfa_token_from_command("echo 123456")  # type: ignore
    assert "failed" in str(exc.value)


def test_mfa_token_from_command_unbalanced_quotes(monkeypatch):
    """Raises configuration errors on malformed command strings."""
    session = _session()
    _mock_run_with_stdout(monkeypatch, "123456")

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo '123456")  # type: ignore


def test_mfa_token_from_command_rejects_stdout_kwarg():
    """Rejects stdout/stderr overrides for command execution."""
    session = _session()

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo 123456", stdout=subprocess.PIPE)  # type: ignore


def test_mfa_token_from_command_rejects_invalid_kwarg():
    """Rejects invalid subprocess.run keyword arguments."""
    session = _session()

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo 123456", not_a_kwarg=True)  # type: ignore


def test_mfa_token_from_command_rejects_shell_by_default():
    """Rejects shell execution for security."""
    session = _session()

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo 123456", shell=True)  # type: ignore


def test_mfa_token_from_command_rejects_executable_kwarg():
    """Rejects executable overrides for security."""
    session = _session()

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo 123456", executable="/bin/sh")  # type: ignore


def test_mfa_token_from_command_rejects_preexec_fn_kwarg():
    """Rejects preexec_fn hooks for security."""
    session = _session()

    with pytest.raises(BRSConfigurationError):
        session._mfa_token_from_command("echo 123456", preexec_fn=lambda: None)  # type: ignore


def test_token_code_validation_accepts_six_digits():
    """Accepts a strict 6-digit TokenCode value."""
    config = AssumeRoleConfig(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="unit-test",
        TokenCode="123456",
    )
    assert config.TokenCode == "123456"


@pytest.mark.parametrize("value", ["12345", "1234567", "abc123", "12345x"])
def test_token_code_validation_rejects_invalid_values(value):
    """Rejects invalid TokenCode values."""
    with pytest.raises(BRSValidationError):
        AssumeRoleConfig(
            RoleArn="arn:aws:iam::123456789012:role/TestRole",
            RoleSessionName="unit-test",
            TokenCode=value,
        )
