# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Utilities for checking the presence of optional dependencies (extras)."""

__all__ = ["IOT_EXTRA_INSTALLED"]

from importlib.util import find_spec
from typing import TYPE_CHECKING

# checking whether 'iot' extra is installed or we're in a type-checking context
IOT_EXTRA_INSTALLED: bool = (
    True
    if TYPE_CHECKING
    else find_spec("awscrt") is not None and find_spec("awsiot") is not None
)
