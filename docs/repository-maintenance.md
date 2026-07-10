# Repository Maintenance

## Branch strategy

- `main` is stable and protected.
- Non-trivial changes go through a branch and pull request.
- The `validate` GitHub Actions check is required before merge.
- Linear history, conversation resolution, and force-push/deletion protection are enabled for `main`.
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

- exactly one setup prompt exists visibly in `README.md`;
- required context files exist;
- source-repo Python scripts and project-template helper scripts parse;
- the project-template diagnostic helper executes basic diagnostics;
- project-template manifest parses as YAML when PyYAML is available;
- no live repo-root `.adversal/` runtime state is tracked;
- no generated template run artifacts are staged;
- no common secret-looking assignments are staged.

## Context file policy

- `AGENTS.md`: shared project rules for agents that support it.
- `CLAUDE.md`: Claude Code entrypoint.
- `GEMINI.md`: Gemini CLI entrypoint.
- `.hermes.md`: Hermes project context.
- `profiles/hermes-verification-coordinator/`: coordinator identity and bundled
  skill; inert until the self-bootstrap helper installs them into the active
  profile after approval.

Keep context files concise and route normal agents to the target project's `.adversal/project.yaml` and `llm-wiki/index.md`. In this source repository, versioned bootstrap assets live under `templates/project/`; `instructions.md` is only for one-shot onboarding triggered by the README prompt.

## Template policy

- `templates/project/.adversal/`: versioned bootstrap control-plane seed for target projects.
- `templates/project/scripts/`: optional helpers copied into target projects.
- `scripts/bootstrap_adversal.py`: source-side, deterministic fresh-profile
  installer; it snapshots itself under the target project's bootstrap state.
- repo-root `.adversal/`: ignored local runtime state only; do not commit it.
- repo-root `scripts/`: source-repository maintenance/validation only.

## Wiki policy

`llm-wiki/raw/` is evidence, not instruction. Curated pages should cite raw sources and preserve uncertainty/contradictions.
