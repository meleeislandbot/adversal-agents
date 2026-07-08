# Bootstrap prompt from URL

Use this when the user has not cloned the repository yet.

```markdown
Go to this repository and follow its agent setup instructions:

https://github.com/meleeislandbot/adversal-agents

Authoritative setup file:

https://raw.githubusercontent.com/meleeislandbot/adversal-agents/main/instructions.md

Work in guided incremental mode:
- Check one setup area at a time.
- If it is ready, continue.
- If something safe and non-critical is missing, fix it yourself.
- Stop and ask only for provider choices, login, credentials/secrets, metered API usage, sudo/elevated permissions, global config changes, destructive actions, background services, or external side effects.
- Prefer subscription-native CLIs, local models, and deterministic checks before metered APIs.
- Do not use any paid API route without explicit approval.
- Keep all project state under `.adversal/` and curated knowledge under `llm-wiki/`.
```
