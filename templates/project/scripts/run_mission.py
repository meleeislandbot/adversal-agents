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
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
DEFAULT_ROLES = ["formalizer", "prior-art-auditor", "skeptic"]
ALLOWED_ROLES = {"formalizer", "prior-art-auditor", "skeptic", "strategist"}
ALLOWED_PROVIDERS = {"claude", "codex"}
SAFE_CLAIM_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def slug(text: str) -> str:
    s = "".join(c if c.isalnum() or c in "-_" else "-" for c in text)[:40]
    return s.strip("-") or "claim"


def main() -> int:
    ap = argparse.ArgumentParser(description="Run one verification mission end to end")
    ap.add_argument("--statement", required=True, help="the claim, in natural language")
    ap.add_argument("--claim-id", default="C1")
    ap.add_argument("--formal-statement", default="",
                    help="canonical Lean type; required before `proven` is possible")
    ap.add_argument("--theorem-name", default="",
                    help="Lean declaration whose type must match --formal-statement")
    ap.add_argument("--project", type=Path, default=Path.cwd(),
                    help="project root containing .adversal/")
    ap.add_argument("--roles", default=",".join(DEFAULT_ROLES),
                    help="comma-separated council roles to dispatch")
    ap.add_argument("--providers", default="claude",
                    help="comma-separated isolated worker providers: claude,codex")
    ap.add_argument("--timeout", type=int, default=480)
    ap.add_argument("--dry-run", action="store_true",
                    help="run the whole pipeline with no model calls")
    ap.add_argument("--allow-api", action="store_true",
                    help="let workers use a metered API route (default: subscription)")
    args = ap.parse_args()

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    unknown_roles = sorted(set(roles) - ALLOWED_ROLES)
    if unknown_roles:
        ap.error(f"unknown role(s): {', '.join(unknown_roles)}")
    unknown_providers = sorted(set(providers) - ALLOWED_PROVIDERS)
    if unknown_providers:
        ap.error(f"unknown provider(s): {', '.join(unknown_providers)}")
    if not providers:
        ap.error("at least one provider is required")
    if not SAFE_CLAIM_ID.fullmatch(args.claim_id):
        ap.error("--claim-id must contain only letters, digits, dot, underscore, or hyphen")
    if bool(args.formal_statement) != bool(args.theorem_name):
        ap.error("--formal-statement and --theorem-name must be supplied together")
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + slug(args.statement)
    run = args.project / ".adversal" / "runs" / run_id
    (run / "workers").mkdir(parents=True, exist_ok=True)

    claim = {"claim_id": args.claim_id, "statement": args.statement}
    if args.formal_statement:
        claim.update({"formal_statement": args.formal_statement,
                      "theorem_name": args.theorem_name})
    (run / "claims.json").write_text(json.dumps([claim], indent=2), encoding="utf-8")
    formal_brief = ""
    if args.formal_statement:
        formal_brief = (
            f"\nCanonical Lean target `{args.theorem_name}`:\n\n"
            f"```lean\n{args.formal_statement}\n```\n"
        )
    (run / "brief.md").write_text(
        f"# Mission {run_id}\n\nClaim {args.claim_id}: {args.statement}\n"
        f"{formal_brief}\nRoles dispatched: {', '.join(roles)}\n", encoding="utf-8")

    print(f"mission {run_id}: {len(roles)} role(s) x {len(providers)} provider(s) "
          f"on claim {args.claim_id}", file=sys.stderr)
    worker_failed = False
    for provider in providers:
        for role in roles:
            cmd = [sys.executable, str(SCRIPTS / f"{provider}_worker.py"),
                   "--role", role, "--run", str(run), "--claim-id", args.claim_id,
                   "--statement", args.statement, "--timeout", str(args.timeout)]
            if args.formal_statement:
                cmd.extend(["--formal-statement", args.formal_statement,
                            "--theorem-name", args.theorem_name])
            if args.dry_run:
                cmd.append("--dry-run")
            if args.allow_api:
                cmd.append("--allow-api")
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                worker_failed = True
                print(f"  ! worker '{provider}/{role}' failed with exit "
                      f"{result.returncode} (see stderr)", file=sys.stderr)

    # The gate decides. The coordinator does not get a vote here.
    gate = subprocess.run(
        [sys.executable, str(SCRIPTS / "verdict_engine.py"), "--run", str(run)],
        check=False)
    if gate.returncode != 0:
        print(f"error: verdict engine failed with exit {gate.returncode}", file=sys.stderr)
        return 3

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
    return 2 if worker_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
