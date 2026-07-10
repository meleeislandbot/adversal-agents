#!/usr/bin/env python3
"""Curated bibliography for the project: known programs and documented dead ends.

This is the sanctioned writer for ``llm-wiki/prior-art/``. It exists because
the divergent phase imagines from model memory, and model memory both re-derives
the canon and forgets the graveyard. A curated, link-backed bibliography gives
the pipeline a second, checkable memory:

- every entry REQUIRES a URL (a human can audit any entry with one click);
- entries are typed: an ``active-program`` is a live route one may join with a
  declared differential bet; a ``documented-dead-end`` is a no-go as stated,
  with the reason recorded; ``partial-result`` and ``survey`` complete the map;
- ``digest`` regenerates a compact block that ``ideate.py``/``decompose.py``
  inject as FORCED CONTRAST: generated directions must name their nearest known
  program and their differential bet, or discard themselves.

Bibliography entries are research context, never verdicts: a paper can be
wrong; the kernel cannot. Nothing here feeds the gate.

Usage:
    python3 bibliography.py add --title "..." --year 1972 \
        --link "https://..." --status active-program --route "spectral" \
        [--authors "..."] [--why-dead "..."] [--notes "..."]
    python3 bibliography.py digest
    python3 bibliography.py list
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PRIOR_ART_REL = Path("llm-wiki") / "prior-art"
ENTRIES_REL = PRIOR_ART_REL / "entries.jsonl"
DIGEST_REL = PRIOR_ART_REL / "digest.md"
INDEX_REL = PRIOR_ART_REL / "index.md"

STATUSES = ("active-program", "documented-dead-end", "partial-result", "survey")
LINK = re.compile(r"^https?://\S+$")
DIGEST_CHAR_BUDGET = 8000  # keep the injected block prompt-sized

STATUS_LABEL = {
    "active-program": "ACTIVE PROGRAMS (live routes; joining one requires a declared differential bet)",
    "documented-dead-end": "DOCUMENTED DEAD ENDS (no-go as stated; the reason is recorded)",
    "partial-result": "PARTIAL RESULTS (established fragments to stand on)",
    "survey": "SURVEYS (maps of the territory)",
}


def load_entries(project: Path) -> list[dict]:
    path = project / ENTRIES_REL
    entries: list[dict] = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # one corrupt line must not take the bibliography down
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def normalize_link(link: str) -> str:
    return link.strip().rstrip("/").lower()


def validate_entry(entry: dict) -> list[str]:
    errors = []
    if not str(entry.get("title", "")).strip():
        errors.append("title is required")
    if not LINK.fullmatch(str(entry.get("link", ""))):
        errors.append("link is required and must be a plain http(s) URL — "
                      "an entry a human cannot click is not bibliography")
    if entry.get("status") not in STATUSES:
        errors.append(f"status must be one of {', '.join(STATUSES)}")
    if not str(entry.get("route", "")).strip():
        errors.append("route is required (short tag: e.g. spectral, sieve, "
                      "random-matrix, translation-from-physics)")
    year = entry.get("year")
    if not (isinstance(year, int) and 1600 <= year <= 2100):
        errors.append("year is required (a plausible integer)")
    if entry.get("status") == "documented-dead-end" and \
            not str(entry.get("why_dead", "")).strip():
        errors.append("a documented-dead-end requires --why-dead: a dead end "
                      "without its reason teaches nothing")
    return errors


def _digest_body(entries: list[dict]) -> str:
    lines = ["# Prior-art digest (generated — do not edit)",
             "",
             "> Curated bibliography, grouped by kind. Injected into divergent",
             "> generation as forced contrast: every proposed direction must name",
             "> its nearest known program here and its differential bet, or",
             "> discard itself. Entries are research context, never verdicts.",
             ""]
    for status in STATUSES:
        group = [e for e in entries if e.get("status") == status]
        if not group:
            continue
        lines.append(f"## {STATUS_LABEL[status]}")
        for e in sorted(group, key=lambda x: (x.get("year", 0), x.get("title", ""))):
            item = (f"- **{e['title']}** ({e.get('authors', '?')}, {e['year']}) — "
                    f"route: {e['route']}")
            if e.get("why_dead"):
                item += f" — why dead: {e['why_dead']}"
            if e.get("notes"):
                item += f" — {e['notes']}"
            lines.append(item)
        lines.append("")
    return "\n".join(lines) + "\n"


def render_digest(entries: list[dict]) -> str:
    text = _digest_body(entries)
    if len(text) <= DIGEST_CHAR_BUDGET:
        return text
    # Newest entries carry the most recent curation; keep as many as fit.
    newest_first = sorted(entries, key=lambda x: x.get("added_at", ""), reverse=True)
    kept: list[dict] = []
    for e in newest_first:
        if len(_digest_body(kept + [e])) > DIGEST_CHAR_BUDGET:
            break
        kept.append(e)
    text = _digest_body(kept)
    text += (f"\n*Digest truncated to the {len(kept)} most recently added "
             f"entries (of {len(entries)}); see index.md for all.*\n")
    return text


def render_index(entries: list[dict]) -> str:
    lines = ["# Prior art — curated bibliography (generated — do not edit)",
             "",
             f"{len(entries)} entr{'y' if len(entries) == 1 else 'ies'}. Every "
             "entry links to its source; click before you trust. Added via "
             "`scripts/bibliography.py` only.",
             ""]
    for status in STATUSES:
        group = [e for e in entries if e.get("status") == status]
        if not group:
            continue
        lines.append(f"## {STATUS_LABEL[status]}")
        lines.append("")
        for e in sorted(group, key=lambda x: (x.get("year", 0), x.get("title", ""))):
            lines.append(f"### [{e['title']}]({e['link']})")
            lines.append(f"- authors: {e.get('authors', '?')} · year: {e['year']} "
                         f"· route: `{e['route']}`")
            if e.get("why_dead"):
                lines.append(f"- **why dead:** {e['why_dead']}")
            if e.get("notes"):
                lines.append(f"- notes: {e['notes']}")
            lines.append(f"- provenance: {e.get('source', '?')}, "
                         f"added {e.get('added_at', '?')}")
            lines.append("")
    return "\n".join(lines) + "\n"


def regenerate(project: Path) -> tuple[Path, Path]:
    entries = load_entries(project)
    digest = project / DIGEST_REL
    index = project / INDEX_REL
    digest.parent.mkdir(parents=True, exist_ok=True)
    digest.write_text(render_digest(entries), encoding="utf-8")
    index.write_text(render_index(entries), encoding="utf-8")
    return digest, index


def cmd_add(args: argparse.Namespace) -> int:
    entry = {
        "title": args.title.strip(),
        "authors": args.authors.strip(),
        "year": args.year,
        "link": args.link.strip(),
        "status": args.status,
        "route": args.route.strip(),
        "why_dead": args.why_dead.strip(),
        "notes": args.notes.strip(),
        "source": args.source.strip(),
        "added_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    errors = validate_entry(entry)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    entries = load_entries(args.project)
    if any(normalize_link(e.get("link", "")) == normalize_link(entry["link"])
           for e in entries):
        print("error: an entry with this link already exists; nothing added "
              "(the bibliography is append-only and deduplicated by link)",
              file=sys.stderr)
        return 1
    path = args.project / ENTRIES_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    digest, index = regenerate(args.project)
    print(f"added [{entry['status']}] {entry['title']} ({entry['year']})")
    print(f"digest: {digest}")
    print(f"index:  {index}")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    digest, index = regenerate(args.project)
    entries = load_entries(args.project)
    print(f"{len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
    print(f"digest: {digest}")
    print(f"index:  {index}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    entries = load_entries(args.project)
    for e in entries:
        dead = f" [why dead: {e.get('why_dead')}]" if e.get("why_dead") else ""
        print(f"[{e.get('status')}] {e.get('title')} ({e.get('year')}) — "
              f"{e.get('route')} — {e.get('link')}{dead}")
    print(f"total: {len(entries)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Curated, link-backed bibliography for llm-wiki/prior-art")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--project", type=Path, default=Path.cwd())

    p = sub.add_parser("add", help="add one entry (link required)")
    common(p)
    p.add_argument("--title", required=True)
    p.add_argument("--authors", default="")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--link", required=True, help="http(s) URL a human can click")
    p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--route", required=True,
                   help="short tag: spectral, sieve, random-matrix, ...")
    p.add_argument("--why-dead", default="",
                   help="required for documented-dead-end")
    p.add_argument("--notes", default="")
    p.add_argument("--source", default="coordinator-web-search",
                   help="who found it and how")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("digest", help="regenerate digest.md and index.md")
    common(p)
    p.set_defaults(fn=cmd_digest)

    p = sub.add_parser("list", help="print all entries")
    common(p)
    p.set_defaults(fn=cmd_list)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
