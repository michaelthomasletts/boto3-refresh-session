.. _iot:

.. currentmodule:: boto3_refresh_session.methods.iot

boto3_refresh_session.methods.iot
=================================

This module currently only supports X.509 certificate based authentication for retrieving 
temporary security credentials from the AWS IoT credentials provider (backed by STS). 
In the future, this module may support additional authentication methods, like Cognito, 
as well as additional protocols / transports like MQTT.

.. versionadded:: 5.0.0

Examples
--------

``private_key`` is optional if ``pkcs11`` is provided instead.

Additionally, if you prefer to explicitly pass the certificate, private key, and-or CA
then you may pass those as bytes. If a string is provided then it will be assumed to be
the location of those files on disk.

>>> session = RefreshableSession(
>>>     method="iot",
>>>     role_alias=<your IAM role alias>,
>>>     endpoint="https://<your endpoint>.credentials.iot.<region>.amazonaws.com",
>>>     certificate="/path/certificate.pem.crt",
>>>     private_key="/path/private.pem.key",
>>>     ca="<CA file location>.pem",
>>>     ...
>>> )

.. seealso::
   :class:`boto3_refresh_session.session.RefreshableSession`

IoT
---

.. autosummary::
   :toctree: generated/
   :nosignatures:

   IOTX509RefreshableSession