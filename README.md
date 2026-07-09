# Adversal Agents

Portable, agent-guided setup for red-teaming AI agents with multiple provider CLIs, local tools, reproducible traces, and cost controls.

The project assumes there will be a **Hermes coordinator profile**, but the repository cannot activate that profile by itself. The template at `profiles/hermes-redteam-coordinator/SOUL.md` only has effect after it is copied into the selected Hermes profile or installed by a setup step.

## Quick start for humans

Repository:

```text
https://github.com/meleeislandbot/adversal-agents
```

Copy the prompt below and paste it into the agent you want to use for the one-time setup.

## One-shot onboarding prompt

<!-- adversal-setup-prompt:start -->
```text
Read and follow this one-time setup guide exactly:
https://github.com/meleeislandbot/adversal-agents/blob/main/instructions.md

Ask me only when the instructions tell you to.
```
<!-- adversal-setup-prompt:end -->

## After onboarding

Once setup is complete, normal agents should use the project context files and **should not re-run onboarding** unless the user explicitly asks to set up a new environment.

## What this repo provides

```text
AGENTS.md                 # shared day-to-day project instructions for agents that support it
CLAUDE.md                 # Claude Code day-to-day entrypoint
GEMINI.md                 # Gemini CLI day-to-day entrypoint
.hermes.md                # Hermes project context
instructions.md           # one-time guided setup procedure for onboarding agents
profiles/                 # Hermes coordinator SOUL.md template; inert until installed/copied
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

- **Agent-first one-shot setup**, not manual installation docs.
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
