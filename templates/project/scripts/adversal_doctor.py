#!/usr/bin/env python3
"""Read-only local diagnostics for Adversal Agents setup.

This script does not install packages, modify files, print secret values, or call LLM APIs.
It checks command availability, versions, and risk-relevant environment variable presence.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKERS = {
    "claude-code": {
        "command": "claude",
        "version_args": ["--version"],
        "hazards": ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"],
    },
    "codex-cli": {
        "command": "codex",
        "version_args": ["--version"],
        "hazards": ["OPENAI_API_KEY", "CODEX_API_KEY"],
    },
    "gemini-cli": {
        "command": "gemini",
        "version_args": ["--version"],
        "hazards": ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"],
    },
    "grok": {
        "command": "grok",
        "version_args": ["--version"],
        "hazards": ["XAI_API_KEY", "GROK_API_KEY"],
    },
    "opencode": {
        "command": "opencode",
        "version_args": ["--version"],
        "hazards": [],
    },
    "ollama": {
        "command": "ollama",
        "version_args": ["--version"],
        "hazards": [],
    },
    "deterministic": {
        "command": "python3",
        "version_args": ["--version"],
        "hazards": [],
    },
}

PACKAGE_MANAGERS = ["brew", "npm", "pnpm", "yarn", "uv", "pipx", "python3", "git", "gh"]

# The formal-verification gate. Without one of these there is no way to grant
# 'proven', so the doctor reports it prominently.
VERIFIERS = ["lake", "lean"]


def run_version(command: str, args: list[str]) -> dict:
    path = shutil.which(command)
    if not path:
        return {"present": False, "path": None, "version": None, "error": None}
    try:
        proc = subprocess.run(
            [path, *args],
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        text = (proc.stdout or proc.stderr or "").strip().splitlines()
        return {
            "present": True,
            "path": path,
            "version": text[0] if text else None,
            "exit_code": proc.returncode,
            "error": None if proc.returncode == 0 else (proc.stderr or proc.stdout).strip()[:500],
        }
    except Exception as exc:  # noqa: BLE001 - diagnostic tool should not crash on one command
        return {"present": True, "path": path, "version": None, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Adversal Agents environment diagnostics")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    root = Path.cwd()
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cwd": str(root),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "project_markers": {
            "instructions.md": (root / "instructions.md").exists(),
            "AGENTS.md": (root / "AGENTS.md").exists(),
            ".adversal/project.yaml": (root / ".adversal" / "project.yaml").exists(),
            "llm-wiki/index.md": (root / "llm-wiki" / "index.md").exists(),
            ".git": (root / ".git").exists(),
        },
        "package_managers": {},
        "workers": {},
    }

    for cmd in PACKAGE_MANAGERS:
        report["package_managers"][cmd] = shutil.which(cmd)

    report["verifiers"] = {cmd: shutil.which(cmd) for cmd in VERIFIERS}
    report["gate_available"] = any(report["verifiers"].values())

    for name, spec in WORKERS.items():
        check = run_version(spec["command"], spec["version_args"])
        hazards_present = [var for var in spec["hazards"] if os.getenv(var)]
        report["workers"][name] = {
            **check,
            "command": spec["command"],
            "hazard_env_present": hazards_present,  # names only, never values
            "cost_warning": bool(hazards_present),
        }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Adversal Agents read-only diagnostics")
        print(f"cwd: {report['cwd']}")
        print(f"platform: {report['platform']['system']} {report['platform']['release']} {report['platform']['machine']}")
        print("\nProject markers:")
        for key, value in report["project_markers"].items():
            print(f"  {'OK' if value else '--'} {key}")
        print("\nFormal-verification gate (required for 'proven'):")
        for cmd, path in report["verifiers"].items():
            print(f"  {'OK' if path else '--'} {cmd}")
        if not report["gate_available"]:
            print("  !! no Lean toolchain found: nothing can be marked 'proven' until one is installed")
        print("\nWorkers:")
        for name, data in report["workers"].items():
            status = "OK" if data["present"] else "missing"
            version = data.get("version") or ""
            hazards = ", ".join(data["hazard_env_present"]) or "none"
            print(f"  {name:15} {status:8} {version} | env hazards: {hazards}")
        print("\nNo files were modified. No secret values were printed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
