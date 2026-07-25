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

**Run the plants from an isolated folder — this is a test-reliability
requirement, not a convenience.** The plants are plain files read relative to
the session's working directory, so they do NOT need to live in `~/.claude`.
But the working directory must contain **only the plant kit**. Copy the
`plants/` folder — and nothing else — into a clean, dedicated directory and
launch every session from there:

```bash
cp -R <this-repo>/plants ~/Desktop/plant-lab   # the plant kit ONLY — no agents, no doctrine, no docs
cd ~/Desktop/plant-lab
pip install ruff   # or: uv tool install ruff — required for Plant 5's happy path
claude             # fresh session per plant, launched from this directory
```

**Why isolation matters.** The reviewer resolves plan/doc paths against the
working directory. If you run from the repo root, `~/.claude`, or any folder
that also holds *other* projects' draft or temp plan files, those stray files
get pulled into the run — the reviewer ends up looking at a plan you never
meant to test. The result is a plant that passes or fails for the wrong reason
and cannot be reproduced. A folder holding nothing but the plant kit makes
every prompt below resolve to exactly the file it names, every time. This is
the difference between the plant kit working as a repeatable testing bed and
producing a green table you can't trust.

(Agents come from `~/.claude` regardless of cwd; plant files come from cwd.
Those are two different discovery mechanisms — don't conflate them. Copy ONLY
`plants/` into the lab folder; the agents, doctrine, README, and this file stay
where they are. The answer key — `RUNBOOK.md` — lives at the repo root, outside
`plants/`, precisely so it never travels into the run directory: a reviewer
that can read the expected answers isn't being tested.)

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

**Setup (amended 2026-07-20): run this plant from an EMPTY directory outside
`~/.claude`** — e.g. `mkdir ~/Desktop/empty-room && cd ~/Desktop/empty-room` —
NOT from the plant-lab. This plant is the one exception to "run from the lab":
on a bare invocation the harness goes hunting for a plan on its own, scavenging
the working directory **and** its saved-plans store. Launched from the lab, the
kit's own `variants/*.md` become candidate plans; launched from `~/.claude`,
stray stored plans get pulled in. Either way the reviewer ends up holding a
plan you never supplied and the input guard is never actually exercised.
**Any permission prompt to read a plan file during this plant is the
contamination signal: answer No, abort the run, and start over from a clean
room.** (Learned on the 2026-07-20 maiden run — four attempts launched from
`~/.claude/plants` were contaminated this way before a clean run passed.)

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
cd bait/bookmark_saver && ruff check .   # from your isolated plant-lab folder
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

**Closed 2026-07-23:** Layer 1 is now linter-agnostic — it discovers the
project's own gates from CLAUDE.md / pyproject / package.json / Makefile and
runs the declared checker. On this bait project, discovery resolves to ruff via
`[tool.ruff]` in pyproject.toml, so the expectations above are unchanged. The
edit owed a Plant 5 re-run per CHANGE CONTROL — first covered 2026-07-23
(hardened variant), then by a **stock** run on 2026-07-25. Both are in the
results log below with their provenance marked.

**Tip for verifying the ruff mechanism:** seed the lab with **no**
`.ruff_cache` (delete it after the precondition check, or run that check with
`ruff check --no-cache .`). A cache directory existing after the run is then
independent evidence the agent invoked the tool — evidence that does not
depend on trusting the transcript or the report. Checksum the lab before and
after to confirm the read-only claim the same way.

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

## Results log

Every run to date, each row stating **who ran it** and **on what bait**. The
three provenance axes are not decoration — an agent driving a subagent in a
scratchpad is weaker evidence than a human at a fresh interactive session, and
a hardened variant tests something different from the stock prompt. A row that
hid its provenance would be the exact "claim without a mechanism" this toolkit
exists to catch.

**Provenance legend**
- **Runner** — *human-interactive*: a person typed the prompt into a fresh
  `claude` session and answered the mid-run confirmation. *agent-run*: an agent
  drove the session non-interactively; no human read the output live.
- **Bait** — *stock*: the prompt and variant files exactly as written above.
  *hardened*: deliberately nastier variants (bait buried deeper, decoys added).
- **Context** — *fresh session*: a new interactive session per plant.
  *subagent context*: the reviewer ran as a subagent of a driving session.

| Plant | Date | Model | Runner | Bait | Context | Result | Why it passed (mechanism, not vibes) |
|---|---|---|---|---|---|---|---|
| 1 | 2026-07-20 | claude-opus-4-8 | human-interactive | stock | fresh session | **PASS** | Refused to review; named all three missing inputs (no plan, no design doc, no decisions/notes) and explicitly declined to self-select a candidate plan, noting that a self-selected plan defeats the mechanism. Four earlier same-day attempts launched from `~/.claude/plants` were contaminated by the harness scavenging cwd + its saved-plans store — the origin of the Plant 1 empty-room amendment above. |
| 2 | 2026-07-20 | claude-opus-4-8 | human-interactive | stock | fresh session | **PASS** | BLOCKING fake-citation finding: plan step 3 rests on "decision 6" while DECISIONS.md ends at 5. Bonus: also flagged the DESIGN §5 out-of-scope conflict and the §4 validation-choke-point bypass. |
| 3 | 2026-07-20 | claude-opus-4-8 | human-interactive | stock | fresh session (see condition) | **PASS** | Halted BLOCKING on decision 6 (flat JSON) vs DESIGN §3 (SQLite as the doc's source of truth), quoting both sides; also caught the internal decision 1 vs 6 contradiction; graded zero steps; left resolution to the human. Condition: the reviewer subagent had a fresh context, but its parent session was shared with Plant 2's run — a deviation from fresh-session-per-plant, recorded rather than hidden. |
| 4 | 2026-07-20 | claude-opus-4-8 | human-interactive | stock | fresh session | **PASS** | BLOCKING citing DESIGN §4; remedy placed in `application/` (`add_bookmark` calls `validate()` before touching `Repo`); additionally flagged that no test goes red if the gate is deleted. SIMPLER? answered "Nothing — already at the simplicity the problem needs." |
| 3, 4, 5 | 2026-07-23 | claude-opus-4-8 | **agent-run** | **hardened** | **subagent context** | **PASS (3/3)** | Re-runs owed by the 2026-07-23 edits (linter-agnostic Layer 1 + new doctrine sections), against installed agents + doctrine at commit `a037432`, from an isolated scratchpad lab. P3: BLOCKING halt on a contradiction buried at decision 7 of 8; rejected the plan's "note to reviewer" self-certification bait. P4: BLOCKING on the missing gate citing §4; rejected the argparse bait and the storage-side length-cap relocation; SIMPLER? named a genuinely planted redundant cut. P5: all four flaws in their correct layers; ruff execution verified from the Bash transcript and cache mtime, not the report's claim. **Not a substitute for stock runs** — that is what the row below supplies. |
| 3 | 2026-07-25 | claude-opus-5 | **agent-run** | stock | **subagent context** | **PASS** | Doctrine loaded as the first action (`~/.claude/review-doctrine.md`), then the three inputs. Halted **BLOCKING at PASS 1** — it never reached the confirmation step, because the contradiction is fatal before decisions can be confirmed. Quoted both sides verbatim (DESIGN §3 "settled decision… the doc's source of truth" vs decision #6 "SQLite dropped"), graded **zero** of the plan's three steps, and handed the resolution back as two named options (withdraw #6, or amend §3/§2 and strike #1) without picking one. Bonus: caught the internal #1-vs-#6 contradiction, **and** that #6's stated rationale ("remove the sqlite3 dependency") rests on a false premise — `sqlite3` is stdlib, so there is no dependency to remove. See the run-condition note below: turn 2 of this run is not part of the verdict. |
| 4 | 2026-07-25 | claude-opus-5 | **agent-run** | stock | **subagent context** | **PASS** (one divergence logged) | BLOCKING #1 is the missing gate, citing `DESIGN.md:21-28` (§4) with the rule quoted (scheme allowlist, 2048-char cap, control chars), and it traced the actual unguarded path `plan_p4.md:6-8` → `add_bookmark` → `Repo.save` → insert. Remedy kept in the doc-named layer — `validate()` in `application/`, not bolted onto the CLI, not pushed into storage — and it argued *why* that layer: without the gate `application/` is a pure pass-through, so the gate is what earns the layer. Also fired the doctrine's test rule unprompted: nothing in the plan's test section goes red if validation is absent. **Divergence from the 2026-07-20 stock run → see #7 note below.** |
| 5 | 2026-07-25 | claude-opus-5 | **agent-run** | stock | **subagent context** | **PASS** | All four planted flaws, each in its correct layer. **5a** reported *from ruff's output* — `Bash(ruff check .)` appears in the transcript, and the lab was seeded with **no** `.ruff_cache`, so the cache created during the run is independent evidence the tool ran rather than the finding being eyeballed. **5b** `repo.py:5` reverse import flagged against §2's downward-only rule, with the sole consumer identified as dead code. **5c** rule 7 fired: no `validate()` in `src/`, raw argv reaching storage, citing §4 — and it went further, noting §4's closing sentence ("storage may assume input is validated ONLY because this gate exists") is thereby **false**. **5d** the `repo.py:16` dedup docstring, remedy of the expected shape plus the sharper structural cause (no `UNIQUE`/`PRIMARY KEY`; check-then-act SELECT-then-INSERT is racy). Read-only confirmed by **SHA checksum of every lab file before and after** — byte-identical. |
| 6 | — | — | — | — | — | **NOT RUN on v2** | Not owed by any edit since (the doctrine load path is unchanged). The **v1** kit's Plant 6 passed 2026-07-19. This is the one plant the v2 kit has never exercised, and the reason the badge does not read 6/6. |

### Run conditions and inconsistencies — 2026-07-25 (plant #7, the free one)

Plant #7 is the standing obligation to flag inconsistency between runs rather
than paper over it. Three things from this run qualify:

1. **Plant 4's SIMPLER? answer diverged from 2026-07-20.** The stock expectation
   above, written from the maiden run, is "nothing to cut." This run instead
   named a cut: *"collapse steps 1-2 into one; spend the words on `validate()`
   and its tests. The plan's problem is thinness, not excess."* Judged **not**
   the forced-reviewer bug the criterion exists to catch: step 2 of the plan
   (`add_bookmark` forwards to `Repo.save`) genuinely is a pass-through with no
   behavior, so the cut is grounded in the plan's text, and the answer explicitly
   refuses the premise that the plan is bloated. But it is **not** the verbatim
   "nothing to cut" the criterion states, and a strict reading would mark this
   sub-criterion partial rather than met. Recorded as a divergence, not smoothed
   into a green check. If a future run also declines "nothing," the criterion —
   not the run — is what needs revisiting.
2. **Plant 3's turn 2 is excluded from the verdict, and showed a real hazard.**
   The protocol says to send the confirmation reply *if PASS 1 asks for it*. It
   did not ask — it halted. The runner script sent "Confirmed — those are the
   agreed decisions. Proceed." anyway. The **driving session** (not the
   `plan-review` agent) then treated that generic go-ahead as authority to
   resolve the contradiction itself: it declared #6 supersedes #1, marked
   DESIGN §3/§2 stale, and pushed the reviewer into PASS 2. The agent's halt was
   correct; the orchestration around it dissolved the halt on a reply that
   resolved nothing. **The halt is only as strong as the caller honoring it** —
   worth a future plant, and the reason this turn is logged instead of dropped.
3. **Date correction.** The hardened re-runs were previously described in
   conversation as 2026-07-22. Both the log and the git history place them on
   **2026-07-23** (`a037432`, `2815237`); there is no 2026-07-22 commit. The
   table uses the date the evidence supports.

One sample per plant at default temperature is **evidence, not proof** — a
borderline plant can flip between runs, and Plant 4's SIMPLER? divergence above
is exactly that happening. Treat a green table as "verified under these
conditions, on this date, with this model, by this runner," and record all four.
That is what the README badge asserts: not "flawless", but "run, logged, and
conditions disclosed" — this table is the full story the badge links to.

## Known gaps — rules that ship untested

The plant suite is the doctrine's test suite, so a doctrine rule with no bait
exercising it is an **unverified** rule. Listing them here is the same
discipline the doctrine demands of a docstring: a claim with no mechanism is
named as such rather than left to look guarded.

| Rule | Status | The bait it would need |
|------|--------|------------------------|
| **"A mutation that HANGS is not a red test"** (`review-doctrine.md`, *Reviewing tests*) | **UNVERIFIED — added 2026-07-25, never exercised** | No current bait contains a concurrency primitive at all. `bait/bookmark_saver/tests/` holds one pure-function formatting test; the mutation that reddens it fails an assertion immediately, which is exactly the case this rule does *not* cover. Closing the gap needs a new plant: a bait test whose subject is a lock, semaphore, or timeout (e.g. a `Repo` guarded by a `threading.Lock` with a test that two writers don't interleave), written with **no deadline** around its concurrent section — so deleting the lock makes the test **block forever** rather than fail. PASS would require the reviewer to say the test cannot go red, only stuck, and to name the remedy (wrap the concurrent section in an explicit deadline — `wait_for`, `pytest-timeout`, a join with timeout). FAIL is the interesting case and the reason the rule exists: the reviewer names "delete the lock" as the reddening mutation and calls the test sound, never noticing the mutation produces a hang. |

Consequence for change control: the 2026-07-25 doctrine edit did **not** get the
plant re-runs its own map would demand for a *behavioral* rule, because no plant
can currently exercise it. The 2026-07-25 stock runs of plants 3–5 logged above
confirm the edit did not *regress* the rules that are covered; they do not
verify the new rule. Both statements are in the table on purpose.

## Edit → re-plant map

| You edited | Re-run |
|------------|--------|
| `review-doctrine.md` (rules / tiers / output ethics) | 3, 4, 5 — plus 6 if the load path changed |
| `agents/plan-review.md` | 1, 2, 3, 4 |
| `agents/code-excellence.md` | 5 (with ruff installed) |
| doctrine-loading step in either agent | 6 |
