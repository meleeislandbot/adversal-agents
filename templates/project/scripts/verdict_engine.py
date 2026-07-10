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
import tempfile
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
class ClaimSpec:
    claim_id: str
    statement: str
    # The Lean type is the canonical mathematical claim. Natural-language text
    # is explanatory only: the kernel cannot certify that an English sentence
    # was translated faithfully.
    formal_statement: str = ""
    theorem_name: str = ""


@dataclass
class ClaimVerdict:
    claim_id: str
    statement: str
    status: str
    decided_by: str            # which cold-iron rule fixed the status
    novel: bool | None         # False only after verified prior art; otherwise unknown
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


SAFE_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}
LEAN_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_'.]*$")
FORMAL_STATEMENT_FORBIDDEN = re.compile(
    r"(?:\r|\n|;|--|/-|#|:=|\b(?:axiom|constant|theorem|lemma|example|def|namespace|end)\b)"
)
UNTRUSTED_COMMAND = re.compile(
    r"(?m)^\s*(?:axiom|constant|syntax|macro|macro_rules|elab|set_option|scoped|attribute)\b"
)
IMPORT_LINE = re.compile(r"^\s*import\s+([A-Za-z0-9_'.]+)\s*$")
TRUSTED_IMPORT = re.compile(r"^(?:Mathlib|Mathlib\..+|Std|Std\..+|Init|Init\..+)$")


def _contained_lean_path(ref: str, run_root: Path) -> Path | None:
    """Resolve a submitted artifact without letting evidence escape the run."""
    if not ref or Path(ref).is_absolute():
        return None
    try:
        lean_root = (run_root / "lean").resolve(strict=True)
        path = (run_root / ref).resolve(strict=True)
        path.relative_to(lean_root)
    except (FileNotFoundError, OSError, ValueError):
        return None
    return path if path.is_file() and path.suffix == ".lean" else None


def _axioms_from_output(output: str, theorem_name: str) -> set[str] | None:
    """Read Lean's ``#print axioms`` result; None means it was not observed."""
    pattern = re.compile(
        rf"['\"]?{re.escape(theorem_name)}['\"]?\s+depends on axioms:\s*\[([^]]*)\]",
        re.IGNORECASE,
    )
    match = pattern.search(output)
    if not match:
        # Lean prints this for constructive theorems with no axioms.
        no_axioms = re.compile(
            rf"['\"]?{re.escape(theorem_name)}['\"]?\s+does not depend on any axioms",
            re.IGNORECASE,
        )
        return set() if no_axioms.search(output) else None
    return {name.strip() for name in match.group(1).split(",") if name.strip()}


def _safe_formal_statement(statement: str) -> bool:
    """Accept a single Lean type expression, never extra checker commands."""
    text = statement.strip()
    return bool(text) and len(text) <= 20_000 and not FORMAL_STATEMENT_FORBIDDEN.search(text)


def _split_trusted_imports(src: str) -> tuple[list[str], str] | None:
    """Move allow-listed imports ahead of the canonical type declaration."""
    imports: list[str] = []
    body: list[str] = []
    for line in src.splitlines():
        match = IMPORT_LINE.fullmatch(line)
        if match:
            module = match.group(1)
            if not TRUSTED_IMPORT.fullmatch(module):
                return None
            imports.append(f"import {module}")
        else:
            body.append(line)
    return imports, "\n".join(body) + "\n"


