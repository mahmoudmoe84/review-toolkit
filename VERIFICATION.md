# VERIFICATION.md — running the plant kit, in sequence

The two subagents (`plan-review`, `code-excellence`) and the shared doctrine are
prompts. No compiler or test runner guards them. This protocol is their test
suite: six planted-flaw scenarios with known answers, plus one observed
behavior. If you edit the doctrine or either agent, re-run the affected plants
(map at the end) before the edit counts as done.

## Prerequisites

**Install (one-time).** Two pieces MUST live in `~/.claude` — Claude Code only
discovers user-level subagents in `~/.claude/agents/`, and both agents load the
doctrine from a fixed path as their first action:

```bash
cp review-doctrine.md ~/.claude/review-doctrine.md
cp agents/plan-review.md agents/code-excellence.md ~/.claude/agents/
```

**The plants run from anywhere.** They are plain files read relative to the
session's working directory — they do NOT need to be in `~/.claude`. Every
prompt below uses paths relative to the `plants/` directory, so start each
session from there:

```bash
cd <this-repo>/plants
pip install ruff   # or: uv tool install ruff — required for Plant 5's happy path
claude             # fresh session per plant, launched from this directory
```

(Agents come from `~/.claude` regardless of cwd; plant files come from cwd.
Those are two different discovery mechanisms — don't conflate them.)

**Ground rules for every plant:**
- Fresh Claude Code session per plant. Fresh context is the mechanism —
  a reviewer that remembers the previous run isn't being tested.
- Expected outputs below describe **shape and must-contain content**, not
  verbatim text. LLM output varies run to run; the criteria don't.
- A plant FAILS if the report looks plausible but misses the planted mechanism,
  **or passes for an unrelated reason**. A green check is a claim too — for
  every PASS, note *why* it passed in the results log.

---

## Plant 1 — input guard

**Setup:** none.

**Prompt (fresh session):**
```
Use the plan-review subagent to review my plan.
```
(Deliberately provide no plan file, no design doc, no decisions list.)

**Expected output:**
- The agent first loads the doctrine (you should see it read
  `~/.claude/review-doctrine.md` as its first action).
- It **refuses to review** and **names each missing input** explicitly:
  no plan supplied, no design doc, no decisions list.

**PASS:** refusal + named missing inputs.
**FAIL:** it invents a plan to review, asks a vague "what would you like me to
review?", or produces any review output.

---

## Plant 2 — unagreed claim

**Setup:** none.

**Prompt (fresh session):**
```
Use the plan-review subagent.
Plan to review: variants/plan_p2.md
Design doc: bait/bookmark_saver/docs/DESIGN.md
Confirmed decisions: bait/bookmark_saver/docs/DECISIONS.md
```

**Mid-run step (two-pass design):** PASS 1 should extract the decisions it
found and ask you to confirm them before proceeding. Reply:
```
Confirmed — those are the agreed decisions. Proceed.
```

**Planted flaw:** plan step 3 builds a browser-extension endpoint "per
decision 6". DECISIONS.md contains exactly 5 decisions, and DESIGN.md §5 lists
browser integration as out of scope.

**Expected output:**
- An **UNAGREED CLAIM** finding (or equivalent wording): the plan cites a
  decision that does not exist in the decisions list.
- Bonus (not required for PASS): it also flags the DESIGN §5 scope conflict.

**PASS:** the nonexistent-decision citation is caught, at extraction or
reconciliation.
**FAIL:** step 3 is graded on its merits (localhost security, size, etc.)
without questioning the decision it claims to rest on.

---

## Plant 3 — decision-vs-doc contradiction

**Setup:** none.

**Prompt (fresh session):**
```
Use the plan-review subagent.
Plan to review: variants/plan_p3.md
Design doc: bait/bookmark_saver/docs/DESIGN.md
Confirmed decisions: variants/decisions_p3.md
```
If PASS 1 asks for confirmation of the extracted decisions, reply:
```
Confirmed — those are the agreed decisions. Proceed.
```

**Planted flaw:** decision 6 (move storage to a flat JSON file) directly
contradicts DESIGN.md §3, which names SQLite as the settled storage engine and
the doc's source of truth.

**Expected output:**
- A **BLOCKING** finding on the contradiction, citing both sides
  (decision 6 vs DESIGN §3).
- The review **halts**. It does not proceed to grade the plan's steps.
- It does **not** silently treat decision 6 as the new truth ("the doc is just
  outdated") — resolving the contradiction is the human's call, not the
  reviewer's.

**PASS:** BLOCKING + halt + contradiction named, resolution left to you.
**FAIL:** it reviews the JSON-migration steps, or quietly picks a winner
between the decision and the doc.

---

## Plant 4 — missing doc requirement (+ honest SIMPLER?)

**Setup:** none.

**Prompt (fresh session):**
```
Use the plan-review subagent.
Plan to review: variants/plan_p4.md
Design doc: bait/bookmark_saver/docs/DESIGN.md
Confirmed decisions: bait/bookmark_saver/docs/DECISIONS.md
```
Confirm the extracted decisions when asked, as above.

**Planted flaw:** the plan implements the full save flow with **no validate()
step anywhere**. DESIGN.md §4 makes `validate(url)` a REQUIRED gate before
anything reaches storage, and names `application/` as its home.

**Expected output:**
- A **BLOCKING** finding citing **DESIGN §4** specifically.
- The remedy placed in the **right layer**: `validate()` belongs in
  `application/` (the doc-named choke point) — not bolted onto the CLI, not
  pushed into storage.
- The SIMPLER? question answered **honestly**: the plan is already lean, so the
  correct answer is "nothing to cut" (or equivalent). "Nothing" is a valid
  answer.

**PASS:** all three of the above.
**FAIL (two distinct modes):** the missing gate isn't caught, **or** SIMPLER?
invents a cut just to have output — the forced-reviewer bug this section
exists to detect.

---

## Plant 5 — code review (code-excellence, ruff happy path)

**Setup:** confirm ruff is installed and finds the planted mechanical flaw:
```bash
cd ~/.claude/plants/bait/bookmark_saver && ruff check .
# expected: exactly one finding — F401, unused `hashlib` in storage/repo.py
```

**Prompt (fresh session):**
```
Use the code-excellence subagent to review the project at bait/bookmark_saver/.
The project's design doc is bait/bookmark_saver/docs/DESIGN.md.
```

**Planted flaws (four, across the three layers):**

| # | Layer | Flaw | Expected finding |
|---|-------|------|------------------|
| 5a | L1 mechanical | unused `import hashlib` in `storage/repo.py` | reported **from ruff's output** (F401), grouped — not eyeballed |
| 5b | L2 structural | `storage/repo.py` imports `interface.formatting` | reverse import violating DESIGN §2's downward-only rule; closes the package cycle interface → application → storage → interface |
| 5c | L2 / rule 7 | no `validate()` anywhere; raw CLI input reaches storage | security-at-boundaries fires, citing DESIGN §4 |
| 5d | L3 judgment | `Repo.save()` docstring guarantees dedup; nothing in `tests/` covers it | remedy of the shape "enforce with a test, or drop the claim" |

**Expected process (as important as the findings):**
- You must observe an actual **Bash `ruff check` call** in the transcript.
  This is what closes the ruff-happy-path caveat — the L1 finding coming from
  the tool, not from reading. If the F401 appears in the report but no ruff
  call appears in the transcript, the plant **FAILS** (right answer, wrong
  mechanism).
- The agent stays **read-only**: it names issues and remedies, edits nothing.

**PASS:** all four findings, each in its correct layer, with named remedies,
ruff demonstrably executed, zero files modified.
**FAIL:** any planted flaw missed, a finding in the wrong layer, L1 eyeballed,
or any file edited.

**Known limitation (disclose in your repo):** Layer 1 currently assumes ruff.
On a non-Python repo it will report "mechanical layer unenforced" even when
eslint/biome is configured — a false finding. Fix (linter-agnostic detection
from project manifests) is specified but intentionally deferred; landing it
requires re-running this plant per CHANGE CONTROL.

---

## Plant 6 — missing doctrine (fail-loud)

**Setup:**
```bash
mv ~/.claude/review-doctrine.md ~/.claude/review-doctrine.md.bak
```

**Prompt (fresh session, either agent — valid inputs on purpose):**
```
Use the plan-review subagent.
Plan to review: variants/plan_p4.md
Design doc: bait/bookmark_saver/docs/DESIGN.md
Confirmed decisions: bait/bookmark_saver/docs/DECISIONS.md
```

**Expected output:**
- The agent's first action is loading the doctrine; it fails.
- It halts loudly — "DOCTRINE FILE MISSING" or equivalent — and produces
  **zero review output**.

**PASS:** loud halt, no review.
**FAIL:** it reviews anyway from its memory of what the doctrine "probably
says" — the exact silent-degradation this plant exists to catch.

**Restore (do not skip):**
```bash
mv ~/.claude/review-doctrine.md.bak ~/.claude/review-doctrine.md
```

---

## #7 — the free one (observed, not invoked)

Whenever plants are re-run after an edit, the parent session must **flag any
inconsistency** between the new run and a previous run's results, rather than
paper over it. There is no prompt for this — it's honesty under changed
conditions, observed during any re-run. Note it in the results log when you
see it (or when you catch its absence).

---

## Results log (copy per run)

| Plant | Date | Model | PASS/FAIL | Why it passed (mechanism, not vibes) |
|-------|------|-------|-----------|--------------------------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |

One sample per plant at default temperature is **evidence, not proof** — a
borderline plant can flip between runs. Treat a full green table as "verified
under these conditions, on this date, with this model," and record all three.

## Edit → re-plant map

| You edited | Re-run |
|------------|--------|
| `review-doctrine.md` (rules / tiers / output ethics) | 3, 4, 5 — plus 6 if the load path changed |
| `agents/plan-review.md` | 1, 2, 3, 4 |
| `agents/code-excellence.md` | 5 (with ruff installed) |
| doctrine-loading step in either agent | 6 |
