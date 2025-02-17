# boto3-refresh-session
[![PyPI Download](https://img.shields.io/pypi/v/boto3-refresh-session?logo=pypis.svg)](https://pypi.org/project/boto3-refresh-session/)
[![Workflow](https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push_pullrequest.yml?logo=github)](https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push_pullrequest.yml)
![Python Version](https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi)

![BRS Image](https://raw.githubusercontent.com/michaelthomasletts/boto3-refresh-session/refs/heads/main/doc/brs.png)

A simple Python package for refreshing boto3 sessions automatically.

- [Documentation](https://michaelthomasletts.github.io/boto3-refresh-session/index.html)
- [Source Code](https://github.com/michaelthomasletts/boto3-refresh-session)
- [PyPI](https://pypi.org/project/boto3-refresh-session/)

### Why should I use this?

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

If any of that sounds relatable, then `boto3-refresh-session` should help you!

### Usage

Simply pass the basic parameters and initialize the `AutoRefreshableSession` object; 
that's it! You're good to go!

`AutoRefreshableSession` will refresh
temporary credentials for you in the background. In the following example,
continue using the `s3_client` object without worry of using `try` and 
`except` blocks!

To use this package, your machine must be configured with AWS
credentials. To learn more about how `boto3` searches for credentials on a
machine, check [this documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

```
sess = AutoRefreshableSession(
    region="<your-region>",
    role_arn="<your-role-arn>",
    session_name="<your-session-name>",
)
s3_client = sess.session.client(service_name="s3")
```

### Authors

- [Michael Letts](https://michaelthomasletts.github.io/)