def _lean_check(ref: str, run_root: Path, theorem_name: str,
                formal_statement: str) -> bool:
    """Return True only if a Lean artifact is confirmed by an actual build.

    If Lean is not installed here we CANNOT confirm it, so we return False.
    Unchecked is not proven. That is the whole point.

    A proof that leans on ``sorry``/``admit`` is not a proof: Lean only warns on
    it and exits 0, so we reject it explicitly. Erring toward "not proven" is the
    correct bias for a truth gate.
    """
    path = _contained_lean_path(ref, run_root)
    if path is None or not LEAN_NAME.fullmatch(theorem_name) \
            or not _safe_formal_statement(formal_statement):
        return False
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    if re.search(r"\bsorry\b", src) or re.search(r"\badmit\b", src):
        return False
    # A model-authored axiom can make any proposition compile. Reject new
    # top-level assumptions before asking Lean for the theorem's dependencies.
    if UNTRUSTED_COMMAND.search(src):
        return False
    split_source = _split_trusted_imports(src)
    if split_source is None:
        return False
    imports, body = split_source
    checker = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".lean", prefix="gate-check-",
            dir=path.parent, delete=False,
        ) as fh:
            checker = Path(fh.name)
            if imports:
                fh.write("\n".join(dict.fromkeys(imports)) + "\n\n")
            # Elaborate the canonical proposition before any model-authored
            # declarations or notation. The later theorem must inhabit this
            # already-fixed type by definitional equality.
            fh.write("namespace AdversalCanonical\n")
            fh.write(f"def Claim : Prop := ({formal_statement})\n")
            fh.write("end AdversalCanonical\n\n")
            fh.write(body)
            fh.write("\n-- Added by the deterministic gate.\n")
            fh.write(f"#check {theorem_name}\n")
            fh.write(f"example : AdversalCanonical.Claim := {theorem_name}\n")
            fh.write(f"#print axioms {theorem_name}\n")

        project = _find_lakefile(path.parent)
        if project:  # Check this exact file inside the Lake environment.
            lake = _resolve_tool("lake")
            if not lake:
                return False
            proc = subprocess.run([lake, "env", "lean", str(checker)], cwd=str(project), text=True,
                                  capture_output=True, timeout=1800, check=False,
                                  env={**os.environ, "PATH": _lean_bin_path()})
        else:  # standalone file: type-check it directly
            lean = _resolve_tool("lean")
            if not lean:
                return False
            proc = subprocess.run([lean, str(checker)], text=True, capture_output=True,
                                  timeout=600, check=False)
        raw_out = proc.stdout + proc.stderr
        out = raw_out.lower()
        if proc.returncode != 0 or "sorry" in out or "error" in out:
            return False
        axioms = _axioms_from_output(raw_out, theorem_name)
        return axioms is not None and axioms <= SAFE_AXIOMS
    except Exception:
        return False
    finally:
        if checker is not None:
            checker.unlink(missing_ok=True)


def _lean_bin_path() -> str:
    """PATH augmented with the elan bin dir so `lake` can find `lean`."""
    elan_bin = Path.home() / ".elan" / "bin"
    base = os.environ.get("PATH", "")
    return f"{elan_bin}:{base}" if elan_bin.exists() else base


