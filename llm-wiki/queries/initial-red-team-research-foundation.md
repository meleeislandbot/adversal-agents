---
title: Initial Red Team Research Foundation
created: 2026-07-05
updated: 2026-07-05
type: query
tags: [adversal-agents, research, red-teaming, agentic-ai, evidence, open-question]
sources: [raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/agentharm-benchmark-llm-agents-2024.md, raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/articles/microsoft-pyrit-github-readme-current.md, raw/articles/garak-llm-vulnerability-scanner.md]
confidence: high
contested: false
contradictions: []
---

# Initial Red Team Research Foundation

## Executive synthesis

The strongest conclusion from this initial research is that agent red teaming must be **system red teaming**. The model is one component; the exploit path usually crosses untrusted data, planning, tools, credentials, memory, and human approval. The key project direction for Adversal Agents is therefore to build a traceable adversarial evaluation harness rather than a prompt-only judge.

## Foundational claims

1. **Prompt injection is the gateway risk, but not the whole risk.** It becomes agentic when it changes plans, tool calls, memory writes, or inter-agent messages. See [[prompt-injection-for-agents]] and [[indirect-prompt-injection]].
2. **Tools amplify impact.** ToolEmu, AgentDojo, and AgentHarm all point toward evaluating side effects and multi-step execution, not just harmful text. See [[tool-use-and-privilege-risk]].
3. **Defenses are brittle under adaptivity.** Adaptive attack papers and AgentVigil suggest fixed filters and static prompts should be treated as defense-in-depth only. See [[agent-safety-benchmarks]].
4. **Memory and RAG turn one attack into persistent influence.** Poisoning, provenance, and expiration must be first-class. See [[memory-and-rag-poisoning]].
5. **Multi-agent verification is promising but dangerous.** It can improve coverage but also launder weak evidence into consensus. See [[multi-agent-verification-failures]].

## Initial architecture recommendation

Build Adversal Agents around five roles:

- **Scenario designer:** converts threat taxonomy into runnable tasks.
- **Attacker:** generates direct, indirect, adaptive, and tool-aware attacks.
- **Executor:** runs the target agent in a sandbox with instrumented tools.
- **Verifier:** checks postconditions, policy compliance, provenance, and evidence.
- **Triage reporter:** assigns severity and creates regression tests.

The harness, not the LLM, should enforce permissions, collect traces, and decide whether a test passed based on observable postconditions. The current favored orchestration pattern is [[hermes-orchestrated-ai-council]] with [[cli-worker-backends]] and [[council-protocols-claims-and-objections]].

## Verified follow-up from asynchronous research

A later subagent batch surfaced newer 2025–2026 papers. I verified the arXiv records before integrating them. The main additions are: sequential tool attack chaining, reasoning-level DoS, function-calling shared-context jailbreaks, persistent memory authority, Claw-like agent security, staged harm planes, spec-driven task synthesis, and multi-turn operator-agent red teaming. See [[emerging-agent-threats-2026]] and [[agentic-evaluation-planes]].

## Priority next questions

- What target agent runtime will Adversal Agents test first?
- Which tools will be in scope: browser, shell, email, filesystem, GitHub, payments, cloud APIs?
- What is the minimum trace schema for replay and audit?
- Should the first benchmark clone AgentDojo-style IPI tasks, ToolEmu-style emulated tools, or project-specific workflows?
- How will the project avoid leaking secrets while preserving useful failure evidence?

## Key pages to read next

- [[ai-agent-red-teaming]]
- [[agent-attack-surface]]
- [[agent-red-team-methodology]]
- [[agent-safety-benchmarks]]
- [[mitigations-for-agentic-systems]]
