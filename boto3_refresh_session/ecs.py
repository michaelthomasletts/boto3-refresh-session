from __future__ import annotations

__doc__ = """
boto3_refresh_session.ecs
=========================

Implements the ECS-based credential refresh strategy for use with
:class:`boto3_refresh_session.session.RefreshableSession`.

This module defines the :class:`ECSRefreshableSession` class, which retrieves
temporary credentials from the ECS container metadata endpoint and automatically
refreshes them in the background.

ECS tasks that are assigned a task role automatically expose temporary
credentials through a local metadata HTTP endpoint. This session class
wraps that mechanism in a refreshable boto3 session, allowing credential
rotation to occur seamlessly over long-lived operations.

.. versionadded:: 1.2.0

Examples
--------
>>> from boto3_refresh_session import RefreshableSession
>>> session = RefreshableSession(method="ecs")
>>> s3 = session.client("s3")
>>> s3.list_buckets()

.. seealso::
   :class:`boto3_refresh_session.session.RefreshableSession`

ECS
---    

.. autosummary::
   :toctree: generated/
   :nosignatures:

   ECSRefreshableSession

Environment Variables
---------------------
The following environment variables are used to locate and authorize
access to the ECS metadata endpoint:

- ``AWS_CONTAINER_CREDENTIALS_RELATIVE_URI`` – Relative path to metadata endpoint (standard)
- ``AWS_CONTAINER_CREDENTIALS_FULL_URI`` – Full URI to endpoint (used in advanced setups)
- ``AWS_CONTAINER_AUTHORIZATION_TOKEN`` – Optional bearer token for accessing metadata endpoint
"""

__all__ = ["ECSRefreshableSession"]

import os
import requests

from .session import BaseRefreshableSession


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
        If ``True``, credentials will not be refreshed until first use.
        Default is ``True``.

    Other Parameters
    ----------------
    kwargs : dict
        Optional keyword arguments passed to :class:`boto3.session.Session`.
    """

    def __init__(
        self, defer_refresh: bool = True, **kwargs
    ):
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
            raise EnvironmentError(
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

    def _get_credentials(self) -> dict[str, str]:
        try:
            response = self._http.get(self._endpoint, timeout=3)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ConnectionError(
                f"Failed to retrieve ECS credentials from {self._endpoint}"
            ) from exc

        credentials = response.json()
        required = {"AccessKeyId", "SecretAccessKey", "Token", "Expiration"}
        if not required.issubset(credentials):
            raise ValueError(f"Incomplete credentials received: {credentials}")

        return {
            "access_key": credentials["AccessKeyId"],
            "secret_key": credentials["SecretAccessKey"],
            "token": credentials["Token"],
            "expiry_time": credentials["Expiration"],  # already ISO8601
        }

    def get_identity(self) -> dict[str, str]:
        """Returns metadata about ECS.

        Returns
        -------
        dict[str, str]
            Dict containing metadata about ECS.
        """

        return {"method": "ecs", "source": "ecs-container-metadata"}
