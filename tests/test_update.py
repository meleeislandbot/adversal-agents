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
SCRIPT = ROOT / "scripts" / "bootstrap_adversal.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_update_under_test", SCRIPT)
assert SPEC and SPEC.loader
bootstrap = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bootstrap
SPEC.loader.exec_module(bootstrap)


def identity(commit: str) -> "bootstrap.SourceIdentity":
    return bootstrap.SourceIdentity(
        version="test", commit=commit, origin=bootstrap.REPOSITORY_URL, clean=True)


def run_main(args: list[str]) -> tuple[int, str, str]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = bootstrap.main(args)
    return code, stdout.getvalue(), stderr.getvalue()


class UpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.project = base / "project"
        self.profile = base / "profile"
        self.profile.mkdir()
        with patch.object(bootstrap, "source_identity",
                          return_value=identity("a" * 40)):
            code, out, err = run_main([
                "apply", "--project", str(self.project),
                "--profile-home", str(self.profile),
                "--approve-profile-write", "--approve-project-write", "--json"])
        self.assertEqual(code, 0, err)
        # Live research state that an update must never touch.
        ledger = self.project / ".adversal" / "ledgers" / "decisions.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text('{"claim_id": "L1", "status": "proven"}\n', encoding="utf-8")
        wiki = self.project / "llm-wiki" / "verified" / "L1.md"
        wiki.parent.mkdir(parents=True, exist_ok=True)
        wiki.write_text("verified knowledge\n", encoding="utf-8")
        self.ledger, self.wiki = ledger, wiki

    def update(self, commit: str, approve: bool = True) -> tuple[int, dict]:
        args = ["update", "--project", str(self.project),
                "--profile-home", str(self.profile), "--json"]
        if approve:
            args += ["--approve-profile-write", "--approve-project-write"]
        with patch.object(bootstrap, "source_identity",
                          return_value=identity(commit)):
            code, out, err = run_main(args)
        payload = json.loads(out) if out.strip().startswith("{") else {}
        return code, payload

    def test_update_requires_bootstrapped_project(self) -> None:
        with tempfile.TemporaryDirectory() as other:
            args = ["update", "--project", str(Path(other) / "empty"),
                    "--profile-home", str(self.profile)]
            with patch.object(bootstrap, "source_identity",
                              return_value=identity("b" * 40)):
                code, _, err = run_main(args)
        self.assertEqual(code, 2)
        self.assertIn("bootstrap", err)

    def test_plan_only_without_approval_writes_nothing(self) -> None:
        state_before = (self.project / bootstrap.STATE_REL).read_bytes()
        code, report = self.update("b" * 40, approve=False)
        self.assertEqual(code, 0)
        self.assertFalse(report["writes_performed"])
        self.assertEqual((self.project / bootstrap.STATE_REL).read_bytes(),
                         state_before)

    def test_update_applies_changed_vendored_file_and_records_state(self) -> None:
        # Simulate a newer source shipping a changed script.
        target_rel = Path("scripts") / "map_tool.py"
        installed = self.project / target_rel
        original = installed.read_text(encoding="utf-8")
        installed.write_text(original.replace("The map", "The old map", 1),
                             encoding="utf-8")  # drift from an older vendored copy
        code, report = self.update("b" * 40)
        self.assertEqual(code, 0, report)
        self.assertTrue(report["writes_performed"])
        self.assertIn(str(target_rel), report["project"]["update"])
        self.assertEqual(installed.read_text(encoding="utf-8"), original)
        state = json.loads((self.project / bootstrap.STATE_REL).read_text(encoding="utf-8"))
        self.assertEqual(state["source"]["commit"], "b" * 40)
        self.assertIn(str(target_rel), state["vendored_sha256"])
        self.assertTrue(report["backup"])
        backup_root = Path(report["backup"])
        self.assertTrue((backup_root / "project" / target_rel).exists())

    def test_live_state_is_never_touched(self) -> None:
        code, report = self.update("b" * 40)
        self.assertEqual(code, 0)
        self.assertTrue(report["live_state_untouched"])
        self.assertEqual(self.ledger.read_text(encoding="utf-8"),
                         '{"claim_id": "L1", "status": "proven"}\n')
        self.assertEqual(self.wiki.read_text(encoding="utf-8"),
                         "verified knowledge\n")
        all_buckets = (report["project"]["add"] + report["project"]["update"]
                       + report["project"]["conflict"])
        self.assertFalse([p for p in all_buckets
                          if p.startswith(".adversal/ledgers")
                          or p.startswith(".adversal/runs")
                          or (p.startswith("llm-wiki") and not p.endswith("README.md"))])

    def test_local_edits_conflict_after_hashes_recorded(self) -> None:
        code, _ = self.update("b" * 40)  # records vendored hashes
        self.assertEqual(code, 0)
        target = self.project / "scripts" / "map_tool.py"
        target.write_text(target.read_text(encoding="utf-8")
                          + "\n# local customization\n", encoding="utf-8")
        code, report = self.update("c" * 40)
        self.assertEqual(code, 0)
        self.assertIn("scripts/map_tool.py", report["project"]["conflict"])
        self.assertIn("# local customization",
                      target.read_text(encoding="utf-8"))

    def test_plugin_ships_to_profile_and_flags_restart(self) -> None:
        code, report = self.update("b" * 40)
        self.assertEqual(code, 0)
        plugin_init = self.profile / "plugins" / "hermes-adversal" / "__init__.py"
        self.assertTrue(plugin_init.exists())
        self.assertTrue(report["plugin_restart_required"])
        # Second run with everything in place: no plugin restart needed.
        code, report = self.update("b" * 40)
        self.assertEqual(code, 0)
        self.assertFalse(report["plugin_restart_required"])


if __name__ == "__main__":
    unittest.main()
