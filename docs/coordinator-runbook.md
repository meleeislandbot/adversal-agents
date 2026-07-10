# Coordinator runbook — where Hermes fits

The tools (the gate, the roles, the worker adapters) are the hands. **Hermes is
the head that drives them.** Your brother only ever talks to Hermes; Hermes does
everything else through files and scripts, and never decides truth itself.

## The mental model

```text
  your brother  ─────talks only to────▶  HERMES (coordinator profile)
                                            │  turns a claim into a mission
                                            │  runs the loop, watches budget
                                            ▼
                              run_mission.py  (one command = one mission)
                                            │  dispatches each role, isolated
                        ┌───────────────────┼───────────────────┐
                        ▼                   ▼                   ▼
                    formalizer       prior-art-auditor       skeptic
                  (Claude/Codex)       (Claude/Codex)      (Claude/Codex)
                        └───────────────────┼───────────────────┘
                                            ▼
                                  verdict_engine.py  (the gate: Lean + rules)
                                            │  proven / known / refuted / …
                                            ▼
                              ledgers + verdict  ──▶  Hermes reports in plain words
```

Hermes is the **secretary general**, not the mathematician and not the judge. It
coordinates; the Lean kernel and the deterministic rules decide.

## What Hermes actually does, step by step

When your brother says, e.g., "I think I can show every zero has real part 1/2 by
this monotonicity argument", Hermes:

1. **Restates it as a bounded claim** and confirms the exact statement.
2. **Runs the mission** — a single command, no human relay:
   ```bash
   python3 .adversal/../scripts/run_mission.py \
     --statement "<the exact claim>" --claim-id C1 \
     --providers claude,codex
   ```
   (In an instantiated project the scripts live under the project's `scripts/`.)
   This dispatches the formalizer, prior-art auditor, and skeptic as isolated
   Claude and Codex workers, then runs the gate. Omit `--providers` to retain
   the lower-cost Claude-only default.
3. **Reads the verdict** (`verdict.json`) — it does not form its own opinion of
   whether the proof is right.
4. **Reports in plain language**, using only the allowed statuses: "Not
   established. The skeptic broke it at step 4; the prior-art auditor says the
   lemma you leaned on is Mertens' theorem (1874). Zero new results." Never
   "great progress" or "you're close".
5. **Keeps the ledgers** so there is a durable, honest record of what has ever
   been proven vs. merely conjectured.

## Two phases: imagine, then verify

Hard mathematics needs bold, cross-field ideas — but imagination in a model is the
same faculty as confabulation, so the two are kept separate, never blended.

1. **Ideate (divergent).** `ideate.py --topic "..."` runs the strategist several
   times with different angles (import a distant field, attack a hidden
   assumption, reason by analogy, invent a definition) to get a *spread* of bold
   directions. Each is forced to a precise, falsifiable statement plus a concrete
   next checkable step. Output is a menu of **unverified directions** — never
   results, nothing promoted to the brain.
2. **Verify (convergent).** Hermes (or the researcher) picks a promising
   direction and runs its next step as a mission (`run_mission.py`), where the
   formalizer, prior-art auditor, skeptic, and the Lean gate decide.

Be as wild as you like in phase 1; be ruthless in phase 2. The gate is what makes
wild ideas affordable: you can generate many and let the kernel filter, instead
of trusting any single one.

## The map: progress you can see, importance by position

The gate answers "is this established?". The map answers "does it move us toward
OUR goal?" — mechanically. It is a dependency blueprint (the Lean community's
"blueprint" practice): the goal at the top, ingredient lemmas below it, each
node colored from the gate's ledger only. Nobody — including the coordinator —
can paint a node green.

```bash
python3 scripts/map_tool.py init --goal "<the declared goal>"   # once per goal
python3 scripts/decompose.py --target GOAL                      # strategist proposes pieces
python3 scripts/map_tool.py import --proposal <run>/proposal.json --only <ids the user accepts>
python3 scripts/map_tool.py next        # ready targets, as run_mission commands
python3 scripts/map_tool.py render      # regenerate .adversal/map/map.md
```

Working rules:

- **A result matters iff it colors a map node** (or supports one). Anything else
  is a side quest — park it without drama; `check` flags orphans.
- **Run missions with the node id as `--claim-id`** so the ledger and the map
  stay joined. `map_tool.py next` prints the exact commands.
- The map is a **plan, not a verdict**: models propose decompositions
  (`decompose.py`), the user accepts pieces, and wrong branches die in the open
  (a red node is information). Redraw freely; colors always re-derive.
- Progress reporting to the user is the map turning green from the leaves up —
  never adjectives.

**Viewing it.** `python3 scripts/map_tool.py export-obsidian` writes a
vault-visible `map/` folder: one note per node plus `Map.canvas`, a JSON-Canvas
dashboard Obsidian renders natively (no plugin) — goal on top, cards colored
from the gate's ledger, arrows toward the goal, click a card to open its lemma
note. Open the project folder as an Obsidian vault and open `map/Map.canvas`;
every `render` refreshes the view, so it updates after each mission. Obsidian's
graph view works too (suggested color groups: `tag:#map/proven` green,
`tag:#map/refuted` red). Without Obsidian, `.adversal/map/map.md` carries the
same information as text.

