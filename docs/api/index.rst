.. _api:

.. currentmodule:: boto3_refresh_session

API
===

boto3-refresh-session includes multiple modules, grouped into several broad categories:

- The core interface (session)
- Individual modules for each supported refresh strategy (e.g., STS)
- The LRU cache
- Configuration objects
- Exceptions and warnings

Learn more about each of these categories below.

.. toctree::
   :maxdepth: 1
   :hidden:

   session
   custom
   iot
   sts
   cache
   config
   exceptions   

Core interface
--------------

Basic usage of boto3-refresh-session requires familiarity only with the `session` module.
The :class:`boto3_refresh_session.session.RefreshableSession` class provides a unified interface for all supported credential refresh strategies.

.. tip::
   
   For most users, STS is sufficient — there’s no need to manually specify the ``method`` parameter unless using advanced strategies like ``custom``.
   All users should, however, familiarize themselves with the documentation in the Refresh strategies in order to understand required and optional parameters and available methods.

- :ref:`session` — Factory interface for creating refreshable boto3 sessions

Refresh strategies
------------------

boto3-refresh-session supports multiple AWS services.
There is also a highly flexible module named "custom" for users with highly sophisticated, novel, or idiosyncratic credential flows.

.. tip::
   
   It is recommended to use :class:`boto3_refresh_session.session.RefreshableSession` instead of initializing the below classes.
   Refer to the below documentation to understand what sort of parameters each refresh strategy requires and what sort of methods
   are available.

Each strategy supported by boto3-refresh-session is encapsulated in its own module below.

- :ref:`custom` - Refresh strategy using a custom credential refresh strategy
- :ref:`iot` - Refresh strategies for IoT Core
- :ref:`sts` — Refresh strategy using :class:`STS.Client`

Cache
-----

boto3-refresh-session caches boto clients to avoid redundant client creation. 
Learn more about the caching mechanism below.

.. tip::

   Refer to the `client caching documentation <../usage.html#cache>`_ for additional details.

- :ref:`cache` - LRU cache for boto3-refresh-session

Configs
-------

boto3-refresh-session provides configuration objects to encapsulate configuration for STS and role assumption.

- :ref:`config` - Configuration objects for boto3-refresh-session

Exceptions and warnings
-----------------------

Mistakes and problems happen. You can find all of the custom exceptions and warnings for boto3-refresh-session below.

- :ref:`exceptions` - Exceptions and warnings for boto3-refresh-session.