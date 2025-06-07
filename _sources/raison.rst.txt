.. _raison:

Raison d'Être
-------------

It is common for data pipelines and workflows that interact with the AWS API via 
``boto3`` to run for a long time and, accordingly, for temporary credentials to 
expire. 

Usually, engineers deal with that problem one of two ways: 

- ``try except`` blocks that catch ``ClientError`` exceptions
- A similar approach as that used in this project -- that is, using methods available 
  within ``botocore`` for refreshing temporary credentials automatically. 
  
Speaking personally, variations of the code found in this package exists in code bases at 
nearly every company where I have worked. Sometimes, I turned that code into a module; 
other times, I wrote it from scratch. Clearly, that is inefficient.

I decided to finally turn that code into a proper Python package with unit testing, 
automatic documentation, and quality checks; the idea being that, henceforth, depending 
on my employer's open source policy, I may simply import this package instead of 
reproducing this code for the Nth time.

If any of that sounds relatable, then ``boto3-refresh-session`` should help you.