---
title: Agent Safety Benchmarks
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, benchmark, llm-evaluation, red-teaming, security, risk]
sources: [raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/agentharm-benchmark-llm-agents-2024.md, raw/papers/agentvigil-black-box-ipi-red-teaming-2025.md, raw/papers/adaptive-attacks-break-ipi-defenses-2025.md, raw/papers/wildteaming-at-scale-2024.md, raw/papers/safeclawbench-tool-using-agent-security-2026.md, raw/papers/seclaw-spec-driven-security-task-synthesis-2026.md, raw/papers/nrt-bench-multiturn-red-teaming-operator-agents-2026.md, raw/papers/how-vulnerable-ai-agents-ipi-competition-2026.md]
confidence: high
contested: false
contradictions: []
---

# Agent Safety Benchmarks

## Benchmarks and methods to track

- **AgentDojo:** dynamic environment for prompt-injection attacks and defenses for LLM agents; 97 realistic tasks, 629 security test cases, attacks and defenses, and released code. ^[raw/papers/agentdojo-prompt-injection-agents-2024.md]
- **ToolEmu:** LM-emulated sandbox for testing agents over high-stakes tools without implementing each environment; 36 tools and 144 test cases in the initial benchmark. ^[raw/papers/toolemu-risks-of-lm-agents-2023.md]
- **AgentHarm:** benchmark for harmful multi-step agent tasks; 110 malicious tasks, 440 with augmentations, across 11 harm categories. ^[raw/papers/agentharm-benchmark-llm-agents-2024.md]
- **AgentVigil:** black-box red-teaming/fuzzing framework for indirect prompt injection; reports high success on AgentDojo and VWA-adv and transferability across unseen tasks and LLMs. ^[raw/papers/agentvigil-black-box-ipi-red-teaming-2025.md]
- **Adaptive IPI attacks:** evaluates defenses under adaptive attacks and reports bypassing eight defenses with >50% success. ^[raw/papers/adaptive-attacks-break-ipi-defenses-2025.md]
- **WildTeaming:** mines in-the-wild jailbreak interactions and composes tactics for automated safety red teaming; useful for attack-seed diversity, though it is not agent-specific. ^[raw/papers/wildteaming-at-scale-2024.md]
- **SafeClawBench:** separates semantic, audit-evidence, and sandbox harm for tool-using agents; useful for avoiding prompt-only safety metrics. ^[raw/papers/safeclawbench-tool-using-agent-security-2026.md]
- **SeClaw:** spec-driven task synthesis for evaluating autonomous agents in stateful environments with tools, files, memory, and services. ^[raw/papers/seclaw-spec-driven-security-task-synthesis-2026.md]
- **NRT-Bench:** multi-turn red-teaming benchmark for LLM operator agents in safety-critical control-room simulations. ^[raw/papers/nrt-bench-multiturn-red-teaming-operator-agents-2026.md]
- **Large-scale IPI competition:** evaluates indirect prompt injection against agents processing external data and foregrounds concealment as a critical dimension. ^[raw/papers/how-vulnerable-ai-agents-ipi-competition-2026.md]

## Evaluation dimensions

| Dimension | Why it matters |
|---|---|
| Benign task success | A defense that blocks the agent from doing useful work is not enough. |
| Attack success | Did the adversary cause the unsafe postcondition? |
| Capability retention | After jailbreak, can the agent still execute the multi-step task? |
| Tool-call safety | Were tool calls authorized, scoped, and validated? |
| Traceability | Can the failure be replayed and attributed? |
| Adaptivity | Does the defense survive attacks optimized against it? |
| Transferability | Does the attack generalize to unseen tasks/models/tools? |
| Harm plane | Was the failure only semantic, visible in audit evidence, or realized in sandbox state? |
| Concealment | Did the final user-visible response hide compromise? |
| Cost/availability | Did the attack inflate latency, reasoning tokens, or tool budget? |

## Design implication

Adversal Agents should not pick one benchmark as ground truth. Use a **benchmark portfolio**: model-level jailbreak breadth, agentic tool-use tasks, IPI scenarios, harmful multi-step tasks, and project-specific regression cases.

Related: [[agent-red-team-methodology]], [[agent-red-team-benchmarks-comparison]], [[red-team-tooling-and-frameworks]], [[agentic-evaluation-planes]], [[emerging-agent-threats-2026]].
