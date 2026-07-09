# Roadmap

The order is deliberate: build the truth gate first, then generation around it.
The gate is what makes everything else safe, so it cannot be last.

## Phase 1 — The gate and the contract (done)

- [x] Epistemic contract: the allowed statuses and the cold-iron rules
      (`docs/epistemics.md`).
- [x] Deterministic verdict engine that enforces them with no LLM
      (`templates/project/scripts/verdict_engine.py`), with a self-test proving
      it cannot be flattered.
- [x] Adversarial role prompts: strategist, formalizer, prior-art auditor,
      skeptic (`templates/project/roles/`).
- [x] Worker output schema (`claim.schema.json`).
- [x] Two-plane control-plane template under `.adversal/`.

## Phase 2 — Formal verification integration

- [x] Engine runs `lake build` (in a Lake project) or `lean` (standalone) and
      records the true kernel result; finds an elan toolchain even when it is
      not on `PATH`.
- [x] Treat `sorry`/`admit` as failure automatically.
- [ ] Lean 4 + mathlib project scaffold generated per run (standalone,
      mathlib-free files already verify today).
- [ ] Cache verified lemmas so re-checks are cheap.

## Phase 3 — Provider adapters (remove the human messenger)

- [x] Claude Code one-shot adapter (`claude_worker.py`): role + claim ->
      schema-valid JSON, with a `--dry-run` mode and loud non-zero failure
      signaling. Codex / Gemini / Grok / OpenCode adapters pending.
- [x] Output normalization: force heterogeneous CLI output into the claim schema
      (implemented for Claude; reused by future adapters).
- [ ] Resolve headless subscription auth so `claude -p` runs as a worker on the
      host. Blocked in nested/sandboxed shells that have no Claude login
      (`claude -p` returns "Not logged in"); works where the user has run
      `claude login`.
- [ ] Auth-route and cost detection per provider; budget ledger entries.
- [ ] Capability routing: send formalization to the strongest Lean model, ideas
      to others, mechanical work to a cheap/local model.

## Phase 4 — Coordinator loop

- [x] Mission brief + run-directory generator and end-to-end runner
      (`run_mission.py`): claim -> roles -> gate -> ledgers, with a `--dry-run`.
- [x] Honest run report: proven / known / refuted / not_established counts.
- [x] Decisions and budget ledgers written per run (subscription route + notional
      cost logged); canonical-brain promotion via the gate still pending.
- [ ] Bounded autonomous loop: generate -> formalize -> check -> repair, with
      hard budget and escalation triggers (currently single-shot per mission).

## Phase 5 — Researcher experience

- [ ] `adversal init` and `adversal run "<claim>"` wrappers.
- [ ] Validation on a known theorem and on a deliberately-injected error, to
      prove the machine catches both, before pointing it at open problems.
- [ ] Long-run resumability and an auditable history of what was ever proven.
