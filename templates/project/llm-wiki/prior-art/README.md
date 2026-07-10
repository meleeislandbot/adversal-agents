# Prior art — the curated, link-backed bibliography

Known programs, documented dead ends, partial results, and surveys relevant to
the goal. This section is what stops the divergent phase from re-deriving the
canon or walking into graves others already dug — model memory does both.

**The only writer is `scripts/bibliography.py`.** Every entry requires a
clickable URL (a human can audit any entry in one click), a route tag, and a
status; a `documented-dead-end` additionally requires the recorded reason it
died. Entries land in `entries.jsonl` (append-only, deduplicated by link), and
two views are regenerated from it:

- `digest.md` — compact, prompt-sized. `ideate.py` and `decompose.py`
  auto-detect it and inject it as **forced contrast**: every generated
  direction must name its nearest known program and its differential bet, or
  discard itself. (Prohibition anchors models to the canon; declared contrast
  does not.)
- `index.md` — the full human-readable list with links and provenance.

How entries get here: the **coordinator** (which, unlike the isolated workers,
has web tools) surveys the literature, verifies each link loads, and calls
`bibliography.py add`. Workers never browse.

Trust tier: bibliography is research context, never a verdict. A paper can be
wrong; the kernel cannot. An `active-program` may be joined with a declared
differential bet; a `documented-dead-end` may be revisited only by a bet that
addresses its recorded cause of death.
