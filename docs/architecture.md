# Architecture

Adversal Agents is a project-local orchestration pattern for red-teaming AI agents.

```text
user's active agent/profile
        |
        v
project root with AGENTS.md / CLAUDE.md / .hermes.md
        |
        v
.adversal control plane
        |
        +--> worker backends: Claude Code, Codex CLI, Gemini, OpenCode, local models, deterministic tools
        |
        +--> traces, ledgers, scenario registry, budget records
        |
        v
curated llm-wiki
```

## Coordinator

The coordinator is whichever agent the user opens in the repo. No special central profile is required.

## Workers

Workers are executable surfaces, not abstract model endpoints. A worker can be:

- a subscription-native CLI;
- a local model/tool;
- a deterministic checker;
- a metered API route, explicitly approved;
- a human review step.

## Evidence flow

1. Scenario definition.
2. Worker execution.
3. Trace capture.
4. Deterministic scoring.
5. Optional verifier/judge for ambiguity.
6. Ledger update.
7. Curated wiki update only when accepted.
