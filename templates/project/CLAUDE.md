# Claude Code project entrypoint

Read `AGENTS.md`, `docs/epistemics.md`, and `.adversal/project.yaml` before
substantial work. When invoked as an isolated worker, follow only the assigned
role and return the required structured artifact; do not seek other workers'
drafts.

Check `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` by presence only. Never
print their values or assume an API-key route is covered by a subscription.
