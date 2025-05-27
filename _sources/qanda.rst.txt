.. _qanda:

Q&A
---

Answers to some common questions (and criticisms).

Doesn't boto3 already refresh temporary credentials?
====================================================

**No.**

Botocore has methods for *manually* refreshing temporary credentials.
Those methods are explicitly used in this package. 
However, those methods, as just mentioned, must be applied *manually*.
There is no way of *automatically* refreshing temporary credentials.
This can be frustrating in some situations.
The boto3 developers have consistently decided not to introduce automatically refreshing temporary credentials.
This is a conspicuously odd decision since `in aws-sdk-go-v2 <https://github.com/aws/aws-sdk-go-v2/blob/8e8487a51e9eb22a101c49cc61b98ca8990c1322/aws/credential_cache.go#L57>`_ allows it . . . 
BRS was released to address this shortcoming specifically.

Is this package really necessary?
=================================

As mentioned above, it is possible to refresh temporary credentials *manually*, but not everyone feels like doing that. 
It is far easier to import an actively supported package which addresses that problem.

How are people using BRS?
=========================

Below is a testimonial from a Cyber Security Engineer at a FAANG company who uses BRS:

*"Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code. 
I often opt to just write this sort of thing myself so I at least know that I can reason about it. 
But I found boto3-refresh-session to be very clean and intuitive . . . 
We're using the RefreshableSession class as part of a client cache construct . . . 
We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, over and over again, all day every day. 
And it turns out that there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition json), 
so we can run MUCH more efficiently if we keep a cache of clients, all equipped with automatically refreshing sessions."*

Why aren't many of the parameters for initializing :class:`boto3_refresh_session.session.RefreshableSession` included as attributes?
====================================================================================================================================

Good question.

BRS was developed to be as simple and intuitive as possible. 
Parameters like ``defer_refresh`` and ``assume_role_kwargs``, et al are not part of ``boto3`` so add clutter.
Functionally, those parameters are also only useful when initializing :class:`boto3_refresh_session.session.RefreshableSession`.
Thus, it was decided *not* to include those parameters as attributes.

Can I submit a request to change BRS? I'd like a few things to be different.
============================================================================

It depends.

If you want *additional* features, like a CLI tool, then there is a good chance that your request will be added.

*However*, if your requested changes are *highly idiosyncratic* or *redactive* -- that is, not generalizable to as many use cases as possible -- then it is suggested that you fork BRS, make your changes, and use those locally instead.
The above user testimonial came from a team who lightly edited BRS in order to satisfy certain requirements that they intuitively understood did not apply to all users. 
Do what that team did.
The MIT license for BRS makes changes and forks completely permissible.
BRS has thousands of users.
Breaking changes have massive implications.

Before submitting a request, ask yourself: *does my request behoove all users, or just me . . . ?*
