.. _config:

.. currentmodule:: boto3_refresh_session.utils.config.config

Configs
=======

.. versionadded:: 7.1.0

Historically, ``assume_role_kwargs`` and ``sts_client_kwargs`` parameters accepted dictionaries to configure STS clients and role assumption behavior.

Beginning v7.1.0, ``AssumeRoleConfig`` and ``STSClientConfig`` objects were introduced to encapsulate these configurations, providing a more structured and maintainable approach.

.. tip::
    
    Dictionaries are still supported for backward compatibility, but using these new objects is now the recommended approach.

.. tip::
    
    ``AssumeRoleConfig`` and ``STSClientConfig`` attributes can be accessed using dot-notation *or* dictionary-style access.

.. warning::

    ``TokenCode`` values in ``AssumeRoleConfig`` which do not conform with AWS' specifications (i.e. 6 digit numeric strings) will result in errors raised during construction of the ``TokenCode`` attribute.

This still works:

.. code-block:: python

    from boto3_refresh_session import RefreshableSession

    refreshable_session = RefreshableSession(
        assume_role_kwargs={
            "RoleArn": "arn:aws:iam::123456789012:role/MyRole",
            "RoleSessionName": "MySession",
            "DurationSeconds": 3600,
        },
        sts_client_kwargs={
            "region_name": "us-west-2",
            "endpoint_url": "https://sts.us-west-2.amazonaws.com",
        },       
    )

But this is now preferred:

.. code-block:: python

    from boto3_refresh_session import (
        AssumeRoleConfig,
        RefreshableSession,
        STSClientConfig,
    )

    refreshable_session = RefreshableSession(
        AssumeRoleConfig(
            RoleArn="arn:aws:iam::123456789012:role/MyRole",
            RoleSessionName="MySession",
            DurationSeconds=3600,
        ),
        sts_client_kwargs=STSClientConfig(
            region_name="us-west-2",
            endpoint_url="https://sts.us-west-2.amazonaws.com",
        ),       
    )

Configs
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   AssumeRoleConfig
   STSClientConfig