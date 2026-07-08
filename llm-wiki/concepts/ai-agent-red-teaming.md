---
title: AI Agent Red Teaming
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, red-teaming, agentic-ai, security, risk, verification, evidence]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/agentharm-benchmark-llm-agents-2024.md, raw/papers/nist-generative-ai-profile-ai-600-1-pdf-text.md]
confidence: high
contested: false
contradictions: []
---

# AI Agent Red Teaming

## Definition

**AI agent red teaming** is adversarial testing of an LLM system that can plan, use tools, retain state, call APIs, browse, execute code, or coordinate with other agents. It differs from chatbot red teaming because the failure condition is often not a bad answer, but an unauthorized **action**, unsafe tool chain, poisoned memory, data exfiltration, or a trace that cannot be attributed after the fact. OWASP frames agentic systems around planning/reasoning, memory/statefulness, action/tool use, and multi-agent communication; those capabilities are exactly the red-team surface. ^[raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]

## Core thesis for Adversal Agents

Red teaming agents must evaluate the **whole control loop**: instructions, retrieved context, memory, tool registry, credentials, runtime sandbox, human approvals, logs, and recovery. A model-level refusal benchmark is necessary but insufficient: AgentHarm shows that agentic misuse requires testing whether a model both refuses malicious multi-step tasks and retains enough capability after jailbreak to execute them. AgentDojo and ToolEmu show that external tools and untrusted data change the risk profile even when the underlying LLM appears safe. ^[raw/papers/agentharm-benchmark-llm-agents-2024.md] ^[raw/papers/agentdojo-prompt-injection-agents-2024.md] ^[raw/papers/toolemu-risks-of-lm-agents-2023.md]

## What is well-supported

- The dominant agent-specific weakness is **instruction/data boundary collapse**: untrusted data can be interpreted as operational instruction, especially through retrieved documents, email, websites, tool output, memory, or inter-agent messages. See [[prompt-injection-for-agents]] and [[indirect-prompt-injection]].
- Tool use creates impact amplification: a jailbreak or injected subgoal can become API calls, email sends, payments, code execution, browser navigation, or data movement. See [[tool-use-and-privilege-risk]].
- Existing prompt-injection defenses are not robust against adaptive attackers; one 2025 paper reports bypassing eight defenses with adaptive attacks and >50% attack success. See [[agent-safety-benchmarks]]. ^[raw/papers/adaptive-attacks-break-ipi-defenses-2025.md]
- A red-team program should be dynamic and regression-based rather than a one-time checklist: AgentDojo is explicitly an extensible environment; PyRIT and garak are reusable attack/evaluation frameworks; NIST frames generative AI risk management as lifecycle governance, mapping, measurement, and management. See [[agent-red-team-methodology]] and [[red-team-tooling-and-frameworks]].

## Working assumptions

- The best initial architecture for Adversal Agents is not “one judge LLM decides truth.” It is a controlled adversarial process: attacker agents generate candidate failures, defender/verifier agents inspect traces and evidence, and a harness enforces permissions, scoring, and reproducibility.
- A useful red team should produce **evidence artifacts**: prompts, retrieved data, tool-call traces, policy decisions, model outputs, postconditions, and replay scripts.
- Consensus between agents is weak evidence unless their context, prompts, tools, and failure modes are sufficiently independent. See [[multi-agent-verification-failures]].

## Open questions

- How much of adversarial generation should be automated by LLM attackers versus seeded by human red-teamers?
- Which defenses remain effective under adaptive, tool-aware, black-box attackers?
- What minimal trace schema lets future agents reproduce a failure without leaking secrets?
- How should Adversal Agents rank severity: policy violation, real-world impact, exploit reliability, or ease of remediation?
