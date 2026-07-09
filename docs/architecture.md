# Architecture

Adversal Agents is a source repository for configuring project-local orchestration patterns for red-teaming AI agents.

```text
configured Hermes coordinator profile
        |
        v
target project root with .hermes.md / AGENTS.md / CLAUDE.md / GEMINI.md
        |
        v
.adversal control plane copied from templates/project/.adversal/
        |
        +--> worker backends: Claude Code, Codex CLI, Gemini, OpenCode, local models, deterministic tools
        |
        +--> traces, ledgers, scenario registry, budget records
        |
        v
curated llm-wiki
```

## Source repo vs instantiated project

The source repository keeps versioned bootstrap assets under `templates/project/`.

An instantiated Adversal project stores live runtime state under its own `.adversal/` directory. The source repository should not track live `.adversal/` ledgers, run directories, temporary artifacts, or worker status generated during experiments.

## Coordinator

The coordinator is the user's selected Hermes profile after it has been configured with the Adversal `SOUL.md`, required toolsets, and required skills. The repository copy of `profiles/hermes-redteam-coordinator/SOUL.md` is only a template until installed into that profile.

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
