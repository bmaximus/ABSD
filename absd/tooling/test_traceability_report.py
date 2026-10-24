"""Tests for traceability_report.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traceability_report  # noqa: E402


def junit(cases):
    """cases: list of (name, status, {property: value})"""
    parts = ['<?xml version="1.0"?><testsuites><testsuite name="s">']
    for name, status, props in cases:
        inner = ""
        if props:
            inner += "<properties>" + "".join(f'<property name="{k}" value="{v}"/>' for k, v in props.items()) + "</properties>"
        if status == "failed":
            inner += '<failure message="boom"/>'
        elif status == "error":
            inner += '<error message="crash"/>'
        elif status == "skipped":
            inner += "<skipped/>"
        parts.append(f'<testcase classname="suite" name="{name}">{inner}</testcase>')
    parts.append("</testsuite></testsuites>")
    return "".join(parts)


CATALOGUE = {"requirements": [
    {"id": "ACC-1", "area": "Accounts", "story": "Users sign in."},
    {"id": "ACC-2", "area": "Accounts", "story": "Users reset passwords."},
    {"id": "PAY-1", "area": "Payments", "story": "Users pay."},
    {"id": "OLD-1", "area": "Legacy", "story": "Gone.", "status": "retired"},
]}

MARKDOWN_CATALOGUE = """# Requirement catalogue

| ID | Area | Role | Story | Source | Status |
|---|---|---|---|---|---|
| ACC-1 | Accounts | Everyone | Users sign in. | C001 | active |
| **ACC-NF-1** | Accounts | Everyone | Sign-in answers within 1 s. | C001 | active |
| `ACC-BR-1` | Accounts | Everyone | Five wrong passwords lock the account. | C002 | active |
| OLD-1 | Legacy | Everyone | Gone. | C001 | Retired — see ACC-1 |

