#!/usr/bin/env python3
"""ID coverage between ABSD pipeline artifacts, so the Manager gates on mechanical checks instead of reading them.

An id is
  DEFINED in a Markdown file when it is the first token of a table row's first cell, or the first token of a heading's
    text (Markdown decoration ** _ ` [ ] ~ around it is ignored; lines inside ``` / ~~~ code fences are neither).
    A definition is EXCLUDED when its status says "removed" or "retired" (whole word, any case): the row's Status
    cell when its table has a Status column, otherwise the whole row or heading line. An id with at least one
    definition that is not excluded counts as defined.
  REFERENCED in files when it appears anywhere in them as a whole token (ACC-1 is not found in ACC-10 or XACC-1; an
    AC id ACC-1.AC2 also references ACC-1).
A path may be a file or a directory (every *.md inside, recursively); X.md also takes in the parts in a directory X/
when one exists (architecture.md + architecture/NN-*.md). Any artifact may be split that way.

Id families: requirement ACC-1 / ACC-NF-1 / ACC-BR-1 (the area code must not be a reserved code — playbook codes and
TC, DEF, CR, ADR, UJ, SCR, DEBT, RISK, EXT, LL, AR, TF, DQ, F, CLR, WP, INH, TSEAM, CHAR, C, A, OQ, D, UXQ, UXA;
QC is the fixed area code of the Foundation quality capabilities) · ac ACC-1.AC1 ·
uj UJ-1 · scr SCR-1 · ext EXT-PAY-1 · tc TC-0042 (at least four digits) · adr ADR-1 · tseam TSEAM-1 · wp WP-1.

Gates (artifacts read from --working; design.md is optional for gate2 and gateT — its checks are then skipped with a
notice). The requirement source is analysis.md; on routes without it (Mode S without the Analyst: the brief in brd.md;
Mode D: defect.md) the first of brd.md, defect.md that exists is used, with a notice.
  gate1    analysis.md defines at least one requirement; every functional requirement it defines has an AC id in it
           (NF/BR exempt); every requirement it defines is defined in the catalogue (retired rows do not count).
  gate-ux  every UJ and SCR defined in design.md is referenced in its Traceability section (a heading containing
           "Traceability"); every requirement referenced in design.md is defined in the catalogue. Ids whose area code
           the catalogue never uses (UTC-5, SHA-256, ISO-8601) are listed in a notice instead.
  gate2    every requirement defined in analysis.md, every UJ/SCR defined in design.md and every EXT referenced in
           analysis.md is referenced in architecture.md; architecture.md defines at least one WP.
  gateT    test_plan.md defines at least one TC; every AC of a requirement defined in analysis.md (any occurrence of the
           AC id counts, so ACs may sit in list items), every NF and BR requirement defined in analysis.md, every
           UJ/SCR defined in design.md and every EXT referenced in architecture.md is referenced in test_plan.md;
           every TC defined in test_plan.md has an oracle source (SPEC:… FACT:… CHAR:…) on its row or in its heading's
           section; no TSEAM defined in test_plan.md is open (the word "open" in its status).
  gate3    the reports the cycle's route produces exist (read from the "Mode:" line of cycle.md: X → audit.md;
           D → test_report.md, audit.md; any other mode, or no cycle.md → arch_review.md, test_report.md, audit.md;
           design_review.md and an arch_review.md the route does not require are read when present) and hold no open
           blocking finding. A finding is a table row whose first cell holds an id (F-3, AR-2, TF-12, DQ-1) in a table
           with a Severity column; it is open when its severity is Critical or Major and no row with the same id in
           that file says fixed, resolved or accepted-by-user in a Status, Route or Resolution column.

usage:
  trace_check.py gate {gate1,gate-ux,gate2,gateT,gate3} [--working absd-project/working]
                 [--catalogue absd-project/catalogue.md] [--json OUT] [--summary-md OUT]
  trace_check.py check --ids {requirement,ac,uj,scr,ext,tc,adr,tseam,wp} --defined-in FILE[,FILE...]
                 --referenced-in FILE[,FILE...] [--json OUT] [--summary-md OUT]

Output: one line per check — "✓ <check> (<n> checked)" or "✗ <check>: <n> missing — ID1, ID2" — then GitHub
annotations (::error:: per failed check, ::notice:: / ::warning:: for skipped or suspicious input) and a verdict line.
--summary-md writes the same as Markdown (also appended to $GITHUB_STEP_SUMMARY); --json writes every check.

Exit code: 0 pass, 1 a check failed, 2 usage/input error. Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

PLAYBOOK_CODES = {"STRAT", "VAR", "ORACLE", "ACCESS", "INTEG", "FAKE", "EXT", "E2E", "TRACE", "GATE", "ESC", "EXPL",
                  "A11Y", "PERF", "RESIL", "VIS", "OPS", "TCQ", "DSN", "LOC", "ARCH", "CODE", "SEC", "PRIV", "ELIC",
                  "DOD", "XCA", "ENR"}
# Product area codes may not use these (contract §9), so "[UJ-3]" or "ABSD:CODE-4" is never a requirement.
# QC is not reserved: it is the fixed area code of the Foundation quality capabilities (catalogue rows QC-n).
RESERVED = PLAYBOOK_CODES | {"TC", "DEF", "CR", "ADR", "UJ", "SCR", "DEBT", "RISK", "EXT", "LL", "AR", "TF", "DQ", "F",
                             "CLR", "WP", "INH", "TSEAM", "CHAR", "C", "A", "OQ", "D", "UXQ", "UXA"}

REQUIREMENT = r"[A-Z][A-Z0-9]*-(?:NF-|BR-)?\d+"
FAMILIES = {                      # family -> (display name, id pattern)
    "requirement": ("requirement", REQUIREMENT),
    "ac": ("AC", REQUIREMENT + r"\.AC\d+"),
    "uj": ("UJ", r"UJ-\d+"),
    "scr": ("SCR", r"SCR-\d+"),
    "ext": ("EXT", r"EXT-[A-Z][A-Z0-9]*-\d+"),
    "tc": ("TC", r"TC-\d{4,}"),
    "adr": ("ADR", r"ADR-\d+"),
    "tseam": ("TSEAM", r"TSEAM-\d+"),
    "wp": ("WP", r"WP-\d+"),
}
EXACT = {family: re.compile(pattern) for family, (_, pattern) in FAMILIES.items()}
WHOLE_TOKEN = {family: re.compile(r"(?<![A-Za-z0-9_-])" + pattern + r"(?![A-Za-z0-9_])")
               for family, (_, pattern) in FAMILIES.items()}

DECORATION = "*_`[]~ \t"
TOKEN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
NON_FUNCTIONAL = re.compile(r"-(?:NF|BR)-")
EXCLUDED = re.compile(r"\b(?:removed|retired)\b", re.IGNORECASE)
OPEN = re.compile(r"\bopen\b", re.IGNORECASE)
ORACLE_SOURCE = re.compile(r"\b(?:SPEC|FACT|CHAR):[ \t]*[^\s|]")
FINDING_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b")
CLOSED = re.compile(r"\b(?:fixed|resolved|accepted-by-user)\b", re.IGNORECASE)
BLOCKING = ("critical", "major")
GATE3_REQUIRED = ("arch_review.md", "test_report.md", "audit.md")      # Mode F, S, B, C, R — and when unknown
GATE3_BY_MODE = {"X": ("audit.md",), "D": ("test_report.md", "audit.md")}
GATE3_OPTIONAL = ("arch_review.md", "test_report.md", "design_review.md")
REQUIREMENT_SOURCES = ("analysis.md", "brd.md", "defect.md")
MODE_LINE = re.compile(r"\bMode:\s*\**\s*([A-Z])\b")


class InputError(Exception):
    """A missing or unreadable input: exit code 2."""


# --- ids --------------------------------------------------------------------------------------------------------------

def in_family(token: str, family: str) -> bool:
    if not EXACT[family].fullmatch(token):
        return False
    return family not in ("requirement", "ac") or token.split("-")[0] not in RESERVED


def requirement_of(ac: str) -> str:
    return ac.rsplit(".AC", 1)[0]


def natural(token: str) -> list:
    """Sort key: ACC-2 before ACC-10."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", token)]


