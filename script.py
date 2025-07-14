#!/usr/bin/env python3

from pprint import pprint

from boto3_refresh_session.session import RefreshableSession

if __name__ == "__main__":
    session = RefreshableSession(
        method="iot", authentication_method="certificate"
    )
    pprint(dir(session))
