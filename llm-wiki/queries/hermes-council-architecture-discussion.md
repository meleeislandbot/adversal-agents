---
title: Hermes Council Architecture Discussion
created: 2026-07-05
updated: 2026-07-05
type: query
tags: [adversal-agents, research, architecture, multi-agent, implementation, open-question]
sources: [raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md]
confidence: medium
contested: false
contradictions: []
---

# Hermes Council Architecture Discussion

## Synthesis

This discussion established a project-level architectural direction: use Hermes as the communication and orchestration layer, while a council of native CLI workers performs the heavy adversarial and research work. The system should avoid manual copy-paste between models and should not depend on metered API calls for routine execution.

## Key decisions currently favored

- Hermes remains the user-facing interface through Telegram, Discord, desktop/CLI, and wiki updates.
- Provider-specific reasoning work should be delegated to native CLIs when that is the only or best way to use subscriptions.
- The correct abstraction is [[cli-worker-backends]], not a single generic LLM provider interface.
- Council operation should follow [[council-protocols-claims-and-objections]]: independent first pass, cross-examination, repair, verification, synthesis.
- The project should preserve skepticism between workers and avoid majority-vote epistemology.

## Riemann example as design probe

The user described a real workflow where a non-mathematician uses Codex and Claude sequentially for a project around the Riemann hypothesis. The workflow’s useful insight is cross-model critique. Its failure mode is that the human becomes the manual message bus, and each model receives the other’s framing without a structured claim ledger.

For mathematical work, the council should produce proof obligations, objections, formalization targets, and literature checks. It should not declare extreme mathematical success based on model agreement.

## Red-team relevance

The same architecture applies to agent red teaming. Instead of asking models whether a prompt is dangerous, workers should produce and attack scenarios, traces, invariants, postconditions, and regressions. The council becomes useful when it makes disagreements explicit and ties conclusions to artifacts.

## Open design questions

- Should the first implementation be a small standalone `council run` CLI invoked by Hermes, or a Hermes plugin/toolset?
- Which worker should be integrated first: Claude Code, Codex CLI, OpenCode, Gemini CLI, or local model runner?
- What is the minimal JSONL schema for claims and objections?
- How much progress should be streamed back to Telegram/Discord versus only final summaries?
- What guardrails are needed so CLI workers have autonomy without shared-workspace contamination?

Related: [[hermes-orchestrated-ai-council]], [[cli-worker-backends]], [[council-protocols-claims-and-objections]].
