---
title: Red Team Source Catalog
created: 2026-07-05
updated: 2026-07-05
type: summary
tags: [adversal-agents, research, prior-art, evidence]
sources: [raw/papers/red-teaming-language-models-with-language-models-2022.md, raw/papers/indirect-prompt-injection-llm-integrated-applications-2023.md, raw/papers/agentdojo-prompt-injection-agents-2024.md, raw/papers/toolemu-risks-of-lm-agents-2023.md, raw/papers/agentharm-benchmark-llm-agents-2024.md, raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md, raw/papers/stac-tool-chain-jailbreak-llm-agents-2025.md, raw/papers/safeclawbench-tool-using-agent-security-2026.md, raw/papers/long-term-memory-poisoning-origin-bound-authority-2026.md]
confidence: medium
contested: false
contradictions: []
---

# Red Team Source Catalog

## Ingested source groups

### Agent-specific empirical work

- AgentDojo — dynamic environment for IPI attacks/defenses against LLM agents.
- ToolEmu — LM-emulated tools for high-stakes risk discovery.
- AgentHarm — harmful multi-step tasks for LLM agents.
- Adaptive Attacks Break Defenses — robustness warning for IPI defenses.
- AgentVigil — black-box fuzzing for IPI against agents.
- ToolHijacker — prompt injection against tool retrieval/selection.

### Model-level red teaming background

- Red Teaming Language Models with Language Models — automated LM red teaming.
- Universal and Transferable Adversarial Attacks on Aligned LLMs — transferable jailbreak-style optimization.
- WildTeaming — mining in-the-wild jailbreak tactics for red-team generation.

### Verified 2025–2026 frontier leads

- STAC — sequential tool attack chaining where individually harmless calls compose into harmful operations.
- OTora — reasoning-level denial of service for tool-augmented agents.
- Beyond the Prompt — function-calling/shared-context jailbreak surface.
- SafeClawBench — semantic vs audit-evidence vs sandbox harm.
- SeClaw — spec-driven security task synthesis.
- Long-term memory poisoning / origin-bound authority — persistent memory as a cross-session attack surface.
- Autonomy Tax — defense training can degrade multi-step agent competence.
- NRT-Bench — multi-turn red teaming for safety-critical operator agents.
- Claw-like agent security — always-on agents as computer-system-like runtimes.
- KAIJU and Trajectory Guard — architectural/trajectory-level defense leads.

### Practitioner/security frameworks

- OWASP LLM Top 10 and Agentic AI Threats and Mitigations.
- NIST AI RMF and Generative AI Profile.
- MITRE ATLAS.
- Google SAIF.

### Tools and repositories

- Microsoft PyRIT.
- NVIDIA garak.
- AgentDojo repository.
- UK AISI Inspect AI docs.

## Caveat

Some raw web sources are extracted from HTML and may include navigation noise. The PDF and arXiv raw notes are stronger provenance for specific claims.

Related: [[ai-agent-red-teaming]], [[red-team-tooling-and-frameworks]], [[agent-safety-benchmarks]].
