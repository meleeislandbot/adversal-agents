#!/usr/bin/env python3
"""Cold-iron verdict engine for the mathematical verification council.

This is the deterministic gate. It takes the structured outputs of the council
workers for one run and computes an honest status for each mathematical claim.

It does NOT average votes and it does NOT let consensus manufacture truth.
A claim becomes ``proven`` only when a machine-checkable artifact backs it.
Everything else defaults to ``not_established``. Praise carries zero weight.

No LLM is called here. No network. Standard library only, so it runs anywhere
and cannot be talked out of its conclusion.

Input:  a run directory containing ``workers/*.json`` files, each conforming to
        the claim-assessment schema (see .adversal/schema/claim.schema.json).
Output: ``verdict.json`` and ``verdict.md`` written into the run directory, and
        a human summary on stdout.

Usage:
    python3 verdict_engine.py --run .adversal/runs/<run-id>
    python3 verdict_engine.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# --- The taxonomy. These are the only words the system may use about a claim. ---
STATUS_PROVEN = "proven"            # backed by a kernel-checked formal artifact
STATUS_KNOWN = "known"              # already in the literature; not new progress
STATUS_REFUTED = "refuted"          # a specific step is false / counterexample exists
STATUS_CONTESTED = "contested"      # workers disagree and nothing resolves it
STATUS_CONJECTURE = "conjecture"    # plausible, unproven
STATUS_SKETCH = "sketch"            # informal argument with acknowledged gaps
STATUS_NOT_ESTABLISHED = "not_established"  # the honest default

# Language that flatters instead of proving. It has no epistemic weight; we count
# it only so the run report can show how much smoke the models blew.
SYCOPHANCY_MARKERS = [
    r"\bgenius\b", r"\bbrilliant\b", r"\bbreakthrough\b", r"\brevolutionary\b",
    r"\bprofound\b", r"\bgroundbreaking\b", r"\bremarkable\b", r"\bstunning\b",
    r"\byou'?re close\b", r"\balmost there\b", r"\bon the verge\b",
    r"\bnobel\b", r"\bfields medal\b", r"\bhistoric\b", r"\bmasterpiece\b",
    r"\bcanela en rama\b", r"\beres dios\b", r"\bgod-?tier\b", r"\bimpressive\b",
    r"\bcongratulations\b", r"\bwell done\b", r"\bexcellent work\b",
]


@dataclass
class Evidence:
    type: str          # lean | citation | counterexample | argument
    ref: str = ""      # file path, DOI, URL, or theorem name
    detail: str = ""
    verified: bool = False  # only set True by an actual kernel/prior-art check


@dataclass
class WorkerAssessment:
    claim_id: str
    role: str                  # formalizer | prior-art-auditor | skeptic | strategist
    worker: str                # which provider produced this (claude, gpt, gemini, ...)
    status_vote: str = STATUS_NOT_ESTABLISHED
    evidence: list[Evidence] = field(default_factory=list)
    breaks_at: str = ""        # the first step that fails, per a skeptic/formalizer
    confidence: float = 0.0
    raw_text: str = ""


@dataclass
class ClaimVerdict:
    claim_id: str
    statement: str
    status: str
    decided_by: str            # which cold-iron rule fixed the status
    novel: bool                # False if it re-derives a known result
    lean_artifact: str = ""
    refutation: str = ""
    prior_art: str = ""
    dissent: list[str] = field(default_factory=list)
    sycophancy_hits: int = 0


def _count_sycophancy(text: str) -> int:
    low = text.lower()
    return sum(len(re.findall(pat, low)) for pat in SYCOPHANCY_MARKERS)


def _resolve_tool(name: str) -> str | None:
    """Find a Lean tool on PATH, or in an elan install that never touched PATH."""
    found = shutil.which(name)
    if found:
        return found
    fallback = Path.home() / ".elan" / "bin" / name
    return str(fallback) if fallback.exists() else None


def _find_lakefile(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if (parent / "lakefile.lean").exists() or (parent / "lakefile.toml").exists():
            return parent
    return None


def _lean_check(ref: str, run_root: Path) -> bool:
    """Return True only if a Lean artifact is confirmed by an actual build.

    If Lean is not installed here we CANNOT confirm it, so we return False.
    Unchecked is not proven. That is the whole point.

    A proof that leans on ``sorry``/``admit`` is not a proof: Lean only warns on
    it and exits 0, so we reject it explicitly. Erring toward "not proven" is the
    correct bias for a truth gate.
    """
    path = (run_root / ref) if not Path(ref).is_absolute() else Path(ref)
    if not path.exists():
        return False
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    if re.search(r"\bsorry\b", src) or re.search(r"\badmit\b", src):
        return False
    try:
        project = _find_lakefile(path.parent)
        if project:  # inside a Lake project (e.g. one using mathlib): full build
            lake = _resolve_tool("lake")
            if not lake:
                return False
            proc = subprocess.run(["lake", "build"], cwd=str(project), text=True,
                                  capture_output=True, timeout=1800, check=False,
                                  env={**os.environ, "PATH": _lean_bin_path()})
        else:  # standalone file: type-check it directly
            lean = _resolve_tool("lean")
            if not lean:
                return False
            proc = subprocess.run([lean, str(path)], text=True, capture_output=True,
                                  timeout=600, check=False)
        out = (proc.stdout + proc.stderr).lower()
        if "sorry" in out or "error" in out:
            return False
        return proc.returncode == 0
    except Exception:
        return False


def _lean_bin_path() -> str:
    """PATH augmented with the elan bin dir so `lake` can find `lean`."""
    elan_bin = Path.home() / ".elan" / "bin"
    base = os.environ.get("PATH", "")
    return f"{elan_bin}:{base}" if elan_bin.exists() else base


def decide(claim_id: str, statement: str, assessments: list[WorkerAssessment],
           run_root: Path) -> ClaimVerdict:
    """Apply the cold-iron rules in strict priority order.

    Priority is deliberate: refutation and prior-art beat approval, and a
    formal artifact must be confirmed, not merely asserted. Consensus never
    promotes a claim on its own.
    """
    dissent = sorted({f"{a.worker}/{a.role}: {a.status_vote}" for a in assessments})
    sycophancy = sum(_count_sycophancy(a.raw_text) for a in assessments)

    # Rule 1 — a specific, evidenced refutation dominates everything.
    for a in assessments:
        refutes = a.status_vote == STATUS_REFUTED or a.breaks_at
        has_evidence = any(e.type in ("counterexample", "citation") for e in a.evidence)
        if refutes and (has_evidence or a.breaks_at):
            ref = a.breaks_at or next((e.detail or e.ref for e in a.evidence
                                       if e.type == "counterexample"), "")
            return ClaimVerdict(claim_id, statement, STATUS_REFUTED,
                                decided_by="rule1_refutation", novel=False,
                                refutation=f"{a.worker}/{a.role}: {ref}",
                                dissent=dissent, sycophancy_hits=sycophancy)

    # Rule 2 — prior art means this is not new progress, whatever else was said.
    for a in assessments:
        if a.role == "prior-art-auditor" and a.status_vote == STATUS_KNOWN:
            cite = next((e.ref for e in a.evidence if e.type == "citation"), "")
            if cite:
                return ClaimVerdict(claim_id, statement, STATUS_KNOWN,
                                    decided_by="rule2_prior_art", novel=False,
                                    prior_art=cite, dissent=dissent,
                                    sycophancy_hits=sycophancy)

    # Rule 3 — 'proven' requires a Lean artifact confirmed by an actual build here.
    for a in assessments:
        for e in a.evidence:
            if e.type == "lean" and e.ref and _lean_check(e.ref, run_root):
                return ClaimVerdict(claim_id, statement, STATUS_PROVEN,
                                    decided_by="rule3_lean_verified", novel=True,
                                    lean_artifact=e.ref, dissent=dissent,
                                    sycophancy_hits=sycophancy)

    # Rule 4 — a claimed formal proof we could not kernel-check is NOT proven.
    claims_formal = any(e.type == "lean" for a in assessments for e in a.evidence)
    if claims_formal:
        return ClaimVerdict(claim_id, statement, STATUS_NOT_ESTABLISHED,
                            decided_by="rule4_formal_unverified", novel=False,
                            dissent=dissent + ["lean artifact did not pass a kernel check here"],
                            sycophancy_hits=sycophancy)

    # Rule 5 — genuine, evidence-backed disagreement is a result. Bare opinions
    # differing is just noise and falls through to the skeptical default.
    substantive = {a.status_vote for a in assessments
                   if a.status_vote not in (STATUS_NOT_ESTABLISHED,)
                   and (a.evidence or a.breaks_at)}
    if len(substantive) > 1:
        return ClaimVerdict(claim_id, statement, STATUS_CONTESTED,
                            decided_by="rule5_unresolved_dissent", novel=False,
                            dissent=dissent, sycophancy_hits=sycophancy)

    # Rule 6 — an informal status must be earned with reasoning, never a bare
    # vote. No argument or citation behind it means it establishes nothing.
    status = STATUS_NOT_ESTABLISHED
    for a in assessments:
        if a.status_vote in (STATUS_CONJECTURE, STATUS_SKETCH) and \
                any(e.type in ("argument", "citation") for e in a.evidence):
            status = a.status_vote
            break
    return ClaimVerdict(claim_id, statement, status,
                        decided_by="rule6_default_skeptical", novel=False,
                        dissent=dissent, sycophancy_hits=sycophancy)


def load_run(run_root: Path) -> dict[str, list[WorkerAssessment]]:
    by_claim: dict[str, list[WorkerAssessment]] = {}
    ev_fields = {"type", "ref", "detail", "verified"}
    for jf in sorted((run_root / "workers").glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        for item in (data if isinstance(data, list) else [data]):
            # Model-produced JSON may carry extra keys; keep only what we model.
            ev = [Evidence(**{k: v for k, v in e.items() if k in ev_fields})
                  for e in item.get("evidence", []) if isinstance(e, dict) and e.get("type")]
            a = WorkerAssessment(
                claim_id=item["claim_id"], role=item.get("role", "unknown"),
                worker=item.get("worker", jf.stem),
                status_vote=item.get("status_vote", STATUS_NOT_ESTABLISHED),
                evidence=ev, breaks_at=item.get("breaks_at", ""),
                confidence=float(item.get("confidence", 0.0)),
                raw_text=item.get("raw_text", ""),
            )
            by_claim.setdefault(a.claim_id, []).append(a)
    return by_claim


def statements_for(run_root: Path) -> dict[str, str]:
    f = run_root / "claims.json"
    if f.exists():
        return {c["claim_id"]: c.get("statement", "") for c in json.loads(f.read_text())}
    return {}


def render_md(verdicts: list[ClaimVerdict]) -> str:
    proven = [v for v in verdicts if v.status == STATUS_PROVEN]
    known = [v for v in verdicts if v.status == STATUS_KNOWN]
    refuted = [v for v in verdicts if v.status == STATUS_REFUTED]
    total_syco = sum(v.sycophancy_hits for v in verdicts)
    lines = ["# Cold-iron verdict", ""]
    lines.append(f"- New theorems established (Lean-verified): **{len(proven)}**")
    lines.append(f"- Claims that were already known results: **{len(known)}**")
    lines.append(f"- Claims refuted at a specific step: **{len(refuted)}**")
    lines.append(f"- Claims total: **{len(verdicts)}**")
    lines.append(f"- Sycophancy markers detected and ignored: **{total_syco}**")
    lines.append("")
    lines.append("## Per claim")
    for v in verdicts:
        lines.append(f"\n### {v.claim_id} — `{v.status}`")
        if v.statement:
            lines.append(f"> {v.statement}")
        lines.append(f"- decided by: `{v.decided_by}`")
        lines.append(f"- novel progress: {'yes' if v.novel else 'no'}")
        if v.lean_artifact:
            lines.append(f"- Lean artifact (kernel-checked): `{v.lean_artifact}`")
        if v.prior_art:
            lines.append(f"- already known: {v.prior_art}")
        if v.refutation:
            lines.append(f"- refuted: {v.refutation}")
        if v.sycophancy_hits:
            lines.append(f"- ⚠ {v.sycophancy_hits} praise markers in worker output, given zero weight")
        if v.dissent:
            lines.append(f"- votes/dissent: {', '.join(v.dissent)}")
    lines.append("\n## Bottom line\n")
    if proven:
        lines.append(f"{len(proven)} claim(s) hold up under a formal check. Everything else is not proven.")
    else:
        lines.append("No claim in this run is formally proven. Treat all of it as work in progress, "
                     "not as a result. Do not write it up as solved.")
    return "\n".join(lines) + "\n"


def run(run_root: Path) -> list[ClaimVerdict]:
    statements = statements_for(run_root)
    by_claim = load_run(run_root)
    verdicts = [decide(cid, statements.get(cid, ""), asmts, run_root)
                for cid, asmts in by_claim.items()]
    (run_root / "verdict.json").write_text(
        json.dumps([asdict(v) for v in verdicts], indent=2), encoding="utf-8")
    (run_root / "verdict.md").write_text(render_md(verdicts), encoding="utf-8")
    return verdicts


def selftest() -> int:
    """Prove the gate cannot be flattered. Runs with no external dependencies."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "workers").mkdir()
        # Five enthusiastic workers all cheer for an unproven claim.
        (root / "workers" / "cheerleaders.json").write_text(json.dumps([
            {"claim_id": "C1", "role": "strategist", "worker": w,
             "status_vote": "conjecture", "confidence": 0.99,
             "raw_text": "This is a genius breakthrough, you're close to a Nobel, canela en rama!"}
            for w in ["gpt", "claude", "gemini", "grok", "hermes"]
        ]))
        (root / "claims.json").write_text(json.dumps(
            [{"claim_id": "C1", "statement": "RH follows from lemma X."}]))
        v = run(root)[0]
        assert v.status == STATUS_NOT_ESTABLISHED, v.status
        assert v.sycophancy_hits >= 5, v.sycophancy_hits
        print(f"[selftest] 5 workers + confidence 0.99 + praise -> {v.status} "
              f"({v.sycophancy_hits} praise markers ignored)  OK")

        # One skeptic with a concrete counterexample refutes the crowd.
        (root / "workers" / "skeptic.json").write_text(json.dumps({
            "claim_id": "C1", "role": "skeptic", "worker": "claude",
            "status_vote": "refuted", "breaks_at": "step 4: divergence assumed without proof",
            "evidence": [{"type": "counterexample", "detail": "s = 1/2 + 14.1i"}],
            "raw_text": "Step 4 does not follow."}))
        v = run(root)[0]
        assert v.status == STATUS_REFUTED, v.status
        print(f"[selftest] one evidenced refutation beats five approvals -> {v.status}  OK")
    print("[selftest] cold iron holds.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Cold-iron verdict engine")
    ap.add_argument("--run", type=Path, help="Run directory to evaluate")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.run:
        ap.error("pass --run <dir> or --selftest")
    verdicts = run(args.run)
    print(render_md(verdicts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