def decide(claim_id: str, statement: str, assessments: list[WorkerAssessment],
           run_root: Path, formal_statement: str = "", theorem_name: str = "") -> ClaimVerdict:
    """Apply the cold-iron rules in strict priority order.

    Priority is deliberate: refutation and prior-art beat approval, and a
    formal artifact must be confirmed, not merely asserted. Consensus never
    promotes a claim on its own.
    """
    dissent = sorted({f"{a.worker}/{a.role}: {a.status_vote}" for a in assessments})
    sycophancy = sum(_count_sycophancy(a.raw_text) for a in assessments)

    # Rule 1 — `refuted` must be EARNED exactly like `proven`: a Lean disproof of
    # the canonical formal statement, kernel-checked here with the same strictness
    # (exact type, no sorry, no introduced axioms). The disproof declaration must
    # be named `<theorem_name>_disproof` and inhabit `¬ (formal_statement)`.
    # Worker prose and worker-authored counterexample text never refute anything.
    disproof_name = f"{theorem_name}_disproof" if theorem_name else ""
    disproof_type = f"¬ ({formal_statement})" if formal_statement else ""
    verified_disproof = ""
    for a in assessments:
        if a.role != "skeptic" or a.status_vote != STATUS_REFUTED or not disproof_name:
            continue
        for e in a.evidence:
            if e.type == "lean" and e.ref and _lean_check(
                    e.ref, run_root, disproof_name, disproof_type):
                verified_disproof = f"{a.worker}/{a.role}: {e.ref}"
                break
        if verified_disproof:
            break

    # Rule 3 — 'proven' requires a Lean artifact confirmed by an actual build here.
    verified_proof = ""
    for a in assessments:
        if a.role != "formalizer" or a.status_vote != STATUS_PROVEN:
            continue
        for e in a.evidence:
            if e.type == "lean" and e.ref and _lean_check(
                    e.ref, run_root, theorem_name, formal_statement):
                verified_proof = e.ref
                break
        if verified_proof:
            break

    # Rule 2 still needs an independent validator: a citation string and the
    # worker-controlled `verified` field are proposals, not facts. The same goes
    # for a refutation vote that did NOT come with a kernel-checked disproof.
    unverified_refutations = [a for a in assessments if a.status_vote == STATUS_REFUTED]
    unverified_citations = [a for a in assessments
                            if a.role == "prior-art-auditor" and a.status_vote == STATUS_KNOWN]
    if unverified_refutations and not verified_disproof:
        dissent.append("refutation candidate present but not independently verified")
    if unverified_citations:
        dissent.append("citation candidate present but not independently verified")

    if verified_proof and verified_disproof:
        # The kernel accepted both P and ¬P. With the safe-axiom allowlist this
        # should be impossible; if it happens, the gate itself is suspect and no
        # status may be granted. Say so loudly instead of picking a side.
        return ClaimVerdict(claim_id, statement, STATUS_CONTESTED,
                            decided_by="rule0_gate_inconsistency", novel=None,
                            lean_artifact=verified_proof, refutation=verified_disproof,
                            dissent=dissent + ["kernel accepted both a proof and a "
                                               "disproof — audit the gate before "
                                               "trusting either"],
                            sycophancy_hits=sycophancy)
    if verified_disproof:
        return ClaimVerdict(claim_id, statement, STATUS_REFUTED,
                            decided_by="rule1_disproof_verified", novel=None,
                            refutation=verified_disproof, dissent=dissent,
                            sycophancy_hits=sycophancy)
    if verified_proof:
        return ClaimVerdict(claim_id, statement, STATUS_PROVEN,
                            decided_by="rule3_lean_verified", novel=None,
                            lean_artifact=verified_proof, dissent=dissent,
                            sycophancy_hits=sycophancy)

    # Rule 4 — a claimed formal proof we could not kernel-check is NOT proven.
    claims_formal = any(e.type == "lean" for a in assessments for e in a.evidence)
    if claims_formal:
        return ClaimVerdict(claim_id, statement, STATUS_NOT_ESTABLISHED,
                            decided_by="rule4_formal_unverified", novel=None,
                            dissent=dissent + ["lean artifact did not pass a kernel check here"],
                            sycophancy_hits=sycophancy)

    # Rule 5 — genuine, evidence-backed disagreement is a result. Bare opinions
    # differing is just noise and falls through to the skeptical default.
    # Only informal, evidence-backed positions can create an unresolved
    # disagreement here. Unverified `known`/`refuted`/`proven` proposals must
    # not gain weight merely by disagreeing with one another.
    substantive = {a.status_vote for a in assessments
                   if a.status_vote in (STATUS_CONJECTURE, STATUS_SKETCH)
                   and (a.evidence or a.breaks_at)}
    if len(substantive) > 1:
        return ClaimVerdict(claim_id, statement, STATUS_CONTESTED,
                            decided_by="rule5_unresolved_dissent", novel=None,
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
                        decided_by="rule6_default_skeptical", novel=None,
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


def claims_for(run_root: Path) -> dict[str, ClaimSpec]:
    f = run_root / "claims.json"
    if f.exists():
        return {
            c["claim_id"]: ClaimSpec(
                claim_id=c["claim_id"],
                statement=c.get("statement", ""),
                formal_statement=c.get("formal_statement", ""),
                theorem_name=c.get("theorem_name", ""),
            )
            for c in json.loads(f.read_text())
        }
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
        novelty = "yes" if v.novel is True else "no" if v.novel is False else "unknown"
        lines.append(f"- novel progress: {novelty}")
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
    claims = claims_for(run_root)
    by_claim = load_run(run_root)
    claim_ids = list(claims)
    claim_ids.extend(cid for cid in by_claim if cid not in claims)
    verdicts = []
    for cid in claim_ids:
        spec = claims.get(cid, ClaimSpec(cid, ""))
        verdicts.append(decide(
            cid, spec.statement, by_claim.get(cid, []), run_root,
            formal_statement=spec.formal_statement,
            theorem_name=spec.theorem_name,
        ))
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

        # A worker-authored counterexample is a candidate, not a verified fact.
        (root / "workers" / "skeptic.json").write_text(json.dumps({
            "claim_id": "C1", "role": "skeptic", "worker": "claude",
            "status_vote": "refuted", "breaks_at": "step 4: divergence assumed without proof",
            "evidence": [{"type": "counterexample", "detail": "s = 1/2 + 14.1i"}],
            "raw_text": "Step 4 does not follow."}))
        v = run(root)[0]
        assert v.status == STATUS_NOT_ESTABLISHED, v.status
        assert any("not independently verified" in note for note in v.dissent)
        print(f"[selftest] unverified refutation text -> {v.status}  OK")

        # A refuted vote pointing at a Lean disproof we cannot check stays unearned.
        (root / "workers" / "skeptic.json").write_text(json.dumps({
            "claim_id": "C1", "role": "skeptic", "worker": "claude",
            "status_vote": "refuted",
            "evidence": [{"type": "lean", "ref": "lean/missing-disproof.lean"}],
            "raw_text": "Disproof attached."}))
        v = run(root)[0]
        assert v.status == STATUS_NOT_ESTABLISHED, v.status
        assert v.status != STATUS_REFUTED
        print(f"[selftest] unverifiable lean disproof -> {v.status}  OK")
        (root / "workers" / "skeptic.json").unlink()

        # A plausible-looking citation cannot award `known` on its own either.
        (root / "workers" / "prior-art.json").write_text(json.dumps({
            "claim_id": "C1", "role": "prior-art-auditor", "worker": "gpt",
            "status_vote": "known",
            "evidence": [{"type": "citation", "ref": "Invented theorem (2099)",
                          "verified": True}],
        }))
        v = run(root)[0]
        assert v.status == STATUS_NOT_ESTABLISHED, v.status
        assert any("citation candidate" in note for note in v.dissent)
        print(f"[selftest] worker-asserted citation -> {v.status}  OK")

        # Regression: a 'proven' vote carrying a stray breaks_at (e.g. str(None))
        # and no counterexample must NOT be read as a refutation.
        for f in (root / "workers").glob("*.json"):
            f.unlink()
        (root / "workers" / "formalizer.json").write_text(json.dumps({
            "claim_id": "C1", "role": "formalizer", "worker": "gpt",
            "status_vote": "proven", "breaks_at": "None",
            "evidence": [{"type": "lean", "ref": "lean/missing.lean"}],
            "raw_text": "compiles"}))
        v = run(root)[0]
        assert v.status == STATUS_NOT_ESTABLISHED, v.status
        assert v.decided_by == "rule4_formal_unverified", v.decided_by
        print(f"[selftest] proven-vote + junk breaks_at + unverifiable lean -> {v.status}  OK")

        # Claims do not disappear just because every worker failed to answer.
        (root / "claims.json").write_text(json.dumps([
            {"claim_id": "C1", "statement": "RH follows from lemma X."},
            {"claim_id": "C2", "statement": "A claim with no worker output."},
        ]))
        verdicts = run(root)
        assert [v.claim_id for v in verdicts] == ["C1", "C2"]
        assert verdicts[1].status == STATUS_NOT_ESTABLISHED
        print("[selftest] missing worker output -> explicit not_established  OK")
    print("[selftest] cold iron holds.")
    return 0 if ok else 1


def selftest_lean() -> int:
    """Exercise the real Lean boundary: exact type, exact file, no new axiom."""
    if not _resolve_tool("lean"):
        print("[selftest-lean] Lean is not installed; cannot test the kernel boundary.",
              file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "workers").mkdir()
        (root / "lean").mkdir()
        artifact = root / "lean" / "C1.lean"
        artifact.write_text("theorem Harmless : True := True.intro\n", encoding="utf-8")
        (root / "claims.json").write_text(json.dumps([{
            "claim_id": "C1", "statement": "The formal proposition True holds.",
            "formal_statement": "True", "theorem_name": "Harmless",
        }]), encoding="utf-8")
        (root / "workers" / "formalizer.json").write_text(json.dumps({
            "claim_id": "C1", "role": "formalizer", "worker": "selftest",
            "status_vote": "proven", "evidence": [{"type": "lean", "ref": "lean/C1.lean"}],
        }), encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_PROVEN, verdict
        print("[selftest-lean] exact theorem type + kernel check -> proven  OK")

        worker_file = root / "workers" / "formalizer.json"
        worker = json.loads(worker_file.read_text(encoding="utf-8"))
        worker["evidence"][0]["ref"] = str(artifact)
        worker_file.write_text(json.dumps(worker), encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_NOT_ESTABLISHED, verdict
        print("[selftest-lean] absolute/out-of-contract artifact path -> not_established  OK")

        worker["evidence"][0]["ref"] = "lean/C1.lean"
        worker["role"] = "skeptic"
        worker_file.write_text(json.dumps(worker), encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_NOT_ESTABLISHED, verdict
        print("[selftest-lean] non-formalizer Lean artifact -> not_established  OK")

        worker["role"] = "formalizer"
        worker_file.write_text(json.dumps(worker), encoding="utf-8")

        (root / "claims.json").write_text(json.dumps([{
            "claim_id": "C1", "statement": "A mismatched formal proposition.",
            "formal_statement": "False", "theorem_name": "Harmless",
        }]), encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_NOT_ESTABLISHED, verdict
        print("[selftest-lean] unrelated compiling theorem -> not_established  OK")

        artifact.write_text(
            "axiom invented : False\ntheorem Harmless : False := invented\n", encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_NOT_ESTABLISHED, verdict
        print("[selftest-lean] model-introduced axiom -> not_established  OK")

        # `refuted` is earned by a kernel-checked disproof of the exact negation.
        for f in (root / "workers").glob("*.json"):
            f.unlink()
        (root / "claims.json").write_text(json.dumps([{
            "claim_id": "C1", "statement": "The formal proposition False holds.",
            "formal_statement": "False", "theorem_name": "Bogus",
        }]), encoding="utf-8")
        disproof = root / "lean" / "C1-disproof.lean"
        disproof.write_text("theorem Bogus_disproof : ¬ (False) := fun h => h\n",
                            encoding="utf-8")
        (root / "workers" / "skeptic.json").write_text(json.dumps({
            "claim_id": "C1", "role": "skeptic", "worker": "selftest",
            "status_vote": "refuted",
            "evidence": [{"type": "lean", "ref": "lean/C1-disproof.lean"}],
        }), encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_REFUTED, verdict
        assert verdict.decided_by == "rule1_disproof_verified", verdict
        print("[selftest-lean] kernel-checked disproof -> refuted  OK")

        # An axiom-smuggled disproof earns nothing, same as an axiom-smuggled proof.
        disproof.write_text(
            "axiom bad : ¬ (False)\ntheorem Bogus_disproof : ¬ (False) := bad\n",
            encoding="utf-8")
        verdict = run(root)[0]
        assert verdict.status == STATUS_NOT_ESTABLISHED, verdict
        print("[selftest-lean] axiom-smuggled disproof -> not_established  OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Cold-iron verdict engine")
    ap.add_argument("--run", type=Path, help="Run directory to evaluate")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-lean", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.selftest_lean:
        return selftest_lean()
    if not args.run:
        ap.error("pass --run <dir>, --selftest, or --selftest-lean")
    verdicts = run(args.run)
    print(render_md(verdicts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
