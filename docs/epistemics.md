# Epistemics — the cold-iron contract

This is the spine of the project. Everything else exists to enforce it.

The failure this system is built to prevent: a person working with AI models on a
hard problem is told, repeatedly and confidently, that they are close, that their
idea is brilliant, that the proof is essentially done — when none of it has been
verified. Multiple models do not fix this. Models share training data and share
the instinct to agree with the user, so five of them praising the same draft is
not five witnesses; it is one bias, five times.

So this system refuses to treat model agreement as truth. Truth has to be earned
against something a model cannot flatter: a proof-assistant kernel, or a citation
to the existing literature.

## The only statuses allowed

A claim is always in exactly one of these. Nothing else may be said about it.

| Status | Meaning | How it is earned |
|---|---|---|
| `proven` | Exact formal proposition established | A named Lean declaration whose type matches the canonical `formal_statement`, checked on the submitted file with no introduced axiom |
| `known` | Already in the literature; not new | A prior-art citation confirmed independently of the worker that proposed it |
| `refuted` | The exact formal proposition is false | A named Lean disproof (`<theorem_name>_disproof`) whose type is the exact negation `¬ (formal_statement)`, kernel-checked with the same strictness as a proof |
| `contested` | Substantive disagreement, unresolved | Evidence on more than one side |
| `conjecture` | Precise, plausible, unproven | A stated argument; never a bare vote |
| `sketch` | Informal argument with listed gaps | An argument plus an explicit gap list |
| `not_established` | The honest default | Awarded when nothing above is earned |

`not_established` is not an error state. It is the correct answer most of the
time. A run that ends with everything `not_established` has told you the truth.

## The cold-iron rules

These are enforced deterministically in `verdict_engine.py`, in this priority
order. Model votes never override them.

1. **A kernel-checked disproof dominates.** `refuted` is earned with exactly the
   same strictness as `proven`: a Lean declaration inhabiting the exact negation
   of the canonical statement, no introduced axioms. One real disproof beats any
   number of approvals; worker counterexample prose is only a lead.
2. **Verified prior art demotes to `known`.** A citation string is not enough:
   its identity and relevance must be checked outside the proposing worker.
3. **`proven` requires an exact kernel check.** The submitted file must define
   the named theorem with exactly the canonical Lean type. Compiling an unrelated
   theorem, escaping the run directory, or introducing an axiom earns nothing.
4. **A claimed formal proof we cannot check is `not_established`,** never
   `proven`. Unchecked is not proven.
5. **Disagreement is preserved,** never averaged into a false middle.
6. **The default is skeptical.** Absent earned evidence, the claim establishes
   nothing.

## Praise has zero weight

The engine scans worker output for flattery ("genius", "breakthrough", "you're
close", and the like) and reports the count only so you can see how much smoke
was blown. It changes no status. A worker that praises instead of proving has
told you about itself, not about the mathematics.

## Why formal verification is the gate

Mathematics is the rare domain where ground truth is mechanical. A statement
proven in Lean 4 is proven — the kernel checks every inference, and it cannot be
argued with. This is why the project targets math first: it is the one place a
council of fallible models can be held to an incorruptible standard. The serious
AI-for-math work (AlphaProof, Tao's formalization projects) all runs this way,
for exactly this reason.

## What this system honestly can and cannot do

- It **cannot** prove the Riemann Hypothesis, and neither can any council of
  current models. Do not aim it there first.
- It **can** formalize and verify individual lemmas and special cases.
- It **can** tell you, rigorously, when a claimed step does not hold.
- It **can** catch a re-derivation of a known theorem masquerading as new work.
- Its most valuable service is negative: it stops you from believing a proof
  that is not there.
