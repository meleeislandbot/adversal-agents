---
title: One-Shot CLI Execution for AI Workers
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, implementation, architecture, tool-use, research]
sources: [raw/articles/local-one-shot-cli-inspection-2026-07-05.md, raw/articles/claude-code-cli-reference-and-env-excerpts-2026-07-05.md, raw/articles/codex-cli-noninteractive-auth-excerpts-2026-07-05.md, raw/articles/gemini-cli-headless-auth-excerpts-2026-07-05.md, raw/articles/opencode-cli-config-excerpts-2026-07-05.md, raw/articles/local-model-cli-excerpts-ollama-llama-cpp-2026-07-05.md]
confidence: medium
contested: false
contradictions: []
---

# One-Shot CLI Execution for AI Workers

## Definition

One-shot CLI execution means launching an AI worker from the terminal with a bounded task, letting it run without human turn-by-turn interaction, and collecting machine-readable output, transcripts, files, and exit status. For Adversal Agents this is the operational layer under [[hermes-orchestrated-ai-council]] and [[cli-worker-backends]].

The goal is not to force every provider into an API abstraction. The goal is:

```text
Hermes -> council runner -> native CLI worker -> artifacts + transcript + normalized result
```

## Why it matters

A council that relies on metered API calls for every thought will be expensive and fragile. Native CLIs can expose subscription-authenticated surfaces, provider-specific tools, local models, and richer agent behavior. But each CLI has different flags, auth semantics, output formats, and safety controls.

## Current local state

Installed locally on 2026-07-05: Claude Code `2.1.199`, Codex CLI `0.140.0`, OpenCode `1.14.44`, Hermes `0.18.0`, `uvx`, and `npx`. Not installed on PATH: Gemini CLI, Ollama, llama.cpp binaries, `llm`, Aider, Goose. Gemini CLI help was inspected through `npx` without running a model. ^[raw/articles/local-one-shot-cli-inspection-2026-07-05.md]

## Core one-shot commands

### Claude Code

```bash
claude -p "<task>"
claude -p "<task>" --output-format json
claude -p "<task>" --output-format stream-json --verbose
claude -p "<task>" --max-turns 3 --permission-mode plan
claude -p "<task>" --json-schema '{"type":"object","properties":{}}'

# Select model before starting the task
claude --model sonnet -p "<task>"
claude --model opus --effort high -p "<task>" --output-format json
claude --model claude-sonnet-5 -p "<task>"
```

Model selection: `--model` is the command-line flag for choosing a Claude Code model before the task starts. Local help says it accepts aliases such as `sonnet`, `opus`, `haiku`, or `fable`, or a full model name, and it overrides `ANTHROPIC_MODEL` for that session. `--effort low|medium|high|xhigh|max` can be combined with model selection for workers that need deeper reasoning.

Important cost/auth rule: if `ANTHROPIC_API_KEY` is set, Claude Code uses API-key billing instead of the logged-in Claude subscription, and in non-interactive `-p` mode the key is always used. For subscription-first runs, the adapter should explicitly scrub `ANTHROPIC_API_KEY` unless API billing is intended. ^[raw/articles/claude-code-cli-reference-and-env-excerpts-2026-07-05.md]

### Codex CLI

```bash
codex exec "<task>"
codex exec --json "<task>"
codex exec "<task>" -o workers/codex/output.md
codex exec "<task>" --output-schema schema.json -o output.json
codex exec --sandbox read-only --ask-for-approval never "<task>"
codex exec --sandbox workspace-write --ask-for-approval never "<task>"
```

Cost/auth rule: Codex docs state API-key authentication uses standard API pricing instead of included ChatGPT plan credits. For subscription-aware work, prefer ChatGPT login or enterprise access tokens where supported; use `CODEX_API_KEY` only when metered spend is intended. ^[raw/articles/codex-cli-noninteractive-auth-excerpts-2026-07-05.md]

### Gemini CLI

