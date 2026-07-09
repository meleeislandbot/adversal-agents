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
| `proven` | Established | A Lean artifact that `lake build` accepts, re-checked by the engine |
| `known` | Already in the literature; not new | A prior-art citation (name, author, year, reference) |
| `refuted` | A specific step is false | A counterexample or a cited false step |
| `contested` | Substantive disagreement, unresolved | Evidence on more than one side |
| `conjecture` | Precise, plausible, unproven | A stated argument; never a bare vote |
| `sketch` | Informal argument with listed gaps | An argument plus an explicit gap list |
| `not_established` | The honest default | Awarded when nothing above is earned |

`not_established` is not an error state. It is the correct answer most of the
time. A run that ends with everything `not_established` has told you the truth.

## The cold-iron rules

These are enforced deterministically in `verdict_engine.py`, in this priority
order. Model votes never override them.

1. **A specific, evidenced refutation dominates.** One real counterexample beats
   any number of approvals.
2. **Prior art demotes to `known`.** If it already exists, it is not progress,
   regardless of how novel it felt.
3. **`proven` requires a kernel check.** Only a Lean artifact the engine can
   build earns it. Confidence, eloquence, and consensus earn nothing.
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
