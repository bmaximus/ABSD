#!/usr/bin/env python3
"""Ownership hook: refuses, at write time, an ABSD agent's file write outside the paths it owns (RULES §5, rule 9).

Claude Code runs it as a PreToolUse hook for file-writing tools (the product settings template installs it):

  {"hooks": {"PreToolUse": [{"matcher": "Write|Edit|MultiEdit|NotebookEdit",
     "hooks": [{"type": "command", "command": "python3 \\"$CLAUDE_PROJECT_DIR/absd/tooling/ownership_hook.py\\"",
                "onFailure": "block"}]}]}}

It reads the hook input (JSON on stdin: `agent_type`, `tool_name`, `tool_input.file_path` or `.notebook_path`, `cwd`)
and decides with the same rules as ownership_check.py (built-in artifact table first, then the "Source Layout &
Ownership" table of absd-project/context.md; first match wins):
  - not an ABSD agent (a plain session, another agent type) → allowed: pipeline bypasses are caught in history by
    ownership_check.py, which reports unattributed commits;
  - a path outside the project directory (scratch files) → allowed;
  - the vendored kit (`absd/`, `.claude/agents/`, `.github/agents/`) → refused for every agent: products never edit
    the kit (upgrade it with absd_sync.py);
  - a path owned by the agent, or "shared", or matched by no rule → allowed (unowned paths are reported by
    ownership_check.py);
  - anything else → refused, with the owner and what to do instead.

Bash commands can still write files; the history check (ownership_check.py) is the backstop for those.

Exit code: 0 allow · 2 refuse (reason on stderr, shown to the agent) — Claude Code's PreToolUse contract.
Python 3.9+, standard library only; imports ownership_check.py from its own directory.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownership_check as oc  # noqa: E402

KIT_GLOBS = ("absd/", ".claude/agents/", ".github/agents/")
CONTEXT = os.path.join(oc.PROJECT_DIR, "context.md")
INSTEAD = {
    "builder": "a test change goes to the Tester as TC-CONFLICT-n in build_log.md",
    "tester": "a production change goes to the Architect as TSEAM-n in test_plan.md",
}


def agent_of(event: dict) -> str:
    """The ABSD agent behind the call, or "" — `agent_type` may be namespaced (`plugin:tester`)."""
    raw = str(event.get("agent_type") or "").strip().lower()
    name = raw.rsplit(":", 1)[-1]
    return name if name in oc.AGENTS else ""


def target_of(event: dict) -> str:
    tool_input = event.get("tool_input") or {}
    return str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")


def relative_to_project(target: str, project: str, cwd: str) -> str | None:
    """Repo-relative POSIX path, or None when the target lies outside the project."""
    absolute = os.path.normpath(target if os.path.isabs(target) else os.path.join(cwd or project, target))
    project = os.path.normpath(project)
    if os.path.commonpath([absolute, project]) != project:
        return None
    return os.path.relpath(absolute, project).replace(os.sep, "/")


def decide(event: dict, project: str) -> tuple[bool, str]:
    """(allowed, reason)."""
    agent = agent_of(event)
    target = target_of(event)
    if not agent or not target:
        return True, "not an ABSD agent write"
    path = relative_to_project(target, project, str(event.get("cwd") or project))
    if path is None:
        return True, "outside the project"
    kit = [oc.make_rule(glob, "kit", "kit") for glob in KIT_GLOBS]
    if oc.owner_of(path, kit)[0] == "kit":
        return False, (f"ABSD ownership: {agent} may not write {path} — the kit is vendored and read-only in products; "
                       "propose a change through absd-project/lessons.md (enrichment), upgrade with absd_sync.py.")
    rules = oc.built_in_rules()
    owner, rule = oc.owner_of(path, rules)
    if rule is None:
        context = os.path.join(project, CONTEXT)
        if os.path.exists(context):
            try:
                owner, rule = oc.owner_of(path, oc.read_source_layout(context))
            except (oc.InputError, OSError) as error:
                return False, (f"ABSD ownership: cannot decide who owns {path}: {error}. "
                               f"The Manager must fix the Source Layout & Ownership table in {CONTEXT}.")
    if owner in (agent, oc.SHARED, oc.UNOWNED):
        return True, f"{path}: owner {owner}"
    where = "the ABSD artifact table" if rule is not None and rule.origin == oc.BUILT_IN else (rule.origin if rule else "?")
    hint = INSTEAD.get(agent, "record the need in your own artifact; the Manager routes it to the owner")
    return False, (f"ABSD ownership: {agent} may not write {path} — it is owned by {owner} ({where}). "
                   f"Do not work around this; {hint}.")


def main(stdin=None, environ=None) -> int:
    environ = os.environ if environ is None else environ
    raw = (stdin or sys.stdin).read()
    try:
        event = json.loads(raw or "{}")
    except json.JSONDecodeError as error:
        print(f"ABSD ownership hook: unreadable hook input ({error}); refusing the write.", file=sys.stderr)
        return 2
    project = environ.get("CLAUDE_PROJECT_DIR") or str(event.get("cwd") or os.getcwd())
    allowed, reason = decide(event, project)
    if not allowed:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
