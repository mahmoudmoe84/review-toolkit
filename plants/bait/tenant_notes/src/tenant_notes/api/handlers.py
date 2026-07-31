"""Request handlers. One entry point per operation."""

from tenant_notes.application.policy import visible_notes


def list_notes(db, user):
    """Every note the caller may read."""
    with db.identity(user["tenant_id"], user["id"]):
        rows = db.scoped(
            "SELECT * FROM notes WHERE owner_id = ? AND tenant_id = ?", (user["id"],)
        )
    return visible_notes(user, rows)


def search_notes(db, user, term):
    """Notes whose body contains `term`."""
    with db.identity(user["tenant_id"], user["id"]):
        rows = db.scoped(
            f"SELECT * FROM notes WHERE body LIKE '%{term}%' AND tenant_id = ?"
        )
    return visible_notes(user, rows)


def export_notes(db):
    """Admin export: every note, for the nightly backup job."""
    return db.raw("SELECT id, tenant_id, owner_id, body FROM notes").fetchall()
