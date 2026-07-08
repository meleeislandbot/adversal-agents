# Adversal Agents

Portable, agent-guided setup for red-teaming AI agents with multiple provider CLIs, local tools, reproducible traces, and cost controls.

The project is intentionally **profile-agnostic**: there is no required "official" Hermes coordinator profile. The coordinator is whichever agent the user opens in this repository — Hermes, Claude Code, Codex, Gemini, OpenCode, or another capable agent.

## Quick start for humans

Repository:

```text
https://github.com/meleeislandbot/adversal-agents
```

If the repo is already cloned/open, paste the prompt from:

```text
prompts/copy-paste-setup.md
```

If the repo is not cloned yet, paste the URL bootstrap prompt from:

```text
prompts/bootstrap-from-url.md
```

The agent should then follow:

```text
instructions.md
```

Raw instructions URL:

```text
https://raw.githubusercontent.com/meleeislandbot/adversal-agents/main/instructions.md
```

The setup is guided and incremental: the agent checks one thing at a time, fixes safe missing pieces itself, and only stops for decisions, login, credentials, cost risk, sudo, destructive actions, or global configuration changes.

## What this repo provides

```text
AGENTS.md                 # persistent project instructions for agents
instructions.md           # guided setup procedure for agents
prompts/                  # copy/paste prompts for users
.adversal/                # project-local control plane
  project.yaml            # manifest and policy defaults
  scenarios/              # red-team scenario registry
  ledgers/                # claims, objections, decisions, budget records
  workers/                # worker catalog and readiness status
  templates/              # run/report/status templates
  runs/                   # generated run traces, ignored by git except .gitkeep
llm-wiki/                 # curated research wiki and source notes
scripts/                  # read-only diagnostics and small setup helpers
```

## Design principles

- **Agent-first setup**, not manual documentation.
- **Guided flow**, not a giant final error report.
- **Project-local state** in `.adversal/`; avoid hidden chat memory as the source of truth.
- **Subscription/local first**; metered APIs require explicit approval.
- **Deterministic scoring first**; LLM judges only for ambiguity.
- **Trace everything**: prompts, tool calls, outputs, verdicts, budget and auth route.
- **Provider CLIs are workers**, not coordinator profiles.

## Safety and cost policy

By default, setup must not:

- use paid/metered APIs;
- write API keys or secrets;
- modify global configs;
- run `sudo`;
- install background services;
- perform real external side effects;
- overwrite existing project files.

The agent may create missing project-local folders/files and run read-only diagnostics without interrupting the user.

## Current status

This is an early project scaffold. The existing `llm-wiki/` contains the research foundation for agent red teaming, benchmarks, threat surfaces, worker architecture, and cost-aware orchestration.
