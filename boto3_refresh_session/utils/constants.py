# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["ASSUME_ROLE_CONFIG_PARAMETERS", "STS_CLIENT_CONFIG_PARAMETERS"]

from .typing import AssumeRoleParams, STSClientParams

# config parameter names
ASSUME_ROLE_CONFIG_PARAMETERS = tuple(AssumeRoleParams.__annotations__)
STS_CLIENT_CONFIG_PARAMETERS = tuple(STSClientParams.__annotations__)
