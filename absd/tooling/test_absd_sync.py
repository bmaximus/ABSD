"""Tests for absd_sync.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import absd_sync  # noqa: E402

# A fake ABSD repository at 2.0.0: kit-owned files plus files the ABSD repo has but never ships.
KIT = {
    "absd/VERSION": "2.0.0\n",
    "absd/RULES.md": "# Rules 2.0\n",
    "absd/CHANGELOG.md": "# Changelog\n## 2.0.0\n",
    "absd/playbook/testing/oracles.md": "**ORACLE-1** — Oracles come from the specification.\n",
    "absd/playbook/process/old-topic.md": "retired in 2.1.0\n",
    "absd/tooling/coverage_gate.py": "# gate\n",
    "absd/lessons/LEDGER.md": "# Ledger\n",
    "absd/templates/project/CLAUDE.md": "@absd/RULES.md\n@absd-project/context.md\n",
    "absd/templates/project/claude-settings.json": '{"agent": "manager"}\n',
    "absd/templates/project/context.md": "# Context template 2.0\n",
    "absd/templates/project/TESTING.md": "# Testing template\n",
    "absd/templates/project/untested-allowlist.txt": "# <unit>  # <reason>\n",
    ".claude/agents/manager.md": "manager 2.0\n",
    ".claude/agents/tester.md": "tester 2.0\n",
    ".github/agents/Manager.agent.md": "Manager mirror 2.0\n",
    # in the ABSD repo, not kit-owned:
    "absd/lessons/inbox/shop-2026-10-01.md": "a product's proposal\n",
    "absd/tooling/__pycache__/coverage_gate.cpython-313.pyc": "bytecode",
    "README.md": "What ABSD is\n",
    "CLAUDE.md": "Maintainer instructions\n",
    ".github/copilot-instructions.md": "Maintainer Copilot instructions\n",
    ".github/workflows/kit.yml": "jobs: {}\n",
    ".claude/agents/README.txt": "not an agent file\n",
    ".claude/agents/drafts/analyst.md": "not directly in .claude/agents\n",
    ".github/agents/Manager.md": "not a mirror (no .agent.md)\n",
}
KIT_OWNED = sorted([
    "absd/VERSION", "absd/RULES.md", "absd/CHANGELOG.md", "absd/playbook/testing/oracles.md",
    "absd/playbook/process/old-topic.md", "absd/tooling/coverage_gate.py", "absd/lessons/LEDGER.md",
    "absd/templates/project/CLAUDE.md", "absd/templates/project/claude-settings.json",
    "absd/templates/project/context.md", "absd/templates/project/TESTING.md",
    "absd/templates/project/untested-allowlist.txt",
    ".claude/agents/manager.md", ".claude/agents/tester.md", ".github/agents/Manager.agent.md",
])
# 2.1.0 changes RULES.md and the context template, adds a playbook file and two templates, drops two kit files.
KIT_NEXT_CHANGES = {
    "absd/VERSION": "2.1.0\n",
    "absd/RULES.md": "# Rules 2.1\n",
    "absd/playbook/testing/new-topic.md": "**VAR-9** — new rule\n",
    "absd/templates/project/context.md": "# Context template 2.1\n",
    "absd/templates/project/EXPLORATORY.md": "# Exploratory template\n",
    "absd/templates/project/catalogue.md": "# Catalogue template\n",
}
KIT_NEXT_REMOVED = ("absd/playbook/process/old-topic.md", ".claude/agents/tester.md")

PRODUCT = {
    "README.md": "# Shop\n",
    "CLAUDE.md": "# Shop\nProduct notes.\n",
    "src/app.py": "print('shop')\n",
}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SyncTestCase(unittest.TestCase):
    """Temporary kit and product directories; git sees no repository above the temp root."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = self.dir.name
        gitconfig = write(os.path.join(self.root, "gitconfig"), "")
        env = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": gitconfig, "GIT_CONFIG_NOSYSTEM": "1",
                                           "GIT_CEILING_DIRECTORIES": self.root})
        env.start()
        self.addCleanup(env.stop)
        for name in ("GITHUB_STEP_SUMMARY", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            os.environ.pop(name, None)

    # --- helpers ----------------------------------------------------------------------------------------------

    def run_sync(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = absd_sync.main(list(args))
        return code, out.getvalue()

    def tree(self, name, files):
        root = os.path.join(self.root, name)
        os.makedirs(root, exist_ok=True)
        for path, text in files.items():
            write(os.path.join(root, *path.split("/")), text)
        return root

    def make_kit(self, name="kit", changes=None, removed=()):
        files = {path: text for path, text in {**KIT, **(changes or {})}.items() if path not in removed}
        kit = self.tree(name, files)
        code, out = self.run_sync("manifest", "--root", kit)
        self.assertEqual(code, 0, out)
        return kit

    def make_next_kit(self):
        return self.make_kit("kit-2.1.0", KIT_NEXT_CHANGES, KIT_NEXT_REMOVED)

    def installed_product(self, name="product", kit=None):
        kit = kit or self.make_kit("kit-2.0.0")
        product = self.tree(name, PRODUCT)
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 0, out)
        return kit, product

    def snapshot(self, root):
        """{posix path: bytes} of every file under root."""
        files = {}
        for directory, _, names in os.walk(root):
            for name in names:
                full = os.path.join(directory, name)
                with open(full, "rb") as f:
                    files[os.path.relpath(full, root).replace(os.sep, "/")] = f.read()
        return files


class ManifestTests(SyncTestCase):
    def test_kit_owned_paths(self):
        expected = {
            "absd/RULES.md": True,
            "absd/templates/project/context.md": True,
            "absd/MANIFEST": False,                          # the manifest does not list itself
            "absd/lessons/inbox/shop-2026-10-01.md": False,  # ABSD repo only
            "absd/lessons/LEDGER.md": True,
            "absd/tooling/__pycache__/gate.cpython-313.pyc": False,
            "absd/tooling/gate.pyc": False,
            ".claude/agents/manager.md": True,
            ".claude/agents/drafts/manager.md": False,       # only files directly in .claude/agents
            ".claude/agents/notes.txt": False,
            ".github/agents/Manager.agent.md": True,
            ".github/agents/Manager.md": False,
            ".github/copilot-instructions.md": False,
            "CLAUDE.md": False,
            "absdx/RULES.md": False,
        }
        self.assertEqual({path: absd_sync.is_kit_owned(path) for path in expected}, expected)

    def test_manifest_lists_every_kit_owned_file_with_its_hash_sorted_by_path(self):
        kit = self.make_kit()
        expected = "# ABSD 2.0.0\n" + "".join(f"{sha(KIT[path])}  {path}\n" for path in KIT_OWNED)
        self.assertEqual(read(os.path.join(kit, "absd", "MANIFEST")), expected)

    def test_manifest_is_deterministic_and_never_lists_itself(self):
        kit = self.make_kit()
        first = read(os.path.join(kit, "absd", "MANIFEST"))
        code, out = self.run_sync("manifest", "--root", kit)   # MANIFEST now exists on disk
        self.assertEqual(code, 0, out)
        self.assertIn("ABSD 2.0.0, 15 kit files", out)
        self.assertEqual(read(os.path.join(kit, "absd", "MANIFEST")), first)
        other = self.tree("same-kit-other-order", dict(reversed(list(KIT.items()))))
        self.run_sync("manifest", "--root", other)
        self.assertEqual(read(os.path.join(other, "absd", "MANIFEST")), first)

    def test_manifest_needs_one_version_line(self):
        for name, files in (("no-version", {"absd/RULES.md": "x\n"}),
                            ("empty-version", {"absd/VERSION": " \n"}),
                            ("two-versions", {"absd/VERSION": "2.0.0\n2.1.0\n"})):
            with self.subTest(name):
                kit = self.tree(name, files)
                code, out = self.run_sync("manifest", "--root", kit)
                self.assertEqual(code, 2, out)
                self.assertIn("absd/VERSION", out)
                if name == "no-version":
                    self.assertIn("is --root the ABSD repository?", out)
                self.assertFalse(os.path.exists(os.path.join(kit, "absd", "MANIFEST")))


class CheckTests(SyncTestCase):
    def test_clean_checkout_passes(self):
        kit = self.make_kit()
        out_json = os.path.join(self.root, "check.json")
        code, out = self.run_sync("check", "--root", kit, "--json", out_json)
        self.assertEqual(code, 0, out)
        self.assertIn("ABSD kit check — passed", out)
        with open(out_json, encoding="utf-8") as f:
            self.assertEqual(json.load(f), {"root": kit, "version": "2.0.0", "files": 15, "passed": True,
                                            "modified": [], "missing": [], "extra": []})

    def test_modified_missing_and_extra_kit_files_fail(self):
        kit = self.make_kit()
        write(os.path.join(kit, "absd", "RULES.md"), "# Rules, locally edited\n")
        os.remove(os.path.join(kit, ".claude", "agents", "tester.md"))
        write(os.path.join(kit, "absd", "playbook", "testing", "local.md"), "local rule\n")
        write(os.path.join(kit, ".github", "agents", "Reviewer.agent.md"), "local mirror\n")
        # not kit-owned, so never "extra":
        write(os.path.join(kit, "absd", "lessons", "inbox", "new-2026-10-02.md"), "proposal\n")
        write(os.path.join(kit, ".claude", "agents", "drafts", "x.md"), "draft\n")
        write(os.path.join(kit, "README.md"), "edited readme\n")
        write(os.path.join(kit, "absd", "tooling", "__pycache__", "absd_sync.cpython-313.pyc"), "bytecode")
        out_json = os.path.join(self.root, "check.json")
        code, out = self.run_sync("check", "--root", kit, "--json", out_json)
        self.assertEqual(code, 1, out)
        self.assertIn("ABSD kit check — FAILED", out)
        self.assertIn("::error title=Kit file modified::absd/RULES.md", out)
        self.assertIn("::error title=Kit file missing::.claude/agents/tester.md", out)
        self.assertIn("::error title=Not in the kit manifest::absd/playbook/testing/local.md", out)
        with open(out_json, encoding="utf-8") as f:
            data = json.load(f)
        self.assertFalse(data["passed"])
        self.assertEqual(data["modified"], ["absd/RULES.md"])
        self.assertEqual(data["missing"], [".claude/agents/tester.md"])
        self.assertEqual(data["extra"], [".github/agents/Reviewer.agent.md", "absd/playbook/testing/local.md"])

    def test_summary_goes_to_the_file_and_the_step_summary(self):
        kit = self.make_kit()
        write(os.path.join(kit, "absd", "RULES.md"), "edited\n")
        summary = os.path.join(self.root, "check.md")
        step = os.path.join(self.root, "step.md")
        with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": step}):
            code, out = self.run_sync("check", "--root", kit, "--summary-md", summary)
        self.assertEqual(code, 1, out)
        for path in (summary, step):
            self.assertIn("**Modified (1)**\n- `absd/RULES.md`", read(path))

    def test_no_manifest_is_an_input_error(self):
        product = self.tree("product", PRODUCT)
        code, out = self.run_sync("check", "--root", product)
        self.assertEqual(code, 2)
        self.assertIn("no absd/MANIFEST", out)

    def test_malformed_or_unsafe_manifest_is_an_input_error(self):
        digest = sha("x")
        for name, text in (
                ("no header", f"{digest}  absd/RULES.md\n"),
                ("no version", "# ABSD \n"),
                ("one space", f"# ABSD 2.0.0\n{digest} absd/RULES.md\n"),
                ("short hash", f"# ABSD 2.0.0\n{digest[:10]}  absd/RULES.md\n"),
                ("not kit-owned", f"# ABSD 2.0.0\n{digest}  src/app.py\n"),
                ("parent segment", f"# ABSD 2.0.0\n{digest}  absd/../../outside.md\n"),
                ("dot segment", f"# ABSD 2.0.0\n{digest}  absd/./RULES.md\n"),
                ("absolute", f"# ABSD 2.0.0\n{digest}  /absd/RULES.md\n"),
                ("empty segment", f"# ABSD 2.0.0\n{digest}  absd//RULES.md\n"),
                ("trailing slash", f"# ABSD 2.0.0\n{digest}  absd/playbook/\n"),
                ("backslash", f"# ABSD 2.0.0\n{digest}  absd/..\\..\\outside.md\n"),
                ("listed twice", f"# ABSD 2.0.0\n{digest}  absd/RULES.md\n{digest}  absd/RULES.md\n")):
            with self.subTest(name):
                repo = self.tree(name.replace(" ", "-"), {"absd/MANIFEST": text, "absd/RULES.md": "x"})
                code, out = self.run_sync("check", "--root", repo)
                self.assertEqual(code, 2, out)
                self.assertIn("::error::", out)

    def test_blank_lines_in_the_manifest_are_ignored(self):
        repo = self.tree("repo", {"absd/MANIFEST": f"# ABSD 2.0.0\n\n{sha('x')}  absd/RULES.md\n\n", "absd/RULES.md": "x"})
        code, out = self.run_sync("check", "--root", repo)
        self.assertEqual(code, 0, out)


class InstallTests(SyncTestCase):
    def test_installs_the_kit_and_seeds_missing_product_files(self):
        kit = self.make_kit()
        product = self.tree("product", PRODUCT)
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 0, out)
        files = self.snapshot(product)
        for path in KIT_OWNED:
            self.assertEqual(files[path], KIT[path].encode(), path)
        self.assertEqual(files["absd/MANIFEST"], read(os.path.join(kit, "absd", "MANIFEST")).encode())
        seeds = {
            ".claude/settings.json": "absd/templates/project/claude-settings.json",
            "absd-project/context.md": "absd/templates/project/context.md",
            "docs/testing/TESTING.md": "absd/templates/project/TESTING.md",
            "tests/untested-allowlist.txt": "absd/templates/project/untested-allowlist.txt",
        }
        for destination, template in seeds.items():
            self.assertEqual(files[destination], KIT[template].encode(), destination)
            self.assertIn(f"seeded   {destination}", out)
        # never shipped: the inbox, maintainer files, non-agent files; product files untouched
        expected = set(KIT_OWNED) | {"absd/MANIFEST"} | set(seeds) | set(PRODUCT)
        self.assertEqual(set(files), expected)
        for path, text in PRODUCT.items():
            self.assertEqual(files[path], text.encode(), path)
        self.assertIn("kept     CLAUDE.md", out)
        self.assertIn("copied   absd/RULES.md", out)
        self.assertIn("::warning title=Template not in this kit::absd/templates/project/catalogue.md — "
                      "absd-project/catalogue.md not seeded", out)
        self.assertIn("claude --agent manager", out)
        self.assertIn("Bootstrap", out)
        code, out = self.run_sync("check", "--root", product)
        self.assertEqual(code, 0, out)

    def test_seeds_claude_md_when_the_product_has_none(self):
        kit = self.make_kit()
        product = self.tree("product", {"src/app.py": "print('shop')\n"})
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 0, out)
        self.assertEqual(read(os.path.join(product, "CLAUDE.md")), KIT["absd/templates/project/CLAUDE.md"])

    def test_seeding_never_overwrites_product_files(self):
        kit = self.make_kit()
        mine = {".claude/settings.json": '{"agent": "manager", "mine": true}\n',
                "absd-project/context.md": "# Context — Shop (already written)\n",
                "docs/testing/TESTING.md": "# Our testing\n"}
        product = self.tree("product", {**PRODUCT, **mine})
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 0, out)
        for path, text in mine.items():
            self.assertEqual(read(os.path.join(product, *path.split("/"))), text, path)
            self.assertIn(f"kept     {path}", out)

    def test_existing_agent_files_are_replaced_with_a_warning_and_others_flagged(self):
        kit = self.make_kit()
        product = self.tree("product", {**PRODUCT, ".claude/agents/manager.md": "v1 manager\n",
                                        ".claude/agents/reviewer.md": "our own agent\n"})
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 0, out)
        self.assertEqual(read(os.path.join(product, ".claude", "agents", "manager.md")), KIT[".claude/agents/manager.md"])
        self.assertIn("::warning title=Replaced::.claude/agents/manager.md", out)
        self.assertNotIn("::warning title=Replaced::.claude/agents/tester.md", out)
        self.assertEqual(read(os.path.join(product, ".claude", "agents", "reviewer.md")), "our own agent\n")
        self.assertIn("::warning title=Not in the kit manifest::.claude/agents/reviewer.md", out)

    def test_refuses_when_the_kit_is_already_installed(self):
        kit = self.make_kit()
        product = self.tree("product", {**PRODUCT, "absd/RULES.md": "installed earlier\n"})
        before = self.snapshot(product)
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 2, out)
        self.assertIn("already exists", out)
        self.assertEqual(self.snapshot(product), before)

    def test_refuses_a_kit_checkout_that_is_not_clean(self):
        for name, change in (("modified", lambda kit: write(os.path.join(kit, "absd", "RULES.md"), "edited\n")),
                             ("missing", lambda kit: os.remove(os.path.join(kit, "absd", "CHANGELOG.md"))),
                             ("extra", lambda kit: write(os.path.join(kit, "absd", "playbook", "x.md"), "new\n"))):
            with self.subTest(name):
                kit = self.make_kit(f"kit-{name}")
                change(kit)
                product = self.tree(f"product-{name}", PRODUCT)
                code, out = self.run_sync("install", "--from", kit, "--to", product)
                self.assertEqual(code, 2, out)
                self.assertIn("kit checkout is not clean", out)
                self.assertIn(name, out)
                self.assertEqual(set(self.snapshot(product)), set(PRODUCT))

    def test_refuses_a_kit_without_a_manifest(self):
        kit = self.tree("kit", KIT)
        product = self.tree("product", PRODUCT)
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 2, out)
        self.assertIn("no absd/MANIFEST", out)

    def test_refuses_while_a_v1_project_is_in_place(self):
        kit = self.make_kit()
        product = self.tree("product", {**PRODUCT, ".claude/working/context.md": "# v1 context\n"})
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 2, out)
        self.assertIn("migrate-v1", out)
        self.assertFalse(os.path.exists(os.path.join(product, "absd")))

    def test_target_must_be_a_directory(self):
        kit = self.make_kit()
        code, out = self.run_sync("install", "--from", kit, "--to", os.path.join(self.root, "nowhere"))
        self.assertEqual(code, 2, out)


