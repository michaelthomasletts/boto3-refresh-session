from __future__ import annotations

__all__ = ["IoTRefreshableSession"]

from typing import get_args

from ...exceptions import BRSError
from ...session import BaseRefreshableSession
from ...utils import (
    AuthenticationMethod,
    BRSSession,
    CredentialProvider,
    Registry,
)


class BaseIoTRefreshableSession(
    Registry[AuthenticationMethod],
    CredentialProvider,
    BRSSession,
    registry_key="__iot_sentinel__",
):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class IoTRefreshableSession(BaseRefreshableSession, registry_key="iot"):
    def __new__(
        cls,
        authentication_method: AuthenticationMethod = "certificate",
        **kwargs,
    ) -> BaseIoTRefreshableSession:
        if authentication_method not in (
            methods := cls.get_available_authentication_methods()
        ):
            raise BRSError(
                f"{authentication_method!r} is an invalid authentication "
                "method parameter. Available authentication methods are "
                f"{', '.join(repr(meth) for meth in methods)}."
            )

        return BaseIoTRefreshableSession.registry[authentication_method](
            **kwargs
        )

    @classmethod
    def get_available_authentication_methods(cls) -> list[str]:
        return list(get_args(AuthenticationMethod))
