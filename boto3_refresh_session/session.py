from __future__ import annotations

__all__ = ["RefreshableSession"]

from typing import get_args

from .exceptions import BRSError
from .utils import BaseRefreshableSession, Method


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
    boto3_refresh_session.methods.custom.CustomRefreshableSession
    boto3_refresh_session.methods.iot.IOTX509RefreshableSession
    boto3_refresh_session.methods.sts.STSRefreshableSession
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
            e.g. 'sts', 'custom'.
        """

        args = list(get_args(Method))
        args.remove("__sentinel__")
        return args
