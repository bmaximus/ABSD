#!/usr/bin/env python3
"""Ownership check: proves separation of duties and test-before-code ordering from git history.

Every ABSD hand-off is a commit with the trailers `ABSD-Agent: <agent>` and `ABSD-Cycle: C###`. For every commit in
the range this check proves that
  1. it is attributed: exactly one ABSD-Agent trailer naming a known agent (manager, analyst, designer, architect,
     tester, builder, auditor; any case). A commit without the trailer is "unattributed": an error unless
     --allow-unattributed (its files are then not checked). A trailer naming an unknown agent, or several agents, is
     an error even with --allow-unattributed. A missing or malformed ABSD-Cycle trailer is a warning.
  2. every file it adds, changes or deletes is owned by its agent or is "shared". Owners come from, in this order:
       - the built-in artifact table for absd-project/ (ABSD contract §5; the context table cannot override it):
         per-cycle artifacts in working/ (also when split into working/<artifact>/ parts), working/evidence/<agent>/,
         the living documents, and archive/ (manager);
       - the table under the first context.md heading containing "Source Layout" (up to the next heading of the same
         or a higher level): its first table with a column named like "Path" or "Glob" (one or more globs per cell,
         separated by commas, spaces or <br>) and a column named "Owner" (an agent or "shared", any case).
     The FIRST matching row wins: list specific globs before general ones. Globs match the whole repo-relative path:
     `**` any number of directories (also none), `*` and `?` within one path segment, a trailing `/` the whole
     directory. A file that no row matches is "unowned": a warning, an error with --strict.
  3. with --t-sha (the Tester's Plan & Bind commit, recorded at Gate T):
       a. every builder commit has T-SHA as an ancestor; otherwise it is a "production change before Gate T";
       b. every test file (tester-owned through the Source Layout table; the Tester's pipeline artifacts are not
          test files) changed by a commit after T-SHA is listed with commit, agent and subject. This is the Auditor's
          review list: each changed expected value or assertion must cite a Gate T amendment (ABSD playbook
          ORACLE-*). Changes by other agents are already errors under check 2.

Kit-sync commits carry the trailer `ABSD-Sync: <install|upgrade|migrate-v1> <version>` instead of ABSD-Agent (absd_sync.py
prints the command): they may change the kit paths (absd/, .claude/agents/*.md, .github/agents/*.agent.md), ADD the
product-owned seeds and make the v1 migration's moves — nothing else. The kit paths are read-only for every agent.

Merge commits are skipped with a notice unless --include-merges (their files are then those that differ from any
parent). Git reads trailers only from the LAST paragraph of the message, so write both in one paragraph:
  git commit -m "absd(C001): WP-01 — builder" -m $'ABSD-Agent: builder\\nABSD-Cycle: C001'
  git commit -m "absd(C001): WP-01 — builder" --trailer "ABSD-Agent: builder" --trailer "ABSD-Cycle: C001"

usage:
  ownership_check.py [--repo .] [--context absd-project/context.md] [--range <rev-range> | --base main]
                     [--t-sha <sha>] [--allow-unattributed] [--strict] [--include-merges]
                     [--json ownership.json] [--summary-md ownership.md]

--range defaults to <merge-base of HEAD and --base>..HEAD. A relative --context path is read from --repo.
Exit code: 0 pass, 1 check failed, 2 usage/input error. Python 3.9+ and git 2.22+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field

AGENTS = ("manager", "analyst", "designer", "architect", "tester", "builder", "auditor")
SHARED = "shared"
OWNERS = AGENTS + (SHARED,)
UNOWNED = "unowned"
UNATTRIBUTED = "unattributed"   # no ABSD-Agent trailer
INVALID = "invalid"             # an ABSD-Agent trailer that names no single known agent
BUILT_IN = "built-in"
SYNC = "sync"                   # a kit install/upgrade/migrate-v1 commit: trailer "ABSD-Sync: <operation> <version>"
KIT = "kit"                     # owner of the vendored kit paths: read-only for every agent
KIT_GLOBS = ("absd/", ".claude/agents/*.md", ".github/agents/*.agent.md")
V1_PATHS = ("working/", ".claude/working/", "archive/", ".claude/archive/")
PROJECT_DIR = "absd-project"

# ABSD contract §5: pipeline artifacts and living documents under absd-project/, by owner.
ARTIFACTS = {
    "manager": ("working/cycle.md", "working/brd.md", "working/defect.md", "context.md", "lessons.md", "archive/"),
    "analyst": ("working/analysis.md", "catalogue.md"),
    "designer": ("working/design.md", "working/design_review.md", "design-system.md"),
    "architect": ("working/architecture.md",),
    "tester": ("working/test_plan.md", "working/test_report.md"),
    "builder": ("working/build_log.md", "working/clarification_needed.md"),
    "auditor": ("working/arch_review.md", "working/audit.md"),
}

LOG_FIELDS = ("%H", "%P", "%an", "%s", "%(trailers:key=ABSD-Agent,valueonly)", "%(trailers:key=ABSD-Cycle,valueonly)",
              "%(trailers:key=ABSD-Sync,valueonly)", "%b")
LOG_FORMAT = "%x1f".join(LOG_FIELDS) + "%x1e"
AGENT_LINE = re.compile(r"^ABSD-Agent\s*:", re.IGNORECASE | re.MULTILINE)
CYCLE_ID = re.compile(r"C\d{3,}")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
SEPARATOR_CELL = re.compile(r":?-{3,}:?")
GLOB_SEPARATORS = re.compile(r"<br\s*/?>|[,\s]+")


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from absd_sync import SEEDS  # noqa: E402  (the product-owned seeds a kit-sync commit may add)

SEED_PATHS = frozenset(destination for _, destination in SEEDS)


class InputError(Exception):
    """Unreadable or malformed input: exit code 2."""


class GitError(Exception):
    """A git command failed: exit code 2."""


# --- ownership rules --------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Rule:
    glob: str
    owner: str
    origin: str             # BUILT_IN or "<context file>:<line>"
    regex: re.Pattern


def glob_regex(glob: str) -> re.Pattern:
    """`**` any number of directories (also none), `*` any characters and `?` one character within a path segment,
    a trailing `/` everything under that directory. Matched against the whole repo-relative path."""
    pattern = glob[2:] if glob.startswith("./") else glob
    pattern = pattern.lstrip("/")
    if pattern.endswith("/"):
        pattern += "**"
    parts, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i) and (i == 0 or pattern[i - 1] == "/"):
            parts.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            parts.append(".*")
            i += 2
        elif pattern[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(parts))


def make_rule(glob: str, owner: str, origin: str) -> Rule:
    return Rule(glob=glob, owner=owner, origin=origin, regex=glob_regex(glob))


def kit_rules() -> list[Rule]:
    """The vendored kit: read-only for every agent; only kit-sync commits (ABSD-Sync trailer) change it."""
    return [make_rule(glob, KIT, BUILT_IN) for glob in KIT_GLOBS]


def built_in_rules() -> list[Rule]:
    """The kit paths, then the contract's artifact ownership. A per-cycle artifact working/<name>.md may be split into
    working/<name>/NN-<part>.md parts; each agent keeps its evidence in working/evidence/<agent>/."""
    globs = []
    for owner, paths in ARTIFACTS.items():
        for path in paths:
            globs.append((path, owner))
            if path.startswith("working/") and path.endswith(".md"):
                globs.append((path[:-len(".md")] + "/", owner))
    globs += [(f"working/evidence/{agent}/", agent) for agent in AGENTS]
    return kit_rules() + [make_rule(f"{PROJECT_DIR}/{glob}", owner, BUILT_IN) for glob, owner in globs]


def owner_of(path: str, rules: list[Rule]) -> tuple[str, Rule | None]:
    """The owner of a repo-relative path: the first rule whose glob matches it wins."""
    for rule in rules:
        if rule.regex.fullmatch(path):
            return rule.owner, rule
    return UNOWNED, None


# --- context.md -------------------------------------------------------------------------------------------------

def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def plain(cell: str) -> str:
    return cell.strip().strip("*`").strip()


def layout_section(lines: list[str], path: str) -> list[tuple[int, str]]:
    """(line number, text) of the lines under the first heading containing "Source Layout", up to the next heading
    of the same or a higher level."""
    level = 0
    section: list[tuple[int, str]] = []
    for number, line in enumerate(lines, start=1):
        heading = HEADING.match(line)
        if not level:
            if heading and "source layout" in heading.group(2).lower():
                level = len(heading.group(1))
            continue
        if heading and len(heading.group(1)) <= level:
            break
        section.append((number, line))
    if not level:
        raise InputError(f'{path}: no heading containing "Source Layout"')
    return section


def markdown_tables(section: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    """Runs of consecutive lines that start with `|`."""
    tables, current = [], []
    for number, line in section:
        if line.strip().startswith("|"):
            current.append((number, line))
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def table_rules(rows: list[tuple[int, str]], path_col: int, owner_col: int, path: str) -> list[Rule]:
    rules = []
    for number, line in rows:
        cells = table_cells(line)
        if all(SEPARATOR_CELL.fullmatch(cell) for cell in cells if cell):
            continue
        origin = f"{path}:{number}"
        if max(path_col, owner_col) >= len(cells):
            raise InputError(f"{origin}: the row has {len(cells)} cells — it needs its Path/Glob and Owner cells")
        owner = plain(cells[owner_col]).lower()
        if owner not in OWNERS:
            raise InputError(f"{origin}: unknown owner '{cells[owner_col]}' — use one of {', '.join(OWNERS)}")
        globs = [glob for glob in GLOB_SEPARATORS.split(cells[path_col].replace("`", "")) if glob]
        if not globs:
            raise InputError(f"{origin}: the row has no path glob")
        rules += [make_rule(glob, owner, origin) for glob in globs]
    return rules


def read_source_layout(path: str) -> list[Rule]:
    """Ownership rules from the Source Layout table of context.md, in row order."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for table in markdown_tables(layout_section(lines, path)):
        header = [plain(cell).lower() for cell in table_cells(table[0][1])]
        path_col = next((i for i, name in enumerate(header) if "path" in name or "glob" in name), None)
        owner_col = next((i for i, name in enumerate(header) if "owner" in name), None)
        if path_col is None or owner_col is None:
            continue
        rules = table_rules(table[1:], path_col, owner_col, path)
        if not rules:
            raise InputError(f"{path}:{table[0][0]}: the Source Layout table has no rows")
        return rules
    raise InputError(f'{path}: no table with a "Path" or "Glob" column and an "Owner" column under the Source Layout heading')


