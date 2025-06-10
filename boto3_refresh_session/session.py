from __future__ import annotations

__doc__ = """
boto3_refresh_session.session
=============================

This module provides the main interface for constructing refreshable boto3 sessions.

The ``RefreshableSession`` class serves as a factory that dynamically selects the appropriate 
credential refresh strategy based on the ``method`` parameter, e.g., ``sts``.

Users can interact with AWS services just like they would with a normal :class:`boto3.session.Session`, 
with the added benefit of automatic credential refreshing.

Examples
--------
>>> from boto3_refresh_session import RefreshableSession
>>> session = RefreshableSession(
...     assume_role_kwargs={"RoleArn": "...", "RoleSessionName": "..."},
...     region_name="us-east-1"
... )
>>> s3 = session.client("s3")
>>> s3.list_buckets()

.. seealso::
    :class:`boto3_refresh_session.sts.STSRefreshableSession`

Factory interface
-----------------
.. autosummary::
   :toctree: generated/
   :nosignatures:

   RefreshableSession
"""

__all__ = ["RefreshableSession"]

from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Literal, get_args
from warnings import warn

from boto3.session import Session
from botocore.credentials import (
    DeferredRefreshableCredentials,
    RefreshableCredentials,
)

#: Type alias for all currently available credential refresh methods.
Method = Literal["sts"]
RefreshMethod = Literal["sts-assume-role"]


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
            warn(f"Method '{method}' is already registered. Overwriting.")

        BaseRefreshableSession.registry[method] = cls

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def _get_credentials(self) -> dict[str, str]: ...

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


class RefreshableSession:
    """Factory class for constructing refreshable boto3 sessions using various authentication
    methods, e.g. STS.

    This class provides a unified interface for creating boto3 sessions whose credentials are
    automatically refreshed in the background.

    Use ``RefreshableSession(method="...")`` to construct an instance using the desired method.

    For additional information on required parameters, refer to the See Also section below.

    Parameters
    ----------
    method : Method
        The authentication and refresh method to use for the session. Must match a registered method name.
        Default is "sts".

    Other Parameters
    ----------------
    **kwargs : dict
        Additional keyword arguments forwarded to the constructor of the selected session class.

    See Also
    --------
    boto3_refresh_session.sts.STSRefreshableSession
    """

    def __new__(
        cls, method: Method = "sts", **kwargs
    ) -> BaseRefreshableSession:
        obj = BaseRefreshableSession.registry[method]
        return obj(**kwargs)

    @classmethod
    def get_available_methods(cls) -> list[str]:
        """Lists all currently available credential refresh methods.

        Returns
        -------
        list[str]
            A list of all currently available credential refresh methods, e.g. 'sts'.
        """

        return list(get_args(Method))
