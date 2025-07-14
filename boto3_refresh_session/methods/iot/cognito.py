__all__ = ["IoTCognitoRefreshableSession"]

from ...utils import TemporaryCredentials
from .core import BaseIoTRefreshableSession


class IoTCognitoRefreshableSession(
    BaseIoTRefreshableSession, registry_key="cognito"
):
    def __init__(self): ...

    def _get_credentials(self) -> TemporaryCredentials: ...

    def get_identity(self): ...
