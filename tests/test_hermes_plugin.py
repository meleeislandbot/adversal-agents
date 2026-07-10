from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "integrations" / "hermes-adversal" / "__init__.py"
SPEC = importlib.util.spec_from_file_location("hermes_adversal", PLUGIN)
assert SPEC and SPEC.loader
plugin = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = plugin
SPEC.loader.exec_module(plugin)


class StubCtx:
    def __init__(self) -> None:
        self.tools: dict[str, dict] = {}
        self.hooks: dict[str, list] = {}
        self.commands: dict[str, tuple] = {}

    def register_tool(self, *, name, toolset, schema, handler, description):
        self.tools[name] = {"toolset": toolset, "schema": schema,
                            "handler": handler, "description": description}

    def register_hook(self, event, callback):
        self.hooks.setdefault(event, []).append(callback)

    def register_command(self, name, handler, description):
        self.commands[name] = (handler, description)


class RegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ctx = StubCtx()
        plugin.register(self.ctx)

    def test_registers_toolset_hooks_and_command(self) -> None:
        expected = {"adversal_mission", "adversal_map_init", "adversal_map_add",
                    "adversal_map_set", "adversal_map_import",
                    "adversal_map_next", "adversal_map_status",
                    "adversal_decompose", "adversal_ideate",
                    "adversal_backtranslate", "adversal_reverify",
                    "adversal_bib_add", "adversal_bib_digest"}
        self.assertEqual(set(self.ctx.tools), expected)
        for name, entry in self.ctx.tools.items():
            self.assertEqual(entry["toolset"], "adversal")
            params = entry["schema"]["parameters"]
            self.assertEqual(params["type"], "object")
            self.assertIn("properties", params)
        self.assertIn("pre_tool_call", self.ctx.hooks)
        self.assertIn("pre_llm_call", self.ctx.hooks)
        self.assertIn("map", self.ctx.commands)

    def test_mission_builds_sanctioned_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".adversal").mkdir()
            (project / ".adversal" / "project.yaml").write_text("x: 1\n")
            (project / "scripts").mkdir()
            (project / "scripts" / "run_mission.py").write_text("")
            (project / "scripts" / "map_tool.py").write_text("")
            calls = []

            def fake_run(cmd, **kwargs):
                calls.append(cmd)

                class R:
                    returncode = 0
                    stdout = "ok"
                    stderr = ""
                return R()

            with patch.object(plugin.subprocess, "run", side_effect=fake_run):
                out = json.loads(self.ctx.tools["adversal_mission"]["handler"](
                    {"statement": "n = n", "claim_id": "L1",
                     "formal_statement": "∀ n : Nat, n = n",
                     "theorem_name": "l1", "project": str(project)}))
            self.assertTrue(out["success"])
            mission_cmd = calls[0]
            self.assertIn("--claim-id", mission_cmd)
            self.assertIn("L1", mission_cmd)
            self.assertIn("--formal-statement", mission_cmd)
            # the map refresh follows the mission
            self.assertTrue(any("map_tool.py" in str(c) for c in calls[1]))

    def test_missing_project_is_a_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = json.loads(self.ctx.tools["adversal_map_status"]["handler"](
                {"project": tmp}))
        self.assertFalse(out["success"])
        self.assertIn("project", out["error"])


class GuardTests(unittest.TestCase):
    def test_blocks_hand_edit_of_ledger(self) -> None:
        decision = plugin.guard_decision(
            "write_file", {"path": "/p/.adversal/ledgers/decisions.jsonl",
                           "content": "{...}"})
        self.assertIsNotNone(decision)
        self.assertEqual(decision["action"], "block")

    def test_blocks_terminal_redirect_into_verdict(self) -> None:
        decision = plugin.guard_decision(
            "terminal", {"command": "echo '{}' > runs/x/verdict.json"})
        self.assertIsNotNone(decision)

    def test_allows_sanctioned_writer(self) -> None:
        self.assertIsNone(plugin.guard_decision(
            "terminal",
            {"command": "python3 scripts/run_mission.py --statement 'x' "
                        "--claim-id C1"}))

    def test_allows_reads_and_unrelated_writes(self) -> None:
        self.assertIsNone(plugin.guard_decision(
            "terminal", {"command": "cat .adversal/ledgers/decisions.jsonl"}))
        self.assertIsNone(plugin.guard_decision(
            "write_file", {"path": "/p/notes/scratch.md", "content": "hi"}))

    def test_guard_never_raises(self) -> None:
        self.assertIsNone(plugin.guard_decision("terminal", {"command": None}))
        self.assertIsNone(plugin.guard_decision("", 42))  # type: ignore[arg-type]


class ProjectAnchorTests(unittest.TestCase):
    def test_env_var_anchors_project_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            (project / ".adversal").mkdir(parents=True)
            (project / ".adversal" / "project.yaml").write_text("x: 1\n")
            with patch.dict(plugin.os.environ,
                            {"ADVERSAL_PROJECT": str(project)}):
                self.assertEqual(plugin.find_project(), project.resolve())
            # A bogus anchor is ignored rather than trusted.
            with patch.dict(plugin.os.environ,
                            {"ADVERSAL_PROJECT": str(Path(tmp) / "nope")}):
                found = plugin.find_project()
                self.assertNotEqual(found, Path(tmp) / "nope")

    def test_explicit_start_beats_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            for p in (a, b):
                (p / ".adversal").mkdir(parents=True)
                (p / ".adversal" / "project.yaml").write_text("x: 1\n")
            with patch.dict(plugin.os.environ, {"ADVERSAL_PROJECT": str(a)}):
                self.assertEqual(plugin.find_project(b), b.resolve())


class StatusLineTests(unittest.TestCase):
    def test_status_line_counts_and_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".adversal" / "map").mkdir(parents=True)
            (project / ".adversal" / "ledgers").mkdir(parents=True)
            (project / ".adversal" / "map" / "map.json").write_text(json.dumps({
                "version": 1, "goal": {"id": "GOAL", "statement": "g"},
                "nodes": [
                    {"id": "L1", "statement": "a", "supports": ["GOAL"]},
                    {"id": "L2", "statement": "b", "supports": ["L1"]},
                ]}), encoding="utf-8")
            (project / ".adversal" / "ledgers" / "decisions.jsonl").write_text(
                json.dumps({"claim_id": "L2", "status": "proven"}) + "\n",
                encoding="utf-8")
            line = plugin.map_status_line(project)
        self.assertIn("2 nodes", line)
        self.assertIn("proven:1", line)
        self.assertIn("L1", line)  # ready: its only ingredient (L2) is proven

    def test_no_map_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(plugin.map_status_line(Path(tmp)))


if __name__ == "__main__":
    unittest.main()
