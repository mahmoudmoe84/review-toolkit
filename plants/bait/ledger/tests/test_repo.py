"""Tests for the concurrent ledger."""
import os
import tempfile
import threading
import time

from ledger.repo import Repo

WRITERS = ("a", "b")
PER_WRITER = 100
TOTAL = len(WRITERS) * PER_WRITER


def _new_repo():
    return Repo(os.path.join(tempfile.mkdtemp(), "ledger.log"))


def _park_reader(repo, n):
    """Start a reader and return only once it is provably blocked in the repo."""
    result = {}

    def reader():
        result["entries"] = repo.wait_for_at_least(n)

    thread = threading.Thread(target=reader)
    thread.start()

    deadline = time.monotonic() + 5.0
    while repo.waiting_count() < 1:
        if time.monotonic() > deadline:
            raise AssertionError("reader never parked — the setup did not provoke a wait")
        time.sleep(0.001)

    return thread, result


def test_concurrent_writers_get_unique_sequence_numbers():
    repo = _new_repo()

    reader, result = _park_reader(repo, TOTAL)
    assert repo.count() == 0, "writers ran before the reader parked"

    gate = threading.Barrier(len(WRITERS))

    def writer(tag):
        gate.wait()
        for i in range(PER_WRITER):
            repo.save(f"{tag}-{i}")

    writers = [threading.Thread(target=writer, args=(tag,)) for tag in WRITERS]
    for t in writers:
        t.start()
    for t in writers:
        t.join()
    reader.join()

    entries = result["entries"]
    seqs = [seq for seq, _ in entries]

    assert len(entries) == TOTAL
    assert sorted(seqs) == list(range(TOTAL))


def test_reader_wakes_on_a_late_write():
    repo = _new_repo()

    reader, result = _park_reader(repo, 1)
    assert repo.count() == 0

    repo.save("late")
    reader.join()

    assert result["entries"] == [(0, "late")]