## Statement fidelity: the back-translation check

`proven` certifies the **formal** statement; nothing certifies that the formal
statement says what the user meant — and this project's users cannot read Lean.
Before celebrating any `proven` (and ideally before running the mission), run:

```bash
python3 scripts/backtranslate.py --claim-id C1 --run .adversal/runs/<run-id> --lang es
```

An isolated worker sees ONLY the Lean proposition — never the original claim —
and translates it back to plain language. Relay the side-by-side report and have
the user compare the two sentences: if any quantifier, bound, hypothesis, or
number differs, the formalization is wrong regardless of what the kernel said
about it. The tool never rules "equivalent"; the human comparison is the check.

## Mathematical CI: reverify what was ever proven

```bash
python3 scripts/reverify.py --project .
```

Re-runs the kernel check on every artifact the gate ever marked `proven`, with
the same strictness. Anything that no longer checks — including runs recorded
before canonical formal statements existed — is reported as a regression and the
map marks it with ⚠ until it checks again. Run it after toolchain or mathlib
changes, before promoting to the wiki, and periodically (it is cheap relative to
missions and needs no model calls).

## Refuted now has teeth — and only kernel teeth

A skeptic's `refuted` vote counts only when it comes with a Lean disproof that
kernel-checks against the exact negation `¬ (formal_statement)` (declaration
`<theorem_name>_disproof`), under the same rules as a proof: no `sorry`, no new
axioms. A refutation in prose — however convincing — is recorded as a lead and
the claim stays `not_established`. This protects the user symmetrically: a
hallucinated refutation could kill a correct idea just as a hallucinated proof
could bless a wrong one.

Two independent axes matter, and they are checked separately. **Novelty** — is a
direction already a known program? — is measured by `ideate.py --audit` (the
prior-art auditor). **Truth** — does the next step actually hold? — is measured by
the gate. A direction can be novel and false, known and true, or any mix; only
verifying both tells you which. Generation alone tells you neither.

## Bounded autonomy

Hermes may loop without pestering your brother — propose a lemma, formalize,
check, repair, check again — because the gate stops false steps. It stops and
asks only for: budget limits (turns / usage), a genuinely ambiguous goal, no
convergence after N repairs, or anything with external side effects.

## Cost posture

Workers default to the **subscription login** (the adapter scrubs API-key
variables that would force metered billing). Every call's route and notional
token cost is logged to `.adversal/ledgers/budget.jsonl`. On a Claude Max plan
this draws from the weekly allowance, not your wallet.

Worker calls inherit the CLI's configured effort/model. At high effort a single
strategist call can run several minutes and use heavy tokens, so a wide ideation
sweep consumes real quota. Tune effort down for generation; reserve high effort
for hard formalization.

## Native Hermes toolset (plugin)

The coordinator does not have to build `python3 scripts/...` command lines by
hand. The `hermes-adversal` plugin (source: `integrations/hermes-adversal/`)
registers a typed `adversal` toolset — `adversal_mission`, `adversal_map_*`,
`adversal_decompose`, `adversal_backtranslate`, `adversal_reverify`,
`adversal_ideate` — plus two hooks: a **cold-iron guard** (`pre_tool_call`)
that blocks hand-edits to gate-owned files (ledgers, verdicts, llm-wiki, the
generated map view; only the sanctioned scripts may write there), and a
per-turn **map status injection** (`pre_llm_call`) so the model always knows
the state. Install: copy the folder to `~/.hermes/plugins/hermes-adversal`,
`hermes tools enable adversal`, restart the profile. The guard is best-effort
and fails open — the deterministic gate remains the only source of truth.

## Worker auth is headless auth

A provider counts as authenticated only if it works from the coordinator's
spawned shell — not from the user's interactive terminal. Claude Code's
interactive login is typically invisible to agent-spawned processes (the macOS
keychain secret is GUI-session bound and the fallback file token is
short-lived), so workers fail with `Not logged in · Please run /login` while
the user is, in fact, logged in. Sending the user to log in again will not fix
the workers.

The durable route: the user runs `claude setup-token` in their own terminal and
stores the result as `CLAUDE_CODE_OAUTH_TOKEN` where the coordinator's terminal
sees it — for Hermes, the profile's `.env`, followed by a profile restart. The
adapter passes that variable through (it scrubs only the metered
`ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`), labels the route
`subscription-token` in the budget ledger, and prints these same steps on every
auth failure — relay them verbatim rather than improvising. Codex CLI stores
file-based credentials that spawned shells can read, so `codex login` suffices;
its quota-exhausted errors are not auth failures and clear at the plan's reset.

## Setup: the profile bootstraps itself

The deployment assumes no separate technical agent. The user creates one fresh
Hermes profile and pastes the README prompt into it. That same profile discovers
its environment, clones an immutable source checkout, asks for the required
permissions, installs its own Adversal identity/skill, and initializes the
project through `bootstrap_adversal.py`.

After the profile changes `SOUL.md`, it checkpoints and stops. A new session in
the same profile resumes setup, verifies the installed hashes, configures Lean
and the user-selected worker routes, then runs deterministic acceptance tests.

Providers are workers, not additional Hermes profiles. CLI syntax, paths,
operating system, installed skills, and auth routes are discovered on the target
machine rather than copied from the development machine.
