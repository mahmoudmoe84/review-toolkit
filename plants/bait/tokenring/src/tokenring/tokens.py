"""Short-lived opaque session tokens (DESIGN §S1-S3)."""

import base64
import hmac
import os
import time
from hashlib import sha256

import urllib3

TTL_SECONDS = 900
HEALTH_URL = os.environ.get("TOKENRING_HEALTH_URL", "https://tokens.internal/health")

_http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED")

_KEY = os.environ.get("TOKENRING_SIGNING_KEY")
if not _KEY:
    raise RuntimeError("TOKENRING_SIGNING_KEY is not set — refusing to start")
SIGNING_KEY = _KEY.encode("utf-8")


def _sign(payload):
    return hmac.new(SIGNING_KEY, payload, sha256).hexdigest()


def issue(user_id, now=None):
    """Return a token for `user_id`, valid for TTL_SECONDS."""
    issued_at = int(now if now is not None else time.time())
    payload = f"{user_id}:{issued_at}".encode("utf-8")
    body = base64.urlsafe_b64encode(payload).decode("ascii")
    return f"{body}.{_sign(payload)}"


def verify(token, now=None):
    """True only if `token` is well-formed, correctly signed, and unexpired."""
    try:
        body, signature = token.split(".", 1)
        payload = base64.urlsafe_b64decode(body.encode("ascii"))
        if not hmac.compare_digest(_sign(payload), signature):
            return False
        _, issued_at = payload.decode("utf-8").rsplit(":", 1)
        age = int(now if now is not None else time.time()) - int(issued_at)
        return 0 <= age < TTL_SECONDS
    except Exception:
        return False


def health():
    """True when the upstream token service answers. Certificate verified."""
    return _http.request("GET", HEALTH_URL, timeout=2.0).status == 200
