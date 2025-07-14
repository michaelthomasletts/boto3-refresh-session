__all__ = ["IoTCertificateRefreshableSession"]

from ...utils import TemporaryCredentials
from .core import BaseIoTRefreshableSession


class IoTCertificateRefreshableSession(
    BaseIoTRefreshableSession, registry_key="certificate"
):
    def __init__(self): ...

    def _get_credentials(self) -> TemporaryCredentials: ...

    def get_identity(self): ...