class UpgradeTests(SyncTestCase):
    def upgrade(self, product, kit, *flags):
        return self.run_sync("upgrade", "--from", kit, "--to", product, *flags)

    def test_upgrade_replaces_kit_files_removes_dropped_ones_and_leaves_product_files_alone(self):
        _, product = self.installed_product()
        # product work after install: the Manager wrote context.md, the Tester removed a seed it does not use
        write(os.path.join(product, "absd-project", "context.md"), "# Context — Shop\n")
        os.remove(os.path.join(product, "docs", "testing", "TESTING.md"))
        write(os.path.join(product, "absd-project", "catalogue.md"), "# Catalogue — Shop\n")
        write(os.path.join(product, "absd-project", "working", "cycle.md"), "Cycle: C003 | Mode: F | Status: COMPLETE\n")
        product_files = {path: data for path, data in self.snapshot(product).items()
                         if not absd_sync.is_kit_owned(path) and path != "absd/MANIFEST"}
        kit = self.make_next_kit()

        code, out = self.upgrade(product, kit)
        self.assertEqual(code, 0, out)
        files = self.snapshot(product)
        self.assertEqual(files["absd/RULES.md"], b"# Rules 2.1\n")
        self.assertEqual(files["absd/playbook/testing/new-topic.md"], KIT_NEXT_CHANGES["absd/playbook/testing/new-topic.md"].encode())
        self.assertEqual(files["absd/MANIFEST"], read(os.path.join(kit, "absd", "MANIFEST")).encode())
        for path in KIT_NEXT_REMOVED:
            self.assertNotIn(path, files)
        self.assertFalse(os.path.exists(os.path.join(product, "absd", "playbook", "process")))  # emptied, removed
        self.assertTrue(os.path.isdir(os.path.join(product, ".claude", "agents")))
        # product-owned files: unchanged, never re-seeded; only a template new in 2.1.0 is seeded where missing
        self.assertEqual(files["docs/testing/EXPLORATORY.md"], b"# Exploratory template\n")
        for path, data in product_files.items():
            self.assertEqual(files[path], data, path)
        self.assertNotIn("docs/testing/TESTING.md", files)
        self.assertEqual(set(files) - set(product_files) - {"docs/testing/EXPLORATORY.md", "absd/MANIFEST"},
                         {path for path in files if absd_sync.is_kit_owned(path)})
        self.assertFalse(os.path.exists(os.path.join(product, "absd-project", "upgrade-local-edits.md")))
        self.assertIn("Upgraded ABSD 2.0.0 → 2.1.0", out)
        self.assertIn("3 added, 3 updated, 2 removed", out)
        self.assertIn("seeded   docs/testing/EXPLORATORY.md", out)
        self.assertIn("kept     absd-project/catalogue.md", out)
        self.assertIn("removed  .claude/agents/tester.md", out)
        self.assertIn("CHANGELOG", out)
        self.assertIn('"ABSD version" in absd-project/context.md to 2.1.0', out)
        code, out = self.run_sync("check", "--root", product)
        self.assertEqual(code, 0, out)

    def test_directories_emptied_by_removed_kit_files_are_pruned_up_the_tree(self):
        nested = "absd/playbook/legacy/deep/old.md"
        kit = self.make_kit("kit-nested", {nested: "old rule\n"})
        _, product = self.installed_product("product-nested", kit)
        self.assertTrue(os.path.isfile(os.path.join(product, *nested.split("/"))))
        code, out = self.upgrade(product, self.make_kit("kit-nested-next", {"absd/VERSION": "2.1.0\n"}))
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.exists(os.path.join(product, "absd", "playbook", "legacy")))
        self.assertTrue(os.path.isdir(os.path.join(product, "absd", "playbook", "testing")))

    def test_refuses_during_an_active_cycle(self):
        _, product = self.installed_product()
        kit = self.make_next_kit()
        for line in ("Cycle: C004 | Mode: F | Status: IN-PROGRESS | Date: 2026-10-01",
                     "status: in-progress",
                     "**Status:** IN-PROGRESS"):
            with self.subTest(line):
                write(os.path.join(product, "absd-project", "working", "cycle.md"), f"# Cycle\n{line}\n")
                before = self.snapshot(product)
                code, out = self.upgrade(product, kit)
                self.assertEqual(code, 2, out)
                self.assertIn("between cycles", out)
                self.assertEqual(self.snapshot(product), before)

    def test_allowed_when_the_cycle_is_complete(self):
        _, product = self.installed_product()
        write(os.path.join(product, "absd-project", "working", "cycle.md"),
              "# Cycle\nCycle: C004 | Mode: F | Status: COMPLETE | Date: 2026-10-01\n| Gate 3 | 1 | PASS |\n")
        code, out = self.upgrade(product, self.make_next_kit())
        self.assertEqual(code, 0, out)

    def test_refuses_local_edits_to_kit_paths(self):
        kit = self.make_next_kit()
        kit_old = self.make_kit("kit-2.0.0")
        edits = {
            "modified": lambda product: write(os.path.join(product, "absd", "RULES.md"), "# Rules, our edit\n"),
            "missing": lambda product: os.remove(os.path.join(product, "absd", "CHANGELOG.md")),
            "extra": lambda product: write(os.path.join(product, ".claude", "agents", "reviewer.md"), "ours\n"),
        }
        for name, edit in edits.items():
            with self.subTest(name):
                _, product = self.installed_product(f"product-{name}", kit_old)
                edit(product)
                before = self.snapshot(product)
                code, out = self.upgrade(product, kit)
                self.assertEqual(code, 2, out)
                self.assertIn("edited locally", out)
                self.assertIn(name, out)
                self.assertIn("--accept-local-edits", out)
                self.assertEqual(self.snapshot(product), before)

    def test_accept_local_edits_records_them_and_replaces_the_kit_files(self):
        _, product = self.installed_product()
        write(os.path.join(product, "absd", "RULES.md"), "# Rules, our edit\n")
        os.remove(os.path.join(product, "absd", "CHANGELOG.md"))
        write(os.path.join(product, ".claude", "agents", "reviewer.md"), "ours\n")
        kit = self.make_next_kit()
        code, out = self.upgrade(product, kit, "--accept-local-edits")
        self.assertEqual(code, 0, out)
        report = read(os.path.join(product, "absd-project", "upgrade-local-edits.md"))
        self.assertIn("2.0.0 → 2.1.0", report)
        self.assertIn(f"| modified | {sha(KIT['absd/RULES.md'])} | {sha('# Rules, our edit' + chr(10))} | `absd/RULES.md` |", report)
        self.assertIn(f"| deleted | {sha(KIT['absd/CHANGELOG.md'])} | — | `absd/CHANGELOG.md` |", report)
        self.assertIn(f"| added | — | {sha('ours' + chr(10))} | `.claude/agents/reviewer.md` |", report)
        self.assertIn("enrichment proposal", report)
        self.assertEqual(read(os.path.join(product, "absd", "RULES.md")), "# Rules 2.1\n")
        self.assertEqual(read(os.path.join(product, "absd", "CHANGELOG.md")), KIT["absd/CHANGELOG.md"])
        self.assertEqual(read(os.path.join(product, ".claude", "agents", "reviewer.md")), "ours\n")
        self.assertIn("::warning title=Local kit edits::3 local changes", out)
        self.assertIn("::warning title=Not in the kit manifest::.claude/agents/reviewer.md", out)
        self.assertIn("upgrade-local-edits.md into enrichment proposals", out)
        code, out = self.run_sync("check", "--root", product, "--json", os.path.join(self.root, "c.json"))
        self.assertEqual(code, 1, out)
        with open(os.path.join(self.root, "c.json"), encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual((data["modified"], data["missing"], data["extra"]), ([], [], [".claude/agents/reviewer.md"]))

    def test_refuses_a_kit_checkout_that_is_not_clean(self):
        _, product = self.installed_product()
        kit = self.make_next_kit()
        write(os.path.join(kit, "absd", "playbook", "stray.md"), "not in the manifest\n")
        before = self.snapshot(product)
        code, out = self.upgrade(product, kit)
        self.assertEqual(code, 2, out)
        self.assertIn("kit checkout is not clean", out)
        self.assertEqual(self.snapshot(product), before)

    def test_refuses_when_no_kit_is_installed(self):
        product = self.tree("product", PRODUCT)
        code, out = self.upgrade(product, self.make_next_kit())
        self.assertEqual(code, 2, out)
        self.assertIn("no absd/MANIFEST", out)


@unittest.skipUnless(shutil.which("git"), "git is not installed — the git case of migrate-v1 needs it")
class MigrateV1GitTests(SyncTestCase):
    def git(self, repo, *args):
        result = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_claude_layout_in_a_git_repo_uses_git_mv_for_tracked_paths(self):
        product = self.tree("product", {
            **PRODUCT,
            ".claude/agents/manager.md": "v1 manager\n",
            ".claude/working/context.md": "# v1 context\n",
            ".claude/working/brd.md": "# v1 brd\n",
            ".claude/archive/001_2026-01-05_login/audit.md": "# audit\n",
        })
        self.git(product, "init", "-q", "-b", "main")
        self.git(product, "config", "user.name", "Test")
        self.git(product, "config", "user.email", "test@example.com")
        self.git(product, "add", "-A")
        self.git(product, "commit", "-q", "-m", "v1 project")
        write(os.path.join(product, ".claude", "archive", "002_2026-02-01_cart", "audit.md"), "# not committed\n")

        code, out = self.run_sync("migrate-v1", "--root", product)
        self.assertEqual(code, 0, out)
        status = self.git(product, "status", "--porcelain").splitlines()
        self.assertIn("R  .claude/working/context.md -> absd-project/context.md", status)
        self.assertIn("R  .claude/archive/001_2026-01-05_login/audit.md -> absd-project/archive/001_2026-01-05_login/audit.md", status)
        self.assertIn("?? absd-project/archive/002_2026-02-01_cart/", status)
        self.assertIn("git mv   .claude/working/context.md → absd-project/context.md", out)
        self.assertIn("moved    .claude/archive/002_2026-02-01_cart → absd-project/archive/002_2026-02-01_cart", out)
        self.assertEqual(read(os.path.join(product, "absd-project", "context.md")), "# v1 context\n")
        self.assertFalse(os.path.exists(os.path.join(product, ".claude", "archive")))
        self.assertTrue(os.path.isfile(os.path.join(product, ".claude", "working", "brd.md")))
        self.assertIn("left     .claude/working/brd.md", out)
        self.assertIn("Continue cycle numbering at C003", out)


class MigrateV1Tests(SyncTestCase):
    V1 = {
        **PRODUCT,
        "working/context.md": "# v1 context\n",
        "working/brd.md": "# v1 brd\n",
        "working/src/app.py": "print('v1')\n",
        "archive/001_2026-01-05_login/brd.md": "# login\n",
        "archive/003_2026-03-01_pay_abandoned/brd.md": "# pay\n",
        "archive/README.md": "archived cycles\n",
    }

    def test_working_layout_without_git_uses_plain_moves(self):
        product = self.tree("product", self.V1)
        code, out = self.run_sync("migrate-v1", "--root", product)
        self.assertEqual(code, 0, out)
        files = self.snapshot(product)
        self.assertEqual(files["absd-project/context.md"], b"# v1 context\n")
        self.assertEqual(files["absd-project/archive/001_2026-01-05_login/brd.md"], b"# login\n")
        self.assertEqual(files["absd-project/archive/003_2026-03-01_pay_abandoned/brd.md"], b"# pay\n")
        self.assertEqual(files["absd-project/archive/README.md"], b"archived cycles\n")
        self.assertNotIn("working/context.md", files)
        self.assertFalse(os.path.exists(os.path.join(product, "archive")))
        self.assertEqual(files["working/brd.md"], b"# v1 brd\n")
        self.assertEqual(files["working/src/app.py"], b"print('v1')\n")
        self.assertEqual(len(files), len(self.V1))
        self.assertIn("moved    working/context.md → absd-project/context.md", out)
        self.assertNotIn("git mv", out.split("Follow-up")[0])
        self.assertIn("left     working/brd.md", out)
        self.assertIn("left     working/src/", out)
        self.assertIn("Continue cycle numbering at C004", out)
        self.assertIn("Foundation-delta", out)
        self.assertIn("v2 sections", out)

    def test_working_directory_with_only_context_md_is_removed(self):
        product = self.tree("product", {**PRODUCT, "working/context.md": "# v1 context\n"})
        code, out = self.run_sync("migrate-v1", "--root", product)
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.exists(os.path.join(product, "working")))
        self.assertNotIn("Left in place", out)
        self.assertIn("Continue cycle numbering at C001", out)

    def test_never_overwrites_a_destination(self):
        for name, existing in (("context", "absd-project/context.md"),
                               ("archive", "absd-project/archive/003_2026-03-01_pay_abandoned/brd.md")):
            with self.subTest(name):
                product = self.tree(f"product-{name}", {**self.V1, existing: "already here\n"})
                before = self.snapshot(product)
                code, out = self.run_sync("migrate-v1", "--root", product)
                self.assertEqual(code, 2, out)
                self.assertIn("never overwrites", out)
                self.assertIn(existing.split("/brd.md")[0], out)
                self.assertEqual(self.snapshot(product), before)

    def test_no_v1_project_is_an_input_error(self):
        product = self.tree("product", PRODUCT)
        code, out = self.run_sync("migrate-v1", "--root", product)
        self.assertEqual(code, 2, out)
        self.assertIn("no v1 ABSD project", out)

    def test_two_v1_layouts_are_an_input_error(self):
        product = self.tree("product", {**self.V1, ".claude/working/context.md": "# other v1 context\n"})
        before = self.snapshot(product)
        code, out = self.run_sync("migrate-v1", "--root", product)
        self.assertEqual(code, 2, out)
        self.assertEqual(self.snapshot(product), before)

    def test_migrate_then_install_keeps_the_migrated_context(self):
        kit = self.make_kit()
        product = self.tree("product", self.V1)
        self.assertEqual(self.run_sync("migrate-v1", "--root", product)[0], 0)
        code, out = self.run_sync("install", "--from", kit, "--to", product)
        self.assertEqual(code, 0, out)
        self.assertEqual(read(os.path.join(product, "absd-project", "context.md")), "# v1 context\n")


if __name__ == "__main__":
    unittest.main()
