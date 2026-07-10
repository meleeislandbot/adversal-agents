# Self-bootstrap safety contract

Setup begins inside the fresh Hermes profile that will become the coordinator.
No separate technical agent is assumed. The profile receives the public setup
prompt, acquires one immutable source checkout, configures itself, initializes a
separate project, restarts, and resumes from project-local state.

## Portability rule

Assume nothing except a running Hermes profile capable of reading the setup URL.
Discover the operating system, active `HERMES_HOME`, CLI syntax, project path,
installed commands, skills, tools, authentication, and cost routes. Never guess
a profile path from its display name.

## Continue automatically when

- the action is read-only;
- cloning/fetching the public source is non-destructive;
- the write creates a new project-local path without overwriting;
- a deterministic local test has no external side effects.

## Stop and ask when

- modifying the active profile, including `SOUL.md`, skills, or toolsets;
- a provider/worker or project root must be selected;
- login, authentication, secrets, or API keys are involved;
- a route may incur API cost or consume unapproved quota;
- installing Lean, mathlib, a CLI, or any other toolchain;
- elevated permissions or global configuration are required;
- an existing file would be overwritten;
- there is risk of external/destructive side effects.

## Deterministic write boundary

Use `scripts/bootstrap_adversal.py` for profile identity/skill installation and
project initialization. It requires separate approval flags, backs up the
previous `SOUL.md`, rejects non-identical files, records the exact source commit,
and writes `.adversal/bootstrap/state.json`.

After `SOUL.md` changes, stop the session. Resume only in a new session of the
same profile; the helper verifies the profile home and installed hashes before
advancing the checkpoint.

Do not produce a giant final problem list. Surface blockers when they occur and
report readiness as separate checked booleans.
