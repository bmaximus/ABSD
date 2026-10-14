"""Tests for kit_lint.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit_lint  # noqa: E402

GATES = """# Quality gates

Code **GATE**. Scope paragraph citing ORACLE-1.

## Checklist

- [ ] A check that did not run is RED (GATE-1)

## Rules

**GATE-1** — Treat a check that did not run as RED.
- *Why:* audits certified suites they never ran (LL-1).
- *Check:* negative controls.
- *Applies when:* always.
- *Provenance:* LL-1 (SomeProduct, 2026-10)

**GATE-2** — Fail on a unit no test runs.
- *Why:* a reader shipped untested.
- *Check:* coverage gate.
- *Applies when:* always.
- *Provenance:* industry baseline
"""

ORACLES = """# Oracles

Codes **ORACLE** and **FAKE**.

## Rules

**ORACLE-1** — Oracles come from the specification.
- *Provenance:* LL-2 (SomeProduct, 2026-10)

**FAKE-1** — Fakes answer like the real thing.
- *Provenance:* industry baseline
"""

README = """# ABSD playbook

## Routing table

| Topic | Code | File |
|---|---|---|
| Gates | GATE | `absd/playbook/testing/gates.md` |
| Oracles and fakes | `ORACLE`, `FAKE` | `absd/playbook/testing/oracles.md` |

## Rule format

```markdown
**CODE-n** — <imperative, checkable sentence>.
**GATE-9** — an example inside a fence is not a rule.
- *Provenance:* LL-n
```

Reserved codes: `GATE` `ORACLE` `FAKE` `TC` `DEF`

Products cite `ABSD:CODE-n`.
"""

LEDGER = """# Lessons ledger

## Entries

| LL | Date | Project | What happened |
|---|---|---|---|
| LL-1 | 2026-10-13 | SomeProduct | A check did not run. |
| LL-2 | 2026-10-13 | SomeProduct | Oracles came from code. |
"""

MIRROR = """---
name: {Name}
description: >-
  ABSD pipeline worker.
---

# ABSD {Name} — mirror

