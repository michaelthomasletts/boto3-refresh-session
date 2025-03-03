.. _usage:

Usage
*****

In order to use :class:`boto3_refresh_session.session.RefreshableSession`, you are required to configure parameters for the :meth:`STS.Client.assume_role` method.

.. code-block:: python

    assume_role_kwargs = {
        'RoleArn': '<your-role-arn>',
        'RoleSessionName': '<your-role-session-name>',
        'DurationSeconds': '<your-selection>',
        ...
    }

You may also want to provide optional parameters for the :class:`STS.Client` object.

.. code-block:: python

    sts_client_kwargs = {
        ...
    }

You may also provide optional parameters for the :class:`boto3.session.Session` object when initializing the ``RefreshableSession`` object. Below, we use the ``region_name`` parameter for illustrative purposes.

.. code-block:: python

    import boto3_refresh_session

    session = boto3_refresh_session.RefreshableSession(
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name='us-east-1',
    )

Using the ``session`` variable that you just created, you can now use all of the methods available from the :class:`boto3.session.Session` object. In the below example, we initialize an S3 client and list all available buckets.

.. code-block:: python

    s3 = session.client(service_name='s3')
    buckets = s3.list_buckets()

There are two ways of refreshing temporary credentials automatically with the :class:`boto3_refresh_session.session.RefreshableSession` object: 

* Refresh credentials the moment they expire, or 
* Wait until temporary credentials are explicitly needed. 
  
The latter is the default. The former must be configured using the ``defer_refresh`` parameter, as shown below.

.. code-block:: python

    session = boto3_refresh_session.RefreshableSession(
        defer_refresh=False,
        assume_role_kwargs=assume_role_kwargs,
        sts_client_kwargs=sts_client_kwargs,
        region_name='us-east-1',
    )