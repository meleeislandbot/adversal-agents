#!/usr/bin/env python3
"""Claude Code worker adapter for the verification council.

Drives Claude Code headlessly (`claude -p`) in ONE fixed role against ONE claim,
and writes a schema-valid assessment into the run directory. This is the piece
that removes the human messenger: the coordinator calls it once per role, and
workers never see each other's output.

For the `formalizer` role, any Lean source the model returns is written to
`lean/<claim_id>.lean` inside the run so the verdict engine can kernel-check it —
the model is never taken at its word that a proof is correct.

Cost: one subscription-native Claude Code call per invocation (none with
--dry-run). No secret is read or printed. If ANTHROPIC_API_KEY is set, Claude
Code may switch to metered billing; this adapter warns but does not decide.

Usage:
    python3 claude_worker.py --role skeptic --run <dir> \
        --claim-id C1 --statement "The sum of two even integers is even."
    python3 claude_worker.py --role formalizer --run <dir> --claim-id C1 \
        --statement "..." --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_STATUS = {"proven", "known", "refuted", "conjecture", "sketch", "not_established"}
EV_FIELDS = {"type", "ref", "detail", "verified"}
ROLES_DIR = Path(__file__).resolve().parent.parent / "roles"


def build_prompt(role: str, claim_id: str, statement: str) -> str:
    role_file = ROLES_DIR / f"{role}.md"
    role_prompt = role_file.read_text(encoding="utf-8") if role_file.exists() \
        else f"You are the {role} on a mathematical verification council."
    formalizer_note = ""
    if role == "formalizer":
        formalizer_note = (
            '\nIf you formalize the step, also include a top-level key "lean_source" '
            "containing the COMPLETE Lean 4 source (prefer Lean core over mathlib "
            "when possible). Do not include `sorry` or `admit`.\n")
    return f"""{role_prompt}

--- CLAIM UNDER TEST ---
claim_id: {claim_id}
statement: {statement}

--- REQUIRED OUTPUT ---
Respond with ONLY one JSON object, no prose and no markdown fences. Keys:
  claim_id, role, worker, status_vote, evidence, breaks_at, confidence, raw_text
- status_vote is one of: proven, known, refuted, conjecture, sketch, not_established
- evidence is a list of objects {{type, ref, detail}} where type is one of:
  lean, citation, counterexample, argument
- Put your full reasoning in raw_text.
- Do NOT vote "proven" unless you provide a Lean artifact; the kernel, not you,
  decides if it holds.{formalizer_note}"""


def extract_json(text: str) -> dict | None:
    """Pull the first JSON object out of a model reply (fenced or bare)."""
    candidates: list[str] = []
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        candidates.append(fenced.group(1))
    start = text.find("{")
    if start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start:i + 1])
                    break
    for c in candidates:
        try:
            return json.loads(c)
        except Exception:
            continue
    return None


FAILURE_MARKERS = ("not logged in", "please run /login", "invalid authentication",
                   "401", "authentication_error", "api error", "rate limit")


def looks_like_failure(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in FAILURE_MARKERS)


def call_claude(prompt: str, cwd: Path, timeout: int) -> str:
    """Invoke Claude Code non-interactively and return the model's text."""
    proc = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        cwd=str(cwd), text=True, capture_output=True, timeout=timeout, check=False)
    out = (proc.stdout or "").strip()
    try:  # `--output-format json` wraps the reply as {"result": "...", ...}
        env = json.loads(out)
        if isinstance(env, dict) and "result" in env:
            return str(env["result"])
    except Exception:
        pass
    return out or (proc.stderr or "")


def normalize(obj: dict | None, role: str, claim_id: str, raw: str) -> dict:
    obj = dict(obj or {})
    status = obj.get("status_vote", "not_established")
    if status not in ALLOWED_STATUS:
        status = "not_established"
    evidence = []
    for e in obj.get("evidence", []) or []:
        if isinstance(e, dict) and e.get("type") in ("lean", "citation", "counterexample", "argument"):
            evidence.append({k: v for k, v in e.items() if k in EV_FIELDS})
    return {
        "claim_id": claim_id,
        "role": role,
        "worker": "claude",
        "status_vote": status,
        "evidence": evidence,
        "breaks_at": str(obj.get("breaks_at", "")),
        "confidence": float(obj.get("confidence", 0.0) or 0.0),
        "raw_text": str(obj.get("raw_text", "")) or raw[:6000],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Claude Code worker adapter")
    ap.add_argument("--role", required=True,
                    choices=["strategist", "formalizer", "prior-art-auditor", "skeptic"])
    ap.add_argument("--claim-id", required=True)
    ap.add_argument("--statement", required=True)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--dry-run", action="store_true",
                    help="write an honest placeholder assessment without calling Claude")
    args = ap.parse_args()

    (args.run / "workers").mkdir(parents=True, exist_ok=True)
    if os.getenv("ANTHROPIC_API_KEY"):
        print("warning: ANTHROPIC_API_KEY is set; Claude Code may use metered billing.",
              file=sys.stderr)

    failed = False
    if args.dry_run:
        obj = normalize({"raw_text": f"[dry-run] no model called for role {args.role}."},
                        args.role, args.claim_id, "")
    else:
        prompt = build_prompt(args.role, args.claim_id, args.statement)
        raw = call_claude(prompt, args.run, args.timeout)
        if looks_like_failure(raw):
            # A worker that could not run is NOT the same as a worker that judged
            # nothing. Signal it loudly so the coordinator does not count it.
            failed = True
            print(f"error: Claude worker could not run (role {args.role}): "
                  f"{raw.strip()[:200]}", file=sys.stderr)
        parsed = extract_json(raw)
        obj = normalize(parsed, args.role, args.claim_id, raw)
        # For the formalizer, persist any Lean source and point evidence at it so
        # the kernel — not the model's say-so — decides whether it is proven.
        if args.role == "formalizer" and isinstance(parsed, dict) and parsed.get("lean_source"):
            (args.run / "lean").mkdir(parents=True, exist_ok=True)
            lean_path = args.run / "lean" / f"{args.claim_id}.lean"
            lean_path.write_text(str(parsed["lean_source"]), encoding="utf-8")
            obj["evidence"] = [{"type": "lean", "ref": f"lean/{args.claim_id}.lean"}]

    out_path = args.run / "workers" / f"claude-{args.role}.json"
    out_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print(out_path)
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
