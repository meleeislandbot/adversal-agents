---
title: Agentic Evaluation Planes
created: 2026-07-05
updated: 2026-07-06
type: concept
tags: [adversal-agents, llm-evaluation, benchmark, verification, evidence, red-teaming]
sources: [raw/papers/safeclawbench-tool-using-agent-security-2026.md, raw/papers/how-vulnerable-ai-agents-ipi-competition-2026.md, raw/papers/seclaw-spec-driven-security-task-synthesis-2026.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/agentharm-benchmark-llm-agents-2024.md]
confidence: high
contested: false
contradictions: []
---

# Agentic Evaluation Planes

## Core idea

Agentic evaluation should distinguish what the model **says**, what the trace **proves**, and what the environment **suffers**. SafeClawBench names this staged distinction as semantic harm, audit-evidence harm, and sandbox harm. ^[raw/papers/safeclawbench-tool-using-agent-security-2026.md]

## Three planes

| Plane | Question | Evidence artifact |
|---|---|---|
| Semantic | Did the model agree with, plan, or describe unsafe behavior? | Model text, planner output, policy classification |
| Audit-evidence | Is there trace evidence of unsafe intent or attempted action? | Tool-call request, parameters, memory diff, browser trace, rejected policy decision |
| Sandbox | Did protected state actually change or leak? | Files modified, message sent, database changed, network request, secret disclosed |

## Concealment as a fourth scoring axis

A large-scale public competition on indirect prompt injection highlights concealment: an attack can be more dangerous if the final user-visible response hides that compromise occurred. ^[raw/papers/how-vulnerable-ai-agents-ipi-competition-2026.md]

Adversal Agents should therefore score each run on:

1. **harm plane reached** — semantic, audit, sandbox;
2. **concealment** — did the response look benign to the user?;
3. **utility preservation** — did the agent still complete or appear to complete the benign task?;
4. **replayability** — can another verifier reproduce the trace?;
5. **defense adaptivity** — did the attack target the actual deployed defense?

## Design implication

The primary pass/fail criterion should be sandbox or externally observable postcondition when available. Semantic agreement is still useful as an early warning, but it should not be treated as equivalent to real-world harm.

## Relationship to scenario synthesis

SeClaw proposes spec-driven synthesis of security tasks for autonomous agents, explicitly targeting stateful environments with tools, files, memory, and services. This suggests a practical path: specify the expected protected invariant, synthesize tasks/attacks, run in a sandbox, and score by trace plus postcondition. ^[raw/papers/seclaw-spec-driven-security-task-synthesis-2026.md]

Related: [[agent-safety-benchmarks]], [[agent-red-team-methodology]], [[emerging-agent-threats-2026]].

## Interpretability signal from J-space

Anthropic's 2026 [[jacobian-lens-and-j-space]] work strengthens the reason to keep Adversal Agents evidence-led: a worker's written answer may omit internal recognition of prompt injection, evaluation setup, or strategic/deceptive considerations. For closed CLI workers this is mostly a limitation, because activation-level methods cannot be applied directly; for local/open workers it suggests a possible future white-box audit layer.