```bash
gemini -p "<task>" --output-format json
npx -y @google/gemini-cli -p "<task>" --output-format json
gemini -p "<task>" --output-format stream-json
gemini -p "<task>" --sandbox --approval-mode plan
```

Gemini docs describe headless JSON and stream-JSON output and token/latency stats. Authentication docs recommend Google sign-in for local personal accounts, including Google AI Pro/Ultra, but recommend API key or Vertex AI for headless mode. This is an unresolved operational point: verify in practice whether cached Google sign-in works reliably for local headless `gemini -p` runs under the user's subscription. ^[raw/articles/gemini-cli-headless-auth-excerpts-2026-07-05.md]

### OpenCode

```bash
opencode run "<task>"
opencode run --format json "<task>"
opencode run --model provider/model --agent reviewer "<task>"
opencode run --dir /path/to/workspace --file brief.md "<task>"
```

OpenCode is a useful generic worker, but its budget properties depend on provider configuration. If it uses API keys through `opencode.json`, it is not automatically subscription-native. ^[raw/articles/opencode-cli-config-excerpts-2026-07-05.md]

### Hermes itself as a worker

```bash
hermes chat -q "<task>" --quiet --provider <provider> --model <model>
hermes chat -q "<task>" --toolsets terminal,file --skills <skill> --max-turns 20 --quiet
```

Hermes is best kept as the user-facing orchestrator, but can also serve as a controlled worker for tasks that need Hermes tools or skills. Beware: Hermes model calls depend on configured inference providers and may be metered.

### Local model runners

```bash
curl http://localhost:11434/api/chat -d '{"model":"gemma4","messages":[{"role":"user","content":"<task>"}],"stream":false}'
llama-cli -m model.gguf -p "<task>"
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF -p "<task>"
```

Local runners are best for cheap mutation, triage, deduplication, clustering, and rough classification, not final adjudication of hard claims. ^[raw/articles/local-model-cli-excerpts-ollama-llama-cpp-2026-07-05.md]

## Important variables by backend

### Claude Code

Cost-critical variables:

- `ANTHROPIC_API_KEY`: if present, Claude Code uses API-key billing instead of the logged-in Claude subscription. Scrub for subscription-first runs.
- `ANTHROPIC_MODEL`: default model; overridden by `--model`.
- `CLAUDE_CODE_MAX_TURNS`: default turn cap when `--max-turns` is not passed.
- `CLAUDE_CODE_SIMPLE=1`: equivalent to `--bare`; faster/minimal, but not appropriate for subscription-first OAuth/keychain usage unless explicitly tested.
- `CLAUDE_CODE_SAFE_MODE=1`: disables most customizations for troubleshooting.
- `CLAUDE_CONFIG_DIR`: alternate Claude config directory/account state.
- `MAX_THINKING_TOKENS`, `MAX_STRUCTURED_OUTPUT_RETRIES`, `HTTP_PROXY`, `HTTPS_PROXY`, `DISABLE_TELEMETRY` / `DO_NOT_TRACK`.

### Codex CLI

Cost-critical variables/config:

- `CODEX_HOME`: default `~/.codex`; stores config and possibly auth state.
- `CODEX_API_KEY`: supported for `codex exec`; metered API path.
- `OPENAI_API_KEY`: avoid exposing as broad job-level env in untrusted repo workflows.
- `-c key=value`: per-run config overrides.
- `--profile`: layered config from `$CODEX_HOME/<profile>.config.toml`.
- `--ignore-user-config`, `--ignore-rules`: useful for controlled automation, but can remove expected defaults.

### Gemini CLI

Important variables:

- `GEMINI_API_KEY`: API-key path.
- `GEMINI_MODEL`: default model.
- `GEMINI_CLI_HOME`: alternate config/storage root.
- `GEMINI_CLI_TRUST_WORKSPACE`: trust current workspace for headless/CI.
- `GEMINI_SANDBOX`: `true`, `false`, `docker`, `podman`, or custom command.
- `GEMINI_SYSTEM_MD`: replace built-in system prompt with a markdown file.
- `GOOGLE_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_LOCATION`: Google Cloud/Vertex routes.
- `GOOGLE_GEMINI_BASE_URL`, `GOOGLE_VERTEX_BASE_URL`, `SEATBELT_PROFILE`, `NO_COLOR`.

