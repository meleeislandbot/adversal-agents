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

- [x] Engine checks the exact submitted file with `lake env lean` (in a Lake
      project) or `lean` (standalone); finds an elan toolchain even when it is
      not on `PATH`.
- [x] Treat `sorry`/`admit` as failure automatically.
- [x] Bind `proven` to an exact canonical Lean type and named declaration;
      reject unrelated files, path escapes, and introduced axioms.
- [ ] Add independent validators for citations and counterexamples. Until then,
      worker proposals fail closed as `not_established`.
- [ ] Lean 4 + mathlib project scaffold generated per run (standalone,
      mathlib-free files already verify today).
- [ ] Cache verified lemmas so re-checks are cheap.

## Phase 3 — Provider adapters (remove the human messenger)

- [x] Claude Code and Codex CLI one-shot adapters: role + claim -> schema-valid
      JSON, with `--dry-run` modes and loud non-zero failure signaling. The
      Codex adapter disables its shell and optional tool surfaces, validates
      structured output, and invalidates calls that emit tool events. Gemini /
      Grok / OpenCode adapters remain pending.
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
- [x] Divergent ideation (`ideate.py`): many bold directions per topic from the
      strategist, each an unverified conjecture + a concrete next checkable step,
      to feed the verification loop. Diversity via independent samples + distinct
      angles today; multi-model diversity once other adapters land. `--audit` tags
      each direction known-vs-off-map (novelty axis, separate from the truth axis).
- [x] Honest run report: proven / known / refuted / not_established counts.
- [x] Decisions and budget ledgers written per run (subscription route + notional
      cost logged); canonical-brain promotion via the gate still pending.
- [ ] Bounded autonomous loop: generate -> formalize -> check -> repair, with
      hard budget and escalation triggers (currently single-shot per mission).

## Phase 5 — Researcher experience

- [x] Fresh-profile self-bootstrap from the public README prompt: immutable
      source acquisition, environment discovery, reversible profile setup,
      project initialization, restart checkpoint, and deterministic readiness
      recorder.
- [ ] `adversal init` and `adversal run "<claim>"` wrappers.
- [ ] Validation on a known theorem and on a deliberately-injected error after
      independent citation/counterexample validators land. Until then setup
      verifies that both kinds of worker proposal fail closed.
- [ ] Long-run resumability and an auditable history of what was ever proven.
