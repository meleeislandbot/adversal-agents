---
source_url: mixed:official-docs-and-local-help
ingested: 2026-07-06
sha256: 27c854d6d3b2311f84ebad8b1183a2e4dd147023c7f700b5111829ac92d24540
source_type: docs
---

# Project Workspace and Agent Context File Research — excerpts

This raw note captures verified excerpts and local-help observations relevant to making a declared project root and shared wiki visible to multiple CLI workers without repeating the same instruction in every prompt.

## Hermes Agent project context files

Hermes project-context discovery, from the loaded `hermes-agent` skill based on current docs:

- Hermes injects project-level instructions from the working directory into the system prompt.
- Discovery order is first-match-wins: `.hermes.md` / `HERMES.md`, then `AGENTS.md`, then `CLAUDE.md`, then `.cursorrules` / `.cursor/rules/*.mdc`.
- `.hermes.md` / `HERMES.md` walks parents up to the git root; `AGENTS.md` and `CLAUDE.md` are cwd-only in Hermes.
- Each context file is capped at about 20,000 characters and can be threat-scanned before injection.
- Cron jobs and some Hermes tool invocations can set a `workdir`; when set, project context files in that directory are loaded.

## Claude Code memory and rules

Claude Code docs (`https://code.claude.com/docs/en/memory`, `https://code.claude.com/docs/en/settings`) describe project instruction/memory files:

- Claude Code uses `CLAUDE.md` files for project memory/instructions.
- It supports user/project/local locations, including `~/.claude/CLAUDE.md`, project `CLAUDE.md` or `.claude/CLAUDE.md`, and `CLAUDE.local.md`.
- It supports importing additional files from a `CLAUDE.md` file.
- It also documents `AGENTS.md` compatibility, rule directories such as `.claude/rules/`, path-specific rules, and symlink-based sharing.
- `--bare` skips hooks, plugins, MCP discovery, `CLAUDE.md`, and OAuth/keychain paths; that is usually unsuitable for subscription-first project-context loading.

Local Claude Code skill/help observations:

- `--setting-sources user,project,local` controls which setting sources load.
- `--append-system-prompt-file` can force extra context for a one-shot run, but that is less portable than native project files.
- `--add-dir` grants access to additional directories.

## Codex CLI project instructions

OpenAI Codex docs (`https://developers.openai.com/codex/config-advanced`, `https://developers.openai.com/codex/noninteractive`) and local help state:

- Codex discovers project configuration and `AGENTS.md` by walking up from the working directory until it reaches a project root.
- Codex reads `AGENTS.md` and related files and includes a limited amount of project guidance in the first turn of a session.
- Config knobs include `project_doc_max_bytes` and `project_doc_fallback_filenames`.
- Project-scoped `.codex/` config layers are loaded only when the project is trusted.
- `codex exec -C <DIR>` / `--cd <DIR>` tells Codex to use a specified directory as its working root.
- `--add-dir <DIR>` can add additional writable directories.
- `--ignore-user-config` and `--ignore-rules` intentionally skip config/rules and should not be used when relying on project context.

## Gemini CLI project context

Gemini CLI docs (`docs/cli/gemini-md.md`, `settings.md`, `session-management.md`) state:

- Gemini CLI uses `GEMINI.md` context files to avoid repeating instructions in every prompt.
- It loads global context at `~/.gemini/GEMINI.md` plus environment/workspace context files in configured workspace directories and parents.
- It supports just-in-time context files: when the model reads files in a directory, Gemini scans for `GEMINI.md` files in that directory and ancestors up to a trusted root.
- `GEMINI.md` can import other files using `@file.md` syntax, e.g. `@./components/instructions.md`.
- The context file name can be customized via settings: `context.fileName`, e.g. `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`.
- Workspace settings live in `your-project/.gemini/settings.json`; settings include `context.discoveryMaxDirs`, `context.loadMemoryFromIncludeDirectories`, and session settings such as `model.maxSessionTurns`.
- Sessions are project-specific and can be resumed, but wiki/ledger files remain better canonical state than provider session memory.

## OpenCode rules

OpenCode docs (`https://opencode.ai/docs/rules/`, `https://opencode.ai/docs/config/`) state:

- OpenCode reads project instructions from `AGENTS.md`; `/init` can create one and docs recommend committing it to Git.
- OpenCode supports Claude Code compatibility: project `CLAUDE.md` is used if no `AGENTS.md` exists; global `~/.claude/CLAUDE.md` is used if no OpenCode global `AGENTS.md` exists.
- OpenCode config has global and per-project `opencode.json` locations with precedence rules; custom config path/directory can also be supplied.
- OpenCode supports compaction configuration and session export, but that should not replace project files as canonical memory.

## Design implication

The portable, lowest-friction pattern is a declared project root containing a small `AGENTS.md` as the canonical cross-agent entrypoint, plus adapter-specific wrappers (`CLAUDE.md`, `GEMINI.md`, `.hermes.md`) that import or point to it and to the project wiki index. Workers should be launched with the project root as cwd/working root so native discovery loads the files automatically.
