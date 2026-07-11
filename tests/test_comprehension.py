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


bibliography = load("bibliography")
read_paper = load("read_paper")
dossier = load("dossier")
ideate = load("ideate")


def run_cli(module, argv: list[str]) -> tuple[int, str, str]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = module.main(argv)
        except SystemExit as exc:
            code = int(exc.code) if isinstance(exc.code, int) else 1
    return code, stdout.getvalue(), stderr.getvalue()


PAPER_BODY = (
    "# A theorem about primes\n\n"
    "Introduction with context. " * 30
    + "\nWe prove that the critical constant equals one half exactly.\n"
    + "Our method relies on the explicit formula and positivity.\n"
    + "Conclusion paragraph. " * 30
)


class SourceAndReadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        code, _, err = run_cli(bibliography, [
            "add", "--project", str(self.project),
            "--title", "A theorem about primes", "--authors", "A. Author",
            "--year", "1999", "--link", "https://example.org/primes",
            "--status", "partial-result", "--route", "explicit-formula"])
        self.assertEqual(code, 0, err)
        raw = self.project / "paper.md"
        raw.write_text(PAPER_BODY, encoding="utf-8")
        code, _, err = run_cli(bibliography, [
            "attach-source", "--project", str(self.project),
            "--link", "https://example.org/primes", "--file", str(raw)])
        self.assertEqual(code, 0, err)

    def entry(self) -> dict:
        return bibliography.find_entry(
            bibliography.load_entries(self.project), "https://example.org/primes")

    def test_attach_pins_source_and_flags_unread(self) -> None:
        entry = self.entry()
        self.assertTrue((self.project / entry["source_file"]).exists())
        self.assertTrue(entry["source_sha256"])
        digest = (self.project / "llm-wiki" / "prior-art" / "digest.md").read_text(encoding="utf-8")
        self.assertIn("UNREAD", digest)

    def _fake_reading(self, quote: str):
        def fake_call(prompt, cwd, timeout, allow_api=False):
            report = {"proves": [{"statement": "critical constant is 1/2",
                                  "quote": quote}],
                      "argues": [], "does_not_claim": ["it does not prove RH"],
                      "method_assumptions": ["explicit formula"],
                      "relevance_to_goal": ["baseline"],
                      "illegible_sections": [], "summary": "short"}
            return json.dumps(report), 0.0, "subscription-token", 0
        return fake_call

    def test_reading_with_verified_quote_records_deep_read(self) -> None:
        good = "the critical constant equals one half exactly"
        with patch.object(read_paper, "call_claude", self._fake_reading(good)):
            code, out, err = run_cli(read_paper, [
                "--project", str(self.project),
                "--link", "https://example.org/primes", "--level", "deep"])
        self.assertEqual(code, 0, err)
        entry = self.entry()
        self.assertEqual(entry["read_level"], "deep-read")
        reading = (self.project / entry["reading_file"]).read_text(encoding="utf-8")
        self.assertIn(good, reading)
        digest = (self.project / "llm-wiki" / "prior-art" / "digest.md").read_text(encoding="utf-8")
        self.assertIn("read in depth", digest)

    def test_hallucinated_quote_rejects_the_whole_reading(self) -> None:
        bad = "we completely settle the Riemann Hypothesis in section nine"
        with patch.object(read_paper, "call_claude", self._fake_reading(bad)):
            code, _, err = run_cli(read_paper, [
                "--project", str(self.project),
                "--link", "https://example.org/primes", "--level", "deep"])
        self.assertEqual(code, 3)
        self.assertIn("REJECTED", err)
        self.assertEqual(self.entry().get("read_level", "catalogued"), "catalogued")

    def test_source_change_makes_reading_stale(self) -> None:
        good = "the critical constant equals one half exactly"
        with patch.object(read_paper, "call_claude", self._fake_reading(good)):
            run_cli(read_paper, ["--project", str(self.project),
                                 "--link", "https://example.org/primes"])
        raw = self.project / "paper2.md"
        raw.write_text(PAPER_BODY + "\nA new appendix changes everything.\n",
                       encoding="utf-8")
        run_cli(bibliography, ["attach-source", "--project", str(self.project),
                               "--link", "https://example.org/primes",
                               "--file", str(raw)])
        entry = self.entry()
        self.assertTrue(bibliography.reading_is_stale(entry))
        self.assertNotIn(bibliography.normalize_link(entry["link"]),
                         bibliography.deep_read_links(self.project))


class DossierRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        # Two deep-read sources and one merely catalogued.
        for i, level in ((1, "deep-read"), (2, "deep-read"), (3, "catalogued")):
            run_cli(bibliography, [
                "add", "--project", str(self.project),
                "--title", f"Source {i}", "--year", "2000",
                "--link", f"https://example.org/s{i}",
                "--status", "survey", "--route", "context"])
        entries = bibliography.load_entries(self.project)
        for e in entries:
            if e["link"].endswith(("s1", "s2")):
                e["read_level"] = "deep-read"
        bibliography.save_entries(self.project, entries)

    def test_respondida_needs_two_deep_read_sources(self) -> None:
        run_cli(dossier, ["question", "--project", str(self.project),
                          "--text", "¿Por qué x=1/2?", "--section", "enunciado"])
        code, _, err = run_cli(dossier, [
            "classify", "--project", str(self.project), "--id", "Q1",
            "--status", "respondida", "--answer", "simetría funcional",
            "--sources", "https://example.org/s1"])
        self.assertEqual(code, 1)
        self.assertIn(">= 2", err)
        code, _, err = run_cli(dossier, [
            "classify", "--project", str(self.project), "--id", "Q1",
            "--status", "respondida", "--answer", "simetría funcional",
            "--sources", "https://example.org/s1,https://example.org/s3"])
        self.assertEqual(code, 1)
        self.assertIn("not deep-read", err)
        code, _, err = run_cli(dossier, [
            "classify", "--project", str(self.project), "--id", "Q1",
            "--status", "respondida", "--answer", "simetría funcional",
            "--sources", "https://example.org/s1,https://example.org/s2"])
        self.assertEqual(code, 0, err)

    def test_establecido_needs_deep_read_and_speculation_does_not(self) -> None:
        code, _, err = run_cli(dossier, [
            "fact", "--project", str(self.project),
            "--text", "El análogo en campos de funciones está probado.",
            "--tier", "establecido", "--sources", "https://example.org/s3,https://example.org/s1",
            "--section", "vecindario"])
        self.assertEqual(code, 1)
        self.assertIn("not deep-read", err)
        code, _, err = run_cli(dossier, [
            "fact", "--project", str(self.project),
            "--text", "El dominio es la nada iterada.",
            "--tier", "especulacion", "--section", "objeto"])
        self.assertEqual(code, 0, err)

    def test_render_flags_unworked_sections_and_digest_grounds(self) -> None:
        run_cli(dossier, ["note", "--project", str(self.project),
                          "--section", "obstrucciones",
                          "--note", "vacía tras 2 búsquedas; se reintenta en ronda 3"])
        run_cli(dossier, ["fact", "--project", str(self.project),
                          "--text", "Hecho de dominio establecido.",
                          "--tier", "establecido",
                          "--sources", "https://example.org/s1,https://example.org/s2",
                          "--section", "objeto"])
        run_cli(dossier, ["question", "--project", str(self.project),
                          "--text", "¿Cuál es el crux?", "--section", "cruxes"])
        code, _, _ = run_cli(dossier, ["render", "--project", str(self.project)])
        self.assertEqual(code, 0)
        text = (self.project / "llm-wiki" / "dossier" / "dossier.md").read_text(encoding="utf-8")
        self.assertIn("SECCIÓN SIN TRABAJAR", text)          # e.g. historia
        self.assertIn("vacía tras 2 búsquedas", text)        # declared emptiness
        digest = (self.project / "llm-wiki" / "dossier" / "digest.md").read_text(encoding="utf-8")
        self.assertIn("Hecho de dominio establecido.", digest)
        self.assertIn("¿Cuál es el crux?", digest)
        # ideate grounding merges prior-art + dossier digests
        merged = ideate.load_grounding(self.project, "", False)
        self.assertIn("Hecho de dominio establecido.", merged)
        self.assertIn("Prior-art digest", merged)

    def test_saturation_hint_after_two_dry_rounds(self) -> None:
        run_cli(dossier, ["round", "--project", str(self.project), "--new-items", "9"])
        run_cli(dossier, ["round", "--project", str(self.project), "--new-items", "1"])
        code, out, _ = run_cli(dossier, ["round", "--project", str(self.project),
                                         "--new-items", "0"])
        self.assertEqual(code, 0)
        self.assertIn("SATURATED", out.upper())
        code, out, _ = run_cli(dossier, ["status", "--project", str(self.project)])
        self.assertTrue(json.loads(out)["saturated_hint"])

    def test_stale_source_degrades_respondida_with_warning(self) -> None:
        run_cli(dossier, ["question", "--project", str(self.project),
                          "--text", "¿Q?", "--section", "objeto"])
        run_cli(dossier, ["classify", "--project", str(self.project), "--id", "Q1",
                          "--status", "respondida", "--answer", "a",
                          "--sources", "https://example.org/s1,https://example.org/s2"])
        entries = bibliography.load_entries(self.project)
        for e in entries:
            if e["link"].endswith("s1"):
                e["read_level"] = "catalogued"
        bibliography.save_entries(self.project, entries)
        code, out, _ = run_cli(dossier, ["status", "--project", str(self.project)])
        report = json.loads(out)
        self.assertTrue(any("Q1" in w for w in report["stale_warnings"]))


if __name__ == "__main__":
    unittest.main()
