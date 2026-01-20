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
    <img 
      src="https://img.shields.io/pypi/v/boto3-refresh-session?color=%23FF0000FF&logo=python&label=Latest%20Version"
      alt="pypi_version"
    />
  </a>

  <a href="https://pypi.org/project/boto3-refresh-session/">
    <img 
      src="https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi&color=%23FF0000FF&logo=python&label=Compatible%20Python%20Versions" 
      alt="py_version"
    />
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push.yml">
    <img 
      src="https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push.yml?logo=github&color=%23FF0000FF&label=Build" 
      alt="workflow"
    />
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/commits/main">
    <img 
      src="https://img.shields.io/github/last-commit/michaelthomasletts/boto3-refresh-session?logo=github&color=%23FF0000FF&label=Last%20Commit" 
      alt="last_commit"
    />
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/stargazers">
    <img 
      src="https://img.shields.io/github/stars/michaelthomasletts/boto3-refresh-session?style=flat&logo=github&labelColor=555&color=FF0000&label=Stars" 
      alt="stars"
    />
  </a>

<a href="https://pepy.tech/projects/boto3-refresh-session">
  <img
    src="https://img.shields.io/endpoint?url=https%3A%2F%2Fmichaelthomasletts.github.io%2Fpepy-stats%2Fboto3-refresh-session.json&style=flat&logo=python&labelColor=555&color=FF0000"
    alt="downloads"
  />
</a>


  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/index.html">
    <img 
      src="https://img.shields.io/badge/Official%20Documentation-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" 
      alt="documentation"
    />
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session">
    <img 
      src="https://img.shields.io/badge/Source%20Code-💻-FF0000?style=flat&labelColor=555&logo=github" 
      alt="github"
    />
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/LICENSE">
    <img 
      src="https://img.shields.io/static/v1?label=License&message=MPL-2.0&color=FF0000&labelColor=555&logo=github&style=flat"
      alt="license"
    />
  </a>

<a href="https://github.com/sponsors/michaelthomasletts">
  <img 
    src="https://img.shields.io/badge/Sponsor%20this%20Project-💙-FF0000?style=flat&labelColor=555&logo=githubsponsors" 
    alt="sponsorship"
  />
</a>

</div>

## Features

- Drop-in replacement for `boto3.session.Session`
- MFA support included for STS
- SSO support via AWS profiles
- Optionally caches boto3 clients
- Supports automatic temporary credential refresh for: 
  - **STS**
  - **IoT Core** 
    - X.509 certificates w/ role aliases over mTLS (PEM files and PKCS#11)
    - MQTT actions are available!
- [Tested](https://github.com/michaelthomasletts/boto3-refresh-session/tree/main/tests), [documented](https://michaelthomasletts.github.io/boto3-refresh-session/index.html), and [published to PyPI](https://pypi.org/project/boto3-refresh-session/)

## Recognition and Testimonials

[Featured in TL;DR Sec.](https://tldrsec.com/p/tldr-sec-282)

[Featured in CloudSecList.](https://cloudseclist.com/issues/issue-290)

Recognized during AWS Community Day Midwest on June 5th, 2025 (the founder's birthday!).

A testimonial from a Cyber Security Engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive [...] We're using the RefreshableSession class as part of a client cache construct [...] We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

## Installation

boto3-refresh-session is available on PyPI:

```bash
pip install boto3-refresh-session
```

## Quick Start Guide

Basic, bare-bones initialization:

```python
from boto3_refresh_session import AssumeRoleConfig, RefreshableSession

session = RefreshableSession(
  AssumeRoleConfig(
    RoleArn="<your role arn>"
  )
)
```

Basic initilization including some additional session parameters:

```python
from boto3_refresh_session import AssumeRoleConfig, RefreshableSession

session = RefreshableSession(
  AssumeRoleConfig(
    RoleArn="<your role arn>"
  ),
  region_name="<your region name>",
  profile_name="<your aws profile name>",
)
```

Slightly advanced initialization using an MFA token provider (Yubikey):

```python
from boto3_refresh_session import AssumeRoleConfig, RefreshableSession
import subprocess
from typing import Sequence


def mfa_token_provider(cmd: Sequence[str], timeout: float):
  p = subprocess.run(
    list(cmd),
    check=False,
    capture_output=True,
    text=True,
    timeout=timeout,
  )
  return (p.stdout or "").strip()


mfa_token_provider_kwargs = {
  "cmd": ["ykman", "oath", "code", "--single", "AWS-prod"],  # example token source
  "timeout": 3.0,
}

session = RefreshableSession(
  AssumeRoleConfig(
    RoleArn="<your role arn>",
    SerialNumber="<your MFA device arn>",
  ),
  mfa_token_provider=mfa_token_provider,
  mfa_token_provider_kwargs=mfa_token_provider_kwargs,
)
```

## Usage

Refer to the [official usage documentation](https://michaelthomasletts.com/boto3-refresh-session/usage.html) for guidance on general usage.

Refer to the [official API documentation](https://michaelthomasletts.com/boto3-refresh-session/modules/index.html) for technical information.

## Versions

Refer to the [changelog](https://michaelthomasletts.com/boto3-refresh-session/changelog.html) for additional information on specific versions and releases.

## License

Beginning v7.0.0, `boto3-refresh-session` is licensed under [Mozilla Public License 2.0 (MPL-2.0)](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/LICENSE). Earlier versions remain licensed under the MIT License.
