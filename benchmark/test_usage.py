"""Tests for usage.py: platform-reported usage from a workflow run recorded as invocation events."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import usage  # noqa: E402


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def transcript(*responses):
    lines = []
    for at, u in responses:
        lines.append(json.dumps({"type": "assistant", "timestamp": at, "message": {"usage": u}}))
    return "\n".join(lines) + "\n"


class Usage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = os.path.join(self.tmp.name, "run")
        self.repo = os.path.join(self.tmp.name, "studio")
        os.makedirs(os.path.join(self.repo, "absd-project"))

    def tearDown(self):
        self.tmp.cleanup()

    def journal(self, *entries):
        write(os.path.join(self.run_dir, "journal.jsonl"), "\n".join(json.dumps(e) for e in entries) + "\n")

    def run_tool(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = usage.main(["--run-dir", self.run_dir, "--repo", f"studio={self.repo}", *extra])
        return code, out.getvalue()

    def test_records_tokens_duration_and_result_per_agent_and_skips_the_owner(self):
        self.journal({"type": "started", "agentId": "a1", "label": "studio|C001|manager|other|strongest|fable|1"},
                     {"type": "result", "agentId": "a1", "result": {"action": "delegate"}},
                     {"type": "started", "agentId": "a2", "label": "studio|C001|builder|build|balanced|sonnet|2.1"},
                     {"type": "result", "agentId": "a2", "result": "Status: HALTED — CLR-1"},
                     {"type": "started", "agentId": "a3", "label": "studio|C001|owner|other|fast|haiku|3"},
                     {"type": "started", "agentId": "a4", "label": "other|C001|analyst|analysis|strongest|fable|4"})
        u = {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000, "output_tokens": 5}
        write(os.path.join(self.run_dir, "agent-a1.jsonl"),
              transcript(("2026-11-11T10:00:00.000Z", u), ("2026-11-11T10:01:30.000Z", u)))
        write(os.path.join(self.run_dir, "agent-a2.jsonl"), transcript(("2026-11-11T10:02:00.000Z", u)))
        code, out = self.run_tool()
        self.assertEqual(code, 0, out)
        with open(os.path.join(self.repo, "absd-project/metrics/C001.json"), encoding="utf-8") as f:
            doc = json.load(f)
        events = doc["events"]
        self.assertEqual([(e["agent"], e["step"], e["model"], e["result"]) for e in events],
                         [("manager", "other", "fable", "done"), ("builder", "build", "sonnet", "halt")])
        self.assertEqual(events[0]["tokens"], 2230)
        self.assertEqual(events[0]["duration_s"], 90)
        self.assertEqual(events[0]["at"], "2026-11-11T10:00:00Z")
        self.assertIn("2 invocations, tokens known for 2", out)

    def test_a_missing_transcript_is_recorded_without_tokens(self):
        self.journal({"type": "started", "agentId": "a9", "label": "studio|C002|tester|verify|balanced|sonnet|9"})
        code, out = self.run_tool()
        self.assertEqual(code, 0, out)
        with open(os.path.join(self.repo, "absd-project/metrics/C002.json"), encoding="utf-8") as f:
            event = json.load(f)["events"][0]
        self.assertNotIn("tokens", event)
        self.assertEqual(event["result"], "interrupted")

    def test_usage_errors(self):
        self.assertEqual(self.run_tool()[0], 2)   # no journal
        self.journal({"type": "launched"})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(usage.main(["--run-dir", self.run_dir, "--repo", "studio"]), 2)


if __name__ == "__main__":
    unittest.main()
