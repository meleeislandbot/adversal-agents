# Hermes Coordinator Profile

Adversal Agents requires a Hermes coordinator in practice, but this repository cannot activate one merely by being cloned. The user should already have, or explicitly choose, a Hermes profile that will become the coordinator.

## What configuration means

A Hermes coordinator profile is configured when these pieces are in the places Hermes actually reads:

1. `SOUL.md` in the selected profile directory:

   ```text
   ~/.hermes/profiles/<profile>/SOUL.md
   ```

2. Required Hermes toolsets enabled for that profile.
3. Required Hermes skills installed/enabled for that profile.
4. Project context files in the target project root for the worker harnesses.

The template at:

```text
profiles/hermes-redteam-coordinator/SOUL.md
```

has no runtime effect until it is copied into the selected Hermes profile or installed by an explicit setup step.

## Read-only discovery

Use read-only commands first:

```bash
hermes profile list
hermes profile show <profile>
hermes -p <profile> tools --summary list
hermes -p <profile> skills list
```

Do not create, overwrite, or switch profiles without the user's explicit approval.

## Coordinator SOUL

Source template:

```text
https://raw.githubusercontent.com/meleeislandbot/adversal-agents/main/profiles/hermes-redteam-coordinator/SOUL.md
```

Install it only after approval, for example:

```bash
mkdir -p ~/.hermes/profiles/<profile>
curl -fsSL https://raw.githubusercontent.com/meleeislandbot/adversal-agents/main/profiles/hermes-redteam-coordinator/SOUL.md \
  -o ~/.hermes/profiles/<profile>/SOUL.md
```

A local clone can copy the same file instead of using `curl`.

## Required skills

Do not recreate existing official skills. Install/enable the official NousResearch/Hermes skills when missing:

```bash
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/hermes-agent
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/llm-wiki
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/claude-code
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/codex
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/opencode
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/github-auth
hermes -p <profile> skills install skills-sh/nousresearch/hermes-agent/github-pr-workflow
```

The wiki directory is only useful to the coordinator if the `llm-wiki` skill is installed/enabled:

```text
https://skills.sh/nousresearch/hermes-agent/llm-wiki
```

## Required toolsets

At minimum, the coordinator normally needs:

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

Enable broader side-effect tools only when the user approves the risk and purpose.

## Project context files

Context files belong in the target project root, not inside the Hermes profile:

| Harness | File | Notes |
|---|---|---|
| Hermes | `.hermes.md` / `HERMES.md` | First-match priority before `AGENTS.md` and `CLAUDE.md`. |
| Claude Code | `CLAUDE.md` | Normal project memory; `--bare` skips it. |
| Codex CLI | `AGENTS.md` | Use `codex exec -C <project-root>` to pin discovery. |
| Gemini CLI | `GEMINI.md` | Default context filename; can import `AGENTS.md`. |
| OpenCode | `AGENTS.md` | May fall back to `CLAUDE.md`, but do not rely on fallback. |

Keep these files short. Large, curated knowledge belongs in `llm-wiki/` and only has effect when a coordinator/worker reads it deliberately.

## What this profile should not do by default

- It should not assume provider API keys are free to use.
- It should not write global Hermes configuration without explicit user approval.
- It should not store run results in profile memory instead of `.adversal/`.
- It should not treat worker outputs as verified facts.
