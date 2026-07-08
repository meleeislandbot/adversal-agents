---
title: Red Team Tooling and Frameworks
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, red-teaming, llm-evaluation, benchmark, tool-use, implementation]
sources: [raw/articles/microsoft-pyrit-github-readme-current.md, raw/articles/garak-llm-vulnerability-scanner.md, raw/articles/agentdojo-github-readme.md, raw/articles/uk-aisi-inspect-ai-docs.md, raw/articles/mitre-atlas.md, raw/articles/google-secure-ai-framework.md, raw/articles/nist-ai-risk-management-framework.md]
confidence: medium
contested: false
contradictions: []
---

# Red Team Tooling and Frameworks

## Tool categories

- **Attack orchestration:** [[microsoft-pyrit]] helps security professionals and engineers proactively identify generative-AI risks through repeatable orchestration.
- **Broad vulnerability scanning:** garak probes LLM/dialog systems for hallucination, leakage, prompt injection, misinformation, toxicity, jailbreaks, and related weaknesses. ^[raw/articles/garak-llm-vulnerability-scanner.md]
- **Agent-specific benchmark harnesses:** AgentDojo provides realistic tool-use tasks and prompt-injection security tests. ^[raw/articles/agentdojo-github-readme.md]
- **Evaluation framework:** UK AISI Inspect AI is a framework for defining and running model evaluations with scoring.
- **Threat knowledge base:** [[mitre-atlas]] catalogs adversarial tactics and techniques against AI systems.
- **Governance/security frameworks:** NIST AI RMF/GAI Profile, OWASP GenAI/Agentic Security, and Google SAIF provide control language and lifecycle framing.

## Adversal Agents integration idea

Use these tools as components, not replacements for project-specific tests:

1. garak/PyRIT for broad initial probes and attack generation.
2. AgentDojo/ToolEmu/AgentHarm-style harnesses for agentic effect testing.
3. Inspect-style task definitions for reproducibility.
4. MITRE/OWASP/NIST as taxonomy and reporting vocabulary.
5. Custom verifier agents to inspect traces, source provenance, and postconditions.

## Gap

Most general LLM red-team tools test model outputs. Adversal Agents needs first-class support for state transitions: tool calls, permissions, memory writes, browser actions, code execution, and inter-agent messages.

Related: [[agent-red-team-methodology]], [[red-team-tools-comparison]], [[agent-safety-benchmarks]].
