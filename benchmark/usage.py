#!/usr/bin/env python3
"""Record each benchmark invocation's platform-reported usage into the fixture's telemetry (ABSD playbook PIPE-8).

The dispatching harness (benchmark/runner/pipeline.workflow.js) labels every agent it starts
`<fixture>|<cycle>|<agent>|<step>|<level>|<model>|<n>`. After the run, this tool reads the workflow's journal
(label → agent id) and each agent's transcript (the usage the platform reported on every model response), and
records one `invocation` event per agent with `absd/tooling/metrics.py record` into
`<repo>/absd-project/metrics/<cycle>.json` — the validated writer, never a hand edit. Owner answers (agent `owner`) are
not pipeline invocations and are skipped.

tokens = input + cache creation + cache read + output tokens, summed over the agent's responses (what the platform
reported, never estimated). duration_s = last minus first transcript timestamp. result = halt / blocked when the
worker's reply says HALTED / BLOCKED, else done.

usage:
  usage.py --run-dir <workflow transcript dir> --repo tally=/path/to/tally --repo shelf=/path/... [--dry-run]

Exit code: 0 recorded, 1 an invocation could not be recorded, 2 usage error. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
METRICS = os.path.join(os.path.dirname(HERE), "absd", "tooling", "metrics.py")
LABEL = re.compile(r"^(?P<fixture>[a-z0-9-]+)\|(?P<cycle>C\d{3})\|(?P<agent>[a-z]+)\|(?P<step>[a-z-]+)\|"
                   r"(?P<level>strongest|balanced|fast)\|(?P<model>[A-Za-z0-9._:/-]+)\|(?P<n>[\d.]+)$")


def stamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def agent_usage(path: str) -> tuple[int, int, str]:
    tokens, times, first = 0, [], ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("timestamp"):
                times.append(stamp(entry["timestamp"]))
            usage = (entry.get("message") or {}).get("usage") if isinstance(entry.get("message"), dict) else None
            if entry.get("type") == "assistant" and usage:
                tokens += sum(int(usage.get(k) or 0) for k in
                              ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"))
                if not first and entry.get("timestamp"):
                    first = entry["timestamp"]
    duration = int((max(times) - min(times)).total_seconds()) if len(times) > 1 else 0
    start = min(times).strftime("%Y-%m-%dT%H:%M:%SZ") if times else ""
    return tokens, duration, start


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--repo", action="append", required=True, metavar="FIXTURE=PATH")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    repos = {}
    for item in args.repo:
        name, sep, path = item.partition("=")
        if not sep or not os.path.isdir(path):
            print(f"::error::--repo {item!r}: use fixture=/existing/path")
            return 2
        repos[name] = path
    journal = os.path.join(args.run_dir, "journal.jsonl")
    if not os.path.isfile(journal):
        print(f"::error::{journal} not found")
        return 2
    started, results = {}, {}
    with open(journal, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("type") == "started":
                started[entry["agentId"]] = entry.get("label", "")
            elif entry.get("type") == "result":
                results[entry["agentId"]] = entry.get("result")
    rows, failed = [], 0
    for agent_id, label in started.items():
        m = LABEL.match(label)
        if not m or m["agent"] == "owner" or m["fixture"] not in repos:
            continue
        transcript = os.path.join(args.run_dir, f"agent-{agent_id}.jsonl")
        if not os.path.isfile(transcript):
            print(f"::warning::{label}: no transcript — recorded without tokens")
            tokens, duration, start = None, 0, ""
        else:
            tokens, duration, start = agent_usage(transcript)
        reply = results.get(agent_id)
        text = reply if isinstance(reply, str) else json.dumps(reply or "")
        result = "halt" if re.search(r"\bHALTED\b", text) else "blocked" if re.search(r"\bBLOCKED\b", text) else \
            "done" if reply is not None else "interrupted"
        event = {"kind": "invocation", "agent": m["agent"], "step": m["step"], "level": m["level"], "model": m["model"],
                 "duration_s": duration, "result": result}
        if tokens:
            event["tokens"] = tokens
        rows.append((start, m["fixture"], m["cycle"], event))
    for start, fixture, cycle, event in sorted(rows, key=lambda r: r[0]):
        path = os.path.join(repos[fixture], "absd-project", "metrics", f"{cycle}.json")
        cmd = [sys.executable, "-B", METRICS, "record", "--file", path, "--cycle", cycle,
               "--context", os.path.join(repos[fixture], "absd-project", "context.md"), "--event", json.dumps(event)]
        if start:
            cmd += ["--at", start]
        if args.dry_run:
            print(" ".join(cmd))
            continue
        done = subprocess.run(cmd, capture_output=True, text=True)
        if done.returncode != 0:
            failed += 1
            print(f"::error::{fixture} {cycle} {event['agent']}·{event['step']}: {done.stdout.strip()} {done.stderr.strip()}")
    known = sum(1 for *_, e in rows if "tokens" in e)
    print(f"{len(rows)} invocations, tokens known for {known}; {failed} not recorded")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
