---
source_url: https://code.claude.com/docs/en/cli-reference ; https://code.claude.com/docs/en/env-vars
ingested: 2026-07-05
sha256: 3452d94b4c46efc168dbdcd7680ee42839830528401caee381e4107046140716
source_type: docs
---

# Claude Code CLI reference and environment excerpts — 2026-07-05

Inspected official Claude Code documentation and local `claude --help`.

## One-shot / non-interactive mode

Claude Code starts interactive by default, but `-p` / `--print` prints a response and exits. Relevant flags include:

```bash
claude -p "query"
claude -p "query" --output-format json
claude -p "query" --output-format stream-json --verbose
claude -p "query" --max-turns 3
claude -p "query" --json-schema '{"type":"object","properties":{...}}'
claude -p "query" --model sonnet
```

Local help showed `--output-format` choices `text`, `json`, and `stream-json`; `--input-format text|stream-json`; `--include-partial-messages`; `--include-hook-events`; `--no-session-persistence`; `--fallback-model`; `--max-budget-usd`; `--tools`; `--allowedTools`; `--disallowedTools`; and `--permission-mode`.

## Cost/auth warning

Official env-var docs state that `ANTHROPIC_API_KEY` is used instead of Claude Pro/Max/Team/Enterprise subscription login. In non-interactive mode (`-p`), the key is always used when present. To use the subscription path, unset `ANTHROPIC_API_KEY`.

## Minimal / faster startup mode

`--bare` skips hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, and CLAUDE.md auto-discovery. It sets `CLAUDE_CODE_SIMPLE=1`, but local help says Anthropic auth is strictly `ANTHROPIC_API_KEY` or `apiKeyHelper`; OAuth/keychain are not read. This makes `--bare` attractive for API-key automation but potentially wrong for subscription-first runs.

`CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` uses a shorter system prompt while keeping the broader tool set and discovery behavior enabled.

## Environment variables surfaced

- `ANTHROPIC_API_KEY`: API key; overrides subscription login.
- `ANTHROPIC_MODEL`: default model; overridden by `--model` or `/model`.
- `CLAUDE_CODE_MAX_TURNS`: default turn cap when `--max-turns` is not passed.
- `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`: maximum read-only tools/subagents in parallel; default noted as 10.
- `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_BEDROCK`: route to third-party/cloud providers.
- `CLAUDE_CONFIG_DIR`: alternate config directory; useful for multiple accounts.
- `CLAUDE_CODE_SAFE_MODE`: disables customizations for troubleshooting.
- `CLAUDE_CODE_SIMPLE`: equivalent to `--bare`.
- `HTTP_PROXY`, `HTTPS_PROXY`: proxy network connections.
- `DISABLE_TELEMETRY` / `DO_NOT_TRACK`: telemetry opt-out signals.
- `MAX_STRUCTURED_OUTPUT_RETRIES`: retries for failed `--json-schema` validation in non-interactive mode; docs state default 5.
- `MAX_THINKING_TOKENS`: override extended thinking budget.
