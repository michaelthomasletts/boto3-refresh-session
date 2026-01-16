__all__ = ["CustomRefreshableSession"]

from ..exceptions import BRSError, BRSWarning
from ..utils import (
    BaseRefreshableSession,
    CustomCredentialsMethod,
    CustomCredentialsMethodArgs,
    Identity,
    TemporaryCredentials,
    refreshable_session,
)


@refreshable_session
class CustomRefreshableSession(BaseRefreshableSession, registry_key="custom"):
    """A :class:`boto3.session.Session` object that automatically refreshes
    temporary credentials returned by a custom credential getter provided
    by the user. Useful for users with highly sophisticated or idiosyncratic
    authentication flows.

    Parameters
    ----------
    custom_credentials_method: CustomCredentialsMethod
        Required. Accepts a callable object that returns temporary AWS
        security credentials. That object must return a dictionary containing
        'access_key', 'secret_key', 'token', and 'expiry_time' when called.
    custom_credentials_method_args : CustomCredentialsMethodArgs, optional
        Optional keyword arguments for the function passed to the
        ``custom_credentials_method`` parameter.
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
        custom_credentials_method: CustomCredentialsMethod,
        custom_credentials_method_args: (
            CustomCredentialsMethodArgs | None
        ) = None,
        **kwargs,
    ):
        if "refresh_method" in kwargs:
            BRSWarning.warn(
                "'refresh_method' cannot be set manually. "
                "Reverting to 'custom'."
            )
            del kwargs["refresh_method"]

        # initializing BRSSession
        super().__init__(refresh_method="custom", **kwargs)

        # initializing various other attributes
        self._custom_get_credentials: CustomCredentialsMethod = (
            custom_credentials_method
        )
        self._custom_get_credentials_args: CustomCredentialsMethodArgs = (
            custom_credentials_method_args
            if custom_credentials_method_args is not None
            else {}
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
