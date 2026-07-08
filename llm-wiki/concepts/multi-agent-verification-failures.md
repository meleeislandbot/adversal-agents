---
title: Multi-Agent Verification Failures
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, multi-agent, verification, debate, consensus, hallucination, risk]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/papers/red-teaming-language-models-with-language-models-2022.md, raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md]
confidence: medium
contested: false
contradictions: []
---

# Multi-Agent Verification Failures

## Why this matters

Adversal Agents is likely to use multiple agents for adversarial generation, verification, debate, or review. Multi-agent structure can improve coverage, but it also creates failure modes: correlated hallucination, shared poisoned context, persuasive but false consensus, inter-agent prompt injection, rogue agents, and untraceable delegation chains.

## Failure modes

- **Correlated model failure:** agents using similar base models, prompts, or evidence make the same mistake.
- **Context contamination:** one compromised agent sends poisoned instructions or summaries to others.
- **Consensus laundering:** weak evidence appears stronger because several agents repeat it.
- **Authority inversion:** a worker agent’s untrusted output is treated as a supervisor instruction.
- **Rogue delegation:** an agent delegates outside allowed scope or to an untrusted tool/agent.
- **Cascading hallucination:** OWASP describes inaccurate information reinforced through memory, tools, or multi-agent interactions, disrupting later decisions. ^[raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]
- **Repudiation:** actions cannot be traced to a source because parallel agent paths lack immutable logs.

## Design implication

Multi-agent verification should be adversarial and evidence-centered. A verifier agent must inspect source artifacts and tool traces, not merely judge another agent’s prose. Consensus is useful only when agents have independent evidence paths and the system preserves dissent.

## Controls

- Separate roles: attacker, executor, verifier, evidence auditor, severity scorer.
- Give verifiers read-only access unless action is explicitly required.
- Preserve each agent’s input, output, tool calls, and source citations.
- Require claims to cite raw evidence or reproducible traces.
- Randomize or diversify models/prompts where independence matters.
- Add a “dissent channel” in final synthesis: unresolved disagreement is a result, not a failure.

Related: [[ai-agent-red-teaming]], [[memory-and-rag-poisoning]], [[mitigations-for-agentic-systems]].
