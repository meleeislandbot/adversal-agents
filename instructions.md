# Adversal Agents — Guided Setup Instructions for AI Agents

This document is written for AI agents. It is the one-time setup guide for turning an existing Hermes profile plus a chosen project directory into an Adversal Agents red-team harness.

Do not assume that cloning this repository makes anything active. Most files in this repository are instructions, templates, or research assets. Files only affect a harness when they are placed where that harness actually reads them, installed as Hermes skills, or explicitly executed.

## Non-negotiable operating model

Use **guided incremental setup**.

Do **not** run a huge diagnostic and wait until the end to report all missing items. For each setup area:

1. State the area you are checking in one short sentence.
2. Run the smallest useful check.
3. If ready, continue.
4. If missing but safe/non-critical, fix it and continue.
5. If user decision or risk is involved, stop and ask immediately.
6. Record durable project state in `.adversal/`.

## What counts as user-risk

Stop and ask before any action involving:

- selecting providers/workers;
- choosing or modifying a Hermes profile;
- writing to `~/.hermes/`, installing Hermes skills, or changing Hermes tool configuration;
- login, browser auth, or device-code flows;
- credentials, API keys, tokens, or secrets;
- paid/metered API usage;
- environment variables that may force paid API usage;
- `sudo` or elevated permissions;
- global configuration changes outside the project root;
- shell profile edits;
- background services/daemons;
- destructive commands or overwrites;
- real external side effects such as sending messages, opening PRs, modifying remote services, making purchases, or touching production systems.

## What you may do without asking

You may proceed without asking for:

- read-only diagnostics;
- checking OS, shell, git, package managers, CLI versions, profile lists, and installed skill lists;
- creating missing project-local folders under `.adversal/`;
- creating empty project-local ledgers and templates;
- writing run artifacts under `.adversal/runs/<run-id>/`;
- running harmless local dry-run scenarios with no external side effects.

When in doubt, ask.

## Setup phases

### Phase 0 — Announce guided mode

Tell the user briefly:

- you will proceed step by step;
- you will only stop for profile changes, decisions, login, cost, credentials, sudo, global changes, destructive actions, or external side effects;
- safe project-local setup will be handled automatically.

Then continue; do not wait for confirmation unless the user has not selected a project root or coordinator profile.

### Phase 1 — Configure the existing Hermes coordinator profile

There will be a Hermes coordinator. Do not create a profile unless the user explicitly asks. Assume the user may already have a blank or partially configured coordinator profile.

Read-only checks:

```bash
hermes profile list
hermes profile show <profile>
hermes -p <profile> tools --summary list
hermes -p <profile> skills list
```

If the active profile is ambiguous, ask which existing Hermes profile should become the Adversal coordinator.

A configured coordinator profile needs four things:

1. **SOUL.md in the Hermes profile directory** — the template in this repo has no effect until copied into the selected profile, for example:

   ```text
   ~/.hermes/profiles/<profile>/SOUL.md
   ```

   Source template:

   ```text
   https://raw.githubusercontent.com/meleeislandbot/adversal-agents/main/profiles/hermes-redteam-coordinator/SOUL.md
   ```

   This is a profile/global change. Ask before writing it.

2. **Hermes toolsets enabled** — at minimum, the coordinator should have:

   ```text
   file
   terminal
   code_execution
   web
   browser
   skills
   todo
   memory
   session_search
   clarify
   delegation
   cronjob
   ```

   `computer_use`, `github`/MCP tools, and messaging/gateway tools are optional and should only be enabled when needed. Do not enable broad or external-side-effect tools without approval.

3. **Official Hermes skills installed/enabled** — do not recreate these skills from scratch. Install or enable the official skills from Hermes/skills.sh when missing:

   ```bash
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/hermes-agent
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/llm-wiki
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/claude-code
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/codex
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/opencode
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/github-auth
   hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/github-pr-workflow
   ```

   The key wiki skill is the official NousResearch/Hermes skill:

   ```text
   skills-sh/nousresearch/hermes-agent/llm-wiki
   https://skills.sh/nousresearch/hermes-agent/llm-wiki
   ```

   If a skill is already installed as `builtin` or enabled, do not reinstall it. If installing a skill asks for confirmation or network access, follow the user-risk rule and ask first.

4. **Project context files in the target project root** — these are not profile files, but the coordinator must ensure they exist where the worker harnesses actually read them:

   ```text
   .hermes.md   # Hermes project context; first-match priority for Hermes
   AGENTS.md    # Codex/OpenCode project instructions
   CLAUDE.md    # Claude Code project memory
   GEMINI.md    # Gemini CLI context file
   ```

Custom Adversal skills, when this repo later provides any, must be installed into the selected Hermes profile's `skills/` directory or via `hermes skills install`. Leaving a custom skill somewhere in this repository does not make Hermes load it.

### Phase 2 — Confirm project root

Check current directory.

