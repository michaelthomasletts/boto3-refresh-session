from __future__ import annotations

__all__ = ["RefreshableSession"]

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, ClassVar, Literal, TypedDict, get_args

from boto3.session import Session
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)

from .exceptions import BRSError, BRSWarning

#: Type alias for all currently available credential refresh methods.
Method = Literal["sts", "ecs", "custom"]
RefreshMethod = Literal["sts-assume-role", "ecs-container-metadata", "custom"]


class TemporaryCredentials(TypedDict):
    """Temporary IAM credentials."""

    access_key: str
    secret_key: str
    token: str
    expiry_time: datetime | str


class BaseRefreshableSession(ABC, Session):
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

    # adding this and __init_subclass__ to avoid circular imports
    # as well as simplify future addition of new methods
    registry: ClassVar[dict[Method, type[BaseRefreshableSession]]] = {}

    def __init_subclass__(cls, method: Method):
        super().__init_subclass__()

        # guarantees that methods are unique
        if method in BaseRefreshableSession.registry:
            BRSWarning(
                f"Method {repr(method)} is already registered. Overwriting."
            )

        BaseRefreshableSession.registry[method] = cls

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def _get_credentials(self) -> TemporaryCredentials: ...

    @abstractmethod
    def get_identity(self) -> dict[str, Any]: ...

    def _refresh_using(
        self,
        credentials_method: Callable,
        defer_refresh: bool,
        refresh_method: RefreshMethod,
    ):
        # determining how exactly to refresh expired temporary credentials
        if not defer_refresh:
            self._credentials = RefreshableCredentials.create_from_metadata(
                metadata=credentials_method(),
                refresh_using=credentials_method,
                method=refresh_method,
            )
        else:
            self._credentials = DeferredRefreshableCredentials(
                refresh_using=credentials_method, method=refresh_method
            )

    def refreshable_credentials(self) -> dict[str, str]:
        """The current temporary AWS security credentials.

        Returns
        -------
        dict[str, str]
            Temporary AWS security credentials containing:
                AWS_ACCESS_KEY_ID : str
                    AWS access key identifier.
                AWS_SECRET_ACCESS_KEY : str
                    AWS secret access key.
                AWS_SESSION_TOKEN : str
                    AWS session token.
        """

        creds = self.get_credentials().get_frozen_credentials()
        return {
            "AWS_ACCESS_KEY_ID": creds.access_key,
            "AWS_SECRET_ACCESS_KEY": creds.secret_key,
            "AWS_SESSION_TOKEN": creds.token,
        }

    @property
    def credentials(self) -> dict[str, str]:
        """The current temporary AWS security credentials."""

        return self.refreshable_credentials()


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
                f"{repr(method)} is an invalid method parameter. "
                "Available methods are "
                f"{', '.join(repr(meth) for meth in methods)}."
            )

        obj = BaseRefreshableSession.registry[method]
        return obj(**kwargs)

    @classmethod
    def get_available_methods(cls) -> list[str]:
        """Lists all currently available credential refresh methods.

        Returns
        -------
        list[str]
            A list of all currently available credential refresh methods,
            e.g. 'sts'.
        """

        return list(get_args(Method))
