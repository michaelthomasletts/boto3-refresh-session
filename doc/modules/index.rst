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

   exceptions
   session
   sts
   ecs

Core interface
--------------

Basic usage of boto3-refresh-session requires familiarity only with the `session` module.
The :class:`boto3_refresh_session.session.RefreshableSession` class provides a unified interface for all supported credential refresh strategies.

.. tip::
   
   For most users, STS is sufficient — there’s no need to manually specify the ``method`` parameter unless using advanced strategies like ECS.
   All users should, however, familiarize themselves with the documentation in the Refresh strategies in order to understand required and optional parameters and available methods.

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

Exceptions and Warnings
-----------------------

Mistakes and problems happen. You can find all of the custom exceptions and warnings for boto3-refresh-session below.

- :ref:`exceptions` - Exceptions and warnings for boto3-refresh-session.