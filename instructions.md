# Adversal Agents — self-bootstrap contract for a fresh Hermes profile

You are both the one-time setup agent and the Hermes profile that will become
the coordinator. The user will not relay technical steps between agents. Starting
from this document, acquire the repository, configure the **currently active
profile**, initialize a separate project, and validate the result.

Do not assume this repository is already cloned, a particular operating system,
a profile name or path, installed tools, provider CLIs, authentication, or paid
API permission. Discover each fact on the target machine.

The governing rule is in `docs/epistemics.md`: model agreement is not truth;
`proven` requires an exact Lean artifact accepted by the kernel; the honest
default is `not_established`.

## Safety and authority

Continue automatically for read-only diagnostics, cloning this public repository,
creating a new project directory, and running local deterministic tests.

Stop and ask immediately before:

- modifying the active Hermes profile, including `SOUL.md`, skills, or toolsets;
- overwriting any existing file;
- installing Lean, a package manager, a provider CLI, or any other toolchain;
- login, device-code flows, credentials, secrets, or API keys;
- paid/metered model calls or a route whose cost is unclear;
- sudo, global shell/configuration changes, destructive actions, or ambiguous
  mathematical/project scope.

Never print secret values. Check credential environment variables by presence
only. Do not create, switch, or modify a different Hermes profile.

## Persistent state and restart rule

The deterministic helper stores progress in:

```text
<project>/.adversal/bootstrap/state.json
```

Completed phases are not repeated. Installing `SOUL.md` does not change the
identity of the session already running, so setup deliberately crosses one new
session. The helper records this boundary as phase `restart_required`. Never
pretend the new identity is active before that restart.

## Phase 0 — identify the active profile and target project

1. Confirm that this conversation is running inside the profile the user wants
   to convert. Do not infer the path from the profile's display name.
2. Resolve its effective `HERMES_HOME` from the environment or the profile-aware
   native Hermes config command. Hermes CLI syntax varies: inspect `--help` and
   use the current profile alias when plain `hermes` would target the default.
3. Verify read-only that the directory exists and contains the current profile's
   `SOUL.md`/configuration. Do not read `.env` values.
4. Ask the user for the runtime project root if it was not supplied. It must be
   separate from the Adversal source checkout. A project name or mathematical
   goal is a user decision.

If the active profile home cannot be identified unambiguously, stop. Writing to
a guessed profile is forbidden.

## Phase 1 — acquire one immutable source checkout

1. Check for `git` and Python 3. If either is missing, explain the exact blocker
   and ask before installing anything.
2. Clone this repository into a disposable setup directory:

   ```text
   https://github.com/meleeislandbot/adversal-agents.git
   ```

   If an existing checkout is offered, verify its `origin` before using it.
3. Record `git rev-parse HEAD` and use that exact checkout for the entire setup.
   Confirm that `origin` is the repository above and that `git status --porcelain`
   is empty. Do not bootstrap from modified/untracked source files or switch back
   to a moving branch midway through setup.
4. From the checkout, read `docs/epistemics.md`, `docs/setup-contract.md`, and
   this file completely.

Run the read-only preflight:

```bash
python3 <source>/scripts/bootstrap_adversal.py inspect \
  --project <absolute-project-root> \
  --profile-home <absolute-HERMES_HOME> --json
```

Adapt shell syntax to the detected operating system; do not change the meaning
of the arguments.

## Phase 2 — configure this profile and initialize the project

Present one concise change plan containing:

- active profile home;
- target project root;
- repository version and full commit;
- `SOUL.md` replacement and backup path;
- bundled `adversal-coordinator` skill installation;
- project template and context files to be created;
- confirmation that no credentials, providers, or packages will be touched.

Ask for explicit approval of both the profile write and project initialization.
After approval, run:

```bash
python3 <source>/scripts/bootstrap_adversal.py apply \
  --project <absolute-project-root> \
  --profile-home <absolute-HERMES_HOME> \
  --approve-profile-write --approve-project-write --json
```

The helper fails closed on non-identical existing files and refuses to instantiate
inside the source checkout. Do not bypass those checks with manual copies.

Read the emitted `continuation_prompt`. Tell the user to start a **new session in
the same profile** and paste that prompt. Stop the current session here.

## Phase 3 — resume in the newly configured profile

In the new session:

1. Load the `adversal-coordinator` skill.
2. Read `<project>/.adversal/bootstrap/state.json` and its snapshotted
   `.adversal/bootstrap/instructions.md`.
3. Use the snapshotted helper at
   `<project>/.adversal/bootstrap/bootstrap_adversal.py`. If its hash check fails,
   clone the recorded repository and check out the exact recorded commit.
4. Run:

   ```bash
   python3 <project>/.adversal/bootstrap/bootstrap_adversal.py resume \
     --project <absolute-project-root> \
     --profile-home <absolute-HERMES_HOME> --json
   ```

The command verifies the installed `SOUL.md`, skill, project, and profile identity
before advancing the checkpoint.

## Phase 4 — discover Hermes capabilities

Use the current profile's native CLI/alias and read-only commands first:

- profile details and doctor/status;
- enabled toolsets;
- installed/enabled skills;
- effective terminal working directory.

Required capabilities are `file`, `terminal`, `code_execution`, `web`, `skills`,
`todo`, `memory`, `session_search`, `clarify`, and `delegation`. Browser and cron
are optional. Computer control, messaging, smart-home, media, and other broad
side-effect tools are not required.

The bundled `adversal-coordinator` skill must be present. Check for `llm-wiki`
and the official worker skills corresponding to providers the user later selects.
Do not recreate official skills. Ask before enabling toolsets or installing
missing skills because those are profile writes and may use the network.

