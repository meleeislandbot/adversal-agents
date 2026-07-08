# Adversal Agents — Guided Setup Instructions for AI Agents

This document is written for AI agents, not humans.

Your job is to configure this repository for agent red-teaming workflows while minimizing user burden, avoiding surprise cost, and preserving auditable project state.

## Non-negotiable operating model

Use **guided incremental setup**.

Do **not** run a huge diagnostic and wait until the end to report all missing items.

Instead, for each setup area:

1. State the area you are checking in one short sentence.
2. Run the smallest useful check.
3. If ready, continue.
4. If missing but safe/non-critical, fix it and continue.
5. If user decision or risk is involved, stop and ask the user immediately.
6. Record durable project state in `.adversal/`.

## What counts as user-risk

Stop and ask before any action involving:

- selecting providers/workers;
- login, browser auth, or device-code flows;
- credentials, API keys, tokens, or secrets;
- paid/metered API usage;
- environment variables that may force paid API usage;
- `sudo` or elevated permissions;
- global configuration changes outside this repository;
- shell profile edits;
- background services/daemons;
- destructive commands or overwrites;
- real external side effects such as sending messages, opening PRs, modifying remote services, making purchases, or touching production systems.

## What you may do without asking

You may proceed without asking for:

- read-only diagnostics;
- checking OS, shell, git, package managers, and CLI versions;
- creating missing project-local folders under `.adversal/`;
- creating empty project-local ledgers and templates;
- writing run artifacts under `.adversal/runs/<run-id>/`;
- installing a user-selected CLI only if the install is clearly non-elevated, non-destructive, and does not require secrets or paid API usage;
- running harmless local dry-run scenarios with no external side effects.

When in doubt, ask.

## Setup phases

### Phase 0 — Announce guided mode

Tell the user briefly:

- you will proceed step by step;
- you will only stop for decisions, login, cost, credentials, sudo, global changes, destructive actions, or external side effects;
- safe project-local setup will be handled automatically.

Then continue; do not wait for confirmation unless the user has not selected a project root.

### Phase 1 — Confirm project root

Check current directory.

A valid root should contain at least one of:

- `instructions.md`
- `AGENTS.md`
- `.adversal/project.yaml`
- `llm-wiki/index.md`
- `.git/`

If uncertain, ask:

> I may not be in the project root. Should I use this directory as the Adversal Agents project root?

Do not continue until root ambiguity is resolved.

### Phase 2 — Project-local structure

Check for and create missing project-local structure:

```text
.adversal/
.adversal/artifacts/
.adversal/ledgers/
.adversal/runs/
.adversal/scenarios/
.adversal/templates/
.adversal/tmp/
.adversal/workers/
llm-wiki/
```

Create missing ledger files without overwriting existing ones:

```text
.adversal/ledgers/claims.jsonl
.adversal/ledgers/objections.jsonl
.adversal/ledgers/decisions.jsonl
.adversal/ledgers/budget.jsonl
```

If `llm-wiki/` is missing, create only a minimal `llm-wiki/index.md` and explain that research context can be added later.

### Phase 3 — Ask for worker/provider choices

Ask the user which worker backends they want to enable.

Offer these choices:

- Claude Code
- Codex CLI
- Gemini CLI
- OpenCode
- local models / Ollama
- deterministic-only mode
- metered APIs

Warn concisely:

- subscription-native CLIs are preferred for cost control;
- metered APIs can incur charges;
- API-key environment variables may override subscription login in some tools.

Do not configure provider-specific workers until the user chooses.

### Phase 4 — Verify selected workers one by one

For each selected worker, use this pattern:

1. Check whether the CLI exists.
2. If missing and safe to install, install it using the official or platform-standard method.
3. Re-check version.
4. Check whether auth/login appears ready, if the CLI exposes a safe check.
5. Check whether environment variables may force API-key/metered usage.
6. If login or cost-sensitive choice is needed, stop and ask immediately.
7. Append/update `.adversal/workers/status.md`.
8. Append a budget/auth note to `.adversal/ledgers/budget.jsonl`.

Never print secret values. Only say whether a relevant variable exists.

#### Claude Code

Check:

```bash
claude --version
```

Cost/auth hazards to check by presence only:

```text
ANTHROPIC_API_KEY
ANTHROPIC_AUTH_TOKEN
```

If `ANTHROPIC_API_KEY` is present, warn that Claude Code automation may use API-key billing instead of subscription login unless the environment is scrubbed.

Recommended automation posture: subscription-native CLI, with API-key variables scrubbed unless the user explicitly approves API mode.

#### Codex CLI

Check:

```bash
codex --version
```

Cost/auth hazards to check by presence only:

```text
OPENAI_API_KEY
CODEX_API_KEY
```

If API keys are present, warn that Codex may use metered API billing depending on auth/config route.

#### Gemini CLI

Check:

```bash
gemini --version
```

Cost/auth hazards to check by presence only:

```text
GOOGLE_API_KEY
GEMINI_API_KEY
GOOGLE_APPLICATION_CREDENTIALS
```

Do not assume Gemini is subscription-free until the auth route is verified.

#### OpenCode

Check:

```bash
opencode --version
```

OpenCode is a provider-routed harness. It is not automatically subscription-native. Inspect project-local config first, then global config only with permission if needed.

#### Local models / Ollama

Check:

```bash
ollama --version
ollama list
```

Local models are preferred for cheap mutation, clustering, deduplication, and rough classification. Do not download large models without asking.

#### Deterministic-only mode

No provider login is required. Enable local scenario validation, trace schema checks, file/postcondition checks, and budget ledger checks.

#### Metered APIs

Do not enable by default. Ask for explicit approval for each provider route and record it in `.adversal/ledgers/decisions.jsonl` and `.adversal/ledgers/budget.jsonl`.

### Phase 5 — Initialize or verify scenario registry

Ensure `.adversal/scenarios/index.md` exists.

Start with safe local scenarios only:

1. direct prompt-injection refusal/containment;
2. indirect prompt injection via a local untrusted text file;
3. tool permission boundary dry run;
4. memory/RAG poisoning simulation with no persistent global memory writes;
5. reasoning/cost DoS simulation with strict local budget limits.

Do not run real external side-effect tests during setup.

### Phase 6 — Run a harmless dry run

Create a timestamped run directory:

```text
.adversal/runs/<YYYYMMDD-HHMMSS>-dry-run/
```

Save:

```text
prompt.md
trace.md
verdict.md
budget.json
```

The dry run must:

- avoid external side effects;
- avoid real credentials;
- avoid paid APIs unless already approved;
- use deterministic checks if no worker is ready;
- produce a clear pass/fail/inconclusive verdict.

### Phase 7 — Final readiness summary

Only after the incremental setup is complete, give a short summary:

- project root;
- ready workers;
- workers needing login/user action;
- disabled workers;
- cost risks;
- files created/changed;
- recommended first real red-team scenario.

Keep it short. The detailed record belongs in `.adversal/`.

## Recommended command helpers

You may use the read-only helper:

```bash
python3 scripts/adversal_doctor.py --json
```

It checks local tool availability and risk-relevant environment-variable presence without printing secret values.

Use it as a supplement, not as a replacement for guided setup. If it reveals a blocking issue, stop at that point and guide the user.
