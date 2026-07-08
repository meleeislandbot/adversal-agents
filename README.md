# Adversal Agents

Portable, agent-guided setup for red-teaming AI agents with multiple provider CLIs, local tools, reproducible traces, and cost controls.

The project is intentionally **profile-agnostic** at the repository level: there is no required official Hermes profile. For serious work, however, we recommend a dedicated Hermes coordinator profile using `profiles/hermes-redteam-coordinator/SOUL.md`.

## Quick start for humans

Repository:

```text
https://github.com/meleeislandbot/adversal-agents
```

Paste the single setup prompt from:

```text
prompts/setup.md
```

The prompt tells the agent to open/clone the repo if needed and then follow:

```text
instructions.md
```

The setup is guided and incremental: the agent checks one thing at a time, fixes safe missing pieces itself, and only stops for decisions, login, credentials, cost risk, sudo, destructive actions, or global configuration changes.

## What this repo provides

```text
AGENTS.md                 # shared project instructions for agents that support it
CLAUDE.md                 # Claude Code entrypoint
.hermes.md                # Hermes project context
instructions.md           # guided setup procedure for agents
prompts/setup.md          # the single copy/paste setup prompt
profiles/                 # optional Hermes coordinator SOUL.md template
.adversal/                # project-local control plane
  project.yaml            # manifest and policy defaults
  scenarios/              # red-team scenario registry
  ledgers/                # claims, objections, decisions, budget records
  workers/                # worker catalog and readiness status
  templates/              # run/report/status templates
  runs/                   # generated run traces, ignored by git except .gitkeep
llm-wiki/                 # curated research wiki and source notes
scripts/                  # read-only diagnostics and small setup helpers
docs/                     # architecture, maintenance, release, and profile docs
```

## Design principles

- **Agent-first setup**, not manual documentation.
- **Guided flow**, not a giant final error report.
- **Project-local state** in `.adversal/`; avoid hidden chat memory as the source of truth.
- **Subscription/local first**; metered APIs require explicit approval.
- **Deterministic scoring first**; LLM judges only for ambiguity.
- **Trace everything**: prompts, tool calls, outputs, verdicts, budget and auth route.
- **Provider CLIs are workers**, not coordinator profiles.
- **Professional maintenance**: versioned, reviewed, validated, and release-managed.

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

## Professional maintenance

This repository uses:

- Semantic Versioning via `VERSION`;
- release history in `CHANGELOG.md`;
- Conventional Commits;
- branch + pull request workflow for non-trivial changes;
- repository validation via `make validate`;
- GitHub Actions validation on pushes and pull requests.

See:

- `CONTRIBUTING.md`
- `docs/repository-maintenance.md`
- `docs/release-process.md`
- `docs/hermes-coordinator-profile.md`

## Current status

This is an early project scaffold. The existing `llm-wiki/` contains the research foundation for agent red teaming, benchmarks, threat surfaces, worker architecture, and cost-aware orchestration.
