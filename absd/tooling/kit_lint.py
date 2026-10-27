#!/usr/bin/env python3
"""ABSD kit lint: the kit repository's own consistency checks, so the golden standard cannot drift from itself.

Kit Markdown = absd/**/*.md (except absd/lessons/inbox/**), .claude/agents/*.md, .github/agents/*.agent.md, README.md,
CLAUDE.md and .github/copilot-instructions.md. Lines inside ``` / ~~~ code fences are ignored by every check.

Checks (numbers for --only):
  1 playbook rules   In absd/playbook/**/*.md a rule is a line starting "**CODE-n**" (CODE = [A-Z][A-Z0-9]*, n an
                     unpadded integer from 1); the playbook has at least one. Ids are unique across the playbook. A
                     rule's block runs to the next rule or the next heading of level 1-2 (### sub-headings and tables
                     belong to it) and holds a "Provenance:" line (leading - * _ and spaces ignored) with text after
                     it — except a tombstone, whose rule text starts with "Retired" or says "retired in <version>"
                     (the README format "**CODE-n** — Retired in x.y.z: superseded by …"). Every code is in the
                     routing table of absd/playbook/README.md (the table with a "Code"/"Codes" column; a cell may hold
                     several codes, comma-separated). Gaps in a code's numbering are warnings.
  2 citations        Every "ABSD:CODE-n", and every bare "CODE-n" whose CODE is a playbook code (has a rule or a
                     routing row), is defined in the playbook. A tombstoned id may be cited only on its own tombstone
                     line, in absd/CHANGELOG.md and in absd/lessons/LEDGER.md. A range "STRAT-1..12" / "VAR-1–20"
                     cites its two endpoints.
  3 LL ids           Every "LL-n" (ranges as above) is a row "| LL-n |" of absd/lessons/LEDGER.md; rows are unique.
  4 paths            Every backticked token starting with absd/, .claude/ or .github/ exists (exact case). Skipped:
                     placeholders (a token with < > * { } $ … or whitespace), absd-project paths, v1 working/archive
                     paths and product-owned files the kit only names (PRODUCT_PATHS).
  5 mirrors          Each .claude/agents/<name>.md has a .github/agents/<Name>.agent.md (name compared ignoring case)
                     whose text contains ".claude/agents/<name>.md", and each mirror has its manual.
  6 reserved codes   absd/playbook/README.md has a "Reserved codes" paragraph naming every playbook code; the
                     PLAYBOOK_CODES set of absd/tooling/trace_check.py and traceability_report.py (when present)
                     equals the playbook codes, and PLAYBOOK_CODES | RESERVED equals the paragraph's codes.
  7 stack words      Outside absd/tooling/**, absd/CHANGELOG.md, absd/lessons/**, YAML frontmatter and "Provenance:"
                     lines (with their continuation lines), a Markdown block — paragraph, list item with its wrapped
                     lines, table row or heading — that names a STACK_WORDS entry (case-sensitive, whole word) names
                     at least two different ones: a labelled illustration of alternatives. PROJECT_WORDS (a real
                     product's names, any case, any suffix: KatenatsioTipster, dbforge.eu) are always errors there.
  8 budgets          Characters: absd/RULES.md <= 16000, each .claude/agents/*.md <= 36000, each absd/playbook/**/*.md
                     <= 20000 (absd/RULES.md §9; about 4 characters per token). absd/RULES.md must exist.
  9 version          absd/VERSION is semver x.y.z and the first "## " heading of absd/CHANGELOG.md names it; both files
                     are required.

usage:
  kit_lint.py [--root .] [--only 1,2,...] [--json OUT] [--summary-md OUT]

Output: one GitHub annotation per finding (::error file=…,line=…,title=…::message; ::warning for numbering gaps), then
one line per check ("✓ 2 citations — 812 checked, 0 errors, 0 warnings") and a verdict. --summary-md writes the same
as Markdown (also appended to $GITHUB_STEP_SUMMARY); --json writes every finding.

Exit code: 0 pass (warnings allowed), 1 at least one error, 2 usage error (--root has no absd/ directory, a bad --only
value, an unreadable kit file). Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

CHECKS = {          # number -> (name, what "checked" counts)
    1: ("playbook rules", "rules"),
    2: ("citations", "citations"),
    3: ("LL ids", "LL citations"),
    4: ("paths", "paths"),
    5: ("mirrors", "agents"),
    6: ("reserved codes", "codes"),
    7: ("stack words", "blocks"),
    8: ("budgets", "files"),
    9: ("version", "files"),
}

PLAYBOOK = "absd/playbook"
README = "absd/playbook/README.md"
LEDGER = "absd/lessons/LEDGER.md"
CHANGELOG = "absd/CHANGELOG.md"
VERSION = "absd/VERSION"
RULES = "absd/RULES.md"
MANUALS = ".claude/agents"
MIRRORS = ".github/agents"
MIRROR_SUFFIX = ".agent.md"
ROOT_FILES = ("README.md", "CLAUDE.md", ".github/copilot-instructions.md")
INBOX = "absd/lessons/inbox/"
RESERVED_LABEL = "Reserved codes"
# Tools that must know the reserved codes: `PLAYBOOK_CODES = {...}` and `RESERVED = PLAYBOOK_CODES | {...}` literals.
CODE_TOOLS = ("absd/tooling/trace_check.py", "absd/tooling/traceability_report.py")
PLAYBOOK_CODES_LITERAL = re.compile(r"^PLAYBOOK_CODES\s*=\s*\{(.*?)\}", re.MULTILINE | re.DOTALL)
RESERVED_LITERAL = re.compile(r"^RESERVED\s*=\s*PLAYBOOK_CODES\s*\|\s*\{(.*?)\}", re.MULTILINE | re.DOTALL)
QUOTED = re.compile(r"[\"']([A-Z][A-Z0-9]*)[\"']")
TOMBSTONE_CITABLE = (CHANGELOG, LEDGER)          # history may name a retired id

# Size budgets in characters (absd/RULES.md §9). Patterns: * = within one directory, **/ = any depth.
BUDGETS = (
    ("absd/RULES.md", 16000),
    (".claude/agents/*.md", 36000),
    ("absd/playbook/**/*.md", 20000),
)

# Stack, vendor and tool names: kit text names them only in an illustration of at least two alternatives.
# Extend freely; matching is case-sensitive and whole-word ("Java" is not found in "JavaScript", "C#" not in "C###").
STACK_WORDS = (
    ".NET", "C#", "xUnit", "NUnit", "JUnit", "pytest", "Jest", "Vitest", "Mocha", "Playwright", "Cypress", "Selenium",
    "Appium", "XCUITest", "Espresso", "Maestro", "React", "Angular", "Vue", "Svelte", "Django", "Flask", "FastAPI",
    "Express", "ASP.NET", "EF Core", "Hibernate", "Prisma", "PostgreSQL", "Postgres", "MySQL", "MongoDB", "SQLite",
    "Redis", "Kafka", "RabbitMQ", "Docker", "Kubernetes", "Portainer", "Terraform", "Azure", "AWS", "GCP", "Tailwind",
    "Spring", "Rails", "Laravel", "Kotlin", "Swift", "TypeScript", "JavaScript", "Python", "Java", "Rust", "Golang",
    "Node.js", "ESLint", "Ruff", "Stryker", "PIT", "mutmut", "Testcontainers", "WireMock", "Mailpit", "Pact", "k6",
    "Gatling", "axe-core", "Lighthouse", "Pa11y",
)
# Stack-neutral terms that contain a stack word: removed from a line before STACK_WORDS are matched.
NEUTRAL_PHRASES = ("JUnit XML", "JUnit format")
# A real product's own names: never in kit text outside provenance, the ledger and the changelog. Matched in any case
# and with any suffix, so the product slug (KatenatsioTipster) and hostnames (dbforge.eu) are caught too.
PROJECT_WORDS = ("dbforge", "Gemini", "Katenatsio")
STACK_EXEMPT = ("absd/tooling/**", CHANGELOG, "absd/lessons/**")

PATH_PREFIXES = ("absd/", ".claude/", ".github/")
PLACEHOLDER = re.compile(r"[<>*{}$…\s]")
# Paths the kit names but a kit repository does not hold: product state, v1 product paths, product-owned seeds.
PRODUCT_PATHS = ("absd/working", "absd/archive", ".claude/working", ".claude/archive", ".claude/settings.json",
                 ".claude/settings.local.json", ".github/instructions/")

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]|$)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
DEFINITION = re.compile(r"^\*\*([A-Z][A-Z0-9]*)-(\d+)\*\*")
TOMBSTONE = re.compile(r"^retired\b|\bretired in v?\d", re.IGNORECASE)
RANGE_TAIL = r"(?:(?: ?(?:\.\.|…|–) ?|—)(\d+))?"         # "-1..12", "-1–20", "-1 … 12": the second endpoint
CITATION = re.compile(r"(?<![A-Za-z0-9_-])(ABSD:)?([A-Z][A-Z0-9]*)-(\d+)" + RANGE_TAIL + r"(?![A-Za-z0-9_])")
LL_CITATION = re.compile(r"(?<![A-Za-z0-9_-])LL-(\d+)" + RANGE_TAIL + r"(?![A-Za-z0-9_])")
LL_ROW = re.compile(r"^\s*\|\s*(LL-\d+)\s*\|")
CODE_WORD = re.compile(r"(?<![A-Za-z0-9])[A-Z][A-Z0-9]*(?![A-Za-z0-9])")
BACKTICKED = re.compile(r"`([^`\n]+)`")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class UsageError(Exception):
    """Exit code 2."""


@dataclass
class Finding:
    check: int
    level: str          # error | warning
    file: str           # path relative to --root
    line: int           # 1-based, or 0 when the finding is about the whole file
    message: str

    def annotation(self) -> str:
        props = [f"file={escape_property(self.file)}"]
        if self.line:
            props.append(f"line={self.line}")
        props.append(f"title={escape_property(f'kit_lint {self.check} {CHECKS[self.check][0]}')}")
        return f"::{self.level} {','.join(props)}::{escape_data(self.message)}"

    def where(self) -> str:
        return f"{self.file}:{self.line}" if self.line else self.file


def escape_data(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(text: str) -> str:
    return escape_data(text).replace(":", "%3A").replace(",", "%2C")


# --- reading the kit --------------------------------------------------------------------------------------------------

class Kit:
    """The files of one kit repository, read once; paths are relative to the root with forward slashes."""

    def __init__(self, root: str):
        self.root = root
        self._text: dict = {}

    def path(self, rel: str) -> str:
        return os.path.join(self.root, *rel.split("/"))

    def is_file(self, rel: str) -> bool:
        return os.path.isfile(self.path(rel))

    def text(self, rel: str) -> str:
        if rel not in self._text:
            try:
                with open(self.path(rel), encoding="utf-8-sig") as f:
                    self._text[rel] = f.read()
            except (OSError, UnicodeDecodeError) as error:
                raise UsageError(f"cannot read {rel}: {error}") from error
        return self._text[rel]

    def lines(self, rel: str) -> list:
        return self.text(rel).splitlines()

    def walk(self, top: str) -> list:
        """Every *.md file under top (recursively), sorted."""
        found = []
        for directory, dirs, names in os.walk(self.path(top)):
            dirs.sort()
            rel_dir = os.path.relpath(directory, self.root).replace(os.sep, "/")
            found += [f"{rel_dir}/{name}" for name in sorted(names) if name.endswith(".md")]
        return found

    def listing(self, top: str, suffix: str) -> list:
        """Files directly in top whose name ends with suffix, sorted."""
        directory = self.path(top)
        if not os.path.isdir(directory):
            return []
        return [f"{top}/{name}" for name in sorted(os.listdir(directory))
                if name.endswith(suffix) and os.path.isfile(os.path.join(directory, name))]

    def exists_exact(self, rel: str) -> bool:
        """rel exists with exactly this spelling, also on case-insensitive file systems."""
        current = self.root
        for part in [p for p in rel.split("/") if p not in ("", ".")]:
            if part == ".." or not os.path.isdir(current) or part not in os.listdir(current):
                return False
            current = os.path.join(current, part)
        return True

    def markdown(self) -> list:
        files = [f for f in self.walk("absd") if not f.startswith(INBOX)]
        files += self.listing(MANUALS, ".md")
        files += self.listing(MIRRORS, MIRROR_SUFFIX)
        files += [f for f in ROOT_FILES if self.is_file(f)]
        return files


def plain_lines(lines: list) -> list:
    """(line number, text) of every line outside ``` / ~~~ code fences."""
    result, fence = [], ""
    for number, line in enumerate(lines, start=1):
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                    and not line[match.end():].strip():
                fence = ""
        elif match:
            fence = match.group(1)
        else:
            result.append((number, line))
    return result


def frontmatter_end(lines: list) -> int:
    """The line number closing a YAML frontmatter that opens on line 1, else 0."""
    if not lines or lines[0].strip() != "---":
        return 0
    for number, line in enumerate(lines[1:], start=2):
        if line.strip() in ("---", "..."):
            return number
    return 0


def blocks(lines: list) -> list:
    """Markdown blocks outside fences and frontmatter, each a list of (line number, text): a paragraph, a list item
    with its wrapped lines, a table row, a heading."""
    result: list = []
    current: list = []
    skip_to = frontmatter_end(lines)
    for number, line in plain_lines(lines):
        if number <= skip_to:
            continue
        starts_new = not line.strip() or LIST_ITEM.match(line) or line.strip().startswith("|") or HEADING.match(line)
        if current and (starts_new or number != current[-1][0] + 1 or current[-1][1].strip().startswith("|")
                        or HEADING.match(current[-1][1])):
            result.append(current)
            current = []
        if line.strip():
            current.append((number, line))
    if current:
        result.append(current)
    return result


def glob_match(pattern: str, rel: str) -> bool:
    regex, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            regex, i = regex + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            regex, i = regex + ".*", i + 2
        elif pattern[i] == "*":
            regex, i = regex + "[^/]*", i + 1
        else:
            regex, i = regex + re.escape(pattern[i]), i + 1
    return re.fullmatch(regex, rel) is not None


def tables(lines: list) -> list:
    """Tables outside fences, each a list of rows (lists of cells); the header row comes first."""
    result, current, previous = [], [], -1
    for number, line in plain_lines(lines):
        if line.strip().startswith("|") and (not current or number == previous + 1):
            current.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        else:
            if current:
                result.append(current)
            current = [[cell.strip() for cell in line.strip().strip("|").split("|")]] \
                if line.strip().startswith("|") else []
        previous = number
    if current:
        result.append(current)
    return result


def is_separator(cells: list) -> bool:
    filled = [c for c in cells if c]
    return bool(filled) and all(re.fullmatch(r":?-{3,}:?", c) for c in filled)


# --- the playbook model -----------------------------------------------------------------------------------------------

@dataclass
class Rule:
    id: str
    code: str
    number: int
    file: str
    line: int
    tombstone: bool
    padded: bool = False              # "GATE-02" or "GATE-0": numbers are unpadded integers from 1
    provenance: str | None = None     # the text after "Provenance:", None when the block has no Provenance line


@dataclass
class Playbook:
    rules: list = field(default_factory=list)
    defined: dict = field(default_factory=dict)     # id -> first Rule with that id
    routed: set = field(default_factory=set)        # codes in the README routing table
    routing_found: bool = False

    @property
    def codes(self) -> set:
        """Playbook codes: those with a rule or a routing row."""
        return {rule.code for rule in self.rules} | self.routed


def provenance_text(line: str) -> str | None:
    stripped = line.lstrip("*-_ \t")
    if not stripped.startswith("Provenance:"):
        return None
    return stripped[len("Provenance:"):].strip("*_ \t")


def parse_rules(kit: Kit, rel: str) -> list:
    rules: list = []
    current: Rule | None = None
    for number, line in plain_lines(kit.lines(rel)):
        heading = HEADING.match(line)
        definition = DEFINITION.match(line)
        if definition:
            code, digits = definition.group(1), definition.group(2)
            text = line[definition.end():].lstrip(" \t—–-:*_")
            current = Rule(f"{code}-{digits}", code, int(digits), rel, number, bool(TOMBSTONE.search(text)),
                           padded=digits != str(int(digits)) or int(digits) == 0)
            rules.append(current)
        elif heading and len(heading.group(1)) <= 2:
            current = None
        elif current is not None and current.provenance is None:
            current.provenance = provenance_text(line)
    return rules


def load_playbook(kit: Kit) -> Playbook:
    book = Playbook()
    for rel in kit.walk(PLAYBOOK):
        book.rules += parse_rules(kit, rel)
    for rule in book.rules:
        book.defined.setdefault(rule.id, rule)
    if kit.is_file(README):
        for table in tables(kit.lines(README)):
            if len(table) < 2 or not is_separator(table[1]):
                continue
            header = [cell.strip("*_` ").lower() for cell in table[0]]
            columns = [i for i, name in enumerate(header) if name in ("code", "codes")]
            book.routing_found |= bool(columns)
            for cells in table[2:]:
                for i in columns:
                    if i < len(cells):
                        book.routed.update(CODE_WORD.findall(cells[i].replace("`", " ").replace("*", " ")))
    return book


