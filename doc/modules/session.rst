.. _session:

.. currentmodule:: boto3_refresh_session.session

RefreshableSession
==================

This module provides the main interface for constructing refreshable boto3 sessions.

The ``RefreshableSession`` class serves as a factory that dynamically selects the appropriate 
credential refresh strategy based on the ``method`` parameter, e.g., ``sts``.

Users can interact with AWS services just like they would with a normal :class:`boto3.session.Session`, 
with the added benefit of automatic credential refreshing.

Examples
--------
>>> from boto3_refresh_session import RefreshableSession
>>> session = RefreshableSession(
...     assume_role_kwargs={"RoleArn": "...", "RoleSessionName": "..."},
...     region_name="us-east-1"
... )
>>> s3 = session.client("s3")
>>> s3.list_buckets()

.. seealso::
    :class:`boto3_refresh_session.methods.custom.CustomRefreshableSession`
    :class:`boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession`
    :class:`boto3_refresh_session.methods.sts.STSRefreshableSession`

Factory interface
-----------------
.. autosummary::
   :toctree: generated/
   :nosignatures:

   RefreshableSession