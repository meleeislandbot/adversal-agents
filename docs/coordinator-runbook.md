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
                    formalizer       prior-art-auditor       skeptic
                  (Claude/Codex)       (Claude/Codex)      (Claude/Codex)
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
     --statement "<the exact claim>" --claim-id C1 \
     --providers claude,codex
   ```
   (In an instantiated project the scripts live under the project's `scripts/`.)
   This dispatches the formalizer, prior-art auditor, and skeptic as isolated
   Claude and Codex workers, then runs the gate. Omit `--providers` to retain
   the lower-cost Claude-only default.
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

Two independent axes matter, and they are checked separately. **Novelty** — is a
direction already a known program? — is measured by `ideate.py --audit` (the
prior-art auditor). **Truth** — does the next step actually hold? — is measured by
the gate. A direction can be novel and false, known and true, or any mix; only
verifying both tells you which. Generation alone tells you neither.

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

## Setup: the profile bootstraps itself

The deployment assumes no separate technical agent. The user creates one fresh
Hermes profile and pastes the README prompt into it. That same profile discovers
its environment, clones an immutable source checkout, asks for the required
permissions, installs its own Adversal identity/skill, and initializes the
project through `bootstrap_adversal.py`.

After the profile changes `SOUL.md`, it checkpoints and stops. A new session in
the same profile resumes setup, verifies the installed hashes, configures Lean
and the user-selected worker routes, then runs deterministic acceptance tests.

Providers are workers, not additional Hermes profiles. CLI syntax, paths,
operating system, installed skills, and auth routes are discovered on the target
machine rather than copied from the development machine.
