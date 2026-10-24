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
  - the vendored kit (`absd/`, `.claude/agents/*.md`, `.github/agents/*.agent.md`) → refused for every agent:
    products never edit the kit (upgrade it with absd_sync.py);
  - the agent configuration (`.claude/`, every `CLAUDE.md`, `.github/copilot-instructions.md`,
    `.github/instructions/`) → the Manager's: no worker switches off this hook or rewrites its own instructions;
  - a path owned by the agent, or "shared", or matched by no rule → allowed (unowned paths are reported by
    ownership_check.py);
  - anything else → refused, with the owner and the route to take instead (by writer and owner).

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

CONTEXT = os.path.join(oc.PROJECT_DIR, "context.md")
INSTEAD = {   # (writer, owner) first, then by owner
    ("builder", "tester"): "a test change goes to the Tester as TC-CONFLICT-n in build_log.md",
    ("tester", "builder"): "a production change goes to the Architect as TSEAM-n in test_plan.md",
    "tester": "a test or gate change is the Tester's: name it in your hand-back (Auditor: a finding in audit.md)",
    "builder": "a production change goes through architecture.md: name it in your hand-back as a finding or question",
    "manager": "configuration, context and cycle files are the Manager's: name the change in your hand-back",
    "analyst": "a requirement question goes to the Manager in your hand-back (open question)",
    "designer": "a design question goes to the Manager in your hand-back (Gate UX delta)",
    "architect": "an architecture gap goes to the Manager in your hand-back (clarification or architecture finding)",
    "auditor": "audit reports are the Auditor's: record your evidence in your own artifact",
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
    if oc.owner_of(path, oc.kit_rules())[0] == oc.KIT:
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
    hint = INSTEAD.get((agent, owner)) or INSTEAD.get(owner, "record the need in your own artifact; the Manager routes it")
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
