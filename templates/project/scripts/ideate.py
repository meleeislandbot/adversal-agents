#!/usr/bin/env python3
"""Divergent ideation: many bold candidate directions for one topic.

This is the imaginative front end. It runs the strategist role several times, each
with a different angle-provocation, to get a SPREAD of directions rather than one
safe answer. Because it is deliberately generative, it is also deliberately
labelled: everything it produces is an UNVERIFIED direction with a concrete next
step — never a result. Pick a promising one and run it as a verification mission
(`run_mission.py`), where the gate decides.

Diversity here comes from independent samples and distinct angles. Claude Code
headless does not expose a temperature knob; broader diversity arrives when the
other provider adapters land and different models take the same angles.

Usage:
    python3 ideate.py --topic "ways to bound the zeros of zeta on the critical line"
    python3 ideate.py --topic "..." --n 5 --dry-run
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

# How mathematicians actually find new angles. One per divergent sample.
ANGLES = [
    "Import a tool from a DISTANT field (random matrices / probability, physics, "
    "combinatorics, logic / model theory, dynamics, algebraic geometry) and say why "
    "it might bite here.",
    "Attack a hidden assumption that everyone working on this takes for granted.",
    "Reason by analogy to a RELATED problem that was actually solved, and port the method.",
    "Invent the right definition or object that would make the problem tractable.",
    "Reformulate the problem as a different KIND of statement (spectral, probabilistic, geometric).",
    "Ask what would have to be true for the statement to FAIL, and show why that route is blocked.",
]


def slug(text: str) -> str:
    s = "".join(c if c.isalnum() or c in "-_" else "-" for c in text)[:40]
    return s.strip("-") or "topic"


def main() -> int:
    ap = argparse.ArgumentParser(description="Divergent ideation over one topic")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--project", type=Path, default=Path.cwd())
    ap.add_argument("--n", type=int, default=len(ANGLES), help="number of divergent samples")
    ap.add_argument("--timeout", type=int, default=480,
                    help="per-sample seconds; strategist reasoning can be slow at high effort")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-api", action="store_true")
    args = ap.parse_args()

    n = max(1, min(args.n, 12))
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-ideate-" + slug(args.topic)
    run = args.project / ".adversal" / "runs" / run_id
    (run / "workers").mkdir(parents=True, exist_ok=True)
    (run / "brief.md").write_text(
        f"# Ideation {run_id}\n\nTopic: {args.topic}\n\nDivergent samples: {n}\n",
        encoding="utf-8")

    print(f"ideation {run_id}: {n} divergent sample(s) on: {args.topic}", file=sys.stderr)
    for i in range(n):
        angle = ANGLES[i % len(ANGLES)]
        statement = (
            f"Topic to explore — propose ONE bold, precise, falsifiable direction "
            f"with its next checkable step:\n{args.topic}\n\nAngle to take this time: {angle}")
        cmd = [sys.executable, str(SCRIPTS / "claude_worker.py"),
               "--role", "strategist", "--run", str(run), "--claim-id", f"idea-{i + 1}",
               "--statement", statement, "--suffix", f"-{i + 1}",
               "--timeout", str(args.timeout)]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.allow_api:
            cmd.append("--allow-api")
        result = subprocess.run(cmd, check=False)
        if result.returncode == 2:
            print(f"  ! sample {i + 1} could not run (see stderr)", file=sys.stderr)

    ideas = [json.loads(jf.read_text(encoding="utf-8"))
             for jf in sorted((run / "workers").glob("claude-strategist-*.json"))]
    lines = [f"# Ideation — {args.topic}", "",
             "> These are UNVERIFIED directions, not results. Most will be wrong.",
             "> Each is only worth anything once its next checkable step is verified.",
             "> Nothing here enters the knowledge base until the gate certifies it.", ""]
    for idx, d in enumerate(ideas, 1):
        lines.append(f"## Direction {idx}  ·  status: `{d.get('status_vote', '?')}`")
        lines.append((d.get("raw_text") or "").strip() or "(no content)")
        lines.append("")
    (run / "ideas.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\nrun: {run}")
    print((run / "ideas.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
