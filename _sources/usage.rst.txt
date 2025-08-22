.. _usage:

Usage
*****

To use `boto3-refresh-session`, you must have AWS credentials configured locally.  
Refer to the :ref:`authorization documentation <authorization>` for details on supported authentication methods.

Basic Initialization
--------------------

Everything in `boto3` is ultimately built on the :class:`boto3.session.Session` object — 
including ``Client`` and ``Resource`` objects.  
`boto3-refresh-session` extends this interface while adding automatic credential refresh.

Creating a session is straightforward:

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

You can also create a ``Resource`` the same way:

.. code-block:: python

    s3 = session.resource('s3')

Optional: set this session globally as the default for `boto3`:

.. code-block:: python

    import boto3
    boto3.DEFAULT_SESSION = session
    s3 = boto3.client('s3')  # will use the custom session automatically

Parameters
----------

At a minimum, you must provide parameters for the STS ``assume_role`` call via ``assume_role_kwargs``:

.. code-block:: python

    assume_role_kwargs = {
        "RoleArn": "<your-role-arn>",
        "RoleSessionName": "<your-session-name>",
        "DurationSeconds": 3600,  # optional
    }

Optional keyword arguments for the underlying ``boto3.client("sts")`` can be passed via ``sts_client_kwargs``:

.. code-block:: python

    sts_client_kwargs = {
        "config": Config(retries={"max_attempts": 5})
    }

And any arguments accepted by :class:`boto3.session.Session` (e.g., ``region_name``, etc.) can be passed directly:

.. code-block:: python

    session = RefreshableSession(
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name="us-east-1"
    )

Refresh Behavior
----------------

There are two ways to trigger automatic credential refresh:

1. **Deferred (default)** — Refresh occurs only when credentials are required  
2. **Eager** — Credentials are refreshed as soon as they expire

Set ``defer_refresh`` to False to enable eager refresh:

.. code-block:: python

    session = RefreshableSession(
        defer_refresh=False,
        assume_role_kwargs=assume_role_kwargs
    )

.. warning::
    It is **highly recommended** to use the default: ``defer_refresh=True``.  
    Eager refresh adds overhead and is only suitable for low-latency systems that cannot tolerate refresh delays.

Parallel Usage and Performance
------------------------------

If you're working with large datasets and sensitive value detection or redaction, 
you may wish to use ``boto3-refresh-session`` in parallel.

The core session class is thread-safe and compatible with Python’s ``concurrent.futures`` or ``multiprocessing``.

To maximize throughput:

- Reuse a single ``RefreshableSession`` object across threads or subprocesses
- Use ``defer_refresh=True`` to avoid concurrent refreshes at process boundaries
- Mount the session into a poolable or global shared object

**Example (using concurrent.futures):**

.. code-block:: python

    from concurrent.futures import ThreadPoolExecutor
    from boto3_refresh_session import RefreshableSession

    session = RefreshableSession(assume_role_kwargs={...})

    def upload_one(bucket, key, body):
        s3 = session.client("s3")
        s3.put_object(Bucket=bucket, Key=key, Body=body)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(upload_one, "my-bucket", f"file-{i}", b"data")
            for i in range(10)
        ]

    for future in futures:
        future.result()

.. note::

    For process-based concurrency (e.g., ``ProcessPoolExecutor``), initialize the session 
    **before** spawning or forking the pool. This ensures memory is shared efficiently via copy-on-write, 
    and avoids unnecessary duplication of temporary credentials.
