.. _authorization:

Authorization
*************

.. warning::
    MFA is not robustly supported at this time! 

    While ``STSRefreshableSession`` accepts MFA parameters via ``assume_role_kwargs`` (specifically ``SerialNumber`` and ``TokenCode``), 
    there is presently no mechanism for dynamically updating the MFA token between credential refreshes. 
    Since MFA tokens typically expire every 30 seconds, this means the first credential refresh will succeed but *subsequent* refreshes 
    will fail with stale tokens. For workflows requiring MFA, in the meantime, developers must use ``method="custom"`` and implement their 
    own credential retrieval logic that prompts for fresh MFA tokens on each refresh. This workaround is functional but cumbersome. 
    A more elegant solution involving an MFA token provider callback is planned for a future release!    

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