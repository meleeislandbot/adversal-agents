# Knowledge base — the coordinator's brain

This is the project's canonical memory. It obeys the same cold-iron rule as
everything else: **nothing is written here unless the gate certified it, and every
entry carries provenance.** Only the coordinator promotes into it, after a mission.

It is **not** a scratchpad for model prose. Unverified "results", model musings,
and encouragement never enter — a poisoned brain contaminates every future
mission. See `docs/epistemics.md`.

## Sections

- [`verified/`](verified/README.md) — lemmas the Lean kernel accepted (statement +
  link to the `.lean` artifact + run id).
- [`prior-art/`](prior-art/README.md) — known results relevant to the target, with
  real citations.
- [`dead-ends/`](dead-ends/README.md) — approaches that were refuted or would not
  formalize, with the exact failing step.

## Promotion rule

After a mission (`run_mission.py`), the coordinator promotes a claim here only if
the verdict granted it a status:

| Verdict | Goes to | Must include |
|---|---|---|
| `proven`  | `verified/`  | the kernel-checked `.lean` artifact path + run id |
| `known`   | `prior-art/` | the citation (name, author, year, reference) |
| `refuted` | `dead-ends/` | the exact breaking step |

Everything else (`not_established`, `conjecture`, `sketch`, `contested`) stays
out. Nothing enters on a model's say-so.

> This template is empty on purpose. Your project's brain grows only from its own
> verified mission outcomes — it is not shipped pre-filled with anyone else's
> research.
