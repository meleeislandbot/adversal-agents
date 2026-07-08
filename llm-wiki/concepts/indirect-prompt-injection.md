---
title: Indirect Prompt Injection
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, red-teaming, security, tool-use, risk]
sources: [raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/agentvigil-black-box-ipi-red-teaming-2025.md, raw/papers/adaptive-attacks-break-ipi-defenses-2025.md]
confidence: high
contested: false
contradictions: []
---

# Indirect Prompt Injection

## Definition

Indirect prompt injection (IPI) occurs when an attacker cannot directly prompt the agent, but places instructions in data the agent later reads: a webpage, email, document, repository issue, search result, retrieved vector chunk, or tool response.

## Why it matters for agents

IPI is the canonical agent red-team problem because the agent’s job is often to consume external data and then act. Greshake et al. describe impacts including data theft, worming, information ecosystem contamination, API manipulation, and behavior control. AgentDojo focuses precisely on agents executing tools over untrusted data. ^[raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md] ^[raw/papers/agentdojo-prompt-injection-agents-2024.md]

## Attack pattern

1. User gives benign task: “summarize this webpage,” “process my inbox,” “book travel.”
2. Agent retrieves untrusted content containing hidden or explicit attacker instructions.
3. Model confuses content with instruction and alters plan or tool calls.
4. Tool execution causes harm: exfiltration, unauthorized action, malicious navigation, memory poisoning, or user manipulation.
5. Logs may look superficially normal unless the trace preserves source provenance.

## Current evidence on defenses

The evidence is not reassuring. Zhan et al. report bypassing eight IPI defenses with adaptive attacks and achieving consistently >50% attack success. AgentVigil proposes black-box fuzzing with MCTS-based seed selection and reports strong success rates on AgentDojo and VWA-adv, plus transferability across unseen tasks and internal LLMs. These results imply defenses should be evaluated against adaptive black-box attackers, not only canned payloads. ^[raw/papers/adaptive-attacks-break-ipi-defenses-2025.md] ^[raw/papers/agentvigil-black-box-ipi-red-teaming-2025.md]

## Red-team checklist

- Does untrusted content ever enter the same context window as privileged instructions?
- Are tool outputs labeled and traced to source?
- Can the agent call external communication tools after reading untrusted content?
- Can hidden text, HTML comments, markdown links, or document metadata steer behavior?
- Are memory writes allowed from untrusted context?
- Does the verifier check actual postconditions or only the final answer?

Related: [[prompt-injection-for-agents]], [[memory-and-rag-poisoning]], [[agent-red-team-methodology]].
