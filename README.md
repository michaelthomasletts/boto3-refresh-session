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
    <img src="https://img.shields.io/pypi/v/boto3-refresh-session?color=%23FF0000FF&logo=python&label=Latest%20Version" alt="PyPI - Version"/>
  </a>

  <a href="https://pypi.org/project/boto3-refresh-session/">
    <img src="https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi&color=%23FF0000FF&logo=python&label=Compatible%20Python%20Versions" alt="Python Version"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push.yml?logo=github&color=%23FF0000FF&label=Build" alt="Workflow"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/commits/main">
    <img src="https://img.shields.io/github/last-commit/michaelthomasletts/boto3-refresh-session?logo=github&color=%23FF0000FF&label=Last%20Commit" alt="GitHub last commit"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/stargazers">
    <img src="https://img.shields.io/github/stars/michaelthomasletts/boto3-refresh-session?style=flat&logo=github&labelColor=555&color=FF0000&label=Stars" alt="Stars"/>
  </a>

  <a href="https://pypistats.org/packages/boto3-refresh-session">
    <img src="https://img.shields.io/badge/downloads-72.1K-red?logo=python&color=%23FF0000&label=Downloads%20%28with%20mirrors%29" alt="Downloads with mirrors"/>
  </a>

  <a href="https://pypistats.org/packages/boto3-refresh-session">
    <img src="https://img.shields.io/badge/downloads-18.1K-red?logo=python&color=%23FF0000&label=Downloads%20%28without%20mirrors%29" alt="Downloads without mirrors"/>
  </a>  

  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/index.html">
    <img src="https://img.shields.io/badge/Official%20Documentation-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" alt="Documentation Badge"/>
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session">
    <img src="https://img.shields.io/badge/Source%20Code-💻-FF0000?style=flat&labelColor=555&logo=github" alt="Source Code Badge"/>
  </a>

  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/qanda.html">
    <img src="https://img.shields.io/badge/Q%26A-❔-FF0000?style=flat&labelColor=555&logo=vercel&label=Q%26A" alt="Q&A Badge"/>
  </a>

  <a href="https://medium.com/@lettsmt/you-shouldnt-have-to-think-about-refreshing-aws-credentials-214f7cbbd83b">
    <img src="https://img.shields.io/badge/Medium%20Article-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" alt="Medium Article"/>
  </a>

<a href="https://github.com/sponsors/michaelthomasletts">
  <img src="https://img.shields.io/badge/Sponsor%20this%20Project-💙-FF0000?style=flat&labelColor=555&logo=githubsponsors" alt="Sponsorship"/>
</a>


</div>

## Features

- Drop-in replacement for `boto3.session.Session`
- Supports automatic credential refresh methods for various AWS services:
  - STS
  - ECS
- Supports custom authentication methods for complicated authentication flows
- Natively supports all parameters supported by `boto3.session.Session`
- [Tested](https://github.com/michaelthomasletts/boto3-refresh-session/tree/main/tests), [documented](https://michaelthomasletts.github.io/boto3-refresh-session/index.html), and [published to PyPI](https://pypi.org/project/boto3-refresh-session/)
- Future releases will include support for EC2, IoT, SSO, and OIDC

## Recognition, Adoption, and Testimonials

[Featured in TL;DR Sec.](https://tldrsec.com/p/tldr-sec-282)

[Featured in CloudSecList.](https://cloudseclist.com/issues/issue-290)

Recognized during AWS Community Day Midwest on June 5th, 2025.

A testimonial from a Cyber Security Engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive [...] We're using the RefreshableSession class as part of a client cache construct [...] We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

## Installation

```bash
pip install boto3-refresh-session
```

## Usage (STS)

Most users use AWS STS to assume an IAM role and return a set of temporary security credentials. boto3-refresh-session can be used to ensure those temporary credentials refresh automatically.

```python
import boto3_refresh_session as brs

# you can pass all of the params normally associated with boto3.session.Session
profile_name = "<your-profile-name>"
region_name = "us-east-1"
...

# as well as all of the params associated with STS.Client.assume_role
assume_role_kwargs = {
  "RoleArn": "<your-role-arn>",
  "RoleSessionName": "<your-role-session-name>",
  "DurationSeconds": "<your-selection>",
  ...
}

# as well as all of the params associated with STS.Client, except for 'service_name'
sts_client_kwargs = {
  "region_name": region_name,
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
```

## Usage (ECS)

You can use boto3-refresh-session in an ECS container to automatically refresh temporary security credentials.

```python
session = RefreshableSession(
  method="ecs", 
  region_name=region_name, 
  profile_name=profile_name,
  ...
)
```

## Usage (Custom)

If you have a highly sophisticated, novel, or idiosyncratic authentication flow not included in boto3-refresh-session then you will need to provide your own custom temporary credentials callable object. `RefreshableSession` accepts custom credentials callable objects, as shown below.

```python
# create (or import) your custom credential method
def your_custom_credential_getter(...):
    ...
    return {
        "access_key": ...,
        "secret_key": ...,
        "token": ...,
        "expiry_time": ...,
    }

# and pass it to RefreshableSession
session = RefreshableSession(
    method="custom",
    custom_credentials_method=your_custom_credential_getter,
    custom_credentials_method_args=...,
    region_name=region_name,
    profile_name=profile_name,
    ...
)
```