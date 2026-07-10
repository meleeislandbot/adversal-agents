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
- [x] Headless subscription auth for `claude -p` workers, diagnosed and routed:
      interactive logins are GUI/keychain-bound and invisible to agent-spawned
      shells, so the supported route is a long-lived `claude setup-token` stored
      as `CLAUDE_CODE_OAUTH_TOKEN` in the coordinator's environment. The adapter
      passes it through, labels the route in the budget ledger, and prints the
      user-facing fix on every auth failure; setup relays it in
      `instructions.md` Phase 6. (Minting the token is a one-time user action
      per machine.)
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
- [x] The map (`map_tool.py` + `decompose.py`): a dependency blueprint from
      lemmas up to one declared goal, mirroring the Lean community's blueprint
      practice. Structure is a redrawable plan; node colors derive only from the
      gate's decisions ledger — nothing can be painted green by hand. `next`
      prints ready targets as `run_mission.py` commands; strategist
      decompositions are proposals imported only with user consent.
- [x] Kernel-checked refutations: `refuted` is earned by a Lean disproof of the
      exact negation (`<theorem_name>_disproof : ¬ (formal_statement)`), same
      strictness as `proven` (no sorry, no introduced axioms). Refutation prose
      stays a lead.
- [ ] Bounded autonomous loop: generate -> formalize -> check -> repair, with
      hard budget and escalation triggers (currently single-shot per mission).

## Phase 5 — Researcher experience

- [x] Fresh-profile self-bootstrap from the public README prompt: immutable
      source acquisition, environment discovery, reversible profile setup,
      project initialization, restart checkpoint, and deterministic readiness
      recorder.
- [x] Statement-fidelity back-translation (`backtranslate.py`): an isolated
      worker sees ONLY the Lean proposition and translates it back; the human
      compares the two sentences. The machine flags numeric mismatches but never
      rules "equivalent".
- [x] Mathematical CI (`reverify.py`): every artifact ever marked `proven` is
      re-checked against the kernel with the same strictness; regressions (and
      pre-canonical, unreproducible verdicts) are reported loudly and flagged on
      the map.
- [ ] `adversal init` and `adversal run "<claim>"` wrappers.
- [ ] Validation on a known theorem once an independent citation validator
      lands (worker citations still fail closed). Injected-error validation is
      live: a kernel-checked disproof earns `refuted`; anything less stays a
      recorded lead.
- [ ] Long-run resumability and an auditable history of what was ever proven
      (partially covered by `reverify.py` over the recorded runs).
