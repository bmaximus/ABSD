"""Tests for trace_check.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trace_check  # noqa: E402

ANALYSIS = """Cycle: C004 | Mode: F | Status: COMPLETE | 2026-10-13

# Analysis

## Requirements

| ID | Title | Status |
|---|---|---|
| ACC-1 | Users sign in | new |
| **ACC-2** | Users reset passwords | changed |
| `ACC-NF-1` | Sign-in answers within 1 s | new |
| ACC-BR-1 | Five wrong passwords lock the account | new |
| [ACC-3] | Admins restore removed accounts | new |
| ACC-4 | Export to CSV | Removed |

### ACC-1 — Sign in
- ACC-1.AC1 GIVEN a member WHEN they sign in with the right password THEN they see the dashboard
- ACC-1.AC2 GIVEN a member WHEN the password is wrong THEN "Wrong password" is shown

### ACC-2 — Reset password
| AC | Given / When / Then |
|---|---|
| ACC-2.AC1 | GIVEN a member WHEN they ask for a reset THEN a mail arrives within 60 s |

ACC-3.AC1 GIVEN an admin WHEN they restore an account THEN its owner can sign in again.
ACC-4.AC1 is gone with ACC-4.

## External facts referenced
- EXT-MAIL-1 — the mail provider rejects messages over 10 MB.

## Inherited behaviour inventory
| # | Behaviour | Decision |
|---|---|---|
| 1 | INH-3 the legacy grid keeps one empty row | Keep (user, D-2) |
"""

CATALOGUE = """# Requirement catalogue

| ID | Area | Story | Status |
|---|---|---|---|
| ACC-1 | Accounts | Users sign in. | active |
| ACC-2 | Accounts | Users reset passwords. | active |
| ACC-NF-1 | Accounts | Sign-in within 1 s. | active |
| ACC-BR-1 | Accounts | Lock after five wrong passwords. | active |
| ACC-3 | Accounts | Admins restore removed accounts. | active |
| ACC-4 | Accounts | Export to CSV. | retired |
"""

DESIGN = """# Design

## Journeys
### UJ-1 — Sign in
1. SCR-1, focus on the e-mail field (ACC-1).
### UJ-2 — Reset password
1. SCR-2 (ACC-2.AC1).

## Screens
| SCR | Name |
|---|---|
| SCR-1 | Sign-in |
| SCR-2 | Reset |

## Formatting
Times in UTC-5 are shown as 24h; hashes are SHA-256.

## Traceability
| Requirement | Journeys | Screens |
|---|---|---|
| ACC-1 | UJ-1 | SCR-1 |
| ACC-2 | UJ-2 | SCR-2 |

## Appendix
Nothing here.
"""

ARCHITECTURE = """# Architecture

| Requirement | Module |
|---|---|
| ACC-1 | auth |

## Work Packages
| WP | Scope |
|---|---|
| WP-1 | sign-in slice |
"""

ARCHITECTURE_PART = """# Part 1 — core
ACC-2, ACC-NF-1, ACC-BR-1 and ACC-3 live in the accounts module; UJ-1, UJ-2, SCR-1 and SCR-2 are served by it.
Mail goes through the provider (EXT-MAIL-1).
"""

TEST_PLAN = """# Test plan

| TC | Covers | Expected | Source |
|---|---|---|---|
| TC-0001 | ACC-1.AC1 | dashboard | SPEC:ACC-1.AC1 |
| TC-0002 | ACC-1.AC2 | "Wrong password" | SPEC:ACC-1.AC2 |
| TC-0003 | ACC-2.AC1 | mail within 60 s | SPEC:ACC-2.AC1 |
| TC-0004 | ACC-3.AC1 | owner signs in | SPEC: ACC-3.AC1 |
| TC-0005 | ACC-NF-1 | p95 < 1 s | SPEC:ACC-NF-1 |
| TC-0006 | ACC-BR-1 | 4 → open, 5 → locked | SPEC:ACC-BR-1 |
| TC-0007 | EXT-MAIL-1 | 413 from the fake | FACT:EXT-MAIL-1 |

### TC-0008 — journeys UJ-1 and UJ-2 on SCR-1 and SCR-2, desktop and phone
#### Oracle
SPEC:UJ-1 and SPEC:UJ-2 as written in design.md.

## Seams
| TSEAM | Need | Status |
|---|---|---|
| TSEAM-1 | a clock seam to open a session at midnight | resolved by ADR-7 |
"""

AUDIT = """# Audit
Overall: PASS
| ID | Severity | Category | Rule cited | Evidence | Proposed route | Status |
|---|---|---|---|---|---|---|
| F-1 | Major | Code | ABSD:CODE-3 | src/a.py:10 | Builder | resolved — fixed in WP-1 @abc1234 |
| F-2 | Minor | Code | ABSD:CODE-4 | src/b.py:3 | Builder | open |
| F-3 | **Critical** | Security | ABSD:SEC-1 | log | user | accepted-by-user (context.md, 2026-10-12) |

## Counts by severity
| Severity | Count |
|---|---|
| Critical | 1 |
| Major | 1 |
"""

TEST_REPORT = """# Test report
| ID | Severity | Category | Rule cited | Evidence | Status |
|---|---|---|---|---|---|
| TF-1 | Major | Oracle | ABSD:ORACLE-2 | TC-0003 | Resolved (C004 fix 1) |
"""

ARCH_REVIEW = """# Architecture review
Verdict: PASS
| ID | Severity | Category | Rule cited | Evidence | Proposed route |
|---|---|---|---|---|---|
| AR-1 | Major | Seams | ABSD:ARCH-4 | §7 | Architect delta |