def first_token(text: str) -> str:
    match = TOKEN.match(text.lstrip(DECORATION))
    return match.group(0) if match else ""


# --- Markdown ---------------------------------------------------------------------------------------------------------

@dataclass
class Definition:
    """One place an id is defined: a table row (first cell) or a heading (first token)."""
    id: str
    status: str    # decides removed/retired/open: the row's Status cell if its table has one, else the whole line
    context: str   # the row, or the heading's whole section (where an oracle source may sit)

    @property
    def excluded(self) -> bool:
        return bool(EXCLUDED.search(self.status))


@dataclass
class Table:
    header: list   # lower-cased header cells; [] when the table has no separator row under its first row
    rows: list     # data rows, each a list of cells


@dataclass
class Doc:
    """An artifact: one file, or an index plus its parts."""
    label: str
    text: str = ""
    definitions: list = field(default_factory=list)
    sections: list = field(default_factory=list)   # (heading text, section text incl. sub-headings)
    tables: list = field(default_factory=list)

    def defined(self, family: str) -> set:
        return {d.id for d in self.definitions if in_family(d.id, family) and not d.excluded}

    def excluded(self, family: str) -> set:
        """Ids whose every definition is marked removed/retired."""
        return {d.id for d in self.definitions if in_family(d.id, family)} - self.defined(family)

    def referenced(self, family: str) -> set:
        return referenced_in(self.text, family)


