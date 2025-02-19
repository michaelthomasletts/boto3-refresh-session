.. _authorization:

Authorization
*************

.. warning::
    ``AutoRefreshableSession`` was not tested for manually passing hard-coded
    account credentials to the ``boto3.client`` object! There is an optional 
    ``client_kwargs`` parameter available for doing so, which *should* work; 
    however, that cannot be guaranteed as that functionality was not tested.
    Pass hard-coded credentials with the ``client_kwargs`` parameter at your
    own discretion.

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