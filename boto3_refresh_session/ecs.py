from __future__ import annotations

__all__ = ["ECSRefreshableSession"]

import os

import requests

from .exceptions import BRSError
from .session import BaseRefreshableSession, TemporaryCredentials

_ECS_CREDENTIALS_RELATIVE_URI = "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"
_ECS_CREDENTIALS_FULL_URI = "AWS_CONTAINER_CREDENTIALS_FULL_URI"
_ECS_AUTHORIZATION_TOKEN = "AWS_CONTAINER_AUTHORIZATION_TOKEN"
_DEFAULT_ENDPOINT_BASE = "http://169.254.170.2"


class ECSRefreshableSession(BaseRefreshableSession, method="ecs"):
    """A boto3 session that automatically refreshes temporary AWS credentials
    from the ECS container credentials metadata endpoint.

    Parameters
    ----------
    defer_refresh : bool, optional
        If ``True`` then temporary credentials are not automatically
        refreshed until they are explicitly needed. If ``False`` then
        temporary credentials refresh immediately upon expiration. It
        is highly recommended that you use ``True``. Default is ``True``.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments passed to :class:`boto3.session.Session`.
    """

    def __init__(self, defer_refresh: bool | None = None, **kwargs):
        super().__init__(**kwargs)

        self._endpoint = self._resolve_endpoint()
        self._headers = self._build_headers()
        self._http = self._init_http_session()

        self._refresh_using(
            credentials_method=self._get_credentials,
            defer_refresh=defer_refresh is not False,
            refresh_method="ecs-container-metadata",
        )

    def _resolve_endpoint(self) -> str:
        uri = os.environ.get(_ECS_CREDENTIALS_FULL_URI) or os.environ.get(
            _ECS_CREDENTIALS_RELATIVE_URI
        )
        if not uri:
            raise BRSError(
                "Neither AWS_CONTAINER_CREDENTIALS_FULL_URI nor "
                "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI is set. "
                "Are you running inside an ECS container?"
            )
        if uri.startswith("http://") or uri.startswith("https://"):
            return uri
        return f"{_DEFAULT_ENDPOINT_BASE}{uri}"

    def _build_headers(self) -> dict[str, str]:
        token = os.environ.get(_ECS_AUTHORIZATION_TOKEN)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def _init_http_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(self._headers)
        return session

    def _get_credentials(self) -> TemporaryCredentials:
        try:
            response = self._http.get(self._endpoint, timeout=3)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise BRSError(
                f"Failed to retrieve ECS credentials from {self._endpoint}"
            ) from exc

        credentials = response.json()
        required = {
            "AccessKeyId",
            "SecretAccessKey",
            "SessionToken",
            "Expiration",
        }
        if not required.issubset(credentials):
            raise BRSError(f"Incomplete credentials received: {credentials}")
        return {
            "access_key": credentials.get("AccessKeyId"),
            "secret_key": credentials.get("SecretAccessKey"),
            "token": credentials.get("SessionToken"),
            "expiry_time": credentials.get("Expiration"),  # already ISO8601
        }

    @staticmethod
    def get_identity() -> dict[str, str]:
        """Returns metadata about ECS.

        Returns
        -------
        dict[str, str]
            Dict containing metadata about ECS.
        """

        return {"method": "ecs", "source": "ecs-container-metadata"}
