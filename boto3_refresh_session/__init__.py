# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A simple Python package for refreshing the temporary security credentials
in a boto3.session.Session object automatically.
"""

__all__ = []

from . import exceptions, session
from .exceptions import *
from .methods import *
from .session import *
from .utils import cache, config, extras, typing
from .utils.cache import *
from .utils.config import *
from .utils.extras import *
from .utils.typing import *

# controlling star imports
__all__ += cache.__all__
__all__ += config.__all__
__all__ += session.__all__
__all__ += exceptions.__all__
__all__ += typing.__all__
__all__ += extras.__all__

# package metadata
__version__ = "7.3.5"
__title__ = "boto3-refresh-session"
__author__ = "Mike Letts"
__maintainer__ = "Mike Letts"
__license__ = "MPL-2.0"
__email__ = "lettsmt@gmail.com"
