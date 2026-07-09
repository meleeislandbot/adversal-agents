# Council roles

The council is not a chat. Workers never talk to each other. Each worker is
given one role, reads the shared brief and the claim(s) under test, and writes a
single structured file to `workers/<worker>-<role>.json`. The deterministic
[verdict engine](../scripts/verdict_engine.py) — not any model — decides the
outcome from those files.

The point of the roles is to remove sycophancy by construction. No role is
allowed to certify a proof by opinion. Only the formalizer can produce the one
kind of evidence that grants `proven`, and only the kernel confirms it.

## Roles

| Role | Job | Can it grant "proven"? |
|---|---|---|
| [strategist](strategist.md) | Propose lemmas, decompositions, next steps | No — output is `conjecture`/`sketch` at most |
| [formalizer](formalizer.md) | Translate a specific step into Lean 4 / mathlib | Only via a Lean file the kernel accepts |
| [prior-art-auditor](prior-art-auditor.md) | Is this already a known result? Cite it | No — it can only demote to `known` |
| [skeptic](skeptic.md) | Find the first step that fails | No — it can only refute or withhold |

## Mandatory output contract

Every worker emits JSON matching `.adversal/schema/claim.schema.json`. One object
per claim, or a list. Fields:

```json
{
  "claim_id": "C1",
  "role": "skeptic",
  "worker": "claude",
  "status_vote": "refuted",
  "evidence": [
    {"type": "counterexample", "ref": "", "detail": "s = 1/2 + 14.1i", "verified": false}
  ],
  "breaks_at": "step 4: monotonicity is assumed, never shown",
  "confidence": 0.0,
  "raw_text": "full prose reply, kept for the record"
}
```

`status_vote` must be one of: `proven`, `known`, `refuted`, `conjecture`,
`sketch`, `not_established`. Evidence `type` is one of: `lean`, `citation`,
`counterexample`, `argument`.

Two rules every role must obey:

1. **Confidence is not evidence.** A high `confidence` with no `evidence` is
   discarded. Say what would have to be true, and whether it is verified.
2. **No praise.** Words like "genius", "breakthrough", "you're close" are
   counted and ignored by the engine. They cost you credibility, nothing more.
