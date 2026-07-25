"""Append-only ledger: a durable log plus an in-memory view with a blocking reader."""
import threading


class Repo:
    """Append-only ledger, safe for concurrent writers.

    Each entry is stamped with a sequence number that is unique and gap-free
    **for the lifetime of this process**. Stamping spans the durable write: the
    number is reserved, the record is persisted under it, and only then is the
    counter advanced. That span is why `save()` must hold the lock — two writers
    inside it at once reserve the same number and one of them is silently
    overwritten. The lock is the entire mechanism.

    The stamp is not crash-safe and does not try to be: `_next_seq` is in-memory
    only and the log is never replayed (DESIGN §4), so a restarted process begins
    at 0 and re-issues numbers already on disk.

    The in-memory view is copy-on-write: `save()` rebinds `_entries` instead of
    mutating it, so a reader can return the list it is holding without copying
    and never observe a half-written state.
    """

    def __init__(self, path):
        self._log = open(path, "a", buffering=1)
        self._entries = []
        self._next_seq = 0
        self._waiting = 0
        self._lock = threading.Lock()
        self._changed = threading.Condition(self._lock)

    def save(self, entry):
        """Persist one entry under the next sequence number; wake any waiter.

        Raises ValueError if `entry` holds a tab or a newline: those are the log
        format's delimiters, and writing one forges a record.
        """
        if "\t" in entry or "\n" in entry:
            raise ValueError("entry may not contain a tab or a newline")
        with self._lock:
            seq = self._next_seq
            self._log.write(f"{seq}\t{entry}\n")
            self._next_seq = seq + 1
            self._entries = self._entries + [(seq, entry)]
            self._changed.notify_all()

    def wait_for_at_least(self, n):
        """Block until the ledger holds at least n entries, then return them."""
        with self._changed:
            self._waiting += 1
            try:
                while len(self._entries) < n:
                    self._changed.wait()
                return self._entries
            finally:
                self._waiting -= 1

    def waiting_count(self):
        """How many threads are currently parked in wait_for_at_least()."""
        with self._lock:
            return self._waiting

    def count(self):
        """Current number of entries."""
        with self._lock:
            return len(self._entries)

    def close(self):
        self._log.close()