def referenced_in(text: str, family: str) -> set:
    return {token for token in WHOLE_TOKEN[family].findall(text) if in_family(token, family)}


def structural_lines(lines: list[str]) -> list[bool]:
    """False for the lines of a ``` / ~~~ code fence: they are neither headings nor table rows."""
    flags, fence = [], ""
    for line in lines:
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                    and not line[match.end():].strip():
                fence = ""
            flags.append(False)
        elif match:
            fence = match.group(1)
            flags.append(False)
        else:
            flags.append(True)
    return flags


def split_cells(line: str) -> list[str]:
    """The cells of a table row; an escaped pipe (\\|) stays inside its cell. A closing pipe adds one empty cell."""
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip())][1:]


def is_separator(cells: list[str]) -> bool:
    filled = [cell for cell in cells if cell]
    return bool(filled) and all(SEPARATOR_CELL.match(cell) for cell in filled)


def cell_at(cells: list[str], index: int) -> str:
    return cells[index] if index < len(cells) else ""


def table_blocks(lines: list[str], structural: list[bool]) -> list[list[str]]:
    blocks, current = [], []
    for line, plain in zip(lines, structural):
        if plain and line.strip().startswith("|"):
            current.append(line)
            continue
        if current:
            blocks.append(current)
        current = []
    if current:
        blocks.append(current)
    return blocks


def parse_table(block: list[str]) -> tuple[Table, list[Definition]]:
    rows = [split_cells(line) for line in block]
    header, first = [], 0
    if len(rows) > 1 and is_separator(rows[1]):
        header, first = [cell.strip(DECORATION).lower() for cell in rows[0]], 2
    status_columns = [index for index, name in enumerate(header) if "status" in name]
    table, definitions = Table(header, []), []
    for line, cells in zip(block[first:], rows[first:]):
        table.rows.append(cells)
        token = first_token(cells[0])
        if token:
            status = " ".join(cell_at(cells, i) for i in status_columns) if status_columns else line
            definitions.append(Definition(token, status, line))
    return table, definitions


def heading_sections(lines: list[str], structural: list[bool]) -> list[tuple[str, str, str]]:
    """(heading line, heading text, section text) — a section runs to the next heading of the same or higher level."""
    headings = []
    for number, line in enumerate(lines):
        match = HEADING.match(line) if structural[number] else None
        if match:
            headings.append((number, len(match.group(1)), (match.group(2) or "").strip()))
    sections = []
    for k, (start, level, text) in enumerate(headings):
        end = next((number for number, other, _ in headings[k + 1:] if other <= level), len(lines))
        sections.append((lines[start], text, "\n".join(lines[start:end])))
    return sections


def parse(text: str, doc: Doc) -> None:
    """Add one file's text, definitions, sections and tables to doc."""
    lines = text.splitlines()
    structural = structural_lines(lines)
    doc.text += text + "\n"
    for line, heading, section in heading_sections(lines, structural):
        doc.sections.append((heading, section))
        token = first_token(heading)
        if token:
            doc.definitions.append(Definition(token, line, section))
    for block in table_blocks(lines, structural):
        table, definitions = parse_table(block)
        doc.tables.append(table)
        doc.definitions += definitions


# --- inputs -----------------------------------------------------------------------------------------------------------

def markdown_files(path: str) -> list[str]:
    """A file; every *.md under a directory; X.md plus the parts in X/ when that directory exists."""
    files = [path] if os.path.isfile(path) else []
    stem, extension = os.path.splitext(path)
    parts = path if os.path.isdir(path) else (stem if extension.lower() == ".md" else "")
    if parts and os.path.isdir(parts):
        for root, dirs, names in os.walk(parts):
            dirs.sort()
            files += [os.path.join(root, name) for name in sorted(names) if name.lower().endswith(".md")]
    return files


