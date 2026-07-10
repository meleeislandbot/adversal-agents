from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "templates" / "project" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


map_tool = load("map_tool")
reverify = load("reverify")
backtranslate = load("backtranslate")


def run_cli(module, argv: list[str]) -> tuple[int, str, str]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = module.main(argv)
        except SystemExit as exc:  # argparse errors and load_map failures
            code = int(exc.code) if isinstance(exc.code, int) else 1
    return code, stdout.getvalue(), stderr.getvalue()


class MapToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)

    def init_map(self) -> None:
        code, _, err = run_cli(map_tool, [
            "init", "--project", str(self.project), "--goal", "The goal statement."])
        self.assertEqual(code, 0, err)

    def add(self, nid: str, supports: str = "", formal: bool = False) -> tuple[int, str]:
        argv = ["add", "--project", str(self.project), "--id", nid,
                "--statement", f"Statement for {nid}."]
        if supports:
            argv += ["--supports", supports]
        if formal:
            argv += ["--formal-statement", "∀ n : Nat, n = n",
                     "--theorem-name", f"thm_{nid.replace('-', '_')}"]
        code, _, err = run_cli(map_tool, argv)
        return code, err

    def write_ledger(self, entries: list[dict]) -> None:
        ledger = self.project / ".adversal" / "ledgers" / "decisions.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text("\n".join(json.dumps(e) for e in entries) + "\n",
                          encoding="utf-8")

    def test_init_add_check(self) -> None:
        self.init_map()
        self.assertEqual(self.add("L1")[0], 0)
        self.assertEqual(self.add("L2", supports="L1")[0], 0)
        code, out, _ = run_cli(map_tool, ["check", "--project", str(self.project)])
        self.assertEqual(code, 0)
        self.assertIn("map ok", out)

    def test_duplicate_and_unknown_supports_rejected(self) -> None:
        self.init_map()
        self.assertEqual(self.add("L1")[0], 0)
        code, err = self.add("L1")
        self.assertEqual(code, 1)
        self.assertIn("duplicate", err)
        code, err = self.add("L9", supports="NOPE")
        self.assertEqual(code, 1)
        self.assertIn("unknown", err)

    def test_cycle_detected_by_validate(self) -> None:
        data = {"version": 1, "goal": {"id": "GOAL", "statement": "g"},
                "nodes": [
                    {"id": "A", "statement": "a", "supports": ["B"]},
                    {"id": "B", "statement": "b", "supports": ["A"]},
                ]}
        errors = map_tool.validate(data)
        self.assertTrue(any("cycle" in e for e in errors), errors)

    def test_colors_come_only_from_ledger_last_entry_wins(self) -> None:
        self.init_map()
        self.add("L1")
        self.add("L2")
        self.write_ledger([
            {"claim_id": "L1", "status": "proven", "run": "r1"},
            {"claim_id": "L1", "status": "not_established", "run": "r2"},
            {"claim_id": "L2", "status": "refuted", "run": "r3"},
        ])
        code, out, _ = run_cli(map_tool, ["status", "--project", str(self.project), "--json"])
        self.assertEqual(code, 0)
        report = json.loads(out)
        by_id = {n["id"]: n["status"] for n in report["nodes"]}
        self.assertEqual(by_id["L1"], "not_established")  # append-only: last wins
        self.assertEqual(by_id["L2"], "refuted")

    def test_ready_requires_established_ingredients(self) -> None:
        self.init_map()
        self.add("L1")                      # leaf
        self.add("L2", supports="GOAL")     # leaf
        self.add("L3")                      # parent of L1 via next add
        # rewire: L1 supports L3
        data = map_tool.load_map(self.project)
        next(n for n in data["nodes"] if n["id"] == "L1")["supports"] = ["L3"]
        map_tool.save_map(self.project, data)
        # nothing proven: only leaves are ready
        code, out, _ = run_cli(map_tool, ["status", "--project", str(self.project), "--json"])
        ready = json.loads(out)["ready"]
        self.assertIn("L1", ready)
        self.assertIn("L2", ready)
        self.assertNotIn("L3", ready)
        # L1 proven -> L3 becomes ready; refuted L2 is never "ready"
        self.write_ledger([
            {"claim_id": "L1", "status": "proven", "run": "r1"},
            {"claim_id": "L2", "status": "refuted", "run": "r2"},
        ])
        code, out, _ = run_cli(map_tool, ["status", "--project", str(self.project), "--json"])
        ready = json.loads(out)["ready"]
        self.assertIn("L3", ready)
        self.assertNotIn("L1", ready)
        self.assertNotIn("L2", ready)

    def test_set_formal_target_on_existing_node(self) -> None:
        self.init_map()
        self.add("L1")
        code, _, err = run_cli(map_tool, [
            "set", "--project", str(self.project), "--id", "L1",
            "--formal-statement", "∀ n : Nat, n = n",
            "--theorem-name", "l1_refl"])
        self.assertEqual(code, 0, err)
        data = map_tool.load_map(self.project)
        node = next(n for n in data["nodes"] if n["id"] == "L1")
        self.assertEqual(node["theorem_name"], "l1_refl")
        code, _, err = run_cli(map_tool, [
            "set", "--project", str(self.project), "--id", "NOPE",
            "--formal-statement", "True", "--theorem-name", "t"])
        self.assertEqual(code, 1)
        self.assertIn("no node", err)

    def test_import_only_accepts_subset(self) -> None:
        self.init_map()
        proposal = self.project / "proposal.json"
        proposal.write_text(json.dumps({"target": "GOAL", "nodes": [
            {"id": "P1", "statement": "p1", "supports": ["GOAL"], "rationale": "why"},
            {"id": "P2", "statement": "p2", "supports": ["GOAL"]},
        ]}), encoding="utf-8")
        code, out, err = run_cli(map_tool, [
            "import", "--project", str(self.project),
            "--proposal", str(proposal), "--only", "P1"])
        self.assertEqual(code, 0, err)
        data = map_tool.load_map(self.project)
        ids = {n["id"] for n in data["nodes"]}
        self.assertEqual(ids, {"P1"})

    def test_render_mentions_goal_and_honesty_note(self) -> None:
        self.init_map()
        self.add("L1", formal=True)
        code, _, _ = run_cli(map_tool, ["render", "--project", str(self.project)])
        self.assertEqual(code, 0)
        md = (self.project / ".adversal" / "map" / "map.md").read_text(encoding="utf-8")
        self.assertIn("The goal statement.", md)
        self.assertIn("plan, not a verdict", md)
        self.assertIn("L1", md)

    def test_next_emits_runnable_commands(self) -> None:
        self.init_map()
        self.add("L1", formal=True)
        code, out, _ = run_cli(map_tool, ["next", "--project", str(self.project)])
        self.assertEqual(code, 0)
        self.assertIn("run_mission.py", out)
        self.assertIn("--claim-id L1", out)
        self.assertIn("--formal-statement", out)


class ObsidianExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        run_cli(map_tool, ["init", "--project", str(self.project),
                           "--goal", "Toy goal."])
        run_cli(map_tool, ["add", "--project", str(self.project), "--id", "L1",
                           "--statement", "Lemma one."])
        run_cli(map_tool, ["add", "--project", str(self.project), "--id", "L2",
                           "--statement", "Lemma two.", "--supports", "L1"])
        ledger = self.project / ".adversal" / "ledgers" / "decisions.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(json.dumps(
            {"claim_id": "L1", "status": "proven", "run": "r1"}) + "\n",
            encoding="utf-8")

    def test_export_writes_canvas_notes_and_colors(self) -> None:
        code, out, err = run_cli(map_tool, ["export-obsidian",
                                            "--project", str(self.project)])
        self.assertEqual(code, 0, err)
        canvas = json.loads((self.project / "map" / "Map.canvas")
                            .read_text(encoding="utf-8"))
        self.assertEqual(len(canvas["nodes"]), 3)  # goal + L1 + L2
        self.assertEqual(len(canvas["edges"]), 2)  # L1->GOAL, L2->L1
        colors = {n["id"]: n.get("color") for n in canvas["nodes"]}
        self.assertEqual(colors["L1"], "4")        # proven -> green
        self.assertEqual(colors["GOAL"], "6")      # untried goal -> accent
        note = (self.project / "map" / "L1.md").read_text(encoding="utf-8")
        self.assertIn("status: proven", note)
        self.assertIn("map/proven", note)
        l2 = (self.project / "map" / "L2.md").read_text(encoding="utf-8")
        self.assertIn("[[L1]]", l2)

    def test_refuses_foreign_nonempty_dir(self) -> None:
        foreign = self.project / "map"
        foreign.mkdir()
        (foreign / "mine.md").write_text("user file", encoding="utf-8")
        code, _, err = run_cli(map_tool, ["export-obsidian",
                                          "--project", str(self.project)])
        self.assertEqual(code, 1)
        self.assertEqual((foreign / "mine.md").read_text(encoding="utf-8"),
                         "user file")

    def test_render_refreshes_view_and_removes_stale_notes(self) -> None:
        run_cli(map_tool, ["export-obsidian", "--project", str(self.project)])
        # Ledger changes; a plain render must refresh the exported note.
        ledger = self.project / ".adversal" / "ledgers" / "decisions.jsonl"
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"claim_id": "L2", "status": "refuted",
                                 "run": "r2"}) + "\n")
        run_cli(map_tool, ["render", "--project", str(self.project)])
        l2 = (self.project / "map" / "L2.md").read_text(encoding="utf-8")
        self.assertIn("status: refuted", l2)
        # Removing a node drops its generated note on the next export.
        data = map_tool.load_map(self.project)
        data["nodes"] = [n for n in data["nodes"] if n["id"] != "L2"]
        map_tool.save_map(self.project, data)
        run_cli(map_tool, ["render", "--project", str(self.project)])
        self.assertFalse((self.project / "map" / "L2.md").exists())
        canvas = json.loads((self.project / "map" / "Map.canvas")
                            .read_text(encoding="utf-8"))
        self.assertEqual(len(canvas["nodes"]), 2)


class ReverifyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)

    def make_run(self, name: str, with_spec: bool) -> Path:
        run = self.project / ".adversal" / "runs" / name
        run.mkdir(parents=True)
        (run / "verdict.json").write_text(json.dumps([{
            "claim_id": "C1", "status": "proven",
            "lean_artifact": "lean/C1.lean"}]), encoding="utf-8")
        claim = {"claim_id": "C1", "statement": "s"}
        if with_spec:
            claim.update({"formal_statement": "True", "theorem_name": "T"})
        (run / "claims.json").write_text(json.dumps([claim]), encoding="utf-8")
        return run

    def test_unreproducible_and_missing_artifact_are_regressions(self) -> None:
        self.make_run("r-old", with_spec=False)   # pre-canonical run
        self.make_run("r-new", with_spec=True)    # spec but artifact file absent
        with patch.object(reverify.verdict_engine, "_resolve_tool",
                          return_value="/usr/bin/true"):
            code, out, _ = run_cli(reverify, ["--project", str(self.project)])
        self.assertEqual(code, 1)
        report = json.loads((self.project / ".adversal" / "map" /
                             "reverify-latest.json").read_text(encoding="utf-8"))
        self.assertEqual(report["checked"], 2)
        self.assertEqual(report["passed"], 0)
        self.assertIn("C1", report["regressions"])
        reasons = {i["run"]: i["reason"] for i in report["items"]}
        self.assertIn("unreproducible", reasons["r-old"])

    def test_without_lean_refuses_to_pass(self) -> None:
        self.make_run("r-new", with_spec=True)
        with patch.object(reverify.verdict_engine, "_resolve_tool", return_value=None):
            code, _, err = run_cli(reverify, ["--project", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("do not treat this as a pass", err)


class BacktranslateHintTests(unittest.TestCase):
    def test_numeric_mismatch_flagged_both_directions(self) -> None:
        hints = backtranslate.numeric_hint("∀ p, p > 2 → Odd p",
                                           "todo primo mayor que 3 es impar")
        joined = " ".join(hints)
        self.assertIn("2", joined)
        self.assertIn("3", joined)

    def test_no_numbers_no_noise(self) -> None:
        self.assertEqual(
            backtranslate.numeric_hint("∀ n : Nat, n = n",
                                       "todo natural es igual a sí mismo"), [])


if __name__ == "__main__":
    unittest.main()
