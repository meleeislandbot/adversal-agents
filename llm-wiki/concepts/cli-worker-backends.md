---
title: CLI Worker Backends
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, implementation, architecture, tool-use, multi-agent]
sources: [raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md, raw/articles/local-one-shot-cli-inspection-2026-07-05.md, raw/articles/claude-code-cli-reference-and-env-excerpts-2026-07-05.md, raw/articles/codex-cli-noninteractive-auth-excerpts-2026-07-05.md, raw/articles/gemini-cli-headless-auth-excerpts-2026-07-05.md, raw/articles/opencode-cli-config-excerpts-2026-07-05.md]
confidence: medium
contested: false
contradictions: []
---

# CLI Worker Backends

## Definition

A CLI worker backend is an adapter that lets Adversal Agents run an external AI worker through its native command-line interface instead of calling a model API directly. Examples include Claude Code, Codex CLI, Gemini CLI, OpenCode, local model runners, and deterministic tools.

The key abstraction is:

```text
worker.run(task, context, constraints) -> artifacts + transcript + normalized result
```

not:

```text
llm.generate(prompt) -> text
```

## Why this abstraction is needed

Subscriptions and OAuth surfaces are uneven. Some provider subscriptions are not available as generic API access in third-party harnesses. A cost-aware system should therefore exploit official subscription-native tools where allowed, while preserving a common artifact protocol. ^[raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md]

## Worker contract

Every backend should normalize at least:

```json
{
  "worker_id": "claude-code",
  "role": "skeptic",
  "status": "completed | failed | timeout | rate_limited",
  "started_at": "...",
  "ended_at": "...",
  "duration_sec": 0,
  "input_files": [],
  "output_files": [],
  "transcript_path": "workers/claude-code/transcript.log",
  "claims_path": "workers/claude-code/claims.jsonl",
  "objections_path": "workers/claude-code/objections.jsonl",
  "cost_estimate": null,
  "rate_limit_observed": false,
  "error": null
}
```

## Adapter responsibilities

- Create an isolated workspace or worktree.
- Write a role-specific prompt and input artifacts.
- Launch the native CLI non-interactively when possible.
- Time out or pause long-running sessions safely.
- Capture stdout/stderr/transcripts.
- Collect changed files and artifacts.
- Normalize result status and metadata.
- Respect provider limits and official interfaces.
- Avoid leaking secrets into prompts or logs.

## Subscription-first policy

For routine council work, prefer this order:

1. deterministic checks and local scripts;
2. local or cheap models for mutation, clustering, and rough triage;
3. subscription-native CLI workers;
4. metered APIs only for promoted or ambiguous cases.

This connects directly to [[hermes-orchestrated-ai-council]] and prevents the project from becoming an uncontrolled API spending engine.

## One-shot execution layer

The first concrete implementation layer is documented in [[one-shot-cli-execution]] and [[one-shot-cli-worker-backends-comparison]]. Each adapter should prefer the CLI's native headless mode, capture JSON/JSONL when available, scrub API-key environment variables unless API spend is explicitly intended, and record exact command/version/auth route for auditability.

## Caveats

- A CLI worker is not just a model; it has its own hidden prompting, tools, memory/session behavior, permissions, and rate limits.
- Native CLIs may change output formats or auth behavior.
- Some tasks require PTY/tmux orchestration; simple one-shot print/exec modes should be preferred for reproducibility.
- Provider terms and official usage limits must be respected.

Related: [[hermes-orchestrated-ai-council]], [[red-team-tooling-and-frameworks]], [[agent-red-team-methodology]].
