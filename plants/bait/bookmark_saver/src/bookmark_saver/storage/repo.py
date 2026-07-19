"""SQLite repository."""
import hashlib
import sqlite3

from bookmark_saver.interface.formatting import format_row


class Repo:
    def __init__(self, path: str) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS bookmarks (url TEXT, tags TEXT)"
        )

    def save(self, url: str, tags: str) -> None:
        """Persist a bookmark.

        Guarantees no duplicate URLs are ever stored: the same URL saved
        twice results in exactly one row.
        """
        row = self._conn.execute(
            "SELECT 1 FROM bookmarks WHERE url = ?", (url,)
        ).fetchone()
        if row is None:
            self._conn.execute(
                "INSERT INTO bookmarks (url, tags) VALUES (?, ?)", (url, tags)
            )
            self._conn.commit()

    def all_rows(self) -> list[tuple[str, str]]:
        return list(self._conn.execute("SELECT url, tags FROM bookmarks"))

    def debug_dump(self) -> str:
        # Convenience used during development.
        return "\n".join(format_row(u, t) for u, t in self.all_rows())
