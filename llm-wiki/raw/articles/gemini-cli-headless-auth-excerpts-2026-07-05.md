---
source_url: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md ; https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/authentication.mdx ; npx @google/gemini-cli --help
ingested: 2026-07-05
sha256: 1e141f587f15e8aad4dd6519b9c5c716f91c80cf1fb6566b62c760403f31cd3f
source_type: docs
---

# Gemini CLI headless and auth excerpts — 2026-07-05

Inspected Gemini CLI docs from the official GitHub repository and `npx -y @google/gemini-cli --help`.

## Installation / availability

Gemini CLI can be installed globally with npm or Homebrew, or run with npx:

```bash
npx @google/gemini-cli
npm install -g @google/gemini-cli
brew install gemini-cli
```

NPM reported `@google/gemini-cli` latest `0.49.0` and preview/nightly channels. The `gemini` binary was not installed locally during inspection.

## One-shot / headless mode

Official docs: headless mode is triggered when non-TTY or with `-p/--prompt`.

```bash
gemini -p "summarize README.md"
cat logs.txt | gemini -p "summarize errors"
gemini -p "query" --output-format json
gemini -p "query" --output-format stream-json
```

Headless JSON output returns `response`, `stats`, and optional `error`. Streaming JSON emits events: `init`, `message`, `tool_use`, `tool_result`, `error`, `result`. Exit codes documented: `0` success, `1` general/API failure, `42` input error, `53` turn limit exceeded.

Local help confirms flags: `--model`, `--prompt`, `--output-format text|json|stream-json`, `--sandbox`, `--approval-mode default|auto_edit|yolo|plan`, `--skip-trust`, `--include-directories`, `--session-id`, and `--resume`.

## Auth / subscription notes

Authentication docs recommend Sign in with Google for local individual users, including free tier, Google AI Pro, and Ultra accounts. The auth table recommends API key or Vertex AI for headless mode. This creates an important design question for subscription-first automation: verify whether cached Google sign-in works reliably for local headless runs, and fall back to API key/Vertex only when cost is acceptable.

## Environment/config surfaced

- `GEMINI_API_KEY`: Gemini API key.
- `GEMINI_MODEL`: default model.
- `GEMINI_CLI_TRUST_WORKSPACE`: trust current workspace for headless/CI.
- `GEMINI_CLI_HOME`: alternate user-level config/storage root.
- `GEMINI_CLI_SURFACE`: custom User-Agent label.
- `GOOGLE_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_LOCATION`: Google Cloud/Vertex paths.
- `GOOGLE_GEMINI_BASE_URL`, `GOOGLE_VERTEX_BASE_URL`: endpoint overrides.
- `GEMINI_SANDBOX`: enable sandbox, accepts `true`, `false`, `docker`, `podman`, or custom command string.
- `GEMINI_SYSTEM_MD`: replace built-in system prompt with markdown file.
- `SEATBELT_PROFILE`: macOS sandbox profile selection.
- `NO_COLOR`: disable color output.
