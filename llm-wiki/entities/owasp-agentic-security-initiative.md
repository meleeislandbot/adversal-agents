---
title: OWASP Agentic Security Initiative
created: 2026-07-05
updated: 2026-07-05
type: entity
tags: [adversal-agents, security, risk, red-teaming, prior-art]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations.md, raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/articles/owasp-llm-top-10-2025.md]
confidence: high
contested: false
contradictions: []
---

# OWASP Agentic Security Initiative

## Overview

The OWASP Agentic Security Initiative produces guidance for agentic AI threats and mitigations. Its February 2025 guide frames agentic AI around planning/reasoning, memory/statefulness, action/tool use, and multi-agent architecture, then maps a reference threat model and taxonomy. ^[raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]

## Relevance to Adversal Agents

OWASP’s agentic threat taxonomy is the best initial backbone for this wiki’s [[agent-attack-surface]] page. It provides threat names that are immediately useful for red-team scenario tagging: memory poisoning, tool misuse, privilege compromise, cascading hallucination, goal manipulation, repudiation, identity spoofing, overwhelming HITL, unexpected code execution, agent communication poisoning, rogue agents, protocol abuse, and supply-chain compromise.

## Caveat

OWASP guidance is a practitioner framework, not empirical proof of exploit prevalence. It should be combined with benchmark evidence from [[agent-safety-benchmarks]] and reproducible tests from [[agent-red-team-methodology]].
