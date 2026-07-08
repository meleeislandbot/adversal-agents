# Copy/paste prompt for your agent

Use this prompt in Hermes, Claude Code, Codex, Gemini CLI, OpenCode, or another agent that can inspect files and run local commands.

```markdown
Open this repository and follow `instructions.md` as a guided setup procedure for Adversal Agents.

Important rules:
- Work step by step. Do not wait until the end to tell me everything that is missing.
- For each setup area: check it, report briefly if needed, fix safe non-critical gaps yourself, then continue.
- Stop and ask me only when there is a real decision or risk: provider selection, login/device-code flow, credentials/secrets, paid or metered API usage, sudo/elevated permissions, global config changes, destructive commands, background services, or overwriting existing files.
- If a selected CLI is missing and can be installed safely without sudo, secrets, or paid API usage, install it and continue.
- Prefer subscription-native CLIs and local/deterministic tools before metered APIs.
- Do not use paid APIs unless I explicitly approve that specific route.
- Keep project state under `.adversal/` and curated knowledge under `llm-wiki/`.
- Save traces, worker status, decisions, objections, and budget notes as files. Do not rely on chat memory as the project record.

Start in read-only discovery mode, then guide me through the minimum decisions needed to initialize the project.
```
