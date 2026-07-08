# Worker Status

This file is updated by the setup agent. Do not store secrets here.

| Worker | CLI present | Version | Auth route | Cost risk | Status | Notes |
|---|---:|---|---|---|---|---|
| deterministic | unknown | unknown | local | low | pending | Always preferred for postconditions. |
| claude-code | unknown | unknown | unknown | unknown | pending | Check `claude --version`; beware API-key env overrides. |
| codex-cli | unknown | unknown | unknown | unknown | pending | Check `codex --version`; verify auth route. |
| gemini-cli | unknown | unknown | unknown | unknown | pending | Check `gemini --version`; verify auth route. |
| opencode | unknown | unknown | provider-routed | unknown | pending | Not automatically subscription-native. |
| ollama | unknown | unknown | local | low | pending | Ask before downloading large models. |
