import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tenant_notes.api.handlers import list_notes, search_notes  # noqa: E402
from tenant_notes.application.policy import may_read  # noqa: E402
from tenant_notes.storage.db import Db  # noqa: E402


def _db(tmp_path):
    db = Db(str(tmp_path / "notes.sqlite"))
    db.setup()
    db.insert("acme", "alice", "quarterly numbers")
    db.insert("acme", "bob", "bob's private note")
    db.insert("globex", "carol", "another company's note")
    return db


def test_scoped_refuses_to_run_outside_an_identity_context(tmp_path):
    db = _db(tmp_path)
    try:
        raised = False
        try:
            db.scoped("SELECT * FROM notes")
        except PermissionError:
            raised = True
        assert raised, "scoped() ran without an identity context"
    finally:
        db.close()


def test_a_user_lists_only_their_own_notes(tmp_path):
    db = _db(tmp_path)
    try:
        alice = {"id": "alice", "tenant_id": "acme", "role": "member"}
        bodies = [r["body"] for r in list_notes(db, alice)]
        assert bodies == ["quarterly numbers"]
    finally:
        db.close()


def test_search_does_not_cross_the_tenant_boundary(tmp_path):
    db = _db(tmp_path)
    try:
        alice = {"id": "alice", "tenant_id": "acme", "role": "member"}
        bodies = [r["body"] for r in search_notes(db, alice, "note")]
        assert "another company's note" not in bodies
    finally:
        db.close()


def test_a_member_may_not_read_another_members_note():
    alice = {"id": "alice", "tenant_id": "acme", "role": "member"}
    bobs_note = {"tenant_id": "acme", "owner_id": "bob"}
    assert may_read(alice, bobs_note) is False


def test_an_admin_reads_their_own_tenant_but_not_another(tmp_path):
    admin = {"id": "dave", "tenant_id": "acme", "role": "admin"}
    assert may_read(admin, {"tenant_id": "acme", "owner_id": "bob"}) is True
    assert may_read(admin, {"tenant_id": "globex", "owner_id": "carol"}) is False
