#!/usr/bin/env python3
"""Install, verify and upgrade the vendored ABSD kit in a product repository; migrate a v1 ABSD project.

Kit-owned paths (ABSD contract §1.1) are read-only in products, replaced wholesale on upgrade and listed with their
SHA-256 in absd/MANIFEST:
  - everything under absd/ except absd/MANIFEST itself and absd/lessons/inbox/** (ABSD repo only);
  - .claude/agents/*.md and .github/agents/*.agent.md (files directly in those directories).
Python bytecode (*.pyc) is never part of the kit, so running the tooling tests does not dirty a checkout.
Product-owned files are seeded from absd/templates/project/ (table SEEDS) only when missing and are never overwritten.

Subcommands:
  manifest    ABSD repo: write absd/MANIFEST — "# ABSD <absd/VERSION>", then "<sha256>  <path>" for every kit-owned
              file, sorted by path. Regenerate it whenever a kit file changes (kit CI runs check).
  check       verify every manifest entry (modified / missing) and report files under kit-owned paths that the
              manifest does not list (extra). Any difference fails.
  install     first installation into a product. Refuses when <to>/absd exists, when a v1 project is still in place
              (run migrate-v1 first so its context.md is kept), and when the kit checkout is not clean. Copies the kit
              files and the MANIFEST, seeds missing product-owned files, prints the next steps.
  upgrade     only between cycles: refuses while absd-project/working/cycle.md has a "Status: IN-PROGRESS" line,
              when the kit checkout is not clean, and when check finds local changes to kit paths — unless
              --accept-local-edits, which records them in absd-project/upgrade-local-edits.md (old → new hash, path)
              for the Manager to turn into enrichment proposals. Then copies the new kit files, deletes kit files the
              new manifest no longer lists, writes the new MANIFEST and seeds product-owned files whose template this
              kit version introduces.
  migrate-v1  moves a v1 project's working/context.md (or .claude/working/context.md) to absd-project/context.md and
              every entry of its sibling archive/ (or .claude/archive/) to absd-project/archive/<same name> — with
              `git mv` for tracked paths in a git work tree, plain moves otherwise. Never overwrites. Other v1 working
              files stay in place and are listed.

usage:
  absd_sync.py manifest [--root .]
  absd_sync.py check [--root .] [--json check.json] [--summary-md check.md]
  absd_sync.py install --from <kit checkout> --to <product repo>
  absd_sync.py upgrade --from <kit checkout> --to <product repo> [--accept-local-edits]
  absd_sync.py migrate-v1 [--root .]

Exit code: 0 pass, 1 check found differences, 2 usage/input error or refusal (a refusal changes nothing).
Python 3.9+, standard library only (migrate-v1 uses git when the root is a git work tree).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

KIT_DIR = "absd"
MANIFEST = "absd/MANIFEST"
VERSION = "absd/VERSION"
INBOX = "absd/lessons/inbox/"
TEMPLATES = "absd/templates/project"
AGENT_FILES = ((".claude/agents", ".md"), (".github/agents", ".agent.md"))   # (directory, suffix); not recursive
BYTECODE = ".pyc"     # written next to the tooling by test runs; never kit content
PROJECT_DIR = "absd-project"
CYCLE = "absd-project/working/cycle.md"
LOCAL_EDITS = "absd-project/upgrade-local-edits.md"

# Product-owned seeds (contract §1.1): template in absd/templates/project/ → path in the product.
# Copied only when the product path is missing; never overwritten.
SEEDS = (
    ("CLAUDE.md", "CLAUDE.md"),
    ("claude-settings.json", ".claude/settings.json"),
    ("copilot-instructions.md", ".github/copilot-instructions.md"),
    ("project.instructions.md", ".github/instructions/project.instructions.md"),
    ("context.md", "absd-project/context.md"),
    ("catalogue.md", "absd-project/catalogue.md"),
    ("design-system.md", "absd-project/design-system.md"),
    ("lessons.md", "absd-project/lessons.md"),
    ("TESTING.md", "docs/testing/TESTING.md"),
    ("ESCAPED-DEFECTS.md", "docs/testing/ESCAPED-DEFECTS.md"),
    ("EXPLORATORY.md", "docs/testing/EXPLORATORY.md"),
    ("EXTERNAL-FACTS.md", "docs/testing/EXTERNAL-FACTS.md"),
    ("untested-allowlist.txt", "tests/untested-allowlist.txt"),
)

# ABSD v1 layouts: (directory holding context.md, its sibling archive directory).
V1_LAYOUTS = (("working", "archive"), (".claude/working", ".claude/archive"))

HEADER = "# ABSD "
ENTRY = re.compile(r"^([0-9a-f]{64})  (\S.*)$")
IN_PROGRESS = re.compile(r"\bstatus\b[\s*_`]*:[\s*_`]*in[-_ ]progress\b", re.IGNORECASE)
CYCLE_DIR = re.compile(r"^(\d+)_")
IN_FLIGHT_CYCLE = re.compile(r"\bCycle\b[\s:#*]*C?(\d{1,4})\b", re.IGNORECASE)   # "## Cycle: 005", "Cycle C005"


class InputError(Exception):
    """Bad input or a refusal: exit code 2, nothing was changed."""


@dataclass
class Manifest:
    version: str
    files: dict = field(default_factory=dict)    # posix path -> sha256

    def render(self) -> str:
        lines = [HEADER + self.version] + [f"{self.files[path]}  {path}" for path in sorted(self.files)]
        return "\n".join(lines) + "\n"


@dataclass
class Differences:
    modified: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    extra: list = field(default_factory=list)    # under kit-owned paths, not in the manifest

    @property
    def clean(self) -> bool:
        return not (self.modified or self.missing or self.extra)

    def describe(self) -> str:
        groups = (("modified", self.modified), ("missing", self.missing), ("extra", self.extra))
        return "; ".join(f"{name}: {', '.join(paths)}" for name, paths in groups if paths)


# --- kit files and the manifest -----------------------------------------------------------------------------------

def local(root: str, path: str) -> str:
    """The file system path of a posix path relative to root."""
    return os.path.join(root, *path.split("/"))


def sha256_of(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_kit_owned(path: str) -> bool:
    """Contract §1.1 for a posix path relative to the repository root."""
    if path.endswith(BYTECODE):
        return False
    if path.startswith(KIT_DIR + "/"):
        return path != MANIFEST and not path.startswith(INBOX)
    directory, _, name = path.rpartition("/")
    return any(directory == agents and name.endswith(suffix) for agents, suffix in AGENT_FILES)


def is_safe_kit_path(path: str) -> bool:
    """A manifest path that stays inside the repository and names a kit-owned file."""
    parts = path.split("/")
    return "\\" not in path and not any(part in ("", ".", "..") for part in parts) and is_kit_owned(path)


def kit_files(root: str) -> list[str]:
    """Every kit-owned file present under root, sorted."""
    found = []
    for directory, _, names in os.walk(local(root, KIT_DIR)):
        relative = os.path.relpath(directory, root).replace(os.sep, "/")
        found += [f"{relative}/{name}" for name in names]
    for agents, _ in AGENT_FILES:
        directory = local(root, agents)
        if os.path.isdir(directory):
            found += [f"{agents}/{name}" for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))]
    return sorted(path for path in found if is_kit_owned(path))


def read_version(root: str) -> str:
    path = local(root, VERSION)
    if not os.path.isfile(path):
        raise InputError(f"{VERSION} not found in {root} — is --root the ABSD repository?")
    with open(path, encoding="utf-8") as f:
        version = f.read().strip()
    if len(version.splitlines()) != 1:
        raise InputError(f"{path} must hold exactly one version line, e.g. 2.0.0")
    return version


def parse_manifest(text: str, origin: str) -> Manifest:
    lines = text.splitlines()
    if not lines or not lines[0].startswith(HEADER) or not lines[0][len(HEADER):].strip():
        raise InputError(f"{origin}: the first line must be '{HEADER}<version>'")
    manifest = Manifest(lines[0][len(HEADER):].strip())
    for number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        match = ENTRY.match(line)
        if not match:
            raise InputError(f"{origin}:{number}: expected '<sha256>  <path>', got '{line}'")
        digest, path = match.groups()
        if not is_safe_kit_path(path):
            raise InputError(f"{origin}:{number}: '{path}' is not a kit-owned path")
        if path in manifest.files:
            raise InputError(f"{origin}:{number}: '{path}' is listed twice")
        manifest.files[path] = digest
    return manifest


def read_manifest(root: str) -> Manifest:
    path = local(root, MANIFEST)
    if not os.path.isfile(path):
        raise InputError(f"no {MANIFEST} in {root} — install the kit first, or in the ABSD repo run: absd_sync.py manifest")
    with open(path, encoding="utf-8") as f:
        return parse_manifest(f.read(), path)


def compare(root: str, manifest: Manifest) -> Differences:
    diff = Differences()
    for path, digest in sorted(manifest.files.items()):
        full = local(root, path)
        if not os.path.isfile(full):
            diff.missing.append(path)
        elif sha256_of(full) != digest:
            diff.modified.append(path)
    diff.extra = [path for path in kit_files(root) if path not in manifest.files]
    return diff


def require_clean_kit(kit: str) -> Manifest:
    """The kit checkout's manifest, after proving the checkout matches it."""
    manifest = read_manifest(kit)
    diff = compare(kit, manifest)
    if not diff.clean:
        raise InputError(f"kit checkout is not clean ({kit}): {diff.describe()} — use a clean checkout of a release, "
                         "or regenerate its manifest with: absd_sync.py manifest")
    return manifest


