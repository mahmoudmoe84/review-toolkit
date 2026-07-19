# Plan — Phase 1: Save flow

Context docs: docs/DESIGN.md, docs/DECISIONS.md

## Steps
1. `bm add <url> [--tags]` parses args and calls `add_bookmark(url, tags)`.
2. `add_bookmark` forwards to `Repo.save(url, tags)`.
3. `Repo.save` inserts the row into SQLite and commits (per decision 1).
4. `bm list` prints each row via `format_row`.

## Test plan
- One test per CLI command against a temp DB file.
