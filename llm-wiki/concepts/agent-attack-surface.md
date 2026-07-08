---
title: Agent Attack Surface
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, agentic-ai, security, risk, tool-use, memory, architecture]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/articles/owasp-llm-top-10-2025.md, raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md]
confidence: high
contested: false
contradictions: []
---

# Agent Attack Surface

## Map

An agent attack surface is broader than a prompt box. For Adversal Agents, model the system as a set of trust boundaries:

1. **Direct user input** — normal prompts, files, images, URLs, and multimodal instructions.
2. **Untrusted external context** — web pages, email, issue trackers, documents, calendar entries, databases, and tool results.
3. **System/developer instructions** — policy hierarchy, hidden prompts, task constraints, and planner instructions.
4. **Tool registry and schemas** — tool descriptions, names, parameters, examples, and retrieval-based tool selection.
5. **Tool execution layer** — APIs, browser, shell, code interpreter, payment systems, messaging, filesystem, and credentials.
6. **Memory/RAG state** — vector stores, summaries, episodic memory, scratchpads, long-term preferences, and cached plans.
7. **Inter-agent communication** — delegation messages, shared blackboards, debate transcripts, supervisor/worker channels.
8. **Human approval surface** — confirmation prompts, dashboards, notifications, fatigue, and social trust.
9. **Logs/provenance** — traces, audit records, attribution, tamper-resistance, and secret redaction.
10. **Supply chain** — model weights, plugins, MCP/A2A servers, packages, prompts, datasets, and deployment config.

OWASP’s agentic threat model specifically highlights memory poisoning, tool misuse, privilege compromise, cascading hallucinations, goal manipulation, repudiation, identity spoofing, unexpected code execution, agent communication poisoning, rogue agents, insecure inter-agent protocol abuse, and supply-chain compromise. ^[raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]

## Red-team implication

Every red-team scenario should specify: **entry point**, **trust boundary crossed**, **asset at risk**, **agent capability abused**, **expected safe behavior**, and **observable postcondition**. Without postconditions, the red team degenerates into prompt anecdotes.

## Related pages

- [[prompt-injection-for-agents]] covers the instruction/data boundary.
- [[tool-use-and-privilege-risk]] covers action amplification and confused-deputy failures.
- [[memory-and-rag-poisoning]] covers persistence and retrieval surfaces.
- [[multi-agent-verification-failures]] covers communication and consensus surfaces.