# --- writing into a product -----------------------------------------------------------------------------------------

def require_directory(path: str, option: str) -> None:
    if not os.path.isdir(path):
        raise InputError(f"{option} {path} is not a directory")


def copy_file(source: str, target: str) -> None:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copy2(source, target)


def copy_from(source_root: str, target_root: str, path: str) -> None:
    copy_file(local(source_root, path), local(target_root, path))


def seed(kit: str, target: str, manifest: Manifest, seeds: tuple[tuple[str, str], ...]
         ) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """Copy each template the kit ships to its product path unless that path exists.
    Returns (seeded paths, kept paths, (template, path) pairs the kit does not ship)."""
    seeded, kept, unshipped = [], [], []
    for template, destination in seeds:
        source = f"{TEMPLATES}/{template}"
        if source not in manifest.files:
            unshipped.append((source, destination))
        elif os.path.lexists(local(target, destination)):
            kept.append(destination)
        else:
            copy_file(local(kit, source), local(target, destination))
            seeded.append(destination)
    return seeded, kept, unshipped


def remove_empty_dirs(root: str, directory: str) -> None:
    """Remove `directory` (posix, relative to root) and then its parents while they are empty; never root itself."""
    parts = directory.split("/") if directory else []
    while parts:
        full = local(root, "/".join(parts))
        if not os.path.isdir(full) or os.listdir(full):
            return
        os.rmdir(full)
        parts.pop()


