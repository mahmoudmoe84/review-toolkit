"""In-memory append-only ledger with a blocking reader."""
import threading


class Repo:
    """Append-only ledger, safe for concurrent writers."""

    def __init__(self):
        self._entries = []
        self._lock = threading.Lock()
        self._changed = threading.Condition(self._lock)

    def save(self, entry):
        """Append one entry and wake any reader waiting on a count."""
        with self._lock:
            self._entries.append(entry)
            self._changed.notify_all()

    def wait_for_at_least(self, n):
        """Block until the ledger holds at least n entries, then snapshot it."""
        with self._changed:
            while len(self._entries) < n:
                self._changed.wait()
            return list(self._entries)

    def count(self):
        """Current number of entries."""
        with self._lock:
            return len(self._entries)
