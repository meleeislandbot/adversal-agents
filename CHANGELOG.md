# Changelog

This project follows [Semantic Versioning](https://semver.org/) and uses Conventional Commits.

## [0.1.0] - 2026-07-08

### Added

- Initial project scaffold for agent-guided red-team setup.
- Single short setup prompt embedded directly in `README.md`, pointing agents to `instructions.md`.
- Agent-facing guided setup procedure in `instructions.md`, scoped as one-shot onboarding.
- Cross-agent context files: `AGENTS.md`, `CLAUDE.md`, and `.hermes.md` for day-to-day work, separated from one-shot onboarding.
- Dedicated Hermes coordinator profile template at `profiles/hermes-redteam-coordinator/SOUL.md`.
- Project-local `.adversal/` control plane with scenarios, ledgers, workers, and templates.
- Read-only diagnostic helper: `scripts/adversal_doctor.py`.
- Run skeleton helper: `scripts/create_run_skeleton.py`.
- Initial red-team research wiki under `llm-wiki/`.
- Professional maintenance docs and validation workflow.
