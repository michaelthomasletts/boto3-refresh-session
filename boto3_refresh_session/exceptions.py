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
        return f"{self.__class__.__name__}({repr(self.message)})"


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
        return f"{self.__class__.__name__}({repr(self.message)})"
