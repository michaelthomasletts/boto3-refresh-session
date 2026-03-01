# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Custom refreshable session using a user-provided credential getter."""

__all__ = ["CustomRefreshableSession"]

from datetime import datetime
from typing import Any, Callable, Dict, cast

from ..exceptions import BRSCredentialError, BRSValidationError, BRSWarning
from ..utils import (
    BRSSession,
    CredentialProvider,
    Identity,
    Registry,
    TemporaryCredentials,
    refreshable_session,
)


@refreshable_session
class CustomRefreshableSession(
    Registry, CredentialProvider, BRSSession, registry_key="custom"
):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary credentials returned by a custom credential getter provided
    by the user. Useful for users with highly sophisticated or idiosyncratic
    authentication flows.

    Parameters
    ----------
    custom_credentials_method : Callable[..., TemporaryCredentials | Dict[str, str]]
        Required. Accepts a callable object that returns temporary AWS
        security credentials. That object must return a dictionary containing
        'access_key', 'secret_key', 'token', and 'expiry_time' when called.
    custom_credentials_method_args : Dict[str, Any], optional
        Optional keyword arguments for the function passed to the
        ``custom_credentials_method`` parameter.
    defer_refresh : bool = True, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.
    advisory_timeout : int = 900, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore will attempt to refresh credentials early according to
        this value (in seconds), but will continue using the existing
        credentials if refresh fails. Default is 15 minutes (900 seconds).
    mandatory_timeout : int = 600, optional
        USE THIS ARGUMENT WITH CAUTION!!!

        Botocore requires a successful refresh before continuing. If
        refresh fails in this window (in seconds), API calls may fail.
        Default is 10 minutes (600 seconds).

    Other Parameters
    ----------------
    **kwargs : Any, optional
        Optional keyword arguments for the :class:`boto3.session.Session`
        object.

    Attributes
    ----------
    cache : SessionCache
        The client and resource cache used to store and retrieve cached
        clients.
    credentials : TemporaryCredentials
        The temporary AWS security credentials.

    Methods
    -------
    client(*args, eviction_policy: EvictionPolicy, max_size: int, **kwargs) -> BaseClient
        Creates a low-level service client by name.
    get_identity() -> Identity
        Returns metadata about the current caller identity.
    refreshable_credentials() -> TemporaryCredentials
        Returns the current temporary AWS security credentials.
    resource(*args, eviction_policy: EvictionPolicy, max_size: int, **kwargs) -> ServiceResource
        Creates a low-level service resource by name.
    whoami() -> Identity
        Alias for :meth:`get_identity`.

    Raises
    ------
    BRSValidationError
        If the provided parameters are of incorrect types or if required
        parameters are missing.
    BRSCredentialError
        If the credentials returned by the custom credential getter are missing
        required key-value pairs or if 'expiry_time' is not a valid ISO 8601
        string or datetime object.

    Notes
    -----
    .. important::

        ``custom_credentials_method`` must be a callable object that returns
        temporary AWS credentials when called. The returned credentials must
        be a dictionary (cast as ``TemporaryCredentials``) containing the
        following key-value pairs: access_key (str), secret_key (str),
        token (str), and expiry_time (str in ISO 8601 format or datetime
        object).

    .. tip::

        You can import ``TemporaryCredentials`` from
        ``boto3_refresh_session.utils.typing.TemporaryCredentials``. To avoid
        typing warnings in your IDE, you may want to cast the dict returned by
        your custom credential getter as ``TemporaryCredentials``.

    Examples
    --------
    Write (or import) the callable object for obtaining temporary AWS security
    credentials.

    >>> def your_custom_credential_getter(your_param, another_param):
    >>>     ...
    >>>     return {
    >>>         'access_key': '...',
    >>>         'secret_key': '...',
    >>>         'token': '...',
    >>>         'expiry_time': '...',
    >>>     }

    Pass that callable object to ``RefreshableSession``.

    >>> sess = RefreshableSession(
    >>>     method='custom',
    >>>     custom_credentials_method=your_custom_credential_getter,
    >>>     custom_credentials_method_args={...},
    >>> )
    """  # noqa: E501

    def __init__(
        self,
        custom_credentials_method: Callable[
            ..., TemporaryCredentials | Dict[str, str]
        ],
        custom_credentials_method_args: Dict[str, Any] | None = None,
        **kwargs,
    ) -> None:
        if "refresh_method" in kwargs:
            BRSWarning.warn(
                "'refresh_method' cannot be set manually. "
                "Reverting to 'custom'."
            )
            del kwargs["refresh_method"]

        # initializing BRSSession
        super().__init__(refresh_method="custom", **kwargs)

        # verifying data types
        if not callable(custom_credentials_method):
            raise BRSValidationError(
                "The 'custom_credentials_method' parameter must be a callable "
                "object that returns temporary AWS credentials when called."
            ) from None
        if (
            not isinstance(custom_credentials_method_args, dict)
            and custom_credentials_method_args is not None
        ):
            raise BRSValidationError(
                "The 'custom_credentials_method_args' parameter must be a dict "
                "of keyword arguments for the custom credentials method."
            ) from None

        # initializing various other attributes
        self._custom_get_credentials = custom_credentials_method
        self._custom_get_credentials_args: Dict[str, Any] = (
            custom_credentials_method_args
            if custom_credentials_method_args is not None
            else {}
        )

    def _get_credentials(self) -> TemporaryCredentials:
        credentials = self._custom_get_credentials(
            **self._custom_get_credentials_args
        )
        required_keys = {"access_key", "secret_key", "token", "expiry_time"}

        if missing := required_keys - credentials.keys():
            raise BRSCredentialError(
                "The dict returned by custom_credentials_method is missing "
                "required key-value pairs.",
                details={"missing": sorted(missing)},
            )

        if isinstance(expiry_time := credentials.get("expiry_time"), datetime):
            credentials["expiry_time"] = expiry_time.isoformat()
        elif not isinstance(expiry_time, str):
            raise BRSCredentialError(
                "'expiry_time' must be an ISO 8601 string.",
                param="expiry_time",
                value=expiry_time,
            ) from None

        return cast(TemporaryCredentials, credentials)

    def get_identity(self) -> Identity:
        """Returns metadata about the custom credential getter.

        Returns
        -------
        Identity
            Dict containing information about the custom credential getter.
        """

        source = getattr(
            self._custom_get_credentials,
            "__name__",
            repr(self._custom_get_credentials),
        )
        return {"method": "custom", "source": repr(source)}
