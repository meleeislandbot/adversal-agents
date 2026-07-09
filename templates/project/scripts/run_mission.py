#!/usr/bin/env python3
"""Run one verification mission end to end: claim -> council roles -> gate.

This is the coordinator's core action. Given a mathematical claim in natural
language, it creates a run, dispatches each council role to a worker adapter
(isolated, one call each), runs the deterministic verdict engine, and records
the outcome in the project ledgers.

Hermes (the coordinator) calls this. The human never shuttles text between
models — that whole loop happens here, and the verdict is decided by the gate,
not by any model's opinion.

Usage:
    python3 run_mission.py --statement "The sum of two even integers is even."
    python3 run_mission.py --statement "..." --roles formalizer,skeptic --dry-run
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
DEFAULT_ROLES = ["formalizer", "prior-art-auditor", "skeptic"]


def slug(text: str) -> str:
    s = "".join(c if c.isalnum() or c in "-_" else "-" for c in text)[:40]
    return s.strip("-") or "claim"


def main() -> int:
    ap = argparse.ArgumentParser(description="Run one verification mission end to end")
    ap.add_argument("--statement", required=True, help="the claim, in natural language")
    ap.add_argument("--claim-id", default="C1")
    ap.add_argument("--project", type=Path, default=Path.cwd(),
                    help="project root containing .adversal/")
    ap.add_argument("--roles", default=",".join(DEFAULT_ROLES),
                    help="comma-separated council roles to dispatch")
    ap.add_argument("--timeout", type=int, default=480)
    ap.add_argument("--dry-run", action="store_true",
                    help="run the whole pipeline with no model calls")
    ap.add_argument("--allow-api", action="store_true",
                    help="let workers use a metered API route (default: subscription)")
    args = ap.parse_args()

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + slug(args.statement)
    run = args.project / ".adversal" / "runs" / run_id
    (run / "workers").mkdir(parents=True, exist_ok=True)

    (run / "claims.json").write_text(
        json.dumps([{"claim_id": args.claim_id, "statement": args.statement}], indent=2),
        encoding="utf-8")
    (run / "brief.md").write_text(
        f"# Mission {run_id}\n\nClaim {args.claim_id}: {args.statement}\n\n"
        f"Roles dispatched: {', '.join(roles)}\n", encoding="utf-8")

    print(f"mission {run_id}: {len(roles)} role(s) on claim {args.claim_id}", file=sys.stderr)
    for role in roles:
        cmd = [sys.executable, str(SCRIPTS / "claude_worker.py"),
               "--role", role, "--run", str(run), "--claim-id", args.claim_id,
               "--statement", args.statement, "--timeout", str(args.timeout)]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.allow_api:
            cmd.append("--allow-api")
        result = subprocess.run(cmd, check=False)
        if result.returncode == 2:
            print(f"  ! worker '{role}' could not run — not counted (see stderr)", file=sys.stderr)

    # The gate decides. The coordinator does not get a vote here.
    subprocess.run([sys.executable, str(SCRIPTS / "verdict_engine.py"), "--run", str(run)],
                   check=False)

    # Record the outcome in the project's append-only ledgers.
    verdicts = []
    if (run / "verdict.json").exists():
        verdicts = json.loads((run / "verdict.json").read_text(encoding="utf-8"))
    ledgers = args.project / ".adversal" / "ledgers"
    ledgers.mkdir(parents=True, exist_ok=True)
    with (ledgers / "decisions.jsonl").open("a", encoding="utf-8") as fh:
        for v in verdicts:
            fh.write(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(), "run": run_id,
                "claim_id": v["claim_id"], "status": v["status"],
                "decided_by": v["decided_by"]}) + "\n")
    if (run / "budget.jsonl").exists():  # fold per-run usage into the project ledger
        with (ledgers / "budget.jsonl").open("a", encoding="utf-8") as out:
            out.write((run / "budget.jsonl").read_text(encoding="utf-8"))

    print(f"\nrun: {run}")
    if (run / "verdict.md").exists():
        print((run / "verdict.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
