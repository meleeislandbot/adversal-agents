# Adversal project rules

Read `docs/epistemics.md` before substantial work. Model agreement is not truth,
and `proven` requires an exact Lean artifact accepted by the kernel.

Use only: `proven`, `known`, `refuted`, `contested`, `conjecture`, `sketch`,
`not_established`. Treat worker output as an attributed proposal, never as a
verdict.

The coordinator manages process but does not decide truth. Workers remain
isolated and communicate through schema-valid files under
`.adversal/runs/<run-id>/workers/`. The deterministic gate decides from those
artifacts.

Safe local writes belong under `.adversal/` and in the project-local
`llm-wiki/`. Canonical wiki entries require deterministic promotion from a
gate-produced verdict. Preserve dissent and provenance; never overwrite them.

Ask before provider selection, authentication, secrets, metered API usage,
toolchain installation, global configuration, destructive actions, budget
breaches, or ambiguous mathematical scope. Check secret-bearing environment
variables by presence only.
