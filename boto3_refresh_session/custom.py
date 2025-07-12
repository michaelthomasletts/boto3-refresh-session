from __future__ import annotations

__all__ = ["CustomRefreshableSession"]

from typing import Any, Callable

from .exceptions import BRSError
from .session import BaseRefreshableSession, TemporaryCredentials


class CustomRefreshableSession(BaseRefreshableSession, method="custom"):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary credentials returned by a custom credential getter provided
    by the user. Useful for users with highly sophisticated or idiosyncratic
    authentication flows.

    Parameters
    ----------
    custom_credentials_method: Callable
        Required. Accepts a callable object that returns temporary AWS
        security credentials. That object must return a dictionary containing
        'access_key', 'secret_key', 'token', and 'expiry_time' when called.
    custom_credentials_method_args : dict[str, Any], optional
        Optional keyword arguments for the function passed to the
        ``custom_credentials_method`` parameter.
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically refreshed
        until they are explicitly needed. If ``False`` then temporary
        credentials refresh immediately upon expiration. It is highly
        recommended that you use ``True``. Default is ``True``.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments for the :class:`boto3.session.Session`
        object.

    Examples
    --------
    Write (or import) the callable object for obtaining temporary AWS security
    credentials.

    >>> def your_custom_credential_getter(your_param, another_param):
    >>>     ...
    >>>     return {
    >>>         'access_key': ...,
    >>>         'secret_key': ...,
    >>>         'token': ...,
    >>>         'expiry_time': ...,
    >>>     }

    Pass that callable object to ``RefreshableSession``.

    >>> sess = RefreshableSession(
    >>>     method='custom',
    >>>     custom_credentials_method=your_custom_credential_getter,
    >>>     custom_credentials_method_args=...,
    >>> )
    """

    def __init__(
        self,
        custom_credentials_method: Callable,
        custom_credentials_method_args: dict[str, Any] | None = None,
        defer_refresh: bool | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._custom_get_credentials = custom_credentials_method
        self._custom_get_credentials_args = (
            custom_credentials_method_args
            if custom_credentials_method_args is not None
            else {}
        )

        self._refresh_using(
            credentials_method=self._get_credentials,
            defer_refresh=defer_refresh is not False,
            refresh_method="custom",
        )

    def _get_credentials(self) -> TemporaryCredentials:
        credentials: TemporaryCredentials = self._custom_get_credentials(
            **self._custom_get_credentials_args
        )
        required_keys = {"access_key", "secret_key", "token", "expiry_time"}

        if missing := required_keys - credentials.keys():
            raise BRSError(
                f"The dict returned by custom_credentials_method is missing "
                "these key-value pairs: "
                f"{', '.join(repr(param) for param in missing)}. "
            )

        return credentials

    def get_identity(self) -> dict[str, str]:
        """Returns metadata about the custom credential getter.

        Returns
        -------
        dict[str, str]
            Dict containing information about the custom credential getter.
        """

        source = getattr(
            self._custom_get_credentials,
            "__name__",
            repr(self._custom_get_credentials),
        )
        return {"method": "custom", "source": repr(source)}
