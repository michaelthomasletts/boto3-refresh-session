.. image:: brs.png
   :align: center

|

.. toctree::
   :maxdepth: 1
   :hidden:

   API Reference <reference/index>
   Installation <installation>
   Authorization <authorization>
   Authors <authors>

boto3-refresh-session
---------------------

A simple Python package for refreshing temporary AWS credentials for ``boto3`` automatically.

Who is this for?
----------------

Software Engineers, Data Engineers, Machine Learning Engineers, DevOps Engineers -- anyone who uses AWS with ``boto3``.

Why should I use this?
----------------------

It is common for data pipelines and workflows that interact with the AWS API via 
``boto3`` to run for a long time and, accordingly, for temporary credentials to 
expire. 

Usually, engineers deal with that problem one of two ways: 

- ``try except`` blocks that catch ``ClientError`` exceptions
- A similar approach as that used in this project -- that is, using methods available 
  within ``botocore`` for refreshing temporary credentials automatically. 
  
Speaking personally, variations of the code found herein exists in code bases at 
nearly every company where I have worked. Sometimes, I turned that code into a module; 
other times, I wrote it from scratch. Clearly, that is inefficient.

I decided to finally turn that code into a proper Python package with unit testing, 
automatic documentation, and quality checks; the idea being that, henceforth, depending 
on my employer's open source policy, I may simply import this package instead of 
reproducing the code herein for the Nth time.

If any of that sounds relatable, then ``boto3-refresh-session`` should help you.

How do I use this?
------------------

This package is extremely easy to use. Simply pass the basic parameters and
initialize the ``AutoRefreshableSession`` class; that's it! You're good to go!

``AutoRefreshableSession`` will refresh temporary credentials for you in the 
background. In the following example, continue using the ``s3_client`` object 
without worry of using ``try`` and ``except`` blocks! For context, you can pass
any ``service_name`` parameter you want, so long as it's included in ``boto3``. 
The following example uses ``s3`` merely for illustrative purposes.

To use this package, your machine must be configured with AWS
credentials. To learn more about how ``boto3`` searches for credentials on a
machine, check the :ref:`authorization documentation <authorization>`.

.. code-block:: python
   
   import boto3_refresh_session as brs

   sess = brs.AutoRefreshableSession(
      region="<your-region>",
      role_arn="<your-role-arn>",
      session_name="<your-session-name>",
   )
   s3_client = sess.session.client(service_name="s3")