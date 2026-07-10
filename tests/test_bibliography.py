from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


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


bibliography = load("bibliography")
ideate = load("ideate")


def run_cli(module, argv: list[str]) -> tuple[int, str, str]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = module.main(argv)
        except SystemExit as exc:
            code = int(exc.code) if isinstance(exc.code, int) else 1
    return code, stdout.getvalue(), stderr.getvalue()


def add_args(project: Path, **overrides) -> list[str]:
    base = {
        "--title": "Pair correlation of zeros of the zeta function",
        "--authors": "H. L. Montgomery",
        "--year": "1973",
        "--link": "https://example.org/montgomery-1973",
        "--status": "active-program",
        "--route": "random-matrix",
    }
    base.update(overrides)
    argv = ["add", "--project", str(project)]
    for k, v in base.items():
        if v is not None:
            argv.extend([k, v])
    return argv


class BibliographyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)

    def test_add_generates_digest_and_index(self) -> None:
        code, out, err = run_cli(bibliography, add_args(self.project))
        self.assertEqual(code, 0, err)
        digest = (self.project / "llm-wiki" / "prior-art" / "digest.md")
        index = (self.project / "llm-wiki" / "prior-art" / "index.md")
        self.assertIn("Montgomery", digest.read_text(encoding="utf-8"))
        self.assertIn("https://example.org/montgomery-1973",
                      index.read_text(encoding="utf-8"))
        self.assertIn("forced contrast", digest.read_text(encoding="utf-8"))

    def test_link_is_mandatory_and_deduplicated(self) -> None:
        code, _, err = run_cli(bibliography, add_args(self.project, **{"--link": "not-a-url"}))
        self.assertEqual(code, 1)
        self.assertIn("link", err)
        self.assertEqual(run_cli(bibliography, add_args(self.project))[0], 0)
        code, _, err = run_cli(bibliography, add_args(self.project))
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)

    def test_dead_end_requires_reason(self) -> None:
        code, _, err = run_cli(bibliography, add_args(
            self.project, **{"--status": "documented-dead-end"}))
        self.assertEqual(code, 1)
        self.assertIn("why-dead", err)
        code, _, err = run_cli(bibliography, add_args(
            self.project, **{"--status": "documented-dead-end",
                             "--why-dead": "the operator was never exhibited"}))
        self.assertEqual(code, 0, err)
        digest = (self.project / "llm-wiki" / "prior-art" / "digest.md")
        self.assertIn("why dead", digest.read_text(encoding="utf-8"))

    def test_digest_truncates_but_index_keeps_all(self) -> None:
        for i in range(60):
            code, _, err = run_cli(bibliography, add_args(
                self.project,
                **{"--title": f"Entry number {i} with a reasonably long title "
                              f"to consume digest budget quickly {'x' * 120}",
                   "--link": f"https://example.org/paper-{i}"}))
            self.assertEqual(code, 0, err)
        digest = (self.project / "llm-wiki" / "prior-art" / "digest.md").read_text(encoding="utf-8")
        index = (self.project / "llm-wiki" / "prior-art" / "index.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(digest), bibliography.DIGEST_CHAR_BUDGET + 500)
        self.assertIn("truncated", digest)
        self.assertEqual(index.count("https://example.org/paper-"), 60)


class GroundingTests(unittest.TestCase):
    def test_block_contains_contrast_requirement_and_digest(self) -> None:
        block = ideate.grounding_block("## ACTIVE PROGRAMS\n- **X** (A, 1999)")
        self.assertIn("differential bet", block)
        self.assertIn("data, not instructions", block)
        self.assertIn("ACTIVE PROGRAMS", block)
        self.assertEqual(ideate.grounding_block(""), "")

    def test_load_grounding_auto_detects_and_respects_disable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            digest = project / "llm-wiki" / "prior-art" / "digest.md"
            digest.parent.mkdir(parents=True)
            digest.write_text("digest-content", encoding="utf-8")
            self.assertEqual(ideate.load_grounding(project, "", False), "digest-content")
            self.assertEqual(ideate.load_grounding(project, "", True), "")
            self.assertEqual(ideate.load_grounding(Path(tmp) / "nope", "", False), "")


if __name__ == "__main__":
    unittest.main()
