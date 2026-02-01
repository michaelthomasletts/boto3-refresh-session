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

boto3-refresh-session is available on PyPI.

.. code-block:: bash

    # with pip
    pip install boto3-refresh-session

    # with pip + iot as an extra
    pip install boto3-refresh-session[iot]

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

.. tip::
    
    You can also provide ``assume_role_kwargs`` as a simple dictionary instead of an ``AssumeRoleConfig`` object if you prefer.
    Both approaches are functionally equivalent!

.. code-block:: python

    from boto3_refresh_session import AssumeRoleConfig, RefreshableSession

    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(
            RoleArn="<your-role-arn>",
            RoleSessionName="<your-role-session-name>",
        )
    )

    s3 = session.client('s3')

``RefreshableSession`` can be initialized exactly like a normal :class:`boto3.session.Session` object. 
It accepts every parameter which :class:`boto3.session.Session` does, in addition to parameters for STS role assumption, refresh behavior, timeout limits, MFA, and client caching.
To illustrate, below is an example of creating a ``Client`` via STS role assumption with custom retry configuration and region specification.

.. tip::

    ``RefreshableSession`` also accepts a ``sts_client_kwargs`` parameter, which allows you to pass custom parameters to the internal STS client used for role assumption.
    Like ``assume_role_kwargs``, ``sts_client_kwargs`` can be provided as either a dictionary or a ``STSClientConfig`` object.
    Check the :class:`STS.Client` documentation for available parameters.

.. code-block:: python

    from botocore.config import Config
    from boto3_refresh_session import AssumeRoleConfig, RefreshableSession

    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(RoleArn="<your-role-arn>"),
        region_name="us-east-1",
    )

    s3 = session.client('s3', config=Config(retries={"max_attempts": 10}))

.. tip::

    Attributes in ``assume_role_kwargs`` and ``sts_client_kwargs`` can be accessed using dot-notation *or* dictionary-style access.
    Same goes for ``AssumeRoleConfig`` and ``STSClientConfig`` objects.

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

    from boto3_refresh_session import AssumeRoleConfig, RefreshableSession

    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(RoleArn="<your-role-arn>"),
        defer_refresh=False,
    )

Eager Refresh Behavior
~~~~~~~~~~~~~~~~~~~~~~

With eager refresh enabled (i.e. ``defer_refresh=False``), credentials are refreshed according to two settings: advisory and mandatory timeouts.
The so-called "advisory" and "mandatory" timeouts are concepts created by botocore to manage credential expiration.
By default in botocore, the advisory timeout is set to 15 minutes before expiration and the mandatory timeout is set to 10 minutes before expiration.
botocore will attempt to refresh credentials when the advisory timeout is reached, but will force a refresh when the mandatory timeout is reached.
This behavior is inherited by boto3-refresh-session when eager refresh is enabled, and the ``advisory_timeout`` and ``mandatory_timeout`` parameters can be adjusted as needed.

.. tip::

    The vast majority of use cases will not require modification of advisory or mandatory timeouts, but they are available for edge cases where precise control over refresh timing is necessary.

.. _mfa:

MFA
---

If your role assumption requires MFA, you must provide a token provider via ``mfa_token_provider``. 
It accepts a ``callable`` (recommended), a ``list[str]`` of command arguments (also recommended), or a command ``str`` (least recommended).

- **Callable**: Called during each refresh. 
  Arguments are passed via ``mfa_token_provider_kwargs``. 
  You are responsible for writing the callable.
- **list[str] | str**: Treated as a CLI command and executed via :py:func:`subprocess.run`. 
  Keyword arguments passed via ``mfa_token_provider_kwargs`` are forwarded to :py:func:`subprocess.run`.

Below are examples for a callable and direct CLI invocation.

.. tip::

    Be sure to provide ``SerialNumber`` in ``assume_role_kwargs`` when using MFA. 
    If you provide ``mfa_token_provider``, any ``TokenCode`` you set in ``assume_role_kwargs`` will be ignored and overwritten on each refresh.
    If you run into latency issues, pass a ``Config`` with retries to the internal STS client via ``sts_client_kwargs``.

