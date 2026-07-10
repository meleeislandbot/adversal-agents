#!/usr/bin/env python3
"""Codex CLI worker adapter for the verification council.

Runs one fixed role against one claim through ``codex exec``. The worker gets
only the prompt: user configuration is ignored, the working directory is
empty, sessions are ephemeral, the shell and other optional tool surfaces are
disabled, and any observed tool event invalidates the call. Structured output
is constrained by a JSON Schema before it reaches the deterministic gate.

By default OPENAI_API_KEY and CODEX_API_KEY are removed from the child
environment so a saved ChatGPT subscription login is preferred. Metered API
usage is possible only with an explicit ``--allow-api``.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from claude_worker import (
    SAFE_CLAIM_ID,
    SAFE_SUFFIX,
    build_prompt,
    looks_like_auth_failure,
    looks_like_failure,
    normalize,
)

BILLING_VARS = ("OPENAI_API_KEY", "CODEX_API_KEY")

# Unlike Claude Code, Codex keeps file-based credentials that agent-spawned
# shells can read, so a plain interactive login is enough.
AUTH_REMEDIATION = """\
fix: Codex CLI is not authenticated for this environment.
Relay to the person at the keyboard: run `codex login` in your own terminal
and finish the ChatGPT sign-in; no extra token wiring is needed afterwards.
Note: an exhausted quota or rate limit is NOT an auth failure — it clears at
the plan's reset; retry later instead of re-authenticating."""
DISABLED_FEATURES = (
    "shell_tool",
    "apps",
    "plugins",
    "browser_use",
    "in_app_browser",
    "computer_use",
    "image_generation",
    "multi_agent",
    "goals",
    "workspace_dependencies",
    "tool_suggest",
    "skill_mcp_dependency_install",
)
TOOL_EVENT_TYPES = {
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "web_search",
    "computer_use",
    "image_generation",
}


def output_schema(formalizer: bool) -> dict:
    properties: dict[str, object] = {
        "claim_id": {"type": "string"},
        "role": {"type": "string"},
        "worker": {"type": "string"},
        "status_vote": {
            "type": "string",
            "enum": ["proven", "known", "refuted", "conjecture", "sketch",
                     "not_established"],
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["lean", "citation", "counterexample", "argument"],
                    },
                    "ref": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["type", "ref", "detail"],
                "additionalProperties": False,
            },
        },
        "breaks_at": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "raw_text": {"type": "string"},
    }
    required = list(properties)
    if formalizer:
        properties["lean_source"] = {"type": ["string", "null"]}
        required.append("lean_source")
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def parse_jsonl_events(text: str) -> tuple[dict[str, int], list[str]]:
    usage: dict[str, int] = {}
    tool_events: list[str] = []
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            for key in ("input_tokens", "cached_input_tokens", "output_tokens",
                        "reasoning_output_tokens"):
                value = event["usage"].get(key)
                if isinstance(value, int) and value >= 0:
                    usage[key] = value
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") in TOOL_EVENT_TYPES:
            tool_events.append(str(item["type"]))
    return usage, tool_events


def call_codex(prompt: str, cwd: Path, timeout: int, formalizer: bool,
               allow_api: bool = False) -> tuple[str, dict[str, int], list[str], str, int]:
    child_env = dict(os.environ)
    route = "api-key-env"
    if not allow_api:
        for var in BILLING_VARS:
            child_env.pop(var, None)
        route = "chatgpt-subscription-preferred"

    schema_path = cwd / "response.schema.json"
    result_path = cwd / "result.json"
    schema_path.write_text(json.dumps(output_schema(formalizer)), encoding="utf-8")
    command = [
        "codex", "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--skip-git-repo-check",
        "--strict-config",
        "--sandbox", "read-only",
        "--json",
        "--output-schema", str(schema_path),
        "--output-last-message", str(result_path),
        "--cd", str(cwd),
    ]
    for feature in DISABLED_FEATURES:
        command.extend(["--disable", feature])
    command.append("-")
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            env=child_env,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"worker timed out after {timeout}s", {}, [], route, 124
    usage, tool_events = parse_jsonl_events(proc.stdout or "")
    raw = result_path.read_text(encoding="utf-8") if result_path.exists() else ""
    if not raw:
        raw = (proc.stderr or proc.stdout or "").strip()
    return raw, usage, tool_events, route, proc.returncode


