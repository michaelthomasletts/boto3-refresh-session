# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Custom exception and warning types for boto3-refresh-session."""

__all__ = [
    "BRSConfigurationError",
    "BRSConnectionError",
    "BRSCredentialError",
    "BRSError",
    "BRSRequestError",
    "BRSValidationError",
    "BRSWarning",
]

import warnings
from typing import Any, Dict


class BRSError(Exception):
    """The base exception for boto3-refresh-session.

    Parameters
    ----------
    message : str, optional
        The message to raise.
    code : str | int, optional
        A short machine-friendly code for the error.
    status_code : int, optional
        An HTTP status code, if applicable.
    details : Dict[str, Any], optional
        Extra structured metadata for debugging or logging.
    param : str, optional
        The parameter name related to the error.
    value : Any, optional
        The parameter value related to the error.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | int | None = None,
        status_code: int | None = None,
        details: Dict[str, Any] | None = None,
        param: str | None = None,
        value: Any | None = None,
    ) -> None:
        self.message = "" if message is None else message
        self.code = code
        self.status_code = status_code
        self.details = details
        self.param = param
        self.value = value
        super().__init__(self.message)

    def __str__(self) -> str:
        base = self.message
        extras: list[str] = []
        if self.code is not None:
            extras.append(f"code={self.code!r}")
        if self.status_code is not None:
            extras.append(f"status_code={self.status_code!r}")
        if self.param is not None:
            extras.append(f"param={self.param!r}")
        if self.value is not None:
            extras.append(f"value={self.value!r}")
        if self.details is not None:
            extras.append(f"details={self.details!r}")
        if extras:
            if base:
                return f"{base} ({', '.join(extras)})"
            return ", ".join(extras)
        return base

    def __repr__(self) -> str:
        args = [repr(self.message)]
        if self.code is not None:
            args.append(f"code={self.code!r}")
        if self.status_code is not None:
            args.append(f"status_code={self.status_code!r}")
        if self.param is not None:
            args.append(f"param={self.param!r}")
        if self.value is not None:
            args.append(f"value={self.value!r}")
        if self.details is not None:
            args.append(f"details={self.details!r}")
        return f"{self.__class__.__name__}({', '.join(args)})"


class BRSValidationError(BRSError):
    """Raised when inputs are missing or invalid."""


class BRSConfigurationError(BRSError):
    """Raised when configuration is incompatible or malformed."""


class BRSCredentialError(BRSError):
    """Raised when credential data is malformed or incomplete."""


class BRSConnectionError(BRSError):
    """Raised when a connection or transport fails."""


class BRSRequestError(BRSError):
    """Raised when a remote request fails."""


class BRSWarning(UserWarning):
    """The base warning for boto3-refresh-session.

    Parameters
    ----------
    message : str, optional
        The message to raise.
    """

    def __init__(self, message: str | None = None) -> None:
        self.message = "" if message is None else message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"

    @classmethod
    def warn(cls, message: str, *, stacklevel: int = 2) -> None:
        """Emits a BRSWarning with a consistent stacklevel."""

        warnings.warn(cls(message), stacklevel=stacklevel)
