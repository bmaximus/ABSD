#!/usr/bin/env python3
"""Cycle telemetry for the ABSD pipeline: record, validate and report `absd-project/metrics/C###.json`.

Each cycle has one telemetry file, owned by the Manager and written ONLY through `record` (ABSD playbook PIPE-3). It
holds numbers, timestamps, enums and ids — never prompts, code, artifact text, names, paths or personal data
(PIPE-4): the tool refuses an unknown key, a wrong type, free text or any value not matching its pattern, and then
writes nothing. The file stays in the product repository; this tool never sends it anywhere. `Telemetry: off` in
context.md §14 makes `record` a no-op (notice, exit 0).

File (`schema: 1`): {"schema": 1, "cycle": "C003", "kit": "2.4.0", "mode": "F", "events": [...]}. Every event has
`seq` (1, 2, … in order) and `at` (UTC ISO 8601 ending in Z), plus by `kind` (required keys first, [optional]):
  invocation  agent step level model result [duration_s tokens]   tokens only when the platform reports them
  gate        gate round verdict [findings rules]                 findings: {critical|major|minor: n}; rules: ids
  halt        agent cause [step]
  rework      from to cause                                       from/to: a gate or an agent
  control     control red green                                   red/green: true|false (the negative control's runs)
  escape      defect why                                          why: the ESC why-missed class (kebab-case slug)
  resume      agent [step]
Enums: agent {manager analyst designer architect builder tester auditor}; step {brd analysis facts design
architecture arch-review plan-bind build verify design-qa audit second-audit reproduce baseline log harvest other};
level {strongest balanced fast}; result {done halt interrupted rejected}; gate {G1 GUX G2 G2R GT G3 XCA REL};
verdict {PASS FAIL}; halt cause {blueprint-gap spec-gap kit-gap external user}; rework cause {review-fail
upstream-gap spec-defect halt clr change-request}; severity = RULES §6 (critical major minor).
Patterns: model ^[A-Za-z0-9][A-Za-z0-9._:/-]{0,63}$; ids (rules, control, defect) ^[A-Z][A-Z0-9]*-\\d+$; cycle
^C\\d{3}$; why ^[a-z0-9]+(-[a-z0-9]+)*$ (≤ 32 chars); integers non-negative.

The report (Harvest, PIPE-5) reads every cycle: invocations, duration and tokens per step, agent, level and model
(tokens: sum of the known ones plus a count of unknown); per gate rounds, FAIL rate and first-pass rate; findings by
severity; rule ids by citation count; playbook rules never cited (listed only once at least --never-cited-after cycles
are read — candidates to drop or merge, proposed upstream, never deleted locally); halts, rework, controls and escapes.

usage:
  metrics.py record --file absd-project/metrics/C003.json --cycle C003 [--kit 2.4.0] [--mode F]
                    [--context absd-project/context.md] [--at 2026-11-11T10:00:00Z]
                    (--kind invocation --set agent=builder --set step=build ... | --event '<json>')
                    --set rules=ARCH-3,SEC-7   --set findings=major:1,minor:2   --set red=true
  metrics.py validate "absd-project/metrics/*.json" [...]
  metrics.py report --metrics "absd-project/metrics/*.json" [--playbook absd/playbook] [--never-cited-after 5]
                    [--json report.json] [--summary-md report.md]

Exit code: 0 ok, 1 an invalid file (validate) or nothing to report, 2 usage/input error (record refuses → 2, nothing
written). Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict

sys.dont_write_bytecode = True   # no __pycache__ in the kit: an untracked file breaks every clean-tree hand-off

SCHEMA = 1
AGENTS = {"manager", "analyst", "designer", "architect", "builder", "tester", "auditor"}
STEPS = {"brd", "analysis", "facts", "design", "architecture", "arch-review", "plan-bind", "build", "verify",
         "design-qa", "audit", "second-audit", "reproduce", "baseline", "log", "harvest", "other"}
LEVELS = {"strongest", "balanced", "fast"}
RESULTS = {"done", "halt", "interrupted", "rejected"}
GATES = {"G1", "GUX", "G2", "G2R", "GT", "G3", "XCA", "REL"}
VERDICTS = {"PASS", "FAIL"}
HALT_CAUSES = {"blueprint-gap", "spec-gap", "kit-gap", "external", "user"}
REWORK_CAUSES = {"review-fail", "upstream-gap", "spec-defect", "halt", "clr", "change-request"}
SEVERITIES = ("critical", "major", "minor")   # RULES §6
ENDPOINTS = GATES | AGENTS

MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,63}$")
ID = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")
CYCLE = re.compile(r"^C\d{3}$")
KIT = re.compile(r"^\d+\.\d+\.\d+$")
MODE = re.compile(r"^[A-Z]$")
WHY = re.compile(r"^(?=.{1,32}$)[a-z0-9]+(?:-[a-z0-9]+)*$")
AT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")

def _enum(values):
    return lambda v: isinstance(v, str) and v in values


def _pattern(rx):
    return lambda v: isinstance(v, str) and bool(rx.match(v))


def _count(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _positive(v):
    return _count(v) and v >= 1


def _bool(v):
    return isinstance(v, bool)


def _findings(v):
    return isinstance(v, dict) and all(k in SEVERITIES and _count(n) for k, n in v.items())


def _rules(v):
    return isinstance(v, list) and all(isinstance(r, str) and ID.match(r) for r in v)


KINDS = {   # kind -> {key: (validator, required?)}
    "invocation": {"agent": (_enum(AGENTS), True), "step": (_enum(STEPS), True), "level": (_enum(LEVELS), True),
                   "model": (_pattern(MODEL), True), "result": (_enum(RESULTS), True),
                   "duration_s": (_count, False), "tokens": (_count, False)},
    "gate": {"gate": (_enum(GATES), True), "round": (_positive, True), "verdict": (_enum(VERDICTS), True),
             "findings": (_findings, False), "rules": (_rules, False)},
    "halt": {"agent": (_enum(AGENTS), True), "cause": (_enum(HALT_CAUSES), True), "step": (_enum(STEPS), False)},
    "rework": {"from": (_enum(ENDPOINTS), True), "to": (_enum(ENDPOINTS), True), "cause": (_enum(REWORK_CAUSES), True)},
    "control": {"control": (_pattern(ID), True), "red": (_bool, True), "green": (_bool, True)},
    "escape": {"defect": (_pattern(ID), True), "why": (_pattern(WHY), True)},
    "resume": {"agent": (_enum(AGENTS), True), "step": (_enum(STEPS), False)},
}
COMMON = {"seq": _positive, "kind": _enum(set(KINDS)), "at": _pattern(AT)}
TOP = {"schema": (lambda v: v == SCHEMA and not isinstance(v, bool), True), "cycle": (_pattern(CYCLE), True),
       "kit": (_pattern(KIT), False), "mode": (_pattern(MODE), False), "events": (lambda v: isinstance(v, list), True)}

PLAYBOOK_RULE = re.compile(r"^\*\*([A-Z][A-Z0-9]*-\d+)\*\* — ?(.*)$", re.MULTILINE)
TELEMETRY_OFF = re.compile(r"\btelemetry\s*:\s*off\b", re.IGNORECASE)
SECTION_14 = re.compile(r"^#{1,6}\s*(?:§\s*)?14\b", re.MULTILINE)
HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)


def _show(value) -> str:
    """A refused value is named by its type only: it may be the very free text the tool refuses to store."""
    return type(value).__name__


def validate_event(event, where: str = "event") -> list[str]:
    if not isinstance(event, dict):
        return [f"{where}: not an object"]
    problems = []
    kind = event.get("kind")
    if not COMMON["kind"](kind):
        return [f"{where}: kind must be one of {', '.join(sorted(KINDS))}"]
    spec = KINDS[kind]
    for key in COMMON:
        if key not in event:
            problems.append(f"{where}: missing '{key}'")
        elif not COMMON[key](event[key]):
            problems.append(f"{where}: '{key}' is not valid ({_show(event[key])})")
    for key, (check, required) in spec.items():
        if key not in event:
            if required:
                problems.append(f"{where}: {kind} needs '{key}'")
        elif not check(event[key]):
            problems.append(f"{where}: {kind} '{key}' is not an allowed value ({_show(event[key])})")
    for key in event:
        if key not in COMMON and key not in spec:
            problems.append(f"{where}: unknown key for {kind} (keys allowed: {', '.join(list(COMMON) + list(spec))})")
    return problems


def validate_doc(doc) -> list[str]:
    """Every problem in a telemetry document (empty list: valid)."""
    if not isinstance(doc, dict):
        return ["the file is not a JSON object"]
    problems = []
    for key, (check, required) in TOP.items():
        if key not in doc:
            if required:
                problems.append(f"missing '{key}'")
        elif not check(doc[key]):
            problems.append(f"'{key}' is not valid ({_show(doc[key])})")
    for key in doc:
        if key not in TOP:
            problems.append("unknown top-level key (allowed: " + ", ".join(TOP) + ")")
    events = doc.get("events") if isinstance(doc.get("events"), list) else []
    for index, event in enumerate(events):
        problems += validate_event(event, f"events[{index}]")
        if isinstance(event, dict) and event.get("seq") != index + 1 and _positive(event.get("seq")):
            problems.append(f"events[{index}]: seq must be {index + 1} (events are numbered 1, 2, … in order)")
    return problems


def load(path: str) -> dict:
    """Read and validate one telemetry file; raises ValueError (naming the file) when it is unreadable or invalid."""
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: cannot read: {error}") from error
    problems = validate_doc(doc)
    if problems:
        raise ValueError(f"{path}: " + "; ".join(problems))
    return doc


def expand(patterns) -> list[str]:
    if isinstance(patterns, str):
        patterns = [patterns]
    return sorted({p for pattern in patterns for p in glob.glob(pattern, recursive=True) if os.path.isfile(p)})


def load_all(patterns) -> list[dict]:
    """Load every file the globs match (sorted by path); raises ValueError on the first invalid one."""
    return [load(path) for path in expand(patterns)]


# ---------------------------------------------------------------------------------------------------------- record

def telemetry_off(context_path: str) -> bool:
    """`Telemetry: off` (any case, Markdown emphasis or code marks allowed) in §14 of context.md; the whole file when it
    has no §14 heading. A missing context.md leaves telemetry on (the kit default)."""
    try:
        with open(context_path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    start = SECTION_14.search(text)
    if start:
        following = HEADING.search(text, start.end())
        text = text[start.start():following.start() if following else len(text)]
    return any(TELEMETRY_OFF.search(re.sub(r"[*`_]", "", line)) for line in text.splitlines())


def parse_value(key: str, raw: str):
    if key == "rules":
        return [r.strip() for r in raw.split(",") if r.strip()]
    if key == "findings":
        findings = {}
        for part in filter(None, (p.strip() for p in raw.split(","))):
            name, sep, number = part.partition(":")
            if not sep or not re.fullmatch(r"\d+", number.strip()):
                raise ValueError(f"findings expects severity:count[,severity:count], got a malformed part for '{name.strip()}'")
            findings[name.strip()] = int(number.strip())
        return findings
    if raw in ("true", "false"):
        return raw == "true"
    if re.fullmatch(r"\d+", raw):
        return int(raw)
    return raw


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write(path: str, doc: dict) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    handle, temp = tempfile.mkstemp(prefix=".metrics-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            json.dump(doc, out, indent=1)
            out.write("\n")
        os.replace(temp, path)
    except BaseException:
        if os.path.exists(temp):
            os.unlink(temp)
        raise


def record(args) -> int:
    if telemetry_off(args.context):
        print(f"::notice title=Telemetry off::{args.context} sets Telemetry: off — nothing recorded.")
        return 0
    if bool(args.event) == bool(args.kind):
        print("::error::record needs exactly one of --kind (with --set) or --event")
        return 2
    try:
        if args.event:
            event = json.loads(args.event)
            if not isinstance(event, dict):
                raise ValueError("--event must be a JSON object")
            if args.set:
                raise ValueError("--set cannot be combined with --event")
        else:
            event = {"kind": args.kind}
            for item in args.set:
                key, sep, raw = item.partition("=")
                if not sep or not key:
                    raise ValueError("--set expects key=value")
                if key in event:
                    raise ValueError(f"--set {key} given twice")
                event[key] = parse_value(key, raw)
    except (ValueError, json.JSONDecodeError) as error:
        print(f"::error::{error} — nothing recorded")
        return 2

    if os.path.exists(args.file):
        try:
            doc = load(args.file)
        except ValueError as error:
            print(f"::error::{error} — nothing recorded")
            return 2
        if doc["cycle"] != args.cycle:
            print(f"::error::{args.file} belongs to {doc['cycle']}, not {args.cycle} — nothing recorded")
            return 2
    else:
        doc = {"schema": SCHEMA, "cycle": args.cycle, "events": []}
    for key in ("kit", "mode"):
        value = getattr(args, key)
        if value is not None:
            if key in doc and doc[key] != value:
                print(f"::error::{args.file} records {key} {doc[key]}, not {value} — nothing recorded")
                return 2
            doc[key] = value

    event = {"seq": len(doc["events"]) + 1, "at": args.at or now_utc(), **{k: v for k, v in event.items() if k not in ("seq", "at")}}
    doc["events"].append(event)
    problems = validate_doc(doc)
    if problems:
        for problem in problems:
            print(f"::error::{problem}")
        print("::error::refused — nothing recorded (only numbers, timestamps, enums and ids are stored; ABSD:PIPE-4)")
        return 2
    try:
        atomic_write(args.file, doc)
    except OSError as error:
        print(f"::error::cannot write {args.file}: {error}")
        return 2
    print(f"recorded {args.cycle} #{event['seq']} {event['kind']}")
    return 0


# -------------------------------------------------------------------------------------------------------- validate

def validate(args) -> int:
    failed, checked = False, 0
    for pattern in args.patterns:
        paths = expand(pattern)
        if not paths:
            print(f"::notice::no telemetry file matches {pattern}")
        for path in paths:
            checked += 1
            try:
                load(path)
            except ValueError as error:
                failed = True
                print(f"::error file={path}::{error}")
    print(f"{'✗' if failed else '✓'} telemetry files ({checked} checked)")
    return 1 if failed else 0


# ---------------------------------------------------------------------------------------------------------- report

def playbook_rules(root: str) -> list[str]:
    """Active rule ids of the playbook: `**CODE-n** —` lines, tombstones ("Retired in …") skipped."""
    ids = set()
    for path in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
        with open(path, encoding="utf-8") as f:
            for match in PLAYBOOK_RULE.finditer(f.read()):
                if not match.group(2).startswith("Retired in"):
                    ids.add(match.group(1))
    return sorted(ids, key=lambda r: (r.rsplit("-", 1)[0], int(r.rsplit("-", 1)[1])))


def _bucket():
    return {"invocations": 0, "duration_s": 0, "duration_unknown": 0, "tokens": 0, "tokens_unknown": 0}


def build_report(docs: list[dict], playbook_ids: list[str] | None = None, never_cited_after: int = 5) -> dict:
    by = {name: defaultdict(_bucket) for name in ("step", "agent", "level", "model")}
    gates = defaultdict(lambda: {"rounds": 0, "fail": 0, "instances": 0, "first_pass": 0})
    first_round = {}   # (cycle, gate) -> verdict of its lowest round
    findings = Counter({s: 0 for s in SEVERITIES})
    cited, halts, rework, escapes = Counter(), Counter(), Counter(), Counter()
    controls = {"total": 0, "ok": 0, "not_ok": []}
    for doc in docs:
        cycle = doc["cycle"]
        lowest = {}
        for event in doc["events"]:
            kind = event["kind"]
            if kind == "invocation":
                for name in by:
                    bucket = by[name][event[name]]
                    bucket["invocations"] += 1
                    for key, unknown in (("duration_s", "duration_unknown"), ("tokens", "tokens_unknown")):
                        if key in event:
                            bucket[key] += event[key]
                        else:
                            bucket[unknown] += 1
            elif kind == "gate":
                gate = gates[event["gate"]]
                gate["rounds"] += 1
                gate["fail"] += event["verdict"] == "FAIL"
                if event["gate"] not in lowest or event["round"] < lowest[event["gate"]][0]:
                    lowest[event["gate"]] = (event["round"], event["verdict"])
                findings.update(event.get("findings", {}))
                cited.update(event.get("rules", []))
            elif kind == "halt":
                halts[event["cause"]] += 1
            elif kind == "rework":
                rework[f"{event['from']}→{event['to']} ({event['cause']})"] += 1
            elif kind == "control":
                controls["total"] += 1
                if event["red"] and event["green"]:
                    controls["ok"] += 1
                else:
                    controls["not_ok"].append(f"{cycle} {event['control']}")
            elif kind == "escape":
                escapes[event["why"]] += 1
        for gate_name, (_, verdict) in lowest.items():
            first_round[(cycle, gate_name)] = verdict
    for (_, gate_name), verdict in first_round.items():
        gates[gate_name]["instances"] += 1
        gates[gate_name]["first_pass"] += verdict == "PASS"
    for gate in gates.values():
        gate["fail_rate"] = round(gate["fail"] / gate["rounds"], 3) if gate["rounds"] else 0.0
        gate["first_pass_rate"] = round(gate["first_pass"] / gate["instances"], 3) if gate["instances"] else 0.0
    cycles = sorted({doc["cycle"] for doc in docs})
    never = None
    if playbook_ids is not None and len(cycles) >= never_cited_after:
        never = [rule for rule in playbook_ids if rule not in cited]
    return {
        "cycles": cycles,
        "by": {name: dict(sorted(values.items())) for name, values in by.items()},
        "gates": dict(sorted(gates.items())),
        "findings": dict(findings),
        "rules_cited": dict(sorted(cited.items(), key=lambda item: (-item[1], item[0]))),
        "never_cited": never,
        "never_cited_after": never_cited_after,
        "halts": dict(halts.most_common()),
        "rework": dict(rework.most_common()),
        "controls": controls,
        "escapes": dict(escapes.most_common()),
    }


def summary_markdown(report: dict) -> str:
    lines = [f"### Pipeline telemetry ({len(report['cycles'])} cycles: {', '.join(report['cycles'])})", ""]
    for name in ("step", "agent", "level", "model"):
        rows = report["by"][name]
        if not rows:
            continue
        lines += [f"| {name.capitalize()} | Invocations | Duration (s) | Tokens (known) | Tokens unknown |", "|---|---|---|---|---|"]
        for key, b in sorted(rows.items(), key=lambda item: -item[1]["tokens"]):
            lines.append(f"| {key} | {b['invocations']} | {b['duration_s']} | {b['tokens']} | {b['tokens_unknown']} |")
        lines.append("")
    if report["gates"]:
        lines += ["| Gate | Rounds | FAIL rate | First-pass rate |", "|---|---|---|---|"]
        for gate, g in report["gates"].items():
            lines.append(f"| {gate} | {g['rounds']} | {100 * g['fail_rate']:.0f}% | {100 * g['first_pass_rate']:.0f}% |")
        lines.append("")
    lines.append("Findings: " + ", ".join(f"{s} {n}" for s, n in report["findings"].items()))
    lines.append("Rules cited: " + (", ".join(f"{r} ×{n}" for r, n in report["rules_cited"].items()) or "none"))
    if report["never_cited"] is None:
        lines.append(f"Never-cited rules: listed from {report['never_cited_after']} cycles on (or no --playbook).")
    else:
        lines.append(f"Never-cited rules ({len(report['never_cited'])}, candidates to drop or merge — propose upstream): "
                     + (", ".join(report["never_cited"]) or "none"))
    for label, key in (("Halts by cause", "halts"), ("Rework", "rework"), ("Escapes by why-missed class", "escapes")):
        lines.append(f"{label}: " + (", ".join(f"{k} {n}" for k, n in report[key].items()) or "none"))
    c = report["controls"]
    lines.append(f"Negative controls: {c['ok']}/{c['total']} red then green"
                 + (f" — not ok: {', '.join(c['not_ok'])}" if c["not_ok"] else ""))
    return "\n".join(lines) + "\n"


def report(args) -> int:
    paths = expand(args.metrics)
    if not paths:
        print(f"::notice::no telemetry file matches {', '.join(args.metrics)} — nothing to report")
        return 1
    try:
        docs = [load(path) for path in paths]
        ids = playbook_rules(args.playbook) if args.playbook else None
    except (ValueError, OSError) as error:
        print(f"::error::{error}")
        return 2
    if args.playbook and not ids:
        print(f"::error::no playbook rule found under {args.playbook}")
        return 2
    result = build_report(docs, ids, args.never_cited_after)
    summary = summary_markdown(result)
    print(summary)
    for target in filter(None, (args.summary_md, os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a", encoding="utf-8") as out:
            out.write(summary + "\n")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as out:
            json.dump(result, out, indent=2, ensure_ascii=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="append one event to a cycle's telemetry file")
    rec.add_argument("--file", required=True, help="absd-project/metrics/C###.json")
    rec.add_argument("--cycle", required=True, help="C###")
    rec.add_argument("--kit", help="kit version (x.y.z)")
    rec.add_argument("--mode", help="cycle mode letter")
    rec.add_argument("--kind", choices=sorted(KINDS))
    rec.add_argument("--set", action="append", default=[], help="key=value (repeatable)")
    rec.add_argument("--event", help="the event as a JSON object instead of --kind/--set")
    rec.add_argument("--at", help="timestamp to record (default: now, UTC)")
    rec.add_argument("--context", default="absd-project/context.md", help="context.md read for 'Telemetry: off'")
    val = sub.add_parser("validate", help="validate telemetry files")
    val.add_argument("patterns", nargs="+", help="globs of telemetry files")
    rep = sub.add_parser("report", help="report over every cycle's telemetry")
    rep.add_argument("--metrics", action="append", required=True, help="glob of telemetry files (repeatable)")
    rep.add_argument("--playbook", help="playbook root, for rules never cited")
    rep.add_argument("--never-cited-after", type=int, default=5, help="list never-cited rules from this many cycles on")
    rep.add_argument("--json", dest="json_out", help="write the report as JSON")
    rep.add_argument("--summary-md", help="write the Markdown summary to this file (also appended to $GITHUB_STEP_SUMMARY)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return int(exit_.code or 0)
    if args.command == "record":
        for name, value, rx in (("--cycle", args.cycle, CYCLE), ("--kit", args.kit, KIT), ("--mode", args.mode, MODE)):
            if value is not None and not rx.match(value):
                print(f"::error::{name} is not valid — nothing recorded")
                return 2
        if args.at is not None and not AT.match(args.at):
            print("::error::--at must be UTC ISO 8601 ending in Z — nothing recorded")
            return 2
        return record(args)
    return validate(args) if args.command == "validate" else report(args)


if __name__ == "__main__":
    sys.exit(main())