def load(paths: list[str], label: str, required: bool = True) -> Doc | None:
    files: list[str] = []
    for path in paths:
        found = markdown_files(path)
        if not found:
            if not required:
                return None
            raise InputError(f"{path}: not found (or a directory without Markdown files)")
        files += [f for f in found if f not in files]
    doc = Doc(label)
    for path in files:
        try:
            with open(path, encoding="utf-8-sig") as f:
                parse(f.read(), doc)
        except (OSError, UnicodeDecodeError) as error:
            raise InputError(f"cannot read {path}: {error}") from error
    return doc


def artifact(working: str, name: str, required: bool = True) -> Doc | None:
    return load([os.path.join(working, name)], name, required)


def split_paths(value: str) -> list[str]:
    paths = [path.strip() for path in value.split(",") if path.strip()]
    if not paths:
        raise InputError(f"no file given in '{value}'")
    return paths


# --- checks -----------------------------------------------------------------------------------------------------------

@dataclass
class Check:
    name: str
    checked: int = 0
    missing: list = field(default_factory=list)
    noun: str = "missing"
    failure: str = ""     # a failure that is not a list of ids

    @property
    def passed(self) -> bool:
        return not self.missing and not self.failure

    def describe(self) -> str:
        if self.failure:
            return f"{self.name}: {self.failure}"
        return f"{self.name}: {len(self.missing)} {self.noun} — {', '.join(self.missing)}"

    def line(self) -> str:
        return f"✓ {self.name} ({self.checked} checked)" if self.passed else f"✗ {self.describe()}"


@dataclass
class Result:
    title: str
    checks: list = field(default_factory=list)
    notes: list = field(default_factory=list)   # (level, text): notice | warning


def coverage(name: str, ids: set, found: set) -> Check:
    return Check(name, len(ids), sorted(ids - found, key=natural))


def at_least_one(name: str, ids: set) -> Check:
    return Check(name, len(ids), failure="" if ids else "none defined")


def excluded_note(doc: Doc, family: str) -> list[tuple[str, str]]:
    excluded = sorted(doc.excluded(family), key=natural)
    if not excluded:
        return []
    return [("notice", f"{doc.label}: not checked, marked removed/retired — {', '.join(excluded)}")]


def design_checks(result: Result, design: Doc | None, working: str, target: Doc) -> None:
    """Every UJ and SCR defined in design.md is referenced in target; skipped with a notice without design.md."""
    if design is None:
        result.notes.append(("notice", f"design.md not found in {working} — UJ and SCR checks skipped"))
        return
    for family in ("uj", "scr"):
        result.checks.append(coverage(f"every {FAMILIES[family][0]} defined in design.md is referenced in {target.label}",
                                      design.defined(family), target.referenced(family)))


def gate1(working: str, catalogue_path: str) -> Result:
    analysis = artifact(working, "analysis.md")
    catalogue = load([catalogue_path], os.path.basename(catalogue_path))
    requirements = analysis.defined("requirement")
    functional = {r for r in requirements if not NON_FUNCTIONAL.search(r)}
    with_ac = {requirement_of(ac) for ac in analysis.referenced("ac")}
    return Result("gate1", [
        at_least_one("analysis.md defines at least one requirement", requirements),
        coverage("every functional requirement defined in analysis.md has an AC in analysis.md", functional, with_ac),
        coverage(f"every requirement defined in analysis.md is defined in {catalogue.label}", requirements,
                 catalogue.defined("requirement")),
    ], excluded_note(analysis, "requirement"))


def gate_ux(working: str, catalogue_path: str) -> Result:
    design = artifact(working, "design.md")
    catalogue = load([catalogue_path], os.path.basename(catalogue_path))
    result = Result("gate-ux")
    traceability = "\n".join(section for heading, section in design.sections if "traceability" in heading.lower())
    for family in ("uj", "scr"):
        ids = design.defined(family)
        result.checks.append(coverage(f"every {FAMILIES[family][0]} defined in design.md is referenced in its "
                                      "Traceability section", ids, referenced_in(traceability, family)))
    if not traceability:
        result.notes.append(("warning", "design.md has no heading containing 'Traceability'"))
    areas = {d.id.split("-")[0] for d in catalogue.definitions if in_family(d.id, "requirement")}
    mentioned = design.referenced("requirement")
    unknown_area = {r for r in mentioned if r.split("-")[0] not in areas}
    result.checks.append(coverage(f"every requirement referenced in design.md is defined in {catalogue.label}",
                                  mentioned - unknown_area, catalogue.defined("requirement")))
    if unknown_area:
        result.notes.append(("notice", f"design.md: not checked, area code unknown to {catalogue.label} — "
                                       + ", ".join(sorted(unknown_area, key=natural))))
    return result


