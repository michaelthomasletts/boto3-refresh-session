.. _sts:

.. currentmodule:: boto3_refresh_session.methods.sts

boto3_refresh_session.methods.sts
=================================

Implements the STS-based credential refresh strategy for use with 
:class:`boto3_refresh_session.session.RefreshableSession`.

This module defines the :class:`STSRefreshableSession` class, which uses 
IAM role assumption via STS to automatically refresh temporary credentials 
in the background.

.. versionadded:: 1.1.0

Examples
--------
>>> from boto3_refresh_session import RefreshableSession
>>> session = RefreshableSession(
...     method="sts",
...     assume_role_kwargs={
...         "RoleArn": "arn:aws:iam::123456789012:role/MyRole",
...         "RoleSessionName": "my-session"
...     },
...     region_name="us-east-1"
... )
>>> s3 = session.client("s3")
>>> s3.list_buckets()

.. seealso::
    :class:`boto3_refresh_session.session.RefreshableSession`

STS
---    

.. autosummary::
   :toctree: generated/
   :nosignatures:

   STSRefreshableSession