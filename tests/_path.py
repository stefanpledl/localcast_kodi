"""Make ``script.localcast/resources/lib`` importable from the tests."""

import os
import sys

LIB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'script.localcast', 'resources', 'lib')

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
