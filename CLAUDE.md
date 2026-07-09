# Claude Code Instructions

Day-to-day entrypoint for Claude Code in this repository.

## Orientation

1. Read [`AGENTS.md`](AGENTS.md) for the shared cross-agent rules.
2. Read [`docs/epistemics.md`](docs/epistemics.md) — the cold-iron contract that
   governs this project. Its core rule: model agreement is not truth, and
   `proven` is granted only by a Lean kernel check.
3. A project's `llm-wiki/` is its canonical brain — verified lemmas, prior art,
   and dead-ends, entered only by gate-certified promotion. It is local
   per-project state; the source repo ships only the template under
   `templates/project/llm-wiki/`.
4. Store run artifacts, claims, objections, and verdicts under `.adversal/`.

## Cold-iron behavior

Do not flatter the user or certify a proof by opinion. The honest default status
is `not_established`. If a run establishes nothing, say so.

## Claude-specific caution

When Claude Code is used as a worker backend, check whether `ANTHROPIC_API_KEY`
or `ANTHROPIC_AUTH_TOKEN` are present by name only — never print secret values.
Warn before using a route that may switch from subscription-native usage to
metered API billing.
