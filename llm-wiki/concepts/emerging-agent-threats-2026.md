---
title: Emerging Agent Threats 2026
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, red-teaming, agentic-ai, security, risk, tool-use, memory, benchmark]
sources: [raw/papers/how-vulnerable-ai-agents-ipi-competition-2026.md, raw/papers/stac-tool-chain-jailbreak-llm-agents-2025.md, raw/papers/otora-reasoning-dos-llm-agents-2026.md, raw/papers/beyond-the-prompt-function-calling-jailbreak-2026.md, raw/papers/claw-like-agent-security-computer-systems-lens-2026.md, raw/papers/long-term-memory-poisoning-origin-bound-authority-2026.md, raw/papers/autonomy-tax-defense-training-breaks-llm-agents-2026.md, raw/papers/nrt-bench-multiturn-red-teaming-operator-agents-2026.md, raw/papers/kaiju-intent-gated-execution-llm-agents-2026.md, raw/papers/trajectory-guard-agentic-anomaly-detection-2026.md]
confidence: medium
contested: false
contradictions: []
---

# Emerging Agent Threats 2026

## Why this page exists

The first research pass covered the established agent-red-team base: [[indirect-prompt-injection]], [[tool-use-and-privilege-risk]], [[memory-and-rag-poisoning]], [[agent-safety-benchmarks]], and OWASP/NIST-style governance. The asynchronous research batch surfaced a newer 2025–2026 wave. I verified the arXiv records before integrating them; this page tracks those newer leads as a living frontier map.

## Verified emerging threat families

### Sequential tool attack chaining

STAC frames a tool-using agent exploit as a sequence where each individual tool call looks harmless but the chain produces a harmful operation. This strengthens the existing warning in [[tool-use-and-privilege-risk]]: pre-approving isolated tools is weaker than reasoning over the whole trajectory. ^[raw/papers/stac-tool-chain-jailbreak-llm-agents-2025.md]

**Design implication:** Adversal Agents should score tool-call sequences and intermediate state, not just individual calls.

### Reasoning-level denial of service

OTora defines Reasoning-Level Denial-of-Service: attacks that preserve task correctness but inflate reasoning depth, latency, or tool-use budget. This expands safety beyond confidentiality/integrity into economic availability. ^[raw/papers/otora-reasoning-dos-llm-agents-2026.md]

**Design implication:** Add cost/latency/tool-budget regressions to red-team scoring.

### Function-calling shared-context attacks

Beyond the Prompt argues that stateful function-calling environments interleave developer schemas, structured arguments, and untrusted tool outputs in shared context, creating a surface beyond plain prompts. ^[raw/papers/beyond-the-prompt-function-calling-jailbreak-2026.md]

**Design implication:** Test schema/tool-output manipulation separately from user-prompt jailbreaks.

### Persistent memory authority failures

Louck’s memory-poisoning paper argues that long-term memory creates cross-session authority problems: untrusted content stored in one session can later steer consequential actions. It specifically challenges content-based or lineage-only authority signals as malleable. ^[raw/papers/long-term-memory-poisoning-origin-bound-authority-2026.md]

**Design implication:** Memory entries need origin-bound authority, not merely a confidence score or sanitized summary.

### Claw-like agents as computer systems

The Claw-like agent paper treats always-on agents with persistent credentials, files, tools, and services through a computer-systems lens. The central warning is that cross-component failures can be more severe than model-output failures. ^[raw/papers/claw-like-agent-security-computer-systems-lens-2026.md]

**Design implication:** Model the agent runtime like an operating system boundary: skills/plugins/tools need isolation, ACLs, audit, and sandboxing.

### Defense training can degrade autonomy

The Autonomy Tax paper reports a capability-alignment paradox: defense training intended to improve prompt-injection safety can degrade tool-using multi-step competence. ^[raw/papers/autonomy-tax-defense-training-breaks-llm-agents-2026.md]

**Design implication:** Always measure benign task utility and timeout/failure rate alongside safety.

### Multi-turn operator-agent red teaming

NRT-Bench evaluates multi-turn red teaming of LLM operator agents in a simulated safety-critical control-room setting. It is relevant because attacks adapt over a dialogue, not a single prompt. ^[raw/papers/nrt-bench-multiturn-red-teaming-operator-agents-2026.md]

**Design implication:** Build attack sessions, not only isolated prompts; preserve turn-by-turn strategy and postconditions.

### Intent-gated and trajectory-level defenses

KAIJU proposes decoupling workflow execution from LLM reasoning via an executive kernel and intent-gated execution; Trajectory Guard proposes sequence-aware anomaly detection over agent action plans. These are defense leads, not settled solutions. ^[raw/papers/kaiju-intent-gated-execution-llm-agents-2026.md] ^[raw/papers/trajectory-guard-agentic-anomaly-detection-2026.md]

**Design implication:** The mitigation layer should reason over intents and trajectories outside the model, not merely add prompt reminders.

## Confidence and caveats

These are recent preprints. They are valuable leads, but not settled consensus. For project decisions, use them to design experiments and regressions, not as proof that a mitigation or attack generalizes across all agent runtimes.

Related: [[agentic-evaluation-planes]], [[tool-use-and-privilege-risk]], [[memory-and-rag-poisoning]], [[agent-red-team-methodology]].
