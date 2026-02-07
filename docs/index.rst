boto3-refresh-session
---------------------

**Version:** |release|

**License:** Mozilla Public License 2.0 (MPL-2.0)

**Authors:** `Mike Letts <https://michaelthomasletts.github.io/>`_

boto3-refresh-session is a simple Python package with a drop-in replacement for :class:`boto3.session.Session` named :class:`boto3_refresh_session.session.RefreshableSession`. 
It automatically refreshes temporary AWS credentials, caches clients, and natively supports MFA providers. 
It also supports automatic temporary AWS security credential refresh for STS, IOT Core, and custom credential callables.

For more information about using boto3-refresh-session, see the :ref:`Usage Guide <usage>`.
For technical documentation of all features and parameters, see the :ref:`API docs <api>`.
For a detailed list of changes, see the :ref:`Changelog <changelog>`.

.. toctree::
   :maxdepth: 1
   :caption: Sitemap
   :name: sitemap
   :hidden:

   Usage <usage>
   API <api/index>
   Changelog <changelog>