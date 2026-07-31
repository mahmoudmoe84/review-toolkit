"""Test setup.

The signing key is generated per run rather than written down, and set before
`tokenring.tokens` is imported — the module reads it at import time and refuses
to start without it.
"""

import os
import secrets
import sys

os.environ["TOKENRING_SIGNING_KEY"] = secrets.token_hex(32)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
