# Security policy

## `plants/bait/` contains planted vulnerabilities on purpose

**Do not fix them. Do not report them. They are the test suite.**

This repository ships prompt-based reviewers (`agents/`) and a planted-flaw suite
that checks whether those reviewers catch what they claim. A planted flaw is how a
review agent is tested, the same way a deliberately failing assertion is how a test
runner is tested. Every file under `plants/bait/` is a **fixture**, not a product:
it is deployed nowhere, imported by nothing outside its own plant, and exists to be
found.

What is planted there, by category — **all five baits**, not only the ones a
scanner sees. (Extended 2026-08-01: this table listed only the three security
baits' scanner-visible flaws, while the do-not-fix rule above has always covered
every file under `plants/bait/` — a contributor tidying `bookmark_saver` or
`ledger` would have broken a plant with this policy on their side.)

| Category | Where | Which plant tests it |
|---|---|---|
| Hardcoded credential — a Stripe-shaped literal that authenticates nothing | `plants/bait/tenant_notes/src/tenant_notes/config.py:8` | Plant 10a |
| SQL injection — f-string interpolation into a query | `plants/bait/tenant_notes/src/tenant_notes/api/handlers.py:19` | Plant 10b |
| Broken authorization — a query path that bypasses the identity context | `plants/bait/tenant_notes/src/tenant_notes/api/handlers.py:24-26` | Plant 10c |
| Fail-open authorization — a policy predicate returning `True` in its `except` branch | `plants/bait/tenant_notes/src/tenant_notes/application/policy.py:13-15` | Plant 10d |
| Command injection — `shell=True` on an f-string holding an untrusted path | `plants/bait/quickcsv/src/quickcsv/importer.py:13-17` | Plant 11 |
| Path containment that is a no-op — `os.path.join` with an absolute path escapes the import directory | `plants/bait/quickcsv/src/quickcsv/importer.py:27` | Plant 11 |
| Missing input validation at an entry point | `plants/bait/tokenring/src/tokenring/tokens.py:31` | Plant 12 — the *defect* is kept open under the stop rule (logged); the plant itself reads PASS on its v4 criterion |
| A knowingly vulnerable pinned dependency (`urllib3==2.0.6`) | `plants/bait/tokenring/requirements.txt` | Plant 12, Layer 1 |
| Unused import — the linter-happy-path bait (ruff F401) | `plants/bait/bookmark_saver/src/bookmark_saver/storage/repo.py:2` | Plant 5a |
| Reverse import — storage reaching upward into interface | `plants/bait/bookmark_saver/src/bookmark_saver/storage/repo.py:5` | Plant 5b |
| Missing validation gate — the design doc requires it and `src/` contains none; **the absence is the plant** | `plants/bait/bookmark_saver/src/` (`application/` names itself as the gate's home) | Plants 4 & 5c |
| Docstring guarantee nothing enforces — "no duplicate URLs" with no `UNIQUE` constraint and no red-capable test | `plants/bait/bookmark_saver/src/bookmark_saver/storage/repo.py:16-20` | Plant 5d |
| Concurrency tests whose reddening mutation **hangs** instead of failing — reader joins with no deadline | `plants/bait/ledger/tests/test_repo.py:58,73` | Plant 8 |

The planning-level baits are fixtures under the same rule: `plants/variants/*.md`
carry a fabricated decision citation, a decision-vs-doc contradiction, and a plan
missing its doc-required gate (Plants 2, 3, 4). No scanner will ever flag a
markdown file — the rule covers them anyway.

Each one has a **known answer and logged runs** in
[VERIFICATION.md](VERIFICATION.md#results-log). Patching one silently un-verifies
the plant that tests it — which is why this repo has a
[bait stop rule](VERIFICATION.md#bait-maintenance--the-stop-rule): a bait defect is
patched **only** when it breaks a required property of a plant, and everything else
is logged in the open list and left alone.

**A pull request that "fixes" a bait will be closed.** If you believe a planted flaw
is in the wrong place, or that a bait no longer supports its plant's criterion, open
an issue citing the plant and the property you think it breaks — that is a
verification argument, and it is welcome.

## Your scanner will alert on this repository, and so will your fork's

Secret scanning, SAST, and dependency scanners all fire on `plants/bait/`, because
the flaws are real code written to look exactly like the mistakes they imitate. That
is the fixture working. Expect, at minimum:

- **secret scanning** on the Stripe-shaped literal in `tenant_notes/config.py`
- **SAST** (bandit, CodeQL, Semgrep) on the SQL injection and the `shell=True` call
- **dependency scanning** on the pinned `urllib3` advisories in `tokenring/`

This repo carries a **standing GitHub push-protection allowance** for the
`config.py:8` literal, submitted with the reason *"it's used in tests."* **A fork
does not inherit it** — your first push touching that file will be blocked, and you
will need to allow it in your own repository, or exclude `plants/bait/` from
scanning. Suppressing by path is the cleaner option if your organization treats
allowances as exceptions to be justified.

None of these alerts indicates an exposure. Nothing in `plants/bait/` is deployed,
nothing there holds a real credential, and no package is published from this
repository.

## Reporting a real vulnerability

The parts of this repository that could actually carry one are `agents/`,
`review-doctrine.md`, and the documentation — prompts and text, with no runtime and
no network surface. If you find something there that would cause harm to someone who
installed these agents (a prompt that could be steered into exfiltrating a file, an
instruction that would have an agent run a mutating command it claims not to run),
report it privately through GitHub's **"Report a vulnerability"** on the Security
tab rather than in a public issue.

Please state clearly whether your report concerns `agents/`/doctrine or
`plants/bait/`. Reports about planted bait flaws will be closed with a pointer to
this file.
