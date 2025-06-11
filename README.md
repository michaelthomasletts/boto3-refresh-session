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

  <a href="https://pepy.tech/project/boto3-refresh-session">
    <img src="https://img.shields.io/badge/downloads-57.4K-red?logo=python&color=%23FF0000&label=Downloads" alt="Downloads"/>
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

</div>

## Features

- Auto-refreshing credentials for long-lived `boto3` sessions
- Drop-in replacement for `boto3.session.Session`
- Supports `assume_role` configuration, custom STS clients, and profile / region configuration, as well as all other parameters supported by `boto3.session.Session`
- Tested, documented, and published to PyPI

## Recognition, Adoption, and Testimonials

[Featured in TL;DR Sec.](https://tldrsec.com/p/tldr-sec-282)

Recognized during AWS Community Day Midwest on June 5th, 2025.

A testimonial from a Cyber Security Engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive [...] We're using the RefreshableSession class as part of a client cache construct [...] We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

The following line plot illustrates the adoption of BRS over the last three months in terms of average daily downloads over a rolling seven day window.

<p align="center">
  <img src="https://raw.githubusercontent.com/michaelthomasletts/boto3-refresh-session/refs/heads/main/doc/downloads.png" />
</p>

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

Long-running data pipelines, security tooling, ETL jobs, and cloud automation scripts frequently interact with the AWS API using boto3 — and often run into the same problem:

**Temporary credentials expire.**

When that happens, engineers typically fall back on one of two strategies:

- Wrapping AWS calls in try/except blocks that catch ClientError exceptions
- Writing ad hoc logic to refresh credentials using botocore credentials internals

Both approaches are fragile, tedious to maintain, and error-prone at scale.

Over the years, I noticed that every company I worked for — whether a scrappy startup or FAANG — ended up with some variation of the same pattern:  
a small in-house module to manage credential refresh, written in haste, duplicated across services, and riddled with edge cases. Things only 
got more strange and difficult when I needed to run things in parallel.

Eventually, I decided to build boto3-refresh-session as a proper open-source Python package:  

- Fully tested  
- Extensible  
- Integrated with boto3 idioms  
- Equipped with automatic documentation and CI tooling  

**The goal:** to solve a real, recurring problem once — cleanly, consistently, and for everyone - with multiple refresh strategies.

If you've ever written the same AWS credential-refresh boilerplate more than once, this library is for you. 