#!/usr/bin/env python3
"""Traceability report for any stack that writes JUnit XML: requirements → tests → results.

Answers two questions after a test run:
  1. Acceptance (ABSD playbook TRACE-*): is each requirement in the product's requirement catalogue
     ✅ verified (its tests passed), ❌ failing (one of its tests failed) or ⚪ untested (no test links to it)?
     A test that links to an id the catalogue does not know is an error (typos must not count as proof).
  2. Plan conformance (ABSD playbook TRACE-*): does every test case planned in test_plan.md (TC-nnnn, flat ids with at
     least four digits) exist as a test, and did it pass? Tests carrying TC ids the plan does not list are unplanned.
     The plan is read the way trace_check.py reads it: a TC is planned when it is the first token of a table row's
     first cell or of a heading, outside code fences, and not marked removed/retired; test_plan.md also takes in the
     parts in a directory test_plan/ next to it (a split plan). A plan that plans no TC is an input error.

How tests link (use any; all are read):
  - JUnit properties on the testcase: <property name="requirement" value="ACC-1"/> (repeatable or comma-separated),
    <property name="tc" value="TC-0042"/>. Playwright writes test annotations this way with the junit reporter
    option `embedAnnotationsAsProperties: true`.
  - Tokens in the test name or classname: "[ACC-1]", "[ACC-NF-2]", "[ACC-BR-3]" for requirements and "TC-0042" for
    planned test cases. `test_TC_0042_...` is NOT matched — write the id with hyphens in the display name or a property.

The catalogue is Markdown (a table whose first cell is the requirement id; optional columns Area, Role, Story, Source,
Status — a Status cell starting with "retired" retires it) or JSON ({"requirements": [{"id", "area", "story", "status"}]}).

JUnit XML is written by: pytest --junitxml, dotnet test --logger junit (JunitXml.TestLogger), jest-junit,
vitest --reporter=junit, Playwright junit reporter, go-junit-report/gotestsum, Maven Surefire/Gradle, cargo-nextest.

usage:
  traceability_report.py --junit "test-results/**/*.xml" [--junit ...]
                         [--catalogue absd-project/catalogue.md]
                         [--plan absd-project/working/test_plan.md]
                         [--fail-on failing,unknown,missing] [--json trace.json] [--summary-md trace.md]
Every --junit glob must match at least one file: a suite whose results are missing did not run (ABSD:GATE-1), and is
an input error, not a smaller report.

--fail-on categories: failing  (a requirement or planned test case failed)
                      unknown  (a test links to a requirement id not in the catalogue, or to a retired one)
                      missing  (a planned test case has no test, or only skipped ones)
                      untested (an active catalogue requirement has no test)
                      unplanned (a test carries a TC id the plan does not list)
Exit code: 0 pass, 1 a --fail-on category is non-empty, 2 usage/input error. Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trace_check  # noqa: E402  (one Markdown reading of test_plan.md for both tools)

REQ_ID = r"[A-Z][A-Z0-9]*-(?:NF-|BR-)?\d+"
REQ_TOKEN = re.compile(r"\[(" + REQ_ID + r")\]")
REQ_EXACT = re.compile(r"^" + REQ_ID + r"$")
TC_TOKEN = re.compile(r"\bTC-\d{4,}\b")
# Ids with these prefixes are not requirements (ABSD reserved codes, the same set as trace_check.py): "[DEF-12]" on a
# regression test or "[E2E-1]" citing a playbook rule is not a typo.
PLAYBOOK_CODES = {"STRAT", "VAR", "ORACLE", "ACCESS", "INTEG", "FAKE", "EXT", "E2E", "TRACE", "GATE", "ESC", "EXPL",
                  "A11Y", "PERF", "RESIL", "VIS", "OPS", "TCQ", "DSN", "LOC", "ARCH", "CODE", "SEC", "PRIV", "ELIC",
                  "DOD", "XCA", "ENR"}
# QC is not reserved: it is the fixed area code of the Foundation quality capabilities (catalogue rows QC-n).
RESERVED = PLAYBOOK_CODES | {"TC", "DEF", "CR", "ADR", "UJ", "SCR", "DEBT", "RISK", "EXT", "LL", "AR", "TF", "DQ", "F",
                             "CLR", "WP", "INH", "TSEAM", "CHAR", "C", "A", "OQ", "D", "UXQ", "UXA"}
REQ_PROPERTIES = {"requirement", "requirements", "req"}
TC_PROPERTIES = {"tc", "testcase", "test-case"}
CATEGORIES = ("failing", "unknown", "missing", "untested", "unplanned")


@dataclass
class Case:
    name: str
    classname: str
    status: str                      # passed | failed | skipped
    requirements: set = field(default_factory=set)
    tcs: set = field(default_factory=set)

    @property
    def title(self) -> str:
        return f"{self.classname} › {self.name}" if self.classname else self.name


def case_status(element: ET.Element) -> str:
    if element.find("failure") is not None or element.find("error") is not None:
        return "failed"
    if element.find("skipped") is not None:
        return "skipped"
    return "passed"


def split_values(value: str) -> list[str]:
    return [v for v in re.split(r"[,\s]+", value or "") if v]


def read_junit(patterns: list[str]) -> tuple[list[Case], list[str]]:
    files: set[str] = set()
    for pattern in patterns:
        matched = {p for p in glob.glob(pattern, recursive=True) if os.path.isfile(p)}
        if not matched:
            raise ValueError(f"No JUnit XML files found for: {pattern} (a suite whose results are missing did not run)")
        files |= matched
    files = sorted(files)
    cases: list[Case] = []
    for path in files:
        for element in ET.parse(path).getroot().iter("testcase"):
            case = Case(name=element.get("name", ""), classname=element.get("classname", ""), status=case_status(element))
            for prop in element.iter("property"):
                key = (prop.get("name") or "").strip().lower()
                value = prop.get("value") or (prop.text or "")
                if key in REQ_PROPERTIES:
                    case.requirements.update(split_values(value))
                elif key in TC_PROPERTIES:
                    case.tcs.update(split_values(value))
            text = f"{case.classname} {case.name}"
            case.requirements.update(t for t in REQ_TOKEN.findall(text) if t.split("-")[0] not in RESERVED)
            case.tcs.update(TC_TOKEN.findall(text))
            cases.append(case)
    return cases, files


def read_markdown_catalogue(path: str) -> list[dict]:
    """Rows of every Markdown table whose first cell is a requirement id; columns named by the table's header row."""
    entries, header = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped.startswith("|"):
                header = []
                continue
            cells = [c.strip().strip("*`") for c in stripped.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
                continue
            if REQ_EXACT.match(cells[0]):
                row = {"id": cells[0]}
                for name, value in zip(header[1:], cells[1:]):
                    row[name.lower()] = value
                if re.match(r"retired\b", row.get("status", "").strip(), re.IGNORECASE):
                    row["status"] = "retired"   # e.g. "retired", "Retired — see ACC-9"
                entries.append(row)
            elif not header:
                header = cells
    return entries


def read_catalogue(path: str) -> tuple[list[dict], set[str]]:
    if path.lower().endswith(".md"):
        entries = read_markdown_catalogue(path)
    else:
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)["requirements"]
    seen, duplicates = set(), set()
    for entry in entries:
        if entry["id"] in seen:
            duplicates.add(entry["id"])
        seen.add(entry["id"])
    if duplicates:
        raise ValueError(f"duplicate requirement ids in {path}: {', '.join(sorted(duplicates))}")
    active = [e for e in entries if e.get("status", "active") != "retired"]
    retired = {e["id"] for e in entries if e.get("status", "active") == "retired"}
    return active, retired


