# hermes-adversal — native Adversal toolset for the Hermes coordinator

Gives the coordinator hands that match the doctrine. Instead of hand-assembling
`python3 scripts/run_mission.py --statement "..." --formal-statement "..."`
shell lines through the terminal toolset, the model calls typed tools:

| Tool | Wraps | Notes |
|---|---|---|
| `adversal_mission` | `run_mission.py` | claim -> roles -> gate -> ledger; auto-refreshes the map |
| `adversal_map_init` / `add` / `import` / `next` / `status` | `map_tool.py` | colors always derive from the gate's ledger |
| `adversal_decompose` | `decompose.py` | strategist PROPOSAL; import only what the user accepts |
| `adversal_ideate` | `ideate.py` | divergent, UNVERIFIED directions |
| `adversal_backtranslate` | `backtranslate.py` | statement fidelity; the human compares |
| `adversal_reverify` | `reverify.py` | math CI over every recorded `proven`; flags regressions |

Plus two hooks and one command:

- **`pre_tool_call` cold-iron guard** — blocks file/terminal writes that touch
  gate-owned paths (`.adversal/ledgers/`, `verdict.json`, `llm-wiki/`, the
  generated map view) unless the write goes through a sanctioned script. This
  turns "the coordinator must not mint verdicts" from doctrine into mechanism.
  It is best-effort string matching and **fails open**: a guard error never
  takes a turn down, and it is not a substitute for the deterministic gate —
  the gate remains the only source of truth.
- **`pre_llm_call` status injection** — one compact line per turn
  (`[adversal] map toward GOAL: 8 nodes (proven:2, untried:5, ...); ready: L4`)
  so the coordinator knows the state without spending tool calls.
- **`/map`** — human shortcut: counts, ready targets, canvas path.

## Install

```bash
cp -R integrations/hermes-adversal ~/.hermes/plugins/hermes-adversal
hermes tools enable adversal        # or via `hermes tools` interactive UI
# restart the Hermes process/profile
```

Tools and hooks resolve the project in this order: explicit `project` argument
→ `ADVERSAL_PROJECT` env var (set it in the profile's `.env` during setup — it
is a path, not a secret, and it anchors every new session even when the agent
process starts far from the project) → walking upward from the working
directory to the nearest `.adversal/project.yaml`.

## What this plugin is not

It does not decide truth, does not talk to any model itself, and adds no new
write path into the ledgers or the wiki — every state change still flows
through the same deterministic scripts and the Lean gate.
