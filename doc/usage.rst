.. _usage:

Usage
*****

boto3-refresh-session is a drop-in replacement for :class:`boto3.session.Session` which automatically refreshes 
temporary security credentials. It includes support for STS, IoT, and custom credential providers. 
MFA and SSO support are included, and boto3-refresh-session also allows client caching! 

Although boto3 already supports automatic temporary credential refresh via role assumption as configured in ``~/.aws/config``, there are 
scenarios and edge cases where that is insufficient. Below are just a *few* examples:

- Profiles or configs are unavailable or impractical (e.g., containerized or serverless environments)
- You need to explicitly assume roles in a program (not profiles or configs) and hand those credentials around without worrying about expiration
- Custom credential providers are required (e.g. IOT, external ID, etc.)

boto3-refresh-session exists to fill those gaps (and others not listed above) while maintaining full compatibility with boto3.

Installation
------------

Install via pip:

.. code-block:: bash

    pip install boto3-refresh-session

Authorization
-------------

To use boto3-refresh-session, you must have AWS credentials configured locally.
Configuring credentials for boto3-refresh-session is the same as for boto3.  
Refer to the `boto3 documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_ for more details.

Initialization
--------------

Everything in boto3 is ultimately built on the :class:`boto3.session.Session` object — including ``Client`` and ``Resource`` objects.  
boto3-refresh-session extends this interface while adding automatic temporary credential refresh and some additional features.

Creating a session with ``RefreshableSession`` is straightforward. 
Below is a basic example of creating a ``Client`` via STS role assumption.

.. tip::

    You can leave ``RoleSessionName`` in ``assume_role_kwargs`` blank if you like.
    boto3-refresh-session will default to "boto3-refresh-session" for you.

.. code-block:: python

    from boto3_refresh_session import RefreshableSession

    assume_role_kwargs = {
        "RoleArn": "<your-role-arn>",
        "RoleSessionName": "<your-role-session-name>",
    }

    session = RefreshableSession(
        assume_role_kwargs=assume_role_kwargs
    )

    s3 = session.client('s3')

``RefreshableSession`` can be initialized exactly like a normal :class:`boto3.session.Session` object. 
It accepts every parameter which :class:`boto3.session.Session` does, in addition to parameters for STS role assumption, refresh behavior, timeout limits, MFA, and client caching.
To illustrate, below is an example of creating a ``Client`` via STS role assumption with custom retry configuration and region specification.

.. tip::

    ``RefreshableSession`` also accepts a ``sts_client_kwargs`` parameter, which allows you to pass custom parameters to the internal STS client used for role assumption.
    Check the :class:`STS.Client` documentation for available parameters.

.. code-block:: python

    from botocore.config import Config
    from boto3_refresh_session import RefreshableSession

    assume_role_kwargs = {
        "RoleArn": "<your-role-arn>",
        "RoleSessionName": "<your-role-session-name>",
    }

    session = RefreshableSession(
        assume_role_kwargs=assume_role_kwargs,
        region_name="us-east-1",
    )

    s3 = session.client('s3', config=Config(retries={"max_attempts": 10}))

Credential Provider Methods
---------------------------

``RefreshableSession`` uses STS by default.
To be more precise, if ``method`` is not specified, it defaults to ``"sts"``.
If you want to use ``RefreshableSession`` with IoT or provide a custom credential provider instead then you must modulate the ``method`` parameter accordingly to ``"iot"`` or ``"custom"``. 
Those methods require additional parameters; refer to the `modules reference <https://michaelthomasletts.com/boto3-refresh-session/modules/index.html>`_ for more details.

Refresh Behavior
----------------

There are two ways to trigger automatic credential refresh in boto3-refresh-session:

1. **Deferred (default)** — Refresh occurs only when credentials are required  
2. **Eager** — Credentials are refreshed as soon as they expire

Set ``defer_refresh`` to False to enable eager refresh:

.. code-block:: python

    session = RefreshableSession(
        defer_refresh=False,
        assume_role_kwargs=assume_role_kwargs
    )

Eager Refresh Behavior
----------------------

With eager refresh enabled (i.e. ``defer_refresh=False``), credentials are refreshed according to two settings: advisory and mandatory timeouts.
The so-called "advisory" and "mandatory" timeouts are concepts created by botocore to manage credential expiration.
By default in botocore, the advisory timeout is set to 15 minutes before expiration and the mandatory timeout is set to 10 minutes before expiration.
botocore will attempt to refresh credentials when the advisory timeout is reached, but will force a refresh when the mandatory timeout is reached.
This behavior is inherited by boto3-refresh-session when eager refresh is enabled, and the ``advisory_timeout`` and ``mandatory_timeout`` parameters can be adjusted as needed.

.. tip::

    The vast majority of use cases will not require modification of advisory or mandatory timeouts, but they are available for edge cases where precise control over refresh timing is necessary.

MFA
---

If your role assumption requires MFA, you must provide an MFA token provider callable via the ``mfa_token_provider`` parameter.
This callable should return a valid MFA token string when called.
If that callable requires arguments, you can provide them via the ``mfa_token_provider_kwargs`` parameter.
Below is an example of using an MFA token provider which calls Yubikey.

