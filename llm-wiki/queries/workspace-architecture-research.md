---
title: Workspace Architecture Research
created: 2026-07-06
updated: 2026-07-06
type: query
tags: [adversal-agents, architecture, implementation, memory, open-question]
sources: [raw/articles/project-workspace-context-file-research-2026-07-06.md, raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md]
confidence: medium
contested: false
contradictions: []
---

# Workspace Architecture Research

## Question

How should Adversal Agents organize a declared project folder so workers are not totally isolated, and can a project-local wiki be shared across Hermes, Claude Code, Codex CLI, Gemini CLI, and OpenCode without repeating instructions in every prompt?

## Short answer

Use a user-declared project root. Inside it, place a curated `llm-wiki/`, a small canonical `AGENTS.md`, adapter-specific project context wrappers (`CLAUDE.md`, `GEMINI.md`, `.hermes.md`), and `.adversal/` run/ledger state. Launch every worker with the project root as its cwd or explicit working root. That lets native context discovery load the project contract automatically.

The wiki is recommended, but the whole wiki should not be auto-injected. Auto-load a short entrypoint that tells agents where the wiki lives and how to use it. Let agents read relevant pages on demand.

## Evidence

- Hermes can auto-load project context files from a working directory, including `.hermes.md`, `AGENTS.md`, and `CLAUDE.md` depending on discovery order. ^[raw/articles/project-workspace-context-file-research-2026-07-06.md]
- Claude Code uses `CLAUDE.md` and related rules/memory files; it also documents imports and `AGENTS.md` compatibility. ^[raw/articles/project-workspace-context-file-research-2026-07-06.md]
- Codex discovers `AGENTS.md` by walking up from the working directory and has `-C/--cd` for setting the working root. ^[raw/articles/project-workspace-context-file-research-2026-07-06.md]
- Gemini CLI uses `GEMINI.md`, can import files via `@file.md`, and can customize context filenames such as `AGENTS.md`. ^[raw/articles/project-workspace-context-file-research-2026-07-06.md]
- OpenCode reads `AGENTS.md`, can fall back to `CLAUDE.md`, and supports project `opencode.json`. ^[raw/articles/project-workspace-context-file-research-2026-07-06.md]

## Proposed MVP

1. User declares project root:

```bash
adversal project init /path/to/project
```

2. The initializer creates:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
.hermes.md
llm-wiki/
.adversal/project.yaml
.adversal/runs/
.adversal/ledgers/
```

3. `AGENTS.md` is the canonical portable entrypoint. Wrappers import or point to it.

4. Council Runner always launches workers with the project root:

```bash
codex exec -C "$PROJECT_ROOT" "$(cat .adversal/runs/<id>/prompts/codex.md)"
claude -p "$(cat .adversal/runs/<id>/prompts/claude.md)"  # terminal workdir = PROJECT_ROOT
opencode run --dir "$PROJECT_ROOT" "$(cat .adversal/runs/<id>/prompts/opencode.md)"
gemini -p "$(cat .adversal/runs/<id>/prompts/gemini.md)"  # cwd/include dirs = PROJECT_ROOT
```

5. Workers write outputs under `.adversal/runs/<run-id>/workers/<worker>/`.

6. Workers propose wiki edits; Hermes curates and applies them after validation.

## Recommended policy

- **Mandatory project root:** yes. Without it, workers cannot share context safely.
- **Shared wiki:** yes, project-local and versionable.
- **Full wiki auto-injection:** no. Use short root context files that point to the wiki.
- **Direct worker wiki writes:** no by default. Use proposed patches and curator merge.
- **Separate scratch:** yes, per worker and per run.
- **Canonical memory:** wiki + ledgers + run artifacts, not provider sessions.

## Key design decision

The system should make the workspace explicit:

```text
Hermes message -> project root -> council runner -> native CLI workers -> run artifacts -> curated wiki update
```

This solves the user’s “messenger” problem: the human no longer copies between providers. The shared wiki and ledgers become the medium of communication, while each worker remains autonomous and skeptical.

## Next decisions

- Pick canonical entrypoint name: likely `AGENTS.md`.
- Define exact `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.hermes.md` templates.
- Decide whether to call the operational directory `.adversal/` or `adversal/`.
- Define the first `project.yaml` schema.
- Decide write permissions for wiki curation roles.

Related: [[declared-project-workspace-and-shared-wiki]], [[hermes-orchestrated-ai-council]], [[cli-worker-backends]], [[one-shot-cli-execution]].
