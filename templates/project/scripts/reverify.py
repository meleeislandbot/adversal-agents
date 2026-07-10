#!/usr/bin/env python3
"""Mathematical CI: re-run the kernel check on everything ever marked proven.

"Proven" is only as good as its reproducibility. This tool walks every recorded
run, finds each claim the gate once granted `proven`, and re-checks its Lean
artifact against the same canonical formal statement, with the same strictness
(exact type, no sorry, no introduced axioms). Anything that no longer checks is
a REGRESSION and is reported loudly; the map renders those nodes with a warning
until the artifact checks again.

A proven verdict that cannot be re-derived from its artifact is treated as not
proven. That includes runs recorded before canonical formal statements existed:
they are listed as unreproducible rather than silently trusted.

Usage:
    python3 reverify.py --project .
    python3 reverify.py --project . --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import verdict_engine  # noqa: E402

REPORT_REL = Path(".adversal") / "map" / "reverify-latest.json"


def proven_items(project: Path) -> list[dict]:
    """Every (run, claim) the gate ever marked proven, newest last."""
    items = []
    runs_dir = project / ".adversal" / "runs"
    if not runs_dir.is_dir():
        return items
    for run_root in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        verdict_file = run_root / "verdict.json"
        if not verdict_file.exists():
            continue
        try:
            verdicts = json.loads(verdict_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            items.append({"run": run_root.name, "claim_id": "<unreadable>",
                          "ok": False, "reason": "verdict.json does not parse"})
            continue
        specs = verdict_engine.claims_for(run_root)
        for v in verdicts if isinstance(verdicts, list) else []:
            if v.get("status") != "proven":
                continue
            items.append({
                "run": run_root.name,
                "run_root": str(run_root),
                "claim_id": v.get("claim_id", "<missing>"),
                "artifact": v.get("lean_artifact", ""),
                "spec": specs.get(v.get("claim_id", "")),
            })
    return items


def recheck(item: dict) -> dict:
    result = {"run": item["run"], "claim_id": item["claim_id"],
              "artifact": item.get("artifact", "")}
    spec = item.get("spec")
    if item.get("ok") is False:  # pre-failed while scanning
        result.update(ok=False, reason=item["reason"])
        return result
    if spec is None or not spec.formal_statement or not spec.theorem_name:
        result.update(ok=False, reason="unreproducible: no canonical formal "
                                       "statement recorded for this claim")
        return result
    if not item.get("artifact"):
        result.update(ok=False, reason="unreproducible: verdict has no artifact path")
        return result
    ok = verdict_engine._lean_check(item["artifact"], Path(item["run_root"]),
                                    spec.theorem_name, spec.formal_statement)
    result.update(ok=bool(ok),
                  reason="kernel re-check passed" if ok else "kernel re-check FAILED")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Re-check every proven artifact against the kernel")
    ap.add_argument("--project", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not verdict_engine._resolve_tool("lean"):
        print("error: Lean is not installed here; cannot re-check anything. "
              "An unchecked 'proven' stays unverified — do not treat this as a pass.",
              file=sys.stderr)
        return 2

    items = proven_items(args.project)
    results = [recheck(i) for i in items]
    regressions = sorted({r["claim_id"] for r in results if not r["ok"]})
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checked": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "regressions": regressions,
        "items": results,
    }
    out = args.project / REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"re-checked {report['checked']} proven artifact(s): "
              f"{report['passed']} passed, {len(regressions)} regression(s)")
        for r in results:
            mark = "ok " if r["ok"] else "FAIL"
            print(f"  [{mark}] {r['run']} / {r['claim_id']}: {r['reason']}")
        print(f"report: {out}")
        if regressions:
            print("\nRegressed claims are NOT proven until their artifact checks "
                  "again. The map marks them with a warning.")
    return 1 if regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
