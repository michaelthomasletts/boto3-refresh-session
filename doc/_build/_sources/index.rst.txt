boto3-refresh-session
=====================

A simple Python package for refreshing boto3 sessions automatically.

.. toctree::
   :maxdepth: 1
   :hidden:

   API Reference <reference/index>
   Installation <installation>

Information
-----------
- :doc:`API Reference <./reference/index>`
- :doc:`Installation <./installation>`

Usage
-----

This package is extremely easy to use. Simply pass the basic parameters and
initialize the ``AutoRefreshableSession`` class; that's it! You're good to go!

``AutoRefreshableSession`` will refresh
temporary credentials for you in the background. In the following example,
continue using the ``s3_client`` object without worry of using `try` and 
`except` blocks!

To use this package, your machine must be configured with AWS
credentials. To learn more about how ``boto3`` searches for credentials on a
machine, check `this documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_.

.. code-block:: python

   sess = AutoRefreshableSession(
      region="<your-region>",
      role_arn="<your-role-arn>",
      session_name="<your-session-name>",
   )
   s3_client = sess.session.client(service_name="s3")

Authors
-------
- `Michael Letts <https://michaelthomasletts.github.io/>`_