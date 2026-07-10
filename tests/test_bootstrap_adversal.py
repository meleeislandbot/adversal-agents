from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bootstrap_adversal.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_adversal", SCRIPT)
assert SPEC and SPEC.loader
bootstrap = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bootstrap
SPEC.loader.exec_module(bootstrap)


class BootstrapAdversalTests(unittest.TestCase):
    def setUp(self) -> None:
        identity = bootstrap.SourceIdentity(
            version="test",
            commit="a" * 40,
            origin=bootstrap.REPOSITORY_URL,
            clean=True,
        )
        patcher = patch.object(bootstrap, "source_identity", return_value=identity)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, args: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = bootstrap.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_inspect_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            profile = base / "profile"
            project = base / "project"
            profile.mkdir()
            (profile / "SOUL.md").write_text("default soul\n", encoding="utf-8")

            code, output, error = self.run_main([
                "inspect",
                "--project",
                str(project),
                "--profile-home",
                str(profile),
                "--json",
            ])

            self.assertEqual(code, 0, error)
            report = json.loads(output)
            self.assertFalse(report["writes_performed"])
            self.assertFalse(project.exists())
            self.assertEqual((profile / "SOUL.md").read_text(), "default soul\n")

    def test_apply_is_reversible_idempotent_and_resumable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            profile = base / "profile"
            project = base / "project"
            profile.mkdir()
            original_soul = "default soul\n"
            (profile / "SOUL.md").write_text(original_soul, encoding="utf-8")
            args = [
                "apply",
                "--project",
                str(project),
                "--profile-home",
                str(profile),
                "--approve-profile-write",
                "--approve-project-write",
                "--json",
            ]

            code, output, error = self.run_main(args)
            self.assertEqual(code, 0, error)
            state = json.loads(output)
            self.assertEqual(state["phase"], "restart_required")
            self.assertEqual((profile / "SOUL.pre-adversal.md").read_text(), original_soul)
            self.assertEqual(
                (profile / "SOUL.md").read_bytes(),
                (ROOT / "profiles/hermes-verification-coordinator/SOUL.md").read_bytes(),
            )
            self.assertTrue((profile / "skills/research/adversal-coordinator/SKILL.md").is_file())
            self.assertTrue((project / ".adversal/project.yaml").is_file())
            self.assertTrue((project / ".adversal/bootstrap/bootstrap_adversal.py").is_file())
            self.assertTrue((project / "docs/epistemics.md").is_file())
            self.assertTrue((project / "lakefile.toml").is_file())

            code, _, error = self.run_main(args)
            self.assertEqual(code, 0, error)
            self.assertEqual((profile / "SOUL.pre-adversal.md").read_text(), original_soul)

            with patch.dict(os.environ, {"HERMES_HOME": str(profile)}, clear=False):
                code, output, error = self.run_main([
                    "resume",
                    "--project",
                    str(project),
                    "--profile-home",
                    str(profile),
                    "--json",
                ])
            self.assertEqual(code, 0, error)
            resumed = json.loads(output)
            self.assertEqual(resumed["phase"], "dependencies_and_validation")
            self.assertIn("profile_restart_confirmed", resumed["completed"])

            (project / "lake-manifest.json").write_text("{}\n", encoding="utf-8")
            (project / ".lake/packages/mathlib").mkdir(parents=True)
            doctor = json.dumps({
                "gate_available": True,
                "workers": {
                    "codex-cli": {
                        "present": True,
                        "version": "test",
                        "hazard_env_present": [],
                    }
                },
            })
            successful_checks = [
                {"ok": True, "exit_code": 0, "output_tail": doctor, "_stdout": doctor},
                {"ok": True, "exit_code": 0, "output_tail": "cold iron holds", "_stdout": ""},
                {"ok": True, "exit_code": 0, "output_tail": "kernel ok", "_stdout": ""},
                {"ok": True, "exit_code": 0, "output_tail": "build ok", "_stdout": ""},
            ]
            with patch.object(bootstrap, "run_check", side_effect=successful_checks):
                readiness = bootstrap.verify_bootstrap(project, profile, record=True)
            self.assertTrue(readiness["bootstrap_complete"])
            self.assertTrue(readiness["gate_ready"])
            self.assertTrue(readiness["deterministic_core_ready"])
            self.assertFalse(readiness["workers_ready"])
            recorded = json.loads((project / bootstrap.STATE_REL).read_text(encoding="utf-8"))
            self.assertEqual(recorded["phase"], "provider_selection")

    def test_apply_requires_both_explicit_approvals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            profile = base / "profile"
            project = base / "project"
            profile.mkdir()

            code, _, error = self.run_main([
                "apply",
                "--project",
                str(project),
                "--profile-home",
                str(profile),
                "--approve-profile-write",
            ])

            self.assertEqual(code, 2)
            self.assertIn("requires both", error)
            self.assertFalse(project.exists())

    def test_conflict_fails_before_profile_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            profile = base / "profile"
            project = base / "project"
            profile.mkdir()
            project.mkdir()
            original_soul = "keep me\n"
            (profile / "SOUL.md").write_text(original_soul, encoding="utf-8")
            (project / "AGENTS.md").write_text("user-owned conflict\n", encoding="utf-8")

            code, _, error = self.run_main([
                "apply",
                "--project",
                str(project),
                "--profile-home",
                str(profile),
                "--approve-profile-write",
                "--approve-project-write",
            ])

            self.assertEqual(code, 2)
            self.assertIn("non-identical files", error)
            self.assertEqual((profile / "SOUL.md").read_text(), original_soul)
            self.assertFalse((profile / "SOUL.pre-adversal.md").exists())

    def test_source_checkout_cannot_be_runtime_project(self) -> None:
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.validate_project_location(ROOT / "runtime-project")

    def test_dirty_source_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            profile = base / "profile"
            project = base / "project"
            profile.mkdir()
            dirty = bootstrap.SourceIdentity(
                version="test",
                commit="b" * 40,
                origin=bootstrap.REPOSITORY_URL,
                clean=False,
            )
            with patch.object(bootstrap, "source_identity", return_value=dirty):
                code, _, error = self.run_main([
                    "apply",
                    "--project",
                    str(project),
                    "--profile-home",
                    str(profile),
                    "--approve-profile-write",
                    "--approve-project-write",
                ])
            self.assertEqual(code, 2)
            self.assertIn("modified or untracked", error)
            self.assertFalse(project.exists())


if __name__ == "__main__":
    unittest.main()
