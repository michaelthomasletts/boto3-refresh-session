# boto3-refresh-session
[![PyPI Download](https://img.shields.io/pypi/v/boto3-refresh-session?logo=pypis.svg)](https://pypi.org/project/boto3-refresh-session/)
[![Workflow](https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push_pullrequest.yml?logo=github)](https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push_pullrequest.yml)
![Python Version](https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi)

## Overview

A simple Python package for refreshing boto3 sessions automatically.

## Links

[Official Documentation](https://michaelthomasletts.github.io/boto3-refresh-session/index.html)

## Features
- `boto3_refresh_session.AutoRefreshableSession` method for generating an automatically refreshing `boto3.Session` object.

## Installation

To install the package using `pip`:

```bash
$ pip install boto3-refresh-session
```

**This package assumes that you have `~/.aws/config` or `~/.aws/credentials` files or `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables configured on your machine!** 

Refer to the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for additional details about configuring those credentials on your machine.

## Directory

```
boto3_refresh_session
├── __init__.py
└── session.py
```

## Usage

Here's how to initialize the `boto3.Client.S3` object:

```python
from boto3_refresh_session import AutoRefreshableSession


session = AutoRefreshableSession(
    region="us-east-1", role_arn="<your-arn>", session_name="test"
)
s3_client = session.session.client(service_name="s3")
```