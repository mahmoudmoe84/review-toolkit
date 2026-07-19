# Plan — Phase 2: Export & Listing polish

Context docs: docs/DESIGN.md, docs/DECISIONS.md

## Steps
1. Implement `bm export` writing all bookmarks to `bookmarks.json` (per decision 5).
2. Add `--sort` flag to `bm list` (alphabetical by URL).
3. Add the browser-extension handshake endpoint, per decision 6, so the
   extension can POST new bookmarks directly to the local process.
4. Update README with export + sort usage.

## Notes
Step 3 is the largest item; the endpoint listens on localhost only.
