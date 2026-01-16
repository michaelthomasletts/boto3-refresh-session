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

  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/qanda.html">
    <img 
      src="https://img.shields.io/badge/Q%26A-❔-FF0000?style=flat&labelColor=555&logo=vercel&label=Q%26A" 
      alt="qanda"
    />
  </a>

  <a href="https://michaelthomasletts.github.io/blog/brs-rationale/">
    <img 
      src="https://img.shields.io/badge/Blog%20Post-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" 
      alt="blog"
    />
  </a>

<a href="https://github.com/sponsors/michaelthomasletts">
  <img 
    src="https://img.shields.io/badge/Sponsor%20this%20Project-💙-FF0000?style=flat&labelColor=555&logo=githubsponsors" 
    alt="sponsorship"
  />
</a>

</div>

## 😛 Features

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

## 😌 Recognition and Testimonials

[Featured in TL;DR Sec.](https://tldrsec.com/p/tldr-sec-282)

[Featured in CloudSecList.](https://cloudseclist.com/issues/issue-290)

Recognized during AWS Community Day Midwest on June 5th, 2025 (the founder's birthday!).

A testimonial from a Cyber Security Engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive [...] We're using the RefreshableSession class as part of a client cache construct [...] We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

## 💻 Installation

```bash
pip install boto3-refresh-session
```

## 🏃 Quick Start Guide

Follow these guides for getting started with `boto3-refresh-session`.

#### Basic

The following example shows the initialization of `RefreshableSession` _using AWS env vars, `~/.aws/credentials`, or default AWS profile_ and how to initialize an S3 client.

```python
from boto3_refresh_session import RefreshableSession

session = RefreshableSession(
  assume_role_kwargs={
    "RoleArn": "arn:aws:iam::123456789012:role/CoolGuy", # required
  },
  region_name="us-east-1",
)
s3 = session.client("s3")
```

#### Advanced

The following example shows how to:

- Initialize `RefreshableSession` _using a non-default AWS profile_
- Enable MFA support
- Initialize an S3 client with some configurations

```python
from boto3_refresh_session import RefreshableSession
from botocore.config import Config
import subprocess


def mfa_token_provider(cmd: list[str], timeout: float = 10.0):
  """Returns an MFA code. Accepts commands which emit tokens."""

  p = subprocess.run(
    cmd,
    check=False,
    capture_output=True,
    text=True,
    timeout=timeout,
  )
  return (p.stdout or "").strip()


session = RefreshableSession(
  assume_role_kwargs={
    "RoleArn": "arn:aws:iam::123456789012:role/CoolGuy", # required
    "RoleSessionName": "just-goofin-around", # defaults to 'boto3-refresh-session'
    "SerialNumber": "arn:aws:iam::123456789012:mfa/test-user", # required if using MFA
  },
  mfa_token_provider=mfa_token_provider, # required if using MFA
  mfa_token_provider_kwargs={ # depends on if mfa_token_provider needs args
    "cmd": ["ykman", "oath", "code", "--single", "AWS-prod"],
    "timeout": 3.0
  },
  profile_name="test-aws-profile",
  region_name="us-east-1",
)
s3 = session.client("s3", config=Config(retries={"max_attempts": 2}))
```

## 📝 Usage

<details>
  <summary><strong>Core Concepts (click to expand)</strong></summary>

  ### Core Concepts

  1. `RefreshableSession` is the intended interface for using `boto3-refresh-session`. Whether you're using this package to refresh temporary credentials returned by STS, the IoT credential provider (which is really just STS, but I digress), or some custom authentication or credential provider, `RefreshableSession` is where you *ought to* be working when using `boto3-refresh-session`.

  2. *You can use all of the same keyword parameters normally associated with `boto3.session.Session`!* For instance, suppose you want to pass `region_name` to `RefreshableSession` as a parameter, whereby it's passed to `boto3.session.Session`. That's perfectly fine! Just pass it like you normally would when initializing `boto3.session.Session`. These keyword parameters are *completely optional*, though. If you're confused, the main idea to remember is this: if initializing `boto3.session.Session` *requires* a particular keyword parameter then pass it to `RefreshableSession`; if not, don't worry about it.

  3. To tell `RefreshableSession` which AWS service you're working with for authentication and credential retrieval purposes (STS vs. IoT vs. some custom credential provider), you'll need to pass a `method` parameter to `RefreshableSession`. Since the `service_name` namespace is already occupied by `boto3.sesssion.Session`, [`boto3-refresh-session` uses `method` instead of "service" so as to avoid confusion](https://github.com/michaelthomasletts/boto3-refresh-session/blob/04acb2adb34e505c4dc95711f6b2f97748a2a489/boto3_refresh_session/utils/typing.py#L40). If you're using `RefreshableSession` for STS, however, then `method` is set to `"sts"` by default. You don't need to pass the `method` keyword argument in that case.

  4. Using `RefreshableSession` for STS, IoT, or custom flows requires different keyword parameters that are unique to those particular methods. For instance, `STSRefreshableSession`, which is the engine for STS in `boto3-refresh-session`, requires `assume_role_kwargs` and optionally allows `sts_client_kwargs` whereas `CustomRefreshableSession` and `IoTX509RefreshableSession` do not. To familiarize yourself with the keyword parameters for each method, check the documentation for each of those engines [in the Refresh Strategies section here](https://michaelthomasletts.com/boto3-refresh-session/modules/index.html).

  5. Irrespective of whatever `method` you pass as a keyword parameter, `RefreshableSession` accepts a keyword parameter named `defer_refresh`. Basically, this boolean tells `boto3-refresh-session` either to refresh credentials *the moment they expire* or to *wait until credentials are explicitly needed*. If you are working in a low-latency environment then `defer_refresh = False` might be helpful. For most users, however, `defer_refresh = True` is most desirable. For that reason, `defer_refresh = True` is the default value. Most users, therefore, should not concern themselves too much with this feature.

  6. Some developers struggle to imagine where `boto3-refresh-session` might be helpful. To figure out if `boto3-refresh-session` is for your use case, or whether `credential_process` satisfies your needs, check out [this blog post](https://michaelthomasletts.com/blog/brs-rationale/). `boto3-refresh-session` is not for every developer or use-case; it is a niche tool. 

  7. `boto3-refresh-session` supports client caching in order to minimize the massive memory footprint associated with duplicative clients. By default, `RefreshableSession` caches clients. To deactivate this feature, set `cache_clients=False`.

  8. `boto3-refresh-session` supports MFA. Refer to the MFA section further below for more details.

  9. `boto3-refresh-session` supports SSO; however, it _does not_ and _will never_ automatically handle `sso login` for you -- that is, not unless you write your own hacky custom credential getter and pass that to `RefreshableSession(method="custom", ...)`, which I do not recommend (but cannot prevent you from doing). 

</details>

<details>
  <summary><strong>Clients (click to expand)</strong></summary>

  ### Clients

  Most developers who use `boto3` interact primarily with `boto3.client` instead of `boto3.session.Session`. But many developers may not realize that `boto3.session.Session` belies `boto3.client`! In fact, that's precisely what makes `boto3-refresh-session` possible!

  Before we get to initializing clients via `RefreshableSession`, however, let's briefly talk about `boto3` clients and memory . . . 
  
  Clients consume a shocking amount of memory. So much so that many developers create their own bespoke client cache. To minimize the memory footprint associated with duplicative clients, as well as make the lives of developers a little easier, `boto3-refresh-session` includes a `cache_clients` parameter which, by default, caches clients according to the parameters passed to the `client` method!
  
  With client caching out of the way, in order to use the `boto3.client` interface, but with the benefits of `boto3-refresh-session`, you have a few options! In the following examples, let's assume you want to use STS for retrieving temporary credentials for the sake of simplicity. Let's also focus specifically on `client`. Switching to `resource` follows the same exact idioms as below, except that `client` must be switched to `resource` in the pseudo-code, obviously. If you are not sure how to use `RefreshableSession` for STS (or custom auth flows) then check the usage instructions in the following sections!

  ##### `RefreshableSession.client` (Recommended)

  So long as you reuse the same `session` object when creating `client` objects, this approach can be used everywhere in your code.

  ```python
  from boto3_refresh_session import RefreshableSession

  assume_role_kwargs = {
    "RoleArn": "<your-role-arn>",
    "RoleSessionName": "<your-role-session-name>",
    "DurationSeconds": "<your-selection>",
    ...
  }
  session = RefreshableSession(assume_role_kwargs=assume_role_kwargs)
  s3 = session.client("s3")
  ```  

  ##### `DEFAULT_SESSION`

  This technique can be helpful if you want to use the same instance of `RefreshableSession` everywhere in your code without reference to `boto3_refresh_session`!

  ```python
  from boto3 import DEFAULT_SESSION, client
  from boto3_refresh_session import RefreshableSession

  assume_role_kwargs = {
    "RoleArn": "<your-role-arn>",
    "RoleSessionName": "<your-role-session-name>",
    "DurationSeconds": "<your-selection>",
    ...
  }
  DEFAULT_SESSION = RefreshableSession(assume_role_kwargs=assume_role_kwargs)
  s3 = client("s3")
  ```

  ##### `botocore_session`

  ```python
  from boto3 import client
  from boto3_refresh_session import RefreshableSession

  assume_role_kwargs = {
    "RoleArn": "<your-role-arn>",
    "RoleSessionName": "<your-role-session-name>",
    "DurationSeconds": "<your-selection>",
    ...
  }
  s3 = client(
    service_name="s3",
    botocore_session=RefreshableSession(assume_role_kwargs=assume_role_kwargs)
  )
  ```  

  </details>

<details>
  <summary><strong>STS (click to expand)</strong></summary>

  ### STS

  Most developers use AWS STS to assume an IAM role and return a set of temporary security credentials. boto3-refresh-session can be used to ensure those temporary credentials refresh automatically. For additional information on the exact parameters that `RefreshableSession` takes for STS, [check this documentation](https://michaelthomasletts.com/boto3-refresh-session/modules/generated/boto3_refresh_session.methods.sts.STSRefreshableSession.html).

  ```python
  import boto3_refresh_session as brs


  assume_role_kwargs = {
    "RoleArn": "<your IAM role arn>",  # required
    "RoleSessionName": "<your role session name>",  # required
    ...
  }

  session = brs.RefreshableSession(
    assume_role_kwargs=assume_role_kwargs,  # required
    sts_client_kwargs={...},  # optional
    ...  # misc. params for boto3.session.Session
  )
  ```

</details>

<details>
  <summary><strong>MFA (click to expand)</strong></summary>

  ### MFA Support

  When assuming a role that requires MFA, `boto3-refresh-session` supports automatic token provisioning through the `mfa_token_provider` parameter. This parameter accepts a callable that returns a fresh MFA token code (string) whenever credentials need to be refreshed.

  The `mfa_token_provider` approach is **strongly recommended** over manually providing `TokenCode` in `assume_role_kwargs`, as MFA tokens expire after 30 seconds while AWS temporary credentials can last for hours. By using a callable, your application can automatically fetch fresh tokens on each refresh without manual intervention. There is nothing preventing you from manually providing `TokenCode` *without* `mfa_token_provider`; however, *you* will be responsible for updating `TokenCode` *before* automatic temporary credential refresh occurs, which is likely to be a fragile and complicated approach.

  When using `mfa_token_provider`, you must also provide `SerialNumber` (your MFA device ARN) in `assume_role_kwargs`. For additional information on the exact parameters that `RefreshableSession` takes for MFA, [check this documentation](https://michaelthomasletts.com/boto3-refresh-session/modules/generated/boto3_refresh_session.methods.sts.STSRefreshableSession.html).

  ⚠️ Most developers will probably find example number four most helpful.

  #### Examples

  ```python
  import boto3_refresh_session as brs

  # Example 1: Interactive prompt for MFA token
  def get_mfa_token():
      return input("Enter MFA token: ")

  # we'll reuse this object in each example for simplicity :)
  assume_role_kwargs = {
      "RoleArn": "<your-role-arn>",
      "RoleSessionName": "<your-role-session-name>",
      "SerialNumber": "arn:aws:iam::123456789012:mfa/your-user",  # required with mfa_token_provider
  }

  session = brs.RefreshableSession(
      assume_role_kwargs=assume_role_kwargs,
      mfa_token_provider=get_mfa_token,  # callable that returns MFA token
  )

  # Example 2: Using pyotp for TOTP-based MFA
  import pyotp

  def get_totp_token():
      totp = pyotp.TOTP("<your-secret-key>")
      return totp.now()

  session = brs.RefreshableSession(
      assume_role_kwargs=assume_role_kwargs,
      mfa_token_provider=get_totp_token,
  )

  # Example 3: Retrieving token from environment variable or external service
  import os

  def get_env_token():
      return os.environ.get("AWS_MFA_TOKEN", "")

  session = brs.RefreshableSession(
      assume_role_kwargs=assume_role_kwargs,
      mfa_token_provider=get_env_token,
  )

  # Example 4: Using Yubikey (or any token provider CLI)
  from typing import Sequence
  import subprocess

  def mfa_token_provider(cmd: Sequence[str], timeout: float):
    p = subprocess.run(
      list(cmd),
      check=False,
      capture_output=True,
      text=True,
      timeout=timeout,
    )
    return (p.stdout or "").strip()

  mfa_token_provider_args = {
      "cmd": ["ykman", "oath", "code", "--single", "AWS-prod"],  # example token source
      "timeout": 3.0,
  }

  session = RefreshableSession(
      assume_role_kwargs=assume_role_kwargs,
      mfa_token_provider=mfa_token_provider,
      mfa_token_provider_args=mfa_token_provider_args,
  )
  ```
</details>

<details>
  <summary><strong>SSO (click to expand)</strong></summary>
  
  ### SSO

  `boto3-refresh-session` supports SSO by virtue of AWS profiles.

  The below pseudo-code illustrates how to assume an IAM role using an AWS profile with SSO. Not shown, however, is running `sso login` manually, which `boto3-refresh-session` does not perform automatically for you. Therefore, you must manually run `sso login` as necessary.
  
  If you wish to automate `sso login` (not recommended) then you will need to write your own custom callable function and pass it to `RefreshableSession(method="custom", ...)`. In that event, please refer to the `Custom` documentation found in a separate section below.

  ```python
  from boto3_refresh_session import RefreshableSession

  session = RefreshableSession(
    assume_role_kwargs={
      "RoleArn": "<your IAM role arn>",
      "RoleSessionName": "<your role session name>",
    },
    profile_name="<your AWS profile name>",
    ...
  )
  s3 = session.client("s3")
  ```  
</details>

<details>
  <summary><strong>Custom (click to expand)</strong></summary>

  ### Custom

  If you have a highly sophisticated, novel, or idiosyncratic authentication flow not included in boto3-refresh-session then you will need to provide your own custom temporary credentials callable object. `RefreshableSession` accepts custom credentials callable objects, as shown below. For additional information on the exact parameters that `RefreshableSession` takes for custom authentication flows, [check this documentation](https://michaelthomasletts.com/boto3-refresh-session/modules/generated/boto3_refresh_session.methods.custom.CustomRefreshableSession.html#boto3_refresh_session.methods.custom.CustomRefreshableSession).

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
      method="custom",                                         # required
      custom_credentials_method=your_custom_credential_getter, # required
      custom_credentials_method_args=...,                      # optional
      region_name=region_name,                                 # optional
      profile_name=profile_name,                               # optional
      ...                                                      # misc. boto3.session.Session params
  )
  ```

</details>

<details>
  <summary><strong>IoT Core X.509 (click to expand)</strong></summary>

  ### IoT Core X.509

  AWS IoT Core can vend temporary AWS credentials through the **credentials provider** when you connect with an X.509 certificate and a **role alias**. `boto3-refresh-session` makes this flow seamless by automatically refreshing credentials over **mTLS**.

  For additional information on the exact parameters that `IOTX509RefreshableSession` takes, [check this documentation](https://michaelthomasletts.com/boto3-refresh-session/modules/generated/boto3_refresh_session.methods.iot.x509.IOTX509RefreshableSession.html).

  ### PEM file

  ```python
  import boto3_refresh_session as brs

  # PEM certificate + private key example
  session = brs.RefreshableSession(
      method="iot",
      endpoint="<your-credentials-endpoint>.credentials.iot.<region>.amazonaws.com",
      role_alias="<your-role-alias>",
      certificate="/path/to/certificate.pem",
      private_key="/path/to/private-key.pem",
      thing_name="<your-thing-name>",       # optional, if used in policies
      duration_seconds=3600,                # optional, capped by role alias
      region_name="us-east-1",
  )

  # Now you can use the session like any boto3 session
  s3 = session.client("s3")
  print(s3.list_buckets())
  ```

  ### PKCS#11

  ```python
  session = brs.RefreshableSession(
      method="iot",
      endpoint="<your-credentials-endpoint>.credentials.iot.<region>.amazonaws.com",
      role_alias="<your-role-alias>",
      certificate="/path/to/certificate.pem",
      pkcs11={
          "pkcs11_lib": "/usr/local/lib/softhsm/libsofthsm2.so",
          "user_pin": "1234",
          "slot_id": 0,
          "token_label": "MyToken",
          "private_key_label": "MyKey",
      },
      thing_name="<your-thing-name>",
      region_name="us-east-1",
  )
  ```

  ### MQTT

  After initializing a session object, you can can begin making actions with MQTT using the [mqtt method](https://github.com/michaelthomasletts/boto3-refresh-session/blob/deb68222925bf648f26e878ed4bc24b45317c7db/boto3_refresh_session/methods/iot/x509.py#L367)! You can reuse the same certificate, private key, et al as that used to initialize `RefreshableSession`. Or, alternatively, you can provide separate PKCS#11 or certificate information, whether those be file paths or bytes values. Either way, at a minimum, you will need to provide the endpoint and client identifier (i.e. thing name).

  ```python
  from awscrt.mqtt.QoS import AT_LEAST_ONCE
  conn = session.mqtt(
    endpoint="<your endpoint>-ats.iot.<region>.amazonaws.com",
    client_id="<your thing name or client ID>",
  )
  conn.connect()
  conn.connect().result()
  conn.publish(topic="foo/bar", payload=b"hi", qos=AT_LEAST_ONCE)
  conn.disconnect().result()
  ```

</details>

## ⚠️ Changes

Browse through the various changes to `boto3-refresh-session` over time.

#### 😥 v3.0.0

**The changes introduced by v3.0.0 will not impact ~99% of users** who generally interact with `boto3-refresh-session` by only `RefreshableSession`, *which is the intended usage for this package after all.* 

Advanced users, however, particularly those using low-level objects such as `BaseRefreshableSession | refreshable_session | BRSSession | utils.py`, may experience breaking changes. 

Please review [this PR](https://github.com/michaelthomasletts/boto3-refresh-session/pull/75) for additional details.

#### ✂️ v4.0.0

The `ecs` module has been dropped. For additional details and rationale, please review [this PR](https://github.com/michaelthomasletts/boto3-refresh-session/pull/78).

#### 😛 v5.0.0

Support for IoT Core via X.509 certificate-based authentication (over HTTPS) is now available!

#### ➕ v5.1.0

MQTT support added for IoT Core via X.509 certificate-based authentication.

#### ➕ v6.0.0

MFA support for STS added!

#### 🔒😥 v6.2.0

- Client caching introduced to `RefreshableSession` in order to minimize memory footprint! Available via `cache_clients` parameter.
- Testing suite expanded to include IOT, MFA, caching, and much more!
- A subtle bug was uncovered where `RefreshableSession` created refreshable credentials but boto3's underlying session continued to resolve credentials via the default provider chain (i.e. env vars, shared config, etc) unless explicitly wired. `get_credentials()` and clients could, in certain setups, use base session credentials instead of the refreshable STS/IoT/custom credentials via assumed role. To fix this, I updated the implementation in `BRSSession.__post_init__` to set `self._session._credentials = self._credentials`, ensuring all boto3 clients created from `RefreshableSession` use the refreshable credentials source of truth provided to `RefreshableCredentials | DeferredRefreshableCredentials`. After this change, refreshable credentials are used consistently everywhere, irrespective of setup.

#### ✂️ v6.2.3

- The `RefreshableTemporaryCredentials` type hint was deprecated in favor of `TemporaryCredentials`.
- `expiry_time` was added as a parameter returned by the `refreshable_credentials` method and `credentials` attribute.