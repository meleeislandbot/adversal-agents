"""Hermes plugin: native Adversal tools, the cold-iron write guard, map status.

What this adds for the coordinator:

- A typed ``adversal`` toolset wrapping the project scripts (missions, map,
  decomposition, back-translation, re-verification, ideation). The model calls
  tools with structured arguments instead of hand-assembling long
  ``python3 scripts/... --flag "..."`` shell lines.
- A ``pre_tool_call`` guard that blocks hand-edits to gate-owned files
  (ledgers, verdicts, the wiki, the generated map view). Only the sanctioned
  scripts write there. This turns "the coordinator must not mint verdicts"
  from doctrine into mechanism at the agent layer.
- A ``pre_llm_call`` injection with one compact map-status line per turn, so
  the coordinator always knows the state without spending tool calls.

Nothing here decides truth. Every tool defers to the deterministic scripts and
the Lean gate; the guard is best-effort string matching (belt and suspenders,
not cryptography) and fails open so it can never take the agent down.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

TOOLSET = "adversal"

# Files only the gate and its scripts may write. Matched as substrings against
# tool parameters and terminal command lines.
PROTECTED_PATTERNS = (
    ".adversal/ledgers/",
    "verdict.json",
    "verdict.md",
    "llm-wiki/",
    ".adversal/map/",
)
# Commands allowed to touch protected paths: the sanctioned writers.
SANCTIONED_SCRIPTS = (
    "run_mission.py", "verdict_engine.py", "map_tool.py", "decompose.py",
    "backtranslate.py", "reverify.py", "ideate.py", "bootstrap_adversal.py",
    "adversal_doctor.py", "bibliography.py",
)
WRITE_HINTS = (">", ">>", "tee ", "rm ", "mv ", "cp ", "sed -i", "truncate",
               "unlink", "shutil", "write_text", "mkdir")


def find_project(start: Path | None = None) -> Path | None:
    """Resolve the instantiated Adversal project.

    Order: explicit start -> ADVERSAL_PROJECT env var (the durable anchor set
    during setup; the agent process may start far from the project) -> walk
    upward from the working directory.
    """
    if start is None:
        anchored = os.environ.get("ADVERSAL_PROJECT", "").strip()
        if anchored:
            candidate = Path(anchored).expanduser()
            if (candidate / ".adversal" / "project.yaml").exists():
                return candidate.resolve()
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".adversal" / "project.yaml").exists():
            return candidate
    return None


def _run(script: str, args: list[str], project: Path, timeout: int) -> str:
    """Run one sanctioned script; return a JSON envelope the model can read."""
    script_path = project / "scripts" / script
    if not script_path.exists():
        return json.dumps({"success": False,
                           "error": f"{script} not found in {project}/scripts — "
                                    f"sync the project scripts first"})
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path), *args],
            cwd=str(project), text=True, capture_output=True,
            timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"success": False,
                           "error": f"{script} timed out after {timeout}s"})
    return json.dumps({
        "success": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-4000:],
    }, ensure_ascii=False)


def _project_or_error(params: dict) -> tuple[Path | None, str | None]:
    explicit = params.get("project")
    project = find_project(Path(explicit)) if explicit else find_project()
    if project is None:
        return None, json.dumps({
            "success": False,
            "error": "no Adversal project found (missing .adversal/project.yaml "
                     "from the working directory upward); pass `project`"})
    return project, None


def _opt(args: list[str], flag: str, value) -> None:
    if value not in (None, "", False):
        args.extend([flag, str(value)])


# --- Map status (used by the tool, the /map command, and the injection) -----

def map_status_line(project: Path) -> str | None:
    """One compact line from map.json + the decisions ledger. None if no map."""
    map_file = project / ".adversal" / "map" / "map.json"
    if not map_file.exists():
        return None
    try:
        data = json.loads(map_file.read_text(encoding="utf-8"))
        decisions: dict[str, str] = {}
        ledger = project / ".adversal" / "ledgers" / "decisions.jsonl"
        if ledger.exists():
            for line in ledger.read_text(encoding="utf-8").splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("claim_id"):
                    decisions[entry["claim_id"]] = entry.get("status", "")
        regressed: set[str] = set()
        report = project / ".adversal" / "map" / "reverify-latest.json"
        if report.exists():
            try:
                regressed = set(json.loads(
                    report.read_text(encoding="utf-8")).get("regressions", []))
            except json.JSONDecodeError:
                pass
        counts: dict[str, int] = {}
        established = {"proven", "known"}
        ready: list[str] = []
        nodes = data.get("nodes", [])
        ids = {n["id"] for n in nodes}
        for n in nodes:
            status = ("regressed" if n["id"] in regressed
                      else decisions.get(n["id"], "untried"))
            counts[status] = counts.get(status, 0) + 1
            ingredients = [m for m in nodes if n["id"] in m.get("supports", [])]
            if status not in established and status != "refuted" and all(
                    decisions.get(m["id"], "") in established for m in ingredients):
                ready.append(n["id"])
        summary = ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()))
        goal = data.get("goal", {}).get("id", "GOAL")
        line = (f"[adversal] map toward {goal}: {len(nodes)} nodes ({summary or 'empty'});"
                f" ready: {', '.join(sorted(ready)[:5]) or 'none'}")
        if regressed & ids:
            line += f"; ⚠ regressions: {', '.join(sorted(regressed & ids))}"
        return line
    except Exception:
        return None


# --- Cold-iron guard ---------------------------------------------------------

def _strings_in(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings_in(v)]
    if isinstance(value, (list, tuple)):
        return [s for v in value for s in _strings_in(v)]
    return []


def guard_decision(tool_name: str, params: dict) -> dict | None:
    """Return a block directive when a tool call would hand-edit gate-owned files."""
    try:
        text = " ".join(_strings_in(params))
        if not any(p in text for p in PROTECTED_PATTERNS):
            return None
        if any(s in text for s in SANCTIONED_SCRIPTS):
            return None  # the sanctioned writers are the whole point
        lowered = (tool_name or "").lower()
        writes = ("write" in lowered or "patch" in lowered or "edit" in lowered
                  or "delete" in lowered or "move" in lowered
                  or (lowered.startswith("terminal")
                      and any(h in text for h in WRITE_HINTS)))
        if not writes:
            return None
        return {"action": "block",
                "message": ("cold-iron guard: ledgers, verdicts, llm-wiki and the "
                            "generated map view are written only by the gate and "
                            "its scripts (run_mission.py, map_tool.py, ...). "
                            "Hand-editing them would let a model mint truth. If "
                            "this is genuinely needed, ask the user to do it "
                            "manually outside the agent.")}
    except Exception:
        return None  # the guard must never take a turn down


# --- Plugin wiring -----------------------------------------------------------

def register(ctx) -> None:  # pragma: no cover - thin wiring, pieces unit-tested
    def tool(name: str, description: str, properties: dict, required: list[str],
             handler) -> None:
        ctx.register_tool(
            name=name, toolset=TOOLSET, handler=handler, description=description,
            schema={"name": name, "description": description,
                    "parameters": {"type": "object", "properties": properties,
                                   "required": required}})

    S = {"type": "string"}
    N = {"type": "integer"}
    B = {"type": "boolean"}

    # -- missions --
    def h_mission(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["--statement", params["statement"],
                "--claim-id", params.get("claim_id", "C1")]
        _opt(args, "--formal-statement", params.get("formal_statement"))
        _opt(args, "--theorem-name", params.get("theorem_name"))
        _opt(args, "--providers", params.get("providers"))
        _opt(args, "--roles", params.get("roles"))
        _opt(args, "--timeout", params.get("worker_timeout"))
        if params.get("dry_run"):
            args.append("--dry-run")
        result = _run("run_mission.py", args, project, timeout=3600)
        _run("map_tool.py", ["render", "--project", str(project)], project, 60)
        return result

    tool("adversal_mission",
         "Run one verification mission (roles -> gate -> ledger) on a bounded "
         "claim. Use the map node id as claim_id so the map colors itself. "
         "`proven` needs formal_statement + theorem_name.",
         {"statement": S, "claim_id": S, "formal_statement": S,
          "theorem_name": S, "providers": {**S, "description": "e.g. claude,codex"},
          "roles": S, "worker_timeout": N, "dry_run": B, "project": S},
         ["statement", "claim_id"], h_mission)

    # -- map --
    def h_map_init(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["init", "--project", str(project), "--goal", params["goal"]]
        _opt(args, "--goal-id", params.get("goal_id"))
        return _run("map_tool.py", args, project, 60)

    tool("adversal_map_init", "Create the map with its goal node (once per goal).",
         {"goal": S, "goal_id": S, "project": S}, ["goal"], h_map_init)

    def h_map_add(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["add", "--project", str(project), "--id", params["id"],
                "--statement", params["statement"]]
        _opt(args, "--supports", params.get("supports"))
        _opt(args, "--formal-statement", params.get("formal_statement"))
        _opt(args, "--theorem-name", params.get("theorem_name"))
        _opt(args, "--notes", params.get("notes"))
        return _run("map_tool.py", args, project, 60)

    tool("adversal_map_add",
         "Add one ingredient lemma to the map (user-approved plans only).",
         {"id": S, "statement": S, "supports": S, "formal_statement": S,
          "theorem_name": S, "notes": S, "project": S},
         ["id", "statement"], h_map_add)

    def h_map_set(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["set", "--project", str(project), "--id", params["id"],
                "--formal-statement", params["formal_statement"],
                "--theorem-name", params["theorem_name"]]
        _opt(args, "--notes", params.get("notes"))
        return _run("map_tool.py", args, project, 60)

    tool("adversal_map_set",
         "Set the canonical Lean target (formal_statement + theorem_name) of an "
         "existing map node. Run adversal_backtranslate on it afterwards and "
         "have the USER confirm fidelity before any mission relies on it.",
         {"id": S, "formal_statement": S, "theorem_name": S, "notes": S,
          "project": S}, ["id", "formal_statement", "theorem_name"], h_map_set)

    def h_map_import(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["import", "--project", str(project),
                "--proposal", params["proposal"]]
        _opt(args, "--only", params.get("only"))
        return _run("map_tool.py", args, project, 60)

    tool("adversal_map_import",
         "Import user-accepted nodes from a decompose proposal file.",
         {"proposal": S, "only": {**S, "description": "comma-separated ids"},
          "project": S}, ["proposal"], h_map_import)

    def h_map_next(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["next", "--project", str(project)]
        _opt(args, "--n", params.get("n"))
        return _run("map_tool.py", args, project, 60)

    tool("adversal_map_next",
         "Ready map targets (all ingredients established), as runnable commands.",
         {"n": N, "project": S}, [], h_map_next)

    def h_map_status(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        return _run("map_tool.py", ["status", "--project", str(project), "--json"],
                    project, 60)

    tool("adversal_map_status", "Machine-readable map state (statuses, ready list).",
         {"project": S}, [], h_map_status)

    # -- generation --
    def h_decompose(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["--project", str(project)]
        _opt(args, "--target", params.get("target"))
        _opt(args, "--n", params.get("n"))
        _opt(args, "--timeout", params.get("worker_timeout"))
        return _run("decompose.py", args, project, timeout=1200)

    tool("adversal_decompose",
         "Ask the strategist for a decomposition PROPOSAL of one map node. "
         "Import only what the user accepts.",
         {"target": S, "n": N, "worker_timeout": N, "project": S}, [], h_decompose)

    def h_ideate(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["--topic", params["topic"], "--project", str(project)]
        _opt(args, "--n", params.get("n"))
        _opt(args, "--timeout", params.get("worker_timeout"))
        if params.get("audit"):
            args.append("--audit")
        return _run("ideate.py", args, project, timeout=3600)

    tool("adversal_ideate",
         "Divergent ideation: several bold UNVERIFIED directions on a topic.",
         {"topic": S, "n": N, "audit": B, "worker_timeout": N, "project": S},
         ["topic"], h_ideate)

    # -- fidelity + CI --
    def h_backtranslate(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["--project", str(project)]
        _opt(args, "--claim-id", params.get("claim_id"))
        _opt(args, "--run", params.get("run"))
        _opt(args, "--formal-statement", params.get("formal_statement"))
        _opt(args, "--statement", params.get("statement"))
        _opt(args, "--lang", params.get("lang"))
        return _run("backtranslate.py", args, project, timeout=600)

    tool("adversal_backtranslate",
         "Statement-fidelity check: an isolated worker translates ONLY the Lean "
         "statement back to plain language; relay the side-by-side report for "
         "the USER to compare. Run before presenting any `proven` as settled.",
         {"claim_id": S, "run": S, "formal_statement": S, "statement": S,
          "lang": S, "project": S}, [], h_backtranslate)

    def h_reverify(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        result = _run("reverify.py", ["--project", str(project)], project,
                      timeout=3600)
        _run("map_tool.py", ["render", "--project", str(project)], project, 60)
        return result

    tool("adversal_reverify",
         "Mathematical CI: re-check every artifact ever marked proven against "
         "the kernel; regressions are flagged on the map. Run before promoting "
         "to the wiki.",
         {"project": S}, [], h_reverify)

    # -- bibliography (the second, checkable memory) --
    def h_bib_add(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        args = ["add", "--project", str(project),
                "--title", params["title"],
                "--year", str(params["year"]),
                "--link", params["link"],
                "--status", params["status"],
                "--route", params["route"]]
        _opt(args, "--authors", params.get("authors"))
        _opt(args, "--why-dead", params.get("why_dead"))
        _opt(args, "--notes", params.get("notes"))
        _opt(args, "--source", params.get("source"))
        return _run("bibliography.py", args, project, 60)

    tool("adversal_bib_add",
         "Add one curated prior-art entry (link REQUIRED — verify it loads "
         "first with your web tools). documented-dead-end entries need "
         "why_dead. Feeds the digest that grounds ideation as forced contrast.",
         {"title": S, "year": N, "link": S,
          "status": {**S, "description": "active-program | documented-dead-end "
                                         "| partial-result | survey"},
          "route": S, "authors": S, "why_dead": S, "notes": S, "source": S,
          "project": S},
         ["title", "year", "link", "status", "route"], h_bib_add)

    def h_bib_digest(params, **_):
        project, err = _project_or_error(params)
        if err:
            return err
        return _run("bibliography.py", ["digest", "--project", str(project)],
                    project, 60)

    tool("adversal_bib_digest",
         "Regenerate the prior-art digest and index from the bibliography. "
         "ideate/decompose auto-detect the digest and ground on it.",
         {"project": S}, [], h_bib_digest)

    # -- hooks --
    def guard(*args, **kwargs):
        tool_name = kwargs.get("tool_name") or (args[0] if args else "")
        params = kwargs.get("params") or (args[1] if len(args) > 1 else {}) or {}
        return guard_decision(str(tool_name), params if isinstance(params, dict) else {})

    ctx.register_hook("pre_tool_call", guard)

    def inject(*_args, **_kwargs):
        try:
            project = find_project()
            if project is None:
                return None
            return map_status_line(project)
        except Exception:
            return None

    ctx.register_hook("pre_llm_call", inject)

    # -- human shortcut --
    def cmd_map(*_args, **_kwargs):
        project = find_project()
        if project is None:
            return "no Adversal project here"
        line = map_status_line(project) or "no map yet — adversal_map_init"
        canvas = project / "map" / "Map.canvas"
        if canvas.exists():
            line += f"\ncanvas: {canvas}"
        return line

    try:
        ctx.register_command("map", cmd_map,
                             "Adversal map status (counts, ready targets, canvas path)")
    except Exception:
        pass  # older Hermes without register_command: tools still work
