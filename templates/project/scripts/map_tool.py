#!/usr/bin/env python3
"""The map: a dependency blueprint from small lemmas up to one declared goal.

The gate answers "is this claim established?". The map answers the question the
gate cannot: "does this established piece move us toward OUR goal?" — and it
answers it mechanically, by position: a node matters exactly when the goal
depends on it, directly or through other nodes. Progress is the map turning
green from the leaves upward; a dead branch turning red is also progress,
because nobody wastes another month inside it.

Cold-iron division of labor:

- ``map.json`` holds STRUCTURE only — nodes, edges, statements. It is a plan,
  authored by fallible people and models, and it may be redrawn at any time.
- Node COLORS are never stored and never hand-edited. Every render derives them
  from the append-only decisions ledger, which only the gate feeds. Nobody can
  paint a node green, including the coordinator.

This mirrors how large formalization projects track progress (the Lean
community's "blueprint" practice); it is not an invention of this repo.

Usage:
    python3 map_tool.py init    --project . --goal "statement of the goal"
    python3 map_tool.py add     --project . --id L1 --statement "..." [--supports GOAL]
    python3 map_tool.py import  --project . --proposal <proposal.json> [--only L1,L2]
    python3 map_tool.py check   --project .
    python3 map_tool.py render  --project .
    python3 map_tool.py next    --project . [--n 3]
    python3 map_tool.py status  --project . [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MAP_REL = Path(".adversal") / "map" / "map.json"
RENDER_REL = Path(".adversal") / "map" / "map.md"
REVERIFY_REL = Path(".adversal") / "map" / "reverify-latest.json"
LEDGER_REL = Path(".adversal") / "ledgers" / "decisions.jsonl"
# Obsidian export state (which folder we own, which files we generated). Lives
# under .adversal so Obsidian never indexes it.
OBSIDIAN_STAMP_REL = Path(".adversal") / "map" / "obsidian-export.json"

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

# Render vocabulary. Colors come from the ledger; "untried" means no gate
# decision exists for the node's claim_id yet.
STATUS_ICON = {
    "proven": "🟩",
    "known": "📚",
    "refuted": "🟥",
    "contested": "🟧",
    "conjecture": "🟨",
    "sketch": "🟨",
    "not_established": "⬜",
    "untried": "⬜",
    "regressed": "⚠️",
}
ESTABLISHED = {"proven", "known"}


def load_map(project: Path) -> dict:
    path = project / MAP_REL
    if not path.exists():
        raise SystemExit(f"error: no map at {path} — run `map_tool.py init` first")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "goal" not in data or "nodes" not in data:
        raise SystemExit(f"error: {path} is not a map file")
    return data


def save_map(project: Path, data: dict) -> Path:
    path = project / MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def node_ids(data: dict) -> set[str]:
    return {data["goal"]["id"], *(n["id"] for n in data["nodes"])}


def ingredients_of(data: dict, target: str) -> list[dict]:
    """Nodes that feed into `target` (i.e. list it in their `supports`)."""
    return [n for n in data["nodes"] if target in n.get("supports", [])]


def validate(data: dict) -> list[str]:
    """Structural errors; an empty list means the map is well-formed."""
    errors: list[str] = []
    goal_id = data["goal"].get("id", "")
    if not SAFE_ID.fullmatch(goal_id):
        errors.append(f"goal id {goal_id!r} is not a valid claim id")
    if not str(data["goal"].get("statement", "")).strip():
        errors.append("goal has no statement")
    seen: set[str] = {goal_id}
    for n in data["nodes"]:
        nid = n.get("id", "")
        if not SAFE_ID.fullmatch(nid):
            errors.append(f"node id {nid!r} is not a valid claim id")
            continue
        if nid in seen:
            errors.append(f"duplicate node id {nid!r}")
        seen.add(nid)
        if not str(n.get("statement", "")).strip():
            errors.append(f"node {nid} has no statement")
        if bool(n.get("formal_statement")) != bool(n.get("theorem_name")):
            errors.append(f"node {nid}: formal_statement and theorem_name go together")
        if not n.get("supports"):
            errors.append(f"node {nid} supports nothing — every node must feed the "
                          f"goal or another node")
    ids = node_ids(data)
    for n in data["nodes"]:
        for target in n.get("supports", []):
            if target not in ids:
                errors.append(f"node {n['id']} supports unknown node {target!r}")
            if target == n["id"]:
                errors.append(f"node {n['id']} supports itself")
    # Cycle check over the supports relation (goal has no outgoing edges).
    if not errors:
        colors: dict[str, int] = {}

        def visit(nid: str, trail: tuple[str, ...]) -> None:
            state = colors.get(nid, 0)
            if state == 1:
                errors.append(f"cycle through {' -> '.join(trail + (nid,))}")
                return
            if state == 2:
                return
            colors[nid] = 1
            node = next((x for x in data["nodes"] if x["id"] == nid), None)
            for target in (node or {}).get("supports", []):
                visit(target, trail + (nid,))
            colors[nid] = 2

        for n in data["nodes"]:
            visit(n["id"], ())
    return errors


def orphans(data: dict) -> list[str]:
    """Nodes from which the goal is unreachable — side quests, worth flagging."""
    goal_id = data["goal"]["id"]
    reached: set[str] = set()

    def reaches_goal(nid: str, seen: frozenset[str]) -> bool:
        if nid == goal_id:
            return True
        if nid in reached:
            return True
        if nid in seen:
            return False
        node = next((x for x in data["nodes"] if x["id"] == nid), None)
        ok = any(reaches_goal(t, seen | {nid}) for t in (node or {}).get("supports", []))
        if ok:
            reached.add(nid)
        return ok

    return [n["id"] for n in data["nodes"] if not reaches_goal(n["id"], frozenset())]


def ledger_statuses(project: Path) -> dict[str, dict]:
    """Latest gate decision per claim_id. The ledger is append-only: last wins."""
    path = project / LEDGER_REL
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # a corrupt line must not take the map down
        cid = entry.get("claim_id")
        if cid:
            out[cid] = entry
    return out


def regressions(project: Path) -> set[str]:
    """Claim ids whose previously-proven artifact failed the last re-check."""
    path = project / REVERIFY_REL
    if not path.exists():
        return set()
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        return set(report.get("regressions", []))
    except (json.JSONDecodeError, AttributeError):
        return set()


def derived_status(nid: str, decisions: dict[str, dict], regressed: set[str]) -> str:
    if nid in regressed:
        return "regressed"
    entry = decisions.get(nid)
    if not entry:
        return "untried"
    status = entry.get("status", "untried")
    return status if status in STATUS_ICON else "untried"


def ready_nodes(data: dict, decisions: dict[str, dict], regressed: set[str]) -> list[dict]:
    """Nodes worth attempting now: not established, all ingredients established."""
    out = []
    for n in data["nodes"]:
        status = derived_status(n["id"], decisions, regressed)
        if status in ESTABLISHED:
            continue
        if status == "refuted":
            continue  # a red node needs redrawing, not retrying as-is
        ingredients = ingredients_of(data, n["id"])
        if all(derived_status(i["id"], decisions, regressed) in ESTABLISHED
               for i in ingredients):
            out.append(n)
    # Deepest first: leaves before the lemmas that depend on them.
    depth: dict[str, int] = {}

    def depth_of(nid: str) -> int:
        if nid in depth:
            return depth[nid]
        depth[nid] = 0  # cycle guard; validate() rejects real cycles
        ings = ingredients_of(data, nid)
        depth[nid] = 1 + max((depth_of(i["id"]) for i in ings), default=0)
        return depth[nid]

    return sorted(out, key=lambda n: (depth_of(n["id"]), n["id"]))


def mission_command(node: dict) -> str:
    parts = [f"python3 scripts/run_mission.py --claim-id {node['id']}",
             f"--statement {json.dumps(node['statement'], ensure_ascii=False)}"]
    if node.get("formal_statement"):
        parts.append(f"--formal-statement {json.dumps(node['formal_statement'], ensure_ascii=False)}")
        parts.append(f"--theorem-name {node['theorem_name']}")
    return " \\\n  ".join(parts)


def render(project: Path, data: dict) -> Path:
    decisions = ledger_statuses(project)
    regressed = regressions(project)
    goal = data["goal"]
    lines = [f"# Map — {goal['statement']}", ""]
    lines.append("> This map is a plan, not a verdict. It was drawn by fallible "
                 "people and models and may be redrawn. Colors are derived from "
                 "the gate's ledger only — nothing here can be painted green by "
                 "hand. A green region can still be the wrong path; a red node "
                 "is information, not failure.")
    lines.append("")

    counts: dict[str, int] = {}
    for n in data["nodes"]:
        s = derived_status(n["id"], decisions, regressed)
        counts[s] = counts.get(s, 0) + 1
    summary = ", ".join(f"{STATUS_ICON[s]} {s}: {c}" for s, c in sorted(counts.items()))
    lines.append(f"**Nodes:** {len(data['nodes'])} — {summary or 'none yet'}")
    lines.append("")

    rendered: set[str] = set()

    def emit(nid: str, statement: str, indent: int) -> None:
        status = derived_status(nid, decisions, regressed)
        icon = STATUS_ICON.get(status, "⬜")
        pad = "  " * indent
        if nid in rendered:
            lines.append(f"{pad}- {icon} **{nid}** *(see above)*")
            return
        rendered.add(nid)
        entry = decisions.get(nid, {})
        run_note = f" — run `{entry['run']}`" if entry.get("run") else ""
        lines.append(f"{pad}- {icon} **{nid}** `{status}`{run_note} — {statement}")
        for child in sorted(ingredients_of(data, nid), key=lambda x: x["id"]):
            emit(child["id"], child["statement"], indent + 1)

    lines.append(f"## Goal: {goal['id']}")
    lines.append("")
    emit(goal["id"], goal["statement"], 0)

    stray = orphans(data)
    if stray:
        lines.append("")
        lines.append(f"**Side quests (do not reach the goal):** {', '.join(sorted(stray))}")

    ready = ready_nodes(data, decisions, regressed)
    lines.append("")
    lines.append("## Next targets (all ingredients established)")
    lines.append("")
    if ready:
        for n in ready[:5]:
            formal = "formal target set" if n.get("formal_statement") \
                else "NO formal target yet — `proven` impossible until one is set"
            lines.append(f"- **{n['id']}** — {n['statement']} *({formal})*")
    else:
        lines.append("- none — either everything is established or the map needs redrawing")
    lines.append("")
    lines.append(f"*Rendered {datetime.now(timezone.utc).isoformat(timespec='seconds')} "
                 f"from the decisions ledger; regenerate with `map_tool.py render`.*")

    out = project / RENDER_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Keep a previously requested Obsidian view fresh: every render re-derives
    # the notes and the canvas from the same ledger.
    if (project / OBSIDIAN_STAMP_REL).exists():
        export_obsidian(project)
    return out


# --- Obsidian view ----------------------------------------------------------
# One note per node plus a Canvas dashboard (JSON Canvas 1.0, rendered natively
# by Obsidian — no plugin). Both are DERIVED views: regenerated from map.json
# and the ledger, never hand-edited, same guarantee as map.md — nothing here
# can be painted green by hand.

CANVAS_COLOR = {
    "proven": "4",       # green
    "known": "5",        # cyan
    "refuted": "1",      # red
    "contested": "2",    # orange
    "regressed": "2",    # orange; the note title carries the ⚠
    "conjecture": "3",   # yellow
    "sketch": "3",       # yellow
    # not_established / untried: no color -> Obsidian's neutral gray
}
CARD_W, CARD_H, GAP_X, GAP_Y = 400, 160, 60, 130


def _layers(data: dict) -> dict[str, int]:
    """Layer 0 = the goal; a node sits one layer below everything it feeds."""
    goal_id = data["goal"]["id"]
    ids = node_ids(data)
    memo: dict[str, int] = {goal_id: 0}

    def layer_of(nid: str, seen: frozenset[str]) -> int:
        if nid in memo:
            return memo[nid]
        if nid in seen:
            return 1  # cycle guard; validate() rejects real cycles
        node = next((x for x in data["nodes"] if x["id"] == nid), None)
        parents = [layer_of(t, seen | {nid})
                   for t in (node or {}).get("supports", []) if t in ids]
        memo[nid] = 1 + max(parents, default=0)
        return memo[nid]

    for n in data["nodes"]:
        layer_of(n["id"], frozenset())
    return memo


def _note(node: dict, status: str, entry: dict, goal: bool = False) -> str:
    """One Obsidian note per node: frontmatter for filters, wikilinks for the graph."""
    def q(v: str) -> str:  # JSON string literals are valid YAML scalars
        return json.dumps(v, ensure_ascii=False)

    warn = "⚠ " if status == "regressed" else ""
    fm = ["---",
          f"map-id: {q(node['id'])}",
          f"status: {status}",
          f"tags: [map, map/{status}]"]
    if entry.get("run"):
        fm.append(f"run: {q(entry['run'])}")
    if node.get("theorem_name"):
        fm.append(f"theorem-name: {q(node['theorem_name'])}")
    fm.append("---")
    body = [f"# {warn}{node['id']} — `{status}`", "", node.get("statement", ""), ""]
    if node.get("formal_statement"):
        body += ["```lean", node["formal_statement"], "```", ""]
    if node.get("notes"):
        body += [node["notes"], ""]
    if goal:
        body += ["*This is the goal. Node colors come only from the gate's "
                 "ledger; the map itself is a plan and may be redrawn.*", ""]
    elif node.get("supports"):
        body += ["Feeds into: " + ", ".join(f"[[{t}]]" for t in node["supports"]), ""]
    body += ["*Generated by `map_tool.py export-obsidian` — do not edit; "
             "regenerated on every render.*"]
    return "\n".join(fm + [""] + body) + "\n"


def _canvas(data: dict, statuses: dict[str, str], folder: str) -> dict:
    layers = _layers(data)
    goal_id = data["goal"]["id"]
    everything = [{"id": goal_id}] + [{"id": n["id"]} for n in data["nodes"]]
    by_layer: dict[int, list[str]] = {}
    for n in everything:
        by_layer.setdefault(layers.get(n["id"], 0), []).append(n["id"])
    nodes = []
    for layer, ids in sorted(by_layer.items()):
        total = len(ids) * CARD_W + (len(ids) - 1) * GAP_X
        x0 = -total // 2
        for i, nid in enumerate(sorted(ids)):
            status = statuses.get(nid, "untried")
            card = {"id": nid, "type": "file", "file": f"{folder}/{nid}.md",
                    "x": x0 + i * (CARD_W + GAP_X),
                    "y": layer * (CARD_H + GAP_Y),
                    "width": CARD_W, "height": CARD_H}
            # An unattempted goal gets the accent color so the target stands out.
            color = "6" if nid == goal_id and status == "untried" \
                else CANVAS_COLOR.get(status)
            if color:
                card["color"] = color
            nodes.append(card)
    edges = [{"id": f"e-{n['id']}-{t}",
              "fromNode": n["id"], "fromSide": "top",
              "toNode": t, "toSide": "bottom", "toEnd": "arrow"}
             for n in data["nodes"] for t in n.get("supports", [])]
    return {"nodes": nodes, "edges": edges}


def export_obsidian(project: Path, out_rel: str | None = None) -> Path:
    """Write the vault-visible view; own the folder, never touch foreign files."""
    data = load_map(project)
    stamp_path = project / OBSIDIAN_STAMP_REL
    stamp: dict = {}
    if stamp_path.exists():
        try:
            stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            stamp = {}
    rel = out_rel or stamp.get("out_dir", "map")
    out_dir = (project / rel).resolve()
    try:
        folder = out_dir.relative_to(project.resolve()).as_posix()
    except ValueError:
        raise SystemExit("error: the Obsidian view must live inside the project")
    if out_dir.exists() and stamp.get("out_dir") != folder and any(out_dir.iterdir()):
        raise SystemExit(f"error: {out_dir} exists, is not empty, and was not "
                         f"created by this exporter — refusing to overwrite it")
    out_dir.mkdir(parents=True, exist_ok=True)

    decisions = ledger_statuses(project)
    regressed = regressions(project)
    goal_id = data["goal"]["id"]
    statuses = {n["id"]: derived_status(n["id"], decisions, regressed)
                for n in data["nodes"]}
    statuses[goal_id] = derived_status(goal_id, decisions, regressed)

    written: list[str] = []

    def write(name: str, content: str) -> None:
        (out_dir / name).write_text(content, encoding="utf-8")
        written.append(name)

    write("README.md", "\n".join([
        "# Map view (generated)", "",
        "This folder is a DERIVED view of `.adversal/map/map.json` plus the",
        "gate's decisions ledger. Open **Map.canvas** for the treasure-map",
        "layout (goal on top, colored from the ledger), or use Obsidian's graph",
        "view — suggested color groups: `tag:#map/proven` green,",
        "`tag:#map/refuted` red, `tag:#map/regressed` orange.", "",
        "Do not edit these files; every `map_tool.py render` regenerates them.",
        "Colors cannot be painted by hand — that is the point.", ""]))
    goal_note = {"id": goal_id, "statement": data["goal"]["statement"]}
    write(f"{goal_id}.md", _note(goal_note, statuses[goal_id],
                                 decisions.get(goal_id, {}), goal=True))
    for n in data["nodes"]:
        write(f"{n['id']}.md", _note(n, statuses[n["id"]], decisions.get(n["id"], {})))
    write("Map.canvas", json.dumps(_canvas(data, statuses, folder),
                                   indent=2, ensure_ascii=False) + "\n")

    # Drop files we generated for nodes that no longer exist. Foreign files in
    # the folder are never touched.
    for stale in set(stamp.get("files", [])) - set(written):
        (out_dir / stale).unlink(missing_ok=True)
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    stamp_path.write_text(json.dumps({"out_dir": folder,
                                      "files": sorted(written)}, indent=2) + "\n",
                          encoding="utf-8")
    return out_dir / "Map.canvas"


def cmd_export_obsidian(args: argparse.Namespace) -> int:
    canvas = export_obsidian(args.project, args.out_dir)
    print(canvas)
    print("Open the project folder as an Obsidian vault, then open Map.canvas: "
          "goal on top, cards colored from the gate's ledger, click a card to "
          "open its lemma note. Every `map_tool.py render` refreshes this view.")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    path = args.project / MAP_REL
    if path.exists():
        print(f"error: map already exists at {path}; edit it with `add`/`import` "
              f"or remove it deliberately first", file=sys.stderr)
        return 1
    if not SAFE_ID.fullmatch(args.goal_id):
        print("error: --goal-id must be a valid claim id", file=sys.stderr)
        return 1
    data = {"version": 1,
            "goal": {"id": args.goal_id, "statement": args.goal},
            "nodes": []}
    save_map(args.project, data)
    render(args.project, data)
    print(f"map initialized: {path}")
    print("Add ingredient lemmas with `map_tool.py add`, or let the strategist "
          "propose a decomposition with `decompose.py` and import the ones you accept.")
    return 0


def _add_node(data: dict, node: dict) -> str | None:
    """Append one node; returns an error string or None."""
    trial = {"version": data.get("version", 1), "goal": data["goal"],
             "nodes": data["nodes"] + [node]}
    errors = validate(trial)
    if errors:
        return "; ".join(errors)
    data["nodes"].append(node)
    return None


def cmd_add(args: argparse.Namespace) -> int:
    data = load_map(args.project)
    node = {
        "id": args.id,
        "statement": args.statement,
        "supports": [s.strip() for s in args.supports.split(",") if s.strip()]
                    or [data["goal"]["id"]],
        "formal_statement": args.formal_statement,
        "theorem_name": args.theorem_name,
        "notes": args.notes,
    }
    err = _add_node(data, node)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    save_map(args.project, data)
    render(args.project, data)
    print(f"added {args.id} -> supports {', '.join(node['supports'])}")
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    """Set the formal target of an existing node (the sanctioned way — the
    map file itself is gate-owned and must not be hand-edited)."""
    data = load_map(args.project)
    node = next((n for n in data["nodes"] if n["id"] == args.id), None)
    if node is None:
        print(f"error: no node {args.id!r} on the map", file=sys.stderr)
        return 1
    node["formal_statement"] = args.formal_statement
    node["theorem_name"] = args.theorem_name
    if args.notes is not None:
        node["notes"] = args.notes
    errors = validate(data)
    if errors:
        print("; ".join(errors), file=sys.stderr)
        return 1
    save_map(args.project, data)
    render(args.project, data)
    print(f"set formal target on {args.id}: `{args.theorem_name}`")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    data = load_map(args.project)
    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    nodes = proposal.get("nodes", [])
    only = {s.strip() for s in args.only.split(",") if s.strip()} if args.only else None
    accepted, rejected = [], []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        nid = str(n.get("id", ""))
        if only is not None and nid not in only:
            continue
        node = {
            "id": nid,
            "statement": str(n.get("statement", "")),
            "supports": [str(s) for s in n.get("supports", [])] or [data["goal"]["id"]],
            "formal_statement": str(n.get("formal_statement", "") or ""),
            "theorem_name": str(n.get("theorem_name", "") or ""),
            "notes": str(n.get("rationale", n.get("notes", "")) or ""),
        }
        err = _add_node(data, node)
        (rejected if err else accepted).append((nid, err))
    if accepted:
        save_map(args.project, data)
        render(args.project, data)
    for nid, _ in accepted:
        print(f"imported {nid}")
    for nid, err in rejected:
        print(f"rejected {nid or '<missing id>'}: {err}", file=sys.stderr)
    if not accepted and not rejected:
        print("nothing matched — check --only against the proposal ids", file=sys.stderr)
    return 0 if accepted and not rejected else 1


def cmd_check(args: argparse.Namespace) -> int:
    data = load_map(args.project)
    errors = validate(data)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    stray = orphans(data)
    if stray:
        print(f"warning: side quests that never reach the goal: {', '.join(sorted(stray))}",
              file=sys.stderr)
    if not errors:
        print(f"map ok: {len(data['nodes'])} node(s), goal {data['goal']['id']}")
    return 1 if errors else 0


def cmd_render(args: argparse.Namespace) -> int:
    data = load_map(args.project)
    out = render(args.project, data)
    print(out)
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    data = load_map(args.project)
    decisions = ledger_statuses(args.project)
    ready = ready_nodes(data, decisions, regressions(args.project))
    if not ready:
        print("no ready targets — either everything is established or the map "
              "needs redrawing (check red nodes)")
        return 0
    for n in ready[: args.n]:
        print(f"# {n['id']} — {n['statement']}")
        if not n.get("formal_statement"):
            print("#   note: no formal target yet; `proven` is impossible until "
                  "--formal-statement/--theorem-name are set on this node")
        print(mission_command(n))
        print()
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    data = load_map(args.project)
    decisions = ledger_statuses(args.project)
    regressed = regressions(args.project)
    nodes = [{
        "id": n["id"],
        "status": derived_status(n["id"], decisions, regressed),
        "supports": n.get("supports", []),
        "has_formal_target": bool(n.get("formal_statement")),
    } for n in data["nodes"]]
    ready = [n["id"] for n in ready_nodes(data, decisions, regressed)]
    report = {
        "goal": data["goal"]["id"],
        "nodes": nodes,
        "ready": ready,
        "counts": {s: sum(1 for n in nodes if n["status"] == s)
                   for s in sorted({n["status"] for n in nodes})},
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for n in nodes:
            print(f"{STATUS_ICON.get(n['status'], '⬜')} {n['id']}: {n['status']}")
        print(f"ready: {', '.join(ready) or 'none'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dependency map toward one goal; "
                                             "colors come only from the gate")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--project", type=Path, default=Path.cwd(),
                       help="project root containing .adversal/")

    p = sub.add_parser("init", help="create the map with its goal node")
    common(p)
    p.add_argument("--goal", required=True, help="the goal statement, in natural language")
    p.add_argument("--goal-id", default="GOAL")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("add", help="add one ingredient node")
    common(p)
    p.add_argument("--id", required=True)
    p.add_argument("--statement", required=True)
    p.add_argument("--supports", default="", help="comma-separated node ids this "
                                                  "lemma feeds (default: the goal)")
    p.add_argument("--formal-statement", default="")
    p.add_argument("--theorem-name", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("set", help="set the formal Lean target of an existing node")
    common(p)
    p.add_argument("--id", required=True)
    p.add_argument("--formal-statement", required=True)
    p.add_argument("--theorem-name", required=True)
    p.add_argument("--notes", default=None)
    p.set_defaults(fn=cmd_set)

    p = sub.add_parser("import", help="import accepted nodes from a decompose proposal")
    common(p)
    p.add_argument("--proposal", required=True)
    p.add_argument("--only", default="", help="comma-separated ids to accept "
                                              "(default: all)")
    p.set_defaults(fn=cmd_import)

    p = sub.add_parser("check", help="validate map structure")
    common(p)
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("render", help="write map.md with ledger-derived colors")
    common(p)
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("next", help="print ready targets as run_mission commands")
    common(p)
    p.add_argument("--n", type=int, default=3)
    p.set_defaults(fn=cmd_next)

    p = sub.add_parser("export-obsidian",
                       help="write the vault-visible view: one note per node + "
                            "a colored Map.canvas (kept fresh by every render)")
    common(p)
    p.add_argument("--out-dir", default=None,
                   help="folder inside the project for the view (default: map)")
    p.set_defaults(fn=cmd_export_obsidian)

    p = sub.add_parser("status", help="machine-readable map state")
    common(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_status)

    args = ap.parse_args(argv)
    if hasattr(args, "id") and not SAFE_ID.fullmatch(args.id):
        ap.error("--id must contain only letters, digits, dot, underscore, or hyphen")
    if hasattr(args, "formal_statement") and \
            bool(args.formal_statement) != bool(args.theorem_name):
        ap.error("--formal-statement and --theorem-name must be supplied together")
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