# --- checks: each returns (findings, number of things checked) ------------------------------------------------------

def check_rules(kit: Kit, book: Playbook) -> tuple:
    findings = []
    if not book.rules:
        findings.append(Finding(1, "error", PLAYBOOK, 0, "no rules (lines starting \"**CODE-n**\") in the playbook"))
    numbers: dict = {}
    first_of: dict = {}
    for rule in book.rules:
        first_of.setdefault(rule.code, rule)
        numbers.setdefault(rule.code, set()).add(rule.number)
        if rule.padded:
            hint = f"write {rule.code}-{rule.number}" if rule.number else "numbering starts at 1"
            findings.append(Finding(1, "error", rule.file, rule.line,
                                    f"{rule.id}: rule numbers are unpadded integers from 1 ({hint})"))
        first = book.defined[rule.id]
        if first is not rule:
            findings.append(Finding(1, "error", rule.file, rule.line,
                                    f"{rule.id} is already defined at {first.file}:{first.line} — ids are unique"))
        if rule.tombstone:
            continue
        if rule.provenance is None:
            findings.append(Finding(1, "error", rule.file, rule.line,
                                    f"{rule.id} has no Provenance line (\"- *Provenance:* LL-n (<project>, YYYY-MM)\" "
                                    "or \"- *Provenance:* industry baseline\")"))
        elif not rule.provenance:
            findings.append(Finding(1, "error", rule.file, rule.line, f"{rule.id} has an empty Provenance line"))
    if not kit.is_file(README):
        findings.append(Finding(1, "error", README, 0, "the playbook README (routing table) is missing"))
    elif not book.routing_found:
        findings.append(Finding(1, "error", README, 0, "no routing table: a Markdown table with a \"Code\" column"))
    for code, rule in sorted(first_of.items()):
        if book.routing_found and code not in book.routed:
            findings.append(Finding(1, "error", rule.file, rule.line,
                                    f"code {code} is not in the routing table of {README}"))
        gaps = sorted(set(range(1, max(numbers[code]) + 1)) - numbers[code])
        if gaps:
            findings.append(Finding(1, "warning", rule.file, rule.line,
                                    f"{code} numbering has gaps: no {', '.join(f'{code}-{n}' for n in gaps)} "
                                    "(retire with a tombstone, never delete)"))
    return findings, len(book.rules)


