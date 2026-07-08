---
source_url: https://developers.openai.com/codex/noninteractive ; https://developers.openai.com/codex/auth ; local codex --help
ingested: 2026-07-05
sha256: 3cd10bccc3cd56d6e7a7e0fe8c6604d12b785589502534c1847c8048aec81e90
source_type: docs
---

# Codex CLI non-interactive and auth excerpts — 2026-07-05

Inspected official OpenAI Codex docs and local Codex CLI help (`codex-cli 0.140.0`).

## One-shot / non-interactive mode

Official docs: use `codex exec` for scripts and CI without opening the TUI.

```bash
codex exec "summarize the repository structure"
codex exec --json "summarize the repo structure" | jq
codex exec "Extract project metadata" --output-schema ./schema.json -o ./project-metadata.json
```

Local help confirms:

- prompt can be argument, stdin, or `-`; if stdin is piped and prompt also supplied, stdin is appended as a `<stdin>` block;
- `--json` emits JSONL events;
- `-o/--output-last-message FILE` writes final message;
- `--output-schema FILE` requests schema-conforming final response;
- `--ephemeral` avoids persisting session files;
- `--ignore-user-config` skips `$CODEX_HOME/config.toml`; `--ignore-rules` skips execpolicy rules;
- `--skip-git-repo-check` permits non-git dirs;
- `-C/--cd DIR` sets working root;
- `--oss --local-provider ollama|lmstudio` routes to local providers.

## Sandbox and approvals

Docs state `codex exec` defaults to a read-only sandbox. Explicit options:

```bash
codex exec --sandbox read-only "<task>"
codex exec --sandbox workspace-write "<task>"
codex exec --sandbox danger-full-access "<task>"
```

Local help also exposes `--ask-for-approval untrusted|on-failure|on-request|never` and warns that `--dangerously-bypass-approvals-and-sandbox` is only for externally sandboxed environments.

## Cost/auth warning

Official auth docs say API key authentication uses standard API pricing instead of included ChatGPT plan credits. For subscription-first local work, prefer ChatGPT login when the local Codex CLI supports the desired workflow. `CODEX_API_KEY` is supported for a single `codex exec` invocation, but using it means metered API spend.

Docs also mention enterprise access tokens for trusted non-interactive workflows needing ChatGPT-managed Codex entitlements without browser sign-in.

## Environment/config surfaced

- `CODEX_HOME`: defaults to `~/.codex`; stores config and, when file credential storage is used, `auth.json`.
- `CODEX_API_KEY`: supported in `codex exec`; set inline for a single run if API-key mode is needed.
- `OPENAI_API_KEY`: docs warn against job-level exposure in workflows that run repository-controlled code.
- Config overrides: `-c key=value`, profiles via `--profile`, model via `--model`, sandbox via `--sandbox`.
