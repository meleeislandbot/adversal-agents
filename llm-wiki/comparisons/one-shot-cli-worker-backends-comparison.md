---
title: One-Shot CLI Worker Backend Comparison
created: 2026-07-05
updated: 2026-07-05
type: comparison
tags: [adversal-agents, comparison, implementation, architecture, tool-use]
sources: [raw/articles/local-one-shot-cli-inspection-2026-07-05.md, raw/articles/claude-code-cli-reference-and-env-excerpts-2026-07-05.md, raw/articles/codex-cli-noninteractive-auth-excerpts-2026-07-05.md, raw/articles/gemini-cli-headless-auth-excerpts-2026-07-05.md, raw/articles/opencode-cli-config-excerpts-2026-07-05.md, raw/articles/local-model-cli-excerpts-ollama-llama-cpp-2026-07-05.md]
confidence: medium
contested: false
contradictions: []
---

# One-Shot CLI Worker Backend Comparison

## Bottom line

For the first Adversal Agents council runner, the practical order is:

1. **Codex CLI** for robust non-interactive traces and sandbox controls.
2. **Claude Code** for strong reasoning/review via subscription-aware local CLI, with careful env scrubbing.
3. **OpenCode** as a generic provider-backed coding worker when cost route is explicit.
4. **Gemini CLI** after verifying subscription/headless auth behavior.
5. **Local runners** for cheap pre-filtering and bulk mutation.
6. **Hermes** as orchestrator first, worker second.

## Comparison table

| Backend | One-shot command | Machine output | Cost route | Strength | Main risk |
|---|---|---|---|---|---|
| Claude Code | `claude -p "<task>"` | `--output-format json|stream-json`, `--json-schema` | Subscription if logged in and API env absent; API if `ANTHROPIC_API_KEY` set | Strong critique/reasoning, rich tools | Accidental API billing; `--bare` disables OAuth/keychain |
| Codex CLI | `codex exec "<task>"` | `--json`, `-o`, `--output-schema` | ChatGPT login/subscription where supported; API with `CODEX_API_KEY` | Good automation surface; sandbox defaults | API-key mode uses standard API pricing |
| Gemini CLI | `gemini -p "<task>"` | `--output-format json|stream-json` with stats | Google sign-in for local users; docs recommend API key/Vertex for headless | Free/Pro/Ultra quotas, large context, Google tooling | Need empirical auth/billing verification for headless subscription use |
| OpenCode | `opencode run "<task>"` | `--format json` | Depends on configured provider/API key | Flexible model/provider abstraction, agents | Not automatically subscription-native |
| Hermes | `hermes chat -q "<task>" --quiet` | final response/session metadata | Depends on Hermes provider config | Skills/tools/memory/orchestration | May become metered API path if used as worker too often |
| Ollama/llama.cpp | `ollama run`, local REST API, `llama-cli -p` | CLI/API text/JSON depending runner | Local compute | Cheap bulk work | Lower capability; setup/model management |

## Best initial recipes

### Claude Code reviewer / skeptic

```bash
env -u ANTHROPIC_API_KEY   claude -p "$(cat prompt.md)"   --output-format json   --max-turns 6   --permission-mode plan   --tools "Read,Bash"
```

Use for skeptical review, proof-gap discovery, security scenario critique, and synthesis. Avoid `--bare` in subscription-first mode until proven compatible with the desired auth route.

### Codex implementation / trace-heavy worker

```bash
codex exec   --sandbox workspace-write   --ask-for-approval never   --json   -C "$RUN_WORKSPACE"   -o workers/codex/final.md   "$(cat prompt.md)"
```

Use when you want JSONL traces, file diffs, sandboxing, and code-oriented action.

### Gemini scout / broad-context worker

```bash
gemini -p "$(cat prompt.md)"   --output-format json   --sandbox   --approval-mode plan
```

Use after validating headless subscription behavior. Good candidate for literature scanning, broad-context summarization, or independent first-pass reasoning.

### OpenCode generic worker

```bash
OPENCODE_CONFIG=/path/to/budgeted-opencode.json   opencode run --format json --dir "$RUN_WORKSPACE" --agent reviewer "$(cat prompt.md)"
```

Use only when the provider route and budget are explicit.

### Local triage worker

```bash
curl http://localhost:11434/api/chat -d @request.json
llama-cli -m model.gguf -p "$(cat prompt.md)"
```

Use for mutation, clustering, dedupe, rough severity labels, and cheap first-pass filtering.

## Design implications

- The Council Runner should not expose a generic `model` field first. It should expose `worker_backend`, `auth_route`, `sandbox`, `output_parser`, and `budget_policy`.
- The scheduler should scrub dangerous cost variables by default: `ANTHROPIC_API_KEY`, `CODEX_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, unless the worker config explicitly opts into API billing.
- Each backend needs a health-check that does not run a paid model prompt: binary present, version, auth status if available, config path, and help checksum.
- For reproducibility, every run should store CLI version, exact command argv, relevant env allowlist, output format, exit code, and artifacts.

Related: [[one-shot-cli-execution]], [[cli-worker-backends]], [[hermes-orchestrated-ai-council]], [[agent-red-team-methodology]].
