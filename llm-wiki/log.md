# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: create, ingest, update, query, lint, archive, delete
> When this file exceeds 500 entries, rotate: rename to `log-YYYY.md`, start fresh.

## [2026-07-05] create | Project research wiki initialized

- Location: `/Users/ia/Documents/Adversal Agents/llm-wiki`.
- Domain: Adversal Agents research, prior art, design decisions, evidence, and evaluation methods.
- Structure created with `SCHEMA.md`, `index.md`, `log.md`, `raw/`, `entities/`, `concepts/`, `comparisons/`, `queries/`, `_meta/`, and `_archive/`.

## [2026-07-05] ingest | Initial AI agent red-team research foundation

- Ingested raw academic and practitioner sources on agent red teaming, prompt injection, tool use, memory/RAG poisoning, benchmarks, and tooling.
- Created concepts: `ai-agent-red-teaming.md`, `agent-attack-surface.md`, `prompt-injection-for-agents.md`, `indirect-prompt-injection.md`, `tool-use-and-privilege-risk.md`, `memory-and-rag-poisoning.md`, `agent-red-team-methodology.md`, `agent-safety-benchmarks.md`, `multi-agent-verification-failures.md`, `mitigations-for-agentic-systems.md`, `red-team-tooling-and-frameworks.md`.
- Created entities: `owasp-agentic-security-initiative.md`, `microsoft-pyrit.md`, `mitre-atlas.md`.
- Created comparisons: `agent-red-team-benchmarks-comparison.md`, `red-team-tools-comparison.md`.
- Created query synthesis: `initial-red-team-research-foundation.md`.
- Created meta catalog: `_meta/red-team-source-catalog.md`.
- Updated `index.md`.
- Corrected NIST source paths in concept frontmatter after write verification.
- Added `comparison` to the schema tag taxonomy because comparison pages use it.

## [2026-07-05] update | Verified asynchronous red-team research leads

- Verified all arXiv IDs surfaced by the async subagents before integration.
- Ingested 13 additional raw paper notes covering STAC, OTora, function-calling context jailbreaks, SafeClawBench, SeClaw, long-term memory poisoning, Claw-like agent security, NRT-Bench, KAIJU, Trajectory Guard, Autonomy Tax, and the Prompt Report.
- Created concepts: `emerging-agent-threats-2026.md`, `agentic-evaluation-planes.md`.
- Updated: `agent-safety-benchmarks.md`, `agent-red-team-methodology.md`, `tool-use-and-privilege-risk.md`, `memory-and-rag-poisoning.md`, `agent-red-team-benchmarks-comparison.md`, `initial-red-team-research-foundation.md`, `_meta/red-team-source-catalog.md`, and `index.md`.
- Did not integrate unverified subagent-only numeric claims beyond what was visible in verified arXiv metadata/abstracts.

## [2026-07-05] update | Hermes-orchestrated CLI council architecture

- Captured current project discussion as `raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md`.
- Created concepts: `hermes-orchestrated-ai-council.md`, `cli-worker-backends.md`, `council-protocols-claims-and-objections.md`.
- Created query note: `hermes-council-architecture-discussion.md`.
- Updated `initial-red-team-research-foundation.md` and `index.md`.
- Core decision captured: Hermes should be the user-facing orchestrator while autonomous CLI workers perform independent work, cross-critique, and artifact-based verification.

## [2026-07-05] ingest | One-shot CLI execution research

- Inspected local CLI availability and help without running model prompts.
- Verified one-shot/headless command surfaces against official Claude Code, Codex CLI, Gemini CLI, OpenCode, Ollama, and llama.cpp documentation.
- Created raw sources: `local-one-shot-cli-inspection-2026-07-05.md`, `claude-code-cli-reference-and-env-excerpts-2026-07-05.md`, `codex-cli-noninteractive-auth-excerpts-2026-07-05.md`, `gemini-cli-headless-auth-excerpts-2026-07-05.md`, `opencode-cli-config-excerpts-2026-07-05.md`, and `local-model-cli-excerpts-ollama-llama-cpp-2026-07-05.md`.
- Created concept: `one-shot-cli-execution.md`.
- Created comparison: `one-shot-cli-worker-backends-comparison.md`.
- Created query note: `one-shot-cli-execution-research.md`.
- Updated `cli-worker-backends.md` and `index.md`.
- Key finding: subscription-first workers require environment hygiene; API-key variables can silently switch native CLIs onto metered billing paths.

## [2026-07-05] update | One-shot CLI variables and session summarization

- Updated `concepts/one-shot-cli-execution.md` with backend-specific environment/config variables for Claude Code, Codex CLI, Gemini CLI, and OpenCode.
- Added session/resume/summarization guidance: summaries are useful handoff artifacts but should not replace raw traces, claim ledgers, objections, postconditions, and cited evidence.

## [2026-07-05] update | Claude Code model flag for one-shot workers

- Updated `concepts/one-shot-cli-execution.md` to capture that Claude Code supports `--model <alias-or-full-name>` before starting a one-shot task.
- Added examples with `--model sonnet`, `--model opus --effort high`, and full model names; noted that `--model` overrides `ANTHROPIC_MODEL` for the session.

## [2026-07-06] query | Project workspace and shared wiki architecture

- Investigated native project-context mechanisms across Hermes, Claude Code, Codex CLI, Gemini CLI, and OpenCode.
- Created raw source: `raw/articles/project-workspace-context-file-research-2026-07-06.md`.
- Created concept: `concepts/declared-project-workspace-and-shared-wiki.md`.
- Created query note: `queries/workspace-architecture-research.md`.
- Updated `index.md`.
- Design recommendation: require a user-declared project root, use `AGENTS.md` as a small portable entrypoint, maintain a shared `llm-wiki/` as curated memory, and launch all workers from the project root so native context discovery works without repeating instructions in each prompt.

## [2026-07-06] ingest | Anthropic global workspace / Jacobian lens research

- Investigated X announcement `https://x.com/AnthropicAI/status/2074185348142280912?s=20`.
- Created raw sources: `raw/articles/anthropic-x-global-workspace-announcement-2026-07-06.md`, `raw/articles/anthropic-global-workspace-research-page-2026-07-06.md`, `raw/papers/gurnee-et-al-global-workspace-language-models-2026.md`, and `raw/articles/anthropics-jacobian-lens-repository-2026-07-06.md`.
- Created concept: `concepts/jacobian-lens-and-j-space.md`.
- Created query note: `queries/anthropic-global-workspace-investigation.md`.
- Updated `SCHEMA.md`, `index.md`, `concepts/agentic-evaluation-planes.md`, and `concepts/hermes-orchestrated-ai-council.md`.
- Design implication: hidden model cognition can diverge from output; J-lens is relevant as a future white-box audit signal for open/local workers, but not directly usable on closed subscription CLI workers without activation access.
