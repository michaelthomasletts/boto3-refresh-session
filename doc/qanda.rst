.. _qanda:

Q&A
---

Answers to common questions (and criticisms) about boto3-refresh-session.

Doesn't boto3 already refresh temporary credentials?
====================================================

**No.**

Botocore provides methods for *manually* refreshing temporary credentials.  
These methods are used internally by boto3-refresh-session, but must otherwise be applied *explicitly* by developers.

There is **no built-in mechanism** in boto3 for *automatically* refreshing credentials.  
This omission can be problematic in production systems.

The boto3 team has historically declined to support this feature —  
despite its availability in other SDKs like  
`aws-sdk-go-v2 <https://github.com/aws/aws-sdk-go-v2/blob/8e8487a51e9eb22a101c49cc61b98ca8990c1322/aws/credential_cache.go#L57>`_.

boto3-refresh-session was created specifically to address this gap.

Is this package really necessary?
=================================

If you’re willing to manage temporary credentials yourself, maybe not.

But if you’d rather avoid boilerplate and use an actively maintained solution, boto3-refresh-session provides a drop-in interface that does the right thing — automatically.

How are people using boto3-refresh-session?
===========================================

Here’s a testimonial from a cybersecurity engineer at a FAANG company:

*"Most of my work is on tooling related to AWS security, so I'm pretty choosy about boto3 credentials-adjacent code.  
I often opt to just write this sort of thing myself so I at least know that I can reason about it.  
But I found boto3-refresh-session to be very clean and intuitive.  
We're using the `RefreshableSession` class as part of a client cache construct.  
We're using AWS Lambda to perform lots of operations across several regions in hundreds of accounts, all day every day.  
And it turns out there's a surprising amount of overhead to creating boto3 clients (mostly deserializing service definition JSON),  
so we run MUCH more efficiently if we cache clients — all equipped with automatically refreshing sessions."*

Why aren’t most constructor parameters exposed as attributes?
=============================================================

Good question.

boto3-refresh-session aims to be simple and intuitive.  
Parameters like ``defer_refresh`` and ``assume_role_kwargs`` are not part of `boto3`’s interface, and are only useful at initialization.

Rather than surface them as persistent attributes (which adds noise), the decision was made to treat them as ephemeral setup-time inputs.

Can I submit a feature request?
===============================

It depends.

If your request adds a general-purpose feature (e.g. CLI tooling), it’s likely to be considered.

But if your proposal is *highly specific* or *non-generalizable*, you’re encouraged to fork the project and tailor it to your needs.  
boto3-refresh-session is MIT-licensed, and local modifications are fully permitted.

Remember: BRS has thousands of users.  
Changes that break compatibility or narrow scope have wide consequences.

Before submitting a request, ask yourself:

*“Does this benefit everyone — or just me?”*