Install the bundled Hermes plugin (a profile write — ask first). It gives the
coordinator the typed `adversal` toolset, the cold-iron guard over gate-owned
files, and per-turn map status. Plugins are **profile-scoped**: copy from the
source checkout into the active profile's home, then enable both the plugin and
its toolset with the profile-aware CLI:

```bash
cp -R <source>/integrations/hermes-adversal <HERMES_HOME>/plugins/hermes-adversal
hermes plugins enable hermes-adversal   # use the profile alias/-p flag if not default
hermes tools enable adversal
```

The plugin needs no built-in tool overrides (decline that privilege if
prompted) and takes effect on the next session. If plugin support is
unavailable, the system still works through the terminal scripts; note it in
the readiness report.

Configure the profile's default terminal working directory to the instantiated
project only after showing the exact path and receiving approval.

## Phase 5 — install and verify the Lean gate

From the project root, run:

```bash
python3 scripts/adversal_doctor.py --json
```

If `gate_available` is false, explain that nothing can become `proven`. Ask before
installing the official Lean toolchain through `elan`; adapt to the detected OS
and avoid sudo or global shell edits unless separately approved.

The project already pins matching Lean and mathlib releases in `lean-toolchain`
and `lakefile.toml`. Once Lean is available, ask before fetching mathlib, then run
`lake update` and `lake build`. Confirm `lake env lean --version` from the project.

## Phase 6 — discover and select workers

Run the doctor again. For every candidate provider:

1. Check CLI presence and version.
2. Check relevant API-key environment variables by **name/presence only**.
3. Determine whether the route is subscription-native, local, metered API, or
   unknown. Never infer this from the model name alone.
4. Ask the user which providers to activate. Provider selection belongs to the
   user.
5. If login is required, stop at that provider, request permission, and set up
   the provider's **headless** route — an interactive login alone is usually not
   enough for spawned workers:

   - **Claude Code.** The interactive `claude` login typically does not reach
     agent-spawned workers: on macOS the keychain secret is bound to the GUI
     session and the fallback file token expires within hours, so `claude -p`
     reports `Not logged in · Please run /login` even though the user is, in
     fact, logged in. Do not tell the user to log in again. Relay these exact
     steps and wait for confirmation:
     1. "In your own terminal, run `claude setup-token` and finish the browser
        sign-in with your Claude subscription account."
     2. "Store the printed token yourself as `CLAUDE_CODE_OAUTH_TOKEN` in the
        environment that launches the workers — for a Hermes coordinator, add
        the line to the profile's `.env`, then restart the profile. Never
        commit it, never paste it into chat."
     The token bills to the subscription, not a metered API; the Claude adapter
     passes it through and scrubs only `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`.
     The adapter prints these same steps whenever a worker hits an auth failure.
   - **Codex CLI.** `codex login` writes file-based credentials that spawned
     workers can read; no extra wiring is needed. An exhausted quota or rate
     limit is not an auth failure — it clears at the plan's reset.

6. Prove auth from the worker's own context before recording it: run one
   trivial worker call from the coordinator's terminal toolset and require a
   non-auth-error reply. A login that works only in the user's interactive
   terminal does not count toward `workers_ready`.

Record the route and cost risk in `.adversal/ledgers/budget.jsonl`. A CLI being
installed does not prove it is authenticated or free to use.

## Phase 7 — deterministic acceptance tests

Before any real mathematics, run all checks that do not call a model:

```bash
python3 scripts/verdict_engine.py --selftest
python3 scripts/verdict_engine.py --selftest-lean
python3 scripts/run_mission.py \
  --statement "For every natural number n, n equals n." \
  --claim-id SETUP-DRY-RUN \
  --formal-statement "∀ n : Nat, n = n" \
  --theorem-name setup_refl \
  --providers claude,codex --dry-run
```

The kernel self-test must accept a true exact theorem and reject a false theorem,
`sorry`/`admit`, path escapes, unrelated declarations, and introduced axioms —
and must grant `refuted` only to a kernel-checked Lean disproof of the exact
negation, rejecting axiom-smuggled disproofs. The ordinary self-test must confirm
that praise, consensus, worker-authored citations, and worker-authored
counterexample prose cannot earn a verdict.

An independent citation validator is not implemented yet. Therefore setup must
**not** demand a `known` verdict; its fail-closed `not_established` behavior is
the acceptance criterion until that validator exists. `refuted` is earnable, but
only through a kernel-checked disproof, so an injected-error mission may honestly
end `refuted` (skeptic constructed a checkable disproof) or `not_established`
with the break recorded as a lead — either is acceptable; silence about the flaw
is not.

A real provider smoke mission is optional and requires explicit approval because
it consumes subscription quota or money. Core readiness must not depend on an
unapproved model call.

Finally run the deterministic readiness recorder:

```bash
python3 <project>/.adversal/bootstrap/bootstrap_adversal.py verify \
  --project <absolute-project-root> \
  --profile-home <absolute-HERMES_HOME> --record --json
```

It returns non-zero until the profile restart, project markers, Lean self-test,
mathlib build, and verdict self-test all pass. Do not edit its readiness booleans
by hand.

## Phase 8 — readiness report

Report separate booleans, never a vague "ready":

- `bootstrap_complete`: profile identity, skill, restart, and project checkpoint;
- `gate_ready`: Lean/mathlib and kernel self-test passed;
- `deterministic_core_ready`: verdict and dry-run pipeline passed;
- `workers_ready`: selected CLIs are present, authenticated, and route-checked;
- `real_worker_smoke_tested`: an approved model mission succeeded.

Include the project root, source commit, selected providers, cost risks, created
paths, failed checks, and exact next action. Do not mark a missing or untested
component ready. Detailed state belongs under `.adversal/`, not profile memory.
