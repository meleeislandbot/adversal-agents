# Adversal Agents — Guided Setup Instructions for AI Agents

This document is for the AI agent doing the one-time setup. It turns a Hermes
profile plus a chosen project directory into a **cold-iron mathematical
verification council**: several AI models in fixed adversarial roles, with every
result gated on a proof-assistant kernel.

Read [`docs/epistemics.md`](docs/epistemics.md) first. The one rule that governs
everything: **model agreement is not truth; `proven` is granted only by a Lean
kernel check; the honest default is `not_established`.**

Cloning this repository activates nothing. Files only take effect when placed
where a harness reads them, installed as skills, or executed.

## Operating model: guided and incremental

Check one area, fix it if it is safe and project-local, and stop to ask the
moment a decision or risk appears. Never dump a giant list of blockers at the
end.

**Stop and ask before:** choosing/modifying a Hermes profile or writing to
`~/.hermes/`; installing toolchains (including Lean); login or device-code flows;
credentials or API keys; paid/metered API usage; env vars that may force paid
billing; sudo or global config; destructive actions or overwrites; any external
side effect.

**Proceed without asking for:** read-only diagnostics; CLI/version/profile
checks; creating project-local folders and empty ledgers under `.adversal/`;
writing run artifacts; running the local verdict engine and self-tests.

## Phase 1 — Configure the verification coordinator profile

There will be a Hermes coordinator. Do not create one unless asked. Read-only
first: `hermes profile list`, `hermes profile show <profile>`,
`hermes -p <profile> tools --summary list`, `hermes -p <profile> skills list`.

A configured coordinator needs:

1. **SOUL.md** copied into the profile (a global change — ask first). Source:
   `profiles/hermes-verification-coordinator/SOUL.md`.
2. **Toolsets**: at minimum `file terminal code_execution web skills todo memory
   session_search clarify delegation`. Enable messaging/gateway tools only if the
   user wants progress pings.
3. **Skills** (install official ones; do not recreate): the Hermes agent skill,
   `llm-wiki`, and the worker skills for each provider CLI the user runs
   (`claude-code`, `codex`, `gemini`, `opencode`, plus any Grok/other route).

## Phase 2 — Confirm the project root

The Adversal project root should end up containing `.hermes.md`, `AGENTS.md`,
`CLAUDE.md`, `GEMINI.md`, `.adversal/`, and the Lean project. If ambiguous, ask
before continuing.

## Phase 3 — Install the gate (Lean 4 + mathlib)

The gate is what makes this project honest. Without it, nothing can ever be
`proven`. Check first: `lake --version` / `lean --version`. If missing, explain
the official install (`elan`, then `lake`) and **ask before installing** — it is
a toolchain install. Once present, scaffold a per-project Lean package with
mathlib as a dependency. Run `python3 scripts/adversal_doctor.py --json` and
confirm `gate_available` is true.

## Phase 4 — Context files

Create minimal day-to-day context files in the root if missing: `.hermes.md`
(Hermes coordinator rules), `AGENTS.md` (cross-agent contract), `CLAUDE.md` and
`GEMINI.md` (thin wrappers pointing to `AGENTS.md`). Do not copy onboarding text
into them.

## Phase 5 — Control plane

Copy the bootstrap assets from `templates/project/` into the root: the
`.adversal/` control plane, `roles/`, and `scripts/`. Do not clone the whole
source repo for runtime state. Create empty ledgers without overwriting:
`.adversal/ledgers/{claims,objections,decisions,budget}.jsonl`.

## Phase 6 — Verify the worker CLIs

For each provider the user pays for (Claude Code, Codex, Gemini, Grok, OpenCode,
local/Ollama), one at a time: check the CLI exists and its version; check the
auth route; check API-key env vars **by presence only, never printing values**;
if login or a cost-sensitive choice is needed, stop and ask. Record each in
`.adversal/workers/status.md` and append an auth/cost note to
`.adversal/ledgers/budget.jsonl`. Prefer subscription-native routes; warn that
API-key env vars may force metered billing.

## Phase 7 — Validate the machine before any real math

Do not point the council at an open problem until it has passed all three:

1. **Known-theorem check** — feed a known theorem; prior-art auditor must return
   `known` with a citation.
2. **Injected-error check** — feed an argument with one false step; the skeptic
   must return `refuted` with the exact `breaks_at`.
3. **True-lemma check** — feed a small provable lemma; the formalizer must
   produce a Lean file that `lake build` accepts before it is `proven`.

Run each as a mission under `.adversal/runs/<run-id>/` and score it with
`scripts/verdict_engine.py --run <dir>`. If the machine mislabels any of the
three, fix the setup before proceeding.

## Phase 8 — Readiness summary

Keep it short: coordinator profile and readiness; project root; gate available
(yes/no); context files present; ready workers and those needing login; cost
risks; files created; and the results of the three validation missions. The
detailed record lives in `.adversal/`.
