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

- [ ] Lean 4 + mathlib project scaffold generated per run.
- [ ] Formalizer worker writes `.lean` files; engine runs `lake build` and
      records the true result.
- [ ] Treat `sorry`/`admit`/added-axiom as failure automatically.
- [ ] Cache verified lemmas so re-checks are cheap.

## Phase 3 — Provider adapters (remove the human messenger)

- [ ] One-shot adapter per provider CLI (Claude Code, Codex, Gemini, Grok/other,
      OpenCode), each: takes a role + brief, returns schema-valid JSON.
- [ ] Output normalization: force heterogeneous CLIs into the claim schema.
- [ ] Auth-route and cost detection per provider; budget ledger entries.
- [ ] Capability routing: send formalization to the strongest Lean model, ideas
      to others, mechanical work to a cheap/local model.

## Phase 4 — Coordinator loop

- [ ] Mission brief format and run-directory generator.
- [ ] Bounded autonomous loop: generate -> formalize -> check -> repair, with
      hard budget and escalation triggers.
- [ ] Two-plane ledger writer and canonical-brain promotion via the gate only.
- [ ] Honest run report: proven / known / refuted / not_established counts.

## Phase 5 — Researcher experience

- [ ] `adversal init` and `adversal run "<claim>"` wrappers.
- [ ] Validation on a known theorem and on a deliberately-injected error, to
      prove the machine catches both, before pointing it at open problems.
- [ ] Long-run resumability and an auditable history of what was ever proven.