A valid Adversal project root is the directory where the red-team harness should operate. It should eventually contain:

```text
.hermes.md
AGENTS.md
CLAUDE.md
GEMINI.md
.adversal/
llm-wiki/
```

If uncertain, ask:

> I may not be in the project root. Should I use this directory as the Adversal Agents project root?

Do not continue until root ambiguity is resolved.

### Phase 3 — Install or create harness context files

Each harness reads different files. Put the files in the project root unless the tool's own docs/config say otherwise.

| Harness | Default context file behavior | Required project file |
|---|---|---|
| Hermes | Discovers project context from cwd/parents. `.hermes.md` / `HERMES.md` has priority before `AGENTS.md` and `CLAUDE.md`. | `.hermes.md` |
| Claude Code | Uses project `CLAUDE.md`/`.claude/CLAUDE.md`; `--bare` skips auto-discovery and is usually wrong for subscription/project-context runs. | `CLAUDE.md` |
| Codex CLI | Discovers `AGENTS.md` from the working root/ancestors. Use `codex exec -C <project-root>` to pin the root. | `AGENTS.md` |
| Gemini CLI | Uses `GEMINI.md` by default. It can be configured to use other filenames, but default compatibility needs `GEMINI.md`. | `GEMINI.md` |
| OpenCode | Uses `AGENTS.md`; may fall back to `CLAUDE.md` when `AGENTS.md` is absent, but do not rely on fallback. | `AGENTS.md` |

If a context file is missing, create a minimal one. Do not copy onboarding text into these files. They are day-to-day harness context.

Recommended relationship:

- `.hermes.md` contains Hermes-specific coordinator rules.
- `AGENTS.md` is the small portable cross-agent contract for Codex/OpenCode and general agents.
- `CLAUDE.md` is a thin Claude wrapper that points to `AGENTS.md` and warns about Claude-specific auth/cost hazards.
- `GEMINI.md` is a thin Gemini wrapper, preferably importing or pointing to `AGENTS.md`.

### Phase 4 — Project-local structure

Check for project-local structure. If this repository or a partial checkout is locally available, copy only the bootstrap assets from:

```text
templates/project/
```

into the selected project root. Do not clone or copy the whole source repository just to get runtime state.

If the template is not available, create the same structure manually:

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

If `llm-wiki/` is missing, create only a minimal `llm-wiki/index.md` and explain that research context can be added later. The directory is useful only if the Hermes coordinator profile has the `llm-wiki` skill installed/enabled.

The source repository stores template state under `templates/project/.adversal/`; instantiated projects store live state under `.adversal/`.

### Phase 5 — Ask for worker/provider choices

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

### Phase 6 — Verify selected workers one by one

For each selected worker, use this pattern:

1. Check whether the CLI exists.
2. If missing, explain the official install route and ask before installing.
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

Recommended automation posture: subscription-native CLI, with API-key variables scrubbed unless the user explicitly approves API mode. Do not use `--bare` for normal Adversal workers because it skips `CLAUDE.md` and keychain/OAuth paths.

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

Run from the project root or use:

```bash
codex exec -C <project-root> ...
```

Do not use `--ignore-rules` when relying on project instructions.

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

Do not assume Gemini is subscription-free until the auth route is verified. Default project context uses `GEMINI.md`; if using another filename, configure Gemini explicitly.

#### OpenCode

Check:

```bash
opencode --version
```

OpenCode is a provider-routed harness. It is not automatically subscription-native. Inspect project-local config first, then global config only with permission if needed.

Run from the project root or use:

```bash
opencode run --dir <project-root> ...
```

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

### Phase 7 — Initialize or verify scenario registry

Ensure `.adversal/scenarios/index.md` exists.

Start with safe local scenarios only:

1. direct prompt-injection refusal/containment;
2. indirect prompt injection via a local untrusted text file;
3. tool permission boundary dry run;
4. memory/RAG poisoning simulation with no persistent global memory writes;
5. reasoning/cost DoS simulation with strict local budget limits.

Do not run real external-side-effect tests during setup.

### Phase 8 — Run a harmless dry run

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

### Phase 9 — Final readiness summary

Only after the incremental setup is complete, give a short summary:

- coordinator Hermes profile name and readiness;
- project root;
- context files present;
- installed/enabled coordinator skills;
- ready workers;
- workers needing login/user action;
- disabled workers;
- cost risks;
- files created/changed;
- recommended first real red-team scenario.

Keep it short. The detailed record belongs in `.adversal/`.

## Optional command helpers

If this repository's project template has been copied into the target project root, you may use the read-only helper:

```bash
python3 scripts/adversal_doctor.py --json
```

In the source repository, the helper lives at `templates/project/scripts/adversal_doctor.py`. Do not assume `scripts/adversal_doctor.py` exists when reading these instructions remotely from GitHub. Use it as a supplement, not as a replacement for guided setup. If it reveals a blocking issue, stop at that point and guide the user.
