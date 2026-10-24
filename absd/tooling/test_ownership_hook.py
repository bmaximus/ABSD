"""Tests for ownership_hook.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownership_hook  # noqa: E402

CONTEXT = """# Project Context

## 3. Source Layout & Ownership (ADR-002)

| Path | Owner | Purpose |
|---|---|---|
| `src/**` | builder | production source |
| `tests/**` | tester | all tests |
| `docs/testing/**` | tester | testing docs |
| `docs/**`, `README.md` | shared | product docs |
| `**` | builder | everything else (catch-all) |

## 4. Execution Environment
"""


class OwnershipHookTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        os.makedirs(os.path.join(self.root, "absd-project"))
        with open(os.path.join(self.root, "absd-project", "context.md"), "w", encoding="utf-8") as f:
            f.write(CONTEXT)

    def tearDown(self):
        self.dir.cleanup()

    def call(self, agent, path, tool="Write", key="file_path", raw=None):
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": self.root,
                 "tool_input": {key: path}}
        if agent is not None:
            event["agent_type"] = agent
        err = io.StringIO()
        with redirect_stderr(err):
            code = ownership_hook.main(io.StringIO(raw if raw is not None else json.dumps(event)),
                                       {"CLAUDE_PROJECT_DIR": self.root})
        return code, err.getvalue()

    def test_owner_may_write_its_paths(self):
        self.assertEqual(self.call("builder", os.path.join(self.root, "src", "cart.py"))[0], 0)
        self.assertEqual(self.call("tester", os.path.join(self.root, "tests", "test_cart.py"))[0], 0)

    def test_builder_may_not_write_tests(self):
        code, err = self.call("builder", os.path.join(self.root, "tests", "test_cart.py"))
        self.assertEqual(code, 2)
        self.assertIn("owned by tester", err)
        self.assertIn("TC-CONFLICT", err)

    def test_tester_may_not_write_production_code(self):
        code, err = self.call("tester", "src/cart.py", tool="Edit")
        self.assertEqual(code, 2)
        self.assertIn("TSEAM", err)

    def test_manager_may_not_write_code_or_tests(self):
        self.assertEqual(self.call("manager", "src/cart.py")[0], 2)
        self.assertEqual(self.call("manager", "tests/test_cart.py")[0], 2)

    def test_pipeline_artifacts_follow_the_built_in_table(self):
        self.assertEqual(self.call("tester", "absd-project/working/test_plan.md")[0], 0)
        self.assertEqual(self.call("builder", "absd-project/working/test_plan.md")[0], 2)
        self.assertEqual(self.call("manager", "absd-project/working/analysis.md")[0], 2)
        self.assertEqual(self.call("analyst", "absd-project/catalogue.md")[0], 0)
        self.assertEqual(self.call("designer", "absd-project/working/evidence/designer/notes.md")[0], 0)
        self.assertEqual(self.call("tester", "absd-project/working/evidence/builder/log.txt")[0], 2)

    def test_manager_owns_context_even_when_the_table_is_broken(self):
        with open(os.path.join(self.root, "absd-project", "context.md"), "w", encoding="utf-8") as f:
            f.write("# Project Context\n\nno table yet\n")
        self.assertEqual(self.call("manager", "absd-project/context.md")[0], 0)
        code, err = self.call("builder", "src/cart.py")
        self.assertEqual(code, 2)
        self.assertIn("Source Layout", err)

    def test_shared_paths_and_the_catch_all_row(self):
        self.assertEqual(self.call("builder", "README.md")[0], 0)
        self.assertEqual(self.call("tester", "docs/guide.md")[0], 0)
        self.assertEqual(self.call("builder", "Makefile")[0], 0)
        self.assertEqual(self.call("tester", "Makefile")[0], 2)

    def test_unowned_paths_are_allowed(self):
        with open(os.path.join(self.root, "absd-project", "context.md"), "w", encoding="utf-8") as f:
            f.write(CONTEXT.replace("| `**` | builder | everything else (catch-all) |\n", ""))
        self.assertEqual(self.call("tester", "Makefile")[0], 0)

    def test_first_matching_row_wins(self):
        # docs/testing/** (tester) is listed before docs/** (shared)
        self.assertEqual(self.call("builder", "docs/testing/TESTING.md")[0], 2)
        self.assertEqual(self.call("tester", "docs/testing/TESTING.md")[0], 0)

    def test_the_kit_is_read_only_for_every_agent(self):
        for agent in ("manager", "builder", "tester", "auditor"):
            self.assertEqual(self.call(agent, "absd/RULES.md")[0], 2, agent)
        code, err = self.call("architect", ".claude/agents/architect.md")
        self.assertEqual(code, 2)
        self.assertIn("read-only", err)
        self.assertEqual(self.call("designer", ".github/agents/Designer.agent.md")[0], 2)

    def test_agent_configuration_is_the_managers(self):
        for path in (".claude/settings.json", "CLAUDE.md", "src/CLAUDE.md", ".github/copilot-instructions.md",
                     ".github/instructions/project.instructions.md"):
            self.assertEqual(self.call("manager", path)[0], 0, path)
            code, err = self.call("builder", path)   # the catch-all row would otherwise give these to the builder
            self.assertEqual(code, 2, path)
            self.assertIn("owned by manager (the ABSD artifact table)", err)
            self.assertIn("name the change in your hand-back", err)
        self.assertEqual(self.call("manager", ".claude/agents/manager.md")[0], 2)   # the kit stays read-only

    def test_refusals_name_the_route_by_writer_and_owner(self):
        self.assertIn("open question", self.call("builder", "absd-project/catalogue.md")[1])
        self.assertIn("Gate UX delta", self.call("tester", "absd-project/design-system.md")[1])
        self.assertIn("architecture finding", self.call("builder", "absd-project/working/architecture.md")[1])
        self.assertIn("audit reports are the Auditor's", self.call("builder", "absd-project/working/audit.md")[1])
        self.assertIn("goes through architecture.md", self.call("designer", "src/cart.py")[1])
        self.assertIn("a test or gate change is the Tester's", self.call("auditor", "tests/test_cart.py")[1])

    def test_non_absd_sessions_and_paths_outside_the_project_are_allowed(self):
        self.assertEqual(self.call(None, "src/cart.py")[0], 0)
        self.assertEqual(self.call("general-purpose", "src/cart.py")[0], 0)
        self.assertEqual(self.call("builder", "/tmp/elsewhere/scratch.txt")[0], 0)
        # the catch-all row would give these to the builder if outside paths were not let through first
        self.assertEqual(self.call("tester", "/tmp/elsewhere/scratch.txt")[0], 0)
        self.assertEqual(self.call("builder", os.path.join(self.root, "..", "sibling", "x.py"))[0], 0)

    def test_namespaced_agent_type_and_notebook_path(self):
        self.assertEqual(self.call("plugin:builder", "tests/test_cart.py")[0], 2)
        self.assertEqual(self.call("Tester", "src/nb.ipynb", tool="NotebookEdit", key="notebook_path")[0], 2)

    def test_relative_paths_resolve_from_cwd(self):
        self.assertEqual(self.call("builder", "./tests/../tests/test_cart.py")[0], 2)

    def test_unreadable_input_refuses(self):
        code, err = self.call("builder", "src/x.py", raw="{not json")
        self.assertEqual(code, 2)
        self.assertIn("unreadable", err)


if __name__ == "__main__":
    unittest.main()