def endpoints(match: re.Match, group: int) -> list:
    """The number of an id and, for a range, the number of its second endpoint."""
    return [match.group(group)] + ([match.group(group + 1)] if match.group(group + 1) else [])


def check_citations(kit: Kit, book: Playbook, files: list) -> tuple:
    findings, checked = [], 0
    codes = book.codes
    for rel in files:
        for number, line in plain_lines(kit.lines(rel)):
            for match in CITATION.finditer(line):
                prefixed, code = bool(match.group(1)), match.group(2)
                if not prefixed and code not in codes:
                    continue
                for value in endpoints(match, 3):
                    checked += 1
                    rule_id = f"{code}-{value}"
                    shown = ("ABSD:" if prefixed else "") + rule_id
                    rule = book.defined.get(rule_id)
                    if rule is None:
                        findings.append(Finding(2, "error", rel, number, f"{shown} is not defined in the playbook"))
                    elif rule.tombstone and rel not in TOMBSTONE_CITABLE and (rel, number) != (rule.file, rule.line):
                        findings.append(Finding(2, "error", rel, number,
                                                f"{shown} is retired ({rule.file}:{rule.line}) — cite its successor"))
    return findings, checked


def check_ll(kit: Kit, files: list) -> tuple:
    if not kit.is_file(LEDGER):
        return [Finding(3, "error", LEDGER, 0, "the lessons ledger is missing")], 0
    findings, checked, rows = [], 0, {}
    for number, line in plain_lines(kit.lines(LEDGER)):
        match = LL_ROW.match(line)
        if match and match.group(1) in rows:
            findings.append(Finding(3, "error", LEDGER, number,
                                    f"{match.group(1)} already has a row at line {rows[match.group(1)]}"))
        elif match:
            rows[match.group(1)] = number
    for rel in files:
        for number, line in plain_lines(kit.lines(rel)):
            for match in LL_CITATION.finditer(line):
                for value in endpoints(match, 1):
                    checked += 1
                    if f"LL-{value}" not in rows:
                        findings.append(Finding(3, "error", rel, number,
                                                f"LL-{value} has no row \"| LL-{value} |\" in {LEDGER}"))
    return findings, checked


