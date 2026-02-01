# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IoT Core credential provider refreshable session methods. Requires the
installation of the 'iot' extra."""

__all__ = []

import importlib.util

# checking if iot extra is installed
if (
    importlib.util.find_spec("awscrt") is not None
    and importlib.util.find_spec("awsiot") is not None
):
    from . import core
    from .core import IoTRefreshableSession
    from .x509 import IOTX509RefreshableSession

    __all__ += core.__all__
