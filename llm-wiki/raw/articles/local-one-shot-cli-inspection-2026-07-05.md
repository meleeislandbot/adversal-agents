---
source_url: command://local-cli-help-and-versions
ingested: 2026-07-05
sha256: 92d6bd2b0b0f3c66661b9d1e61b857f5b60d6fe3bd3e894f34bb78e4ef45aefa
source_type: other
---

# Local one-shot CLI inspection — 2026-07-05

Commands inspected without running model prompts.

## Installed locally

```json
[
  {"cmd":"claude","path":"/Users/ia/.local/bin/claude","version":"2.1.199 (Claude Code)"},
  {"cmd":"codex","path":"/opt/homebrew/bin/codex","version":"codex-cli 0.140.0"},
  {"cmd":"opencode","path":"/opt/homebrew/bin/opencode","version":"1.14.44"},
  {"cmd":"hermes","path":"/Users/ia/.local/bin/hermes","version":"Hermes Agent v0.18.0 (2026.7.1)"},
  {"cmd":"uvx","path":"/Users/ia/.local/bin/uvx","version":"uvx 0.11.18"},
  {"cmd":"npx","path":"/Users/ia/.local/bin/npx","version":"10.9.8"}
]
```

## Not installed locally

`gemini`, `ollama`, `llama-cli`, `llama-server`, `llm`, `aider`, and `goose` were not found on PATH. Gemini help was inspected with `npx -y @google/gemini-cli --help` without authenticating or running a model prompt.

## Local help highlights

- Claude Code: `claude -p/--print` for non-interactive output; `--output-format text|json|stream-json`; `--max-turns`; `--json-schema`; `--model`; `--effort`; `--tools`; `--allowedTools`; `--permission-mode`; `--bare`.
- Codex CLI: `codex exec` for non-interactive mode; `--json`; `-o/--output-last-message`; `--output-schema`; `--sandbox read-only|workspace-write|danger-full-access`; `--ask-for-approval`; `--ignore-user-config`; `--ignore-rules`; `--ephemeral`; `--oss --local-provider ollama|lmstudio`.
- OpenCode: `opencode run`; `--format json`; `--model provider/model`; `--agent`; `--dir`; `--file`; `--variant`; `--dangerously-skip-permissions`.
- Gemini CLI: `gemini -p/--prompt` headless mode; `--output-format text|json|stream-json`; `--model`; `--sandbox`; `--approval-mode`; `--skip-trust`; `--session-id`; `--include-directories`.
- Hermes: `hermes chat -q/--query`; `--provider`; `--model`; `--toolsets`; `--skills`; `--quiet`; `--max-turns`; `--yolo`; `--ignore-user-config`; `--safe-mode`.