def kit_path(token: str) -> str | None:
    """The kit path a backticked token names, or None when it is not one to check."""
    if not token.startswith(PATH_PREFIXES) or PLACEHOLDER.search(token):
        return None
    if "absd-project" in token or token.startswith(PRODUCT_PATHS):
        return None
    return token.split("#", 1)[0]


def check_paths(kit: Kit, files: list) -> tuple:
    findings, checked = [], 0
    for rel in files:
        for number, line in plain_lines(kit.lines(rel)):
            for token in BACKTICKED.findall(line):
                path = kit_path(token.strip())
                if path is None:
                    continue
                checked += 1
                if not kit.exists_exact(path):
                    findings.append(Finding(4, "error", rel, number, f"`{path}` does not exist in the kit"))
    return findings, checked


def check_mirrors(kit: Kit) -> tuple:
    findings = []
    manuals = kit.listing(MANUALS, ".md")
    mirrors = {os.path.basename(m)[:-len(MIRROR_SUFFIX)].lower(): m for m in kit.listing(MIRRORS, MIRROR_SUFFIX)}
    if not manuals:
        findings.append(Finding(5, "error", MANUALS, 0, "no agent manuals (*.md)"))
    names = set()
    for manual in manuals:
        name = os.path.basename(manual)[:-len(".md")]
        names.add(name.lower())
        mirror = mirrors.get(name.lower())
        if mirror is None:
            findings.append(Finding(5, "error", manual, 0,
                                    f"no Copilot mirror {MIRRORS}/{name[:1].upper()}{name[1:]}{MIRROR_SUFFIX}"))
        elif manual not in kit.text(mirror):
            findings.append(Finding(5, "error", mirror, 0, f"the mirror does not point to its manual `{manual}`"))
    for key, mirror in sorted(mirrors.items()):
        if key not in names:
            findings.append(Finding(5, "error", mirror, 0, f"no manual {MANUALS}/{key}.md for this mirror"))
    return findings, len(names | set(mirrors))


