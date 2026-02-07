boto3-refresh-session
---------------------

**Version:** |release|

**License:** Mozilla Public License 2.0 (MPL-2.0)

**Author:** `Mike Letts <https://michaelthomasletts.com>`_

boto3-refresh-session is a simple Python package with a drop-in replacement for :class:`boto3.session.Session` named :class:`boto3_refresh_session.session.RefreshableSession`. 
It automatically refreshes temporary AWS credentials, caches clients, and natively supports MFA providers. 
It also supports automatic temporary AWS security credential refresh for STS, IOT Core, and custom credential callables.

Although boto3 already supports automatic temporary credential refresh via role assumption as configured in ``~/.aws/config``, there are 
scenarios and edge cases where that is insufficient. Below are just a *few* examples:

- Profiles or configs are unavailable or impractical (e.g., containerized or serverless environments)
- You need to explicitly assume roles in a program (not profiles or configs) and hand those credentials around without worrying about expiration
- Custom credential providers are required (e.g. IOT, external ID, etc.)

boto3-refresh-session exists to fill those gaps (and others not listed above) while maintaining full compatibility with boto3.

Although there are other open source tools available which address automatic temporary AWS credential refresh, boto3-refresh-session is ergonomically designed to feel like an *extension* of boto3 (with a few extra parameters) rather than a separate library with an unfamiliar API.
More, the available alternatives to boto3-refresh-session do not support the breadth of features that boto3-refresh-session does, such as client caching, MFA providers, or IoT Core X.509 credential refresh, among others.
Even if you don't need automatic temporary AWS credential refresh, boto3-refresh-session's client caching feature may still be useful to you.

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