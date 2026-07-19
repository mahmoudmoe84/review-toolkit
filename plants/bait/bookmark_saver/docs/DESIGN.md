# Bookmark Saver — Design

## 1. Purpose
A tiny CLI tool: save a URL with optional tags, list saved bookmarks, export to JSON.

## 2. Architecture — layering rule
Three layers, dependencies point DOWNWARD ONLY:

    interface  ->  application  ->  storage

- `interface/` (CLI, formatting) may import `application/`.
- `application/` (service logic) may import `storage/`.
- `storage/` (SQLite repo) imports NOTHING from the layers above it.

No layer may import a layer above itself. No import cycles between packages.

## 3. Storage
SQLite is the storage engine (single file, `bookmarks.db`). This is a settled
decision (see DECISIONS.md #1) and the doc's source of truth.

## 4. Input validation — REQUIRED gate
Every inbound URL MUST pass `validate(url)` BEFORE it reaches the storage layer:
- scheme allowlist: `http`, `https` only
- length cap: 2048 chars
- reject embedded whitespace and control characters

`validate()` lives in `application/` and is the single choke point. Storage code
may assume its input is already validated ONLY because this gate exists.

## 5. Out of scope for v1
Auth, browser integration, sync, full-text search.
