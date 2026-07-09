# Roadmap

## Phase 1 — Bootstrap scaffold

- [x] Agent-facing guided setup instructions.
- [x] Single human copy/paste prompt embedded visibly in `README.md`.
- [x] Project-local `.adversal/` control plane.
- [x] Initial safe scenario registry.
- [x] Read-only environment diagnostic helper.
- [x] Cost and auth-route policy.

## Phase 0.5 — Repository professionalism

- [x] Add `CLAUDE.md` for Claude Code compatibility.
- [x] Add `GEMINI.md` for Gemini CLI default context discovery.
- [x] Add Hermes coordinator `SOUL.md` template.
- [x] Add versioning, changelog, contribution, security, and release-process docs.
- [x] Add repository validation script and GitHub Actions workflow.
- [x] Add branch protection once the first validation workflow has run successfully.

## Phase 2 — Worker adapters

- [ ] Claude Code one-shot adapter with environment scrubbing.
- [ ] Codex CLI one-shot adapter with sandbox/output capture.
- [ ] Gemini CLI adapter with verified auth route.
- [ ] OpenCode adapter with explicit provider/cost config.
- [ ] Ollama/local-model adapter for cheap mutation/classification.
- [ ] Deterministic scorer adapter.

## Phase 3 — Red-team harness

- [ ] Scenario schema validator.
- [ ] Run directory generator with trace manifest.
- [ ] Deterministic postcondition checks.
- [ ] Budget ledger writer.
- [ ] Worker status updater.
- [ ] Regression suite runner.

## Phase 4 — Council workflow

- [ ] Attacker / target / verifier / curator role prompts.
- [ ] Claims, objections, and decisions ledger tooling.
- [ ] Cross-worker trace comparison.
- [ ] Wiki proposal and curation flow.

## Phase 5 — Packaging

- [ ] `adversal init` helper.
- [ ] `adversal doctor` command wrapper.
- [ ] Install-free script mode.
- [ ] Optional Python package or single-binary CLI.
