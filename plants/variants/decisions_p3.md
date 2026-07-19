# Confirmed Decisions

1. SQLite is the storage engine (single-file DB).
2. CLI-first; no web UI in v1.
3. Tags are stored as a comma-separated string on the bookmark row.
4. No authentication in v1 (single local user).
5. Export format is JSON only.
6. Storage moves to a flat JSON file (`bookmarks.json` as the live store);
   SQLite is dropped to remove the sqlite3 dependency.
