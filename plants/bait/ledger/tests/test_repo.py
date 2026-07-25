"""Tests for the concurrent ledger."""
import threading
import time

from ledger.repo import Repo


def test_concurrent_writers_do_not_lose_entries():
    repo = Repo()

    def writer(tag):
        # stagger startup so the reader is already parked in wait_for_at_least
        time.sleep(0.2)
        for i in range(50):
            repo.save(f"{tag}-{i}")

    threads = [threading.Thread(target=writer, args=(tag,)) for tag in ("a", "b")]
    for t in threads:
        t.start()

    entries = repo.wait_for_at_least(100)

    for t in threads:
        t.join()

    assert len(entries) == 100
    assert len(set(entries)) == 100


def test_reader_waits_for_a_late_writer():
    repo = Repo()

    def late_writer():
        time.sleep(0.2)
        repo.save("late")

    threading.Thread(target=late_writer).start()

    entries = repo.wait_for_at_least(1)

    assert entries == ["late"]
