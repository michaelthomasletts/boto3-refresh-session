.. _custom:

.. currentmodule:: boto3_refresh_session.methods.custom

boto3_refresh_session.methods.custom
====================================

Implements a custom credential refresh strategy for use with
:class:`boto3_refresh_session.session.RefreshableSession`.

This module defines the :class:`CustomRefreshableSession` class, which retrieves
temporary credentials using a user provided custom credential object and automatically
refreshes those credentials in the background.

This module is useful for users with highly sophisticated, novel, or idiosyncratic
authentication flows not included in this library. This module is AWS service agnostic.
Meaning: this module is extremely flexible.

.. versionadded:: 1.3.0

Examples
--------
Write (or import) the callable object for obtaining temporary AWS security credentials.

>>> def your_custom_credential_getter(your_param, another_param):
>>>     ...
>>>     return {
>>>         'access_key': ...,
>>>         'secret_key': ...,
>>>         'token': ...,
>>>         'expiry_time': ...,
>>>     }

Pass that callable object to ``RefreshableSession``.

>>> sess = RefreshableSession(
>>>     method='custom',
>>>     custom_credentials_method=your_custom_credential_getter,
>>>     custom_credentials_method_args=...,
>>> )

.. seealso::
   :class:`boto3_refresh_session.session.RefreshableSession`

Custom
------ 

.. autosummary::
   :toctree: generated/
   :nosignatures:

   CustomRefreshableSession