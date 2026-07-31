# DESIGN — tenant_notes

## 1. Purpose

A multi-tenant notes service. Several companies (tenants) share one database;
each user reads their own notes and, if they are an admin, their tenant's.

## 2. Layers

`api/` (request handling) → `application/` (policy) → `storage/` (the database).
Imports point down only.

## 3. Security spine

This section is the security contract. Code that contradicts a rule here is a
defect in the code, not a difference of opinion.

### S1 — Isolation: every data path opens an identity context

No query touches a note except through `Db.scoped()`, and `Db.scoped()` refuses
to run outside an open `Db.identity(tenant_id, user_id)` block. The context is
what appends the tenant predicate; a query issued outside one has no tenant
filter and returns every company's rows.

`Db.raw()` exists for schema setup at startup and for nothing else. It bypasses
the identity context by construction, so a caller in `api/` or `application/`
using it is a violation of this rule regardless of what the query says.

### S2 — Queries carry values as parameters, never as text

Every value that came from a request is passed to sqlite3 as a bound parameter.
No query string is built by concatenation, `%`, `.format()`, or an f-string with
request data in it. This is absolute: there is no "the input is safe here" case,
because the point of the rule is that no reader has to check.

### S3 — Authority predicates fail closed

`application/policy.py` decides who may read what. Every predicate returns False
unless it can positively establish permission. An unexpected shape, a missing
field, or an exception means **deny** — the predicate must never return True on a
path it did not understand. A gate that opens when confused is worse than no gate,
because the code around it reads as guarded.

### S4 — Secrets live in the environment

No credential, token, or key appears as a literal in source, in a test fixture, or
in a log line. They are read from the environment at startup and the process fails
to start if one is absent.

## 4. Storage

One SQLite file. Three columns matter: `tenant_id`, `owner_id`, `body`.

## 5. Out of scope

Authentication itself (a token is assumed already verified upstream), rate
limiting, and audit logging. Do not review for their absence — they are
deliberately not built yet.
