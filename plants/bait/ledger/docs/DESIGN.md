# DESIGN — ledger

## 1. Purpose

An append-only ledger written by several threads at once and read by a consumer
that needs to wait until a known number of entries have landed.

## 2. Layers

One module, `ledger/repo.py`. There is no layering to violate — this project
exists to exercise the concurrency contract in §3, nothing else.

## 3. Concurrency contract

`Repo.save()` may be called from any thread.

Every entry is stamped with a sequence number that is **unique and gap-free
within one process run**. Stamping spans the durable write: the number is
reserved, the record is persisted under it, and only then is the counter
advanced. Because that span covers an I/O call, two unsynchronised writers can
both reserve the same number, and one entry is then silently lost. `save()`
therefore holds the repo's lock for the whole span; the lock is the whole of
the mechanism, and uniqueness is exactly as strong as it.

The guarantee stops at the process boundary, and nothing here extends it.
`_next_seq` lives only in memory and §4 puts log replay out of scope, so a
restarted process begins again at 0 and re-issues numbers already on disk. The
reserve→write→advance ordering is **not** crash safety and buys nothing across
a restart; it exists only to put the I/O inside the critical section, which is
what makes the lock's absence detectable.

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

One record is one line, `<seq>\t<entry>`. The entry text may therefore not
contain a tab or a newline: a newline forges a record boundary and a tab
corrupts the field split. `save()` **rejects** such entries with `ValueError`
instead of writing them — replay being out of scope defers when the corruption
would be read, not whether it reaches the disk.

Both storage claims above are enforced by tests, not asserted here: one reads
the log file back and compares it byte for byte, one holds a returned list
across a later `save()` and requires it to be unchanged.
