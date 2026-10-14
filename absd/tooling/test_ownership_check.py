"""Tests for ownership_check.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
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
import ownership_check  # noqa: E402

CONTEXT = """# Context — Shop

## Old layout notes
| Path | Owner |
|---|---|
| src/ | tester |

## Source Layout & Ownership

Production code is the Builder's; tests are the Tester's.

| Root | Purpose |
|---|---|
| src | production |

### Ownership globs
| Area | Path glob | Owner | Notes |
|---|---|---|---|
| Snapshots | `src/**/snapshots/` | Tester | golden files next to the code |
| Test runner config | `ci/tests.yml`, `pytest.ini` | tester | |
| Pipelines | `ci/` | **builder** | whole directory |
| Production | `src/` | builder | |
| Build scripts | `./scripts/` `/Makefile` | builder | |
| Tests | `tests/**` | tester | |
| Fixtures | `fixtures/`<br>`seeds/` | tester | |
| Testing docs | docs/testing/ | tester | |
| Docs | `docs/**/*.md` | shared | |
| Release notes | `notes/v?.md` | shared | |
| Config | `config/*.json` | builder | top level only |
| Other product memory | `absd-project/` | manager | |

## Conventions
| Path | Owner |
|---|---|
| unowned/** | builder |
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


class OwnershipRuleTests(unittest.TestCase):
    """Glob semantics, the context table and the built-in artifact table — no git needed."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.context = write(os.path.join(self.dir.name, "context.md"), CONTEXT)

    def owners(self, rules, paths):
        return {path: ownership_check.owner_of(path, rules)[0] for path in paths}

    def test_glob_semantics_and_first_match_wins(self):
        expected = {
            "src/cart.py": "builder",
            "src/shop/deep/cart.py": "builder",           # trailing / = the whole directory
            "srcx/cart.py": "unowned",                    # ... a directory, not a name prefix
            "src/snapshots/cart.json": "tester",          # ** = no directory (and first match beats src/)
            "src/shop/a/snapshots/cart.json": "tester",   # ** = several directories
            "ci/tests.yml": "tester",                     # first match wins over ci/
            "ci/deploy.yml": "builder",
            "pytest.ini": "tester",                       # second glob in the same cell
            "pytest.ini.bak": "unowned",                  # the whole path must match
            "sub/pytest.ini": "unowned",                  # anchored at the repo root
            "scripts/build.sh": "builder",                # leading ./ ignored
            "Makefile": "builder",                        # leading / ignored
            "tests/test_cart.py": "tester",
            "tests/unit/deep/test_x.py": "tester",        # trailing ** crosses directories
            "fixtures/users.json": "tester",
            "seeds/users.json": "tester",                 # <br> separates globs
            "docs/testing/TESTING.md": "tester",          # first match wins over docs/**/*.md
            "docs/guide.md": "shared",
            "docs/api/v2/endpoints.md": "shared",
            "docs/guide.txt": "unowned",
            "notes/v1.md": "shared",
            "notes/v10.md": "unowned",                    # ? is exactly one character
            "notes/v/.md": "unowned",                     # ... and never a /
            "config/app.json": "builder",
            "config/env/app.json": "unowned",             # * stays inside one path segment
            "README.md": "unowned",
            "unowned/x.py": "unowned",                    # tables after the section are not read
        }
        rules = ownership_check.read_source_layout(self.context)
        self.assertEqual(self.owners(rules, expected), expected)

    def test_rule_origin_names_the_context_line(self):
        rules = ownership_check.read_source_layout(self.context)
        _, rule = ownership_check.owner_of("tests/test_cart.py", rules)
        line = CONTEXT.splitlines().index("| Tests | `tests/**` | tester | |") + 1
        self.assertEqual(rule.origin, f"{self.context}:{line}")
        self.assertEqual(rule.glob, "tests/**")

    def test_built_in_artifact_owners(self):
        project = "absd-project/"
        expected = {
            "working/cycle.md": "manager", "working/brd.md": "manager", "working/defect.md": "manager",
            "context.md": "manager", "lessons.md": "manager", "archive/001_2026-10-01_cart/audit.md": "manager",
            "working/analysis.md": "analyst", "catalogue.md": "analyst",
            "working/design.md": "designer", "working/design_review.md": "designer", "design-system.md": "designer",
            "working/evidence/designer/home.png": "designer",
            "working/architecture.md": "architect", "working/architecture/01-core.md": "architect",
            "working/test_plan.md": "tester", "working/test_report.md": "tester",
            "working/test_plan/02-oracles.md": "tester", "working/evidence/tester/red.log": "tester",
            "working/build_log.md": "builder", "working/clarification_needed.md": "builder",
            "working/evidence/builder/build.log": "builder",
            "working/arch_review.md": "auditor", "working/audit.md": "auditor",
            "working/evidence/auditor/probe.log": "auditor", "working/evidence/analyst/interview.md": "analyst",
            "working/notes.md": "unowned", "working/test_report.md.bak": "unowned", "working/evidence/x.log": "unowned",
        }
        rules = ownership_check.built_in_rules()
        actual = self.owners(rules, [project + path for path in expected])
        self.assertEqual(actual, {project + path: owner for path, owner in expected.items()})
        self.assertEqual(ownership_check.owner_of("working/test_report.md", rules)[0], "unowned")  # only under absd-project/

    def test_glob_header_and_plain_owner_cells(self):
        path = write(os.path.join(self.dir.name, "glob.md"),
                     "## Source Layout\n| Glob | Owner |\n|:---|:---:|\n| lib/ | `Builder` |\n| spec/ | Shared |\n")
        rules = ownership_check.read_source_layout(path)
        self.assertEqual(self.owners(rules, ["lib/a.rb", "spec/a_spec.rb"]), {"lib/a.rb": "builder", "spec/a_spec.rb": "shared"})

    def test_malformed_context_tables_are_input_errors(self):
        cases = {
            "no heading": ("# Context\n| Path | Owner |\n|---|---|\n| src/ | builder |\n", "no heading"),
            "table only in the next section": (
                "## Source Layout\nTo be decided.\n## Conventions\n| Path | Owner |\n|---|---|\n| src/ | builder |\n",
                "no table"),
            "no owner column": ("## Source Layout\n| Path | Notes |\n|---|---|\n| src/ | builder |\n", "no table"),
            "unknown owner": ("## Source Layout\n| Path | Owner |\n|---|---|\n| src/ | developer |\n", "unknown owner 'developer'"),
            "missing owner cell": ("## Source Layout\n| Area | Path | Owner |\n|---|---|---|\n| Code | src/ |\n", "cells"),
            "empty glob": ("## Source Layout\n| Path | Owner |\n|---|---|\n|  | builder |\n", "no path glob"),
            "no rows": ("## Source Layout\n| Path | Owner |\n|---|---|\n", "no rows"),
        }
        for name, (text, message) in cases.items():
            with self.subTest(name):
                path = write(os.path.join(self.dir.name, "bad.md"), text)
                with self.assertRaises(ownership_check.InputError) as caught:
                    ownership_check.read_source_layout(path)
                self.assertIn(message, str(caught.exception))


