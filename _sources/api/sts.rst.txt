.. _sts:

.. currentmodule:: boto3_refresh_session.methods.sts

STS Refresh Methods
===================

Implements the STS-based credential refresh strategy for use with 
:class:`boto3_refresh_session.session.RefreshableSession`.

This module defines the :class:`STSRefreshableSession` class, which uses 
IAM role assumption via STS to automatically refresh temporary credentials 
in the background.

.. versionadded:: 1.1.0

.. tip::

    For additional details on configuring MFA, refer to the `MFA usage documentation <../usage.html#mfa>`_.
    For additional details on client caching, refer to the `client caching documentation <../usage.html#cache>`_.

Examples
--------
>>> from boto3_refresh_session import AssumeRoleConfig, RefreshableSession
>>> session = RefreshableSession(
...     assume_role_kwargs=AssumeRoleConfig(
...         RoleArn="arn:aws:iam::123456789012:role/MyRole",
...         RoleSessionName="my-session",
...     ),
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