# Roadmap

## Phase 1 — Bootstrap scaffold

- [x] Agent-facing guided setup instructions.
- [x] Human copy/paste prompt.
- [x] Project-local `.adversal/` control plane.
- [x] Initial safe scenario registry.
- [x] Read-only environment diagnostic helper.
- [x] Cost and auth-route policy.

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
