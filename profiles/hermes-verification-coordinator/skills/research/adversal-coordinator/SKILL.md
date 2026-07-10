---
name: adversal-coordinator
description: Configure, resume, and operate an Adversal cold-iron mathematical verification project from a fresh Hermes profile. Use when the user asks to bootstrap or continue Adversal setup, inspect readiness, run an ideation or verification mission, coordinate isolated mathematical workers, interpret a verdict, or update the gated project wiki.
---

# Adversal Coordinator

Coordinate the protocol; never decide truth by model judgment.

## Orient

1. Locate the project root containing `.adversal/project.yaml`. Do not assume the
   source-repository checkout is the runtime project.
2. Read `docs/epistemics.md`, `.adversal/project.yaml`, and
   `llm-wiki/index.md` completely before a mission or promotion.
3. Use only these statuses: `proven`, `known`, `refuted`, `contested`,
   `conjecture`, `sketch`, `not_established`.
4. Treat worker JSON as proposals. The verdict engine and independent validators
   are authoritative.

## Resume bootstrap

When `.adversal/bootstrap/state.json` has phase `restart_required`:

1. Read `.adversal/bootstrap/instructions.md` and the state file.
2. Run `.adversal/bootstrap/bootstrap_adversal.py resume` from the project. It is
   the helper snapshot recorded during the first session.
3. Pass the current profile's verified `HERMES_HOME`; never guess a profile path.
4. Continue from the recorded phase. Do not repeat completed writes.

If the helper snapshot fails its recorded hash check, clone the recorded
repository, check out the exact 40-character commit in the state file, and
recover it from there. Do not continue from a moving branch.

## Run a mission

1. Convert the user's idea into a bounded claim. Require both the exact Lean
   `formal_statement` and declaration name before `proven` is possible.
2. Decide the roles, providers, timeouts, and cost boundary before dispatch.
3. Ask before login, credentials, metered APIs, or exceeding the agreed budget.
4. Invoke `scripts/run_mission.py`; do not manually shuttle worker drafts.
5. Read `verdict.json` and report what the gate checked, artifact paths,
   unresolved dissent, and the next checkable step.

Use `scripts/ideate.py` only for divergent generation. Its output is unverified
and never enters canonical knowledge directly.

## Promote knowledge

Promote only through a deterministic promotion command that consumes a
gate-produced verdict and preserves provenance. If the installed project has no
such command, do not edit canonical wiki sections manually; report promotion as
unavailable. Never promote `not_established`, `conjecture`, `sketch`, or
`contested`.

Until independent citation and counterexample validators exist, their worker
proposals remain leads and cannot become `known` or `refuted`. Inspect the
installed gate rather than assuming roadmap items are complete.

## Stop conditions

Stop and ask for ambiguous mathematical scope, profile/global writes, toolchain
installation, authentication, secrets, paid routes, destructive actions,
budget breaches, or non-convergence after the configured repair limit.
