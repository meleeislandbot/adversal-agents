---
title: Agent Red Team Benchmarks Comparison
created: 2026-07-05
updated: 2026-07-05
type: comparison
tags: [adversal-agents, benchmark, llm-evaluation, red-teaming, comparison]
sources: [raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/agentharm-benchmark-llm-agents-2024.md, raw/papers/agentvigil-black-box-ipi-red-teaming-2025.md, raw/papers/adaptive-attacks-break-ipi-defenses-2025.md, raw/papers/wildteaming-at-scale-2024.md, raw/papers/safeclawbench-tool-using-agent-security-2026.md, raw/papers/seclaw-spec-driven-security-task-synthesis-2026.md, raw/papers/nrt-bench-multiturn-red-teaming-operator-agents-2026.md, raw/papers/otora-reasoning-dos-llm-agents-2026.md]
confidence: high
contested: false
contradictions: []
---

# Agent Red Team Benchmarks Comparison

## Comparison

| Benchmark / method | Main target | Strength | Limitation for Adversal Agents |
|---|---|---|---|
| AgentDojo | IPI attacks/defenses for tool-using agents | Realistic tasks, 629 security test cases, extensible environment | Focused on selected suites; project still needs custom tools and policies |
| ToolEmu | Risk discovery using LM-emulated tools | Lowers cost of testing high-stakes tools; finds long-tail failures | Emulated execution must be validated against real tool behavior |
| AgentHarm | Harmful multi-step agent misuse | Tests refusal plus capability retention after jailbreak | Malicious-task taxonomy may not cover enterprise workflow abuse |
| AgentVigil | Black-box IPI fuzzing | Adaptive seed optimization, transferability | Needs integration into controlled harness to measure actual side effects |
| Adaptive IPI attacks | Defense robustness | Directly tests defenses under adaptive attackers | Abstract-level result; defense details must be replicated before relying on numbers |
| WildTeaming | Model jailbreak tactic mining | Broad in-the-wild seed diversity | Not agent-specific; must be converted into tool/memory scenarios |
| SafeClawBench | Tool-using agent harm staging | Separates semantic, audit-evidence, and sandbox harm | New benchmark; needs local reproduction before adopting its labels wholesale |
| SeClaw | Spec-driven agent security task synthesis | Converts specifications into stateful agent security tasks | Depends on quality and coverage of the spec |
| NRT-Bench | Multi-turn operator-agent red teaming | Tests adaptive pressure in safety-critical control-room setting | Domain-specific simulation; not a general enterprise agent benchmark |
| OTora | Reasoning-level DoS | Captures latency/cost/tool-budget availability attacks | Availability-oriented; not a confidentiality/integrity benchmark |

## Synthesis

Adversal Agents should combine static benchmark suites with adaptive red-team generation. The foundation should be an internal registry where each scenario stores: attack family, benchmark inspiration, tool/memory surfaces used, postcondition, severity, and regression status.

Related: [[agent-safety-benchmarks]], [[agent-red-team-methodology]], [[prompt-injection-for-agents]], [[agentic-evaluation-planes]].