def record_budget(run: Path, role: str, claim_id: str, route: str,
                  usage: dict[str, int]) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "worker_check",
        "worker": "codex-cli",
        "auth_route": "subscription" if route.startswith("chatgpt-") else "api-key",
        "cost_risk": "low" if route.startswith("chatgpt-") else "high",
        "role": role,
        "claim_id": claim_id,
        "usage": usage,
        "notes": "Tool-less isolated Codex worker; token usage is quota usage, not a dollar charge.",
    }
    with (run / "budget.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Codex CLI worker adapter")
    ap.add_argument("--role", required=True,
                    choices=["strategist", "formalizer", "prior-art-auditor", "skeptic"])
    ap.add_argument("--claim-id", required=True)
    ap.add_argument("--statement", required=True)
    ap.add_argument("--formal-statement", default="")
    ap.add_argument("--theorem-name", default="")
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-api", action="store_true")
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    if bool(args.formal_statement) != bool(args.theorem_name):
        ap.error("--formal-statement and --theorem-name must be supplied together")
    if not SAFE_CLAIM_ID.fullmatch(args.claim_id):
        ap.error("--claim-id must contain only letters, digits, dot, underscore, or hyphen")
    if not SAFE_SUFFIX.fullmatch(args.suffix):
        ap.error("--suffix must be empty or a hyphen followed by letters/digits/_/-")

    (args.run / "workers").mkdir(parents=True, exist_ok=True)
    present_keys = [var for var in BILLING_VARS if os.getenv(var)]
    if present_keys:
        action = "allowed" if args.allow_api else "scrubbed"
        print(f"note: API-key environment variable(s) present but values hidden; {action}.",
              file=sys.stderr)

    failed = False
    parsed: dict | None = None
    if args.dry_run:
        obj = normalize({"raw_text": f"[dry-run] no model called for role {args.role}."},
                        args.role, args.claim_id, "", worker="codex")
    else:
        prompt = build_prompt(
            args.role,
            args.claim_id,
            args.statement,
            formal_statement=args.formal_statement,
            theorem_name=args.theorem_name,
        )
        with tempfile.TemporaryDirectory(prefix="adversal-codex-worker-") as isolated:
            raw, usage, tool_events, route, worker_exit = call_codex(
                prompt, Path(isolated), args.timeout, args.role == "formalizer",
                allow_api=args.allow_api)
        record_budget(args.run, args.role, args.claim_id, route, usage)
        print(f"[codex_worker] route={route} usage={usage}", file=sys.stderr)
        if tool_events:
            failed = True
            print(f"error: isolated Codex worker attempted tool use: {tool_events}", file=sys.stderr)
        if worker_exit != 0 or looks_like_failure(raw):
            failed = True
            print(f"error: Codex worker could not run (role {args.role}, exit {worker_exit}): "
                  f"{raw.strip()[:200]}", file=sys.stderr)
            if looks_like_auth_failure(raw):
                print(AUTH_REMEDIATION, file=sys.stderr)
        try:
            candidate = json.loads(raw)
            parsed = candidate if isinstance(candidate, dict) else None
        except json.JSONDecodeError:
            parsed = None
        if parsed is None:
            failed = True
            print("error: Codex worker did not return a JSON object", file=sys.stderr)
        obj = normalize(parsed, args.role, args.claim_id, raw, worker="codex")
        if args.role == "formalizer" and isinstance(parsed, dict) and parsed.get("lean_source"):
            (args.run / "lean").mkdir(parents=True, exist_ok=True)
            lean_path = args.run / "lean" / f"{args.claim_id}-codex.lean"
            lean_path.write_text(str(parsed["lean_source"]), encoding="utf-8")
            obj["evidence"] = [{"type": "lean", "ref": f"lean/{lean_path.name}"}]
        if args.role == "skeptic" and isinstance(parsed, dict) and parsed.get("lean_disproof_source"):
            (args.run / "lean").mkdir(parents=True, exist_ok=True)
            lean_path = args.run / "lean" / f"{args.claim_id}-disproof-codex{args.suffix}.lean"
            lean_path.write_text(str(parsed["lean_disproof_source"]), encoding="utf-8")
            obj["evidence"] = list(obj.get("evidence") or []) + [
                {"type": "lean", "ref": f"lean/{lean_path.name}"}]

    out_path = args.run / "workers" / f"codex-{args.role}{args.suffix}.json"
    out_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print(out_path)
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
