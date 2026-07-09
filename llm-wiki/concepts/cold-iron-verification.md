---
title: Cold-Iron Verification
created: 2026-07-09
updated: 2026-07-09
type: concept
tags: [adversal-agents, verification, mathematics, formal-methods, sycophancy, epistemics]
sources: []
confidence: high
contested: false
contradictions: []
---

# Cold-Iron Verification

## Why this matters

The project exists to solve one failure: a researcher working with AI models on a
hard mathematical problem is repeatedly told, with confidence, that they are
close and that their idea is brilliant — when nothing has been verified. Adding
more models does not help, because they share training data and a bias toward
agreeing with the user. Five models praising the same draft are one bias, five
times, not five independent witnesses. See [[multi-agent-verification-failures]].

## The doctrine

Model agreement is never treated as truth. Truth is earned against something a
model cannot flatter:

- `proven` — only a proof-assistant kernel (Lean 4 + mathlib) grants this, and
  the verdict engine re-runs the build rather than trusting the worker.
- `known` — a literature citation demotes a claim; a re-derivation is not
  progress.
- `refuted` — one specific, evidenced broken step beats any number of approvals.
- `not_established` — the honest default, correct most of the time.

Praise ("genius", "breakthrough", "you're close") is detected and given zero
weight; it is counted only to show how much smoke was blown.

## Design implications

- Separate orchestration (Hermes), generation (the council), and judgment (the
  gate). The coordinator's model never decides truth.
- Isolate workers so a confident error does not propagate as shared context.
- Use multiple models for coverage and independent attack, not for voting.
- Autonomy is safe only because the gate is objective: a loop cannot promote
  anything the kernel rejects.

## Honest limits

No council of current models will prove a famous open problem. The system's real
value is negative and rigorous: it verifies small pieces, catches re-derivations,
locates the exact step where an argument fails, and stops a researcher from
believing a proof that is not there.

Related: [[multi-agent-verification-failures]], [[memory-and-rag-poisoning]],
[[council-protocols-claims-and-objections]].
