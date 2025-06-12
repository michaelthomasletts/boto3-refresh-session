.. _ecs:

.. currentmodule:: boto3_refresh_session.ecs

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