#!/usr/bin/env python3
"""Create a project-local run directory skeleton for Adversal Agents."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="dry-run", help="Short run suffix")
    args = parser.parse_args()

    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in args.name).strip("-") or "run"
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{safe_name}"
    root = Path(".adversal") / "runs" / run_id
    root.mkdir(parents=True, exist_ok=False)
    for name in ["prompt.md", "trace.md", "verdict.md", "budget.json"]:
        (root / name).write_text("", encoding="utf-8")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