def requirement_source(working: str) -> tuple[Doc, list]:
    """analysis.md, or on routes without it the brief (brd.md) or the defect list (defect.md) — with a notice."""
    for name in REQUIREMENT_SOURCES:
        doc = artifact(working, name, required=False)
        if doc is not None:
            notes = [] if name == "analysis.md" else [("notice", f"analysis.md not found — requirements read from {name}")]
            return doc, notes
    raise InputError(f"none of {', '.join(REQUIREMENT_SOURCES)} found in {working}")


def gate2(working: str, catalogue_path: str) -> Result:
    analysis, notes = requirement_source(working)
    architecture = artifact(working, "architecture.md")
    design = artifact(working, "design.md", required=False)
    result = Result("gate2", notes=notes + excluded_note(analysis, "requirement"))
    result.checks.append(coverage(f"every requirement defined in {analysis.label} is referenced in architecture.md",
                                  analysis.defined("requirement"), architecture.referenced("requirement")))
    design_checks(result, design, working, architecture)
    result.checks.append(coverage(f"every EXT referenced in {analysis.label} is referenced in architecture.md",
                                  analysis.referenced("ext"), architecture.referenced("ext")))
    result.checks.append(at_least_one("architecture.md defines at least one WP", architecture.defined("wp")))
    return result


def gate_t(working: str, catalogue_path: str) -> Result:
    analysis, notes = requirement_source(working)
    architecture = artifact(working, "architecture.md", required=False)
    plan = artifact(working, "test_plan.md")
    design = artifact(working, "design.md", required=False)
    result = Result("gateT", notes=notes + excluded_note(analysis, "requirement"))
    requirements = analysis.defined("requirement")
    acs = {ac for ac in analysis.referenced("ac") if requirement_of(ac) in requirements} - analysis.excluded("ac")
    tcs = plan.defined("tc")
    result.checks += [
        at_least_one("test_plan.md defines at least one TC", tcs),
        coverage(f"every AC of a requirement defined in {analysis.label} is referenced in test_plan.md", acs,
                 plan.referenced("ac")),
        coverage(f"every NF requirement defined in {analysis.label} is referenced in test_plan.md",
                 {r for r in requirements if "-NF-" in r}, plan.referenced("requirement")),
        coverage(f"every BR requirement defined in {analysis.label} is referenced in test_plan.md",
                 {r for r in requirements if "-BR-" in r}, plan.referenced("requirement")),
    ]
    design_checks(result, design, working, plan)
    if architecture is None:
        result.notes.append(("notice", f"architecture.md not found in {working} — EXT check skipped (no architecture change on this route)"))
    else:
        result.checks.append(coverage("every EXT referenced in architecture.md is referenced in test_plan.md",
                                      architecture.referenced("ext"), plan.referenced("ext")))
    sourced = {d.id for d in plan.definitions if d.id in tcs and not d.excluded and ORACLE_SOURCE.search(d.context)}
    oracle = coverage("every TC defined in test_plan.md has an oracle source (SPEC:, FACT: or CHAR:)", tcs, sourced)
    oracle.noun = "without a source"
    seams = plan.defined("tseam")
    open_seams = {d.id for d in plan.definitions if d.id in seams and not d.excluded and OPEN.search(d.status)}
    result.checks += [oracle, Check("no TSEAM defined in test_plan.md is open", len(seams),
                                    sorted(open_seams, key=natural), noun="open")]
    return result


def open_findings(doc: Doc) -> tuple[int, list[str]]:
    """(number of Critical/Major findings, the open ones as 'F-3 (Major)')."""
    blocking: dict[str, str] = {}
    closed: set[str] = set()
    for table in doc.tables:
        severity = [i for i, name in enumerate(table.header) if "severity" in name]
        status = [i for i, name in enumerate(table.header)
                  if any(word in name for word in ("status", "route", "resolution"))]
        for cells in table.rows:
            match = FINDING_ID.search(cells[0])
            if not match:
                continue
            finding = match.group(0)
            if any(CLOSED.search(cell_at(cells, i)) for i in status):
                closed.add(finding)
            for i in severity:
                level = first_token(cell_at(cells, i)).lower()
                if level in BLOCKING:
                    blocking.setdefault(finding, level.capitalize())
    still_open = sorted(set(blocking) - closed, key=natural)
    return len(blocking), [f"{finding} ({blocking[finding]})" for finding in still_open]


