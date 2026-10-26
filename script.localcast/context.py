"""Entry point for the context menu item "Cast with LocalCast"."""

import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'lib'))

from localcast import actions  # noqa: E402

try:
    actions.cast_listitem()
except Exception as exc:  # pylint: disable=broad-except
    actions.report_error(exc, traceback.format_exc())
