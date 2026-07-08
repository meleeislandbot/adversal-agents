---
title: Tool Use and Privilege Risk
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, tool-use, security, risk, architecture, verification]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/toolhijacker-tool-selection-llm-agents-2025.md, raw/papers/agentharm-benchmark-llm-agents-2024.md, raw/papers/stac-tool-chain-jailbreak-llm-agents-2025.md, raw/papers/beyond-the-prompt-function-calling-jailbreak-2026.md, raw/papers/claw-like-agent-security-computer-systems-lens-2026.md]
confidence: high
contested: false
contradictions: []
---

# Tool Use and Privilege Risk

## Core risk

Tools transform language failures into real actions. OWASP identifies tool misuse, privilege compromise, identity spoofing, unexpected remote-code/code attacks, and supply-chain compromise as agentic threats. It also highlights the confused-deputy problem: an agent with broader privileges than the user can be tricked into acting on the attacker’s behalf. ^[raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]

## Failure modes

- **Over-broad credentials:** one agent token can read/write more than the user or task needs.
- **Unsafe tool chaining:** individually permitted calls compose into prohibited behavior; STAC makes this an explicit multi-turn attack family. ^[raw/papers/stac-tool-chain-jailbreak-llm-agents-2025.md]
- **Tool selection manipulation:** malicious or poisoned tool metadata causes the model to pick an attacker-controlled tool. ^[raw/papers/toolhijacker-tool-selection-llm-agents-2025.md]
- **Code execution:** generated code runs with ambient filesystem, network, or shell permissions; Claw-like always-on agents intensify this because skills/plugins/tools can resemble privileged OS components. ^[raw/papers/claw-like-agent-security-computer-systems-lens-2026.md]
- **Browser abuse:** agent navigates to malicious URLs, leaks session data, or performs unauthorized transactions.
- **Capability retention after jailbreak:** AgentHarm emphasizes that an agentic jailbreak matters if the model still completes multi-step harmful tasks after policy bypass. ^[raw/papers/agentharm-benchmark-llm-agents-2024.md]

## Evidence

ToolEmu uses LM-emulated tools to lower the cost of testing high-stakes scenarios and reports that 68.8% of failures identified by its framework would be valid real-world agent failures; even the safest LM agent in its evaluation had severe failures 23.9% of the time according to its evaluator. ^[raw/papers/toolemu-risks-of-lm-agents-2023.md]

## Design implication

Adversal Agents should score tool risk by **effect**, not by prompt text. The key question is: what state changed? A red-team harness should capture requested tool call, allowed policy, executed call, external side effect, and rollback/containment result.

## Mitigations to test

- Per-tool, per-user least privilege and short-lived credentials.
- Policy engine outside the LLM for high-risk actions.
- Pre-execution validation plus postcondition checks.
- Sandboxed code and browser contexts with network/file limits.
- Explicit tool-call budgets and rate limits.
- Deny tool access after reading untrusted content unless the action is low-risk or separately approved.

Related: [[agent-attack-surface]], [[mitigations-for-agentic-systems]], [[agent-safety-benchmarks]], [[emerging-agent-threats-2026]].
