#!/usr/bin/env python3
"""Repository validation for Adversal Agents.

No network calls. No secrets printed.
"""
from __future__ import annotations

import ast
import re
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
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".hermes.md",
    "profiles/hermes-redteam-coordinator/SOUL.md",
    ".adversal/project.yaml",
    "scripts/adversal_doctor.py",
    "scripts/create_run_skeleton.py",
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


def check_context_files_do_not_trigger_onboarding() -> None:
    forbidden = ("instructions.md", "one-shot onboarding", "guided setup")
    for rel in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".hermes.md"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        hits = [term for term in forbidden if term in text]
        if hits:
            fail(f"{rel} must stay day-to-day only; found onboarding terms: {hits}")


def check_python_syntax() -> None:
    for path in sorted((ROOT / "scripts").glob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def check_doctor_runs() -> None:
    subprocess.run(
        [sys.executable, "scripts/adversal_doctor.py", "--json"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        timeout=15,
    )


def check_yaml_if_available() -> None:
    try:
        import yaml  # type: ignore
    except Exception:
        return
    with (ROOT / ".adversal/project.yaml").open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or data.get("schema_version") is None:
        fail(".adversal/project.yaml did not parse as expected")


def check_no_generated_runs_tracked() -> None:
    proc = subprocess.run(
        ["git", "ls-files", ".adversal/runs"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    tracked = [line for line in proc.stdout.splitlines() if line and not line.endswith(".gitkeep")]
    if tracked:
        fail(f"generated run artifacts are tracked: {tracked}")


def check_no_obvious_secrets() -> None:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    offenders: list[str] = []
    for rel in proc.stdout.splitlines():
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
    check_context_files_do_not_trigger_onboarding()
    check_python_syntax()
    check_doctor_runs()
    check_yaml_if_available()
    check_no_generated_runs_tracked()
    check_no_obvious_secrets()
    print("validate_repo_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
