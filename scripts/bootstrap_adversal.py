#!/usr/bin/env python3
"""Deterministic, resumable bootstrap for a fresh Hermes profile.

This helper performs only local file operations. It never installs packages,
changes Hermes toolsets, reads credential files, or calls a model/provider.
Those actions remain guided steps in instructions.md and require the approvals
defined by docs/setup-contract.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_TEMPLATE = SOURCE_ROOT / "templates" / "project"
PROFILE_TEMPLATE = SOURCE_ROOT / "profiles" / "hermes-verification-coordinator"
PROFILE_SOUL = PROFILE_TEMPLATE / "SOUL.md"
PROFILE_SKILL = PROFILE_TEMPLATE / "skills" / "research" / "adversal-coordinator"
REPOSITORY_URL = "https://github.com/meleeislandbot/adversal-agents.git"
STATE_REL = Path(".adversal/bootstrap/state.json")
INSTRUCTIONS_REL = Path(".adversal/bootstrap/instructions.md")
HELPER_REL = Path(".adversal/bootstrap/bootstrap_adversal.py")

PROJECT_DOCS = {
    Path("docs/epistemics.md"): SOURCE_ROOT / "docs" / "epistemics.md",
    Path("docs/coordinator-runbook.md"): SOURCE_ROOT / "docs" / "coordinator-runbook.md",
    Path("docs/cost-safety.md"): SOURCE_ROOT / "docs" / "cost-safety.md",
    Path("docs/setup-contract.md"): SOURCE_ROOT / "docs" / "setup-contract.md",
}


class BootstrapError(RuntimeError):
    """A fail-closed bootstrap error safe to show to the user."""


@dataclass(frozen=True)
class SourceIdentity:
    version: str
    commit: str
    origin: str
    clean: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def same_file(left: Path, right: Path) -> bool:
    return left.exists() and left.is_file() and left.read_bytes() == right.read_bytes()


def atomic_write(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def copy_file(source: Path, destination: Path) -> None:
    atomic_write(destination, source.read_bytes(), source.stat().st_mode & 0o777)


def git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=SOURCE_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    commit = proc.stdout.strip()
    valid = len(commit) == 40 and all(character in "0123456789abcdef" for character in commit.lower())
    return commit if proc.returncode == 0 and valid else "unknown"


def git_origin() -> str:
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=SOURCE_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def git_clean() -> bool:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=SOURCE_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0 and not proc.stdout.strip()


def official_origin(origin: str) -> bool:
    normalized = origin.removesuffix(".git").rstrip("/").lower()
    return normalized in {
        "https://github.com/meleeislandbot/adversal-agents",
        "git@github.com:meleeislandbot/adversal-agents",
        "ssh://git@github.com/meleeislandbot/adversal-agents",
    }


def source_identity() -> SourceIdentity:
    version = (SOURCE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return SourceIdentity(
        version=version,
        commit=git_commit(),
        origin=git_origin(),
        clean=git_clean(),
    )


def resolve_profile_home(raw: str | None) -> tuple[Path | None, str]:
    if raw:
        return Path(raw).expanduser().resolve(), "argument"
    env_home = os.environ.get("HERMES_HOME")
    if env_home:
        return Path(env_home).expanduser().resolve(), "HERMES_HOME"
    return None, "unavailable"


def validate_source() -> None:
    required = [
        PROJECT_TEMPLATE,
        PROFILE_SOUL,
        PROFILE_SKILL / "SKILL.md",
        SOURCE_ROOT / "instructions.md",
        SOURCE_ROOT / "VERSION",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise BootstrapError(f"source checkout is incomplete: {missing}")


def validate_project_location(project: Path) -> None:
    project = project.resolve()
    source = SOURCE_ROOT.resolve()
    if project == source or source in project.parents:
        raise BootstrapError(
            "the instantiated project must be outside the Adversal source checkout"
        )
    if project.exists() and not project.is_dir():
        raise BootstrapError(f"project path exists but is not a directory: {project}")


def iter_files(root: Path) -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for source in sorted(root.rglob("*")):
        if source.is_symlink():
            raise BootstrapError(f"symlinks are not allowed in bootstrap assets: {source}")
        if source.is_file():
            files.append((source.relative_to(root), source))
    return files


def project_files() -> dict[Path, Path]:
    files = {relative: source for relative, source in iter_files(PROJECT_TEMPLATE)}
    for relative, source in PROJECT_DOCS.items():
        if relative in files:
            raise BootstrapError(f"duplicate project bootstrap destination: {relative}")
        files[relative] = source
    files[INSTRUCTIONS_REL] = SOURCE_ROOT / "instructions.md"
    files[HELPER_REL] = Path(__file__).resolve()
    return files


def skill_files() -> dict[Path, Path]:
    return {relative: source for relative, source in iter_files(PROFILE_SKILL)}


def existing_state(project: Path) -> dict | None:
    path = project / STATE_REL
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"bootstrap state is unreadable: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BootstrapError(f"bootstrap state is not a JSON object: {path}")
    return data


def preflight_apply(project: Path, profile_home: Path) -> dict:
    validate_source()
    validate_project_location(project)
    if not profile_home.exists() or not profile_home.is_dir():
        raise BootstrapError(f"Hermes profile home does not exist: {profile_home}")

    identity = source_identity()
    if identity.commit == "unknown":
        raise BootstrapError(
            "the source must be a Git checkout so the installed commit can be recorded"
        )
    if not official_origin(identity.origin):
        raise BootstrapError(
            f"source origin is not the official Adversal repository: {identity.origin}"
        )
    if not identity.clean:
        raise BootstrapError(
            "source checkout has modified or untracked files; bootstrap requires a clean commit"
        )

    state = existing_state(project)
    if state:
        previous = state.get("source", {}).get("commit")
        if previous and previous != identity.commit:
            raise BootstrapError(
                "this project was bootstrapped from a different commit; upgrades require "
                "an explicit migration, not a bootstrap rerun"
            )

    project_conflicts: list[str] = []
    for relative, source in project_files().items():
        destination = project / relative
        if destination.exists() and not same_file(destination, source):
            project_conflicts.append(str(destination))

    skill_root = profile_home / "skills" / "research" / "adversal-coordinator"
    skill_conflicts: list[str] = []
    for relative, source in skill_files().items():
        destination = skill_root / relative
        if destination.exists() and not same_file(destination, source):
            skill_conflicts.append(str(destination))

    soul_destination = profile_home / "SOUL.md"
    soul_backup = profile_home / "SOUL.pre-adversal.md"
    needs_soul_backup = soul_destination.exists() and not same_file(soul_destination, PROFILE_SOUL)
    if needs_soul_backup and soul_backup.exists():
        raise BootstrapError(
            f"refusing to replace SOUL.md because its backup already exists: {soul_backup}"
        )

    conflicts = project_conflicts + skill_conflicts
    if conflicts:
        raise BootstrapError(
            "bootstrap would overwrite non-identical files; resolve these first: "
            + ", ".join(conflicts)
        )

    return {
        "source": {
            "version": identity.version,
            "commit": identity.commit,
            "origin": identity.origin,
            "clean": identity.clean,
        },
        "project_root": str(project),
        "profile_home": str(profile_home),
        "project_files": len(project_files()),
        "skill_files": len(skill_files()),
        "soul_backup_required": needs_soul_backup,
        "soul_backup": str(soul_backup) if needs_soul_backup else None,
    }


def apply_bootstrap(project: Path, profile_home: Path) -> dict:
    plan = preflight_apply(project, profile_home)
    project.mkdir(parents=True, exist_ok=True)

    soul_destination = profile_home / "SOUL.md"
    soul_backup = profile_home / "SOUL.pre-adversal.md"
    if plan["soul_backup_required"]:
        copy_file(soul_destination, soul_backup)
    if not same_file(soul_destination, PROFILE_SOUL):
        copy_file(PROFILE_SOUL, soul_destination)

    skill_root = profile_home / "skills" / "research" / "adversal-coordinator"
    for relative, source in skill_files().items():
        destination = skill_root / relative
        if not same_file(destination, source):
            copy_file(source, destination)

    for relative, source in project_files().items():
        destination = project / relative
        if not same_file(destination, source):
            copy_file(source, destination)

    identity = source_identity()
    state = {
        "schema_version": 1,
        "updated_at": utc_now(),
        "phase": "restart_required",
        "completed": ["source_acquired", "profile_configured", "project_initialized"],
        "next_action": "start_a_new_session_in_the_same_profile",
        "continuation_prompt": (
            f"Continúa el bootstrap de Adversal en {project}. "
            "Usa la skill adversal-coordinator y lee .adversal/bootstrap/state.json."
        ),
        "source": {
            "repository": REPOSITORY_URL,
            "version": identity.version,
            "commit": identity.commit,
            "origin": identity.origin,
        },
        "profile": {
            "home": str(profile_home),
            "soul_sha256": sha256_file(PROFILE_SOUL),
            "skill_sha256": sha256_file(PROFILE_SKILL / "SKILL.md"),
            "bootstrap_helper_sha256": sha256_file(Path(__file__).resolve()),
            "previous_soul_backup": plan["soul_backup"],
        },
        "project_root": str(project),
    }
    atomic_write(
        project / STATE_REL,
        (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        0o644,
    )
    return state


def resume_bootstrap(project: Path, profile_home: Path) -> dict:
    state = existing_state(project)
    if not state:
        raise BootstrapError(f"no bootstrap state found under {project / STATE_REL}")
    if Path(state.get("project_root", "")).resolve() != project.resolve():
        raise BootstrapError("bootstrap state project_root does not match this project")
    recorded_home = Path(state.get("profile", {}).get("home", "")).resolve()
    if recorded_home != profile_home.resolve():
        raise BootstrapError("this is not the Hermes profile that started the bootstrap")

    active_home = os.environ.get("HERMES_HOME")
    if active_home and Path(active_home).expanduser().resolve() != profile_home.resolve():
        raise BootstrapError("HERMES_HOME identifies a different active profile")

    expected_soul = state.get("profile", {}).get("soul_sha256")
    expected_skill = state.get("profile", {}).get("skill_sha256")
    if not (profile_home / "SOUL.md").exists() or sha256_file(profile_home / "SOUL.md") != expected_soul:
        raise BootstrapError("the active profile did not load the installed Adversal SOUL.md")
    skill = profile_home / "skills" / "research" / "adversal-coordinator" / "SKILL.md"
    if not skill.exists() or sha256_file(skill) != expected_skill:
        raise BootstrapError("the active profile is missing the installed coordinator skill")
    helper = project / HELPER_REL
    expected_helper = state.get("profile", {}).get("bootstrap_helper_sha256")
    if not helper.exists() or sha256_file(helper) != expected_helper:
        raise BootstrapError("the project bootstrap helper differs from the recorded source")

    state["updated_at"] = utc_now()
    state["phase"] = "dependencies_and_validation"
    state["completed"] = sorted(set(state.get("completed", [])) | {"profile_restart_confirmed"})
    state["next_action"] = "follow_the_dependency_and_validation_phases_in_instructions"
    atomic_write(
        project / STATE_REL,
        (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        0o644,
    )
    return state


def run_check(command: list[str], cwd: Path, timeout: int) -> dict:
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exit_code": None, "error": str(exc)}
    output = (proc.stdout + proc.stderr).strip()
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "output_tail": output[-1200:],
        "_stdout": proc.stdout,
    }


def verify_bootstrap(project: Path, profile_home: Path, record: bool) -> dict:
    state = existing_state(project)
    if not state:
        raise BootstrapError(f"no bootstrap state found under {project / STATE_REL}")
    recorded_home = Path(state.get("profile", {}).get("home", "")).resolve()
    if recorded_home != profile_home.resolve():
        raise BootstrapError("this is not the Hermes profile recorded by the bootstrap")
    active_home = os.environ.get("HERMES_HOME")
    if active_home and Path(active_home).expanduser().resolve() != profile_home.resolve():
        raise BootstrapError("HERMES_HOME identifies a different active profile")
    required_markers = [
        ".adversal/project.yaml",
        "AGENTS.md",
        ".hermes.md",
        "docs/epistemics.md",
        "llm-wiki/index.md",
        "lean-toolchain",
        "lakefile.toml",
        "scripts/adversal_doctor.py",
        "scripts/verdict_engine.py",
        "scripts/run_mission.py",
    ]
    marker_status = {relative: (project / relative).is_file() for relative in required_markers}

    doctor_check = run_check(
        [sys.executable, "scripts/adversal_doctor.py", "--json"], project, 30
    )
    doctor: dict = {}
    if doctor_check["ok"]:
        try:
            doctor = json.loads(doctor_check.get("_stdout", ""))
        except json.JSONDecodeError:
            doctor_check["ok"] = False
            doctor_check["error"] = "doctor did not return JSON"
    doctor_check.pop("_stdout", None)

    verdict_check = run_check(
        [sys.executable, "scripts/verdict_engine.py", "--selftest"], project, 60
    )
    gate_available = bool(doctor.get("gate_available"))
    lean_check = (
        run_check([sys.executable, "scripts/verdict_engine.py", "--selftest-lean"], project, 120)
        if gate_available
        else {"ok": False, "exit_code": None, "error": "Lean gate unavailable"}
    )

    manifest = project / "lake-manifest.json"
    mathlib_checkout = project / ".lake" / "packages" / "mathlib"
    mathlib_check = (
        run_check(["lake", "build"], project, 600)
        if gate_available and manifest.is_file() and mathlib_checkout.is_dir()
        else {
            "ok": False,
            "exit_code": None,
            "error": (
                "mathlib checkout missing; run approved `lake update` before verification"
                if manifest.is_file()
                else "lake-manifest.json missing from the instantiated project"
            ),
        }
    )
    verdict_check.pop("_stdout", None)
    lean_check.pop("_stdout", None)
    mathlib_check.pop("_stdout", None)

    soul_ok = (profile_home / "SOUL.md").is_file() and (
        sha256_file(profile_home / "SOUL.md")
        == state.get("profile", {}).get("soul_sha256")
    )
    skill = profile_home / "skills" / "research" / "adversal-coordinator" / "SKILL.md"
    skill_ok = skill.is_file() and (
        sha256_file(skill) == state.get("profile", {}).get("skill_sha256")
    )
    restart_confirmed = "profile_restart_confirmed" in state.get("completed", [])
    deterministic_core_ready = all(marker_status.values()) and all(
        [doctor_check["ok"], verdict_check["ok"], lean_check["ok"], mathlib_check["ok"]]
    )

    result = {
        "bootstrap_complete": soul_ok and skill_ok and restart_confirmed and all(marker_status.values()),
        "gate_ready": gate_available and lean_check["ok"] and mathlib_check["ok"],
        "deterministic_core_ready": deterministic_core_ready,
        "workers_ready": False,
        "real_worker_smoke_tested": False,
        "profile": {"soul_ok": soul_ok, "skill_ok": skill_ok, "restart_confirmed": restart_confirmed},
        "project_markers": marker_status,
        "checks": {
            "doctor": doctor_check,
            "verdict_selftest": verdict_check,
            "lean_selftest": lean_check,
            "mathlib_build": mathlib_check,
        },
        "detected_workers": {
            name: {
                "present": data.get("present", False),
                "version": data.get("version"),
                "hazard_env_present": data.get("hazard_env_present", []),
            }
            for name, data in doctor.get("workers", {}).items()
        },
    }
    if record:
        state["updated_at"] = utc_now()
        state["readiness"] = {
            key: result[key]
            for key in (
                "bootstrap_complete",
                "gate_ready",
                "deterministic_core_ready",
                "workers_ready",
                "real_worker_smoke_tested",
            )
        }
        if deterministic_core_ready and result["bootstrap_complete"]:
            state["phase"] = "provider_selection"
            state["next_action"] = "select_and_validate_worker_auth_routes_with_the_user"
        else:
            state["phase"] = "dependencies_and_validation"
            state["next_action"] = "repair_failed_deterministic_checks"
        atomic_write(
            project / STATE_REL,
            (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            0o644,
        )
    return result


def inspect(project: Path, profile_home: Path | None, profile_source: str) -> dict:
    validate_source()
    validate_project_location(project)
    identity = source_identity()
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "source": {
            "root": str(SOURCE_ROOT),
            "repository": REPOSITORY_URL,
            "version": identity.version,
            "commit": identity.commit,
            "origin": identity.origin,
            "clean": identity.clean,
            "git_available": shutil.which("git") is not None,
        },
        "profile": {
            "home": str(profile_home) if profile_home else None,
            "home_source": profile_source,
            "exists": bool(profile_home and profile_home.is_dir()),
            "soul_exists": bool(profile_home and (profile_home / "SOUL.md").is_file()),
        },
        "project": {
            "root": str(project),
            "exists": project.is_dir(),
            "state_exists": (project / STATE_REL).is_file(),
        },
        "writes_performed": False,
    }


PLUGIN_SOURCE = SOURCE_ROOT / "integrations" / "hermes-adversal"
PLUGIN_DEST_REL = Path("plugins") / "hermes-adversal"

# The updater's contract: only vendored assets are ever touched. Live research
# state — ledgers, runs, the map, the wiki's knowledge, bootstrap state — is
# never written by an update, whatever the source ships.
UPDATABLE_PREFIXES = (
    Path("scripts"),
    Path("roles"),
    Path("docs"),
    Path(".adversal/schema"),
    Path(".adversal/templates"),
)
UPDATABLE_TOP = {
    Path("README.md"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("GEMINI.md"),
    Path(".hermes.md"),
    Path("MISIONES.md"),
    Path("COMO-FUNCIONA.md"),
    INSTRUCTIONS_REL,
    HELPER_REL,
}
# Files where a difference is reported for a human decision, never auto-applied:
# toolchain changes trigger rebuilds, and project.yaml may carry user config.
MANUAL_REVIEW = {
    Path("lakefile.toml"),
    Path("lean-toolchain"),
    Path("lake-manifest.json"),
    Path(".adversal/project.yaml"),
}


def _updatable(relative: Path) -> bool:
    if relative in UPDATABLE_TOP:
        return True
    if relative.parts and relative.parts[0] == "llm-wiki":
        # Wiki knowledge is live state; only its documentation files update.
        return relative.name == "README.md"
    return any(relative.is_relative_to(prefix) for prefix in UPDATABLE_PREFIXES)


def _profile_update_items(profile_home: Path, state: dict) -> list[dict]:
    """Skill, SOUL, and plugin files with their per-file action."""
    items: list[dict] = []
    recorded = state.get("profile", {})

    soul_dest = profile_home / "SOUL.md"
    if same_file(soul_dest, PROFILE_SOUL):
        action = "unchanged"
    elif not soul_dest.exists():
        action = "add"
    elif recorded.get("soul_sha256") and sha256_file(soul_dest) != recorded["soul_sha256"]:
        action = "conflict"  # locally personalized SOUL: a human must decide
    else:
        action = "update"
    items.append({"kind": "soul", "source": PROFILE_SOUL, "dest": soul_dest,
                  "rel": "SOUL.md", "action": action})

    skill_root = profile_home / "skills" / "research" / "adversal-coordinator"
    for relative, source in skill_files().items():
        dest = skill_root / relative
        if same_file(dest, source):
            action = "unchanged"
        elif not dest.exists():
            action = "add"
        elif relative == Path("SKILL.md") and recorded.get("skill_sha256") \
                and sha256_file(dest) != recorded["skill_sha256"]:
            action = "conflict"
        else:
            action = "update"
        items.append({"kind": "skill", "source": source, "dest": dest,
                      "rel": f"skills/research/adversal-coordinator/{relative}",
                      "action": action})

    if PLUGIN_SOURCE.is_dir():
        plugin_root = profile_home / PLUGIN_DEST_REL
        for relative, source in iter_files(PLUGIN_SOURCE):
            dest = plugin_root / relative
            if same_file(dest, source):
                action = "unchanged"
            elif not dest.exists():
                action = "add"
            else:
                action = "update"
            items.append({"kind": "plugin", "source": source, "dest": dest,
                          "rel": str(PLUGIN_DEST_REL / relative), "action": action})
    return items


def plan_update(project: Path, profile_home: Path) -> dict:
    """Fail-closed diff between this source checkout and an installed project."""
    validate_source()
    validate_project_location(project)
    if not profile_home.exists() or not profile_home.is_dir():
        raise BootstrapError(f"Hermes profile home does not exist: {profile_home}")

    identity = source_identity()
    if identity.commit == "unknown":
        raise BootstrapError(
            "the source must be a Git checkout so the updated commit can be recorded")
    if not official_origin(identity.origin):
        raise BootstrapError(
            f"source origin is not the official Adversal repository: {identity.origin}")
    if not identity.clean:
        raise BootstrapError(
            "source checkout has modified or untracked files; update requires a clean commit")

    state = existing_state(project)
    if not state:
        raise BootstrapError(
            "no bootstrap state found — update migrates an installed project; "
            "run the bootstrap first")
    if Path(state.get("project_root", "")).resolve() != project.resolve():
        raise BootstrapError("bootstrap state project_root does not match this project")
    recorded_home = Path(state.get("profile", {}).get("home", "")).resolve()
    if recorded_home != profile_home.resolve():
        raise BootstrapError("this is not the Hermes profile that owns this project")

    vendored_old: dict = state.get("vendored_sha256", {})
    buckets: dict[str, list[str]] = {
        "add": [], "update": [], "unchanged": [], "conflict": [], "manual_review": []}
    project_actions: list[dict] = []
    for relative, source in sorted(project_files().items()):
        dest = project / relative
        if relative in MANUAL_REVIEW:
            if not same_file(dest, source):
                buckets["manual_review"].append(str(relative))
            continue
        if not _updatable(relative):
            continue  # live state: never touched, not even listed
        if same_file(dest, source):
            buckets["unchanged"].append(str(relative))
            continue
        if not dest.exists():
            action = "add"
        elif str(relative) in vendored_old and sha256_file(dest) != vendored_old[str(relative)]:
            action = "conflict"  # proven local edit of a vendored file
        else:
            action = "update"
        buckets[action].append(str(relative))
        project_actions.append({"rel": str(relative), "source": source,
                                "dest": dest, "action": action})

    profile_items = _profile_update_items(profile_home, state)
    profile_summary = {
        "add": [i["rel"] for i in profile_items if i["action"] == "add"],
        "update": [i["rel"] for i in profile_items if i["action"] == "update"],
        "conflict": [i["rel"] for i in profile_items if i["action"] == "conflict"],
        "unchanged_count": sum(1 for i in profile_items if i["action"] == "unchanged"),
    }
    plugin_touched = any(i["kind"] == "plugin" and i["action"] != "unchanged"
                         for i in profile_items)
    return {
        "from_commit": state.get("source", {}).get("commit"),
        "to_commit": identity.commit,
        "to_version": identity.version,
        "same_commit": state.get("source", {}).get("commit") == identity.commit,
        "project": buckets,
        "profile": profile_summary,
        "plugin_restart_required": plugin_touched,
        "live_state_untouched": True,
        "_project_actions": project_actions,
        "_profile_items": profile_items,
        "_state": state,
    }


def apply_update(project: Path, profile_home: Path) -> dict:
    plan = plan_update(project, profile_home)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = project / ".adversal" / "bootstrap" / f"update-backup-{stamp}"
    backed_up: list[str] = []

    def place(source: Path, dest: Path, rel: str, scope: str) -> None:
        if dest.exists() and not same_file(dest, source):
            copy_file(dest, backup_root / scope / rel)
            backed_up.append(f"{scope}/{rel}")
        copy_file(source, dest)

    for item in plan["_project_actions"]:
        if item["action"] in ("add", "update"):
            place(item["source"], item["dest"], item["rel"], "project")
    for item in plan["_profile_items"]:
        if item["action"] in ("add", "update"):
            place(item["source"], item["dest"], item["rel"], "profile")

    state = plan["_state"]
    identity = source_identity()
    vendored: dict[str, str] = {}
    for relative, source in project_files().items():
        dest = project / relative
        if _updatable(relative) and relative not in MANUAL_REVIEW and dest.exists():
            vendored[str(relative)] = sha256_file(dest)
    state["source"] = {
        "repository": REPOSITORY_URL,
        "version": identity.version,
        "commit": identity.commit,
        "origin": identity.origin,
    }
    profile_state = state.setdefault("profile", {})
    soul_dest = profile_home / "SOUL.md"
    skill_md = profile_home / "skills" / "research" / "adversal-coordinator" / "SKILL.md"
    if soul_dest.exists():
        profile_state["soul_sha256"] = sha256_file(soul_dest)
    if skill_md.exists():
        profile_state["skill_sha256"] = sha256_file(skill_md)
    helper = project / HELPER_REL
    if helper.exists():
        profile_state["bootstrap_helper_sha256"] = sha256_file(helper)
    state["vendored_sha256"] = vendored
    state["last_update"] = {
        "at": utc_now(),
        "from_commit": plan["from_commit"],
        "to_commit": plan["to_commit"],
        "to_version": plan["to_version"],
        "backup": str(backup_root) if backed_up else None,
    }
    state["updated_at"] = utc_now()
    atomic_write(
        project / STATE_REL,
        (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        0o644,
    )

    report = {key: plan[key] for key in
              ("from_commit", "to_commit", "to_version", "same_commit",
               "project", "profile", "plugin_restart_required",
               "live_state_untouched")}
    report["writes_performed"] = True
    report["backup"] = str(backup_root) if backed_up else None
    report["backed_up_files"] = backed_up
    return report


def emit(data: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    for key, value in data.items():
        print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect, apply, or resume a fresh-profile Adversal bootstrap"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--project", type=Path, required=True)
        command.add_argument(
            "--profile-home",
            help="active Hermes HERMES_HOME; defaults to the HERMES_HOME environment variable",
        )
        command.add_argument("--json", action="store_true")

    inspect_parser = sub.add_parser("inspect", help="read-only portability preflight")
    common(inspect_parser)

    apply_parser = sub.add_parser("apply", help="configure the profile and initialize the project")
    common(apply_parser)
    apply_parser.add_argument("--approve-profile-write", action="store_true")
    apply_parser.add_argument("--approve-project-write", action="store_true")

    resume_parser = sub.add_parser("resume", help="continue after starting a new profile session")
    common(resume_parser)

    verify_parser = sub.add_parser("verify", help="run deterministic setup acceptance checks")
    common(verify_parser)
    verify_parser.add_argument(
        "--record", action="store_true", help="write readiness results to bootstrap state"
    )

    update_parser = sub.add_parser(
        "update",
        help="migrate an installed project/profile to this source checkout "
             "(plan-only without approval flags; live state is never touched)",
    )
    common(update_parser)
    update_parser.add_argument("--approve-profile-write", action="store_true")
    update_parser.add_argument("--approve-project-write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project = args.project.expanduser().resolve()
    profile_home, profile_source = resolve_profile_home(args.profile_home)
    try:
        if args.command == "inspect":
            emit(inspect(project, profile_home, profile_source), args.json)
            return 0
        if profile_home is None:
            raise BootstrapError(
                "cannot identify the active Hermes profile; supply --profile-home explicitly"
            )
        if args.command == "apply":
            if not args.approve_profile_write or not args.approve_project_write:
                raise BootstrapError(
                    "apply requires both --approve-profile-write and --approve-project-write "
                    "after explicit user approval"
                )
            emit(apply_bootstrap(project, profile_home), args.json)
            return 0
        if args.command == "resume":
            emit(resume_bootstrap(project, profile_home), args.json)
            return 0
        if args.command == "verify":
            result = verify_bootstrap(project, profile_home, args.record)
            emit(result, args.json)
            return 0 if result["deterministic_core_ready"] else 3
        if args.command == "update":
            if args.approve_profile_write and args.approve_project_write:
                emit(apply_update(project, profile_home), args.json)
                return 0
            plan = plan_update(project, profile_home)
            report = {key: plan[key] for key in
                      ("from_commit", "to_commit", "to_version", "same_commit",
                       "project", "profile", "plugin_restart_required",
                       "live_state_untouched")}
            report["writes_performed"] = False
            report["note"] = ("plan only — rerun with --approve-project-write "
                              "--approve-profile-write after user approval")
            emit(report, args.json)
            return 0
        raise BootstrapError(f"unsupported command: {args.command}")
    except BootstrapError as exc:
        print(f"bootstrap_error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
