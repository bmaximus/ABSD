#!/usr/bin/env python3
"""Coverage gate for any stack that writes Cobertura XML or LCOV.

Fails the build when
  1. total line coverage (merged across every report: a line counts as covered if any test run hit it) is below
     --min-total, or
  2. a unit of code that NO test runs at all (not one of its lines) appears, unless it is listed in the allowlist
     together with its reason (ABSD playbook GATE-02). Allowlist entries without a reason are themselves an error.

Stale allowlist entries (units that are now tested) produce a warning so the list shrinks over time.

Cobertura is written by coverlet (.NET), coverage.py (`coverage xml`), istanbul/nyc/c8/vitest/jest
(`cobertura` reporter), gocover-cobertura (Go), cargo-llvm-cov / grcov (Rust), JaCoCo via converters (JVM).
LCOV (`*.info` / `*.lcov`, or any file starting with `TN:`/`SF:`) is written by c8/istanbul, grcov, cargo-llvm-cov,
genhtml-based tools and lcov itself; LCOV has no classes, so its units are files.

The minimum is a ratchet (ABSD playbook GATE-*): when coverage is more than one point above it, the report says what
to raise it to. Raising it is the Tester's change; lowering it needs the user's approval (a gate loosening).

usage:
  coverage_gate.py --reports "**/coverage.cobertura.xml" [--reports "<glob>" ...] --min-total 80
                   [--untested-allowlist tests/untested-allowlist.txt] [--unit class|file] [--min-lines 5]
                   [--exclude "/Migrations/" ...] [--layer Domain=/Domain/ ...]
                   [--json coverage.json] [--summary-md coverage.md]

Exit code: 0 pass, 1 gate failed, 2 usage/input error. Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field

LineKey = tuple  # (filename, line number)


@dataclass
class Coverage:
    lines: dict = field(default_factory=dict)                         # (file, line) -> covered?
    units: dict = field(default_factory=lambda: defaultdict(dict))    # unit -> {(file, line): covered?}


def normalise_unit(name: str, filename: str, mode: str) -> str:
    """The unit a line belongs to. Nested and compiler-generated types (C# async state machines and lambdas
    `Outer/<Method>d__3`, generics `Outer<T>` / `Outer`1`; JVM `Outer$Inner`) fold into their declaring type."""
    if mode == "file":
        return filename.replace("\\", "/")
    unit = name.split("/")[0]
    for marker in ("<", "`", "$"):
        unit = unit.split(marker)[0]
    return unit or filename.replace("\\", "/")


def is_lcov(path: str) -> bool:
    if path.lower().endswith((".info", ".lcov")):
        return True
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.read(64).lstrip()
    return head.startswith(("TN:", "SF:"))


def read_lcov(path: str, excludes: list[re.Pattern], cov: Coverage) -> None:
    filename = ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("SF:"):
                filename = line[3:].replace("\\", "/")
            elif line == "end_of_record":
                filename = ""
            elif line.startswith("DA:") and filename and not any(rx.search(filename) for rx in excludes):
                number, _, rest = line[3:].partition(",")
                hits = rest.split(",")[0]
                key = (filename, number)
                hit = int(hits or 0) > 0
                cov.lines[key] = cov.lines.get(key, False) or hit
                cov.units[filename][key] = cov.units[filename].get(key, False) or hit


def read_reports(patterns: list[str], excludes: list[re.Pattern], unit_mode: str) -> tuple[Coverage, list[str]]:
    files = sorted({path for pattern in patterns for path in glob.glob(pattern, recursive=True) if os.path.isfile(path)})
    cov = Coverage()
    for path in files:
        if is_lcov(path):
            read_lcov(path, excludes, cov)
            continue
        root = ET.parse(path).getroot()
        for cls in root.iter("class"):
            filename = (cls.get("filename") or "").replace("\\", "/")
            if any(rx.search(filename) for rx in excludes):
                continue
            unit = normalise_unit(cls.get("name") or "", filename, unit_mode)
            for line in cls.iter("line"):
                key = (filename, line.get("number", ""))
                hit = int(line.get("hits", "0") or 0) > 0
                cov.lines[key] = cov.lines.get(key, False) or hit
                cov.units[unit][key] = cov.units[unit].get(key, False) or hit
    return cov, files


def untested_units(cov: Coverage, min_lines: int) -> list[tuple[str, int]]:
    return sorted((unit, len(lines)) for unit, lines in cov.units.items()
                  if len(lines) >= min_lines and not any(lines.values()))


def read_allowlist(path: str) -> tuple[dict[str, str], list[str]]:
    """`<unit>  # <reason>` per line. Returns (unit -> reason, errors)."""
    allowed, errors = {}, []
    with open(path, encoding="utf-8") as f:
        for number, raw in enumerate(f, start=1):
            entry, _, reason = raw.partition("#")
            entry, reason = entry.strip(), reason.strip()
            if not entry:
                continue
            if not reason:
                errors.append(f"{path}:{number}: '{entry}' has no reason — write '{entry}  # <why no test runs it>'")
            allowed[entry] = reason
    return allowed, errors


def layer_of(filename: str, layers: list[tuple[str, re.Pattern]]) -> str:
    return next((name for name, rx in layers if rx.search(filename)), "other")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reports", action="append", required=True, help="glob of Cobertura XML files (repeatable, ** allowed)")
    parser.add_argument("--min-total", type=float, required=True, help="minimum total line coverage, percent")
    parser.add_argument("--untested-allowlist", help="fail on units no test runs, except those listed with a reason")
    parser.add_argument("--unit", choices=("class", "file"), default="class", help="what counts as a unit (default: class)")
    parser.add_argument("--min-lines", type=int, default=5, help="units with fewer coverable lines are not gated (default 5)")
    parser.add_argument("--exclude", action="append", default=[], help="regex on file path to leave out (generated code, migrations)")
    parser.add_argument("--layer", action="append", default=[], help="NAME=REGEX on file path, for the per-layer table")
    parser.add_argument("--json", dest="json_out", help="write the numbers as JSON")
    parser.add_argument("--summary-md", help="write the Markdown summary to this file (also appended to $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)

    try:
        excludes = [re.compile(x) for x in args.exclude]
        layers = []
        for spec in args.layer:
            name, sep, rx = spec.partition("=")
            if not sep or not name:
                raise ValueError(f"--layer expects NAME=REGEX, got '{spec}'")
            layers.append((name, re.compile(rx)))
    except (re.error, ValueError) as error:
        print(f"::error::{error}")
        return 2

    try:
        cov, files = read_reports(args.reports, excludes, args.unit)
    except (OSError, ET.ParseError, ValueError) as error:
        print(f"::error::cannot read coverage report: {error}")
        return 2
    if not files or not cov.lines:
        print("::error::No Cobertura coverage reports (or no coverable lines) found for: " + ", ".join(args.reports))
        return 2

    per_layer: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for (filename, _), covered in cov.lines.items():
        bucket = per_layer[layer_of(filename, layers)]
        bucket[0] += covered
        bucket[1] += 1
    covered_total = sum(cov.lines.values())
    total = 100.0 * covered_total / len(cov.lines)

    failed = False
    messages: list[str] = []
    if total < args.min_total:
        failed = True
        messages.append(f"::error::Line coverage {total:.1f}% is below the {args.min_total:g}% minimum.")

    if total >= args.min_total + 1:
        messages.append(f"::notice title=Coverage ratchet::{total:.1f}% — raise the minimum from {args.min_total:g}% to {int(total)}%.")

    untested = untested_units(cov, args.min_lines)
    new, stale, allowed = untested, [], {}
    if args.untested_allowlist:
        allowed, errors = read_allowlist(args.untested_allowlist)
        if errors:
            failed = True
            messages += [f"::error::{e}" for e in errors]
        untested_names = {name for name, _ in untested}
        new = [(name, n) for name, n in untested if name not in allowed]
        stale = sorted(set(allowed) - untested_names)
        if new:
            failed = True
            listing = ", ".join(f"{name} ({n} lines)" for name, n in new)
            messages.append(f"::error title=Code no test runs::{listing} — add a test, or list it with its reason in {args.untested_allowlist}.")
        if stale:
            messages.append(f"::warning::Now tested or gone — remove from {args.untested_allowlist}: {', '.join(stale)}")

    rows = ["| Layer | Line coverage |", "|---|---|"]
    rows += [f"| {name} | {100.0 * c / t:.1f}% ({c}/{t}) |" for name, (c, t) in sorted(per_layer.items())]
    rows.append(f"| **Total** | **{total:.1f}%** ({covered_total}/{len(cov.lines)}; minimum {args.min_total:g}%) |")
    summary = "### Test coverage\n" + "\n".join(rows) + "\n"
    if args.untested_allowlist:
        summary += f"\nUnits no test runs: {len(new)} new, {len(untested) - len(new)} allowlisted, {len(stale)} stale allowlist entries.\n"
        if new:
            summary += "\n" + "\n".join(f"- `{name}` ({n} lines) — needs a test" for name, n in new) + "\n"

    print(summary)
    for message in messages:
        print(message)
    for target in filter(None, (args.summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(summary + "\n")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as out:
            json.dump({
                "total": round(total, 1),
                "minimum": args.min_total,
                "passed": not failed,
                "layers": {name: {"covered": c, "lines": t} for name, (c, t) in per_layer.items()},
                "untested": [{"unit": name, "lines": n, "allowlisted": name in allowed} for name, n in untested],
                "staleAllowlist": stale,
            }, out, indent=2)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
