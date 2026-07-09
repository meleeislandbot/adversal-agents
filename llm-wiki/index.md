# Wiki Index

> Content catalog. Every wiki page is listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: 2026-07-09 | Total pages: 31

> **Note (2026-07-09):** the project pivoted from an agent red-team lab to a
> cold-iron mathematical verification council (see `docs/epistemics.md`). Most
> pages below are research from the earlier framing — treat them as background,
> not current objective. The pages that still apply directly are
> [[multi-agent-verification-failures]], [[memory-and-rag-poisoning]],
> [[council-protocols-claims-and-objections]], and the new
> [[cold-iron-verification]].

## Entities

- [[microsoft-pyrit]] — Microsoft open-source framework for generative-AI risk identification; useful for repeatable red-team orchestration.
- [[mitre-atlas]] — Adversarial AI tactics/techniques knowledge base for shared reporting vocabulary.
- [[owasp-agentic-security-initiative]] — Practitioner guidance and threat taxonomy for agentic AI systems.

## Concepts

- [[agent-attack-surface]] — Trust-boundary map for agent systems: inputs, tools, memory, RAG, inter-agent channels, humans, logs, and supply chain.
- [[agent-red-team-methodology]] — Reproducible workflow for agent red teaming with threat model, harness, traces, scoring, and regression.
- [[agent-safety-benchmarks]] — Benchmark portfolio covering AgentDojo, ToolEmu, AgentHarm, AgentVigil, adaptive IPI attacks, WildTeaming, SafeClawBench, SeClaw, and newer 2026 leads.
- [[agentic-evaluation-planes]] — Distinguishes semantic, audit-evidence, sandbox harm, concealment, utility preservation, and replayability.
- [[cli-worker-backends]] — Adapter abstraction for subscription-native CLI workers such as Claude Code, Codex CLI, Gemini CLI, OpenCode, local models, and deterministic tools.
- [[cold-iron-verification]] — Current project doctrine: model agreement is not truth; a claim is `proven` only via a proof-assistant kernel; the default is `not_established`.
- [[ai-agent-red-teaming]] — Umbrella synthesis: agent red teaming as whole-system adversarial evaluation, not prompt-only testing.
- [[council-protocols-claims-and-objections]] — Protocol for independent passes, cross-examination, claim ledgers, objection ledgers, repairs, and evidence-based synthesis.
- [[declared-project-workspace-and-shared-wiki]] — Project-root architecture where all CLI workers share a curated wiki and auto-loaded context files without total isolation.
- [[emerging-agent-threats-2026]] — Verified 2025–2026 frontier threats: STAC, R-DoS, function-calling context attacks, memory authority, Claw-like systems, and defense/trajectory leads.
- [[hermes-orchestrated-ai-council]] — Architecture where Hermes is the user-facing orchestrator coordinating autonomous CLI workers through artifacts and traces.
- [[indirect-prompt-injection]] — Attack class where malicious instructions arrive through external data the agent reads.
- [[jacobian-lens-and-j-space]] — Anthropic/Transformer Circuits 2026 interpretability work on J-space/global-workspace-like internal representations and its limits for Adversal Agents.
- [[memory-and-rag-poisoning]] — Persistent influence risks in memory, vector stores, retrieved documents, summaries, and shared state.
- [[one-shot-cli-execution]] — How to run subscription-native and local AI workers non-interactively from terminal CLIs with bounded cost and machine-readable traces.
- [[mitigations-for-agentic-systems]] — Layered controls: least privilege, sandboxing, policy engines, memory governance, HITL, logs, and regression.
- [[multi-agent-verification-failures]] — Failure modes in agent debate/verification: correlated errors, poisoned communication, false consensus, rogue delegation.
- [[prompt-injection-for-agents]] — Direct, indirect, plan, goal, tool-selection, and adaptive prompt injection against agentic systems.
- [[red-team-tooling-and-frameworks]] — Tools and frameworks: PyRIT, garak, AgentDojo, Inspect AI, MITRE ATLAS, OWASP, NIST, SAIF.
- [[tool-use-and-privilege-risk]] — How tool calls, credentials, code execution, browser actions, and tool selection turn language failures into side effects.

## Comparisons

- [[agent-red-team-benchmarks-comparison]] — Side-by-side comparison of AgentDojo, ToolEmu, AgentHarm, AgentVigil, adaptive IPI attacks, and WildTeaming.
- [[one-shot-cli-worker-backends-comparison]] — Practical comparison of Claude Code, Codex CLI, Gemini CLI, OpenCode, Hermes, and local runners as one-shot council workers.
- [[red-team-tools-comparison]] — Practical comparison of PyRIT, garak, AgentDojo, Inspect AI, MITRE ATLAS, and OWASP guidance.

## Queries

- [[hermes-council-architecture-discussion]] — Curated discussion note on using Hermes as orchestrator for a skeptical council of subscription-native CLI workers.
- [[initial-red-team-research-foundation]] — Executive synthesis and architecture recommendations for the first Adversal Agents research foundation.
- [[one-shot-cli-execution-research]] — Research note on one-shot terminal execution, auth/billing pitfalls, and first adapter priorities.
- [[workspace-architecture-research]] — Research note on declared project roots, shared wiki design, native context files, and worker isolation policy.
- [[anthropic-global-workspace-investigation]] — Investigation of Anthropic’s July 2026 global-workspace/Jacobian-lens announcement and implications for Adversal Agents.

## Meta / Catalogs

- `_meta/` — Project-local wiki metadata and maintenance notes.
- [[red-team-source-catalog]] — Catalog of the raw sources ingested for this initial red-team research pass.
