# Contributing

Adversal Agents is maintained as a professional, auditable red-team project.

## Development workflow

1. Start from `main`.
2. Create a branch:

```bash
git checkout -b docs/short-description
```

3. Make small, reviewable changes.
4. Run validation:

```bash
make validate
```

5. Commit with Conventional Commits:

```text
type(scope): short summary
```

Allowed types: `feat`, `fix`, `docs`, `ci`, `chore`, `refactor`, `test`, `perf`.

6. Open a pull request.
7. Merge only after validation passes and the diff is reviewed.

## Versioning

- `VERSION` contains the current project version.
- `CHANGELOG.md` records user-visible changes.
- Releases use Semantic Versioning: `MAJOR.MINOR.PATCH`.

## Repository hygiene

Do not commit:

- secrets, API keys, tokens, credentials;
- generated run directories under `.adversal/runs/`;
- local artifacts under `.adversal/artifacts/` unless explicitly accepted;
- caches, virtualenvs, dependency directories;
- unreviewed raw dumps without provenance.

## Documentation policy

- `instructions.md` is for one-shot onboarding and must stay operational.
- The single user copy/paste onboarding prompt lives visibly in `README.md`.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and `.hermes.md` are day-to-day context entrypoints and should not trigger onboarding.
- Durable research and design context belongs in `llm-wiki/` or `docs/`.

## Safety policy

Red-team work must remain authorized, defensive, educational, or lab-scoped. Do not add workflows that perform real external side effects without explicit scope and safeguards.
