# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IoT refreshable session factory for selecting auth methods."""

from __future__ import annotations

__all__ = ["IoTRefreshableSession"]

from typing import get_args

from ...exceptions import BRSValidationError
from ...utils import (
    BaseIoTRefreshableSession,
    BaseRefreshableSession,
    PublicIoTAuthenticationMethod,
)


class IoTRefreshableSession(BaseRefreshableSession, registry_key="iot"):
    def __new__(
        cls,
        authentication_method: PublicIoTAuthenticationMethod = "x509",
        **kwargs,
    ) -> BaseIoTRefreshableSession:
        if authentication_method not in (
            methods := cls.get_available_authentication_methods()
        ):
            raise BRSValidationError(
                f"{authentication_method!r} is an invalid authentication "
                "method parameter. Available authentication methods are "
                f"{', '.join(repr(meth) for meth in methods)}.",
                param="authentication_method",
                value=authentication_method,
            )

        return BaseIoTRefreshableSession.registry[authentication_method](
            **kwargs
        )

    @classmethod
    def get_available_authentication_methods(cls) -> list[str]:
        return list(get_args(PublicIoTAuthenticationMethod))
