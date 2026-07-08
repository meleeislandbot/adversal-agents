---
title: Hermes-Orchestrated AI Council
created: 2026-07-05
updated: 2026-07-06
type: concept
tags: [adversal-agents, architecture, multi-agent, implementation, verification, evidence]
sources: [raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md, raw/articles/microsoft-pyrit-github-readme-current.md, raw/articles/agentdojo-github-readme.md]
confidence: medium
contested: false
contradictions: []
---

# Hermes-Orchestrated AI Council

## Core idea

Hermes should be the **user-facing orchestrator** for Adversal Agents, not the single model doing all reasoning. Its main value is communication and coordination: Telegram, Discord, desktop/CLI, project memory, wiki updates, process control, and durable session context. The heavy cognitive work can be delegated to a council of autonomous CLI workers such as [[cli-worker-backends]]. ^[raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md]

## Why this matters

The project’s cost and provider constraints make a pure API harness unattractive. Some subscriptions are only usable through native tools such as Claude Code or Codex CLI. Therefore, Adversal Agents should treat each CLI as an **executable worker** rather than trying to force every provider into Hermes as an API-backed profile.

## Proposed architecture

```text
Hermes
  ├── receives user requests from Telegram/Discord/CLI
  ├── creates a mission brief
  ├── launches council workers through adapters
  ├── monitors processes and rate/cost limits
  ├── collects artifacts, claims, objections, traces
  ├── updates the wiki / claim ledger
  └── returns synthesis and next decisions to the user

Council workers
  ├── Claude Code
  ├── Codex CLI
  ├── Gemini CLI or other native provider CLI
  ├── OpenCode
  ├── local models
  ├── deterministic verifiers
  └── human review when needed
```

## Design principle

Hermes is the **secretary general** and process supervisor. It should not pretend that its active model has the final say. The council should be structured so that independent workers generate, criticize, repair, and verify work through artifacts. See [[council-protocols-claims-and-objections]].

## Minimal run directory

```text
runs/<mission-id>/
├── brief.md
├── constraints.md
├── sources/
├── artifacts/
├── claims.jsonl
├── objections.jsonl
├── votes-or-status.jsonl
├── final.md
└── workers/
    ├── claude-code/output.md
    ├── codex-cli/output.md
    ├── gemini-cli/output.md
    └── opencode/output.md
```

## Non-goals

- Do not create one Hermes profile per provider as the primary architecture.
- Do not rely on consensus as truth.
- Do not make the human copy/paste outputs between agents.
- Do not require metered API calls for routine runs when subscription-native workers or local checks can do the job.

## Open questions

- Which worker adapters should be implemented first?
- How much process control should Hermes expose directly versus via a small `council run` CLI?
- What is the minimum artifact schema for a useful council run?
- Which messaging surfaces should receive progress updates versus final summaries only?

Related: [[cli-worker-backends]], [[council-protocols-claims-and-objections]], [[agent-red-team-methodology]], [[multi-agent-verification-failures]].

## Closed-worker limitation: no activation access

Anthropic's 2026 [[jacobian-lens-and-j-space]] work strengthens the reason to keep Adversal Agents evidence-led: a worker's written answer may omit internal recognition of prompt injection, evaluation setup, or strategic/deceptive considerations. For closed CLI workers this is mostly a limitation, because activation-level methods cannot be applied directly; for local/open workers it suggests a possible future white-box audit layer.
