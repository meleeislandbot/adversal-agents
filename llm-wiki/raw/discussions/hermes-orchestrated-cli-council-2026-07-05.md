---
source_url: chat://current-session
ingested: 2026-07-05
sha256: 8c73bc16add22548c69371794414a14d784e3e11965b47c38a33a4c464d1ca0d
source_type: discussion
---

# Discussion: Hermes-Orchestrated CLI Council

Date: 2026-07-05
Source: project conversation with user.

## User constraints and insight

- Hermes should remain the comfortable communication layer because it already connects to Telegram, Discord, and other messaging surfaces.
- The project should not create one Hermes profile per model/provider. Some providers do not expose OAuth in a way Hermes can use directly, and some subscriptions are only usable through native surfaces.
- To use subscription value, the system should call official/native CLIs where appropriate: Claude through Claude Code, OpenAI/Codex through Codex CLI, potentially Gemini CLI, OpenCode, and similar tools.
- The user wants a "council" of CLI-based AIs doing the work: autonomous enough to think and act, but skeptical of each other.
- The council should not be a fragile interactive manual relay. Workers should run independently, leave artifacts, critique each other, and communicate through structured outputs.
- Motivation example: the user's brother is exploring a project around the Riemann hypothesis by manually moving work between Codex and Claude. This shows the value of cross-model critique, but the current method is inefficient because the human becomes the message bus.

## Assistant synthesis accepted for wiki curation

- Hermes should be the orchestrator/social interface, not the only reasoning engine.
- The right abstraction is a worker backend, not a model provider. A worker can be Claude Code, Codex CLI, Gemini CLI, OpenCode, a local model, deterministic tooling, or a human.
- Use rounds rather than manual ping-pong: independent first pass, cross-examination, repair/defense, external verification, and synthesis.
- The central unit should be claims, objections, artifacts, traces, postconditions, and invariants — not unstructured essays or chat transcripts.
- The council should not be democratic. Evidence, reproducible tests, formal checks, and valid objections beat majority vote.
- For mathematical work, especially extreme claims such as work around Riemann, the system should produce proof obligations and identify gaps rather than declare proof success.
- For red teaming agents, the same pattern maps to scenarios, trajectories, postconditions, sandbox evidence, and regressions.
