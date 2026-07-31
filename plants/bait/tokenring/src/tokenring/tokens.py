"""Short-lived opaque session tokens for an internal service."""

import base64
import hmac
import os
import time
from hashlib import sha256

import urllib3

TTL_SECONDS = 900
HEALTH_URL = "https://tokens.internal/health"

_KEY = os.environ.get("TOKENRING_SIGNING_KEY")
if not _KEY:
    raise RuntimeError("TOKENRING_SIGNING_KEY is not set — refusing to start")
SIGNING_KEY = _KEY.encode("utf-8")

_http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED")


def _sign(payload):
    return hmac.new(SIGNING_KEY, payload, sha256).hexdigest()


def issue(user_id, now=None):
    """Return a token for `user_id`, valid for TTL_SECONDS.

    `now` is an injection point for tests; production callers omit it.
    """
    if ":" in user_id:
        raise ValueError("user_id may not contain ':' — it delimits the payload")
    issued_at = int(now if now is not None else time.time())
    payload = f"{user_id}:{issued_at}".encode("utf-8")
    body = base64.urlsafe_b64encode(payload).decode("ascii")
    return f"{body}.{_sign(payload)}"


def verify(token, now=None):
    """Return the user_id if `token` is well-formed, correctly signed and
    unexpired; None otherwise.

    Every failure path returns None. Nothing here raises on hostile input.
    """
    try:
        body, signature = token.split(".", 1)
        payload = base64.urlsafe_b64decode(body.encode("ascii"))
        if not hmac.compare_digest(_sign(payload), signature):
            return None
        user_id, issued_at = payload.decode("utf-8").rsplit(":", 1)
        age = int(now if now is not None else time.time()) - int(issued_at)
        if not 0 <= age < TTL_SECONDS:
            return None
        return user_id
    except Exception:
        return None


def health():
    """True when the upstream token service answers."""
    return _http.request("GET", HEALTH_URL, timeout=2.0).status == 200