def check_reserved(kit: Kit, book: Playbook) -> tuple:
    if not kit.is_file(README):
        return [Finding(6, "error", README, 0, "the playbook README (reserved codes) is missing")], 0
    def names_them(line: str) -> bool:
        return RESERVED_LABEL in line and not HEADING.match(line)

    paragraph = next((block for block in blocks(kit.lines(README)) if any(names_them(line) for _, line in block)),
                     None)
    if paragraph is None:
        return [Finding(6, "error", README, 0, f"no \"{RESERVED_LABEL}\" paragraph")], 0
    start = next(i for i, (_, line) in enumerate(paragraph) if names_them(line))
    named = {code for _, line in paragraph[start:] for code in CODE_WORD.findall(line.replace("`", " "))}
    line_no = paragraph[start][0]
    findings = [Finding(6, "error", README, line_no, f"playbook code {code} is not in the reserved codes")
                for code in sorted(book.codes - named)]
    for tool in CODE_TOOLS:
        if kit.is_file(tool):
            findings += tool_codes(kit, tool, book.codes, named)
    return findings, len(book.codes)


def tool_codes(kit: Kit, tool: str, playbook: set, reserved: set) -> list:
    """The tool's PLAYBOOK_CODES equal the playbook's codes and its RESERVED set equals the README's reserved codes."""
    text = kit.text(tool)
    found = []
    for label, pattern, expected in (("PLAYBOOK_CODES", PLAYBOOK_CODES_LITERAL, playbook),
                                     ("RESERVED", RESERVED_LITERAL, reserved)):
        match = pattern.search(text)
        if match is None:
            found.append(Finding(6, "error", tool, 0, f"no {label} set literal to compare with {README}"))
            continue
        codes = set(QUOTED.findall(match.group(1)))
        if label == "RESERVED":
            playbook_match = PLAYBOOK_CODES_LITERAL.search(text)
            codes |= set(QUOTED.findall(playbook_match.group(1))) if playbook_match else set()
        line_no = text[:match.start()].count("\n") + 1
        missing, extra = sorted(expected - codes), sorted(codes - expected)
        if missing or extra:
            parts = [f"missing {', '.join(missing)}" if missing else "", f"extra {', '.join(extra)}" if extra else ""]
            found.append(Finding(6, "error", tool, line_no, f"{label} differs from {README}: "
                                 + "; ".join(p for p in parts if p)))
    return found


