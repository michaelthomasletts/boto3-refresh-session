# boto3-refresh-session
[![PyPI Download](https://img.shields.io/pypi/v/boto3-refresh-session?logo=pypis.svg)](https://pypi.org/project/boto3-refresh-session/)
[![Workflow](https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push.yml?logo=github)](https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push.yml)
![Python Version](https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi)
![GitHub last commit](https://img.shields.io/github/last-commit/michaelthomasletts/boto3-refresh-session?logo=github)
![PyPI Downloads (Monthly)](https://img.shields.io/pypi/dm/boto3-refresh-session?logo=pypi)
![PyPI Downloads (Total)](https://static.pepy.tech/badge/boto3-refresh-session)

![BRS Image](https://raw.githubusercontent.com/michaelthomasletts/boto3-refresh-session/refs/heads/main/doc/brs.png)

A simple Python package for refreshing the temporary security credentials in a `boto3.session.Session` object automatically.

- [Official Documentation](https://michaelthomasletts.github.io/boto3-refresh-session/index.html)
- [Source Code](https://github.com/michaelthomasletts/boto3-refresh-session)
- [PyPI](https://pypi.org/project/boto3-refresh-session/)
- [Contributing](https://michaelthomasletts.github.io/boto3-refresh-session/contributing.html)
- [Authorization](https://michaelthomasletts.github.io/boto3-refresh-session/authorization.html)

### Installation

```bash
pip install boto3-refresh-session
```

### Usage

```python
import boto3_refresh_session as brs

# you can pass all of the params associated with boto3.session.Session
profile_name = '<your-profile-name>'
region_name = 'us-east-1'
...

# as well as all of the params associated with STS.Client.assume_role
assume_role_kwargs = {
  'RoleArn': '<your-role-arn>',
  'RoleSessionName': '<your-role-session-name>',
  'DurationSeconds': '<your-selection>',
  ...
}

# as well as all of the params associated with STS.Client, except for 'service_name'
sts_client_kwargs = {
  'region_name': region_name,
  ...
}

# basic initialization of boto3.session.Session
session = brs.RefreshableSession(
  assume_role_kwargs=assume_role_kwargs, # required
  sts_client_kwargs=sts_client_kwargs,
  region_name=region_name,
  profile_name=profile_name,
  ...
)

# now you can create clients, resources, etc. without worrying about expired temporary 
# security credentials
s3 = session.client(service_name='s3')
buckets = s3.list_buckets()
```

### Raison d'être

It is common for data pipelines and workflows that interact with the AWS API via 
`boto3` to run for a long time and, accordingly, for temporary credentials to 
expire. 

Usually, engineers deal with that problem one of two ways: 

- `try except` blocks that catch `ClientError` exceptions
- A similar approach as that used in this project -- that is, using methods available 
  within `botocore` for refreshing temporary credentials automatically. 
  
Speaking personally, variations of the code found herein exists in code bases at 
nearly every company where I have worked. Sometimes, I turned that code into a module; 
other times, I wrote it from scratch. Clearly, that is inefficient.

I decided to finally turn that code into a proper Python package with unit testing, 
automatic documentation, and quality checks; the idea being that, henceforth, depending 
on my employer's open source policy, I may simply import this package instead of 
reproducing the code herein for the Nth time.

If any of that sounds relatable, then `boto3-refresh-session` should help you.