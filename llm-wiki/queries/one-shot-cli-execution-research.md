---
title: One-Shot CLI Execution Research
created: 2026-07-05
updated: 2026-07-05
type: query
tags: [adversal-agents, research, implementation, tool-use, architecture]
sources: [raw/articles/local-one-shot-cli-inspection-2026-07-05.md, raw/articles/claude-code-cli-reference-and-env-excerpts-2026-07-05.md, raw/articles/codex-cli-noninteractive-auth-excerpts-2026-07-05.md, raw/articles/gemini-cli-headless-auth-excerpts-2026-07-05.md, raw/articles/opencode-cli-config-excerpts-2026-07-05.md, raw/articles/local-model-cli-excerpts-ollama-llama-cpp-2026-07-05.md]
confidence: medium
contested: false
contradictions: []
---

# One-Shot CLI Execution Research

## Research question

How should Adversal Agents run AI workers one-shot from terminal CLIs so Hermes can orchestrate a skeptical council without manual copy-paste or uncontrolled API spend?

## Findings

1. The right abstraction is **CLI worker backend**, not model provider. See [[cli-worker-backends]].
2. Claude Code, Codex CLI, Gemini CLI, and OpenCode all expose non-interactive/headless entrypoints, but their auth and billing semantics differ.
3. Machine-readable output exists for the main candidates: Claude Code JSON/stream-JSON, Codex JSONL, Gemini JSON/stream-JSON, OpenCode JSON.
4. Subscription-first automation requires environment hygiene. In particular, Claude Code docs say `ANTHROPIC_API_KEY` overrides subscription login, and Codex docs say API-key auth uses standard API pricing.
5. Local models should sit at the cheap end of the funnel, not replace frontier workers.

## Recommendation

Build the first Council Runner around three adapters:

```text
codex-cli adapter   -> best initial automation surface
claude-code adapter -> strongest subscription-aware reviewer/skeptic
local adapter       -> cheap triage/mutation path
```

Then add Gemini CLI once headless subscription behavior is empirically verified. Add OpenCode when a specific provider route is chosen and budgeted.

## Proposed next experiment

Create a tiny `runs/smoke-one-shot/` workspace with a harmless prompt that asks each worker to write a structured JSON file from a local `brief.md`. Run:

- no external network except provider auth/model call;
- no secrets in environment;
- strict timeouts;
- JSON/JSONL capture;
- no API-key variables unless deliberately testing API path.

The experiment should record whether each CLI can run unattended, what output schema is stable, whether usage stats are visible, and whether subscription/auth route is preserved.

Related: [[one-shot-cli-execution]], [[one-shot-cli-worker-backends-comparison]], [[hermes-orchestrated-ai-council]], [[council-protocols-claims-and-objections]].
