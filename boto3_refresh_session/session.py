from __future__ import annotations

__all__ = ["RefreshableSession"]

from typing import get_args

from .exceptions import BRSError
from .utils import BRSSession, CredentialProvider, Method, Registry


class BaseRefreshableSession(
    Registry[Method],
    CredentialProvider,
    BRSSession,
    registry_key="__sentinel__",
):
    """Abstract base class for implementing refreshable AWS sessions.

    Provides a common interface and factory registration mechanism
    for subclasses that generate temporary credentials using various
    AWS authentication methods (e.g., STS).

    Subclasses must implement ``_get_credentials()`` and ``get_identity()``.
    They should also register themselves using the ``method=...`` argument
    to ``__init_subclass__``.

    Parameters
    ----------
    registry : dict[str, type[BaseRefreshableSession]]
        Class-level registry mapping method names to registered session types.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RefreshableSession:
    """Factory class for constructing refreshable boto3 sessions using various
    authentication methods, e.g. STS.

    This class provides a unified interface for creating boto3 sessions whose
    credentials are automatically refreshed in the background.

    Use ``RefreshableSession(method="...")`` to construct an instance using
    the desired method.

    For additional information on required parameters, refer to the See Also
    section below.

    Parameters
    ----------
    method : Method
        The authentication and refresh method to use for the session. Must
        match a registered method name. Default is "sts".

    Other Parameters
    ----------------
    **kwargs : dict
        Additional keyword arguments forwarded to the constructor of the
        selected session class.

    See Also
    --------
    boto3_refresh_session.custom.CustomRefreshableSession
    boto3_refresh_session.sts.STSRefreshableSession
    boto3_refresh_session.ecs.ECSRefreshableSession
    """

    def __new__(
        cls, method: Method = "sts", **kwargs
    ) -> BaseRefreshableSession:
        if method not in (methods := cls.get_available_methods()):
            raise BRSError(
                f"{method!r} is an invalid method parameter. "
                "Available methods are "
                f"{', '.join(repr(meth) for meth in methods)}."
            )

        return BaseRefreshableSession.registry[method](**kwargs)

    @classmethod
    def get_available_methods(cls) -> list[str]:
        """Lists all currently available credential refresh methods.

        Returns
        -------
        list[str]
            A list of all currently available credential refresh methods,
            e.g. 'sts', 'ecs', 'custom'.
        """

        args = list(get_args(Method))
        args.remove("__sentinel__")
        return args
