__all__ = [
    "ROLE_ARN_PATTERN",
    "MFA_SERIAL_PATTERN",
    "ROLE_SESSION_NAME_PATTERN",
]

from re import compile

# AWS ARN validation patterns
ROLE_ARN_PATTERN = compile(r"^arn:aws[a-z-]*:iam::\d{12}:role/[\w+=,.@-]+$")
MFA_SERIAL_PATTERN = compile(r"^arn:aws[a-z-]*:iam::\d{12}:mfa/[\w+=,.@-]+$")
ROLE_SESSION_NAME_PATTERN = compile(r"^[a-zA-Z0-9+=,.@-]{2,64}$")
