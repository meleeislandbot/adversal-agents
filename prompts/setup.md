# Setup prompt

Copy and paste this single prompt into your agent while it is opened in, or has access to, the Adversal Agents repository.

```markdown
Use the Adversal Agents repository as the project root and follow `instructions.md` as your authoritative guided setup procedure.

If the repository is not local yet, clone or open:
https://github.com/meleeislandbot/adversal-agents

Then continue from the repository root.

Operating rules:
- Work step by step. Do not wait until the end to report all missing items.
- For each setup area: check it, fix safe non-critical gaps yourself, then continue.
- Stop and ask me only for real decisions or risk: provider/worker selection, login or device-code flow, credentials/secrets, metered API usage, sudo/elevated permissions, global config changes, destructive commands, background services, overwriting existing files, or external side effects.
- If a selected CLI is missing and can be installed safely without sudo, secrets, paid API usage, shell-profile edits, or background services, install it and continue.
- Prefer deterministic checks, local tools, local models, and subscription-native CLIs before metered APIs.
- Do not use paid APIs unless I explicitly approve that specific route.
- Keep project state under `.adversal/` and curated knowledge under `llm-wiki/`.
- Save traces, worker status, decisions, objections, budget notes, and final readiness as files. Do not rely on chat memory as the project record.

Start now in read-only discovery mode, then guide me through the minimum decisions needed to initialize the project.
```
