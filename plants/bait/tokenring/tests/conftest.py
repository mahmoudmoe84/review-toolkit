"""Test setup.

DESIGN §S1 forbids a key literal in a test fixture as firmly as in source, so the
suite generates a key per run instead of writing one down. It must be set before
`tokenring.tokens` is imported, because the module reads it at import time and
refuses to start without it — which is the behaviour §S1 describes.
"""

import os
import secrets
import sys

os.environ.setdefault("TOKENRING_SIGNING_KEY", secrets.token_hex(32))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
