import os
import sys

os.environ.setdefault("TOKENRING_SIGNING_KEY", "test-key-not-a-real-secret")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tokenring.tokens import issue, verify  # noqa: E402


def test_a_fresh_token_verifies():
    assert verify(issue("alice", now=1000), now=1010) is True


def test_an_expired_token_is_refused():
    assert verify(issue("alice", now=1000), now=1000 + 900) is False


def test_a_tampered_signature_is_refused():
    token = issue("alice", now=1000)
    flipped = token[:-1] + ("0" if token[-1] != "0" else "1")
    assert verify(flipped, now=1010) is False


def test_a_malformed_token_is_refused_rather_than_raising():
    for junk in ["", "garbage", "no-dot", "a.b", "...", "\x00"]:
        assert verify(junk, now=1010) is False
