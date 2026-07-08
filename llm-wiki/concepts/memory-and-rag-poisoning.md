---
title: Memory and RAG Poisoning
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, memory, security, risk, hallucination, provenance]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/articles/owasp-llm-top-10-2025.md, raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md, raw/papers/long-term-memory-poisoning-origin-bound-authority-2026.md]
confidence: high
contested: false
contradictions: []
---

# Memory and RAG Poisoning

## Definition

Memory and RAG poisoning occur when an attacker introduces false, malicious, or policy-bypassing content into state that the agent will later retrieve or trust. This can affect short-term scratchpads, long-term memories, vector stores, document corpora, summaries, caches, and inter-agent shared state.

## Agent-specific concern

OWASP lists memory poisoning as a distinct agentic threat and notes that RAG can introduce knowledge poisoning, hallucination amplification, and indirect prompt injection. The problem is persistence: one malicious artifact can influence many future tasks, users, or agents. ^[raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]

A 2026 memory-security paper sharpens the issue: persistent memory creates an authority problem, because untrusted content stored in one session can steer consequential actions in later sessions; content-only and lineage-only authority signals are themselves malleable. ^[raw/papers/long-term-memory-poisoning-origin-bound-authority-2026.md]

## Attack patterns

- Poison a document that is likely to be retrieved for a benign task.
- Induce the agent to save an attacker instruction as a durable “preference” or “fact.”
- Poison summaries so later agents inherit a distorted version of evidence.
- Insert high-similarity vector chunks that override authoritative sources.
- Use multi-agent communication to propagate a false belief into shared memory.

## Design implication

Adversal Agents should never treat memory as neutral context. Memory writes require provenance, source trust, expiration, confidence, and authorization. Memory reads should preserve source identity in the trace so a verifier can distinguish user instruction, system policy, tool output, and retrieved data.

## Controls to evaluate

- Quarantine memory created from untrusted content.
- Require explicit confirmation before persistent memory writes.
- Attach source, timestamp, actor, confidence, and authority scope to every memory item.
- Use permission-aware retrieval: the agent should not retrieve content the acting user cannot access.
- Run poisoning regressions that verify whether a poisoned item influences future tool calls.
- Separate evidence stores from preference stores.
- Treat origin-bound authority as a requirement for any memory item that can authorize future action.

Related: [[indirect-prompt-injection]], [[multi-agent-verification-failures]], [[mitigations-for-agentic-systems]], [[emerging-agent-threats-2026]].
