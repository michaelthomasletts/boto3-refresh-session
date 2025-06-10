.. _raison:

Raison d'Être
-------------

Long-running data pipelines, security tooling, ETL jobs, and cloud automation scripts frequently interact with the AWS API via ``boto3`` — and often run into the same problem:

**Temporary credentials expire.**

When that happens, engineers typically fall back on one of two strategies:

- Wrapping AWS calls in ``try/except`` blocks that catch ``ClientError`` exceptions
- Writing ad hoc logic to refresh credentials using ``botocore.credentials`` internals

Both approaches are fragile, tedious to maintain, and error-prone at scale.

Over the years, I noticed that every company I worked for — whether a scrappy startup or FAANG — ended up with some variation of the same pattern:  
a small in-house module to manage credential refresh, written in haste, duplicated across services, and riddled with edge cases. Things only 
got more strange and difficult when I needed to run things in parallel.

Eventually, I decided to build ``boto3-refresh-session`` as a proper open-source Python package:  

- Fully tested  
- Extensible  
- Integrated with ``boto3`` idioms  
- Equipped with automatic documentation and CI tooling  

**The goal:** to solve a real, recurring problem once — cleanly, consistently, and for everyone -- with multiple refresh strategies.

If you've ever written the same AWS credential-refresh boilerplate more than once, this library is for you. 
