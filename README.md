# boto3-refresh-session
[![PyPI Download](https://img.shields.io/pypi/v/boto3-refresh-session?logo=pypis.svg)](https://pypi.org/project/boto3-refresh-session/)
[![Workflow](https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push.yml?logo=github)](https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push_pullrequest.yml)
![Python Version](https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi)
![GitHub last commit](https://img.shields.io/github/last-commit/michaelthomasletts/boto3-refresh-session?logo=github)
![PyPI - Downloads](https://img.shields.io/pypi/dm/boto3-refresh-session?logo=pypi)

![BRS Image](https://raw.githubusercontent.com/michaelthomasletts/boto3-refresh-session/refs/heads/main/doc/brs.png)

A simple Python package for refreshing the temporary security credentials in a `boto3.session.Session` object automatically.

- [Documentation](https://michaelthomasletts.github.io/boto3-refresh-session/index.html)
- [Source Code](https://github.com/michaelthomasletts/boto3-refresh-session)
- [PyPI](https://pypi.org/project/boto3-refresh-session/)
- [Contributing](https://michaelthomasletts.github.io/boto3-refresh-session/contributing.html)

### Why should I use this?

It is common for data pipelines and workflows that interact with the AWS API via 
`boto3` to run for a long time and, accordingly, for temporary credentials to 
expire. 

Usually, engineers deal with that problem one of two different ways: 

- A `try except` block that catches `botocore.exceptions.ClientError` exceptions
- A similar approach as that used in this project -- that is, using methods available 
  within `botocore` for refreshing temporary credentials automatically. 
  
Speaking personally, variations of the code found herein exists in code bases at 
nearly every company where I have worked. Sometimes, I turned that code into a module; 
other times, I wrote it from scratch. Clearly, that is inefficient.

I decided to finally turn that code into a proper Python package with unit testing, 
automatic documentation, and quality checks; the idea being that, henceforth, depending 
on my employer's open source policy, I may simply import this package instead of 
reproducing the code herein for the Nth time.

If any of that sounds relatable, then `boto3-refresh-session` should help you!

### Usage

Simply pass the basic parameters and initialize the `RefreshableSession` object; 
that's it! You're good to go!

`RefreshableSession` will refresh
temporary credentials for you in the background. In the following example,
continue using the `s3_client` object without worry of using `try` and 
`except` blocks!

To use this package, your machine must be configured with AWS
credentials. To learn more about how `boto3` searches for credentials on a
machine, check [this documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

```python
import boto3_refresh_session as brs

assume_role_kwargs = {
  'RoleArn': '<your-role-arn>',
  'RoleSessionName': '<your-role-session-name>',
  'DurationSeconds': '<your-selection>',
  ...
}
sts_client_kwargs = {
  ...
}
session = brs.RefreshableSession(
  assume_role_kwargs=assume_role_kwargs,
  sts_client_kwargs=sts_client_kwargs,
  region_name='us-east-1',
)
s3 = session.client(service_name='s3')
buckets = s3.list_buckets()
```

### Installation

```bash
pip install boto3-refresh-session
```

### Authors

- [Michael Letts](https://michaelthomasletts.github.io/)
