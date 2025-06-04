<div align="center">
  <img src="https://raw.githubusercontent.com/michaelthomasletts/boto3-refresh-session/refs/heads/main/doc/brs.png" />
</div>

</br>

<div align="center"><em>
  A simple Python package for refreshing the temporary security credentials in a <code>boto3.session.Session</code> object automatically.
</em></div>

</br>

<div align="center">

  <a href="https://pypi.org/project/boto3-refresh-session/">
    <img src="https://img.shields.io/pypi/v/boto3-refresh-session?color=%23FF0000FF&logo=python" alt="PyPI - Version"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push.yml?logo=github&color=%23FF0000FF" alt="Workflow"/>
  </a>

  <a href="https://pypi.org/project/boto3-refresh-session/">
    <img src="https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi&color=%23FF0000FF&logo=python" alt="Python Version"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/commits/main">
    <img src="https://img.shields.io/github/last-commit/michaelthomasletts/boto3-refresh-session?logo=github&color=%23FF0000FF" alt="GitHub last commit"/>
  </a>

  <a href="https://pepy.tech/project/boto3-refresh-session">
    <img src="https://img.shields.io/badge/downloads-53.7K-red?logo=python&color=%23FF0000" alt="Downloads"/>
  </a>

  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/index.html">
    <img src="https://img.shields.io/badge/official%20documentation-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" alt="Documentation Badge"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session">
    <img src="https://img.shields.io/badge/source%20code-💻-FF0000?style=flat&labelColor=555&logo=github" alt="Source Code Badge"/>
  </a>

  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/qanda.html">
    <img src="https://img.shields.io/badge/Q%26A-❔-FF0000?style=flat&labelColor=555&logo=vercel" alt="Q&A Badge"/>
  </a>

</div>

## Features

- Auto-refreshing credentials for long-lived `boto3` sessions
- Drop-in replacement for `boto3.session.Session`
- Supports `assume_role` configuration, custom STS clients, and profile / region configuration, as well as all other parameters supported by `boto3.session.Session`
- Tested, documented, and published to PyPI
- Used in production at major tech companies

## Adoption

The following line plot illustrates the adoption of BRS from the last three months in terms of average daily downloads over a rolling seven day window.

<p align="center">
  <img src="https://raw.githubusercontent.com/michaelthomasletts/boto3-refresh-session/refs/heads/main/doc/downloads.png" />
</p>

## Testimonials

From a Cyber Security Engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive . . . we're using the RefreshableSession class as part of a client cache construct . . . we're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

## Installation

```bash
pip install boto3-refresh-session
```

## Usage

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

## Raison d'être

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

---

📄 Licensed under the MIT License.