# --- git --------------------------------------------------------------------------------------------------------

@dataclass
class Commit:
    sha: str
    parents: list
    author: str
    subject: str
    agent: str                  # a known agent, UNATTRIBUTED or INVALID
    problem: str                # why the commit is not attributed ("" when it is)
    cycles: list
    files: list = field(default_factory=list)
    deleted: set = field(default_factory=set)   # the subset of files the commit deletes
    added: set = field(default_factory=set)     # the subset of files the commit adds

    @property
    def short(self) -> str:
        return self.sha[:7]

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1


def run_git(repo: str, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError as error:
        raise GitError("git is not installed") from error


def git(repo: str, *args: str) -> str:
    result = run_git(repo, *args)
    if result.returncode != 0:
        raise GitError(f"git {args[0]} failed: {result.stderr.strip() or f'exit code {result.returncode}'}")
    return result.stdout


def is_ancestor(repo: str, ancestor: str, commit: str) -> bool:
    result = run_git(repo, "merge-base", "--is-ancestor", ancestor, commit)
    if result.returncode not in (0, 1):
        raise GitError(f"git merge-base --is-ancestor failed: {result.stderr.strip()}")
    return result.returncode == 0


def attribute(agent_trailers: str, body: str) -> tuple[str, str]:
    """(agent, problem) from the ABSD-Agent trailer values of one commit."""
    names = sorted({value.strip().lower() for value in agent_trailers.splitlines() if value.strip()})
    if not names:
        if AGENT_LINE.search(body):
            return UNATTRIBUTED, "its ABSD-Agent line is not in the message's last paragraph, so git does not read it as a trailer"
        return UNATTRIBUTED, "no ABSD-Agent trailer"
    if len(names) > 1:
        return INVALID, f"several agents in ABSD-Agent trailers ({', '.join(names)})"
    if names[0] not in AGENTS:
        return INVALID, f"unknown agent '{names[0]}' in the ABSD-Agent trailer"
    return names[0], ""


def read_commits(repo: str, rev_range: str) -> list[Commit]:
    """Commits in the range, oldest first."""
    out = git(repo, "log", "--topo-order", "--reverse", f"--format={LOG_FORMAT}", rev_range, "--")
    commits = []
    for record in out.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        sha, parents, author, subject, agents, cycles, sync, body = record.split("\x1f", len(LOG_FIELDS) - 1)
        agent, problem = attribute(agents, body)
        if sync.strip():
            agent, problem = (SYNC, "") if agent == UNATTRIBUTED else (INVALID, "both ABSD-Agent and ABSD-Sync trailers")
        commits.append(Commit(sha=sha, parents=parents.split(), author=author, subject=subject, agent=agent,
                              problem=problem, cycles=sorted({c.strip() for c in cycles.splitlines() if c.strip()})))
    return commits


def changed_files(repo: str, sha: str) -> tuple[list[str], set[str], set[str]]:
    """(every path the commit adds, changes or deletes; the deleted ones; the added ones) — a rename is its old and its
    new path."""
    out = git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", "-m", "--root", "--no-renames", "-z", sha)
    fields = out.split("\0")
    files, deleted, added = set(), set(), set()
    for status, path in zip(fields[0::2], fields[1::2]):
        if not status or not path:
            continue
        files.add(path)
        if status.startswith("D"):
            deleted.add(path)
        elif status.startswith("A"):
            added.add(path)
    return sorted(files), deleted, added


def is_archive_move(commit: Commit, path: str) -> bool:
    """The Manager archives a cycle by moving every per-cycle artifact out of working/ into archive/ (RULES §1):
    deleting another agent's file there in a commit that also adds archive files is that move, not authorship. Writing
    or changing such a file, or deleting it without archiving, is still a violation."""
    return (commit.agent == "manager" and path in commit.deleted
            and path.startswith(f"{PROJECT_DIR}/working/")
            and any(added.startswith(f"{PROJECT_DIR}/archive/") for added in commit.added))


def default_range(repo: str, base: str) -> str:
    return git(repo, "merge-base", "HEAD", base).strip() + "..HEAD"


def resolve_commit(repo: str, revision: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").strip()


# --- checks -----------------------------------------------------------------------------------------------------

@dataclass
class Findings:
    errors: list = field(default_factory=list)      # (title, message)
    warnings: list = field(default_factory=list)    # (title, message)
    review: list = field(default_factory=list)      # (path, Commit)


def describe(commit: Commit) -> str:
    return f"{commit.short} ({commit.agent}) '{commit.subject}'"


def check_attribution(commits: list[Commit], allow_unattributed: bool, findings: Findings) -> None:
    for commit in commits:
        if commit.agent == UNATTRIBUTED:
            target = findings.warnings if allow_unattributed else findings.errors
            target.append(("unattributed", f"{describe(commit)}: {commit.problem}"))
        elif commit.agent == INVALID:
            findings.errors.append(("unattributed", f"{describe(commit)}: {commit.problem}"))
        elif commit.agent != SYNC and (len(commit.cycles) != 1 or not CYCLE_ID.fullmatch(commit.cycles[0])):
            found = ", ".join(commit.cycles) or "none"
            findings.warnings.append(("cycle trailer", f"{describe(commit)}: expected one `ABSD-Cycle: C###` trailer, found {found}"))


def sync_allows(commit: Commit, path: str, rules: list[Rule]) -> bool:
    """A kit-sync commit (absd_sync.py install / upgrade / migrate-v1) may change kit paths, ADD the product-owned
    seeds, and make the v1 migration's moves (v1 working/archive paths out, absd-project/ context and archive in)."""
    if owner_of(path, kit_rules())[0] == KIT:
        return True
    if path in commit.added and path in SEED_PATHS:
        return True
    if path in commit.deleted and path.startswith(V1_PATHS):
        return True
    return path in commit.added and (path == f"{PROJECT_DIR}/context.md" or path.startswith(f"{PROJECT_DIR}/archive/"))


def check_ownership(commits: list[Commit], rules: list[Rule], strict: bool, findings: Findings) -> None:
    unowned: dict[str, list[Commit]] = defaultdict(list)
    for commit in commits:
        if commit.agent == SYNC:
            for path in commit.files:
                if not sync_allows(commit, path, rules):
                    findings.errors.append(("ownership", f"{describe(commit)} (kit sync) changed {path}: a kit-sync "
                                            "commit may only change kit paths, add seeds and make v1 migration moves"))
            continue
        if commit.agent not in AGENTS:
            continue
        for path in commit.files:
            owner, rule = owner_of(path, rules)
            if owner == UNOWNED:
                unowned[path].append(commit)
            elif owner not in (commit.agent, SHARED) and not is_archive_move(commit, path):
                findings.errors.append(("ownership", f"{describe(commit)} changed {path}, owned by {owner} ({rule.origin}: {rule.glob})"))
    for path, touching in sorted(unowned.items()):
        message = f"{path} matches no Source Layout row (changed by {', '.join(f'{c.short} ({c.agent})' for c in touching)})"
        (findings.errors if strict else findings.warnings).append(("unowned", message))


def check_gate_t(repo: str, commits: list[Commit], rules: list[Rule], t_sha: str, findings: Findings) -> None:
    for commit in commits:
        descends = is_ancestor(repo, t_sha, commit.sha)
        if commit.agent == "builder" and not descends:
            findings.errors.append(("Gate T order", f"production change before Gate T: {describe(commit)} does not descend from T-SHA {t_sha[:7]}"))
        if not descends or commit.sha == t_sha:
            continue
        for path in commit.files:
            owner, rule = owner_of(path, rules)
            if owner == "tester" and rule.origin != BUILT_IN:
                findings.review.append((path, commit))


# --- report -----------------------------------------------------------------------------------------------------

def agent_stats(commits: list[Commit]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for label in AGENTS + (SYNC, UNATTRIBUTED, INVALID):
        mine = [c for c in commits if c.agent == label]
        if mine:
            stats[label] = {"commits": len(mine), "files": len({path for c in mine for path in c.files})}
    return stats


def cell(text: str) -> str:
    return text.replace("|", "\\|")


def markdown(rev_range: str, checked: list[Commit], merges: list[Commit], t_sha: str, findings: Findings) -> str:
    verdict = "FAILED" if findings.errors else "passed"
    facts = [f"range `{rev_range}`", f"{len(checked)} commits checked"]
    if merges:
        facts.append(f"{len(merges)} merge commits skipped")
    if t_sha:
        facts.append(f"T-SHA `{t_sha[:7]}`")
    lines = [f"### Ownership check — {verdict}", " · ".join(facts), "", "| Agent | Commits | Files |", "|---|---|---|"]
    lines += [f"| {agent} | {s['commits']} | {s['files']} |" for agent, s in agent_stats(checked).items()]
    for heading, items in (("Violations", findings.errors), ("Warnings", findings.warnings)):
        if items:
            lines += ["", f"**{heading} ({len(items)})**", *[f"- {message}" for _, message in items]]
    if t_sha:
        lines += ["", f"**Test files changed after Gate T ({len(findings.review)})** — each changed expected value or "
                      "assertion must cite a Gate T amendment"]
        if findings.review:
            lines += ["", "| File | Commit | Agent | Subject |", "|---|---|---|---|"]
            lines += [f"| {cell(path)} | {c.short} | {c.agent} | {cell(c.subject)} |" for path, c in findings.review]
    return "\n".join(lines) + "\n"


def json_report(rev_range: str, checked: list[Commit], merges: list[Commit], t_sha: str, rules: list[Rule],
                findings: Findings) -> dict:
    return {
        "range": rev_range,
        "tSha": t_sha or None,
        "passed": not findings.errors,
        "agents": agent_stats(checked),
        "commits": [{
            "sha": c.sha, "author": c.author, "subject": c.subject, "agent": c.agent, "cycles": c.cycles,
            "files": [{"path": path, "owner": owner_of(path, rules)[0]} for path in c.files],
        } for c in checked],
        "skippedMerges": [c.sha for c in merges],
        "errors": [message for _, message in findings.errors],
        "warnings": [message for _, message in findings.warnings],
        "review": [{"file": path, "commit": c.sha, "agent": c.agent, "subject": c.subject} for path, c in findings.review],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="the git repository (default: current directory)")
    parser.add_argument("--context", default=f"{PROJECT_DIR}/context.md", help="context.md with the Source Layout table (relative: inside --repo)")
    parser.add_argument("--range", help="git revision range to check (default: <merge-base of HEAD and --base>..HEAD)")
    parser.add_argument("--base", default="main", help="default branch for the default range (default: main)")
    parser.add_argument("--t-sha", help="the Gate T commit: builder commits must descend from it; test changes after it are listed")
    parser.add_argument("--allow-unattributed", action="store_true", help="commits without an ABSD-Agent trailer are warnings, not errors")
    parser.add_argument("--strict", action="store_true", help="files no Source Layout row matches are errors, not warnings")
    parser.add_argument("--include-merges", action="store_true", help="check merge commits too (default: skip them)")
    parser.add_argument("--json", dest="json_out", help="write the result as JSON")
    parser.add_argument("--summary-md", help="write the Markdown summary to this file (also appended to $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)

    for option, value in (("--range", args.range), ("--base", args.base), ("--t-sha", args.t_sha)):
        if value is not None and (not value.strip() or value.startswith("-")):
            print(f"::error::{option} must be a git revision, got '{value}'")
            return 2

    context = os.path.normpath(os.path.join(args.repo, args.context))  # an absolute --context replaces --repo
    try:
        rules = built_in_rules() + read_source_layout(context)
        rev_range = args.range or default_range(args.repo, args.base)
        commits = read_commits(args.repo, rev_range)
        if not commits:
            raise InputError(f"no commits in range {rev_range} — check --range or --base")
        t_sha = resolve_commit(args.repo, args.t_sha) if args.t_sha else ""
        skip_merges = not args.include_merges
        merges = [c for c in commits if skip_merges and c.is_merge]
        checked = [c for c in commits if not (skip_merges and c.is_merge)]
        for commit in checked:
            commit.files, commit.deleted, commit.added = changed_files(args.repo, commit.sha)
        findings = Findings()
        check_attribution(checked, args.allow_unattributed, findings)
        check_ownership(checked, rules, args.strict, findings)
        if t_sha:
            check_gate_t(args.repo, checked, rules, t_sha, findings)
    except (OSError, InputError, GitError) as error:
        print(f"::error::{error}")
        return 2

    summary = markdown(rev_range, checked, merges, t_sha, findings)
    print(summary)
    for title, message in findings.errors:
        print(f"::error title={title}::{message}")
    for title, message in findings.warnings:
        print(f"::warning title={title}::{message}")
    if merges:
        print(f"::notice title=merges::{len(merges)} merge commits skipped ({', '.join(c.short for c in merges)}) — "
              "pass --include-merges to check them")
    for target in filter(None, (args.summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(summary + "\n")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as out:
            json.dump(json_report(rev_range, checked, merges, t_sha, rules, findings), out, ensure_ascii=False, indent=2)
    return 1 if findings.errors else 0


if __name__ == "__main__":
    sys.exit(main())
