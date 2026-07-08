# Adversal Agents

Portable, agent-guided setup for red-teaming AI agents with multiple provider CLIs, local tools, reproducible traces, and cost controls.

The project is intentionally **profile-agnostic** at the repository level: there is no required official Hermes profile. For serious work, however, we recommend a dedicated Hermes coordinator profile using `profiles/hermes-redteam-coordinator/SOUL.md`.

## Quick start for humans

Repository:

```text
https://github.com/meleeislandbot/adversal-agents
```

Copy the prompt below and paste it into the agent you want to use for the one-time setup.

## One-shot onboarding prompt

<!-- adversal-setup-prompt:start -->
```markdown
Use the Adversal Agents repository as the project root and follow `instructions.md` as the authoritative one-time guided setup procedure.

If the repository is not local yet, clone or open:
https://github.com/meleeislandbot/adversal-agents

Then continue from the repository root.

Operating rules:
- This is onboarding. Run it once, then record what was configured.
- Work step by step. Do not wait until the end to report all missing items.
- For each setup area: check it, fix safe non-critical gaps yourself, then continue.
- Stop and ask me only for real decisions or risk: provider/worker selection, login or device-code flow, credentials/secrets, metered API usage, sudo/elevated permissions, global config changes, destructive commands, background services, overwriting existing files, or external side effects.
- If a selected CLI is missing and can be installed safely without sudo, secrets, paid API usage, shell-profile edits, or background services, install it and continue.
- Prefer deterministic checks, local tools, local models, and subscription-native CLIs before metered APIs.
- Do not use paid APIs unless I explicitly approve that specific route.
- Keep project state under `.adversal/` and curated knowledge under `llm-wiki/`.
- Save traces, worker status, decisions, objections, budget notes, and final readiness as files. Do not rely on chat memory as the project record.

Start now in read-only discovery mode, then guide me through the minimum decisions needed to initialize the project.
```
<!-- adversal-setup-prompt:end -->

## After onboarding

Once setup is complete, normal agents should use the project context files and **should not re-run onboarding** unless the user explicitly asks to set up a new environment.

## What this repo provides

```text
AGENTS.md                 # shared day-to-day project instructions for agents that support it
CLAUDE.md                 # Claude Code day-to-day entrypoint
.hermes.md                # Hermes project context
instructions.md           # one-time guided setup procedure for onboarding agents
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
