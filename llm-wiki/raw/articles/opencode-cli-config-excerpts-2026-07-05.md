---
source_url: https://opencode.ai/docs/cli ; https://opencode.ai/docs/config ; https://opencode.ai/docs/providers ; local opencode run --help
ingested: 2026-07-05
sha256: af8a5f022be6066cfea25d9ae17b766d6f9bdc506cd854b3bc8ccfce82308919
source_type: docs
---

# OpenCode CLI/config excerpts — 2026-07-05

Inspected OpenCode official docs and local `opencode run --help` (`opencode 1.14.44`).

## One-shot mode

Official docs and local help show:

```bash
opencode run "Explain how closures work in JavaScript"
opencode run --format json "<task>"
opencode run --model anthropic/claude-sonnet-4 "<task>"
opencode run --agent reviewer "<task>"
```

Local help exposes:

- `--format default|json` for output;
- `--model provider/model`;
- `--agent`;
- `--file` attachments;
- `--dir` working directory;
- `--continue`, `--session`, `--fork`;
- `--variant` for provider-specific reasoning effort;
- `--thinking` to show thinking blocks;
- `--dangerously-skip-permissions` to auto-approve non-denied permissions.

## Config and providers

Docs state OpenCode uses provider configuration and credentials. Config supports environment substitution:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "models": {},
      "options": { "apiKey": "{env:ANTHROPIC_API_KEY}" }
    }
  }
}
```

`OPENCODE_CONFIG` can point at a custom config file and `OPENCODE_CONFIG_DIR` at a custom config directory. Docs mention provider API keys and custom OpenAI-compatible providers.

## Cost note

OpenCode is useful as a generic coding agent/harness, but its cost properties depend on the configured provider. If configured with API keys, it does not automatically exploit Anthropic/OpenAI/Google consumer subscriptions. Treat it as a worker backend only when the provider route is known and budgeted.
