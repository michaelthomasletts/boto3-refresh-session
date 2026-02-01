# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""STS assume-role refreshable session implementation."""

__all__ = ["STSRefreshableSession"]

import collections.abc as abc
import os
import re
import shlex
import subprocess
from typing import Callable

from ..exceptions import BRSConfigurationError, BRSValidationError, BRSWarning
from ..utils import (
    SUBPROCESS_ALLOWED_PARAMETERS,
    AssumeRoleConfig,
    AssumeRoleParams,
    BaseRefreshableSession,
    Identity,
    STSClientConfig,
    STSClientParams,
    TemporaryCredentials,
    refreshable_session,
)


@refreshable_session
class STSRefreshableSession(BaseRefreshableSession, registry_key="sts"):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary AWS credentials using an IAM role that is assumed via STS.

    .. tip::

        For additional details on configuring MFA, refer to the
        :ref:`MFA usage documentation <mfa>`. For additional details on client
        caching, refer to the :ref:`client caching documentation <cachedocs>`.

    Parameters
    ----------
    assume_role_kwargs : AssumeRoleParams | AssumeRoleConfig
        Required keyword arguments for :meth:`STS.Client.assume_role` (i.e.
        boto3 STS client). ``RoleArn`` is required. ``RoleSessionName`` will
        default to 'boto3-refresh-session' if not provided.

        For MFA authentication, two modalities are supported:

        1. **Dynamic tokens (recommended)**: Provide ``SerialNumber`` in
           ``assume_role_kwargs`` and pass ``mfa_token_provider`` callable.
           The provider callable will be invoked on each refresh to obtain
           fresh MFA tokens. Do not include ``TokenCode`` in this case.

        2. **Static/injectable tokens**: Provide both ``SerialNumber`` and
           ``TokenCode`` in ``assume_role_kwargs``. You are responsible for
           updating ``assume_role_kwargs["TokenCode"]`` before the token
           expires.
    sts_client_kwargs : STSClientParams | STSClientConfig, optional
        Optional keyword arguments for the :class:`STS.Client` object. Do not
        provide values for ``service_name`` as they are unnecessary. Default
        is None.
    mfa_token_provider : Callable[[], str] | list[str] | str, optional
        An optional callable *or* CLI command *or* list of command arguments
        that returns a string representing a fresh MFA token code. If provided,
        this will be called or run during each credential refresh to obtain a
        new token, which overrides any ``TokenCode`` in ``assume_role_kwargs``.
        When using this parameter, ``SerialNumber`` must be provided in
        ``assume_role_kwargs``. Callables and lists of command arguments are
        most recommended. Default is None.
    mfa_token_provider_kwargs : dict, optional
        Optional keyword arguments to pass to the ``mfa_token_provider``
        callable *or*, when ``mfa_token_provider`` is a command string or list
        of command arguments, these keyword arguments are forwarded to
        :py:func:`subprocess.run`. Default is None.
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.
    advisory_timeout : int, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore will attempt to refresh credentials early according to
        this value (in seconds), but will continue using the existing
        credentials if refresh fails. Default is 15 minutes (900 seconds).
    mandatory_timeout : int, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore requires a successful refresh before continuing. If
        refresh fails in this window (in seconds), API calls may fail.
        Default is 10 minutes (600 seconds).
    cache_clients : bool, optional
        If ``True`` then clients created by this session will be cached and
        reused for subsequent calls to :meth:`client()` with the same
        parameter signatures. Due to the memory overhead of clients, the
        default is ``True`` in order to protect system resources.
    client_cache_max_size : int, optional
        The maximum number of clients to store in the client cache. Only
        applicable if ``cache_clients`` is ``True``. Defaults to 10.
    allow_shell : bool
        Whether to allow the 'shell' parameter in ``mfa_token_provider_kwargs``
        for MFA subprocess execution. Default is ``False`` for security
        reasons. USE THIS ARGUMENT WITH CAUTION!!!
    allow_executable : bool
        Whether to allow the 'executable' parameter in
        ``mfa_token_provider_kwargs`` for MFA subprocess execution. Default is
        ``False`` for security reasons. USE THIS ARGUMENT WITH CAUTION!!!
    allow_preexec_fn : bool
        Whether to allow the 'preexec_fn' parameter in
        ``mfa_token_provider_kwargs`` for MFA subprocess execution. Default is
        ``False`` for security reasons. USE THIS ARGUMENT WITH CAUTION!!!
    default_mfa_token_provider_timeout : int
        The default timeout (in seconds) to apply to the MFA subprocess
        execution if no timeout is provided in ``mfa_token_provider_kwargs``.
        Default is 30 seconds.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments for the :class:`boto3.session.Session`
        object.

    Attributes
    ----------
    client_cache : ClientCache
        The client cache used to store and retrieve cached clients.

    See Also
    --------
    boto3_refresh_session.utils.config.AssumeRoleConfig
    boto3_refresh_session.utils.config.STSClientConfig

    Examples
    --------

    Basic initialization using ``AssumeRoleConfig``:

    >>> from boto3_refresh_session import (
    ...     AssumeRoleConfig, STSRefreshableSession
    ... )
    >>> session = STSRefreshableSession(
    ...     assume_role_kwargs=AssumeRoleConfig(RoleArn="<your-role-arn>")
    ... )

    MFA with dynamic tokens (recommended). Provide ``SerialNumber`` and a
    token provider (callable or CLI command). The provider is invoked on each
    refresh and its 6-digit token overrides any ``TokenCode``:

    >>> assume_role = AssumeRoleConfig(
    ...     RoleArn="<your-role-arn>",
    ...     SerialNumber="arn:aws:iam::<account-id>:mfa/<user-name>",
    ... )
    ... # using a simple lambda function as the token provider
    >>> session = STSRefreshableSession(
    ...     assume_role_kwargs=assume_role,
    ...     mfa_token_provider=lambda: "123456",
    ... )
    ... # or using a CLI command to get the token from a YubiKey OATH app
    >>> session = STSRefreshableSession(
    ...     assume_role_kwargs=assume_role,
    ...     mfa_token_provider=["ykman", "oath", "code", "<your-issuer>"],
    ...     mfa_token_provider_kwargs={"timeout": 45},  # custom timeout
    ... )
    """

    def __init__(
        self,
        assume_role_kwargs: AssumeRoleParams | AssumeRoleConfig,
        sts_client_kwargs: STSClientParams | STSClientConfig | None = None,
        mfa_token_provider: Callable[[], str] | list[str] | str | None = None,
        mfa_token_provider_kwargs: dict | None = None,
        allow_shell: bool | None = None,
        allow_executable: bool | None = None,
        allow_preexec_fn: bool | None = None,
        default_mfa_token_provider_timeout: int | None = None,
        **kwargs,
    ):
        # default restrictions on subprocess parameters for security
        self.allow_shell = False or allow_shell
        self.allow_executable = False or allow_executable
        self.allow_preexec_fn = False or allow_preexec_fn
        self.default_mfa_token_provider_timeout = (
            30 or default_mfa_token_provider_timeout
        )  # seconds

        # initializing asssume_role_kwargs attribute
        match assume_role_kwargs:
            case AssumeRoleConfig():
                self.assume_role_kwargs = assume_role_kwargs
            case dict():
                self.assume_role_kwargs = AssumeRoleConfig(
                    **assume_role_kwargs
                )
            case _:
                raise BRSValidationError(
                    "'assume_role_kwargs' must be an instance of "
                    "'AssumeRoleConfig' or a dictionary!",
                    param="assume_role_kwargs",
                )

        # initializing sts_client_kwargs attribute
        match sts_client_kwargs:
            case STSClientConfig():
                self.sts_client_kwargs = sts_client_kwargs
            case None:
                self.sts_client_kwargs = STSClientConfig()
            case dict():
                self.sts_client_kwargs = STSClientConfig(**sts_client_kwargs)
            case _:
                raise BRSValidationError(
                    "'sts_client_kwargs' must be an instance of "
                    "'STSClientConfig' or a dictionary!",
                    param="sts_client_kwargs",
                )

        # ensuring 'refresh_method' is not set manually
        if "refresh_method" in kwargs:
            BRSWarning.warn(
                "'refresh_method' cannot be set manually. "
                "Reverting to 'sts-assume-role'."
            )
            del kwargs["refresh_method"]

        # setting 'RoleSessionName' if not provided
        self.assume_role_kwargs.RoleSessionName = self.assume_role_kwargs.get(
            "RoleSessionName", "boto3-refresh-session"
        )

        # store MFA token provider
        try:
            # verifying mfa_token_provider is Callable, str, list[str], or None
            assert (
                isinstance(mfa_token_provider, abc.Callable)
                or isinstance(mfa_token_provider, str)
                or (
                    isinstance(mfa_token_provider, list)
                    and all(
                        isinstance(item, str) for item in mfa_token_provider
                    )
                )
                or mfa_token_provider is None
            )
            self.mfa_token_provider = mfa_token_provider
        except AssertionError as err:
            raise BRSValidationError(
                "'mfa_token_provider' must be a callable, CLI command or list "
                "of command arguments that returns a string representing an "
                "MFA token code!",
                param="mfa_token_provider",
            ) from err

        # storing mfa_token_provider_kwargs
        self.mfa_token_provider_kwargs = mfa_token_provider_kwargs or {}

        # ensure SerialNumber is set appropriately with mfa_token_provider
        if (
            self.mfa_token_provider
            and self.assume_role_kwargs.SerialNumber is None
        ):
            raise BRSConfigurationError(
                "'SerialNumber' must be provided in 'assume_role_kwargs' "
                "when using 'mfa_token_provider'!",
                param="SerialNumber",
            )

        # ensure SerialNumber and TokenCode are set in the absence of
        # mfa_token_provider
        if (
            self.mfa_token_provider is None
            and (
                self.assume_role_kwargs.SerialNumber is not None
                and self.assume_role_kwargs.TokenCode is None
            )
            or (
                self.assume_role_kwargs.SerialNumber is None
                and self.assume_role_kwargs.TokenCode is not None
            )
        ):
            raise BRSConfigurationError(
                "'SerialNumber' and 'TokenCode' must be provided in "
                "'assume_role_kwargs' when 'mfa_token_provider' is not set "
                "and 'SerialNumber' or 'TokenCode' is missing!",
                param="SerialNumber/TokenCode",
            )

        # warn if TokenCode provided with mfa_token_provider
        if (
            self.mfa_token_provider
            and self.assume_role_kwargs.TokenCode is not None
        ):
            BRSWarning.warn(
                "'TokenCode' provided in 'assume_role_kwargs' will be "
                "ignored and overridden by 'mfa_token_provider' on each "
                "refresh."
            )

        # initializing BRSSession
        super().__init__(refresh_method="sts-assume-role", **kwargs)

        # initializing STS client attribute
        self._sts_client = self.client(**self.sts_client_kwargs)

    def _get_credentials(self) -> TemporaryCredentials:
        # override TokenCode with fresh token from provider if configured
        match self.mfa_token_provider:
            # custom token callable provided
            case abc.Callable() if self.mfa_token_provider is not None:
                self.assume_role_kwargs.TokenCode = self.mfa_token_provider(
                    **self.mfa_token_provider_kwargs
                )  # type: ignore[call-arg]
            # CLI command (str) provided
            case str() | list() if self.mfa_token_provider is not None:
                self.assume_role_kwargs.TokenCode = (
                    self._mfa_token_from_command(
                        self.mfa_token_provider,
                        **self.mfa_token_provider_kwargs,
                    )
                )
            # no MFA token provider given (type already validated in __init__)
            case _:
                ...

        temporary_credentials = self._sts_client.assume_role(
            **self.assume_role_kwargs
        )["Credentials"]

        return {
            "access_key": temporary_credentials.get("AccessKeyId"),
            "secret_key": temporary_credentials.get("SecretAccessKey"),
            "token": temporary_credentials.get("SessionToken"),
            "expiry_time": temporary_credentials.get("Expiration").isoformat(),
        }

    def get_identity(self) -> Identity:
        """Returns metadata about the identity assumed.

        Returns
        -------
        Identity
            Dict containing caller identity according to AWS STS.
        """

        return self._sts_client.get_caller_identity()

    def _mfa_token_from_command(
        self, command: list[str] | str, **kwargs
    ) -> str:
        """Private method which runs a CLI command in order to obtain an MFA
        token.

        .. versionadded:: 7.2.12

        .. tip::
            This method does not perform retries. Users who want retries
            should provide their own custom callable as the
            ``mfa_token_provider``.

        .. note::
            Commands that output additional text alongside the MFA token
            (e.g. prompts, logging, etc.) are supported as long as the final
            output contains a valid 6-digit numeric token. The last valid
            6-digit numeric token in the output will be used. Adjacent
            characters to the token will cause an error.

        .. note::
            The use of certain subprocess parameters such as 'shell',
            'executable', and 'preexec_fn' are restricted for security
            reasons. You may permit their use at your own risk by modifying
            the ``allow_shell``, ``allow_executable``, and-or
            ``allow_preexec_fn`` attributes. ``stdout`` and ``stderr``
            are not supported and will raise an error if provided no matter
            what.

        .. note::
            A default timeout of 30 seconds is applied to the command execution
            unless overridden by the ``timeout`` keyword argument or by
            modifying the ``default_mfa_token_provider_timeout`` attribute.

        Parameters
        ----------
        command : str | list[str]
            The command string or list of command arguments to execute to
            obtain the MFA token.

        Other Parameters
        ----------------
        **kwargs : dict, optional
            Keyword arguments to pass to :py:func:`subprocess.run`. ``stdout``
            and ``stderr`` are not supported and will raise an error if
            provided. ``check``, ``capture_output``, and ``text`` are set to
            ``True`` automatically. ``shell``, ``executable``, and
            ``preexec_fn`` are restricted for security reasons unless
            explicitly allowed by modifying the ``allow_shell``,
            ``allow_executable``, and ``allow_preexec_fn`` attributes. A
            default timeout is applied unless overridden by the ``timeout``
            keyword argument or by modifying the
            ``default_mfa_token_provider_timeout`` attribute.

        Returns
        -------
        str
            The MFA token obtained from the command output. Must be a 6-digit
            numeric string without adjacent characters.

        Raises
        ------
        BRSConfigurationError
            If the command is empty, not found, times out, fails, returns
            empty or malformed output, permission denied, or if invalid or
            unallowed keyword arguments are provided.
        """

        # validating command is not empty
        if not command:
            raise BRSConfigurationError(
                "MFA token command is empty.",
                param="mfa_token_provider",
                value=command,
            )

        try:
            # splitting command into list for subprocess
            _command: list[str] = (
                shlex.split(command, posix=os.name != "nt")
                if isinstance(command, str)
                else command
            )
        except ValueError as err:
            raise BRSConfigurationError(
                "MFA token command parsing failed (you may want to check "
                "quoting).",
                param="mfa_token_provider",
                value=command,
            ) from err

        # command should not be empty after splitting
        if not _command:
            raise BRSConfigurationError(
                "MFA token command is empty.",
                param="mfa_token_provider",
                value=command,
            )

        # validating unsupported subprocess.run kwargs
        if "stdout" in kwargs or "stderr" in kwargs:
            raise BRSConfigurationError(
                "'stdout' and 'stderr' are not supported in "
                "'mfa_token_provider_kwargs'.",
                param="mfa_token_provider_kwargs",
            )

        # ensuring all kwargs are valid for subprocess.run
        for kwarg in kwargs:
            if kwarg not in SUBPROCESS_ALLOWED_PARAMETERS:
                raise BRSConfigurationError(
                    f"Invalid keyword argument '{kwarg}' for subprocess.run.",
                    param="mfa_token_provider_kwargs",
                )

        # ensuring required subprocess.run kwargs are set
        kwargs.update({"check": True, "capture_output": True, "text": True})

        # validating restricted subprocess.run kwargs
        if not self.allow_shell and kwargs.get("shell", False):
            raise BRSConfigurationError(
                "'shell' parameter in 'mfa_token_provider_kwargs' is not "
                "allowed for security reasons. To use 'shell', modify the "
                "'allow_shell' attribute at your own risk.",
                param="mfa_token_provider_kwargs",
            )
        if not self.allow_executable and kwargs.get("executable", False):
            raise BRSConfigurationError(
                "'executable' parameter in 'mfa_token_provider_kwargs' is not "
                "allowed for security reasons. To use 'executable', modify "
                "the 'allow_executable' attribute at your own risk.",
                param="mfa_token_provider_kwargs",
            )
        if not self.allow_preexec_fn and kwargs.get("preexec_fn", False):
            raise BRSConfigurationError(
                "'preexec_fn' parameter in 'mfa_token_provider_kwargs' is not "
                "allowed for security reasons. To use 'preexec_fn', modify "
                "the 'allow_preexec_fn' attribute at your own risk.",
                param="mfa_token_provider_kwargs",
            )

        # adding default timeout if not provided
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.default_mfa_token_provider_timeout

        try:
            # running command to obtain MFA token
            completed: subprocess.CompletedProcess = subprocess.run(
                _command, **kwargs
            )
        except FileNotFoundError as err:
            raise BRSConfigurationError(
                "MFA token command not found.",
                param="mfa_token_provider",
                value=command,
            ) from err
        except PermissionError as err:
            raise BRSConfigurationError(
                "Permission denied when executing MFA token command.",
                param="mfa_token_provider",
                value=command,
            ) from err
        except OSError as err:
            raise BRSConfigurationError(
                "Error occurred when executing MFA token command.",
                param="mfa_token_provider",
                value=command,
                details={"errno": err.errno, "strerror": err.strerror},
            ) from err
        except subprocess.TimeoutExpired as err:
            raise BRSConfigurationError(
                "MFA token command timed out.",
                param="mfa_token_provider",
                value=command,
                details={
                    "timeout": err.timeout,
                    "stdout": err.stdout,
                    "stderr": err.stderr,
                },
            ) from err
        except subprocess.CalledProcessError as err:
            raise BRSConfigurationError(
                "MFA token command failed.",
                param="mfa_token_provider",
                value=command,
                details={
                    "returncode": err.returncode,
                    "stdout": err.stdout,
                    "stderr": err.stderr,
                },
            ) from err
        except TypeError as err:
            raise BRSConfigurationError(
                "Invalid mfa_token_provider_kwargs for command execution.",
                param="mfa_token_provider_kwargs",
            ) from err

        # using regex to extract the LAST 6-digit token from output
        # 6-digit numeric tokens with adjacent characters will raise an error
        if not (
            match := re.findall(r"\b\d{6}\b", (completed.stdout or "").strip())
        ):
            raise BRSConfigurationError(
                "MFA token command output did not include a valid 6-digit "
                "token.",
                param="mfa_token_provider",
                value=command,
                details={"stderr": completed.stderr},
            )
        return match[-1]