def word_pattern(word: str) -> re.Pattern:
    """Whole-word match; a word ending (starting) in punctuation must not continue (follow) with it: "C#" ≠ "C###"."""
    before = "A-Za-z0-9_" + ("" if word[0].isalnum() else re.escape(word[0]))
    after = "A-Za-z0-9_" + ("" if word[-1].isalnum() else re.escape(word[-1]))
    return re.compile(f"(?<![{before}]){re.escape(word)}(?![{after}])")


STACK_PATTERNS = [(word, word_pattern(word)) for word in STACK_WORDS]
PROJECT_PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(w) for w in PROJECT_WORDS) + r")[\w.-]*",
                             re.IGNORECASE)


def check_stack_words(kit: Kit, files: list) -> tuple:
    findings, checked = [], 0
    for rel in files:
        if any(glob_match(pattern, rel) for pattern in STACK_EXEMPT):
            continue
        for block in blocks(kit.lines(rel)):
            checked += 1
            # a Provenance line and the lines that continue it are provenance, where real names belong
            cut = next((i for i, (_, line) in enumerate(block) if "Provenance:" in line), len(block))
            first_seen: dict = {}
            for number, line in block[:cut]:
                project = sorted({m.group(0).rstrip(".-") for m in PROJECT_PATTERN.finditer(line)})
                if project:
                    findings.append(Finding(7, "error", rel, number,
                                            f"names a real product ({', '.join(project)}) — only provenance, the "
                                            "ledger and the changelog may"))
                for phrase in NEUTRAL_PHRASES:
                    line = line.replace(phrase, " ")
                for word, pattern in STACK_PATTERNS:
                    if word not in first_seen and pattern.search(line):
                        first_seen[word] = number
            if len(first_seen) == 1:
                (word, number), = first_seen.items()
                findings.append(Finding(7, "error", rel, number,
                                        f"names one stack ({word}) — kit text is stack-neutral; an illustration names "
                                        "at least two alternatives"))
    return findings, checked


