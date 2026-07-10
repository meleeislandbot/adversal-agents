#!/usr/bin/env python3
"""Repository validation for Adversal Agents.

No network calls. No secrets printed.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "VERSION",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "instructions.md",
    "scripts/bootstrap_adversal.py",
    "tests/test_bootstrap_adversal.py",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "lean-toolchain",
    ".hermes.md",
    "profiles/hermes-verification-coordinator/SOUL.md",
    "profiles/hermes-verification-coordinator/skills/research/adversal-coordinator/SKILL.md",
    "docs/epistemics.md",
    "templates/project/scripts/verdict_engine.py",
    "templates/project/scripts/codex_worker.py",
    "templates/project/scripts/map_tool.py",
    "templates/project/scripts/decompose.py",
    "templates/project/scripts/backtranslate.py",
    "templates/project/scripts/reverify.py",
    "tests/test_map_tool.py",
    "integrations/hermes-adversal/plugin.yaml",
    "integrations/hermes-adversal/__init__.py",
    "integrations/hermes-adversal/README.md",
    "tests/test_hermes_plugin.py",
    "templates/project/MISIONES.md",
    "templates/project/COMO-FUNCIONA.md",
    "templates/project/roles/skeptic.md",
    "templates/project/.adversal/schema/claim.schema.json",
    "templates/project/.adversal/schema/claims.schema.json",
    "templates/project/llm-wiki/index.md",
    "templates/project/.adversal/project.yaml",
    "templates/project/scripts/adversal_doctor.py",
    "templates/project/scripts/create_run_skeleton.py",
    "templates/project/.hermes.md",
    "templates/project/AGENTS.md",
    "templates/project/CLAUDE.md",
    "templates/project/GEMINI.md",
    "templates/project/lean-toolchain",
    "templates/project/lakefile.toml",
    "templates/project/lake-manifest.json",
]

PROMPT_START = "<!-- adversal-setup-prompt:start -->"
PROMPT_END = "<!-- adversal-setup-prompt:end -->"
SECRET_PATTERN = re.compile(
    r'''(?i)(api[_-]?key|secret|token|password|passwd)\s*=\s*['"]([^'"]{8,})['"]'''
)
EXAMPLE_SECRET_VALUES = ("redacted", "your-", "example", "placeholder", "changeme", "<", "...", "xxxx")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def git_files(*pathspecs: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", *pathspecs],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line for line in proc.stdout.splitlines() if line]


def check_required_files() -> None:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_setup_prompt() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if readme.count(PROMPT_START) != 1 or readme.count(PROMPT_END) != 1:
        fail("README.md must contain exactly one marked setup prompt")
    if readme.index(PROMPT_START) > readme.index(PROMPT_END):
        fail("README.md setup prompt markers are reversed")
    prompt_files = sorted(p.name for p in (ROOT / "prompts").glob("*.md")) if (ROOT / "prompts").exists() else []
    if prompt_files:
        fail(f"setup prompt must not be hidden in prompts/*.md; found {prompt_files}")


def check_self_bootstrap_contract() -> None:
    instructions = (ROOT / "instructions.md").read_text(encoding="utf-8")
    required = (
        "bootstrap_adversal.py inspect",
        "bootstrap_adversal.py apply",
        "bootstrap_adversal.py resume",
        "bootstrap_adversal.py verify",
        "--approve-profile-write",
        "restart_required",
        "An independent citation validator is not implemented yet",
    )
    missing = [term for term in required if term not in instructions]
    if missing:
        fail(f"instructions.md is missing self-bootstrap contract terms: {missing}")


def check_context_files_do_not_trigger_onboarding() -> None:
    forbidden = ("instructions.md", "one-shot onboarding", "guided setup")
    for rel in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".hermes.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        hits = [term for term in forbidden if term in text]
        if hits:
            fail(f"{rel} must stay day-to-day only; found onboarding terms: {hits}")


def check_python_syntax() -> None:
    for rel in sorted(git_files("*.py")):
        path = ROOT / rel
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def check_template_doctor_runs() -> None:
    subprocess.run(
        [sys.executable, "templates/project/scripts/adversal_doctor.py", "--json"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        timeout=15,
    )


def check_verdict_engine_selftest() -> None:
    """The cold-iron guarantee is part of CI: praise never earns a status."""
    subprocess.run(
        [sys.executable, "templates/project/scripts/verdict_engine.py", "--selftest"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        timeout=30,
    )


def check_verdict_engine_lean_selftest_if_available() -> None:
    """Exercise the kernel boundary when Lean is installed, including via elan."""
    lean = shutil.which("lean")
    if lean is None:
        fallback = Path.home() / ".elan" / "bin" / "lean"
        lean = str(fallback) if fallback.exists() else None
    if lean is None:
        return
    env = dict(os.environ)
    env["PATH"] = f"{Path(lean).parent}:{env.get('PATH', '')}"
    subprocess.run(
        [sys.executable, "templates/project/scripts/verdict_engine.py", "--selftest-lean"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        timeout=120,
        env=env,
    )


def check_json_schemas_parse() -> None:
    for rel in (
        "templates/project/.adversal/schema/claim.schema.json",
        "templates/project/.adversal/schema/claims.schema.json",
    ):
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("$schema") is None:
            fail(f"{rel} did not parse as a JSON schema")
    manifest = json.loads((ROOT / "templates/project/lake-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") is None or not isinstance(manifest.get("packages"), list):
        fail("templates/project/lake-manifest.json did not parse as a Lake manifest")


def check_yaml_if_available() -> None:
    try:
        import yaml  # type: ignore
    except Exception:
        return
    with (ROOT / "templates/project/.adversal/project.yaml").open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or data.get("schema_version") is None:
        fail("templates/project/.adversal/project.yaml did not parse as expected")


def check_runtime_state_not_tracked_at_repo_root() -> None:
    # A project's live control plane and knowledge base are local state. Only the
    # empty templates under templates/project/ belong in the source repo.
    for path in (".adversal", "llm-wiki"):
        tracked = git_files(path)
        if tracked:
            fail(f"repo-root runtime state '{path}/' is tracked; use templates/project/ instead: {tracked[:5]}")


def check_no_generated_template_runs_tracked() -> None:
    tracked = [
        line
        for line in git_files("templates/project/.adversal/runs")
        if line and not line.endswith(".gitkeep")
    ]
    if tracked:
        fail(f"generated template run artifacts are tracked: {tracked}")


def check_no_obvious_secrets() -> None:
    offenders: list[str] = []
    for rel in git_files():
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size > 500_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in SECRET_PATTERN.finditer(text):
            value = match.group(2).strip().lower()
            if any(marker in value for marker in EXAMPLE_SECRET_VALUES):
                continue
            offenders.append(rel)
            break
    if offenders:
        fail(f"possible hardcoded secrets in tracked files: {offenders}")


def main() -> int:
    check_required_files()
    check_setup_prompt()
    check_self_bootstrap_contract()
    check_context_files_do_not_trigger_onboarding()
    check_python_syntax()
    check_template_doctor_runs()
    check_verdict_engine_selftest()
    check_verdict_engine_lean_selftest_if_available()
    check_json_schemas_parse()
    check_yaml_if_available()
    check_runtime_state_not_tracked_at_repo_root()
    check_no_generated_template_runs_tracked()
    check_no_obvious_secrets()
    print("validate_repo_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
