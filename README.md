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

  <a href="https://medium.com/@lettsmt/you-shouldnt-have-to-think-about-refreshing-aws-credentials-214f7cbbd83b">
    <img 
      src="https://img.shields.io/badge/Medium%20Article-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" 
      alt="medium"
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
- Supports automatic credential refresh methods for STS
- Supports custom authentication methods with automatic refresh for complicated authentication flows
- Natively supports all parameters supported by `boto3.session.Session`
- [Tested](https://github.com/michaelthomasletts/boto3-refresh-session/tree/main/tests), [documented](https://michaelthomasletts.github.io/boto3-refresh-session/index.html), and [published to PyPI](https://pypi.org/project/boto3-refresh-session/)
- Future releases will include support for IoT (coming soon)

## ⚠️ Important Updates

#### 😥 v3.0.0

**The changes introduced by v3.0.0 will not impact ~99% of users** who generally interact with `boto3-refresh-session` by only `RefreshableSession`, *which is the intended usage for this package after all.* 

Advanced users, however, particularly those using low-level objects such as `BaseRefreshableSession | refreshable_session | BRSSession | utils.py`, may experience breaking changes. 

Please review [this PR](https://github.com/michaelthomasletts/boto3-refresh-session/pull/75) for additional details.

#### ☎️ Delayed Responses

I am currently grappling with a very serious medical condition. Accordingly, expect delayed responses to issues and requests until my health stabilizes.

## 😌 Recognition and Testimonials

[Featured in TL;DR Sec.](https://tldrsec.com/p/tldr-sec-282)

[Featured in CloudSecList.](https://cloudseclist.com/issues/issue-290)

Recognized during AWS Community Day Midwest on June 5th, 2025.

A testimonial from a Cyber Security Engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive [...] We're using the RefreshableSession class as part of a client cache construct [...] We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

## 💻 Installation

```bash
pip install boto3-refresh-session
```

## 📝 Usage

<details>
  <summary><strong>Clients and Resources (click to expand)</strong></summary>

  ### Clients and Resources

  Most developers who use `boto3` interact primarily with `boto3.client` or `boto3.resource` instead of `boto3.session.Session`. But many developers may not realize that `boto3.session.Session` belies `boto3.client` and `boto3.resource`! In fact, that's precisely what makes `boto3-refresh-session` possible!

  To use the `boto3.client` or `boto3.resource` interface, but with the benefits of `boto3-refresh-session`, you have a few options! 
  
  In the following examples, let's assume you want to use STS for retrieving temporary credentials for the sake of simplicity. Let's also focus specifically on `client`. Switching to `resource` follows the same exact idioms as below, except that `client` must be switched to `resource` in the pseudo-code, obviously. If you are not sure how to use `RefreshableSession` for STS (or custom auth flows) then check the usage instructions in the following sections!

  ##### `RefreshableSession.client` (Recommended)

  So long as you reuse the same `session` object when creating `client` and `resource` objects, this approach can be used everywhere in your code. It is very simple and straight-forward!

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

  Most developers use AWS STS to assume an IAM role and return a set of temporary security credentials. boto3-refresh-session can be used to ensure those temporary credentials refresh automatically. For additional information on the exact parameters that `RefreshableSession` takes for STS, [check this documentation](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/boto3_refresh_session/methods/sts.py).

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

</details>

<details>
   <summary><strong>Custom Authentication Flows (click to expand)</strong></summary>

  ### Custom

  If you have a highly sophisticated, novel, or idiosyncratic authentication flow not included in boto3-refresh-session then you will need to provide your own custom temporary credentials callable object. `RefreshableSession` accepts custom credentials callable objects, as shown below. For additional information on the exact parameters that `RefreshableSession` takes for custom authentication flows, [check this documentation](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/boto3_refresh_session/methods/custom.py).

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

</details>