# DESIGN — ledger

## 1. Purpose

An in-process, append-only ledger shared by several writer threads and read by
one consumer that needs to wait until a known number of entries have landed.

## 2. Layers

One module, `ledger/repo.py`. There is no layering to violate — this project
exists to exercise the concurrency contract in §3, nothing else.

## 3. Concurrency contract

`Repo.save()` may be called from any thread. Appends are serialized by the
repo's lock, so no entry is lost when writers overlap.

`Repo.wait_for_at_least(n)` blocks the calling thread until the ledger holds at
least `n` entries, then returns a snapshot. The condition variable is the
mechanism that makes this work: every `save()` must signal waiters after
appending. A writer that appends without signalling leaves every waiting reader
blocked with no way to notice.

## 4. Storage

In memory only. Persistence is out of scope.
