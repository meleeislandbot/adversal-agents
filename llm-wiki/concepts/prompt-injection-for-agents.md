---
title: Prompt Injection for Agents
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, red-teaming, security, tool-use, verification]
sources: [raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/adaptive-attacks-break-ipi-defenses-2025.md, raw/papers/toolhijacker-tool-selection-llm-agents-2025.md]
confidence: high
contested: false
contradictions: []
---

# Prompt Injection for Agents

## Definition

Prompt injection is an attack where adversarial text causes an LLM application to follow attacker-controlled instructions instead of its intended instructions. For agents, the risk is higher because injected instructions can steer planning, tool choice, API calls, memory writes, and inter-agent messages.

## Agent-specific variants

- **Direct prompt injection:** the user asks the agent to ignore policy, reveal secrets, or call tools unsafely.
- **Indirect prompt injection:** the malicious instruction arrives through untrusted context such as a website, document, email, tool result, or retrieved memory. See [[indirect-prompt-injection]].
- **Plan/goal injection:** the attacker alters subgoals or planning criteria, causing gradual drift rather than an obvious policy break.
- **Tool-description injection:** malicious tool metadata or tool documents bias retrieval/selection toward attacker-controlled tools; ToolHijacker targets this exact stage. ^[raw/papers/toolhijacker-tool-selection-llm-agents-2025.md]
- **Defense-adaptive injection:** the attack is crafted against the known defense, which is why static filters tend to overstate security. ^[raw/papers/adaptive-attacks-break-ipi-defenses-2025.md]

## Evidence

Greshake et al. argued that LLM-integrated applications blur data and instruction boundaries and demonstrated attacks that remotely influence applications by placing prompts in likely-to-be-retrieved data. AgentDojo operationalizes this risk for agents with tools over untrusted data, using realistic tasks such as email, banking, and travel booking plus hundreds of security test cases. ^[raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md] ^[raw/papers/agentdojo-prompt-injection-agents-2024.md]

## Design implication

Adversal Agents should treat prompt injection as an **environment-level exploit**, not a string-classification problem. A robust test case should include the injected artifact, the benign user task, the available tools, the expected safe trace, and a postcondition such as “no email sent,” “no secret appears in outgoing request,” or “malicious tool is not selected.”

## Mitigation directions

- Isolate trusted instructions from untrusted data in separate fields and logs.
- Require tool-call policies outside the model, not just natural-language reminders.
- Run adaptive attack regressions after adding any defense.
- Use independent verifiers to inspect candidate tool calls and final effects.
- Treat detection as defense-in-depth, not proof of safety.

Related: [[agent-attack-surface]], [[agent-safety-benchmarks]], [[mitigations-for-agentic-systems]].
