# boto3-refresh-session
[![PyPI Download](https://img.shields.io/pypi/v/boto3-refresh-session?logo=pypis.svg)](https://pypi.org/project/boto3-refresh-session/)
[![Workflow](https://img.shields.io/github/actions/workflow/status/michaelthomasletts/boto3-refresh-session/push_pullrequest.yml?logo=github)](https://github.com/michaelthomasletts/boto3-refresh-session/actions/workflows/push_pullrequest.yml)
![Python Version](https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi)

## Overview

A simple Python package for refreshing boto3 sessions automatically.

## Features
- `boto3_refresh_session.AutoRefreshableSession` method for generating an automatically refreshing `boto.Session` object.

## Installation

To install the package using `pip`:

```bash
$ pip install boto3-refresh-session
```

Refer to the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for configuring credentials on your machine.

## Directory

```
boto3_refresh_session
├── __init__.py
└── session.py
```

## Usage

Here's how to initialize the `boto3.Client.S3` object:

>>> from boto3_refresh_session import AutoRefreshableSession
>>> session = AutoRefreshableSession(region="us-east-1", role_arn="<your-arn>", session_name="test")
>>> s3_client = session.session.client(service_name="s3")