def read_plan(path: str) -> list[str]:
    """Planned test cases, in id order: TC ids test_plan.md (and its parts) defines and does not mark removed."""
    try:
        doc = trace_check.load([path], os.path.basename(path))
    except trace_check.InputError as error:
        raise ValueError(str(error)) from error
    planned = sorted(doc.defined("tc"), key=trace_check.natural)
    if not planned:
        raise ValueError(f"{path} plans no test case (no TC-nnnn defined) — nothing to conform to")
    return planned


def verdict(statuses: list[str]) -> str:
    ran = [s for s in statuses if s != "skipped"]
    if not ran:
        return "untested"
    return "failing" if "failed" in ran else "verified"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--junit", action="append", required=True, help="glob of JUnit XML files (repeatable, ** allowed)")
    parser.add_argument("--catalogue", help="requirement catalogue: Markdown table (absd-project/catalogue.md) or JSON "
                                            "with a 'requirements' list")
    parser.add_argument("--plan", help="test_plan.md (plus its test_plan/ parts) whose planned TC-nnnn ids must all "
                                       "exist as tests and pass")
    parser.add_argument("--fail-on", default="failing,unknown,missing", help=f"comma list of: {', '.join(CATEGORIES)}")
    parser.add_argument("--json", dest="json_out")
    parser.add_argument("--summary-md")
    args = parser.parse_args(argv)

    fail_on = {c.strip() for c in args.fail_on.split(",") if c.strip()}
    if fail_on - set(CATEGORIES):
        print(f"::error::unknown --fail-on categories: {', '.join(sorted(fail_on - set(CATEGORIES)))}")
        return 2
    if not args.catalogue and not args.plan:
        print("::error::give --catalogue, --plan, or both")
        return 2

    try:
        cases, files = read_junit(args.junit)
        catalogue, retired = read_catalogue(args.catalogue) if args.catalogue else ([], set())
        planned = read_plan(args.plan) if args.plan else []
    except (OSError, ValueError, KeyError, ET.ParseError, json.JSONDecodeError) as error:
        print(f"::error::{error}")
        return 2

    problems: dict[str, list[str]] = {c: [] for c in CATEGORIES}
    sections: list[str] = []
    report: dict = {"files": files}

    if args.catalogue:
        known = {e["id"] for e in catalogue}
        linked: dict[str, list[Case]] = {}
        for case in cases:
            for req in sorted(case.requirements):
                if req in known:
                    linked.setdefault(req, []).append(case)
                else:
                    why = "retired" if req in retired else "not in the catalogue"
                    problems["unknown"].append(f"{case.title} → {req} ({why})")
        icon = {"verified": "✅", "failing": "❌", "untested": "⚪"}
        counts = {"verified": 0, "failing": 0, "untested": 0}
        rows, entries = [], []
        for entry in catalogue:
            tests = linked.get(entry["id"], [])
            state = verdict([t.status for t in tests])
            counts[state] += 1
            if state == "failing":
                problems["failing"].append(f"requirement {entry['id']}")
            if state == "untested":
                problems["untested"].append(f"requirement {entry['id']}")
            proof = "<br>".join(f"{'✓' if t.status == 'passed' else ('–' if t.status == 'skipped' else '✗')} {t.title}" for t in tests) or "—"
            rows.append(f"| {icon[state]} **{entry['id']}** | {entry.get('area', '')} | {entry.get('story', '')} | {proof} |")
            entries.append({**entry, "state": state, "tests": [{"title": t.title, "status": t.status} for t in tests]})
        sections.append("\n".join([
            f"### Acceptance — {counts['verified']}/{len(catalogue)} requirements verified",
            f"{counts['failing']} failing · {counts['untested']} without a test · catalogue: `{args.catalogue}`",
            "",
            "| Requirement | Area | Story | Proven by |",
            "|---|---|---|---|",
            *rows,
        ]))
        report["acceptance"] = {"total": len(catalogue), **counts, "requirements": entries}

    if args.plan:
        by_tc: dict[str, list[Case]] = {}
        for case in cases:
            for tc in case.tcs:
                by_tc.setdefault(tc, []).append(case)
        states = {}
        for tc in planned:
            statuses = [c.status for c in by_tc.get(tc, [])]
            if not statuses or all(s == "skipped" for s in statuses):
                states[tc] = "missing" if not statuses else "skipped"
                problems["missing"].append(f"{tc} ({states[tc]})")
            elif "failed" in statuses:
                states[tc] = "failed"
                problems["failing"].append(tc)
            else:
                states[tc] = "passed"
        unplanned = sorted(set(by_tc) - set(planned))
        problems["unplanned"].extend(unplanned)
        passing = sum(1 for s in states.values() if s == "passed")
        not_passing = [f"| {tc} | {state} |" for tc, state in states.items() if state != "passed"]
        sections.append("\n".join([
            f"### Test plan conformance — {passing}/{len(planned)} planned test cases passing",
            f"plan: `{args.plan}` · unplanned TC ids in tests: {', '.join(unplanned) or 'none'}",
            *(["", "| Test case | State |", "|---|---|", *not_passing] if not_passing else []),
        ]))
        report["plan"] = {"planned": len(planned), "passing": passing, "states": states, "unplanned": unplanned}

    markdown = "\n\n".join(sections) + "\n"
    print(markdown)
    for target in filter(None, (args.summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(markdown + "\n")

    failed = False
    for category in CATEGORIES:
        if not problems[category]:
            continue
        level = "error" if category in fail_on else "warning"
        failed |= category in fail_on
        print(f"::{level} title={category}::" + "; ".join(problems[category]))
    report["problems"] = problems
    report["passed"] = not failed
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as out:
            json.dump(report, out, ensure_ascii=False, indent=2)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
