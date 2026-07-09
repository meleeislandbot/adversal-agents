# Architecture

Adversal Agents is a coordinated council of AI models with a deterministic truth
gate. The design separates three things that are usually (and dangerously)
collapsed into one model: process orchestration, generation, and the judgment of
what is true.

```text
        Hermes coordinator
        - runs the protocol loop, manages files, talks to the user
        - does NOT decide what is true
                |
        mission brief + claims under test
                |
     +----------+-----------+-----------+
     |          |           |           |     workers are isolated;
 strategist  formalizer  prior-art    skeptic  they never see each other's
     |          |          auditor       |     drafts (no context contamination)
     +----------+-----------+-----------+
                |
   structured assessments: workers/*.json
                |
        Deterministic verdict engine  (no LLM, no network)
        - cold-iron rules, in priority order
        - checks the exact submitted Lean theorem/type
        - accepts citations/refutations only after independent validation
                |
        verdict.json / verdict.md  +  append-only ledgers
```

## Three separated concerns

1. **Orchestration (Hermes).** Launches workers through adapters, enforces
   budget and turn limits, checkpoints state to files, messages the user. It is
   a secretary and process supervisor, not a philosopher-king. Its own model
   never has the final say on truth.
2. **Generation (the council).** Multiple providers, each pinned to one role.
   Diversity is used for coverage (different proof paths, different attacks), not
   for voting. Workers communicate only through artifacts.
3. **Judgment (the gate).** A deterministic engine and a proof assistant. This
   is the only component allowed to grant `proven`. It cannot be flattered.

The canonical mathematical object is the Lean type in `claims.json`. Its prose
`statement` is explanatory and is not itself kernel-certified; this prevents a
model from proving an easy formal statement and attaching it to a stronger
English claim. Workers run without tools in isolated empty directories and can
only return proposal JSON.

## Why workers are isolated

If one worker's output is fed to the others as context, a single confident error
propagates and the models converge on it — correlated failure and consensus
laundering. Each worker gets the brief and the claim, not the other workers'
prose. Reconciliation happens in the deterministic engine, from evidence.

## The two-plane ledger

- **Proposal plane** (append-only, attributed): any worker may add a claim,
  objection, or piece of evidence to its own lane. Nothing is overwritten.
- **Canonical plane** (the "brain"): the coordinator promotes a claim here only
  after the gate grants it a status. Every canonical entry carries provenance,
  the deciding rule, confidence, and a link to any dissent.

This keeps the shared brain trustworthy without making the coordinator an
infallible oracle: workers propose, the gate disposes, dissent survives.

## Source repo vs instantiated project

The source repository holds versioned bootstrap assets under `templates/project/`
(roles, schema, scripts, control-plane template, and the empty `llm-wiki/`
template). An instantiated project stores live state under its own `.adversal/`
(runs, ledgers, worker status, verdicts) and grows its own `llm-wiki/` knowledge
base from verified outcomes. Neither the live `.adversal/` nor a project's
`llm-wiki/` is ever committed to the source repository — only the empty
templates are.

## Autonomy is safe here because the gate is objective

A coordinator may loop for many turns without asking the user — generate,
formalize, check, repair, check — because Lean stops false steps. The bounds are
budget (max turns/tokens/cost/wall-clock) and explicit escalation triggers
(irreversible actions, spend threshold, ambiguous goal, non-convergence). In a
domain without an objective gate this autonomy would manufacture confident
nonsense; here it cannot promote anything the kernel rejects.
