# Adversal Agents

A cold-iron mathematical verification council. It coordinates several AI models
(Claude, GPT, Gemini, Grok, ...) through a Hermes coordinator to work on a
mathematical goal — but it is built so that no model, and no chorus of models,
can ever tell you something is proven when it is not.

The adversary here is aimed inward: a dedicated skeptic attacks *your own*
claims, and every "proven" must survive a proof-assistant kernel, not a vote.

## The problem it solves

Working a hard problem with one AI, you get flattered: "brilliant", "you're
close", "this is essentially done". Adding more models does not fix it — they
share training data and the same instinct to agree, so five approvals are one
bias repeated five times. This system refuses to treat agreement as truth.

Concretely, it replaces the exhausting manual loop of pasting one model's answer
into another model to check it. The coordinator runs that loop for you, assigns
each model an adversarial role, and gates every result on evidence a model
cannot fake.

## What it honestly can and cannot do

- It **will not** prove the Riemann Hypothesis, and neither will any council of
  today's models. Point it at tractable, checkable pieces first.
- It **will** formalize and verify individual lemmas in Lean.
- It **will** tell you, with a specific broken step, when an argument fails.
- It **will** catch a re-proof of a known theorem dressed up as new work.
- Its most valuable output is negative: it stops you believing a proof that
  isn't there. See [`docs/epistemics.md`](docs/epistemics.md).

## How it works

```text
Hermes coordinator (process + protocol, NOT the arbiter of truth)
      | writes a mission brief and the claims under test
      v
Council workers, each with ONE role, isolated (no cross-talk):
  strategist        -> proposes lemmas/reductions        (max status: conjecture)
  formalizer        -> writes Lean; kernel decides        (only path to proven)
  prior-art-auditor -> "is this already known?" + cite    (demotes to known)
  skeptic           -> finds the first broken step        (refutes; never praises)
      | each writes a structured JSON assessment
      v
Deterministic verdict engine  (scripts/verdict_engine.py)
  applies the cold-iron rules; consensus never grants "proven"
      v
Honest verdict + append-only ledger of what is actually proven vs conjectured
```

The gate is real and runs today with no paid API:

```bash
python3 templates/project/scripts/verdict_engine.py --selftest
```

It demonstrates that five workers at 0.99 confidence, praising loudly, still
produce `not_established` — and that one evidenced refutation beats them all.

## Roles and contract

Worker role prompts live in [`templates/project/roles/`](templates/project/roles/).
Every worker emits the JSON in
[`claim.schema.json`](templates/project/.adversal/schema/claim.schema.json). The
coordinator profile template is in
[`profiles/hermes-verification-coordinator/SOUL.md`](profiles/hermes-verification-coordinator/SOUL.md);
it is inert until copied into a Hermes profile.

## Quick start

Paste the prompt below into the agent you want to use for the one-time setup. It
configures a verification coordinator profile, installs the Lean gate, verifies
your paid worker CLIs, and runs the machine-validation missions before any real
mathematics.

<!-- adversal-setup-prompt:start -->
```text
Read and follow this one-time setup guide exactly:
https://github.com/meleeislandbot/adversal-agents/blob/main/instructions.md

Ask me only when the instructions tell you to.
```
<!-- adversal-setup-prompt:end -->

## Status

Early but running end to end. The deterministic gate, Lean kernel integration,
adversarial roles, the Claude Code worker adapter, and a mission runner are in
place (see [`docs/roadmap.md`](docs/roadmap.md)); adapters for the other
providers are next. An instantiated project grows its own `llm-wiki/` — the
coordinator's gated knowledge base — locally; the source repo ships only the
empty template under `templates/project/llm-wiki/`.