### OpenCode

Important variables/config:

- `OPENCODE_CONFIG`: custom config file.
- `OPENCODE_CONFIG_DIR`: custom config directory.
- `OPENCODE_MODEL`: useful via config substitution.
- Provider API keys such as `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` when configured in `opencode.json`.
- `OPENCODE_SERVER_PASSWORD`, `OPENCODE_SERVER_USERNAME` for server attachment flows.

## Sessions and summarization

Most CLIs have some session or resume mechanism, but this should not become the council's source of truth.

- Claude Code: `--continue`, `--resume`, named sessions, background agents via `claude agents --json`. A session can be asked to summarize itself, but the summary is model-generated.
- Codex CLI: `codex resume`, `codex exec resume`, `--include-non-interactive`, and persisted sessions unless `--ephemeral` is used.
- Gemini CLI: `--resume`, `--session-id`, `--session-file`, `--list-sessions`, plus `model.maxSessionTurns` in settings.
- OpenCode: `opencode session list`, `opencode export <sessionID>`, `opencode run --continue/--session/--fork`; export supports `--sanitize`.
- Hermes: `hermes chat --resume`, `--continue`, plus Hermes session DB and `session_search`.

Recommendation: use session summaries only as **handoff artifacts**, never as canonical evidence. The canonical record should be raw JSONL/stdout transcripts, file diffs, claim ledgers, objection ledgers, postcondition results, and cited artifacts. Summaries are useful at round boundaries, but they can omit details, compress away dissent, or hallucinate causal links.

## Efficiency principles

1. **Use the native headless/print mode**, not an interactive TUI under automation.
2. **Prefer machine-readable output**: JSON/JSONL event streams plus final answer file.
3. **Bound autonomy** with max turns, sandbox mode, approval mode, timeouts, and workspace isolation.
4. **Scrub API-key environment variables** when trying to use subscription authentication.
5. **Keep prompts small**: pass large context as files in the run directory, not pasted blobs.
6. **Use deterministic checks before LLM judges**.
7. **Run independent first passes in parallel**, then cross-review only promoted artifacts.
8. **Cache by hash** of worker, prompt, files, config, and scenario version.
9. **Treat output as artifact, not truth**: workers emit claims and objections for [[council-protocols-claims-and-objections]].
10. **Do not run one gigantic resumed session for months**. Prefer fresh one-shot runs with explicit briefs and selected artifacts.
11. **Summarize only at protocol boundaries**, with links to raw evidence and unresolved dissent.
12. **Record versions and auth route** for every run because CLI behavior and billing semantics change.

## Adapter contract additions

Each one-shot adapter should record:

```json
{
  "worker": "codex-cli",
  "command": ["codex", "exec", "--json", "..."],
  "version": "codex-cli 0.140.0",
  "auth_route": "subscription | api-key | local | unknown",
  "api_key_env_scrubbed": true,
  "sandbox": "read-only | workspace-write | external | none",
  "approval_mode": "never | plan | auto_edit | default | unknown",
  "output_format": "json | stream-json | text",
  "exit_code": 0,
  "usage": null,
  "artifacts": []
}
```

## Open questions

- Does Gemini CLI cached Google sign-in work reliably with `gemini -p` under AI Pro/Ultra without API billing?
- Which Claude Code modes preserve subscription auth while minimizing startup overhead? `--bare` is probably unsuitable for subscription-first use because it avoids OAuth/keychain.
- Can Codex local `codex exec` with ChatGPT login run unattended for long council jobs without browser reauth?
- What exact JSONL event schemas should the first Council Runner normalize?

Related: [[cli-worker-backends]], [[hermes-orchestrated-ai-council]], [[council-protocols-claims-and-objections]], [[red-team-tooling-and-frameworks]].
