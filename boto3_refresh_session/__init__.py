# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = []

import importlib.util

from . import exceptions, session
from .exceptions import *
from .methods.custom import *
from .methods.sts import *
from .session import *
from .utils import cache, config
from .utils.cache import *
from .utils.config import *

# checking if iot extra is installed
if (
    importlib.util.find_spec("awscrt") is not None
    and importlib.util.find_spec("awsiot") is not None
):
    from .methods.iot import *

__all__.extend(cache.__all__)
__all__.extend(config.__all__)
__all__.extend(session.__all__)
__all__.extend(exceptions.__all__)
__version__ = "7.2.8"
__title__ = "boto3-refresh-session"
__author__ = "Mike Letts"
__maintainer__ = "Mike Letts"
__license__ = "MPL-2.0"
__email__ = "lettsmt@gmail.com"
