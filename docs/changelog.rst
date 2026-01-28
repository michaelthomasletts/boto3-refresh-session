.. _changelog:

Changelog
*********

v3.0.0
------

**The changes introduced by v3.0.0 will not impact ~99% of users** who generally interact with ``boto3-refresh-session`` by only ``RefreshableSession``, *which is the intended usage for this package after all.* 

Advanced users, however, particularly those using low-level objects such as ``BaseRefreshableSession | refreshable_session | BRSSession | utils.py``, may experience breaking changes. 

Please review `this PR <https://github.com/michaelthomasletts/boto3-refresh-session/pull/75>`__ for additional details.

v4.0.0
------

The ``ecs`` module has been dropped. For additional details and rationale, please review `this PR <https://github.com/michaelthomasletts/boto3-refresh-session/pull/78>`__.

v5.0.0
------

Support for IoT Core via X.509 certificate-based authentication (over HTTPS) is now available!

v5.1.0
------

MQTT support added for IoT Core via X.509 certificate-based authentication.

v6.0.0
------

MFA support for STS added!

v6.2.0
------

- Client caching introduced to ``RefreshableSession`` in order to minimize memory footprint! Available via ``cache_clients`` parameter.
- Testing suite expanded to include IOT, MFA, caching, and much more!
- A subtle bug was uncovered where ``RefreshableSession`` created refreshable credentials but boto3's underlying session continued to resolve credentials via the default provider chain (i.e. env vars, shared config, etc) unless explicitly wired. ``get_credentials()`` and clients could, in certain setups, use base session credentials instead of the refreshable STS/IoT/custom credentials via assumed role. To fix this, I updated the implementation in ``BRSSession.__post_init__`` to set ``self._session._credentials = self._credentials``, ensuring all boto3 clients created from ``RefreshableSession`` use the refreshable credentials source of truth provided to ``RefreshableCredentials | DeferredRefreshableCredentials``. After this change, refreshable credentials are used consistently everywhere, irrespective of setup.

v6.2.3
------

- The ``RefreshableTemporaryCredentials`` type hint was deprecated in favor of ``TemporaryCredentials``.
- ``expiry_time`` was added as a parameter returned by the ``refreshable_credentials`` method and ``credentials`` attribute.

v6.3.0
------

The exception suite was expanded to include new exceptions which are more precise than ``BRSError``. Additionally, new parameters were added to ``BRSError`` in order to make error handling more robust. Since these new exceptions inherit from ``BRSError``, developers catching exceptions raised by ``BRSError`` will not experience breaking changes; however, code that checks ``type(err) is BRSError`` (instead of ``isinstance``), exact ``str(err) / repr(err)`` comparisons, and parsing messages instead of using the new attributes (e.g. ``details|code|status_code|param|value``, etc.) may experience breaking changes.

v7.0.0
------

Beginning v7.0.0, boto3-refresh-session is licensed under `Mozilla Public License 2.0 (MPL-2.0) <https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/LICENSE>`_. 
Earlier versions remain licensed under the MIT License.

v7.1.0
------

``AssumeRoleConfig`` and ``STSClientConfig`` objects were added to ``boto3_refresh_session.utils``.
These objects encapsulate configuration parameters for assuming roles via STS, enhancing code readability and maintainability.
Users should find it easier to manage and pass around STS-related configurations using these.
Dictionaries are still supported for backward compatibility on ``sts_client_kwargs`` and ``assume_role_kwargs``.
However, using these new objects is now the recommended approach.
Refer to the `PR <https://github.com/michaelthomasletts/boto3-refresh-session/pull/102>`_ for more details.

v7.1.12
-------
LRU caching has been added to ``ClientCache`` which previously did not have an eviction strategy. 
To disable client caching altogether, set ``cache_clients=False`` when initializing ``RefreshableSession`` (it's set to True by default).
To adjust the default maximum size of the client cache (which is 10), set the ``client_cache_max_size`` parameter when initializing ``RefreshableSession``.
When caching is enabled, the least recently used client will be evicted when the cache exceeds its maximum size.
The ``_client_cache`` private attribute in ``RefreshableSession`` has been replaced with ``client_cache``, which invites direct interaction with the ``ClientCache`` instance for advanced use cases.
Lastly, the hashing (keying) strategy for ``ClientCache`` has been adjusted to require ``ClientCacheKey``. 
Simply pass ``*args`` and ``**kwargs`` (the same parameters passed to ``RefreshableSession.client``) to ``ClientCache`` when calling it to store or retrieve clients, and it will internally create a ``ClientCacheKey`` for you.

v7.2.0
------

As of v7.2.0, ``boto3-refresh-session`` requires explicitly installing "iot" as an extra dependency in order to use IoT features, i.e. ``pip install boto3-refresh-session[iot]``.
This change was made to reduce the number of dependencies for users who do not require IoT functionality.