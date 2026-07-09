# Changelog

This project follows [Semantic Versioning](https://semver.org/) and uses Conventional Commits.

## [Unreleased]

### Changed

- Hardened the truth boundary: `proven` now requires the submitted Lean file to
  define a named declaration with exactly the canonical formal type. The gate
  rejects path escapes, unrelated compiling theorems, `sorry`/`admit`, and
  model-introduced axioms.
- Worker-authored citations and counterexamples are treated as unverified leads,
  never as automatic `known` or `refuted` verdicts.
- Claude workers run without tools or project customizations in isolated empty
  directories, preventing cross-worker draft access.
- Claims with no worker output now receive explicit `not_established` verdicts,
  and mission failures propagate non-zero exit codes.
- CI now installs the pinned Lean toolchain and exercises the real kernel-boundary
  self-test on every pull request.

### Fixed

- `ideate.py --audit --dry-run` no longer performs real auditor calls.

## [0.3.1] - 2026-07-09

### Added

- `ideate.py --audit`: runs the prior-art auditor on each generated direction and
  tags it in `ideas.md` as `KNOWN` (with citation) or `no prior art found`. This
  measures the *novelty* axis — is a direction already a named program? — which is
  separate from the *truth* axis the gate checks. It stops recall from being
  mistaken for invention. Opt-in, since it adds one worker call per direction.

## [0.3.0] - 2026-07-09

### Added

- Divergent ideation mode (`templates/project/scripts/ideate.py`): given a topic,
  it runs the strategist several times with distinct angle-provocations (import a
  distant field, attack a hidden assumption, reason by analogy, invent a
  definition, reformulate, or probe the failure mode) and assembles a menu of
  bold candidate directions. Every direction is an explicitly unverified
  conjecture with a concrete next checkable step — never a result.
- `--suffix` option on `claude_worker.py` so one role can produce many samples.

### Changed

- Reframed the strategist role (`templates/project/roles/strategist.md`) as an
  imaginative divergent generator held to a strict discipline: each idea must be a
  precise falsifiable statement plus the next checkable step, capped at
  `conjecture`, with no self-congratulation. Imagination up front, iron at the
  gate.

## [0.2.1] - 2026-07-09

### Changed

- The source repo no longer ships a personal research wiki. A project's
  `llm-wiki/` is now local per-project state — the coordinator's gated knowledge
  base — and the repo carries only an empty template under
  `templates/project/llm-wiki/` with `verified/`, `prior-art/`, and `dead-ends/`
  sections plus the gate-promotion rule. The root `llm-wiki/` is git-ignored and
  a `make validate` guard prevents a personal wiki from being committed.

## [0.2.0] - 2026-07-09

### Changed

- **Pivoted the project** from a red-team lab for autonomous agents to a cold-iron
  mathematical verification council. The goal is now to coordinate several AI
  models against a mathematical claim while making it structurally impossible for
  model agreement to be mistaken for truth.
- Rewrote `README.md`, `IDEA.md`, `docs/architecture.md`, `docs/roadmap.md`, and
  the context files (`.hermes.md`, `AGENTS.md`, `CLAUDE.md`) around the new
  objective.
- Replaced the coordinator profile with
  `profiles/hermes-verification-coordinator/SOUL.md` (removed the red-team one).
- Replaced the red-team scenarios with math verification missions and a
  machine-validation procedure (known-theorem / injected-error / true-lemma).
- Rewrote `instructions.md` to set up the verification coordinator and the Lean
  gate.

### Added

- `docs/epistemics.md` — the cold-iron contract: the allowed claim statuses and
  the deterministic rules that grant them.
- `templates/project/scripts/verdict_engine.py` — the deterministic gate. It
  computes an honest status per claim, grants `proven` only for a kernel-checked
  Lean artifact, demotes known results, lets one evidenced refutation beat any
  number of approvals, and gives praise zero weight. Ships with a self-test.
- Adversarial role prompts under `templates/project/roles/` (strategist,
  formalizer, prior-art-auditor, skeptic) and a worker output schema
  (`claim.schema.json`).
- Lean-toolchain detection in `adversal_doctor.py`; the verdict-engine self-test
  wired into `make validate` so CI guarantees the gate cannot be flattered.
- Real Lean kernel integration in the verdict engine: it type-checks standalone
  `.lean` files (or `lake build`s a Lake project), finds an elan toolchain even
  when it is off `PATH`, and rejects any proof using `sorry`/`admit` (Lean only
  warns and exits 0 on those). Verified end-to-end: a true theorem becomes
  `proven`; `2 + 2 = 5` and a `sorry` proof stay `not_established`.
- `templates/project/scripts/claude_worker.py` — Claude Code worker adapter that
  drives `claude -p` in one role against one claim and returns a schema-valid
  assessment; for the formalizer it saves the model's Lean source for the kernel
  to check. Has a `--dry-run` mode and signals worker failure with a non-zero
  exit so an auth/rate error is never mistaken for a real judgment. Defaults to
  the subscription login by scrubbing API-key/token env vars (override with
  `--allow-api`), and logs each call's route and notional cost.
- `templates/project/scripts/run_mission.py` — the coordinator's core action:
  one command takes a claim, dispatches the council roles as isolated workers,
  runs the gate, and records the outcome in the decisions and budget ledgers.
- `docs/coordinator-runbook.md` — how Hermes drives a mission (it coordinates;
  the kernel and rules decide) and how to set up the coordinator profile.

## [0.1.0] - 2026-07-08

### Added

- Initial project scaffold for agent-guided red-team setup.
- Single short setup prompt embedded directly in `README.md`, pointing agents to `instructions.md`.
- README project objective section describing the ideal end-state: a Hermes-orchestrated, auditable red-team lab for autonomous agents.
- Agent-facing guided setup procedure in `instructions.md`, scoped as one-shot onboarding.
- Cross-agent context files: `.hermes.md`, `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` for day-to-day work, separated from one-shot onboarding.
- Dedicated Hermes coordinator profile template at `profiles/hermes-redteam-coordinator/SOUL.md`, documented as inert until installed/copied into the selected Hermes profile.
- Project bootstrap template at `templates/project/.adversal/` with scenarios, ledgers, workers, and templates.
- Read-only diagnostic helper template: `templates/project/scripts/adversal_doctor.py`.
- Run skeleton helper template: `templates/project/scripts/create_run_skeleton.py`.
- Initial red-team research wiki under `llm-wiki/`.
- Professional maintenance docs and validation workflow.
