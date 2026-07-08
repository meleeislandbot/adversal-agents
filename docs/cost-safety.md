# Cost Safety

Adversal Agents defaults to cost-aware orchestration.

## Preferred order

1. Deterministic checks.
2. Local scripts/tools.
3. Local models.
4. Subscription-native CLIs.
5. Metered APIs only after explicit approval.

## Required budget fields

Each worker/run should record:

```json
{
  "timestamp": "ISO-8601",
  "event": "worker_check | run_start | run_end | approval | warning",
  "worker": "claude-code | codex-cli | gemini-cli | opencode | ollama | deterministic | api",
  "auth_route": "subscription | local | api-key | unknown | not-applicable",
  "cost_risk": "low | medium | high | unknown",
  "notes": "short human-readable note"
}
```

Never record secret values.
