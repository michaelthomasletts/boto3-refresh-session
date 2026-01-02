.. _authorization:

Authorization
************* 

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