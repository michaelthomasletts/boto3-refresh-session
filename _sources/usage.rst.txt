.. _usage:

Usage
*****

In order to use this package, you must have AWS credentials configured on your machine locally. Check the :ref:`authorization documentation <authorization>` for additional details.

Basic Initialization
--------------------

``Client`` and ``Resource`` objects in ``boto3`` are derived from the :class:`boto3.session.Session` object. 
In other words, everything in ``boto3`` is basically a :class:`boto3.session.Session` object. 
That knowledge matters because it directly implicates your ability to flexibly use boto3-refresh-session or incorporate it into your existing code with minimal effort.

A ``Client`` object can be created directly from the :class:`boto3_refresh_session.session.RefreshableSession` object.
For your convenience, that code, which initializes an ``S3.Client`` object for illustrative purposes, is included below.

.. code-block:: python
    
    import boto3
    import boto3_refresh_session
    
    assume_role_kwargs = {
        'RoleArn': '<your-role-arn>',
        'RoleSessionName': '<your-role-session-name>',
        'DurationSeconds': '<your-selection>',
    }
    session = boto3_refresh_session.RefreshableSession(
        assume_role_kwargs=assume_role_kwargs
    )
    s3 = session.client(service_name='s3')

You can also create a ``Resource`` object in exactly the same way as above.

.. code-block:: python

    s3 = session.resource("s3")

Alternatively, you can reuse the same :class:`boto3_refresh_session.session.RefreshableSession` object everywhere by assigning the ``session`` object we created above to ``DEFAULT_SESSION`` as well. 

.. code-block:: python

    boto3.DEFAULT_SESSION = session
    s3_client = boto3.client("s3")

Parameters
----------

In order to use :class:`boto3_refresh_session.session.RefreshableSession`, you are **required** to configure parameters for the :meth:`STS.Client.assume_role` method which are assigned to the ``assume_role_kwargs`` parameter.


.. code-block:: python

    assume_role_kwargs = {
        'RoleArn': '<your-role-arn>',
        'RoleSessionName': '<your-role-session-name>',
        'DurationSeconds': '<your-selection>',
        ...
    }

You may also want to provide **optional** parameters for the :class:`STS.Client` object.

.. code-block:: python

    sts_client_kwargs = {
        ...
    }

You may also provide optional parameters for the :class:`boto3.session.Session` object when initializing the :class:`boto3_refresh_session.session.RefreshableSession` object. Below, we use the ``region_name`` parameter for illustrative purposes.

.. code-block:: python

    import boto3_refresh_session

    session = boto3_refresh_session.RefreshableSession(
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name='us-east-1',
    )

There are two ways of refreshing temporary credentials automatically with the :class:`boto3_refresh_session.session.RefreshableSession` object: 

* Refresh credentials the moment they expire, or 
* Wait until temporary credentials are explicitly requested. 
  
The latter is the default.
The former must be configured using the ``defer_refresh`` parameter, as shown below.

.. code-block:: python

    session = boto3_refresh_session.RefreshableSession(
        defer_refresh=False,
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name='us-east-1',
    )

.. warning::
    It is **highly recommended** that you set the ``defer_refresh`` parameter to ``True`` (the default).
    Reason being that refreshing temporary credentials the *moment* they expire incurs backend effort that may be superfluous. 
    ``defer_refresh`` set to ``False`` is only recommended for systems that demand low latency, i.e. available temporary credentials at all times.