def check_budgets(kit: Kit) -> tuple:
    findings, checked = [], 0
    if not kit.is_file(RULES):
        findings.append(Finding(8, "error", RULES, 0, "the canonical rules file is missing"))
    for rel in [RULES] + kit.listing(MANUALS, ".md") + kit.walk(PLAYBOOK):
        if not kit.is_file(rel):
            continue
        for pattern, limit in BUDGETS:
            if glob_match(pattern, rel):
                checked += 1
                size = len(kit.text(rel))
                if size > limit:
                    findings.append(Finding(8, "error", rel, 0,
                                            f"{size} characters — {size - limit} over the {limit}-character budget; "
                                            "split by topic or tighten"))
    return findings, checked


def check_version(kit: Kit) -> tuple:
    findings, version = [], None
    if not kit.is_file(VERSION):
        findings.append(Finding(9, "error", VERSION, 0, "the kit version file is missing"))
    elif SEMVER.match(kit.text(VERSION).strip()):
        version = kit.text(VERSION).strip()
    else:
        findings.append(Finding(9, "error", VERSION, 1,
                                f"'{kit.text(VERSION).strip()}' is not a semantic version x.y.z"))
    if not kit.is_file(CHANGELOG):
        findings.append(Finding(9, "error", CHANGELOG, 0, "the changelog is missing"))
        return findings, 1
    heading = next(((n, line) for n, line in plain_lines(kit.lines(CHANGELOG)) if line.startswith("## ")), None)
    if heading is None:
        findings.append(Finding(9, "error", CHANGELOG, 0, "no \"## <version>\" entry"))
    elif version and not re.search(r"(?<![0-9.])" + re.escape(version) + r"(?![0-9]|\.[0-9])", heading[1]):
        findings.append(Finding(9, "error", CHANGELOG, heading[0],
                                f"the newest entry \"{heading[1].strip()}\" does not name {VERSION} {version}"))
    return findings, 2


