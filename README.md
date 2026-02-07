# boto3-refresh-session

<div align="left">

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

</br>

boto3-refresh-session is a simple Python package with a drop-in replacement for `boto3.Session` named `RefreshableSession`. It automatically refreshes temporary AWS credentials, caches clients, and natively supports MFA providers. It also supports automatic temporary AWS credential refresh for STS, IOT Core, and custom credential callables.

## Features

- A drop-in replacement for [boto3.session.Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) named `RefreshableSession`
- MFA support for STS using custom token callables or CLI commands for token providers
- Optional boto3 client caching
- Automatic temporary credential refresh for STS, IoT Core (X.509), and custom credential callables
- [Thorough testing](https://github.com/michaelthomasletts/boto3-refresh-session/tree/main/tests), [regular updates](https://github.com/michaelthomasletts/boto3-refresh-session/commits/main/), [comprehensive documentation](https://michaelthomasletts.github.io/boto3-refresh-session/index.html), and [publication to PyPI](https://pypi.org/project/boto3-refresh-session/)

## Recognition and Testimonials

[Featured in TL;DR Sec.](https://tldrsec.com/p/tldr-sec-282)

[Featured in CloudSecList.](https://cloudseclist.com/issues/issue-290)

Recognized during AWS Community Day Midwest on June 5th, 2025 (my birthday!).

A testimonial from an engineer at a FAANG company:

> _Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. I often opt to just write this sort of thing myself so I at least know that I can reason about it. But I found boto3-refresh-session to be very clean and intuitive [...] We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions._

## Installation

boto3-refresh-session is available on PyPI.

```bash
# with pip
pip install boto3-refresh-session

# with pip + iot as an extra
pip install boto3-refresh-session[iot]

# installation for contributors
pip install boto3-refresh-session[iot,dev]
```

## Usage

Refer to the [official usage documentation](https://michaelthomasletts.com/boto3-refresh-session/usage.html) for detailed guidance on how to use boto3-refresh-session.

Refer to the [official API documentation](https://michaelthomasletts.com/boto3-refresh-session/api/index.html) for technical information about boto3-refresh-session.

## Versions

Refer to the [changelog](https://michaelthomasletts.com/boto3-refresh-session/changelog.html) for additional information on specific versions and releases.

## License

Beginning v7.0.0, `boto3-refresh-session` is licensed under [Mozilla Public License 2.0 (MPL-2.0)](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/LICENSE). Earlier versions remain licensed under the MIT License.

## Contributing

Refer to the [contributing guidelines](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/CONTRIBUTING.md) for additional information on contributing to boto3-refresh-session.

## Special Thanks

The people listed below inspired features, adopted boto3-refresh-session early, provided critical feedback, and more. Thank you for all of your support, encouragement, and guidance which make this project possible. 

- [Gavin Adams](https://github.com/gadams999)
- [Patrick Sanders](https://github.com/patricksanders)
- [Liam Wadman](https://github.com/liwadman)
- [Ben Kehoe](https://github.com/benkehoe)