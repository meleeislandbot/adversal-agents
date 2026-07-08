# Release Process

This repository uses Semantic Versioning and Conventional Commits.

## Version files

- `VERSION` — single source for current version.
- `CHANGELOG.md` — human-readable release history.

## Release checklist

1. Ensure `main` is clean and up to date.
2. Create a release branch:

```bash
git checkout -b release/vX.Y.Z
```

3. Update `VERSION`.
4. Update `CHANGELOG.md`.
5. Run:

```bash
make validate
```

6. Open PR and review.
7. Merge to `main`.
8. Tag:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

9. Create GitHub release from the tag.

## Version bump guidance

- `PATCH`: fixes, clarifications, validation improvements.
- `MINOR`: new adapters, scenarios, workflows, docs with new capability.
- `MAJOR`: incompatible manifest/schema or workflow changes.
