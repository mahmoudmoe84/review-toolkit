# DESIGN — ledger

## 1. Purpose

An append-only ledger written by several threads at once and read by a consumer
that needs to wait until a known number of entries have landed.

## 2. Layers

One module, `ledger/repo.py`. There is no layering to violate — this project
exists to exercise the concurrency contract in §3, nothing else.

## 3. Concurrency contract

`Repo.save()` may be called from any thread.

Every entry is stamped with a **unique, gap-free sequence number**. Stamping
deliberately spans the durable write: the number is reserved, the record is
persisted under it, and only then is the counter advanced — so an interrupted
process can never leave the same number recorded twice. Because that span
covers an I/O call, two unsynchronised writers can both reserve the same
number, and one entry is then silently lost. `save()` therefore holds the
repo's lock for the whole span; this is the guarantee the lock exists to
provide.

`Repo.wait_for_at_least(n)` blocks the calling thread until the ledger holds at
least `n` entries, then returns them. The condition variable is the mechanism:
every `save()` must signal waiters after appending. A writer that appends
without signalling leaves every waiting reader blocked with no way to notice.

`Repo.waiting_count()` reports how many threads are currently parked in
`wait_for_at_least()`.

## 4. Storage

Entries are appended to a line-buffered log file at the path given to the
constructor, and mirrored in memory copy-on-write so a reader can return the
list it holds without copying. Reading the log back at startup is out of scope.
