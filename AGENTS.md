# Adversal Agents — Project Instructions for Agents

This repository builds a **cold-iron mathematical verification council**: several
AI models, each in a fixed adversarial role, coordinated toward a mathematical
goal, with every result gated on evidence a model cannot fake.

Read [`docs/epistemics.md`](docs/epistemics.md) before substantial work. It is
the spine; everything else enforces it.

## The one rule that overrides everything

**Model agreement is not truth.** You may never present a claim as `proven` on
the strength of confidence, eloquence, or consensus. `proven` is granted only by
a Lean artifact the kernel accepts. The honest default for any claim is
`not_established`. Do not flatter the user or their claims.

## Statuses

Use only: `proven`, `known`, `refuted`, `contested`, `conjecture`, `sketch`,
`not_established`. Definitions and the deciding rules are in `docs/epistemics.md`.

## Coordination model

- The active agent coordinates process; it does not decide truth. The
  deterministic verdict engine (`templates/project/scripts/verdict_engine.py`)
  and the Lean kernel do.
- Workers are pinned to one role each (`templates/project/roles/`) and are
  isolated — they communicate through artifacts, never by seeing each other's
  drafts.
- Every worker emits JSON matching
  `templates/project/.adversal/schema/claim.schema.json`.

## Write policy

Safe project-local writes are allowed:

- `.adversal/runs/<run-id>/...` (briefs, worker JSON, Lean files, verdicts)
- `.adversal/ledgers/*.jsonl` (append-only proposal plane)
- `.adversal/workers/status.md`

Promote a claim into the canonical brain only after the gate grants it a status,
with provenance and the deciding rule. Preserve dissent; never overwrite it. Do
not commit live `.adversal/` runtime state in the source repo — versioned
bootstrap assets live under `templates/project/`.

## Interrupt the user for

Provider/worker selection; login/auth; secrets or API keys; paid/metered API
usage; sudo or global config; destructive actions; budget-limit breaches;
ambiguous mathematical scope. Do not interrupt for read-only diagnostics,
creating project-local folders, or empty ledgers.

## Cost policy

Prefer: deterministic checks; local tools; local models; subscription-native
CLIs; metered APIs only with explicit approval. Record auth route and cost risk
in `.adversal/ledgers/budget.jsonl`. Check API-key env vars by presence only.

## Repository maintenance

Branch for non-trivial changes; Conventional Commits; update `CHANGELOG.md` for
user-visible changes; run `make validate` before pushing; prefer pull requests.

The `llm-wiki/` still holds research from the earlier red-team framing. Treat it
as background context, not as the current objective.
