__all__ = ["STSRefreshableSession"]

from typing import Callable

from ..exceptions import BRSError, BRSWarning
from ..utils import (
    AssumeRoleParams,
    BaseRefreshableSession,
    Identity,
    STSClientParams,
    TemporaryCredentials,
    refreshable_session,
)


@refreshable_session
class STSRefreshableSession(BaseRefreshableSession, registry_key="sts"):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary AWS credentials using an IAM role that is assumed via STS.

    Parameters
    ----------
    assume_role_kwargs : AssumeRoleParams
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
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.
    sts_client_kwargs : STSClientParams, optional
        Optional keyword arguments for the :class:`STS.Client` object. Do not
        provide values for ``service_name`` as they are unnecessary. Default
        is None.
    mfa_token_provider : Callable[[], str], optional
        An optional callable that returns a string representing a fresh MFA
        token code. If provided, this will be called during each credential
        refresh to obtain a new token, which overrides any ``TokenCode`` in
        ``assume_role_kwargs``. When using this parameter, ``SerialNumber``
        must be provided in ``assume_role_kwargs``. Default is None.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments for the :class:`boto3.session.Session`
        object.
    """

    def __init__(
        self,
        assume_role_kwargs: AssumeRoleParams,
        sts_client_kwargs: STSClientParams | None = None,
        mfa_token_provider: Callable[[], str] | None = None,
        **kwargs,
    ):
        # ensuring 'refresh_method' is not set manually
        if "refresh_method" in kwargs:
            BRSWarning.warn(
                "'refresh_method' cannot be set manually. "
                "Reverting to 'sts-assume-role'."
            )
            del kwargs["refresh_method"]

        # verifying 'RoleArn' is provided in 'assume_role_kwargs'
        if "RoleArn" not in assume_role_kwargs:
            raise BRSError(
                "'RoleArn' must be provided in 'assume_role_kwargs'!"
            )

        # setting default 'RoleSessionName' if not provided
        if "RoleSessionName" not in assume_role_kwargs:
            BRSWarning.warn(
                "'RoleSessionName' not provided in "
                "'assume_role_kwargs'! Defaulting to "
                "'boto3-refresh-session'."
            )
            assume_role_kwargs["RoleSessionName"] = "boto3-refresh-session"

        # store MFA token provider
        self.mfa_token_provider = mfa_token_provider

        # ensure SerialNumber is set appropriately with mfa_token_provider
        if (
            self.mfa_token_provider
            and "SerialNumber" not in assume_role_kwargs
        ):
            raise BRSError(
                "'SerialNumber' must be provided in 'assume_role_kwargs' "
                "when using 'mfa_token_provider'!"
            )

        # ensure SerialNumber and TokenCode are set without mfa_token_provider
        if (
            self.mfa_token_provider is None
            and (
                "SerialNumber" in assume_role_kwargs
                and "TokenCode" not in assume_role_kwargs
            )
            or (
                "SerialNumber" not in assume_role_kwargs
                and "TokenCode" in assume_role_kwargs
            )
        ):
            raise BRSError(
                "'SerialNumber' and 'TokenCode' must be provided in "
                "'assume_role_kwargs' when 'mfa_token_provider' is not set!"
            )

        # warn if TokenCode provided with mfa_token_provider
        if self.mfa_token_provider and "TokenCode" in assume_role_kwargs:
            BRSWarning.warn(
                "'TokenCode' provided in 'assume_role_kwargs' will be "
                "ignored and overridden by 'mfa_token_provider' on each "
                "refresh."
            )

        # initializing assume role kwargs attribute
        self.assume_role_kwargs = assume_role_kwargs

        # initializing BRSSession
        super().__init__(refresh_method="sts-assume-role", **kwargs)

        if sts_client_kwargs is not None:
            # overwriting 'service_name' if if appears in sts_client_kwargs
            if "service_name" in sts_client_kwargs:
                BRSWarning.warn(
                    "'sts_client_kwargs' cannot contain values for "
                    "'service_name'. Reverting to service_name = 'sts'."
                )
                del sts_client_kwargs["service_name"]
            self._sts_client = self.client(
                service_name="sts", **sts_client_kwargs
            )
        else:
            self._sts_client = self.client(service_name="sts")

    def _get_credentials(self) -> TemporaryCredentials:
        params = dict(self.assume_role_kwargs)

        # override TokenCode with fresh token from provider if configured
        if self.mfa_token_provider:
            params["TokenCode"] = self.mfa_token_provider()

        # validating TokenCode format
        if "TokenCode" in params:
            token_code = params["TokenCode"]

            if (
                not isinstance(token_code, str)
                or len(token_code) != 6
                or not token_code.isdigit()
            ):
                raise BRSError(
                    "'TokenCode' must be a 6-digit string per AWS MFA "
                    "token specifications!"
                )

        temporary_credentials = self._sts_client.assume_role(**params)[
            "Credentials"
        ]

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
