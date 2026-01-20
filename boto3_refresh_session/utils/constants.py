# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["ASSUME_ROLE_CONFIG_PARAMETERS", "STS_CLIENT_CONFIG_PARAMETERS"]

from re import compile

# THESE CONSTANTS WILL BE DEPRECATED IN A FUTURE RELEASE!!
ROLE_ARN_PATTERN = compile(r"^arn:aws[a-z-]*:iam::\d{12}:role/[\w+=,.@-]+$")
MFA_SERIAL_PATTERN = compile(r"^arn:aws[a-z-]*:iam::\d{12}:mfa/[\w+=,.@-]+$")
ROLE_SESSION_NAME_PATTERN = compile(r"^[a-zA-Z0-9+=,.@-]{2,64}$")

# config parameter names
ASSUME_ROLE_CONFIG_PARAMETERS = (
    "RoleArn",
    "RoleSessionName",
    "PolicyArns",
    "Policy",
    "DurationSeconds",
    "ExternalId",
    "SerialNumber",
    "TokenCode",
    "Tags",
    "TransitiveTagKeys",
    "SourceIdentity",
    "ProvidedContexts",
)
STS_CLIENT_CONFIG_PARAMETERS = (
    "service_name",
    "region_name",
    "api_version",
    "use_ssl",
    "verify",
    "endpoint_url",
    "aws_access_key_id",
    "aws_secret_access_key",
    "aws_session_token",
    "config",
    "aws_account_id",
)
