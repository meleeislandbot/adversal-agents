# Hermes Coordinator Profile

Adversal Agents can be coordinated by any capable agent, but for serious work we recommend creating a dedicated Hermes profile and giving it the project-specific `SOUL.md` in this repository.

## Recommended profile creation

Clean profile:

```bash
hermes profile create adversal-redteam
```

Or clone an existing well-configured profile:

```bash
hermes profile create adversal-redteam --clone-from <existing-profile>
```

Then copy or symlink the coordinator soul:

```bash
mkdir -p ~/.hermes/profiles/adversal-redteam
cp profiles/hermes-redteam-coordinator/SOUL.md ~/.hermes/profiles/adversal-redteam/SOUL.md
```

Start Hermes from the project root:

```bash
cd /path/to/adversal-agents
hermes --profile adversal-redteam
```

## Recommended enabled capabilities

The profile should have, at minimum:

- file tools;
- terminal tools;
- web/browser only when current-source verification is needed;
- GitHub tools or `gh` CLI for repository work;
- memory enabled only for stable user/project preferences, not transient run state;
- skills enabled for Hermes, GitHub, red teaming, CLI workers, and project workspaces.

## What this profile should not do by default

- It should not assume provider API keys are free to use.
- It should not write global Hermes configuration without explicit user approval.
- It should not store run results in profile memory instead of `.adversal/`.
- It should not treat worker outputs as verified facts.

## Project context files

- Hermes reads `.hermes.md` first when launched from this repo.
- Claude Code reads `CLAUDE.md`.
- Codex/OpenCode and several other agents commonly use `AGENTS.md`.

Keep these files short. Large, curated knowledge belongs in `llm-wiki/`.
