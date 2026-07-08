---
title: Mitigations for Agentic Systems
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, security, safety, verification, tool-use, memory, implementation]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/papers/adaptive-attacks-break-ipi-defenses-2025.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/nist-generative-ai-profile-ai-600-1-pdf-text.md]
confidence: high
contested: false
contradictions: []
---

# Mitigations for Agentic Systems

## Framing

No single guardrail is enough for agent safety. Current evidence suggests layered defenses must be tested against adaptive attackers and measured against real postconditions. The practical goal is risk reduction plus traceable failure, not a claim of absolute prompt-injection immunity.

## Defense layers

1. **Authority separation:** keep system/developer instructions, user goals, untrusted content, tool output, and memory in distinct fields and traces.
2. **Least privilege:** tools and credentials scoped to user, task, time, and environment.
3. **External policy engine:** high-risk tool calls require checks outside the LLM.
4. **Sandboxing:** browser, shell, code execution, filesystem, and network isolated by default.
5. **Tool mediation:** validate parameters, rate-limit, require dry-run for destructive actions, and block unexpected tool chains.
6. **Memory governance:** provenance, confidence, TTL, quarantine, and human confirmation for durable writes.
7. **Untrusted-data handling:** retrieved content cannot directly authorize actions or modify goals.
8. **Adaptive HITL:** ask humans only for high-signal approvals; avoid flooding reviewers with low-value prompts.
9. **Traceability:** immutable logs, source provenance, memory diffs, and replayable test cases.
10. **Regression red teaming:** every fixed exploit becomes a test; defenses are re-evaluated after model/tool/prompt changes.

## What would change this page

Evidence that a particular defense family reliably survives adaptive black-box IPI across multiple agent environments would raise confidence in that defense. Current papers instead show meaningful bypasses and transferability, so this page treats defenses as composable controls rather than silver bullets. ^[raw/papers/adaptive-attacks-break-ipi-defenses-2025.md] ^[raw/papers/agentdojo-prompt-injection-agents-2024.md]

Related: [[tool-use-and-privilege-risk]], [[memory-and-rag-poisoning]], [[agent-red-team-methodology]].
