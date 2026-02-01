# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IoT refreshable session factory for selecting auth methods."""

from __future__ import annotations

from typing import Any, Literal, overload

from ...utils import (
    BaseIoTRefreshableSession,
    BaseRefreshableSession,
    PublicIoTAuthenticationMethod,
)
from .x509 import IOTX509RefreshableSession

class IoTRefreshableSession(BaseRefreshableSession):  # type: ignore[misc]
    """IoT refreshable session factory for selecting auth methods."""

    @overload
    def __new__(
        cls,
        authentication_method: Literal["x509"] = "x509",
        **kwargs: Any,
    ) -> IOTX509RefreshableSession: ...
    @overload
    def __new__(  # type: ignore[reportOverlappingOverloads]
        cls,
        authentication_method: PublicIoTAuthenticationMethod = "x509",
        **kwargs: Any,
    ) -> BaseIoTRefreshableSession: ...
    def __new__(
        cls,
        authentication_method: PublicIoTAuthenticationMethod = "x509",
        **kwargs: Any,
    ) -> BaseIoTRefreshableSession: ...
    @classmethod
    def get_available_authentication_methods(cls) -> list[str]:
        """Lists all currently available IoT authentication methods.

        Returns
        -------
        list[str]
            A list of all currently available IoT authentication methods,
            e.g. 'x509'.
        """

        ...
