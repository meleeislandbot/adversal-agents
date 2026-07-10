# Hermes coordinator profile

Adversal Agents starts from a fresh user-created Hermes profile. The profile
configures itself from the README prompt and `instructions.md`; cloning the
repository alone activates nothing.

## Effective profile state

The bootstrap must discover, not assume:

- the active profile's effective `HERMES_HOME`;
- the current Hermes CLI/alias syntax;
- `SOUL.md`, skills, tools, model/provider configuration, and terminal cwd;
- the target machine's operating system and installed commands.

Named profiles commonly live below `~/.hermes/profiles/`, but setup must never
write there based on that convention alone. It verifies the active profile home
through the environment or profile-aware native configuration.

## Installed assets

After explicit approval, `scripts/bootstrap_adversal.py apply` installs:

1. `profiles/hermes-verification-coordinator/SOUL.md` as the active profile's
   durable identity, preserving the previous file as `SOUL.pre-adversal.md`;
2. the bundled `adversal-coordinator` skill under the profile's
   `skills/research/` tree;
3. an instantiated project with context files, control plane, scripts, Lean
   pins, and empty wiki;
4. a source-commit-bound checkpoint and helper snapshot under
   `.adversal/bootstrap/`.

The running session stops after these writes. A new session is required before
the installed identity can be considered active.

## Capabilities

Normally required toolsets are:

```text
file terminal code_execution web skills todo memory session_search clarify delegation
```

Browser and cron are optional. Broad side-effect tools are not prerequisites.
Setup checks the current profile's official `llm-wiki` and selected provider
skills, installing or enabling missing components only after approval.

## Boundaries

- A profile is not a filesystem sandbox; prompt text does not enforce access.
- The profile does not decide mathematical truth.
- Profile memory is not the canonical research brain.
- Worker output is unverified until the deterministic gate validates it.
- Credentials, global configuration, toolchains, paid routes, and overwrites
  always require user approval.
