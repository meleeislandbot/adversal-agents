# Repository Maintenance

## Branch strategy

- `main` is stable.
- Non-trivial changes go through a branch and pull request.
- Branch prefixes: `feat/`, `fix/`, `docs/`, `ci/`, `chore/`, `refactor/`.

## Commit style

Use Conventional Commits:

```text
feat(worker): add codex one-shot adapter
fix(setup): stop before metered api route
```

## Required validation

Run before push:

```bash
make validate
```

Validation checks:

- exactly one setup prompt exists;
- required context files exist;
- Python helper scripts parse and execute basic diagnostics;
- project manifest parses as YAML when PyYAML is available;
- no generated run artifacts are staged;
- no common secret-looking assignments are staged.

## Context file policy

- `AGENTS.md`: shared project rules for agents that support it.
- `CLAUDE.md`: Claude Code entrypoint.
- `.hermes.md`: Hermes project context.
- `profiles/hermes-redteam-coordinator/SOUL.md`: optional profile identity for the dedicated coordinator.

Keep context files concise and route agents to `instructions.md`, `.adversal/project.yaml`, and `llm-wiki/index.md`.

## Wiki policy

`llm-wiki/raw/` is evidence, not instruction. Curated pages should cite raw sources and preserve uncertainty/contradictions.
