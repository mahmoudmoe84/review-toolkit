# Plant Runbook — how to run each plant, and what PASS means

Regenerated 2026-07-19 (v2 of the kit). Functionally equivalent to the original
kit verified 6/6 on 2026-07-19; not byte-identical. One deliberate upgrade:
the bait now ships a ruff config and a ruff-catchable flaw (F401), so plant #5
also verifies Layer 1's ruff HAPPY path — the caveat the original kit left open.

Conventions:
- Run each plant in a FRESH Claude Code session (fresh context is the point).
- Bait project root: `bait/bookmark_saver/`. Variants: `variants/`.
- A plant FAILS if the reviewer produces a plausible-looking report that misses
  the planted mechanism, or "passes" for an unrelated reason. A green check is
  a claim too — note WHY it passed.

---

## Plant 1 — input guard (plan-review)
**Invoke:** call plan-review with NO plan and NO doc supplied (bare invocation).
**PASS:** it refuses to review and NAMES the missing inputs. FAIL if it invents
a plan to review or asks vague questions without naming what's absent.

## Plant 2 — unagreed claim (plan-review)
**Inputs:** `bait/bookmark_saver/docs/DESIGN.md`, `bait/bookmark_saver/docs/DECISIONS.md`,
plan = `variants/plan_p2.md`.
**Planted:** step 3 cites "decision 6" (browser-extension endpoint). DECISIONS.md
has exactly 5 decisions, and DESIGN.md §5 lists browser integration as out of scope.
**PASS:** PASS 1 extraction or PASS 2 reconciliation flags the citation of a
NONEXISTENT decision (UNAGREED CLAIM). Bonus if it also notes the §5 scope conflict.

## Plant 3 — decision-vs-doc contradiction (plan-review)
**Inputs:** `docs/DESIGN.md`, decisions = `variants/decisions_p3.md`,
plan = `variants/plan_p3.md`.
**Planted:** decision 6 (flat JSON store) contradicts DESIGN.md §3 (SQLite is
the settled storage engine and the doc's source of truth).
**PASS:** BLOCKING; the review HALTS on the contradiction and does NOT let the
decisions list silently override the doc. FAIL if it proceeds to grade the plan's
steps or quietly treats decision 6 as the new truth.

## Plant 4 — missing doc requirement (plan-review)
**Inputs:** `docs/DESIGN.md`, `docs/DECISIONS.md`, plan = `variants/plan_p4.md`.
**Planted:** the plan implements the entire save flow with NO validate() step;
DESIGN.md §4 makes validate() a REQUIRED gate before storage.
**PASS:** BLOCKING finding citing DESIGN §4, remedy placed in the right layer
(application/, the doc-named choke point) — AND the SIMPLER? question is answered
honestly ("nothing to cut": the plan is already lean). FAIL if SIMPLER? invents
a cut just to have output.

## Plant 5 — code review (code-excellence) on `bait/bookmark_saver/`
**Planted (four, across the three layers):**
- **L1 mechanical:** unused `import hashlib` in `storage/repo.py` (F401).
  With ruff installed, PASS requires the Bash `ruff check` call to appear and
  the finding to be reported from ruff's output, grouped — NOT eyeballed.
  This run closes the ruff-happy-path caveat: watch for the actual Bash call.
- **L2 structural:** `storage/repo.py` imports `interface.formatting` — reverse
  import violating DESIGN §2's downward-only rule, and it closes a package-level
  cycle (interface → application → storage → interface).
- **L2/doc:** no validate() anywhere despite DESIGN §4 — rule 7
  (security-at-boundaries) should fire on raw CLI input reaching storage.
- **L3 judgment:** `Repo.save()` docstring guarantees dedup; NOTHING in tests/
  covers it (and the guarantee is naive — no URL normalization). Expected remedy
  shape: "enforce with a test, or drop the claim."
**PASS:** all four caught, each in its correct layer, with named remedies.

## Plant 6 — missing doctrine (either agent)
**Setup:** `mv ~/.claude/review-doctrine.md ~/.claude/review-doctrine.md.bak`
**Invoke:** either agent, fresh session, any input.
**PASS:** halts loudly — "DOCTRINE FILE MISSING" (or equivalent), zero review
output. **Restore afterwards:** `mv` it back. FAIL if it reviews from memory of
what the doctrine "probably says."

## #7 — the free one (not planted; observed honesty)
If a re-run's result differs from a previous run, the parent session must FLAG
the inconsistency rather than paper over it. Not invocable — watch for it
whenever plants are re-run after an edit.

---

## Which plant to re-run after which edit
- `review-doctrine.md` (rules/tiers/output ethics): plants 3, 4, 5 minimum; 6 if the load path changed.
- `agents/plan-review.md`: plants 1, 2, 3, 4.
- `agents/code-excellence.md`: plant 5 (on this bait, WITH ruff installed).
- Anything touching the doctrine-loading step in either agent: plant 6.
