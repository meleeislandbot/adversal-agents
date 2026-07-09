# Coordinator runbook — where Hermes fits

The tools (the gate, the roles, the worker adapters) are the hands. **Hermes is
the head that drives them.** Your brother only ever talks to Hermes; Hermes does
everything else through files and scripts, and never decides truth itself.

## The mental model

```text
  your brother  ─────talks only to────▶  HERMES (coordinator profile)
                                            │  turns a claim into a mission
                                            │  runs the loop, watches budget
                                            ▼
                              run_mission.py  (one command = one mission)
                                            │  dispatches each role, isolated
                        ┌───────────────────┼───────────────────┐
                        ▼                   ▼                   ▼
                  claude_worker      claude_worker        claude_worker
                   (formalizer)     (prior-art-auditor)     (skeptic)
                        └───────────────────┼───────────────────┘
                                            ▼
                                  verdict_engine.py  (the gate: Lean + rules)
                                            │  proven / known / refuted / …
                                            ▼
                              ledgers + verdict  ──▶  Hermes reports in plain words
```

Hermes is the **secretary general**, not the mathematician and not the judge. It
coordinates; the Lean kernel and the deterministic rules decide.

## What Hermes actually does, step by step

When your brother says, e.g., "I think I can show every zero has real part 1/2 by
this monotonicity argument", Hermes:

1. **Restates it as a bounded claim** and confirms the exact statement.
2. **Runs the mission** — a single command, no human relay:
   ```bash
   python3 .adversal/../scripts/run_mission.py \
     --statement "<the exact claim>" --claim-id C1
   ```
   (In an instantiated project the scripts live under the project's `scripts/`.)
   This dispatches the formalizer, prior-art auditor, and skeptic as isolated
   Claude workers, then runs the gate.
3. **Reads the verdict** (`verdict.json`) — it does not form its own opinion of
   whether the proof is right.
4. **Reports in plain language**, using only the allowed statuses: "Not
   established. The skeptic broke it at step 4; the prior-art auditor says the
   lemma you leaned on is Mertens' theorem (1874). Zero new results." Never
   "great progress" or "you're close".
5. **Keeps the ledgers** so there is a durable, honest record of what has ever
   been proven vs. merely conjectured.

## Two phases: imagine, then verify

Hard mathematics needs bold, cross-field ideas — but imagination in a model is the
same faculty as confabulation, so the two are kept separate, never blended.

1. **Ideate (divergent).** `ideate.py --topic "..."` runs the strategist several
   times with different angles (import a distant field, attack a hidden
   assumption, reason by analogy, invent a definition) to get a *spread* of bold
   directions. Each is forced to a precise, falsifiable statement plus a concrete
   next checkable step. Output is a menu of **unverified directions** — never
   results, nothing promoted to the brain.
2. **Verify (convergent).** Hermes (or the researcher) picks a promising
   direction and runs its next step as a mission (`run_mission.py`), where the
   formalizer, prior-art auditor, skeptic, and the Lean gate decide.

Be as wild as you like in phase 1; be ruthless in phase 2. The gate is what makes
wild ideas affordable: you can generate many and let the kernel filter, instead
of trusting any single one.

## Bounded autonomy

Hermes may loop without pestering your brother — propose a lemma, formalize,
check, repair, check again — because the gate stops false steps. It stops and
asks only for: budget limits (turns / usage), a genuinely ambiguous goal, no
convergence after N repairs, or anything with external side effects.

## Cost posture

Workers default to the **subscription login** (the adapter scrubs API-key
variables that would force metered billing). Every call's route and notional
token cost is logged to `.adversal/ledgers/budget.jsonl`. On a Claude Max plan
this draws from the weekly allowance, not your wallet.

Worker calls inherit the CLI's configured effort/model. At high effort a single
strategist call can run several minutes and use heavy tokens, so a wide ideation
sweep consumes real quota. Tune effort down for generation; reserve high effort
for hard formalization.

## Setup: molding the profile (your plan is correct)

Your plan — you create a Hermes profile, a prompt configures it, your brother
talks only to Hermes — is the right route. Concretely:

- **One coordinator profile per person is fine; one profile per provider is the
  anti-pattern.** The providers (Claude, later Codex/Gemini/Grok) are *workers*
  the one coordinator calls, not separate Hermes profiles.
- The setup prompt already exists: the README quick-start points the agent to
  [`instructions.md`](../instructions.md), which installs the Lean gate,
  configures the coordinator profile from
  [`profiles/hermes-verification-coordinator/SOUL.md`](../profiles/hermes-verification-coordinator/SOUL.md),
  verifies the worker CLIs, and runs the validation missions.
- "Molding" the profile means: copy that `SOUL.md` into the profile, enable the
  `terminal` / `file` / `code_execution` toolsets (Hermes needs a terminal to
  run `run_mission.py`), and let it read this runbook.