## Resolution
| AR | Resolution |
|---|---|
| AR-1 | resolved by ADR-7 |
"""


class TraceCheckTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        self.working = os.path.join(self.root, "working")
        self.catalogue = self.write("catalogue.md", CATALOGUE)
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        for name, text in (("analysis.md", ANALYSIS), ("design.md", DESIGN), ("architecture.md", ARCHITECTURE),
                           ("architecture/01-core.md", ARCHITECTURE_PART), ("test_plan.md", TEST_PLAN),
                           ("audit.md", AUDIT), ("test_report.md", TEST_REPORT), ("arch_review.md", ARCH_REVIEW)):
            self.write(os.path.join("working", name), text)

    def tearDown(self):
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        self.dir.cleanup()

    def write(self, relative, text):
        path = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def edit(self, relative, old, new):
        path = os.path.join(self.root, relative)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text, f"fixture {relative} has no {old!r}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new))

    def remove(self, relative):
        os.remove(os.path.join(self.root, relative))

    def run_main(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = trace_check.main(list(args))
        return code, out.getvalue()

    def run_gate(self, name, *args):
        return self.run_main("gate", name, "--working", self.working, "--catalogue", self.catalogue, *args)

    def run_json(self, *args):
        out_json = os.path.join(self.root, "out.json")
        code, out = self.run_main(*args, "--json", out_json)
        with open(out_json, encoding="utf-8") as f:
            return code, out, json.load(f)

    def gate_json(self, name, *extra):
        code, out, data = self.run_json("gate", name, "--working", self.working, "--catalogue", self.catalogue, *extra)
        return code, out, {check["name"]: check for check in data["checks"]}

    def parsed(self, text):
        doc = trace_check.Doc("x.md")
        trace_check.parse(text, doc)
        return doc

    # --- definitions and references ---------------------------------------------------------------------------

    def test_ids_are_defined_by_first_table_cells_and_heading_first_tokens(self):
        doc = self.parsed(
            "| ID | Title |\n|---|---|\n| **ACC-1** | a |\n| `ACC-2` x | b |\n| [ACC-3](#acc-3) | c |\n"
            "| see ACC-4 | d |\n\n## ACC-5 — five\n## Notes on ACC-6\n#ACC-7 is not a heading\n- ACC-8 list item\n"
            "| ACC-9.AC1 | an AC row defines the AC, not ACC-9 |\nProse | ACC-11 | is not a table row\n")
        self.assertEqual(doc.defined("requirement"), {"ACC-1", "ACC-2", "ACC-3", "ACC-5"})
        self.assertEqual(doc.defined("ac"), {"ACC-9.AC1"})

    def test_a_table_header_row_defines_nothing(self):
        doc = self.parsed("| UJ-1 | UJ-2 |\n|-|:-:|\n| SCR-1 | x |\n")
        self.assertEqual(doc.defined("uj"), set())
        self.assertEqual(doc.defined("scr"), {"SCR-1"})

    def test_a_table_without_separator_row_has_no_header(self):
        doc = self.parsed("| UJ-1 | first |\n| UJ-2 | second |\n")
        self.assertEqual(doc.defined("uj"), {"UJ-1", "UJ-2"})

    def test_code_fences_define_nothing_and_do_not_end_sections(self):
        doc = self.parsed("## TC-0001 — run\n```bash\n# install\n| TC-0002 | x |\n```\nSPEC:ACC-1.AC1\n"
                          "~~~~\n## TC-0003\n~~~\n~~~~~\n## TC-0004\n")
        self.assertEqual(doc.defined("tc"), {"TC-0001", "TC-0004"})
        self.assertIn("SPEC:ACC-1.AC1", dict(doc.sections)["TC-0001 — run"])
        self.assertEqual(doc.referenced("tc"), {"TC-0001", "TC-0002", "TC-0003", "TC-0004"})

    def test_a_fence_line_with_an_info_string_does_not_close_a_fence(self):
        doc = self.parsed("```\n## TC-0001\n```python\n## TC-0002\n```\n## TC-0003\n")
        self.assertEqual(doc.defined("tc"), {"TC-0003"})

    def test_removed_or_retired_whole_word_excludes_a_definition(self):
        doc = self.parsed("| ACC-1 | Removed |\n| ACC-2 | was RETIRED in C003 |\n| ACC-3 | unremoved, retiree |\n"
                          "## ACC-4 (removed)\n## ACC-5 — keep\n| ACC-5 | removed |\n")
        self.assertEqual(doc.defined("requirement"), {"ACC-3", "ACC-5"})
        self.assertEqual(doc.excluded("requirement"), {"ACC-1", "ACC-2", "ACC-4"})

    def test_a_status_column_alone_decides_removal(self):
        doc = self.parsed("| ID | Story | Status |\n|---|---|---|\n| ACC-1 | Restore removed posts | active |\n"
                          "| ACC-2 | Export | retired |\n")
        self.assertEqual(doc.defined("requirement"), {"ACC-1"})
        self.assertEqual(doc.excluded("requirement"), {"ACC-2"})

    def test_an_escaped_pipe_stays_inside_its_cell(self):
        doc = self.parsed("| ID | Title | Status |\n|---|---|---|\n| ACC-1 | a \\| b | removed |\n| ACC-2 | c | active |\n")
        self.assertEqual(doc.defined("requirement"), {"ACC-2"})
        self.assertEqual(doc.excluded("requirement"), {"ACC-1"})

    def test_reserved_codes_are_not_requirements(self):
        text = ("UJ-1 SCR-2 TC-0003 ABSD:CODE-4 E2E-5 F-6 WP-8 EXT-9 TC-CONFLICT-1 A-1 OQ-2 D-3 UXQ-4 UXA-5 "
                "ACC-10 PAY-NF-2 PAY-BR-3 QC-7")
        # QC is the fixed area code of the Foundation quality capabilities, so QC-7 is a requirement
        self.assertEqual(trace_check.referenced_in(text, "requirement"), {"ACC-10", "PAY-NF-2", "PAY-BR-3", "QC-7"})

    def test_references_are_whole_tokens(self):
        text = "ACC-10 xACC-1 ACC-1x acc-1 ACC-NF-1 and [ACC-2] and ACC-3.AC4 and ACC-5."
        self.assertEqual(trace_check.referenced_in(text, "requirement"), {"ACC-10", "ACC-NF-1", "ACC-2", "ACC-3", "ACC-5"})
        self.assertEqual(trace_check.referenced_in(text, "ac"), {"ACC-3.AC4"})

    def test_id_family_formats(self):
        text = "TC-001 TC-0042 TC-12345 EXT-PAY-1 EXT-1 UJ-3 SCR-4 ADR-5 TSEAM-6 WP-7 WP-x"
        self.assertEqual(trace_check.referenced_in(text, "tc"), {"TC-0042", "TC-12345"})
        self.assertEqual(trace_check.referenced_in(text, "ext"), {"EXT-PAY-1"})
        for family, expected in (("uj", "UJ-3"), ("scr", "SCR-4"), ("adr", "ADR-5"), ("tseam", "TSEAM-6"), ("wp", "WP-7")):
            self.assertEqual(trace_check.referenced_in(text, family), {expected})

    def test_heading_sections_run_to_the_next_heading_of_the_same_or_higher_level(self):
        doc = self.parsed("## A\na\n### B\nb\n## C\nc\n# D\n")
        sections = dict(doc.sections)
        self.assertEqual(sections["A"], "## A\na\n### B\nb")
        self.assertEqual(sections["B"], "### B\nb")
        self.assertEqual(sections["C"], "## C\nc")

    def test_missing_ids_are_sorted_naturally(self):
        check = trace_check.coverage("c", {"ACC-10", "ACC-2", "ACC-1"}, {"ACC-1"})
        self.assertEqual(check.missing, ["ACC-2", "ACC-10"])

    # --- gate1 ------------------------------------------------------------------------------------------------

    def test_gate1_passes_on_a_complete_analysis(self):
        code, out = self.run_gate("gate1")
        self.assertEqual(code, 0, out)
        self.assertIn("✓ every requirement defined in analysis.md is defined in catalogue.md (5 checked)", out)
        self.assertIn("::notice::analysis.md: not checked, marked removed/retired — ACC-4", out)
        self.assertTrue(out.rstrip().endswith("gate1: PASS — 3 checks passed"), out)

    def test_gate1_a_functional_requirement_without_ac_fails_but_nf_and_br_are_exempt(self):
        self.edit("working/analysis.md", "ACC-3.AC1 GIVEN", "GIVEN")
        code, out = self.run_gate("gate1")
        self.assertEqual(code, 1)
        self.assertIn("✗ every functional requirement defined in analysis.md has an AC in analysis.md: 1 missing — ACC-3", out)
        self.assertIn("::error title=trace_check gate1::every functional requirement", out)
        self.assertIn("gate1: FAIL — 1 of 3 checks failed", out)

    def test_gate1_an_ac_of_another_requirement_does_not_count(self):
        self.edit("working/analysis.md", "ACC-3.AC1 GIVEN", "ACC-30.AC1 GIVEN")
        code, out = self.run_gate("gate1")
        self.assertEqual(code, 1)
        self.assertIn("1 missing — ACC-3", out)

    def test_gate1_a_requirement_missing_or_retired_in_the_catalogue_fails(self):
        self.edit("catalogue.md", "| ACC-2 | Accounts | Users reset passwords. | active |\n", "")
        self.edit("catalogue.md", "Lock after five wrong passwords. | active", "Lock after five wrong passwords. | retired")
        code, out = self.run_gate("gate1")
        self.assertEqual(code, 1)
        self.assertIn("is defined in catalogue.md: 2 missing — ACC-2, ACC-BR-1", out)

    def test_gate1_an_analysis_without_requirements_fails(self):
        self.write("working/analysis.md", "# Analysis\nNothing yet.\n")
        code, out = self.run_gate("gate1")
        self.assertEqual(code, 1)
        self.assertIn("✗ analysis.md defines at least one requirement: none defined", out)

    def test_gate1_missing_inputs_are_input_errors(self):
        self.remove("catalogue.md")
        code, out = self.run_gate("gate1")
        self.assertEqual(code, 2)
        self.assertIn("::error::", out)
        self.assertIn("catalogue.md: not found", out)
        self.remove("working/analysis.md")
        code, out = self.run_main("gate", "gate1", "--working", self.working, "--catalogue", self.write("c.md", CATALOGUE))
        self.assertEqual(code, 2)
        self.assertIn("analysis.md: not found", out)

    # --- gate-ux ----------------------------------------------------------------------------------------------

    def test_gate_ux_passes_and_lists_unknown_area_ids_as_a_notice(self):
        code, out = self.run_gate("gate-ux")
        self.assertEqual(code, 0, out)
        self.assertIn("✓ every UJ defined in design.md is referenced in its Traceability section (2 checked)", out)
        self.assertIn("::notice::design.md: not checked, area code unknown to catalogue.md — SHA-256, UTC-5", out)

    def test_gate_ux_a_reference_outside_the_traceability_section_does_not_count(self):
        self.edit("working/design.md", "| ACC-2 | UJ-2 | SCR-2 |\n", "")
        self.edit("working/design.md", "Nothing here.", "Nothing here. UJ-2 SCR-2")
        code, out = self.run_gate("gate-ux")
        self.assertEqual(code, 1)
        self.assertIn("referenced in its Traceability section: 1 missing — UJ-2", out)
        self.assertIn("referenced in its Traceability section: 1 missing — SCR-2", out)

    def test_gate_ux_without_a_traceability_heading_fails_with_a_warning(self):
        self.edit("working/design.md", "## Traceability", "## Mapping")
        code, out = self.run_gate("gate-ux")
        self.assertEqual(code, 1)
        self.assertIn("::warning::design.md has no heading containing 'Traceability'", out)
        self.assertIn("2 missing — UJ-1, UJ-2", out)

    def test_gate_ux_a_requirement_unknown_to_the_catalogue_fails(self):
        self.edit("working/design.md", "(ACC-1)", "(ACC-1, ACC-12)")
        self.edit("catalogue.md", "Export to CSV. | retired", "Export to CSV. | retired |\n| AUD-1 | Audit | x. | active")
        self.edit("working/design.md", "Nothing here.", "Retired ACC-4 and AUD-1.")
        code, out = self.run_gate("gate-ux")
        self.assertEqual(code, 1)
        self.assertIn("is defined in catalogue.md: 2 missing — ACC-4, ACC-12", out)

    def test_gate_ux_needs_design_md(self):
        self.remove("working/design.md")
        code, out = self.run_gate("gate-ux")
        self.assertEqual(code, 2)
        self.assertIn("design.md: not found", out)

    # --- gate2 ------------------------------------------------------------------------------------------------

    def test_gate2_reads_architecture_parts_next_to_the_index(self):
        code, out = self.run_gate("gate2")
        self.assertEqual(code, 0, out)
        self.assertIn("gate2: PASS — 5 checks passed", out)

    def test_gate2_lists_every_uncovered_id(self):
        self.remove("working/architecture/01-core.md")
        code, out, checks = self.gate_json("gate2")
        self.assertEqual(code, 1)
        self.assertEqual(checks["every requirement in scope of analysis.md is referenced in architecture.md"]["missing"],
                         ["ACC-2", "ACC-3", "ACC-BR-1", "ACC-NF-1"])
        self.assertEqual(checks["every UJ defined in design.md is referenced in architecture.md"]["missing"], ["UJ-1", "UJ-2"])
        self.assertEqual(checks["every SCR defined in design.md is referenced in architecture.md"]["missing"], ["SCR-1", "SCR-2"])
        self.assertEqual(checks["every EXT referenced in analysis.md is referenced in architecture.md"]["missing"], ["EXT-MAIL-1"])
        self.assertTrue(checks["architecture.md defines at least one WP"]["passed"])

    def test_gate2_architecture_without_work_packages_fails(self):
        self.edit("working/architecture.md", "| WP-1 | sign-in slice |", "| Slice 1 | WP-1 is planned |")
        code, out = self.run_gate("gate2")
        self.assertEqual(code, 1)
        self.assertIn("✗ architecture.md defines at least one WP: none defined", out)

    def test_gate2_without_design_md_skips_ui_checks_with_a_notice(self):
        self.remove("working/design.md")
        self.remove("working/architecture/01-core.md")
        self.write("working/architecture/01-core.md", "ACC-2 ACC-NF-1 ACC-BR-1 ACC-3 EXT-MAIL-1\n")
        code, out = self.run_gate("gate2")
        self.assertEqual(code, 0, out)
        self.assertIn("::notice::design.md not found in", out)
        self.assertIn("gate2: PASS — 3 checks passed", out)

    def test_gate2_defect_mode_checks_every_def(self):
        self.remove("working/analysis.md")
        self.write("working/defect.md", "| DEF | Title | Severity |\n|---|---|---|\n| DEF-7 | wrong zone on ACC-1.AC1 | Critical |\n")
        code, out, checks = self.gate_json("gate2")
        self.assertEqual(checks["every DEF defined in defect.md is referenced in architecture.md"]["missing"], ["DEF-7"])
        self.write("working/architecture/02-fix.md", "DEF-7 is fixed in WP-1.\n")
        code, out, checks = self.gate_json("gate2")
        self.assertEqual(checks["every DEF defined in defect.md is referenced in architecture.md"]["missing"], [])

    def test_gate2_removed_requirements_need_no_architecture(self):
        self.edit("working/architecture/01-core.md", "ACC-3 live", "live")
        code, out = self.run_gate("gate2")
        self.assertEqual(code, 1)
        self.assertIn("1 missing — ACC-3", out)
        self.edit("working/analysis.md", "| [ACC-3] | Admins restore removed accounts | new |",
                  "| [ACC-3] | Admins restore removed accounts | removed |")
        code, out = self.run_gate("gate2")
        self.assertEqual(code, 0, out)

    # --- gateT ------------------------------------------------------------------------------------------------

    def test_gate_t_passes_on_a_complete_plan(self):
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 0, out)
        self.assertIn("✓ every AC in scope of analysis.md is referenced in a TC row of test_plan.md (4 checked)", out)
        self.assertIn("gateT: PASS — 11 checks passed", out)

    def test_gate_t_reports_each_uncovered_family(self):
        self.write("working/test_plan.md", "| TC | Source |\n|---|---|\n| TC-0001 | SPEC:ACC-1.AC1 |\n")
        code, out, checks = self.gate_json("gateT")
        self.assertEqual(code, 1)
        name = "every {} is referenced in a TC row of test_plan.md".format
        self.assertEqual(checks[name("AC in scope of analysis.md")]["missing"],
                         ["ACC-1.AC2", "ACC-2.AC1", "ACC-3.AC1"])
        self.assertEqual(checks[name("NF requirement in scope of analysis.md")]["missing"], ["ACC-NF-1"])
        self.assertEqual(checks[name("BR requirement in scope of analysis.md")]["missing"], ["ACC-BR-1"])
        self.assertEqual(checks[name("UJ defined in design.md")]["missing"], ["UJ-1", "UJ-2"])
        self.assertEqual(checks[name("SCR defined in design.md")]["missing"], ["SCR-1", "SCR-2"])
        self.assertEqual(checks[name("EXT referenced in architecture.md")]["missing"], ["EXT-MAIL-1"])

    def test_gate_t_ext_ids_come_from_the_architecture(self):
        self.edit("working/architecture/01-core.md", "(EXT-MAIL-1)", "(EXT-MAIL-1); deploys go to the platform (EXT-HOST-2)")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 1)
        self.assertIn("✗ every EXT referenced in architecture.md is referenced in a TC row of test_plan.md: 1 missing — EXT-HOST-2", out)

    def test_gate_t_a_requirement_id_alone_does_not_cover_its_ac(self):
        self.edit("working/test_plan.md", "| TC-0002 | ACC-1.AC2 | \"Wrong password\" | SPEC:ACC-1.AC2 |",
                  "| TC-0002 | ACC-1 | \"Wrong password\" | SPEC:ACC-1 |")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 1)
        self.assertIn("1 missing — ACC-1.AC2", out)

    def test_gate_t_acs_of_removed_requirements_and_removed_acs_are_not_required(self):
        self.edit("working/analysis.md", "## External facts", "| ACC-1.AC3 | removed in C004 |\n\n## External facts")
        self.edit("working/test_plan.md", "ACC-3.AC1", "ACC-3")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 1)  # ACC-3.AC1 still required; ACC-4.AC1 and ACC-1.AC3 are not
        self.assertIn("1 missing — ACC-3.AC1", out)

    def test_gate_t_every_tc_needs_an_oracle_source_on_its_row_or_in_its_section(self):
        self.edit("working/test_plan.md", "| SPEC:ACC-1.AC2 |", "| |")
        self.edit("working/test_plan.md", "| SPEC: ACC-3.AC1 |", "| SPEC: |")
        self.edit("working/test_plan.md", "SPEC:UJ-1 and SPEC:UJ-2", "UJ-1 and UJ-2")
        self.edit("working/test_plan.md", "## Seams", "TC-0009 in prose is not planned.\n\n## Seams")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 1)
        self.assertIn("has an oracle source (SPEC:, FACT: or CHAR:): 3 without a source — TC-0002, TC-0004, TC-0008", out)

    def test_gate_t_a_source_in_a_deeper_heading_of_the_tc_section_counts(self):
        self.edit("working/test_plan.md", "#### Oracle", "#### Oracle\nCHAR:INH-3")
        self.edit("working/test_plan.md", "SPEC:UJ-1 and SPEC:UJ-2", "UJ-1 and UJ-2")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 0, out)

    def test_gate_t_an_open_tseam_fails(self):
        self.edit("working/test_plan.md", "| resolved by ADR-7 |", "| Open |")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 1)
        self.assertIn("✗ no TSEAM defined in test_plan.md is open: 1 open — TSEAM-1", out)

    def test_gate_t_open_is_a_whole_word_and_removed_seams_are_ignored(self):
        self.edit("working/test_plan.md", "## Seams\n| TSEAM | Need | Status |\n|---|---|---|\n", "## Seams\n")
        self.edit("working/test_plan.md", "a clock seam to open a session at midnight | resolved by ADR-7",
                  "reopened, then closed |\n| TSEAM-2 | open, now removed")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 0, out)
        self.assertIn("✓ no TSEAM defined in test_plan.md is open (1 checked)", out)

    def test_gate_t_a_plan_without_test_cases_fails(self):
        self.write("working/test_plan.md", "# Test plan\nTC-0001 mentioned in prose only.\n")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 1)
        self.assertIn("✗ test_plan.md defines at least one TC: none defined", out)

    def test_gate_t_needs_the_test_plan(self):
        self.remove("working/test_plan.md")
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 2)
        self.assertIn("test_plan.md: not found", out)

    # --- gate3 ------------------------------------------------------------------------------------------------

    def test_gate3_passes_when_every_blocking_finding_is_closed(self):
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 0, out)
        self.assertIn("✓ no open Critical/Major finding in audit.md (2 checked)", out)
        self.assertIn("✓ no open Critical/Major finding in arch_review.md (1 checked)", out)
        self.assertIn("gate3: PASS — 5 checks passed", out)

    def test_gate3_lists_open_critical_and_major_findings(self):
        self.edit("working/audit.md", "resolved — fixed in WP-1 @abc1234", "not yet resolved")   # must START with it
        self.edit("working/audit.md", "accepted-by-user (context.md, 2026-10-12)", "open")
        self.edit("working/test_report.md", "Resolved (C004 fix 1)", "unresolved")
        self.edit("working/arch_review.md", "| AR-1 | resolved by ADR-7 |", "| AR-2 | resolved by ADR-7 |")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 1)
        self.assertIn("✗ no open Critical/Major finding in audit.md: 2 open — F-1 (Major), F-3 (Critical)", out)
        self.assertIn("in test_report.md: 1 open — TF-1 (Major)", out)
        self.assertIn("in arch_review.md: 1 open — AR-1 (Major)", out)
        self.assertNotIn("F-2", out)

    def test_gate3_verdict_word_belongs_to_the_report(self):
        self.edit("working/audit.md", "Overall: PASS", "Verdict: PASS")   # the audit's verdict line is "Overall:"
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 1)
        self.assertIn("audit.md verdict is PASS: 1 not passing — Overall: missing", out)

    def test_gate3_reads_design_review_when_present(self):
        self.write("working/design_review.md", "| ID | Severity | Status |\n|---|---|---|\n| DQ-1 | Major | open |\n")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 1)
        self.assertIn("in design_review.md: 1 open — DQ-1 (Major)", out)

    def test_gate3_needs_all_three_reports(self):
        for name in ("arch_review.md", "test_report.md", "audit.md"):
            self.write("working/" + name, "# ok\n")
            self.remove("working/" + name)
            code, out = self.run_gate("gate3")
            self.assertEqual(code, 2, name)
            self.assertIn(f"{name}: not found", out)
            self.write("working/" + name, "# ok\n")

    def test_gate3_route_mode_x_needs_only_the_audit(self):
        self.write("working/cycle.md", "# Cycle C007\nCycle: C007 | Mode: X | Status: IN-PROGRESS\n")
        self.remove("working/arch_review.md")
        self.remove("working/test_report.md")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 0, out)
        self.assertIn("route Mode X: requires audit.md", out)

    def test_gate3_route_mode_d_needs_no_architecture_review_but_reads_one(self):
        self.write("working/cycle.md", "Cycle: C008 | **Mode:** D | Status: IN-PROGRESS\n")
        self.remove("working/arch_review.md")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 0, out)
        self.remove("working/test_report.md")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 2, out)
        self.assertIn("test_report.md: not found", out)
        self.write("working/test_report.md", TEST_REPORT)
        self.write("working/arch_review.md", "| ID | Severity | Status |\n|---|---|---|\n| AR-9 | Major | open |\n")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 1, out)
        self.assertIn("AR-9 (Major)", out)

    def test_gate3_route_mode_r_needs_the_release_report_and_the_audit(self):
        self.write("working/cycle.md", "Cycle: C010 | Mode: R | Status: IN-PROGRESS\n")
        self.remove("working/arch_review.md")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 0, out)
        self.assertIn("route Mode R: requires test_report.md, audit.md", out)
        self.remove("working/test_report.md")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 2)

    def test_gate3_mode_f_cycle_needs_all_three_reports(self):
        self.write("working/cycle.md", "Cycle: C009 | Mode: F | Status: IN-PROGRESS\n")
        self.remove("working/arch_review.md")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 2, out)
        self.assertIn("arch_review.md: not found", out)

    def test_gate2_and_gate_t_fall_back_to_the_brief_without_analysis(self):
        with open(os.path.join(self.working, "analysis.md"), encoding="utf-8") as f:
            analysis = f.read()
        self.remove("working/analysis.md")
        self.write("working/brd.md", analysis)
        for gate in ("gate2", "gateT"):
            code, out = self.run_gate(gate)
            self.assertEqual(code, 0, out)
            self.assertIn("analysis.md not found — requirements read from brd.md", out)

    def test_gate_t_without_architecture_reads_the_defect_list_and_skips_ext(self):
        with open(os.path.join(self.working, "analysis.md"), encoding="utf-8") as f:
            analysis = f.read()
        self.remove("working/analysis.md")
        self.remove("working/architecture.md")
        self.remove("working/architecture/01-core.md")   # split parts count as the architecture too
        self.write("working/defect.md", analysis)
        code, out = self.run_gate("gateT")
        self.assertEqual(code, 0, out)
        self.assertIn("requirements read from defect.md", out)
        self.assertIn("EXT check skipped", out)

    def test_gate2_without_any_requirement_source_is_an_input_error(self):
        self.remove("working/analysis.md")
        code, out = self.run_gate("gate2")
        self.assertEqual(code, 2)
        self.assertIn("none of analysis.md, brd.md, defect.md", out)

    def test_gate3_requires_passing_verdicts(self):
        self.edit("working/audit.md", "Overall: PASS", "Overall: BLOCKED")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 1)
        self.assertIn("audit.md verdict is PASS: 1 not passing — Overall: BLOCKED", out)
        self.edit("working/audit.md", "Overall: BLOCKED", "Overall: PASS")
        self.write("working/design_review.md", "# Design QA\n| Level | Verdict: PASS / FAIL |\n|---|---|\n")
        code, out = self.run_gate("gate3")   # a "Verdict:" inside a table is not the verdict line
        self.assertEqual(code, 1)
        self.assertIn("design_review.md verdict is PASS or N/A: 1 not passing — Verdict: missing", out)
        self.write("working/arch_review.md", "# Review\n**Verdict:** N/A — no architecture change on this route\n")
        self.write("working/design_review.md", "Verdict: PASS\n")
        code, out = self.run_gate("gate3")
        self.assertEqual(code, 0, out)

    def test_gate_t_ignores_mentions_outside_tc_rows(self):
        self.write("working/test_plan.md", "Out of scope: ACC-1.AC2, ACC-NF-1, UJ-2\n\n"
                   "| # | Blocking? | Source | Defect | Status |\n|---|---|---|---|---|\n"
                   "| 1 | yes | ACC-BR-1 | no boundary given | open |\n\n"
                   "| TC | Requirement ids | Source |\n|---|---|---|\n| TC-0001 | ACC-1 | SPEC:ACC-1.AC1 |\n")
        code, out, checks = self.gate_json("gateT")
        self.assertEqual(code, 1)
        name = "every {} is referenced in a TC row of test_plan.md".format
        self.assertIn("ACC-1.AC2", checks[name("AC in scope of analysis.md")]["missing"])
        self.assertEqual(checks[name("NF requirement in scope of analysis.md")]["missing"], ["ACC-NF-1"])
        self.assertIn("UJ-2", checks[name("UJ defined in design.md")]["missing"])
        self.assertEqual(len(checks["no blocking spec defect in test_plan.md is open"]["missing"]), 1)

    def test_gate_t_blocking_spec_defect_closes_when_answered(self):
        self.edit("working/test_plan.md", "| TC |", "| # | Blocking? | Defect | Status |\n|---|---|---|---|\n"
                  "| 1 | yes | boundary | answered — D-4 |\n| 2 | no | wording | open |\n\n| TC |")
        code, out = self.run_gate("gateT")
        self.assertIn("✓ no blocking spec defect in test_plan.md is open (1 checked)", out)

    def test_gate_t_oracle_sources_must_resolve(self):
        self.write("working/test_plan.md",
                   "| TC | Requirement ids | Source |\n|---|---|---|\n"
                   "| TC-0001 | ACC-1 | SPEC:ACC-1.AC9 |\n"
                   "| TC-0002 | ACC-1 | SPEC:architecture §5 |\n"
                   "| TC-0003 | — | SPEC:architecture §6 |\n"
                   "| TC-0004 | — | FACT:EXT-MAIL-1 |\n"
                   "| TC-0005 | — | CHAR:INH-9 |\n"
                   "| TC-0006 | — | SPEC:SCR-7.empty |\n"
                   "| TC-0007 | — | SPEC:the design |\n")
        self.write("facts.md", "| EXT | Fact | Status |\n|---|---|---|\n| EXT-MAIL-1 | size limit | UNVERIFIED |\n")
        code, out, checks = self.gate_json("gateT", "--external-facts", os.path.join(self.root, "facts.md"))
        self.assertEqual(code, 1)
        bad = "\n".join(checks["every oracle source resolves (ABSD:ORACLE-1)"]["missing"])
        self.assertIn("TC-0001 → SPEC:ACC-1.AC9 (unknown AC)", bad)
        self.assertIn("TC-0002 → SPEC:architecture", bad)
        self.assertNotIn("TC-0003", bad)   # an internal unit may cite the architecture
        self.assertIn("TC-0004 → FACT:EXT-MAIL-1 (not VERIFIED", bad)
        self.assertIn("TC-0005 → CHAR:INH-9 (INH id not in analysis.md)", bad)
        self.assertIn("TC-0006 → SPEC:SCR-7.empty (unknown UJ/SCR)", bad)
        self.assertIn("TC-0007 → SPEC:the (not an id", bad)
        self.write("facts.md", "| EXT | Fact | Status |\n|---|---|---|\n| EXT-MAIL-1 | size limit | VERIFIED 2026-10-12 |\n")
        code, out, checks = self.gate_json("gateT", "--external-facts", os.path.join(self.root, "facts.md"))
        self.assertNotIn("TC-0004", "\n".join(checks["every oracle source resolves (ABSD:ORACLE-1)"]["missing"]))

    def test_gate_t_source_forms_and_the_catalogue(self):
        self.remove("working/analysis.md")
        self.write("working/brd.md", "# Brief\n- ACC-1.AC1 copy\n")
        self.write("working/test_plan.md", "| TC | Covers | Source |\n|---|---|---|\n"
                   "| TC-0001 | ACC-1.AC1 | SPEC:ACC-1.AC1. |\n"
                   "| TC-0002 | ACC-3 | SPEC:ACC-3 |\n"        # a catalogue requirement the brief does not cite
                   "| TC-0003 | ACC-1 | SPEC:ZZZ-9. |\n"
                   "| TC-0004 | — | FACT:mail-limit |\n"
                   "| TC-0005 | — | CHAR:legacy-grid |\n")
        code, out, checks = self.gate_json("gateT")
        self.assertEqual(checks["every oracle source resolves (ABSD:ORACLE-1)"]["missing"], [
            "TC-0003 → SPEC:ZZZ-9 (unknown requirement)", "TC-0004 → FACT:mail-limit (not an EXT id)",
            "TC-0005 → CHAR:legacy-grid (not an INH id)"])

    def test_gate_t_brief_mode_checks_cited_nf_and_br_requirements(self):
        self.remove("working/analysis.md")
        self.write("working/brd.md", "# Brief\n- keep ACC-NF-1 and ACC-BR-1 as they are\n")
        self.write("working/test_plan.md", "| TC | Covers | Source |\n|---|---|---|\n| TC-0001 | ACC-NF-1 | SPEC:ACC-NF-1 |\n")
        code, out, checks = self.gate_json("gateT")
        name = "every {} requirement in scope of brd.md is referenced in a TC row of test_plan.md".format
        self.assertEqual(checks[name("NF")]["missing"], [])
        self.assertEqual(checks[name("NF")]["checked"], 1)
        self.assertEqual(checks[name("BR")]["missing"], ["ACC-BR-1"])

    def test_gate_t_brief_mode_checks_the_cited_acs(self):
        self.remove("working/analysis.md")
        self.write("working/brd.md", "# Brief\n## 11. Acceptance\n- ACC-1.AC1 copy\n- ACC-2.AC3 new wording\n")
        code, out, checks = self.gate_json("gateT")
        self.assertEqual(code, 1)
        self.assertEqual(checks["every AC in scope of brd.md is referenced in a TC row of test_plan.md"]["missing"],
                         ["ACC-2.AC3"])

    def test_gate_t_defect_mode_checks_every_def(self):
        self.remove("working/analysis.md")
        self.write("working/defect.md", "| DEF | Title | Severity |\n|---|---|---|\n| DEF-7 | wrong zone | Critical |\n"
                   "| DEF-8 | stale card | Minor |\n")
        self.edit("working/test_plan.md", "| TC |", "| TC-0901 | regression DEF-7 | SPEC:ACC-1.AC1 |\n| TC |")
        code, out, checks = self.gate_json("gateT")
        self.assertEqual(checks["every DEF defined in defect.md is referenced in a TC row of test_plan.md"]["missing"],
                         ["DEF-8"])

    # --- generic check ----------------------------------------------------------------------------------------

    def test_check_with_comma_separated_files_and_directories(self):
        analysis = os.path.join(self.working, "analysis.md")
        code, out = self.run_main("check", "--ids", "requirement", "--defined-in", analysis,
                                  "--referenced-in", os.path.join(self.working, "architecture"))
        self.assertEqual(code, 1)
        self.assertIn("1 missing — ACC-1", out)
        code, out = self.run_main("check", "--ids", "requirement", "--defined-in", analysis, "--referenced-in",
                                  os.path.join(self.working, "architecture") + "," + os.path.join(self.working, "test_plan.md"))
        self.assertEqual(code, 0, out)
        self.assertIn("check: PASS — 1 checks passed", out)

    def test_a_byte_order_mark_does_not_hide_the_first_line(self):
        path = os.path.join(self.root, "bom.md")
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("| ADR-1 | stack |\n")
        code, out = self.run_main("check", "--ids", "adr", "--defined-in", path, "--referenced-in", self.catalogue)
        self.assertEqual(code, 1)
        self.assertIn("1 missing — ADR-1", out)

    def test_check_tc_family_and_json(self):
        self.write("tests/a.md", "TC-0001 TC-0002")
        code, out, data = self.run_json("check", "--ids", "tc", "--defined-in", os.path.join(self.working, "test_plan.md"),
                                        "--referenced-in", os.path.join(self.root, "tests"))
        self.assertEqual(code, 1)
        self.assertFalse(data["passed"])
        self.assertEqual(data["checks"][0]["checked"], 8)
        self.assertEqual(data["checks"][0]["missing"], ["TC-0003", "TC-0004", "TC-0005", "TC-0006", "TC-0007", "TC-0008"])

    def test_check_input_errors(self):
        code, out = self.run_main("check", "--ids", "uj", "--defined-in", os.path.join(self.root, "nope.md"),
                                  "--referenced-in", self.catalogue)
        self.assertEqual(code, 2)
        self.assertIn("nope.md: not found", out)
        os.makedirs(os.path.join(self.root, "empty"))
        code, out = self.run_main("check", "--ids", "uj", "--defined-in", self.catalogue,
                                  "--referenced-in", os.path.join(self.root, "empty"))
        self.assertEqual(code, 2)
        code, out = self.run_main("check", "--ids", "uj", "--defined-in", ",", "--referenced-in", self.catalogue)
        self.assertEqual(code, 2)
        with redirect_stdout(io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                trace_check.main(["check", "--ids", "story", "--defined-in", "a", "--referenced-in", "b"])
        self.assertEqual(raised.exception.code, 2)

    # --- output -----------------------------------------------------------------------------------------------

    def test_summary_markdown_goes_to_the_file_and_the_step_summary(self):
        summary = os.path.join(self.root, "summary.md")
        step = self.write("step.md", "")
        os.environ["GITHUB_STEP_SUMMARY"] = step
        self.edit("working/test_plan.md", "| resolved by ADR-7 |", "| open |")
        code, out = self.run_gate("gateT", "--summary-md", summary)
        self.assertEqual(code, 1)
        for path in (summary, step):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("### trace_check gateT", text)
            self.assertIn("- ✗ no TSEAM defined in test_plan.md is open: 1 open — TSEAM-1", text)
            self.assertIn("**gateT: FAIL — 1 of 11 checks failed**", text)

    def test_json_lists_every_check_and_note(self):
        code, out, data = self.run_json("gate", "gate1", "--working", self.working, "--catalogue", self.catalogue)
        self.assertEqual(code, 0, out)
        self.assertTrue(data["passed"])
        self.assertEqual(data["title"], "gate1")
        self.assertEqual([c["passed"] for c in data["checks"]], [True, True, True])
        self.assertEqual(data["notes"], [{"level": "notice", "text": "analysis.md: not checked, marked removed/retired — ACC-4"}])


if __name__ == "__main__":
    unittest.main()