Your manual is **`.claude/agents/{name}.md`**.
"""

BASE = {
    "absd/VERSION": "1.2.3\n",
    "absd/CHANGELOG.md": "# Changelog\n\nNewest first.\n\n## 1.2.3 — 2026-10-14\n\n- GATE-2 added (LL-2).\n\n## 1.2.2\n",
    "absd/RULES.md": "# Rules\n\nCite ABSD:GATE-1 and ORACLE-1 (`absd/playbook/README.md`).\n",
    "absd/lessons/LEDGER.md": LEDGER,
    "absd/playbook/README.md": README,
    "absd/playbook/testing/gates.md": GATES,
    "absd/playbook/testing/oracles.md": ORACLES,
    ".claude/agents/manager.md": "---\nname: manager\n---\n\n# Manager\n\nRead `absd/RULES.md` first (GATE-1).\n",
    ".claude/agents/tester.md": "---\nname: tester\n---\n\n# Tester\n\nApply ABSD:FAKE-1.\n",
    ".github/agents/Manager.agent.md": MIRROR.format(Name="Manager", name="manager"),
    ".github/agents/Tester.agent.md": MIRROR.format(Name="Tester", name="tester"),
    "README.md": "# ABSD\n\nThe kit lives in `absd/`; agents in `.claude/agents/`.\n",
    "CLAUDE.md": "# Maintainer guide\n\nFollow `absd/playbook/README.md`.\n",
}


class KitLintTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        for rel, text in BASE.items():
            self.write(rel, text)

    def tearDown(self):
        self.dir.cleanup()

    def write(self, rel, text):
        path = os.path.join(self.root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def append(self, rel, text):
        with open(os.path.join(self.root, *rel.split("/")), "a", encoding="utf-8") as f:
            f.write(text)

    def remove(self, rel):
        os.remove(os.path.join(self.root, *rel.split("/")))

    def run_lint(self, *args):
        out = io.StringIO()
        report = os.path.join(self.root, "report.json")
        if os.path.exists(report):
            os.remove(report)
        with redirect_stdout(out):
            code = kit_lint.main(["--root", self.root, "--json", report, *args])
        data = {}
        if os.path.exists(report):
            with open(report, encoding="utf-8") as f:
                data = json.load(f)
        return code, out.getvalue(), data

    def findings(self, check, level="error"):
        code, out, data = self.run_lint("--only", str(check))
        found = [f for c in data["checks"] for f in c["findings"] if f["level"] == level]
        return code, found, out

    def messages(self, check, level="error"):
        return [f"{f['file']}:{f['line']}: {f['message']}" for f in self.findings(check, level)[1]]

    def assertClean(self, check):
        code, found, out = self.findings(check)
        self.assertEqual((code, found), (0, []), out)

    def assertFlags(self, check, *fragments, count=None):
        code, found, out = self.findings(check)
        self.assertEqual(code, 1, out)
        text = "\n".join(f"{f['file']}:{f['line']}: {f['message']}" for f in found)
        for fragment in fragments:
            self.assertIn(fragment, text)
        if count is not None:
            self.assertEqual(len(found), count, text)
        return found


class BaseKitTests(KitLintTestCase):
    def test_the_base_kit_passes_every_check(self):
        code, out, data = self.run_lint()
        self.assertEqual(code, 0, out)
        self.assertEqual([c["check"] for c in data["checks"]], list(range(1, 10)))
        self.assertTrue(data["passed"])
        self.assertEqual(data["errors"] + data["warnings"], 0)
        self.assertIn("kit_lint: PASS — 0 errors, 0 warnings", out)

    def test_checked_counts_show_the_checks_ran(self):
        _, out, data = self.run_lint()
        checked = {c["check"]: c["checked"] for c in data["checks"]}
        self.assertEqual(checked[1], 4)          # GATE-1, GATE-2, ORACLE-1, FAKE-1 — not the fenced examples
        self.assertEqual(checked[5], 2)          # manager, tester
        self.assertEqual(checked[6], 3)          # GATE, ORACLE, FAKE
        self.assertEqual(checked[8], 6)          # RULES.md, two manuals, three playbook files
        self.assertEqual(checked[9], 2)
        for number in (2, 3, 4, 7):
            self.assertGreater(checked[number], 0, number)
        self.assertIn("✓ 1 playbook rules — 4 rules checked, 0 errors, 0 warnings", out)


class PlaybookRuleTests(KitLintTestCase):
    def test_a_rule_without_provenance_is_an_error(self):
        self.append("absd/playbook/testing/gates.md", "\n**GATE-3** — Gate coverage.\n- *Why:* drift.\n")
        self.assertFlags(1, "absd/playbook/testing/gates.md:23: GATE-3 has no Provenance line", count=1)

    def test_provenance_after_sub_headings_and_tables_belongs_to_the_rule(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Gate coverage.\n\n### Thresholds\n\n| Gate | Floor |\n|---|---|\n| total | 80 |\n\n"
                    "- *Provenance:* industry baseline\n")
        self.assertClean(1)

    def test_a_level_two_heading_ends_the_rule_block(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Gate coverage.\n\n## Reference\n\n- *Provenance:* industry baseline\n")
        self.assertFlags(1, "GATE-3 has no Provenance line", count=1)

    def test_a_level_one_heading_ends_the_rule_block(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Gate coverage.\n\n# Appendix\n\n- *Provenance:* industry baseline\n")
        self.assertFlags(1, "GATE-3 has no Provenance line", count=1)

    def test_the_next_rule_ends_the_block(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Gate coverage.\n\n**GATE-4** — Strict.\n- *Provenance:* industry baseline\n")
        self.assertFlags(1, "GATE-3 has no Provenance line", count=1)

    def test_provenance_spellings(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — a.\n*Provenance:* LL-1\n\n**GATE-4** — b.\nProvenance: industry baseline\n\n"
                    "**GATE-5** — c.\n  - _Provenance:_ LL-2 (SomeProduct, 2026-10)\n\n"
                    "**GATE-6** — d.\n- **Provenance:** industry baseline\n")
        self.assertClean(1)

    def test_an_empty_provenance_line_is_an_error(self):
        self.append("absd/playbook/testing/gates.md", "\n**GATE-3** — a.\n- *Provenance:*\n")
        self.assertFlags(1, "GATE-3 has an empty Provenance line", count=1)

    def test_provenance_inside_a_fence_does_not_count(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — a.\n\n```\n- *Provenance:* industry baseline\n```\n")
        self.assertFlags(1, "GATE-3 has no Provenance line", count=1)

    def test_a_tombstone_needs_no_provenance(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Retired in 1.2.0: superseded by GATE-1.\n- *Applies when:* never — retired\n\n"
                    "**GATE-4** — ~~Old text~~ — retired in v1.2.1, no successor.\n")
        self.assertClean(1)

    def test_a_rule_that_mentions_retired_ids_is_not_a_tombstone(self):
        self.append("absd/playbook/testing/gates.md", "\n**GATE-3** — A link to a retired id fails the run.\n")
        self.assertFlags(1, "GATE-3 has no Provenance line", count=1)

    def test_ids_are_unique_across_the_playbook(self):
        self.append("absd/playbook/testing/oracles.md", "\n**GATE-2** — Again.\n- *Provenance:* industry baseline\n")
        self.assertFlags(1, "absd/playbook/testing/oracles.md:13: GATE-2 is already defined at "
                            "absd/playbook/testing/gates.md:17 — ids are unique", count=1)

    def test_a_code_missing_from_the_routing_table_is_an_error(self):
        self.write("absd/playbook/process/audits.md",
                   "# Audits\n\n## Rules\n\n**XCA-1** — Audit.\n- *Provenance:* industry baseline\n\n"
                   "**XCA-2** — Evidence.\n- *Provenance:* industry baseline\n")
        self.assertFlags(1, "absd/playbook/process/audits.md:5: code XCA is not in the routing table", count=1)

    def test_a_routing_cell_may_hold_several_codes(self):
        self.write("absd/playbook/README.md", README.replace("| `ORACLE`, `FAKE` |", "| **ORACLE**,FAKE |"))
        self.assertClean(1)
        self.write("absd/playbook/README.md", README.replace("| `ORACLE`, `FAKE` |", "| ORACLE |"))
        self.assertFlags(1, "code FAKE is not in the routing table", count=1)

    def test_the_routing_header_may_say_codes(self):
        self.write("absd/playbook/README.md", README.replace("| Topic | Code | File |", "| File | **Codes** | Topic |")
                   .replace("| Gates | GATE |", "| Gates | GATE |"))
        self.assertClean(1)

    def test_codes_in_other_tables_do_not_count_as_routed(self):
        text = README.replace("| Topic | Code | File |", "| Topic | Owner | File |")
        self.write("absd/playbook/README.md", text + "\n| Code | Note |\n| GATE | header row only, no separator |\n")
        self.assertFlags(1, "no routing table", count=1)

    def test_a_missing_readme_is_an_error(self):
        self.remove("absd/playbook/README.md")
        self.assertFlags(1, "absd/playbook/README.md:0: the playbook README (routing table) is missing", count=1)

    def test_numbering_gaps_are_warnings(self):
        self.append("absd/playbook/testing/gates.md", "\n**GATE-5** — Mutation.\n- *Provenance:* industry baseline\n")
        code, found, out = self.findings(1, "warning")
        self.assertEqual(code, 0, out)
        self.assertEqual([f["message"] for f in found],
                         ["GATE numbering has gaps: no GATE-3, GATE-4 (retire with a tombstone, never delete)"])
        self.assertIn("::warning file=absd/playbook/testing/gates.md,line=11,title=kit_lint 1 playbook rules::GATE numbering", out)

    def test_numbering_must_start_at_one(self):
        self.write("absd/playbook/testing/oracles.md", ORACLES.replace("**FAKE-1**", "**FAKE-2**"))
        code, found, _ = self.findings(1, "warning")
        self.assertEqual((code, [f["message"] for f in found]),
                         (0, ["FAKE numbering has gaps: no FAKE-1 (retire with a tombstone, never delete)"]))

    def test_padded_and_zero_ids_are_errors(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-03** — a.\n- *Provenance:* industry baseline\n\n**GATE-0** — b.\n"
                    "- *Provenance:* industry baseline\n")
        self.assertFlags(1, "GATE-03: rule numbers are unpadded integers from 1 (write GATE-3)",
                         "GATE-0: rule numbers are unpadded integers from 1 (numbering starts at 1)", count=2)

    def test_definitions_inside_fences_are_not_rules(self):
        _, _, data = self.run_lint("--only", "1")
        self.assertEqual(data["checks"][0]["checked"], 4)

    def test_a_definition_needs_the_bold_id_at_the_line_start(self):
        self.append("absd/playbook/testing/gates.md", "\nSee **GATE-7** — not a definition.\n GATE-8 neither.\n")
        code, found, _ = self.findings(1, "warning")
        self.assertEqual((code, found), (0, []))

    def test_an_empty_playbook_is_an_error(self):
        self.write("absd/playbook/testing/gates.md", "# Gates\n")
        self.write("absd/playbook/testing/oracles.md", "# Oracles\n")
        self.assertFlags(1, "absd/playbook:0: no rules", count=1)


class CitationTests(KitLintTestCase):
    def test_prefixed_and_bare_citations_of_undefined_ids(self):
        self.append("absd/RULES.md", "\nSee ABSD:GATE-9, GATE-8 and ABSD:FOO-1; FOO-2 is a product id.\n")
        self.assertFlags(2, "absd/RULES.md:5: ABSD:GATE-9 is not defined", "absd/RULES.md:5: GATE-8 is not defined",
                         "absd/RULES.md:5: ABSD:FOO-1 is not defined", count=3)

    def test_a_code_known_only_from_the_routing_table_is_a_playbook_code(self):
        self.write("absd/playbook/README.md", README.replace(
            "| Gates | GATE |", "| Requirements | ELIC | `absd/playbook/process/requirements.md` |\n| Gates | GATE |"))
        self.append("absd/RULES.md", "\nApply ELIC-1.\n")
        self.assertFlags(2, "ELIC-1 is not defined", count=1)

    def test_ranges_cite_both_endpoints(self):
        self.append("absd/RULES.md", "\nGATE-1..2, GATE-1–2, GATE-1 … 2 and GATE-1—2 are fine; GATE-1..7 is not.\n")
        self.assertFlags(2, "GATE-7 is not defined", count=1)

    def test_an_id_inside_a_longer_token_is_not_a_citation(self):
        self.append("absd/RULES.md", "\nEXT-GATE-9, XGATE-9, GATE-9a, GATE_9 and gate-9 cite nothing.\n")
        self.assertClean(2)

    def test_fenced_code_is_ignored(self):
        self.append("absd/RULES.md", "\n```\nGATE-9\n```\n~~~\nABSD:GATE-8\n~~~\n")
        self.assertClean(2)

    def test_citing_a_tombstone_is_an_error_outside_history(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Retired in 1.2.0: superseded by GATE-1 (was GATE-3).\n- *Why:* unchanged\n")
        self.append("absd/RULES.md", "\nApply ABSD:GATE-3.\n")
        self.append("absd/CHANGELOG.md", "\n- GATE-3 retired.\n")
        self.append("absd/lessons/LEDGER.md", "| LL-3 | 2026-10-14 | SomeProduct | retired GATE-3 |\n")
        self.append("absd/playbook/testing/oracles.md", "\nNever GATE-3.\n")
        self.assertFlags(2, "absd/RULES.md:5: ABSD:GATE-3 is retired (absd/playbook/testing/gates.md:23)",
                         "absd/playbook/testing/oracles.md:13: GATE-3 is retired", count=2)

    def test_a_tombstone_block_may_not_cite_its_own_id_below_the_tombstone_line(self):
        self.append("absd/playbook/testing/gates.md",
                    "\n**GATE-3** — Retired in 1.2.0: no successor.\n- *Why:* GATE-3 was noise.\n")
        self.assertFlags(2, "absd/playbook/testing/gates.md:24: GATE-3 is retired", count=1)

    def test_scope_includes_manuals_mirrors_and_root_files(self):
        for rel in (".claude/agents/manager.md", ".github/agents/Tester.agent.md", "README.md", "CLAUDE.md",
                    "absd/templates/project/context.md"):
            self.append(rel, "\nSee GATE-9.\n") if os.path.exists(os.path.join(self.root, rel)) \
                else self.write(rel, "See GATE-9.\n")
        self.write(".github/copilot-instructions.md", "See GATE-9.\n")
        found = self.assertFlags(2, count=6)
        self.assertEqual(sorted(f["file"] for f in found),
                         sorted([".claude/agents/manager.md", ".github/agents/Tester.agent.md", "README.md",
                                 "CLAUDE.md", "absd/templates/project/context.md", ".github/copilot-instructions.md"]))

    def test_inbox_proposals_and_non_markdown_files_are_out_of_scope(self):
        self.write("absd/lessons/inbox/idea-2026-10-14.md", "Proposal citing GATE-9 and LL-99 and `absd/nope.md`.\n")
        self.write("absd/templates/project/notes.txt", "GATE-9\n")
        self.write("docs/other.md", "GATE-9\n")
        self.write(".claude/agents/sub/deep.md", "GATE-9\n")
        code, out, _ = self.run_lint("--only", "2,3,4")
        self.assertEqual(code, 0, out)


class LedgerTests(KitLintTestCase):
    def test_an_unknown_ll_id_is_an_error(self):
        self.append("absd/RULES.md", "\nFrom LL-1, LL-2 and LL-7; LL-n is a placeholder; XLL-9 and LL-9b are not ids.\n")
        self.assertFlags(3, "absd/RULES.md:5: LL-7 has no row \"| LL-7 |\" in absd/lessons/LEDGER.md", count=1)

    def test_ranges_cite_both_endpoints(self):
        self.append("absd/CHANGELOG.md", "\nLedger: LL-1 … LL-2, LL-1..2, LL-1–5.\n")
        self.assertFlags(3, "LL-5 has no row", count=1)

    def test_fenced_code_is_ignored(self):
        self.append("CLAUDE.md", "\n```\nLL-77\n```\n")
        self.assertClean(3)

    def test_duplicate_ledger_rows_are_errors(self):
        self.append("absd/lessons/LEDGER.md", "|  LL-2  | 2026-10-14 | Other | again |\n")
        self.assertFlags(3, "absd/lessons/LEDGER.md:9: LL-2 already has a row at line 8", count=1)

    def test_a_row_must_start_with_the_id(self):
        self.append("absd/lessons/LEDGER.md", "| note | LL-3 is mentioned, not defined |\n")
        self.assertFlags(3, "LL-3 has no row", count=1)

    def test_a_missing_ledger_is_an_error(self):
        self.remove("absd/lessons/LEDGER.md")
        self.assertFlags(3, "the lessons ledger is missing", count=1)


class PathTests(KitLintTestCase):
    def test_missing_paths_are_errors(self):
        self.append("absd/RULES.md", "\n`absd/nope.md`, `.claude/agents/ghost.md`, `.github/workflows/kit.yml`.\n")
        self.assertFlags(4, "absd/RULES.md:5: `absd/nope.md` does not exist",
                         "`.claude/agents/ghost.md` does not exist", "`.github/workflows/kit.yml` does not exist",
                         count=3)

    def test_existing_files_and_directories_pass(self):
        self.write(".github/workflows/kit.yml", "name: kit\n")
        self.append("absd/RULES.md", "\n`absd/playbook/` `absd/playbook` `.github/workflows/kit.yml` "
                                     "`absd/RULES.md#3-immutable-rules` ` absd/VERSION `\n")
        self.assertClean(4)

    def test_placeholders_and_product_paths_are_skipped(self):
        self.append("absd/RULES.md",
                    "\n`absd/<x>.md` `absd/tooling/*.py` `absd/a b.md` `absd/{x}` `absd/$X` `absd/…` "
                    "`absd/tooling/absd_sync.py check` `absd-project/context.md` `absd/../absd-project/x` "
                    "`absd/working/brd.md` `absd/archive/001/` `.claude/working/context.md` `.claude/archive/x` "
                    "`.claude/settings.json` `.claude/settings.local.json` `.github/instructions/p.instructions.md` "
                    "`docs/testing/TESTING.md` `src/absd/x`\n")
        self.assertClean(4)

    def test_the_case_must_match_exactly(self):
        self.append("absd/RULES.md", "\n`absd/rules.md` and `ABSD/RULES.md`\n")
        self.assertFlags(4, "`absd/rules.md` does not exist", count=1)

    def test_parent_directory_steps_are_refused(self):
        self.append("absd/RULES.md", "\n`absd/../absd/RULES.md`\n")
        self.assertFlags(4, "`absd/../absd/RULES.md` does not exist", count=1)

    def test_a_file_is_not_a_directory(self):
        self.append("absd/RULES.md", "\n`absd/RULES.md/x`\n")
        self.assertFlags(4, "`absd/RULES.md/x` does not exist", count=1)

    def test_fenced_code_is_ignored(self):
        self.append("absd/RULES.md", "\n```bash\n`absd/nope.md`\n```\n")
        self.assertClean(4)


class MirrorTests(KitLintTestCase):
    def test_a_manual_without_a_mirror_is_an_error(self):
        self.write(".claude/agents/builder.md", "# Builder\n")
        self.assertFlags(5, ".claude/agents/builder.md:0: no Copilot mirror .github/agents/Builder.agent.md", count=1)

    def test_a_mirror_must_point_to_its_manual(self):
        self.write(".github/agents/Tester.agent.md", MIRROR.format(Name="Tester", name="manager"))
        self.assertFlags(5, ".github/agents/Tester.agent.md:0: the mirror does not point to its manual "
                            "`.claude/agents/tester.md`", count=1)

    def test_a_mirror_without_a_manual_is_an_error(self):
        self.write(".github/agents/Auditor.agent.md", MIRROR.format(Name="Auditor", name="auditor"))
        self.assertFlags(5, ".github/agents/Auditor.agent.md:0: no manual .claude/agents/auditor.md", count=1)

    def test_names_match_ignoring_case(self):
        self.remove(".github/agents/Tester.agent.md")
        self.write(".github/agents/TESTER.agent.md", MIRROR.format(Name="Tester", name="tester"))
        self.assertClean(5)

    def test_no_mirrors_at_all_is_an_error_per_manual(self):
        self.remove(".github/agents/Tester.agent.md")
        self.remove(".github/agents/Manager.agent.md")
        self.assertFlags(5, "no Copilot mirror .github/agents/Manager.agent.md",
                         "no Copilot mirror .github/agents/Tester.agent.md", count=2)

    def test_no_manuals_is_an_error(self):
        for name in ("manager", "tester"):
            self.remove(f".claude/agents/{name}.md")
            self.remove(f".github/agents/{name.title()}.agent.md")
        self.assertFlags(5, ".claude/agents:0: no agent manuals", count=1)

    def test_other_files_in_the_agent_folders_are_ignored(self):
        self.write(".github/agents/README.md", "notes\n")
        self.write(".claude/agents/notes.txt", "notes\n")
        self.assertClean(5)


class ReservedCodeTests(KitLintTestCase):
    def test_a_playbook_code_missing_from_the_reserved_codes_is_an_error(self):
        self.write("absd/playbook/README.md", README.replace("`FAKE` ", ""))
        self.assertFlags(6, "absd/playbook/README.md:18: playbook code FAKE is not in the reserved codes", count=1)

    def test_the_paragraph_may_wrap_and_use_commas(self):
        self.write("absd/playbook/README.md", README.replace(
            "Reserved codes: `GATE` `ORACLE` `FAKE` `TC` `DEF`", "Reserved codes (no product area may use them):\nGATE,\nORACLE, FAKE, TC"))
        self.assertClean(6)

    def test_codes_after_the_paragraph_do_not_count(self):
        self.write("absd/playbook/README.md", README.replace("`FAKE` ", "") + "\nFAKE\n")
        self.assertFlags(6, "FAKE is not in the reserved codes", count=1)

    def test_codes_before_the_label_do_not_count(self):
        self.write("absd/playbook/README.md", README.replace(
            "Reserved codes: `GATE` `ORACLE` `FAKE` `TC` `DEF`", "FAKE\nReserved codes: `GATE` `ORACLE`"))
        self.assertFlags(6, "FAKE is not in the reserved codes", count=1)

    def test_a_routing_only_code_must_be_reserved_too(self):
        self.write("absd/playbook/README.md", README.replace(
            "| Gates | GATE |", "| Requirements | ELIC | `absd/playbook/process/requirements.md` |\n| Gates | GATE |"))
        self.assertFlags(6, "playbook code ELIC is not in the reserved codes", count=1)

    def test_a_heading_is_not_the_paragraph(self):
        self.write("absd/playbook/README.md", README.replace(
            "Reserved codes: `GATE` `ORACLE` `FAKE` `TC` `DEF`", "## Reserved codes\n\nGATE ORACLE FAKE"))
        self.assertFlags(6, "no \"Reserved codes\" paragraph", count=1)

    def test_the_label_is_case_sensitive(self):
        self.write("absd/playbook/README.md", README.replace("Reserved codes:", "reserved codes:"))
        self.assertFlags(6, "no \"Reserved codes\" paragraph", count=1)

    def test_a_missing_readme_is_an_error(self):
        self.remove("absd/playbook/README.md")
        self.assertFlags(6, "the playbook README (reserved codes) is missing", count=1)


class StackWordTests(KitLintTestCase):
    def test_a_line_naming_one_stack_is_an_error(self):
        self.append("absd/RULES.md", "\nRun the suite with pytest before merging.\n")
        self.assertFlags(7, "absd/RULES.md:5: names one stack (pytest)", count=1)

    def test_an_illustration_naming_two_stacks_passes(self):
        self.append("absd/RULES.md", "\nParameterize (e.g. xUnit `[Theory]`, pytest `parametrize`).\n")
        self.assertClean(7)

    def test_a_wrapped_list_item_or_paragraph_counts_as_one_block(self):
        self.append("absd/RULES.md", "\n- Skip markers are banned (e.g. xUnit `Skip=`,\n  Jest `it.skip`).\n\n"
                                     "A paragraph naming Docker\nand Kubernetes on two lines.\n")
        self.assertClean(7)

    def test_separate_blocks_are_judged_separately(self):
        self.append("absd/RULES.md", "\n- Use Docker.\n- Use Kubernetes.\n\n| Kafka | queue |\n| Redis | cache |\n"
                                     "## Deploy to Azure\nThen AWS.\n")
        self.assertFlags(7, "absd/RULES.md:5: names one stack (Docker)", "absd/RULES.md:6: names one stack (Kubernetes)",
                         "absd/RULES.md:8: names one stack (Kafka)", "absd/RULES.md:9: names one stack (Redis)",
                         "absd/RULES.md:10: names one stack (Azure)", "absd/RULES.md:11: names one stack (AWS)",
                         count=6)

    def test_matching_is_whole_word_and_case_sensitive(self):
        self.append("absd/RULES.md", "\nCycle C### and react to change; express intent; a pit stop; JavaScripted.\n")
        self.assertClean(7)
        self.append("absd/RULES.md", "\nWrite JavaScript.\n\nOn ASP.NET only.\n\nC#, alone.\n")
        found = self.assertFlags(7, "names one stack (JavaScript)", "names one stack (ASP.NET)",
                                 "names one stack (C#)", count=3)
        self.assertEqual([f["line"] for f in found], [7, 9, 11])

    def test_neutral_phrases_are_not_stacks(self):
        self.append("absd/RULES.md", "\nReports in JUnit XML or the JUnit format.\n")
        self.assertClean(7)

    def test_project_words_are_errors_even_in_a_two_stack_line(self):
        self.append("absd/RULES.md", "\nLike katenatsiotipster (React, Vue) and the dbforge.eu feed and GEMINI OCR.\n")
        self.assertFlags(7, "absd/RULES.md:5: names a real product (GEMINI, dbforge.eu, katenatsiotipster)", count=1)

    def test_a_project_word_at_a_sentence_end_is_named_without_punctuation(self):
        self.append("absd/RULES.md", "\nAs seen at dbforge.\n")
        self.assertFlags(7, "names a real product (dbforge) —", count=1)

    def test_provenance_lines_and_their_continuations_are_exempt(self):
        self.append("absd/RULES.md", "\n- *Provenance:* LL-1 (KatenatsioTipster, 2026-10), its dbforge feed,\n"
                                     "  and its Postgres database.\n- Next item names Postgres.\n")
        self.assertFlags(7, "absd/RULES.md:7: names one stack (Postgres)", count=1)

    def test_lines_before_a_provenance_line_in_a_block_are_checked(self):
        self.append("absd/RULES.md", "\nUse Redis here.\nProvenance: Python and Katenatsio.\n")
        self.assertFlags(7, "absd/RULES.md:5: names one stack (Redis)", count=1)

    def test_exempt_places(self):
        self.write("absd/tooling/README.md", "Python 3.9+, stdlib only.\n")
        self.write("absd/lessons/notes.md", "dbforge served China time; Postgres.\n")
        self.append("absd/CHANGELOG.md", "\n- Katenatsio lessons; Python tools.\n")
        self.append("absd/RULES.md", "\n```bash\npython3 -m pytest  # Python\n```\n")
        self.write(".claude/agents/manager.md", "---\nname: manager\nmodel: Python\n---\n\n# Manager\n")
        self.assertClean(7)

    def test_an_unclosed_frontmatter_is_not_frontmatter(self):
        self.write(".claude/agents/manager.md", "---\nname: manager on Docker\n")
        self.assertFlags(7, ".claude/agents/manager.md:2: names one stack (Docker)", count=1)

    def test_only_a_frontmatter_on_line_one_counts(self):
        self.write(".claude/agents/manager.md", "# Manager\n---\nUse Docker\n---\n")
        self.assertFlags(7, "names one stack (Docker)", count=1)

    def test_a_dot_word_needs_a_boundary(self):
        self.append("absd/RULES.md", "\nNode.jsx and X.NET and ..NET are not stacks.\n")
        self.assertClean(7)

    def test_the_word_lists_are_well_formed(self):
        self.assertEqual(len(set(kit_lint.STACK_WORDS)), len(kit_lint.STACK_WORDS))
        for word in ("C#", "Playwright", "EF Core", "Node.js", ".NET", "Testcontainers", "Pa11y", "k6"):
            self.assertIn(word, kit_lint.STACK_WORDS)
        self.assertEqual(set(kit_lint.PROJECT_WORDS), {"dbforge", "Gemini", "Katenatsio"})


class BudgetTests(KitLintTestCase):
    def test_rules_budget(self):
        self.write("absd/RULES.md", "x" * 16000)
        self.assertClean(8)
        self.write("absd/RULES.md", "x" * 16001)
        self.assertFlags(8, "absd/RULES.md:0: 16001 characters — 1 over the 16000-character budget", count=1)

    def test_budgets_count_characters_not_bytes(self):
        self.write("absd/RULES.md", "é" * 16000)
        self.assertClean(8)

    def test_agent_manual_budget(self):
        self.write(".claude/agents/tester.md", "x" * 36000)
        self.assertClean(8)
        self.write(".claude/agents/tester.md", "x" * 36001)
        self.assertFlags(8, ".claude/agents/tester.md:0: 36001 characters", count=1)

    def test_playbook_budget_at_any_depth(self):
        self.write("absd/playbook/testing/deep/more.md", "x" * 20000)
        self.assertClean(8)
        self.write("absd/playbook/testing/deep/more.md", "x" * 20001)
        self.write("absd/playbook/README.md", README + "x" * 20001)
        self.assertFlags(8, "absd/playbook/testing/deep/more.md:0: 20001 characters",
                         "absd/playbook/README.md:0:", count=2)

    def test_other_files_have_no_budget(self):
        self.write("absd/templates/project/context.md", "x" * 40000)
        self.write(".github/agents/Tester.agent.md", MIRROR.format(Name="Tester", name="tester") + "x" * 40000)
        self.write("README.md", "x" * 40000)
        self.assertClean(8)

    def test_a_missing_rules_file_is_an_error(self):
        self.remove("absd/RULES.md")
        self.assertFlags(8, "absd/RULES.md:0: the canonical rules file is missing", count=1)


class VersionTests(KitLintTestCase):
    def test_version_must_be_semver(self):
        for bad in ("1.2", "v1.2.3", "01.2.3", "1.2.3-rc1", "1.2.3.4", ""):
            self.write("absd/VERSION", bad + "\n")
            self.assertFlags(9, f"absd/VERSION:1: '{bad}' is not a semantic version x.y.z", count=1)

    def test_the_first_entry_must_name_the_version(self):
        self.write("absd/VERSION", "1.2.2\n")
        self.assertFlags(9, "absd/CHANGELOG.md:5: the newest entry \"## 1.2.3 — 2026-10-14\" does not name "
                            "absd/VERSION 1.2.2", count=1)

    def test_heading_spellings(self):
        for heading in ("## [1.2.3] - 2026-10-14", "## v1.2.3", "## 1.2.3", "## Version 1.2.3 (minor)"):
            self.write("absd/CHANGELOG.md", f"# Changelog\n\n{heading}\n")
            self.assertClean(9)
        for heading in ("## 11.2.3", "## 1.2.30", "## 1.2.3.4", "## 21.2.3", "### 1.2.3\n## 1.2.4"):
            self.write("absd/CHANGELOG.md", f"# Changelog\n\n{heading}\n")
            self.assertFlags(9, "does not name absd/VERSION 1.2.3", count=1)

    def test_a_heading_inside_a_fence_does_not_count(self):
        self.write("absd/CHANGELOG.md", "# Changelog\n\n```\n## 1.2.3\n```\n\n## 1.2.4\n")
        self.assertFlags(9, "absd/CHANGELOG.md:7:", count=1)

    def test_a_changelog_without_entries_is_an_error(self):
        self.write("absd/CHANGELOG.md", "# Changelog\n\nNothing yet.\n")
        self.assertFlags(9, "absd/CHANGELOG.md:0: no \"## <version>\" entry", count=1)

    def test_both_files_are_required(self):
        self.remove("absd/VERSION")
        self.assertFlags(9, "absd/VERSION:0: the kit version file is missing", count=1)
        self.remove("absd/CHANGELOG.md")
        self.assertFlags(9, "absd/VERSION:0", "absd/CHANGELOG.md:0: the changelog is missing", count=2)


class CommandLineTests(KitLintTestCase):
    def test_a_root_without_absd_is_a_usage_error(self):
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        out = io.StringIO()
        with redirect_stdout(out):
            code = kit_lint.main(["--root", empty.name])
        self.assertEqual(code, 2)
        self.assertIn("has no absd/ directory", out.getvalue())

    def test_bad_only_values_are_usage_errors(self):
        for value in ("x", "10", "0", "1,,2", ""):
            code, out, _ = self.run_lint("--only", value)
            self.assertEqual(code, 2, value)
            self.assertIn("--only", out)

    def test_only_selects_checks(self):
        self.append("absd/RULES.md", "\nGATE-9 and LL-9.\n")
        code, out, data = self.run_lint("--only", "3", "--only", "1, 9")
        self.assertEqual([c["check"] for c in data["checks"]], [1, 3, 9])
        self.assertEqual(code, 1)
        self.assertNotIn("GATE-9", out)
        self.assertIn("LL-9", out)
        code, out, data = self.run_lint("--only", "1")
        self.assertEqual(code, 0, out)

    def test_annotation_format(self):
        self.append("absd/RULES.md", "\nSee ABSD:GATE-9.\n")
        code, out, _ = self.run_lint("--only", "2")
        self.assertIn("::error file=absd/RULES.md,line=5,title=kit_lint 2 citations::ABSD:GATE-9 is not defined in "
                      "the playbook\n", out)
        self.assertRegex(out, r"\n✗ 2 citations — \d+ citations checked, 1 errors, 0 warnings\n")
        self.assertIn("kit_lint: FAIL — 1 errors, 0 warnings (checks 2)", out)

    def test_a_whole_file_annotation_has_no_line(self):
        self.remove("absd/VERSION")
        _, out, _ = self.run_lint("--only", "9")
        self.assertIn("::error file=absd/VERSION,title=kit_lint 9 version::the kit version file is missing", out)

    def test_annotation_escaping(self):
        finding = kit_lint.Finding(4, "error", "a,b:c%.md", 3, "100% done\nnext")
        self.assertEqual(finding.annotation(),
                         "::error file=a%2Cb%3Ac%25.md,line=3,title=kit_lint 4 paths::100%25 done%0Anext")
        self.assertEqual(kit_lint.escape_data("a\rb"), "a%0Db")

    def test_warnings_alone_pass(self):
        self.append("absd/playbook/testing/gates.md", "\n**GATE-4** — a.\n- *Provenance:* industry baseline\n")
        code, out, data = self.run_lint()
        self.assertEqual(code, 0, out)
        self.assertEqual((data["errors"], data["warnings"], data["passed"]), (0, 1, True))
        self.assertIn("kit_lint: PASS — 0 errors, 1 warnings", out)

    def test_json_lists_every_finding(self):
        self.append("absd/RULES.md", "\nGATE-9 and LL-9.\n")
        code, _, data = self.run_lint("--only", "2,3")
        self.assertEqual(code, 1)
        self.assertEqual(data["errors"], 2)
        self.assertFalse(data["passed"])
        self.assertEqual(data["root"], self.root)
        self.assertEqual(data["checks"][0]["findings"],
                         [{"level": "error", "file": "absd/RULES.md", "line": 5,
                           "message": "GATE-9 is not defined in the playbook"}])
        self.assertEqual((data["checks"][1]["name"], data["checks"][1]["errors"]), ("LL ids", 1))

    def test_summary_markdown_and_step_summary(self):
        self.append("absd/RULES.md", "\nGATE-9.\n")
        summary = os.path.join(self.root, "summary.md")
        step = os.path.join(self.root, "step.md")
        self.write("step.md", "earlier step\n")
        os.environ["GITHUB_STEP_SUMMARY"] = step
        self.addCleanup(os.environ.pop, "GITHUB_STEP_SUMMARY", None)
        self.run_lint("--only", "2,9", "--summary-md", summary)
        for path in (summary, step):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("### kit_lint", text)
            self.assertIn("- ✗ 2 citations — ", text)
            self.assertIn("- ✓ 9 version — 2 files checked, 0 errors, 0 warnings", text)
            self.assertIn("- error: `absd/RULES.md:5` — GATE-9 is not defined in the playbook", text)
            self.assertIn("**kit_lint: FAIL — 1 errors, 0 warnings (checks 2, 9)**", text)
        with open(step, encoding="utf-8") as f:
            self.assertTrue(f.read().startswith("earlier step\n"))

    def test_summary_lists_at_most_fifty_findings_per_check(self):
        self.append("absd/RULES.md", "\n" + "\n".join(f"GATE-{n}" for n in range(10, 70)) + "\n")
        summary = os.path.join(self.root, "summary.md")
        self.run_lint("--only", "2", "--summary-md", summary)
        with open(summary, encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text.count("- error: "), 50)
        self.assertIn("- … and 10 more", text)

    def test_an_unreadable_kit_file_is_a_usage_error(self):
        with open(os.path.join(self.root, "absd", "RULES.md"), "wb") as f:
            f.write(b"\xff\xfe\xfa not utf-8")
        code, out, _ = self.run_lint()
        self.assertEqual(code, 2)
        self.assertIn("::error::cannot read absd/RULES.md", out)

    def test_a_byte_order_mark_is_not_content(self):
        with open(os.path.join(self.root, "absd", "VERSION"), "w", encoding="utf-8-sig") as f:
            f.write("1.2.3\n")
        self.assertClean(9)


class HelperTests(unittest.TestCase):
    def test_glob_match(self):
        self.assertTrue(kit_lint.glob_match("absd/playbook/**/*.md", "absd/playbook/README.md"))
        self.assertTrue(kit_lint.glob_match("absd/playbook/**/*.md", "absd/playbook/a/b/c.md"))
        self.assertFalse(kit_lint.glob_match("absd/playbook/**/*.md", "absd/playbookx/c.md"))
        self.assertTrue(kit_lint.glob_match(".claude/agents/*.md", ".claude/agents/tester.md"))
        self.assertFalse(kit_lint.glob_match(".claude/agents/*.md", ".claude/agents/x/tester.md"))
        self.assertFalse(kit_lint.glob_match(".claude/agents/*.md", ".claude/agentsXtester.md"))
        self.assertTrue(kit_lint.glob_match("absd/lessons/**", "absd/lessons/inbox/x.md"))
        self.assertFalse(kit_lint.glob_match("absd/lessons/**", "absd/lessonsX/x.md"))

    def test_fences_need_a_matching_close(self):
        lines = ["a", "````", "```", "b", "````", "c", "~~~", "```", "d", "~~~ trailing", "e", "~~~", "f"]
        self.assertEqual([text for _, text in kit_lint.plain_lines(lines)], ["a", "c", "f"])

    def test_indented_code_fence_up_to_three_spaces(self):
        lines = ["   ```", "x", "   ```", "    ```", "y"]
        self.assertEqual([text for _, text in kit_lint.plain_lines(lines)], ["    ```", "y"])

    def test_blocks(self):
        lines = ["# H", "para one", "para two", "", "- item", "  wrapped", "- next", "| a |", "| b |", "after",
                 "1. numbered", "2) also"]
        self.assertEqual([[n for n, _ in block] for block in kit_lint.blocks(lines)],
                         [[1], [2, 3], [5, 6], [7], [8], [9], [10], [11], [12]])

    def test_blocks_split_at_fences(self):
        lines = ["para", "```", "code", "```", "more"]
        self.assertEqual([[n for n, _ in block] for block in kit_lint.blocks(lines)], [[1], [5]])


if __name__ == "__main__":
    unittest.main()
