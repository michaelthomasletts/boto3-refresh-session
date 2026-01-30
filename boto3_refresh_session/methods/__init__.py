# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = []

import importlib.util

from . import custom, sts
from .custom import *
from .sts import *

__all__.extend(custom.__all__)
__all__.extend(sts.__all__)

# checking if iot extra is installed
if (
    importlib.util.find_spec("awscrt") is not None
    and importlib.util.find_spec("awsiot") is not None
):
    from . import iot
    from .iot import *

    __all__.extend(iot.__all__)
