#!/usr/bin/env python3
"""ABSD agent benchmark scorer (ABSD playbook PIPE-6): seeded traps caught, gate rounds, halts and cost per fixture run.

A benchmark run installs the kit into an empty repository, gives the runner a fixture's brief.md (never its
traps.json), runs Bootstrap and the feature cycle with telemetry on, and then scores the final repository here.

Commands:
  score    One fixture run → one result JSON.
             traps    each trap in <fixture>/traps.json is caught when its detectors' regexes (case-insensitive,
                      multiline: ^ and $ are line ends, . stays on one line) match in at least min_matches of its
                      detector globs (relative to --repo, ** allowed) — the artifact evidence that a requirement,
                      question, assumption, decision or test case dealt with it.
             gates    from the repo's absd-project/metrics/*.json (read with absd/tooling/metrics.py, so an invalid
                      telemetry file is refused): per (cycle, gate) the rounds, FAIL rounds and whether round 1 passed.
             halts    by cause, kit-gap halts counted apart (a question the kit should have answered).
             controls negative controls that turned both RED and GREEN.
             cost     invocations, total duration, tokens (sum of the known ones, count of unknown ones).
             criteria the runner's reported ENR-14 results, --criteria c1=pass,c2=pass,c3=pass:
                      c1 every Foundation negative control turned RED then GREEN; c2 trace_check and ownership_check
                      passed at every gate; c3 no agent halted on a question the kit should have answered.
           No metrics directory, or one with no telemetry file, is RED: telemetry is part of the benchmark.
  combine  Result JSONs of one kit version → benchmark/results/<version>.json (per fixture + totals).
  compare  Candidate against the last accepted baseline. Regression (exit 1): a fixture missing, a trap the baseline
           caught now missed or fewer traps caught in total, more kit-gap halts, any ENR-14 criterion not passing,
           first-pass gate rate down by more than 10 points. Token or time growth above 25 % is a warning (record it in
           the CHANGELOG). A missing baseline is a notice: the candidate becomes the first baseline.

usage:
  score.py score --fixture benchmark/fixtures/tally --repo <run repo> --kit-version 2.4.0
                 [--criteria c1=pass,c2=pass,c3=pass] --out result.json
  score.py combine RESULT.json... --out benchmark/results/2.4.0.json
  score.py compare --baseline benchmark/results/<prev>.json --candidate benchmark/results/<new>.json
  --summary-md OUT (any command) writes the printed lines as Markdown; also appended to $GITHUB_STEP_SUMMARY.

Exit code: 0 pass, 1 red (traps file fine but telemetry missing, or a regression), 2 usage/input error.
Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.dont_write_bytecode = True   # keep the kit tree clean: no __pycache__ next to the tools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "absd", "tooling"))
import metrics  # noqa: E402  (one reading of the telemetry format for the pipeline and the benchmark)

SCHEMA = 1
TRAP_KINDS = {"ambiguity", "variation", "contradiction", "security", "external-fact", "time", "process",
              "reachability", "idempotency", "aesthetic"}
LEVELS = ("planned", "tested")   # depth above "raised": a TC row plans it, test code exercises it
SKIP_DIRS = {"node_modules", ".venv", "venv", ".git", "__pycache__", "dist", "build"}
TOKEN_COVERAGE = 90.0       # % of invocations with a platform-reported token count (PIPE-6)
TRAP_ID = re.compile(r"^TRAP-[A-Z][A-Z0-9]*-\d+$")
CRITERIA = ("c1", "c2", "c3")
CRITERION_VALUES = {"pass", "fail"}
METRICS_DIR = "absd-project/metrics"
FIRST_PASS_DROP = 10.0      # points
COST_GROWTH = 0.25          # fraction


class InputError(Exception):
    """A usage or input problem: exit 2."""


# ------------------------------------------------------------------------------------------------------------ traps

def load_traps(fixture: str) -> list[dict]:
    path = os.path.join(fixture, "traps.json")
    try:
        with open(path, encoding="utf-8") as f:
            traps = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InputError(f"{path}: cannot read: {error}") from error
    if not isinstance(traps, list) or not traps:
        raise InputError(f"{path}: a non-empty list of traps is required")
    seen = set()
    for n, trap in enumerate(traps, 1):
        where = f"{path}: trap {n}"
        if not isinstance(trap, dict) or set(trap) - {"id", "kind", "summary", "detect", "min_matches", *LEVELS}:
            raise InputError(f"{where}: an object with id, kind, summary, detect, min_matches"
                             f" [, {', '.join(LEVELS)}] is required")
        if not isinstance(trap.get("id"), str) or not TRAP_ID.match(trap["id"]) or trap["id"] in seen:
            raise InputError(f"{where}: id must be a unique TRAP-<FIXTURE>-n")
        seen.add(trap["id"])
        if trap.get("kind") not in TRAP_KINDS:
            raise InputError(f"{where}: kind must be one of {', '.join(sorted(TRAP_KINDS))}")
        if not isinstance(trap.get("summary"), str) or not trap["summary"].strip():
            raise InputError(f"{where}: summary is required")
        trap["min_matches"] = check_detectors(trap.get("detect"), trap.get("min_matches", 1), where)
        for level in LEVELS:
            if level in trap:
                spec = trap[level]
                if not isinstance(spec, dict) or set(spec) - {"detect", "min_matches"}:
                    raise InputError(f"{where}: {level} is {{\"detect\": [...], \"min_matches\": n}}")
                spec["min_matches"] = check_detectors(spec.get("detect"), spec.get("min_matches", 1),
                                                      f"{where} {level}")
    return traps


def check_detectors(detect, need, where: str) -> int:
    if not isinstance(detect, list) or not detect:
        raise InputError(f"{where}: detect must be a non-empty list")
    for d in detect:
        if not isinstance(d, dict) or set(d) != {"glob", "regex"} or not all(isinstance(v, str) for v in d.values()):
            raise InputError(f"{where}: each detector is {{\"glob\": ..., \"regex\": ...}}")
        try:
            d["compiled"] = re.compile(d["regex"], re.IGNORECASE | re.MULTILINE)
        except re.error as error:
            raise InputError(f"{where}: bad regex {d['regex']!r}: {error}") from error
    if not isinstance(need, int) or isinstance(need, bool) or not 1 <= need <= len(detect):
        raise InputError(f"{where}: min_matches must be an integer from 1 to the number of detectors")
    return need


def run_detectors(detect: list, repo: str) -> list:
    matches = []
    for d in detect:
        for path in sorted(glob.glob(os.path.join(repo, d["glob"]), recursive=True)):
            if not os.path.isfile(path) or SKIP_DIRS & set(os.path.relpath(path, repo).split(os.sep)):
                continue
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            hit = d["compiled"].search(text)
            if hit:
                matches.append({"glob": d["glob"], "file": os.path.relpath(path, repo).replace(os.sep, "/"),
                                "line": text.count("\n", 0, hit.start()) + 1})
                break   # one file is enough for this detector
    return matches


def detect_trap(trap: dict, repo: str) -> dict:
    """Raised when at least min_matches detectors matched; depth adds 1 for each level (planned, tested) reached."""
    matches = run_detectors(trap["detect"], repo)
    caught = len(matches) >= trap["min_matches"]
    levels = {}
    for level in LEVELS:
        if level in trap:
            found = run_detectors(trap[level]["detect"], repo)
            levels[level] = {"reached": caught and len(found) >= trap[level]["min_matches"], "matches": found}
    depth = (1 + sum(v["reached"] for v in levels.values())) if caught else 0
    return {"id": trap["id"], "kind": trap["kind"], "summary": trap["summary"], "caught": caught, "matches": matches,
            "depth": depth, "max_depth": 1 + len(levels), "levels": levels}


# ---------------------------------------------------------------------------------------------------------- metrics

def telemetry_summary(docs: list[dict]) -> dict:
    gates: dict = {}
    halts: dict = {}
    controls = {"total": 0, "ok": 0}
    cost = {"invocations": 0, "duration_s": 0, "tokens": 0, "tokens_unknown": 0}
    for doc in docs:
        for event in sorted(doc["events"], key=lambda e: e["seq"]):
            kind = event["kind"]
            if kind == "gate":
                if event.get("repass"):
                    continue   # a re-pass after an upstream change is not a review round
                rounds = gates.setdefault((doc["cycle"], event["gate"]), [])
                rounds.append(event["verdict"])
            elif kind == "halt":
                halts[event["cause"]] = halts.get(event["cause"], 0) + 1
            elif kind == "control":
                controls["total"] += 1
                controls["ok"] += bool(event.get("red") and event.get("green"))
            elif kind == "invocation":
                cost["invocations"] += 1
                cost["duration_s"] += event.get("duration_s", 0)
                if "tokens" in event:
                    cost["tokens"] += event["tokens"]
                else:
                    cost["tokens_unknown"] += 1
    cost["token_coverage"] = rate(cost["invocations"] - cost["tokens_unknown"], cost["invocations"])
    per_gate = [{"cycle": cycle, "gate": gate, "rounds": len(v), "fail_rounds": v.count("FAIL"),
                 "first_pass": v[0] == "PASS"} for (cycle, gate), v in sorted(gates.items())]
    first = sum(g["first_pass"] for g in per_gate)
    return {"cycles": sorted(doc["cycle"] for doc in docs),
            "gates": {"total": len(per_gate), "first_pass": first, "first_pass_rate": rate(first, len(per_gate)),
                      "fail_rounds": sum(g["fail_rounds"] for g in per_gate), "list": per_gate},
            "halts": {"total": sum(halts.values()), "kit_gap": halts.get("kit-gap", 0), "by_cause": halts},
            "controls": controls, "cost": cost}


def rate(part: int, whole: int):
    return round(100.0 * part / whole, 1) if whole else None


def parse_criteria(raw: str | None) -> dict:
    criteria = {c: None for c in CRITERIA}     # None: not reported — counts as not passing in compare
    for item in filter(None, (s.strip() for s in (raw or "").split(","))):
        key, sep, value = item.partition("=")
        if not sep or key not in CRITERIA or value not in CRITERION_VALUES:
            raise InputError(f"--criteria: {item!r} is not one of {', '.join(CRITERIA)} = pass|fail")
        criteria[key] = value
    return criteria


def score(args) -> tuple[int, list[str]]:
    if not os.path.isdir(args.repo):
        raise InputError(f"--repo {args.repo} is not a directory")
    if not metrics.KIT.match(args.kit_version):
        raise InputError(f"--kit-version {args.kit_version!r} is not x.y.z")
    traps = load_traps(args.fixture)
    criteria = parse_criteria(args.criteria)
    fixture = os.path.basename(os.path.normpath(args.fixture))
    pattern = os.path.join(args.repo, METRICS_DIR, "*.json")
    if not glob.glob(pattern):
        return 1, [f"::error::no telemetry in {os.path.join(args.repo, METRICS_DIR)} — run the cycle with telemetry on "
                   "(PIPE-3); the benchmark scores it"]
    try:
        docs = metrics.load_all([pattern])
    except ValueError as error:
        return 1, [f"::error::invalid telemetry: {error}"]
    caught = [detect_trap(t, args.repo) for t in traps]
    result = {"schema": SCHEMA, "fixture": fixture, "kit": args.kit_version,
              "traps": {"total": len(caught), "caught": sum(t["caught"] for t in caught),
                        "depth": sum(t["depth"] for t in caught), "max_depth": sum(t["max_depth"] for t in caught),
                        "list": caught},
              **telemetry_summary(docs), "criteria": criteria}
    write_json(args.out, result)
    lines = [f"{fixture} on kit {args.kit_version}: {result['traps']['caught']}/{len(caught)} traps caught, depth "
             f"{result['traps']['depth']}/{result['traps']['max_depth']}"]
    lines += [f"  {'✓' if t['caught'] else '✗'} {t['id']} ({t['kind']}, depth {t['depth']}/{t['max_depth']})"
              + (f" — {', '.join(m['file'] + ':' + str(m['line']) for m in t['matches'])}" if t["matches"] else "")
              for t in caught]
    g = result["gates"]
    c = result["cost"]
    lines.append(f"  gates {g['first_pass']}/{g['total']} first pass, {g['fail_rounds']} FAIL rounds; "
                 f"kit-gap halts {result['halts']['kit_gap']}; controls {result['controls']['ok']}/"
                 f"{result['controls']['total']} ok; {c['invocations']} invocations, tokens known for "
                 f"{c['token_coverage']}%")
    return 0, lines


# ---------------------------------------------------------------------------------------------- combine and compare

def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InputError(f"{path}: cannot read: {error}") from error
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise InputError(f"{path}: not a schema {SCHEMA} benchmark result")
    return doc


def write_json(path: str, doc: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
        f.write("\n")


def totals(fixtures: dict) -> dict:
    results = list(fixtures.values())
    gates = sum(r["gates"]["total"] for r in results)
    first = sum(r["gates"]["first_pass"] for r in results)
    invocations = sum(r["cost"]["invocations"] for r in results)
    unknown = sum(r["cost"]["tokens_unknown"] for r in results)
    return {"traps_total": sum(r["traps"]["total"] for r in results),
            "traps_caught": sum(r["traps"]["caught"] for r in results),
            "depth": sum(r["traps"].get("depth", r["traps"]["caught"]) for r in results),
            "max_depth": sum(r["traps"].get("max_depth", r["traps"]["total"]) for r in results),
            "token_coverage": rate(invocations - unknown, invocations),
            "gates_total": gates, "gates_first_pass": first, "first_pass_rate": rate(first, gates),
            "fail_rounds": sum(r["gates"]["fail_rounds"] for r in results),
            "kit_gap_halts": sum(r["halts"]["kit_gap"] for r in results),
            "criteria_not_passing": sum(v != "pass" for r in results for v in r["criteria"].values()),
            **{k: sum(r["cost"][k] for r in results) for k in ("invocations", "duration_s", "tokens", "tokens_unknown")}}


def combine(args) -> tuple[int, list[str]]:
    fixtures: dict = {}
    kit = None
    for path in args.results:
        result = read_json(path)
        if "fixture" not in result:
            raise InputError(f"{path}: not a single-fixture result (combine takes score outputs)")
        if kit is not None and result["kit"] != kit:
            raise InputError(f"{path}: kit {result['kit']} differs from {kit}; combine one kit version at a time")
        kit = result["kit"]
        if result["fixture"] in fixtures:
            raise InputError(f"{path}: fixture {result['fixture']} given twice")
        fixtures[result["fixture"]] = result
    combined = {"schema": SCHEMA, "kit": kit, "fixtures": fixtures, "totals": totals(fixtures)}
    write_json(args.out, combined)
    t = combined["totals"]
    return 0, [f"kit {kit}: {len(fixtures)} fixtures, {t['traps_caught']}/{t['traps_total']} traps caught, depth "
               f"{t['depth']}/{t['max_depth']}, tokens known for {t['token_coverage']}%, "
               f"first-pass gate rate {t['first_pass_rate']}%, kit-gap halts {t['kit_gap_halts']}"]


def compare(args) -> tuple[int, list[str]]:
    if not os.path.isfile(args.baseline):
        return 0, [f"::notice::no baseline at {args.baseline} — this result becomes the first baseline"]
    base, cand = read_json(args.baseline), read_json(args.candidate)
    for path, doc in ((args.baseline, base), (args.candidate, cand)):
        if "fixtures" not in doc:
            raise InputError(f"{path}: not a combined result (run combine first)")
    regressions, warnings = [], []
    for name, b in sorted(base["fixtures"].items()):
        c = cand["fixtures"].get(name)
        if c is None:
            regressions.append(f"fixture {name} has no result in the candidate")
            continue
        now = {t["id"]: t["caught"] for t in c["traps"]["list"]}
        regressions += [f"{name}: {t['id']} was caught by {base['kit']}, missed now"
                        for t in b["traps"]["list"] if t["caught"] and not now.get(t["id"], False)]
    bt, ct = base["totals"], cand["totals"]
    if ct["traps_caught"] < bt["traps_caught"]:
        regressions.append(f"traps caught {ct['traps_caught']} < {bt['traps_caught']}")
    if "depth" in bt and "depth" in ct:
        common = {name for name in base["fixtures"] if name in cand["fixtures"]}
        b_depth = sum(base["fixtures"][n]["traps"].get("depth", base["fixtures"][n]["traps"]["caught"]) for n in common)
        c_depth = sum(cand["fixtures"][n]["traps"].get("depth", cand["fixtures"][n]["traps"]["caught"]) for n in common)
        if c_depth < b_depth:
            regressions.append(f"trap depth on the baseline's fixtures {c_depth} < {b_depth}")
    if ct.get("token_coverage") is None or ct["token_coverage"] < TOKEN_COVERAGE:
        regressions.append(f"tokens known for {ct.get('token_coverage')}% of invocations — at least "
                           f"{TOKEN_COVERAGE:g}% required (PIPE-6)")
    if ct["kit_gap_halts"] > bt["kit_gap_halts"]:
        regressions.append(f"kit-gap halts {ct['kit_gap_halts']} > {bt['kit_gap_halts']}")
    regressions += [f"{name}: ENR-14 criterion {k} is {v or 'not reported'}"
                    for name, r in sorted(cand["fixtures"].items()) for k, v in sorted(r["criteria"].items())
                    if v != "pass"]
    if bt["first_pass_rate"] is not None and ct["first_pass_rate"] is not None \
            and bt["first_pass_rate"] - ct["first_pass_rate"] > FIRST_PASS_DROP:
        regressions.append(f"first-pass gate rate {ct['first_pass_rate']}% is more than {FIRST_PASS_DROP:g} points "
                           f"below {bt['first_pass_rate']}%")
    for key, label in (("tokens", "tokens"), ("duration_s", "duration")):
        if bt[key] and ct[key] > bt[key] * (1 + COST_GROWTH):
            warnings.append(f"{label} grew {100.0 * (ct[key] - bt[key]) / bt[key]:.0f} % ({bt[key]} → {ct[key]}) — "
                            "record it in the CHANGELOG")
    if ct["tokens_unknown"] or bt["tokens_unknown"]:
        warnings.append(f"token totals are partial (unknown: baseline {bt['tokens_unknown']}, "
                        f"candidate {ct['tokens_unknown']})")
    lines = [f"::error::{r}" for r in regressions] + [f"::warning::{w}" for w in warnings]
    verdict = "REGRESSION" if regressions else "no regression"
    lines.append(f"{cand['kit']} against {base['kit']}: {verdict} ({ct['traps_caught']}/{ct['traps_total']} traps, "
                 f"first-pass {ct['first_pass_rate']}%, kit-gap halts {ct['kit_gap_halts']})")
    return (1 if regressions else 0), lines


# ------------------------------------------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--summary-md")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("score", help="score one fixture run")
    p.add_argument("--fixture", required=True, help="benchmark/fixtures/<name> (holds traps.json)")
    p.add_argument("--repo", required=True, help="the fixture run's final repository")
    p.add_argument("--kit-version", required=True)
    p.add_argument("--criteria", help="c1=pass,c2=pass,c3=pass (the runner's ENR-14 results)")
    p.add_argument("--out", required=True)
    p.add_argument("--summary-md", dest="summary_md_sub")
    p = sub.add_parser("combine", help="one kit version's results into one file")
    p.add_argument("results", nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--summary-md", dest="summary_md_sub")
    p = sub.add_parser("compare", help="candidate against the last accepted baseline")
    p.add_argument("--baseline", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--summary-md", dest="summary_md_sub")
    args = parser.parse_args(argv)
    try:
        code, lines = {"score": score, "combine": combine, "compare": compare}[args.command](args)
    except InputError as error:
        print(f"::error::{error}")
        return 2
    print("\n".join(lines))
    summary = "\n".join(["## ABSD benchmark", ""] + [f"- {re.sub(r'^::[a-z]+::', '', line)}" for line in lines]) + "\n"
    for target in filter(None, (getattr(args, "summary_md_sub", None) or args.summary_md,
                                os.environ.get("GITHUB_STEP_SUMMARY"))):
        with open(target, "a" if target == os.environ.get("GITHUB_STEP_SUMMARY") else "w", encoding="utf-8") as f:
            f.write(summary)
    return code


if __name__ == "__main__":
    sys.exit(main())