Notes mention ACC-9 in prose, which is not a catalogue entry.
"""

PLAN = """# Test Plan
| TC | Level | Title |
|---|---|---|
| TC-0001 | integration | sign in |
| `TC-0002` | integration | wrong password |
| **TC-0003** | e2e | sign in screen |
### TC-0004 — journey
Mentions TC-0999 in prose only, which is not planned.
"""


class TraceabilityReportTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        self.catalogue = self.write("catalogue.json", json.dumps(CATALOGUE))
        self.plan = self.write("test_plan.md", PLAN)

    def tearDown(self):
        self.dir.cleanup()

    def write(self, relative, text):
        path = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    @staticmethod
    def load(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def run_report(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = traceability_report.main(["--junit", os.path.join(self.root, "**", "*.xml"), *args])
        return code, out.getvalue()

    # --- acceptance -------------------------------------------------------------------------------------------

    def test_requirement_states_from_properties_and_name_tokens(self):
        self.write("r/junit.xml", junit([
            ("signs in [ACC-1]", "passed", {}),
            ("resets password", "failed", {"requirement": "ACC-2"}),
        ]))
        out_json = os.path.join(self.root, "t.json")
        code, out = self.run_report("--catalogue", self.catalogue, "--json", out_json)
        self.assertEqual(code, 1, out)  # ACC-2 failing (default fail-on includes failing)
        states = {r["id"]: r["state"] for r in self.load(out_json)["acceptance"]["requirements"]}
        self.assertEqual(states, {"ACC-1": "verified", "ACC-2": "failing", "PAY-1": "untested"})

    def test_untested_is_a_warning_by_default_and_an_error_on_request(self):
        self.write("r/junit.xml", junit([("a [ACC-1]", "passed", {}), ("b [ACC-2]", "passed", {})]))
        code, out = self.run_report("--catalogue", self.catalogue)
        self.assertEqual(code, 0, out)
        self.assertIn("::warning title=untested::requirement PAY-1", out)
        code, out = self.run_report("--catalogue", self.catalogue, "--fail-on", "untested")
        self.assertEqual(code, 1, out)

    def test_reserved_prefixes_in_brackets_are_not_requirements(self):
        self.write("r/junit.xml", junit([("regression [DEF-12] [TC-0001] [E2E-1] [OQ-3] [D-2] [ACC-1]", "passed", {})]))
        code, out = self.run_report("--catalogue", self.catalogue)
        self.assertEqual(code, 0, out)
        self.assertNotIn("not in the catalogue", out)

    def test_unknown_and_retired_ids_fail(self):
        self.write("r/junit.xml", junit([("typo [ACC-10]", "passed", {}), ("old", "passed", {"requirement": "OLD-1"})]))
        code, out = self.run_report("--catalogue", self.catalogue)
        self.assertEqual(code, 1)
        self.assertIn("ACC-10 (not in the catalogue)", out)
        self.assertIn("OLD-1 (retired)", out)

    def test_skipped_only_counts_as_untested_and_error_counts_as_failing(self):
        self.write("r/junit.xml", junit([("a [ACC-1]", "skipped", {}), ("b [ACC-2]", "error", {})]))
        out_json = os.path.join(self.root, "t.json")
        self.run_report("--catalogue", self.catalogue, "--json", out_json)
        states = {r["id"]: r["state"] for r in self.load(out_json)["acceptance"]["requirements"]}
        self.assertEqual(states["ACC-1"], "untested")
        self.assertEqual(states["ACC-2"], "failing")

    def test_same_requirement_on_two_devices_fails_if_either_fails(self):
        self.write("desktop/junit.xml", junit([("journey [ACC-1]", "passed", {})]))
        self.write("phone/junit.xml", junit([("journey [ACC-1]", "failed", {})]))
        code, out = self.run_report("--catalogue", self.catalogue)
        self.assertEqual(code, 1)
        self.assertIn("requirement ACC-1", out)

    def test_comma_separated_requirement_property(self):
        self.write("r/junit.xml", junit([("both", "passed", {"requirements": "ACC-1, ACC-2"})]))
        out_json = os.path.join(self.root, "t.json")
        self.run_report("--catalogue", self.catalogue, "--json", out_json)
        data = self.load(out_json)["acceptance"]
        self.assertEqual(data["verified"], 2)

    def test_markdown_catalogue_with_nf_and_br_ids(self):
        catalogue = self.write("catalogue.md", MARKDOWN_CATALOGUE)
        self.write("r/junit.xml", junit([
            ("signs in [ACC-1]", "passed", {}),
            ("fast [ACC-NF-1]", "passed", {}),
            ("locks", "failed", {"requirement": "ACC-BR-1"}),
            ("old [OLD-1]", "passed", {}),
        ]))
        out_json = os.path.join(self.root, "t.json")
        code, out = self.run_report("--catalogue", catalogue, "--json", out_json)
        self.assertEqual(code, 1)
        data = self.load(out_json)["acceptance"]
        states = {r["id"]: r["state"] for r in data["requirements"]}
        self.assertEqual(states, {"ACC-1": "verified", "ACC-NF-1": "verified", "ACC-BR-1": "failing"})
        self.assertEqual(data["requirements"][0]["story"], "Users sign in.")
        self.assertIn("OLD-1 (retired)", out)

    def test_duplicate_catalogue_ids_are_an_input_error(self):
        dup = self.write("dup.json", json.dumps({"requirements": [{"id": "A-1"}, {"id": "A-1"}]}))
        self.write("r/junit.xml", junit([("x", "passed", {})]))
        code, out = self.run_report("--catalogue", dup)
        self.assertEqual(code, 2)
        self.assertIn("duplicate", out)

    # --- plan conformance -------------------------------------------------------------------------------------

    def test_plan_ids_are_read_from_table_first_cells_and_headings_only(self):
        self.assertEqual(traceability_report.read_plan(self.plan), ["TC-0001", "TC-0002", "TC-0003", "TC-0004"])

    def test_split_plan_parts_fences_and_removed_cases(self):
        self.write("test_plan/02-e2e.md", "| TC | Status |\n|---|---|\n| TC-0005 | planned |\n| TC-0006 | removed (D-3) |\n"
                   "```\n| TC-0007 | an example inside a code fence |\n```\n")
        self.assertEqual(traceability_report.read_plan(self.plan),
                         ["TC-0001", "TC-0002", "TC-0003", "TC-0004", "TC-0005"])

    def test_a_plan_without_test_cases_is_an_input_error(self):
        empty = self.write("empty_plan.md", "# Test plan\nTC-0001 is only mentioned in prose.\n")
        self.write("r/junit.xml", junit([("TC-0001", "passed", {})]))
        code, out = self.run_report("--plan", empty)
        self.assertEqual(code, 2)
        self.assertIn("plans no test case", out)

    def test_missing_failed_and_unplanned_test_cases(self):
        self.write("r/junit.xml", junit([
            ("TC-0001 signs in", "passed", {}),
            ("wrong password", "failed", {"tc": "TC-0002"}),
            ("TC-0003 screen", "skipped", {}),
            ("TC-0050 extra", "passed", {}),
        ]))
        out_json = os.path.join(self.root, "t.json")
        code, out = self.run_report("--plan", self.plan, "--json", out_json)
        self.assertEqual(code, 1)
        plan = self.load(out_json)["plan"]
        self.assertEqual(plan["states"], {"TC-0001": "passed", "TC-0002": "failed", "TC-0003": "skipped", "TC-0004": "missing"})
        self.assertEqual(plan["unplanned"], ["TC-0050"])
        self.assertIn("::warning title=unplanned::TC-0050", out)

    def test_all_planned_cases_passing_passes(self):
        self.write("r/junit.xml", junit([
            ("TC-0001", "passed", {}), ("TC-0002", "passed", {}),
            ("TC-0003", "passed", {}), ("TC-0004 desktop", "passed", {}), ("TC-0004 phone", "passed", {}),
        ]))
        code, out = self.run_report("--plan", self.plan)
        self.assertEqual(code, 0, out)
        self.assertIn("4/4 planned test cases passing", out)

    # --- usage ------------------------------------------------------------------------------------------------

    def test_malformed_junit_is_an_input_error(self):
        self.write("r/junit.xml", "<testsuites><testcase name='x'")
        code, out = self.run_report("--catalogue", self.catalogue)
        self.assertEqual(code, 2)

    def test_directories_matched_by_the_glob_are_ignored(self):
        self.write("r/desktop/junit.xml", junit([("a [ACC-1]", "passed", {})]))  # r/** also matches the directory r/desktop
        out = io.StringIO()
        with redirect_stdout(out):
            code = traceability_report.main(["--junit", os.path.join(self.root, "r", "**", "*"), "--catalogue", self.catalogue])
        self.assertEqual(code, 0, out.getvalue())

    def test_needs_catalogue_or_plan(self):
        self.write("r/junit.xml", junit([("x", "passed", {})]))
        code, out = self.run_report()
        self.assertEqual(code, 2)

    def test_no_junit_files_is_an_input_error(self):
        code, out = self.run_report("--catalogue", self.catalogue)
        self.assertEqual(code, 2)
        self.assertIn("No JUnit XML", out)

    def test_every_junit_glob_must_match(self):
        self.write("unit/junit.xml", junit([("a [ACC-1]", "passed", {})]))
        out = io.StringIO()
        with redirect_stdout(out):
            code = traceability_report.main(["--junit", os.path.join(self.root, "unit", "*.xml"),
                                             "--junit", os.path.join(self.root, "e2e", "*.xml"), "--catalogue", self.catalogue])
        self.assertEqual(code, 2)   # the e2e suite left no results: it did not run
        self.assertIn("No JUnit XML files found for: " + os.path.join(self.root, "e2e", "*.xml"), out.getvalue())

    def test_a_glob_whose_files_hold_no_test_case_is_an_input_error(self):
        self.write("unit/junit.xml", junit([("a [ACC-1]", "passed", {})]))
        self.write("phone/junit.xml", '<?xml version="1.0"?><testsuites><testsuite name="phone"/></testsuites>')
        out = io.StringIO()
        with redirect_stdout(out):
            code = traceability_report.main(["--junit", os.path.join(self.root, "unit", "*.xml"),
                                             "--junit", os.path.join(self.root, "phone", "*.xml"), "--catalogue", self.catalogue])
        self.assertEqual(code, 2)   # the phone project ran no test
        self.assertIn("No test cases in the JUnit XML files for: " + os.path.join(self.root, "phone", "*.xml"), out.getvalue())

    def test_unknown_fail_on_category_is_an_input_error(self):
        self.write("r/junit.xml", junit([("x", "passed", {})]))
        code, out = self.run_report("--catalogue", self.catalogue, "--fail-on", "nonsense")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
