# DESIGN — tokenring

## 1. Purpose

Issues and verifies short-lived opaque session tokens for an internal service.

## 2. Layers

One module, `tokenring/tokens.py`.

## 3. Security spine

### S1 — Secrets live in the environment

The signing key is read from `TOKENRING_SIGNING_KEY` at import time. The process
refuses to start without it. No key, token, or credential appears as a literal in
source or in a test fixture.

### S2 — Verification fails closed

`verify()` returns False unless it can positively establish that the token is
well-formed, correctly signed, and unexpired. A malformed token, a bad signature,
an unparseable timestamp, or any exception raised on the way means **deny**.

### S3 — Comparison of secrets is constant-time

Signature comparison uses `hmac.compare_digest`, never `==`, so a caller cannot
recover a signature one byte at a time from response timing.

## 4. Gates

`make security` runs `bandit -c pyproject.toml -r src/ tests/` and `pip-audit -r requirements.txt`.
`make check` runs `ruff check .` and `pytest -q`. CI runs both on every push
(`.github/workflows/ci.yml`); neither is a target a human has to remember.

bandit scans `tests/` as well as `src/` because §S1 forbids a key literal in a
fixture — a gate that skipped `tests/` would be blind to half the rule it exists
to enforce. The dependency pin lives in `requirements.txt` alone, and
`pyproject.toml` reads it from there, so what `pip-audit` audits is what
`pip install .` installs.

## 5. Out of scope

Token revocation, key rotation, and storage of issued tokens. The health check
in §1 is a liveness probe only — it carries no token and no user data.
