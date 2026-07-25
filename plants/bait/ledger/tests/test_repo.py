"""Tests for the concurrent ledger."""
import os
import tempfile
import threading
import time

from ledger.repo import Repo

WRITERS = ("a", "b")
PER_WRITER = 100
TOTAL = len(WRITERS) * PER_WRITER


def _new_path():
    return os.path.join(tempfile.mkdtemp(), "ledger.log")


def _new_repo():
    return Repo(_new_path())


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

    repo.save("late")
    reader.join()

    assert result["entries"] == [(0, "late")]


def test_log_file_holds_one_line_per_entry():
    """Red if the durable write of DESIGN §4 is dropped — nothing else reads it back."""
    path = _new_path()
    repo = Repo(path)

    repo.save("first")
    repo.save("second")
    repo.close()

    with open(path) as log:
        assert log.read().splitlines() == ["0\tfirst", "1\tsecond"]


def test_a_returned_list_is_not_mutated_by_a_later_save():
    """Red if save() appends in place — §4's copy-on-write claim is what allows
    wait_for_at_least() to hand back its own list uncopied."""
    repo = _new_repo()
    repo.save("first")

    held = repo.wait_for_at_least(1)   # already satisfied: returns without blocking
    repo.save("second")

    assert held == [(0, "first")]


def test_save_rejects_the_log_delimiters():
    """Red if the delimiter guard goes — an entry with a newline forges a record."""
    repo = _new_repo()

    for bad in ("two\tfields", "two\nlines"):
        try:
            repo.save(bad)
        except ValueError:
            continue
        raise AssertionError(f"save() accepted a delimiter: {bad!r}")

    assert repo.count() == 0
