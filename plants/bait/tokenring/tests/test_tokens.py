import importlib
import sys

import pytest

from tokenring.tokens import issue, verify


def test_a_fresh_token_returns_its_user_id():
    assert verify(issue("alice", now=1000), now=1010) == "alice"


def test_an_expired_token_is_refused():
    assert verify(issue("alice", now=1000), now=1000 + 900) is None


def test_a_tampered_signature_is_refused():
    token = issue("alice", now=1000)
    flipped = token[:-1] + ("0" if token[-1] != "0" else "1")
    assert verify(flipped, now=1010) is None


def test_a_malformed_token_is_refused_rather_than_raising():
    for junk in ["", "garbage", "no-dot", "a.b", "...", "\x00", "." * 5000]:
        assert verify(junk, now=1010) is None


def test_a_colon_in_the_user_id_is_rejected_at_issue():
    with pytest.raises(ValueError):
        issue("alice:9999999999")


def test_the_module_refuses_to_load_without_a_signing_key(monkeypatch):
    """The import-time guard. Goes red if the `if not _KEY` check is removed.

    The `issue`/`verify` above are already bound, so dropping the module from
    the cache cannot affect the other tests.
    """
    monkeypatch.delenv("TOKENRING_SIGNING_KEY", raising=False)
    monkeypatch.delitem(sys.modules, "tokenring.tokens", raising=False)
    with pytest.raises(RuntimeError, match="TOKENRING_SIGNING_KEY is not set"):
        importlib.import_module("tokenring.tokens")
