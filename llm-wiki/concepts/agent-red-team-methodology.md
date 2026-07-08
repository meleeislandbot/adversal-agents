---
title: Agent Red Team Methodology
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, red-teaming, llm-evaluation, benchmark, evidence, implementation]
sources: [raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/nist-generative-ai-profile-ai-600-1-pdf-text.md, raw/articles/microsoft-pyrit-github-readme-current.md, raw/articles/garak-llm-vulnerability-scanner.md, raw/papers/safeclawbench-tool-using-agent-security-2026.md, raw/papers/seclaw-spec-driven-security-task-synthesis-2026.md, raw/papers/otora-reasoning-dos-llm-agents-2026.md]
confidence: high
contested: false
contradictions: []
---

# Agent Red Team Methodology

## Principle

Agent red teaming should be a reproducible experiment, not a collection of scary prompts. A useful run has a threat model, controlled environment, attacker strategy, expected safe behavior, evidence trace, severity rubric, and regression outcome.

## Workflow

1. **Scope the system:** model, prompts, tools, credentials, memory, RAG, users, data, and deployment environment.
2. **Draw trust boundaries:** map [[agent-attack-surface]] and classify untrusted data sources.
3. **Define assets and harms:** secrets, money movement, account actions, code execution, reputation, compliance, user manipulation.
4. **Choose attack families:** direct injection, [[indirect-prompt-injection]], tool misuse, memory poisoning, malicious tool metadata, privilege escalation, multi-agent poisoning.
5. **Build a harness:** deterministic task setup, mock or sandboxed tools, trace capture, and postcondition scoring.
6. **Generate attacks:** human seeds plus automated attackers/fuzzers; include adaptive attacks against known defenses.
7. **Run baseline and defended agents:** measure task utility without attack and safety under attack; AgentDojo explicitly warns that agents can fail benign tasks even before attacks. ^[raw/papers/agentdojo-prompt-injection-agents-2024.md]
8. **Triage by effect:** classify whether harm is semantic, audit-evidence, or sandbox-realized; then score unauthorized action, data leak, policy violation, persistence, exploit reliability, blast radius, concealment, and remediation cost. See [[agentic-evaluation-planes]].
9. **Patch and regress:** add failing cases to a living suite; re-run after prompt, model, tool, or policy changes.
10. **Preserve evidence:** prompts, retrieved content, memory diffs, tool calls, model outputs, evaluator decisions, and environment version.

## Tooling fit

- Use [[microsoft-pyrit]] for orchestrated generative-AI risk identification flows.
- Use garak for broad LLM/dialog vulnerability probes before deeper agent-specific harnesses.
- Use AgentDojo-style environments for IPI + tools.
- Use Inspect AI-style task definitions when evaluation needs reproducibility and scoring.
- Use NIST AI RMF/GAI Profile as governance structure: govern, map, measure, manage.

## Minimal trace schema

- task id, user goal, safety policy, model/version, tool set/version;
- trusted instructions and untrusted artifacts separated;
- attacker payload and source;
- plan steps, tool-call requests, policy decisions, executed calls;
- memory reads/writes;
- final answer and external side effects;
- cost/latency/tool-budget usage for availability attacks;
- scorer verdict, harm plane, concealment rating, and severity.

Related: [[ai-agent-red-teaming]], [[agent-safety-benchmarks]], [[red-team-tooling-and-frameworks]], [[agentic-evaluation-planes]], [[emerging-agent-threats-2026]].
