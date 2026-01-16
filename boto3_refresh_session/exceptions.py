"""Custom exception and warning types for boto3-refresh-session."""

__all__ = ["BRSError", "BRSWarning"]

import warnings


class BRSError(Exception):
    """The base exception for boto3-refresh-session.

    Parameters
    ----------
    message : str, optional
        The message to raise.
    """

    def __init__(self, message: str | None = None):
        self.message = "" if message is None else message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class BRSWarning(UserWarning):
    """The base warning for boto3-refresh-session.

    Parameters
    ----------
    message : str, optional
        The message to raise.
    """

    def __init__(self, message: str | None = None):
        self.message = "" if message is None else message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"

    @classmethod
    def warn(cls, message: str, *, stacklevel: int = 2):
        """Emits a BRSWarning with a consistent stacklevel."""

        warnings.warn(cls(message), stacklevel=stacklevel)
