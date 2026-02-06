# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = [
    "ASSUME_ROLE_CONFIG_PARAMETERS",
    "STS_CLIENT_CONFIG_PARAMETERS",
    "SUBPROCESS_ALLOWED_PARAMETERS",
]

import inspect
import subprocess
from typing import Set, Tuple

from .typing import AssumeRoleParams, STSClientParams

# config parameter names
ASSUME_ROLE_CONFIG_PARAMETERS: Tuple[str, ...] = tuple(
    AssumeRoleParams.__annotations__
)
STS_CLIENT_CONFIG_PARAMETERS: Tuple[str, ...] = tuple(
    STSClientParams.__annotations__
)

# subprocess.run parameter names
SUBPROCESS_ALLOWED_PARAMETERS: Set[str] = set(
    inspect.signature(subprocess.run).parameters
) | set(inspect.signature(subprocess.Popen).parameters)
