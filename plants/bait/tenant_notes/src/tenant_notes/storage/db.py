"""The database and the identity context that scopes it (DESIGN §S1)."""

import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id        INTEGER PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    owner_id  TEXT NOT NULL,
    body      TEXT NOT NULL
)
"""


class Db:
    """Every read of `notes` goes through `scoped()`, inside an `identity()` block.

    `scoped()` is the only method that appends the tenant predicate, and it
    refuses to run without an identity — so a query that forgets the context
    fails loudly instead of returning every tenant's rows.
    """

    def __init__(self, path):
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._identity = None

    @contextmanager
    def identity(self, tenant_id, user_id):
        previous = self._identity
        self._identity = (tenant_id, user_id)
        try:
            yield
        finally:
            self._identity = previous

    def scoped(self, sql, params=()):
        if self._identity is None:
            raise PermissionError("scoped() called outside an identity context")
        tenant_id, _ = self._identity
        if "tenant_id = ?" not in sql:
            raise ValueError("scoped() requires an explicit `tenant_id = ?` predicate")
        return self._conn.execute(sql, (*params, tenant_id)).fetchall()

    def raw(self, sql):
        """Schema setup only — bypasses the identity context by construction."""
        return self._conn.execute(sql)

    def setup(self):
        self.raw(SCHEMA)
        self._conn.commit()

    def insert(self, tenant_id, owner_id, body):
        self._conn.execute(
            "INSERT INTO notes (tenant_id, owner_id, body) VALUES (?, ?, ?)",
            (tenant_id, owner_id, body),
        )
        self._conn.commit()

    def close(self):
        self._conn.close()
