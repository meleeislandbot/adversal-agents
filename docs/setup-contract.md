# Guided Setup Contract

Setup must be incremental and user-safe.

## Continue automatically when

- the action is read-only;
- the write is project-local and non-destructive;
- a missing file/folder can be created without overwriting;
- a selected CLI can be installed without sudo, credentials, paid API use, or global shell edits.

## Stop and ask when

- a provider/worker choice is needed;
- login/auth is required;
- a secret or API key is involved;
- a route may incur API cost;
- elevated permissions are required;
- global configuration would be modified;
- there is risk of external side effects;
- existing user files would be overwritten.

## Do not produce a giant final problem list

The agent should surface blockers at the point they matter.
