# review-toolkit

Two Claude Code subagents that review plans and code against *your* project's
documents — plus the test suite that keeps them honest.

- **`plan-review`** — two-pass plan reviewer. Pass 1 extracts the decisions the
  plan claims to rest on and makes you confirm them. Pass 2 reconciles those
  decisions against your design doc, then grills the plan in three tiers. A
  decision that contradicts the doc is a BLOCKING halt — the reviewer never
  silently picks a winner; that call is yours.
- **`code-excellence`** — three-layer code reviewer: mechanical (runs the
  linter — never eyeballs what a tool catches better), structural (your
  project's stated rules: layering, boundaries, security at inputs), and
  judgment (Ousterhout-style depth: does a docstring promise something no test
  enforces?). Read-only: it names issues and remedies, edits nothing.
- **`review-doctrine.md`** — the shared spine both agents load as their first
  action, and halt loudly without. Tier discipline, seven default architecture
  rules, finding-quality ordering, and the rule that "nothing to cut" is a
  valid answer — a reviewer forced to always produce findings is a reviewer
  that invents them.
- **`plants/`** — the test suite. The agents are prompts; no compiler or
  pytest guards a prompt. Six planted-flaw scenarios with known answers are the
  only mechanism that makes "the reviewers work" a checkable claim instead of
  prose. See [VERIFICATION.md](VERIFICATION.md) for the exact run protocol.

## Why subagents, not a skill file

A subagent runs in a **fresh context**. That's not an implementation detail —
it's the core mechanism. This toolkit was distilled from a real project whose
recurring failure was: *the finding doesn't transfer to the finder*. The same
model that writes "every claim needs an enforcing mechanism" ships, in the same
commit, a claim with no mechanism — because knowing ≠ applying, inside one
context. A reviewer with fresh eyes applies the doctrine from outside the head
that produced the work. Same model, different context, different result.

## Origin

Extracted from a production Slack-bot project where every bug of an entire
phase had the same shape: **a claim not backed by a mechanism**. A spec section
cited fourteen times for a rule it never contained. A docstring arguing a
requirement no test guarded. A "verified" feature whose output died at a logger
before any handler — every test green, feature dead in prod. The doctrine's
rules, the tier system, and the plant suite are each a direct answer to a bug
that actually shipped (or nearly did). Nothing here is theoretical.

The plants exist because the toolkit must obey its own rule: "the reviewers
catch real flaws" is a claim, and the planted-flaw suite is its mechanism.
Corollary learned the hard way — **a green check is a claim too**: several
plants specifically verify *why* something passed, not just that it did.

## Install

Two pieces MUST live in `~/.claude` (Claude Code discovers user-level
subagents in `~/.claude/agents/`, and both agents load the doctrine from that
fixed path):

```bash
cp review-doctrine.md ~/.claude/review-doctrine.md
cp agents/plan-review.md agents/code-excellence.md ~/.claude/agents/
```

**The plants stay in this clone.** They're plain files read from the session's
working directory — agents install, plants travel:

```bash
cd plants && pip install ruff && claude   # then follow VERIFICATION.md
```

## Verify before you trust

Run the six plants per [VERIFICATION.md](VERIFICATION.md) — exact prompts, in
sequence, with PASS/FAIL criteria and a results log. One green run at default
temperature is evidence, not proof; record date, model, and *why* each plant
passed.

## Change control

**Editing the doctrine or either agent requires re-running the affected plants
before the edit counts as done.** The edit → re-plant map is at the bottom of
VERIFICATION.md and plants/RUNBOOK.md. An unverified edit silently un-verifies
the whole toolkit — the "verified" label belongs to a version, not a name.

## Known limitations (disclosed on purpose)

- **Layer 1 is currently Python-hardcoded.** code-excellence assumes `ruff`;
  on a repo whose mechanical layer is enforced by eslint/biome/etc., it will
  report "mechanical layer unenforced" — a false finding. The fix
  (linter-agnostic detection from project manifests) is specified and
  deliberately deferred; landing it requires re-running plant 5 per change
  control.
- **Doctrine defaults vs your project's rules.** The seven architecture rules
  are defaults. Both agents read your project's own docs and stated rules
  first; the doctrine fills gaps, it doesn't override. A project with no
  stated rules is itself a flagged finding, not a license to assume.

## Design decisions worth stealing

- Reviewers **name** issues + remedies; they never edit. An editor grades its
  own homework.
- Tiers encode **epistemic status** (mechanically checkable vs argued
  judgment), orthogonal to severity. A reader should always know *how* a
  finding could be wrong.
- One doctrine file, loaded fail-loud. Duplicated rules drift — a fix landing
  in one copy and not the other is how this file came to exist.
