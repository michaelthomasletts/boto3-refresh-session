.. _cache:

.. currentmodule:: boto3_refresh_session.utils.cache

Cache
=====

By default, :class:`RefreshableSession` employs a boto client cache with an LRU eviction strategy.
This feature was introduced in order to minimize the (surprisingly) massive memory footprint of duplicative boto clients.
Each time a client is instantiated or retrieved from the cache, the cache is updated to mark that client as recently used.
When the maximum size of the cache is reached, the least recently used client is evicted from the cache.
You can interact with the cache like a ``dict``; however, some methods, like ``setdefault``, are not supported.

.. note::

    In a future release, boto3-refresh-session may optionally include LFU caching as an alternative strategy to LRU.

To disable caching, set ``cache_clients=False`` when instantiating the session.
To increase the maximum size of the cache, set ``client_cache_max_size`` to the desired integer value (the default is 10).
To retrieve a particular client from the cache, instantiate :class:`ClientCacheKey` with the specific boto parameters and use it to query the session's ``client_cache`` attribute.

.. code-block:: python

    from boto3_refresh_session import(
        AssumeRoleConfig,
        ClientCacheKey,
        RefreshableSession,
    )

    # instantiate a session with default LRU caching
    session = RefreshableSession(
        assume_role_kwargs=AssumeRoleConfig(
            RoleArn="<your role arn>"
        ),
    )

    # instantiate an S3 client
    s3 = session.client("s3", region_name="us-west-2")

    ...

    # later, retrieve that client using the same parameters via ClientCacheKey
    cache_key = ClientCacheKey("s3", region_name="us-west-2")
    s3_client = session.client_cache.get(cache_key)

    # clear the cache if you like
    session.client_cache.clear()

.. tip::

   Refer to the `client caching documentation <../usage.html#cache>`_ for additional details on usage.

Cache
-----

.. autosummary::
   :toctree: generated/
   :nosignatures:

   ClientCache
   ClientCacheKey