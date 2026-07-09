# Changelog

This project follows [Semantic Versioning](https://semver.org/) and uses Conventional Commits.

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
