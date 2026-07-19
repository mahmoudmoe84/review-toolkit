# Plan — Phase 2: Storage simplification

Context docs: docs/DESIGN.md, variants/decisions_p3.md

## Steps
1. Replace `storage/repo.py` SQLite implementation with a flat-JSON store
   (read file -> mutate list -> rewrite file), per decision 6.
2. Keep the `Repo` public surface (`save`, `all_rows`) unchanged.
3. Delete the sqlite3 import and the CREATE TABLE bootstrap.