@unittest.skipUnless(shutil.which("git"), "git is not installed — ownership_check reads git history")
class OwnershipCheckTests(unittest.TestCase):
    """End to end against real temporary git repositories."""

    BRANCH = "absd/C001-cart"

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = self.dir.name
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        gitconfig = write(os.path.join(self.root, "gitconfig"), "")
        env = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": gitconfig, "GIT_CONFIG_NOSYSTEM": "1",
                                           "GIT_CEILING_DIRECTORIES": self.root})
        env.start()
        self.addCleanup(env.stop)
        for name in ("GITHUB_STEP_SUMMARY", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            os.environ.pop(name, None)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test Agent")
        self.git("config", "user.email", "agent@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.context = write(os.path.join(self.repo, "absd-project", "context.md"), CONTEXT)
        self.commit("bootstrap", None, ["README.md", "src/app.py", "tests/test_app.py"])  # unattributed, on main
        self.git("checkout", "-q", "-b", self.BRANCH)

    # --- helpers ----------------------------------------------------------------------------------------------

    def git(self, *args):
        result = subprocess.run(["git", "-C", self.repo, *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, subject, agent, files=(), cycle="C001", trailers=None, paragraphs=()):
        """Commit changes to `files` with the ABSD trailers in the message's last paragraph."""
        for path in files:
            full = os.path.join(self.repo, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "a", encoding="utf-8") as f:
                f.write(f"{subject}\n")
        self.git("add", "-A")
        if trailers is None:
            trailers = "\n".join(t for t in (agent and f"ABSD-Agent: {agent}", agent and cycle and f"ABSD-Cycle: {cycle}") if t)
        message = ["-m", subject]
        for paragraph in (*paragraphs, trailers):
            if paragraph:
                message += ["-m", paragraph]
        self.git("commit", "-q", "--allow-empty", *message)
        return self.git("rev-parse", "HEAD")

    def run_check(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = ownership_check.main(["--repo", self.repo, *args])
        return code, out.getvalue()

    def run_json(self, *args):
        path = os.path.join(self.root, "ownership.json")
        code, out = self.run_check(*args, "--json", path)
        with open(path, encoding="utf-8") as f:
            return code, out, json.load(f)

    def mode_f_history(self):
        """A clean cycle: every agent writes only its own paths. Returns the T-SHA."""
        self.commit("absd(C001): brd — manager", "manager", ["absd-project/working/brd.md", "absd-project/working/cycle.md"])
        self.commit("absd(C001): analysis — analyst", "analyst", ["absd-project/working/analysis.md", "absd-project/catalogue.md"])
        self.commit("absd(C001): architecture — architect", "architect",
                    ["absd-project/working/architecture.md", "absd-project/working/architecture/01-core.md"])
        t_sha = self.commit("absd(C001): plan & bind — tester", "tester",
                            ["absd-project/working/test_plan.md", "tests/test_cart.py", "ci/tests.yml"])
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py", "ci/deploy.yml", "absd-project/working/build_log.md"])
        self.commit("absd(C001): verify — tester", "tester", ["absd-project/working/test_report.md",
                    "absd-project/working/evidence/tester/run.log", "src/shop/snapshots/cart.json", "ci/tests.yml"])
        self.commit("absd(C001): audit — auditor", "auditor", ["absd-project/working/audit.md", "docs/guide.md"])
        return t_sha

    # --- clean history ----------------------------------------------------------------------------------------

    def test_clean_history_passes(self):
        t_sha = self.mode_f_history()
        code, out, data = self.run_json("--t-sha", t_sha)
        self.assertEqual(code, 0, out)
        self.assertTrue(data["passed"])
        self.assertEqual((data["errors"], data["warnings"]), ([], []))
        self.assertEqual(len(data["commits"]), 7)  # the unattributed bootstrap commit on main is outside the range
        self.assertEqual(data["agents"], {
            "manager": {"commits": 1, "files": 2}, "analyst": {"commits": 1, "files": 2},
            "architect": {"commits": 1, "files": 2}, "tester": {"commits": 2, "files": 6},
            "builder": {"commits": 1, "files": 3}, "auditor": {"commits": 1, "files": 2},
        })
        self.assertIn("### Ownership check — passed", out)
        self.assertIn("| tester | 2 | 6 |", out)
        self.assertNotIn("::error", out)

    def test_default_range_starts_at_the_merge_base_with_base(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        code, out, data = self.run_json()
        self.assertEqual(code, 0, out)
        self.assertEqual(data["range"], self.git("rev-parse", "main") + "..HEAD")
        self.assertEqual([c["subject"] for c in data["commits"]], ["absd(C001): WP-01 — builder"])

    # --- separation of duties ---------------------------------------------------------------------------------

    def test_builder_touching_a_test_path_fails(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py", "tests/test_cart.py"])
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertFalse(data["passed"])
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("changed tests/test_cart.py, owned by tester", data["errors"][0])
        self.assertIn(f"{self.context}:", data["errors"][0])
        self.assertIn("::error title=ownership::", out)
        self.assertIn("### Ownership check — FAILED", out)

    def test_builder_loosening_test_runner_config_fails(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["ci/deploy.yml", "ci/tests.yml"])
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("changed ci/tests.yml, owned by tester", data["errors"][0])

    def test_builder_deleting_or_moving_a_test_fails(self):
        self.commit("absd(C001): plan & bind — tester", "tester", ["tests/test_cart.py", "tests/test_pay.py"])
        self.git("rm", "-q", "tests/test_pay.py")
        self.git("mv", "tests/test_cart.py", "src/cart_check.py")
        self.commit("absd(C001): WP-01 — builder", "builder")
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        joined = "\n".join(data["errors"])
        self.assertIn("changed tests/test_cart.py, owned by tester", joined)
        self.assertIn("changed tests/test_pay.py, owned by tester", joined)

    def test_tester_touching_production_fails(self):
        self.commit("absd(C001): plan & bind — tester", "tester", ["tests/test_cart.py", "src/cart.py"])
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("(tester)", data["errors"][0])
        self.assertIn("changed src/cart.py, owned by builder", data["errors"][0])

    def test_shared_paths_are_open_to_every_agent(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["docs/guide.md", "notes/v1.md"])
        self.commit("absd(C001): verify — tester", "tester", ["docs/api/endpoints.md", "notes/v1.md"])
        code, out = self.run_check("--strict")
        self.assertEqual(code, 0, out)

    def test_artifact_ownership(self):
        self.commit("absd(C001): verify — tester", "tester", ["absd-project/working/test_report.md"])
        self.commit("absd(C001): WP-01 — builder", "builder", ["absd-project/working/evidence/builder/build.log"])
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.commit("absd(C001): fix report — builder", "builder", ["absd-project/working/test_report.md"])
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertEqual(data["errors"], [
            f"{self.git('rev-parse', '--short=7', 'HEAD')} (builder) 'absd(C001): fix report — builder' changed "
            "absd-project/working/test_report.md, owned by tester (built-in: absd-project/working/test_report.md)"])

    def test_manager_archive_moves_other_agents_artifacts_out_of_working(self):
        self.mode_f_history()
        archive = "absd-project/archive/001_2026-10-14_cart"
        os.makedirs(os.path.join(self.repo, archive), exist_ok=True)
        for name in ("analysis.md", "test_plan.md", "build_log.md", "audit.md", "architecture"):
            self.git("mv", f"absd-project/working/{name}", f"{archive}/{name}")
        self.commit("absd(C001): archive — manager", "manager")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_manager_editing_or_another_agent_deleting_an_artifact_still_fails(self):
        self.mode_f_history()
        self.commit("absd(C001): tweak plan — manager", "manager", ["absd-project/working/test_plan.md"])
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertIn("changed absd-project/working/test_plan.md, owned by tester", "\n".join(data["errors"]))
        self.git("reset", "-q", "--hard", "HEAD~1")
        self.git("rm", "-q", "absd-project/working/test_plan.md")
        self.commit("absd(C001): drop plan — builder", "builder")
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertIn("(builder)", "\n".join(data["errors"]))
        self.git("reset", "-q", "--hard", "HEAD~1")
        self.git("rm", "-q", "tests/test_cart.py")
        self.commit("absd(C001): drop a test — manager", "manager")
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertIn("changed tests/test_cart.py, owned by tester", "\n".join(data["errors"]))

    def test_built_in_artifacts_take_precedence_over_the_context_table(self):
        # the context table's last row gives everything else under absd-project/ to the manager
        self.commit("absd(C001): notes — manager", "manager", ["absd-project/working/notes.md"])
        self.commit("absd(C001): build log — manager", "manager", ["absd-project/working/build_log.md"])
        code, out, data = self.run_json()
        self.assertEqual(code, 1)
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("build_log.md, owned by builder (built-in", data["errors"][0])

    def test_unowned_files_warn_by_default_and_fail_with_strict(self):
        sha = self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py", "README.md"])
        message = f"README.md matches no Source Layout row (changed by {sha[:7]} (builder))"
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn(f"::warning title=unowned::{message}", out)
        code, out = self.run_check("--strict")
        self.assertEqual(code, 1)
        self.assertIn(f"::error title=unowned::{message}", out)

    # --- attribution ------------------------------------------------------------------------------------------

    def test_unattributed_commit_fails_unless_allowed(self):
        self.commit("quick fix", None, ["src/cart.py", "tests/test_cart.py"])
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("::error title=unattributed::", out)
        self.assertIn("no ABSD-Agent trailer", out)
        code, out, data = self.run_json("--allow-unattributed")
        self.assertEqual(code, 0, out)
        self.assertIn("::warning title=unattributed::", out)
        self.assertEqual(data["errors"], [])  # its files are not ownership-checked
        self.assertEqual(data["agents"], {"unattributed": {"commits": 1, "files": 2}})

    def test_unknown_or_several_agents_fail_even_when_unattributed_is_allowed(self):
        self.commit("WP-01", "buidler", ["src/cart.py"])
        self.commit("WP-02", None, ["src/pay.py"], trailers="ABSD-Agent: builder\nABSD-Agent: tester\nABSD-Cycle: C001")
        code, out, data = self.run_json("--allow-unattributed")
        self.assertEqual(code, 1)
        self.assertEqual(len(data["errors"]), 2)
        self.assertIn("unknown agent 'buidler'", data["errors"][0])
        self.assertIn("several agents in ABSD-Agent trailers (builder, tester)", data["errors"][1])

    def test_agent_line_outside_the_last_paragraph_is_not_a_trailer(self):
        self.commit("absd(C001): WP-01 — builder", None, ["src/cart.py"], trailers="ABSD-Cycle: C001",
                    paragraphs=["ABSD-Agent: builder"])
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("not in the message's last paragraph", out)

    def test_agent_names_are_case_insensitive_and_git_trailer_option_works(self):
        self.git("commit", "-q", "--allow-empty", "-m", "absd(C001): WP-01 — builder",
                 "--trailer", "ABSD-Agent: Builder", "--trailer", "ABSD-Cycle: C001")
        code, out, data = self.run_json()
        self.assertEqual(code, 0, out)
        self.assertEqual(data["commits"][0]["agent"], "builder")
        self.assertEqual(data["commits"][0]["cycles"], ["C001"])
        self.assertEqual(data["commits"][0]["author"], "Test Agent")

    def test_missing_or_malformed_cycle_trailer_is_a_warning(self):
        self.commit("WP-01", "builder", ["src/cart.py"], cycle=None)
        self.commit("WP-02", "builder", ["src/pay.py"], cycle="cycle-2")
        self.commit("WP-03", "builder", ["src/tax.py"], cycle="C0001")
        self.commit("WP-04", "builder", ["src/fee.py"], cycle="C01")
        self.commit("WP-05", None, ["src/vat.py"], trailers="ABSD-Agent: builder\nABSD-Cycle: C001\nABSD-Cycle: C002")
        code, out, data = self.run_json()
        self.assertEqual(code, 0, out)
        self.assertEqual(len(data["warnings"]), 4, data["warnings"])
        self.assertIn("'WP-01': expected one `ABSD-Cycle: C###` trailer, found none", data["warnings"][0])
        self.assertIn("'WP-02': expected one `ABSD-Cycle: C###` trailer, found cycle-2", data["warnings"][1])
        self.assertIn("'WP-04': expected one `ABSD-Cycle: C###` trailer, found C01", data["warnings"][2])
        self.assertIn("'WP-05': expected one `ABSD-Cycle: C###` trailer, found C001, C002", data["warnings"][3])
        self.assertIn("::warning title=cycle trailer::", out)

    # --- Gate T -----------------------------------------------------------------------------------------------

    def test_builder_commit_before_gate_t_fails(self):
        self.commit("absd(C001): brd — manager", "manager", ["absd-project/working/brd.md"])
        early = self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        t_sha = self.commit("absd(C001): plan & bind — tester", "tester", ["tests/test_cart.py"])
        self.commit("absd(C001): WP-02 — builder", "builder", ["src/pay.py"])
        code, out = self.run_check()
        self.assertEqual(code, 0, out)  # ordering is only checked with --t-sha
        code, out, data = self.run_json("--t-sha", t_sha[:10])
        self.assertEqual(code, 1)
        self.assertEqual(data["errors"], [f"production change before Gate T: {early[:7]} (builder) "
                                          f"'absd(C001): WP-01 — builder' does not descend from T-SHA {t_sha[:7]}"])
        self.assertEqual(data["tSha"], t_sha)
        self.assertIn("::error title=Gate T order::", out)

    def test_review_list_of_test_files_changed_after_gate_t(self):
        self.commit("absd(C001): red tests draft — tester", "tester", ["tests/test_pay.py"])
        t_sha = self.commit("absd(C001): plan & bind — tester", "tester", ["absd-project/working/test_plan.md", "tests/test_cart.py"])
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        amend = self.commit("TC-0007 | amend expected total — tester", "tester", [
            "tests/test_cart.py", "absd-project/working/test_plan.md", "absd-project/working/test_report.md", "docs/guide.md"])
        code, out, data = self.run_json("--t-sha", t_sha)
        self.assertEqual(code, 0, out)
        self.assertEqual(data["review"], [{"file": "tests/test_cart.py", "commit": amend, "agent": "tester",
                                           "subject": "TC-0007 | amend expected total — tester"}])
        self.assertIn("**Test files changed after Gate T (1)**", out)
        self.assertIn(f"| tests/test_cart.py | {amend[:7]} | tester | TC-0007 \\| amend expected total — tester |", out)

    def test_review_list_includes_test_changes_by_other_agents(self):
        t_sha = self.commit("absd(C001): plan & bind — tester", "tester", ["tests/test_cart.py"])
        fix = self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py", "tests/test_cart.py"])
        code, out, data = self.run_json("--t-sha", t_sha)
        self.assertEqual(code, 1)
        self.assertEqual([(r["file"], r["commit"], r["agent"]) for r in data["review"]], [("tests/test_cart.py", fix, "builder")])

    def test_no_review_list_without_t_sha(self):
        self.commit("absd(C001): verify — tester", "tester", ["tests/test_cart.py"])
        code, out, data = self.run_json()
        self.assertEqual(code, 0, out)
        self.assertEqual(data["review"], [])
        self.assertNotIn("after Gate T", out)

    # --- merges -----------------------------------------------------------------------------------------------

    def test_merge_commits_are_skipped_with_a_notice_unless_included(self):
        self.commit("absd(C001): plan & bind — tester", "tester", ["tests/test_cart.py"])
        self.git("checkout", "-q", "-b", "side")
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        self.git("checkout", "-q", self.BRANCH)
        self.commit("absd(C001): verify — tester", "tester", ["absd-project/working/test_report.md"])
        self.git("merge", "-q", "--no-ff", "side", "-m", "merge side", "-m", "ABSD-Agent: builder\nABSD-Cycle: C001")
        merge = self.git("rev-parse", "HEAD")
        code, out, data = self.run_json()
        self.assertEqual(code, 0, out)
        self.assertEqual(data["skippedMerges"], [merge])
        self.assertIn(f"::notice title=merges::1 merge commits skipped ({merge[:7]})", out)
        self.assertEqual(len(data["commits"]), 3)
        # included, the merge brings in the tester's report relative to its other parent
        code, out, data = self.run_json("--include-merges")
        self.assertEqual(code, 1)
        self.assertEqual(data["skippedMerges"], [])
        self.assertIn(f"{merge[:7]} (builder) 'merge side' changed absd-project/working/test_report.md, owned by tester",
                      "\n".join(data["errors"]))

    # --- range and input errors -------------------------------------------------------------------------------

    def test_explicit_range(self):
        bad = self.commit("absd(C001): WP-01 — builder", "builder", ["tests/test_cart.py"])
        self.commit("absd(C001): WP-02 — builder", "builder", ["src/cart.py"])
        self.assertEqual(self.run_check()[0], 1)
        code, out = self.run_check("--range", f"{bad}..HEAD")
        self.assertEqual(code, 0, out)

    def test_empty_range_is_an_input_error(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        code, out = self.run_check("--base", self.BRANCH)
        self.assertEqual(code, 2)
        self.assertIn("no commits in range", out)

    def test_bad_revisions_are_input_errors(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        cases = {
            "unknown base": ["--base", "trunk"],
            "unknown range": ["--range", "nope..HEAD"],
            "unknown t-sha": ["--t-sha", "0123456789abcdef"],
            "option-like range": ["--range=--output=x"],
            "option-like t-sha": ["--t-sha=-1"],
            "blank base": ["--base", " "],
        }
        for name, args in cases.items():
            with self.subTest(name):
                code, out = self.run_check(*args)
                self.assertEqual(code, 2, out)
                self.assertIn("::error::", out)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "x")))

    def test_missing_or_malformed_context_is_an_input_error(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py"])
        code, out = self.run_check("--context", os.path.join(self.root, "missing.md"))
        self.assertEqual(code, 2)
        bad = write(os.path.join(self.root, "bad.md"), "## Source Layout\n| Path | Owner |\n|---|---|\n| src/ | developer |\n")
        code, out = self.run_check("--context", bad)
        self.assertEqual(code, 2)
        self.assertIn("unknown owner 'developer'", out)

    def test_not_a_git_repository_is_an_input_error(self):
        empty = os.path.join(self.root, "empty")
        os.makedirs(empty)
        out = io.StringIO()
        with redirect_stdout(out):
            code = ownership_check.main(["--repo", empty, "--context", self.context])
        self.assertEqual(code, 2, out.getvalue())

    # --- outputs ----------------------------------------------------------------------------------------------

    def test_summary_markdown_and_github_step_summary(self):
        self.commit("absd(C001): WP-01 — builder", "builder", ["src/cart.py", "tests/test_cart.py"])
        summary_md = os.path.join(self.root, "ownership.md")
        step = write(os.path.join(self.root, "step.md"), "earlier step\n")
        with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": step}):
            code, out = self.run_check("--summary-md", summary_md)
        self.assertEqual(code, 1)
        for path in (summary_md, step):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("### Ownership check — FAILED", text)
            self.assertIn("| builder | 1 | 2 |", text)
            self.assertIn("**Violations (1)**", text)
        with open(step, encoding="utf-8") as f:
            self.assertTrue(f.read().startswith("earlier step\n"))


if __name__ == "__main__":
    unittest.main()