def route_mode(working: str) -> str:
    """The mode letter on the first "Mode:" line of cycle.md, or "" when there is none."""
    cycle = artifact(working, "cycle.md", required=False)
    match = MODE_LINE.search(cycle.text) if cycle is not None else None
    return match.group(1) if match else ""


def gate3(working: str, catalogue_path: str) -> Result:
    mode = route_mode(working)
    required = GATE3_BY_MODE.get(mode, GATE3_REQUIRED)
    docs = [artifact(working, name) for name in required]
    docs += [doc for doc in (artifact(working, name, required=False) for name in GATE3_OPTIONAL if name not in required)
             if doc]
    result = Result("gate3", notes=[("notice", f"route Mode {mode or '? (no cycle.md — strictest set)'}: requires "
                                               + ", ".join(required))])
    for doc in docs:
        count, still_open = open_findings(doc)
        result.checks.append(Check(f"no open Critical/Major finding in {doc.label}", count, still_open, noun="open"))
    return result


def generic_check(family: str, defined_in: list[str], referenced_in_paths: list[str]) -> Result:
    source = load(defined_in, ", ".join(defined_in))
    target = load(referenced_in_paths, ", ".join(referenced_in_paths))
    name = f"every {FAMILIES[family][0]} defined in {source.label} is referenced in {target.label}"
    return Result("check", [coverage(name, source.defined(family), target.referenced(family))],
                  excluded_note(source, family))


GATES = {"gate1": gate1, "gate-ux": gate_ux, "gate2": gate2, "gateT": gate_t, "gate3": gate3}


# --- output -----------------------------------------------------------------------------------------------------------

def report(result: Result, json_out: str | None, summary_md: str | None) -> int:
    failed = [check for check in result.checks if not check.passed]
    if failed:
        verdict = f"{result.title}: FAIL — {len(failed)} of {len(result.checks)} checks failed"
    else:
        verdict = f"{result.title}: PASS — {len(result.checks)} checks passed"
    for check in result.checks:
        print(check.line())
    for level, text in result.notes:
        print(f"::{level}::{text}")
    for check in failed:
        print(f"::error title=trace_check {result.title}::{check.describe()}")
    print(verdict)

    markdown = "\n".join([f"### trace_check {result.title}", "",
                          *(f"- {check.line()}" for check in result.checks),
                          *(f"- {level}: {text}" for level, text in result.notes),
                          "", f"**{verdict}**"]) + "\n"
    for target in filter(None, (summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(markdown + "\n")
    if json_out:
        with open(json_out, "w", encoding="utf-8") as out:
            json.dump({
                "title": result.title,
                "passed": not failed,
                "checks": [{"name": c.name, "passed": c.passed, "checked": c.checked, "missing": c.missing,
                            "failure": c.failure} for c in result.checks],
                "notes": [{"level": level, "text": text} for level, text in result.notes],
            }, out, ensure_ascii=False, indent=2)
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", dest="json_out", help="write every check as JSON")
    common.add_argument("--summary-md", help="write the Markdown summary to this file (also appended to $GITHUB_STEP_SUMMARY)")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    gate = commands.add_parser("gate", parents=[common], help="run a gate's preset checks")
    gate.add_argument("name", choices=list(GATES))
    gate.add_argument("--working", default="absd-project/working", help="cycle artifacts (default absd-project/working)")
    gate.add_argument("--catalogue", default="absd-project/catalogue.md", help="requirement catalogue (gate1, gate-ux)")
    check = commands.add_parser("check", parents=[common], help="every id of a family defined in A is referenced in B")
    check.add_argument("--ids", required=True, choices=list(FAMILIES))
    check.add_argument("--defined-in", required=True, help="comma-separated files or directories")
    check.add_argument("--referenced-in", required=True, help="comma-separated files or directories")
    args = parser.parse_args(argv)

    try:
        if args.command == "gate":
            result = GATES[args.name](args.working, args.catalogue)
        else:
            result = generic_check(args.ids, split_paths(args.defined_in), split_paths(args.referenced_in))
    except InputError as error:
        print(f"::error::{error}")
        return 2
    return report(result, args.json_out, args.summary_md)


if __name__ == "__main__":
    sys.exit(main())
