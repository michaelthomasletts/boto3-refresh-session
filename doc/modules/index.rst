.. _modules:

.. currentmodule:: boto3_refresh_session

Modules
=======

boto3-refresh-session includes multiple modules, grouped into two categories:

- The core interface (session)
- Individual modules for each supported refresh strategy (e.g., STS)

.. toctree::
   :maxdepth: 1
   :hidden:

   session
   sts
   ecs

Core interface
--------------

Basic usage of boto3-refresh-session requires familiarity only with the `session` module.
The :class:`boto3_refresh_session.session.RefreshableSession` class provides a unified interface for all supported credential refresh strategies.

.. tip::
   
   For most users, STS is sufficient — there’s no need to manually specify the ``method`` parameter unless using advanced strategies like ECS.

.. tip::

   :class:`boto3_refresh_session.session.RefreshableSession`, no matter what value is specified to ``method=...``, has access to the following functions and properties:

   - ``get_identity()``
   - ``refreshable_credentials()``
   - ``credentials``

- :ref:`session` — Factory interface for creating refreshable boto3 sessions

Refresh strategies
------------------

boto3-refresh-session is designed to grow.
In addition to the default STS strategy, support for additional credential sources like AWS IoT, SSO, and others will be added in future releases.

.. tip::
   
   It is recommended to use :class:`boto3_refresh_session.session.RefreshableSession` instead of initializing the below classes. 

Each strategy supported by boto3-refresh-session is encapsulated in its own module below.

- :ref:`sts` — Refresh strategy using :class:`STS.Client`
- :ref:`ecs` - Refresh strategy using AWS ECS container metadata