.. note::

    Token output is parsed to the **last** 6-digit numeric token found in stdout when ``mfa_token_provider`` is a CLI command. 
    The token must be a standalone 6-digit string (adjacent characters cause an error).

.. code-block:: python

    from boto3_refresh_session import AssumeRoleConfig, RefreshableSession
    import subprocess
    from typing import Sequence

    # example MFA token provider as a callable
    def mfa_token_provider(cmd: Sequence[str], timeout: float) -> str:
        p = subprocess.run(
            list(cmd),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (p.stdout or "").strip()


    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(
            RoleArn="<your-role-arn>",
            RoleSessionName="<your-role-session-name>",
            SerialNumber="arn:aws:iam::<account-id>:mfa/<device-name>",
        ),
        mfa_token_provider=mfa_token_provider,
        mfa_token_provider_kwargs={
            # "ykman oath code --single AWS-prod" is equivalent to the cmd below
            "cmd": ["ykman", "oath", "code", "--single", "AWS-prod"],
            "timeout": 3.0,
        },
    )

    # or, pass a CLI command directly (list[str] or str)
    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(
            RoleArn="<your-role-arn>",
            RoleSessionName="<your-role-session-name>",
            SerialNumber="arn:aws:iam::<account-id>:mfa/<device-name>",
        ),
        mfa_token_provider=["ykman", "oath", "code", "--single", "AWS-prod"],
        mfa_token_provider_kwargs={"timeout": 20},
    )

.. warning::

    It is highly recommended to use ``mfa_token_provider`` instead of passing ``TokenCode`` directly. 
    Without ``mfa_token_provider``, you must refresh ``TokenCode`` yourself, which will be cumbersome.

.. warning::

    Erroneous ``TokenCode`` values (i.e. non 6-digit numeric strings) will raise errors during construction of ``assume_role_kwargs``. 
    Ensure your token provider returns valid tokens.

.. warning::

    For security, the ``shell``, ``executable``, and ``preexec_fn`` :py:func:`subprocess.run` parameters are blocked by default. 
    You may enable them with ``allow_shell``, ``allow_executable``, and ``allow_preexec_fn``, but use extreme caution. 
    ``stdout`` and ``stderr`` overrides are not supported.

.. _cachedocs:

Client Caching
--------------

boto3-refresh-session supports ``Client`` caching using an LRU eviction strategy.
The purpose of this feature is to minimize the massive memory footprint of multiple ``Client`` objects created with identical parameters.
To do this, when ``cache_clients`` is enabled, ``Client`` objects created via the refreshable session's ``client`` method are cached and reused for subsequent calls with the same parameters.

.. tip::
    
    **boto3-refresh-session caches clients by default**; to disable client caching, set ``cache_clients=False`` when initializing ``RefreshableSession``.

.. tip:: 
    
    To interact with the client cache directly, reference the ``RefreshableSession.client_cache`` attribute.

.. note::
    
    In order to retrieve clients from the cache, you must use the ``ClientCacheKey`` object.

.. code-block:: python
    
    from boto3_refresh_session import AssumeRoleConfig, ClientCacheKey, RefreshableSession

    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(RoleArn="<your-role-arn>")
    )
    
    # deliberately creating two clients with the same parameters
    s3_client_1 = session.client("s3", region_name="us-east-1")
    s3_client_2 = session.client("s3", region_name="us-east-1")

    # but s3_client_1 and s3_client_2 are the same object since client caching is enabled
    assert s3_client_1 is s3_client_2

    # accessing the client cache directly via client_cache
    # and retrieving the cached client using ClientCacheKey
    cache_key = ClientCacheKey("s3", region_name="us-east-1")
    cached_s3_client = session.client_cache.get(cache_key)

    # and ensuring equality again
    assert s3_client_1 is cached_s3_client

IoT Core X.509
--------------

.. note::

    This section requires that you have installed boto3-refresh-session with the IoT extra.
    If you have not done so, please reinstall using:
    
    .. code-block:: bash

        pip install boto3-refresh-session[iot]

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
