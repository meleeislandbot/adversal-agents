# Changelog

This project follows [Semantic Versioning](https://semver.org/) and uses Conventional Commits.

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