def lint(kit: Kit, only: set) -> dict:
    """check number -> (findings, checked) for the chosen checks."""
    files = kit.markdown()
    book = load_playbook(kit)
    runners = {
        1: lambda: check_rules(kit, book),
        2: lambda: check_citations(kit, book, files),
        3: lambda: check_ll(kit, files),
        4: lambda: check_paths(kit, files),
        5: lambda: check_mirrors(kit),
        6: lambda: check_reserved(kit, book),
        7: lambda: check_stack_words(kit, files),
        8: lambda: check_budgets(kit),
        9: lambda: check_version(kit),
    }
    return {number: runners[number]() for number in sorted(only)}


# --- output -----------------------------------------------------------------------------------------------------------

SUMMARY_LIMIT = 50     # findings listed per check in the Markdown summary


def report(results: dict, root: str, json_out: str | None, summary_md: str | None) -> int:
    def count(findings: list, level: str) -> int:
        return sum(1 for f in findings if f.level == level)

    every = [f for findings, _ in results.values() for f in findings]
    errors, warnings = count(every, "error"), count(every, "warning")
    verdict = f"kit_lint: {'FAIL' if errors else 'PASS'} — {errors} errors, {warnings} warnings " \
              f"(checks {', '.join(str(n) for n in results)})"
    lines = []
    for number, (findings, checked) in results.items():
        name, noun = CHECKS[number]
        mark = "✗" if count(findings, "error") else "✓"
        lines.append(f"{mark} {number} {name} — {checked} {noun} checked, "
                     f"{count(findings, 'error')} errors, {count(findings, 'warning')} warnings")
    for finding in every:
        print(finding.annotation())
    print("\n".join(lines))
    print(verdict)

    markdown = ["### kit_lint", "", *(f"- {line}" for line in lines)]
    for number, (findings, _) in results.items():
        if findings:
            markdown += ["", f"**{number} {CHECKS[number][0]}**", ""]
            markdown += [f"- {f.level}: `{f.where()}` — {f.message}" for f in findings[:SUMMARY_LIMIT]]
            if len(findings) > SUMMARY_LIMIT:
                markdown.append(f"- … and {len(findings) - SUMMARY_LIMIT} more")
    markdown += ["", f"**{verdict}**"]
    text = "\n".join(markdown) + "\n"
    for target in filter(None, (summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(text + "\n")
    if json_out:
        with open(json_out, "w", encoding="utf-8") as out:
            json.dump({
                "root": root,
                "passed": not errors,
                "errors": errors,
                "warnings": warnings,
                "checks": [{"check": number, "name": CHECKS[number][0], "checked": checked,
                            "errors": count(findings, "error"), "warnings": count(findings, "warning"),
                            "findings": [{"level": f.level, "file": f.file, "line": f.line, "message": f.message}
                                         for f in findings]}
                           for number, (findings, checked) in results.items()],
            }, out, ensure_ascii=False, indent=2)
    return 1 if errors else 0


def parse_only(values: list) -> set:
    if not values:
        return set(CHECKS)
    chosen = set()
    for part in (p.strip() for value in values for p in value.split(",")):
        if not part.isdigit() or int(part) not in CHECKS:
            raise UsageError(f"--only: '{part}' is not a check number (1-{max(CHECKS)})")
        chosen.add(int(part))
    return chosen


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="the kit repository (default: the current directory)")
    parser.add_argument("--only", action="append", default=[], help="comma-separated check numbers (repeatable)")
    parser.add_argument("--json", dest="json_out", help="write every finding as JSON")
    parser.add_argument("--summary-md", help="write the Markdown summary to this file (also appended to $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)
    try:
        only = parse_only(args.only)
        if not os.path.isdir(os.path.join(args.root, "absd")):
            raise UsageError(f"{args.root} has no absd/ directory — give --root the kit repository")
        results = lint(Kit(args.root), only)
    except UsageError as error:
        print(f"::error::{error}")
        return 2
    return report(results, args.root, args.json_out, args.summary_md)


if __name__ == "__main__":
    sys.exit(main())