def cycle_in_progress(target: str) -> bool:
    path = local(target, CYCLE)
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8", errors="replace") as f:
        return any(IN_PROGRESS.search(line) for line in f)


def local_edit_rows(target: str, old: Manifest, diff: Differences) -> list[tuple[str, str, str, str]]:
    """(change, old hash, new hash, path) per local change to a kit path — computed before anything is replaced."""
    rows = [("modified", old.files[path], sha256_of(local(target, path)), path) for path in diff.modified]
    rows += [("deleted", old.files[path], "—", path) for path in diff.missing]
    rows += [("added", "—", sha256_of(local(target, path)), path) for path in diff.extra]
    return rows


def write_local_edits(target: str, old_version: str, new_version: str, rows: list[tuple[str, str, str, str]]) -> None:
    lines = [
        "# ABSD upgrade — local kit edits",
        "",
        f"The upgrade {old_version} → {new_version} on {datetime.date.today().isoformat()} found these local changes "
        "under kit-owned paths.",
        "Modified and deleted kit files were replaced by the new kit's versions; the edited content is in git history",
        "(the commit before the upgrade). Added files stay unless the new kit ships the same path; `absd_sync.py check`",
        "fails until they move out of kit-owned paths.",
        "Manager: turn every change worth keeping into an enrichment proposal (ABSD playbook ENR), then delete this file.",
        "",
        "| Change | Old hash (manifest) | New hash (local) | Path |",
        "|---|---|---|---|",
        *[f"| {change} | {old} | {new} | `{path}` |" for change, old, new, path in rows],
    ]
    path = local(target, LOCAL_EDITS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def print_paths(label: str, paths: list[str]) -> None:
    for path in paths:
        print(f"  {label:<8} {path}")


def print_steps(title: str, steps: list[str]) -> None:
    print(title)
    for number, step in enumerate(steps, start=1):
        print(f"  {number}. {step}")


# --- v1 migration ---------------------------------------------------------------------------------------------------

def run_git(root: str, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None


def is_git_work_tree(root: str) -> bool:
    result = run_git(root, "rev-parse", "--is-inside-work-tree")
    return result is not None and result.returncode == 0 and result.stdout.strip() == "true"


def is_tracked(root: str, path: str) -> bool:
    result = run_git(root, "--literal-pathspecs", "ls-files", "-z", "--", path)
    return result is not None and result.returncode == 0 and bool(result.stdout)


def find_v1(root: str) -> list[tuple[str, str]]:
    return [(working, archive) for working, archive in V1_LAYOUTS if os.path.isfile(local(root, f"{working}/context.md"))]


def move(root: str, source: str, destination: str, use_git: bool) -> str:
    os.makedirs(os.path.dirname(local(root, destination)), exist_ok=True)
    if use_git and is_tracked(root, source):
        result = run_git(root, "mv", "--", source, destination)
        if result is None or result.returncode != 0:
            raise InputError(f"git mv {source} {destination} failed: {result.stderr.strip() if result else 'no git'}")
        return "git mv"
    shutil.move(local(root, source), local(root, destination))
    return "moved"


def names_in(root: str, directory: str) -> list[str]:
    """The sorted entry names of a directory; none when it does not exist."""
    full = local(root, directory)
    return sorted(os.listdir(full)) if os.path.isdir(full) else []


def next_cycle(root: str, in_flight: int = 0) -> str:
    """The cycle id after the highest archived NNN_ directory and the in-flight v1 cycle (if any)."""
    numbers = [0, in_flight]
    for name in names_in(root, f"{PROJECT_DIR}/archive"):
        match = CYCLE_DIR.match(name)
        if match:
            numbers.append(int(match.group(1)))
    return f"C{max(numbers) + 1:03d}"


def in_flight_cycle(root: str, paths: list[str]) -> int:
    """The highest cycle number the v1 working files left in place declare ("## Cycle: 005"), or 0."""
    found = 0
    for path in paths:
        full = local(root, path)
        files = [full] if os.path.isfile(full) else [os.path.join(d, n) for d, _, ns in os.walk(full) for n in ns]
        for name in files:
            if not name.endswith(".md"):
                continue
            with open(name, encoding="utf-8", errors="replace") as f:
                found = max([found] + [int(n) for n in IN_FLIGHT_CYCLE.findall(f.read())])
    return found


# --- subcommands ----------------------------------------------------------------------------------------------------

def cmd_manifest(args: argparse.Namespace) -> int:
    manifest = Manifest(read_version(args.root))
    for path in kit_files(args.root):
        manifest.files[path] = sha256_of(local(args.root, path))
    with open(local(args.root, MANIFEST), "w", encoding="utf-8", newline="\n") as f:
        f.write(manifest.render())
    print(f"Wrote {MANIFEST}: ABSD {manifest.version}, {len(manifest.files)} kit files.")
    return 0


def check_summary(root: str, manifest: Manifest, diff: Differences) -> str:
    lines = [
        f"### ABSD kit check — {'passed' if diff.clean else 'FAILED'}",
        f"`{root}` · ABSD {manifest.version} · {len(manifest.files)} kit files in the manifest · "
        f"{len(diff.modified)} modified · {len(diff.missing)} missing · {len(diff.extra)} extra",
    ]
    for heading, paths in (("Modified", diff.modified), ("Missing", diff.missing), ("Extra — not in the manifest", diff.extra)):
        if paths:
            lines += ["", f"**{heading} ({len(paths)})**", *[f"- `{path}`" for path in paths]]
    return "\n".join(lines) + "\n"


def cmd_check(args: argparse.Namespace) -> int:
    manifest = read_manifest(args.root)
    diff = compare(args.root, manifest)
    summary = check_summary(args.root, manifest, diff)
    print(summary)
    for title, paths in (("Kit file modified", diff.modified), ("Kit file missing", diff.missing),
                         ("Not in the kit manifest", diff.extra)):
        for path in paths:
            print(f"::error title={title}::{path}")
    if not diff.clean:
        print("::notice::Kit paths are read-only in a product: keep product-specific text in product-owned files and "
              "propose kit changes upstream (ABSD playbook ENR). In the ABSD repo, regenerate: absd_sync.py manifest")
    for target in filter(None, (args.summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(summary + "\n")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as out:
            json.dump({"root": args.root, "version": manifest.version, "files": len(manifest.files), "passed": diff.clean,
                       "modified": diff.modified, "missing": diff.missing, "extra": diff.extra}, out, indent=2)
    return 0 if diff.clean else 1


def cmd_install(args: argparse.Namespace) -> int:
    kit, target = args.source, args.target
    require_directory(target, "--to")
    if os.path.lexists(local(target, KIT_DIR)):
        raise InputError(f"{local(target, KIT_DIR)} already exists — the kit is installed; use upgrade")
    v1 = find_v1(target)
    if v1:
        raise InputError(f"v1 ABSD project found ({v1[0][0]}/context.md) — run migrate-v1 first so its context.md "
                         "and archive are kept, then install")
    manifest = require_clean_kit(kit)
    replaced = [path for path in sorted(manifest.files) if os.path.lexists(local(target, path))]
    for path in sorted(manifest.files):
        copy_from(kit, target, path)
    copy_from(kit, target, MANIFEST)
    seeded, kept, unshipped = seed(kit, target, manifest, SEEDS)
    leftover = [path for path in kit_files(target) if path not in manifest.files]

    print(f"Installed ABSD {manifest.version} from {kit} into {target}:")
    print_paths("copied", sorted(manifest.files) + [MANIFEST])
    print_paths("seeded", seeded)
    print_paths("kept", kept)
    for path in replaced:
        print(f"::warning title=Replaced::{path} existed and now holds the kit's version (git history has the old one)")
    for template, destination in unshipped:
        print(f"::warning title=Template not in this kit::{template} — {destination} not seeded")
    for path in leftover:
        print(f"::warning title=Not in the kit manifest::{path} sits under a kit-owned path — move it out, or check fails")
    print_steps("Next steps:", [
        f'Commit the installed kit and the seeded files as a kit-sync commit: git add -A && git commit -m "absd: install '
        f'ABSD {manifest.version}" --trailer "ABSD-Sync: install {manifest.version}" (ownership_check accepts it).',
        "Start the Manager as the main thread: `claude --agent manager` (the seeded .claude/settings.json makes it "
        "the default agent).",
        "Ask it to run Bootstrap (Mode B: the Foundation cycle, or a Foundation-delta for a migrated v1 project); "
        f'it records "ABSD version: {manifest.version}" in absd-project/context.md.',
    ])
    return 0


def cmd_upgrade(args: argparse.Namespace) -> int:
    kit, target = args.source, args.target
    require_directory(target, "--to")
    old = read_manifest(target)
    if cycle_in_progress(target):
        raise InputError(f"{CYCLE} says Status: IN-PROGRESS — upgrade only between cycles: finish (Gate 3, archive) "
                         "or park the cycle first")
    new = require_clean_kit(kit)
    diff = compare(target, old)
    if not diff.clean and not args.accept_local_edits:
        raise InputError(f"kit files were edited locally in {target} ({diff.describe()}) — the upgrade would replace "
                         f"them. Rerun with --accept-local-edits to record them in {LOCAL_EDITS} for enrichment proposals")
    edits = local_edit_rows(target, old, diff)

    added = sorted(set(new.files) - set(old.files))
    removed = sorted(set(old.files) - set(new.files))
    updated = sorted(path for path in set(new.files) & set(old.files) if new.files[path] != old.files[path])
    for path in sorted(new.files):
        current = local(target, path)
        if not os.path.isfile(current) or sha256_of(current) != new.files[path]:
            copy_from(kit, target, path)
    for path in removed:
        if os.path.lexists(local(target, path)):
            os.remove(local(target, path))
            remove_empty_dirs(target, path.rpartition("/")[0])
    copy_from(kit, target, MANIFEST)
    introduced = tuple((template, destination) for template, destination in SEEDS
                       if f"{TEMPLATES}/{template}" not in old.files)
    seeded, kept, _ = seed(kit, target, new, introduced)
    if edits:
        write_local_edits(target, old.version, new.version, edits)
    leftover = [path for path in kit_files(target) if path not in new.files]

    print(f"Upgraded ABSD {old.version} → {new.version} in {target}: "
          f"{len(added)} added, {len(updated)} updated, {len(removed)} removed.")
    print_paths("added", added)
    print_paths("updated", updated)
    print_paths("removed", removed)
    print_paths("seeded", seeded)
    print_paths("kept", kept)
    if edits:
        print(f"::warning title=Local kit edits::{len(edits)} local changes to kit paths recorded in {LOCAL_EDITS}")
    for path in leftover:
        print(f"::warning title=Not in the kit manifest::{path} sits under a kit-owned path — move it out, or check fails")
    steps = [
        f"Read absd/CHANGELOG.md for every version after {old.version} up to {new.version}.",
        f'Update "ABSD version" in {PROJECT_DIR}/context.md to {new.version}.',
        "Tester baseline against the new and changed rules → gap list → DEBT items or a Foundation-delta cycle (Mode U).",
    ]
    if edits:
        steps.append(f"Manager: turn {LOCAL_EDITS} into enrichment proposals (ABSD playbook ENR).")
    steps.append(f'Commit the upgrade as a kit-sync commit: git add -A && git commit -m "absd: upgrade ABSD {new.version}" '
                 f'--trailer "ABSD-Sync: upgrade {new.version}".')
    print_steps("Next steps:", steps)
    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    root = args.root
    require_directory(root, "--root")
    layouts = find_v1(root)
    if not layouts:
        raise InputError(f"no v1 ABSD project in {root}: neither working/context.md nor .claude/working/context.md exists")
    if len(layouts) > 1:
        raise InputError("both working/context.md and .claude/working/context.md exist — move the stale one out of the "
                         "way, then rerun")
    working, archive = layouts[0]
    moves = [(f"{working}/context.md", f"{PROJECT_DIR}/context.md")]
    moves += [(f"{archive}/{name}", f"{PROJECT_DIR}/archive/{name}") for name in names_in(root, archive)]
    taken = [destination for _, destination in moves if os.path.lexists(local(root, destination))]
    if taken:
        raise InputError(f"migrate-v1 never overwrites — already exists: {', '.join(taken)}")

    use_git = is_git_work_tree(root)
    print(f"Migrating the v1 ABSD project in {root} ({working}/ layout):")
    for source, destination in moves:
        how = move(root, source, destination, use_git)
        print(f"  {how:<8} {source} → {destination}")
    remove_empty_dirs(root, archive)
    remove_empty_dirs(root, working)
    left = [f"{working}/{name}" + ("/" if os.path.isdir(local(root, f"{working}/{name}")) else "")
            for name in names_in(root, working)]
    in_flight = in_flight_cycle(root, left)
    if left:
        print("Left in place — v1 working files; the Foundation-delta cycle decides what becomes of them:")
        print_paths("left", left)
    print_steps("Follow-up for the Manager (ABSD contract Mode B, v1 migration recipe):", [
        "Install the v2 kit if it is not installed: absd_sync.py install --from <kit> --to <this repo> "
        "(keeps the migrated context.md).",
        f"Restructure {PROJECT_DIR}/context.md into the v2 sections of {TEMPLATES}/context.md and record "
        '"ABSD version".',
        f"CLAUDE.md: keep the product text, replace the v1 pipeline rules with the imports from {TEMPLATES}/CLAUDE.md.",
        "Run the first v2 cycle as a Foundation-delta (Mode B); v1 production source moves to the Source Layout it "
        "declares.",
        *([f"The v1 working files describe an in-flight cycle C{in_flight:03d}: park it (Mode P — git mv them into "
            f"{PROJECT_DIR}/archive/{in_flight:03d}_<date>_<slug>_parked/) and redo its intake as a new cycle after the "
            "Foundation-delta."] if in_flight else []),
        f"Continue cycle numbering at {next_cycle(root, in_flight)} — archived cycles keep their numbers.",
        'Commit the moves as a kit-sync commit (`git mv` ones are already staged): git add -A && git commit -m '
        '"absd: migrate v1 project" --trailer "ABSD-Sync: migrate-v1".',
    ])
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")
    manifest = commands.add_parser("manifest", help="ABSD repo: write absd/MANIFEST")
    manifest.add_argument("--root", default=".", help="the ABSD repository (default: current directory)")
    check = commands.add_parser("check", help="verify kit files against absd/MANIFEST")
    check.add_argument("--root", default=".", help="the repository to check (default: current directory)")
    check.add_argument("--json", dest="json_out", help="write the result as JSON")
    check.add_argument("--summary-md", help="write the Markdown summary to this file (also appended to $GITHUB_STEP_SUMMARY)")
    install = commands.add_parser("install", help="first installation of the kit into a product")
    upgrade = commands.add_parser("upgrade", help="replace the installed kit with a newer one, between cycles")
    for sub in (install, upgrade):
        sub.add_argument("--from", dest="source", required=True, help="a clean checkout of the ABSD kit (a release tag)")
        sub.add_argument("--to", dest="target", required=True, help="the product repository")
    upgrade.add_argument("--accept-local-edits", action="store_true",
                         help=f"replace locally edited kit files and record them in {LOCAL_EDITS}")
    migrate = commands.add_parser("migrate-v1", help="move a v1 project's context.md and archive to absd-project/")
    migrate.add_argument("--root", default=".", help="the product repository (default: current directory)")
    args = parser.parse_args(argv)

    handlers = {"manifest": cmd_manifest, "check": cmd_check, "install": cmd_install, "upgrade": cmd_upgrade,
                "migrate-v1": cmd_migrate}
    try:
        return handlers[args.command](args)
    except (InputError, OSError) as error:
        print(f"::error::{error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
