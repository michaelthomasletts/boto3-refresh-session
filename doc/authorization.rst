.. _authorization:

Authorization
*************

.. warning::
    ``AutoRefreshableSession`` was not tested for manually passing hard-coded
    account credentials to the :class:`boto3.session.Session`` or ``boto3.client`` 
    objects! There are optional ``session_kwargs`` and ``client_kwargs``
    parameters available for passing hard-coded account credentials, which
    *should* work; however, that cannot be guaranteed! In any case, the ``boto3``
    documentation generally recommends against passing hard-coded account credentials
    as parameters; it is for that reason the documentation below, and everywhere
    else, only mentions ``~/.aws/config`` and ``~/.aws/credentials`` for 
    authorization. Since the ``session_kwargs`` and ``client_kwargs`` parameters 
    were not tested, you will need to use those parameters at your own discretion.

In order to use this package, it is **recommended** that you follow one of the
below methods for authorizing access to your AWS instance:

- Create local environment variables containing your credentials, 
  e.g. ``ACCESS_KEY``, ``SECRET_KEY``, and ``SESSION_TOKEN``.
- Create a shared credentials file, i.e. ``~/.aws/credentials``.
- Create an AWS config file, i.e. ``~/.aws/config``.
  
For additional details concerning how to authorize access, check the 
`boto3 documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_.

For additional details concerning how to configure an AWS credentials file
on your machine, check the `AWS CLI documentation <https://aws.amazon.com/cli/>`_.