.. tip::

    Be sure to provide ``SerialNumber`` in ``assume_role_kwargs`` when using MFA!
    Because ``mfa_token_provider`` is a callable, you should not provide ``TokenCode`` in ``assume_role_kwargs``; it will be supplied automatically by the callable you provided.
    If you run into latency issues then you may want to pass a ``Config`` with retries to the internal STS client via the ``sts_client_kwargs`` parameter.

.. code-block:: python

    from boto3_refresh_session import RefreshableSession
    import subprocess
    from typing import Sequence

    
    def mfa_token_provider(cmd: Sequence[str], timeout: float):
        p = subprocess.run(
            list(cmd),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (p.stdout or "").strip()
    
    
    assume_role_kwargs = {
        "RoleArn": "<your-role-arn>",
        "RoleSessionName": "<your-role-session-name>",
        "SerialNumber": "arn:aws:iam::<your-aws-account-id>:mfa/<your-mfa-device-name>",
    }
    mfa_token_provider_kwargs = {
        "cmd": ["ykman", "oath", "code", "--single", "AWS-prod"],  # example token source
        "timeout": 3.0,
    }

    session = RefreshableSession(
        assume_role_kwargs=assume_role_kwargs,
        mfa_token_provider=mfa_token_provider,
        mfa_token_provider_kwargs=mfa_token_provider_kwargs,
    )

Client Caching
--------------

boto3-refresh-session supports ``Client`` caching via the ``cache_clients`` parameter.
The purpose of this feature is to minimize the massive memory footprint of multiple ``Client`` objects created with identical parameters.
When ``cache_clients`` is set to True, ``Client`` objects created via the session's ``client`` method are cached and reused for subsequent calls with the same parameters.
This can improve performance by reducing the overhead of creating new ``Client`` objects.
boto3-refresh-session caches clients by default; to disable client caching, set ``cache_clients=False`` when initializing ``RefreshableSession``.

IoT Core X.509
--------------

AWS IoT Core can vend temporary AWS credentials through the credentials provider when you connect with an X.509 certificate and a role alias. 
boto3-refresh-session makes this flow seamless by automatically refreshing credentials over mTLS.
boto3-refresh-session supports both PEM files and PKCS#11 modules for private key storage.
For additional information on the exact parameters that ``RefreshableSession`` takes for IoT, check `this documentation <https://michaelthomasletts.com/boto3-refresh-session/modules/generated/boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession.html#boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession>`_.

For PEM files:

.. code-block:: python

    from boto3_refresh_session import RefreshableSession
    session = RefreshableSession(
        method="iot",
        endpoint="<your-credentials-endpoint>.credentials.iot.<region>.amazonaws.com",
        role_alias="<your-role-alias>",
        certificate="/path/to/certificate.pem",
        private_key="/path/to/private-key.pem",
        thing_name="<your-thing-name>",       # optional, if used in policies
        duration_seconds=3600,                # optional, capped by role alias
        region_name="us-east-1",
    )

For PKCS#11:

.. code-block:: python

    from boto3_refresh_session import RefreshableSession

    session = brs.RefreshableSession(
        method="iot",
        endpoint="<your-credentials-endpoint>.credentials.iot.<region>.amazonaws.com",
        role_alias="<your-role-alias>",
        certificate="/path/to/certificate.pem",
        pkcs11={
            "pkcs11_lib": "/usr/local/lib/softhsm/libsofthsm2.so",
            "user_pin": "1234",
            "slot_id": 0,
            "token_label": "MyToken",
            "private_key_label": "MyKey",
        },
        thing_name="<your-thing-name>",
        region_name="us-east-1",
    )

For MQTT operations:

.. code-block:: python

    from awscrt.mqtt.QoS import AT_LEAST_ONCE
    from boto3_refresh_session import RefreshableSession

    conn = session.mqtt(
    endpoint="<your endpoint>-ats.iot.<region>.amazonaws.com",
    client_id="<your thing name or client ID>",
    )
    conn.connect()
    conn.connect().result()
    conn.publish(topic="foo/bar", payload=b"hi", qos=AT_LEAST_ONCE)
    conn.disconnect().result()

Miscellaneous
-------------

To see which identity the session is currently using, call the ``get_caller_identity`` method:

.. code-block:: python

    print(session.get_caller_identity())

.. tip::

    The value returned by ``get_caller_identity`` when ``method="custom"`` is not especially informative. 
    This is because custom credential providers vary widely, which this library cannot infer or anticipate in advance.
    Users employing ``method="custom"`` should implement their own identity verification logic as needed.

To return the currently active temporary security credentials, call the ``refreshable_credentials`` method or ``credentials`` property:

.. code-block:: python

    # refreshable_credentials method
    print(session.refreshable_credentials())

    # credentials property
    print(session.credentials)

If you wish to make ``RefreshableSession`` globally available in your application without needing to pass it around explicitly, cleverly update the default session in boto3 like so:

.. code-block:: python

    from boto3 import DEFAULT_SESSION, client
    from boto3_refresh_session import RefreshableSession

    DEFAULT_SESSION = RefreshableSession(
        assume_role_kwargs={
            "RoleArn": "<your-role-arn>",
            "RoleSessionName": "<your-role-session-name>",
        },
        ...
    )
    s3 = client("s3")  # uses DEFAULT_SESSION under the hood