# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = []

from ..utils import IOT_EXTRA_INSTALLED
from . import custom, sts
from .custom import *
from .sts import *

__all__ += custom.__all__
__all__ += sts.__all__

# checking if iot extra is installed
if IOT_EXTRA_INSTALLED:
    from . import iot
    from .iot import *

    __all__ += iot.__all__
