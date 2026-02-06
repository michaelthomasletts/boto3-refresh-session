# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""IoT Core credential provider refreshable session methods. Requires the
installation of the 'iot' extra."""

__all__ = []

from ...utils import IOT_EXTRA_INSTALLED

# checking if iot extra is installed
if IOT_EXTRA_INSTALLED:
    from . import x509
    from .x509 import IOTX509RefreshableSession

    __all__ += x509.__all__
