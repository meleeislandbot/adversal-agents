---
name: adversal-coordinator
description: Configure, resume, and operate an Adversal cold-iron mathematical verification project from a fresh Hermes profile. Use when the user asks to bootstrap or continue Adversal setup, inspect readiness, run an ideation or verification mission, coordinate isolated mathematical workers, interpret a verdict, or update the gated project wiki.
---

# Adversal Coordinator

Coordinate the protocol; never decide truth by model judgment.

## Orient

1. Locate the project root containing `.adversal/project.yaml`. Do not assume the
   source-repository checkout is the runtime project.
2. Read `docs/epistemics.md`, `.adversal/project.yaml`, and
   `llm-wiki/index.md` completely before a mission or promotion.
3. Use only these statuses: `proven`, `known`, `refuted`, `contested`,
   `conjecture`, `sketch`, `not_established`.
4. Treat worker JSON as proposals. The verdict engine and independent validators
   are authoritative.

## Resume bootstrap

When `.adversal/bootstrap/state.json` has phase `restart_required`:

1. Read `.adversal/bootstrap/instructions.md` and the state file.
2. Run `.adversal/bootstrap/bootstrap_adversal.py resume` from the project. It is
   the helper snapshot recorded during the first session.
3. Pass the current profile's verified `HERMES_HOME`; never guess a profile path.
4. Continue from the recorded phase. Do not repeat completed writes.

If the helper snapshot fails its recorded hash check, clone the recorded
repository, check out the exact 40-character commit in the state file, and
recover it from there. Do not continue from a moving branch.

## Run a mission

1. Convert the user's idea into a bounded claim. Require both the exact Lean
   `formal_statement` and declaration name before `proven` is possible. If the
   project has a map (`.adversal/map/map.json`), prefer targets from
   `scripts/map_tool.py next` and use the node id as the claim id, so the gate's
   ledger colors the map; work outside the map is a side quest and must be
   labeled as such. Draw or extend the map with `scripts/decompose.py`
   proposals, importing only the pieces the user accepts.
2. Decide the roles, providers, timeouts, and cost boundary before dispatch.
3. Ask before login, credentials, metered APIs, or exceeding the agreed budget.
   On a worker auth error (`Not logged in`), relay the adapter's printed fix —
   for Claude Code: the user runs `claude setup-token` in their own terminal and
   stores the token as `CLAUDE_CODE_OAUTH_TOKEN` in the profile env, then
   restarts. Do not ask the user to log in interactively; that does not reach
   spawned workers.
4. Invoke `scripts/run_mission.py`; do not manually shuttle worker drafts.
5. Read `verdict.json` and report what the gate checked, artifact paths,
   unresolved dissent, and the next checkable step.
6. Before presenting any `proven` as settled, run
   `scripts/backtranslate.py --claim-id <id> --run <run>` and relay the
   side-by-side report: the user compares the back-translation with their
   original claim. A quantifier/bound/number mismatch means the formalization is
   wrong, whatever the kernel said about it.

Use `scripts/ideate.py` only for divergent generation. Its output is unverified
and never enters canonical knowledge directly. Before the first serious
ideation or decomposition on a goal, run a bibliography sweep: search the
literature with YOUR web tools (workers never browse), verify each link loads,
and record entries via `scripts/bibliography.py add` — dead ends with their
reason. Generation then grounds on the digest automatically and each direction
must declare its nearest known program and differential bet; relay those
declarations to the user when presenting proposals.

## Promote knowledge

Promote only through a deterministic promotion command that consumes a
gate-produced verdict and preserves provenance. If the installed project has no
such command, do not edit canonical wiki sections manually; report promotion as
unavailable. Never promote `not_established`, `conjecture`, `sketch`, or
`contested`.

`refuted` is earned only by a kernel-checked Lean disproof of the exact negation
(declaration `<theorem_name>_disproof`); refutation prose and worker-authored
counterexample text remain leads. An independent citation validator does not
exist yet, so prior-art proposals remain leads and cannot become `known`.
Inspect the installed gate rather than assuming roadmap items are complete.
Run `scripts/reverify.py` before promoting to the wiki: a `proven` that no
longer re-checks is a regression, not a result.

## Worker auth verification

`adversal_doctor.py --json` checks CLI presence and `--version` exit code. A
`present: true` worker can still be unauthenticated. **The only definitive auth
check is a real smoke test** (`run_mission.py` without `--dry-run`). A worker
that fails every role with "Not logged in" or "quota exhausted" is not usable
regardless of what the doctor reports.

Pre-flight checklist before a real mission:

1. Run `scripts/adversal_doctor.py --json` for presence.
2. Check `.adversal/workers/status.md` for the last known auth state.
3. If a worker has never passed a smoke test, run one with a trivial claim
   (`∀ n : Nat, n = n`, theorem `setup_refl`) before trusting it with real work.
4. Treat `adversal_doctor.py`'s `gate_available: false` as a PATH-level warning,
   not final evidence that Lean is unavailable: the verdict engine also resolves
   `~/.elan/bin/lake` and `~/.elan/bin/lean`. Before stopping or proposing an
   installation, check those executable paths and run their `--version` commands.
   If they work, proceed; the gate will use the same fallback.

## Stop conditions

Stop and ask for ambiguous mathematical scope, profile/global writes, toolchain
installation, authentication, secrets, paid routes, destructive actions,
budget breaches, or non-convergence after the configured repair limit.
