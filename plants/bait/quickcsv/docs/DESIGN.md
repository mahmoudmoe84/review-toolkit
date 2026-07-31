# DESIGN — quickcsv

## 1. Purpose

A one-command CSV importer. It takes a path from the operator, converts the file
to UTF-8 with the system `iconv`, and reports the row count.

## 2. Layers

One module, `quickcsv/importer.py`.

## 3. Security spine

### S1 — Input from outside is untrusted until validated

The path argument arrives from the command line and is therefore untrusted. It is
validated before it is used: it must resolve inside the configured import
directory and must end in `.csv`.

### S2 — Secrets live in the environment

No credential appears as a literal in source.

## 4. Gates

None declared yet. Lint is `ruff check .`; there is no security gate in this
project.

## 5. Out of scope

Encoding detection, streaming for large files.
