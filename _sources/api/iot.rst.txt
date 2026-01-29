.. _iot:

.. currentmodule:: boto3_refresh_session.methods.iot

IOT Refresh Methods
===================

.. versionadded:: 5.0.0

.. note::
   
   As of v7.2.0, ``boto3-refresh-session`` requires explicitly installing "iot" as an extra dependency in order to use IoT features, i.e. ``pip install boto3-refresh-session[iot]``.

This module currently only supports X.509 certificate based authentication for retrieving 
temporary security credentials from the AWS IoT credentials provider (backed by STS). 
In the future, this module may support additional authentication methods like Cognito.
MQTT actions are available!

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

You may also interact with MQTT actions using this session!

>>> from awscrt.mqtt.QoS import AT_LEAST_ONCE
>>> conn = session.mqtt(
>>>     endpoint="<your endpoint>-ats.iot.<region>.amazonaws.com",
>>>     client_id="<your thing name or client ID>",
>>> )
>>> conn.connect()
>>> conn.connect().result()
>>> conn.publish(topic="foo/bar", payload=b"hi", qos=AT_LEAST_ONCE)
>>> conn.disconnect().result()

.. seealso::
   :class:`boto3_refresh_session.session.RefreshableSession`

IoT
---

.. autosummary::
   :toctree: generated/
   :nosignatures:

   x509.IOTX509RefreshableSession