"""Tests for metrics.py — run: python3 -m unittest discover -s absd/tooling -p 'test_*.py'"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics  # noqa: E402

AT = "2026-11-11T10:00:00Z"
INVOCATION = ["--kind", "invocation", "--set", "agent=architect", "--set", "step=architecture", "--set", "level=strongest",
              "--set", "model=opus", "--set", "duration_s=600", "--set", "tokens=12345", "--set", "result=done"]


class MetricsTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        self.file = os.path.join(self.root, "absd-project", "metrics", "C003.json")
        self.context = os.path.join(self.root, "absd-project", "context.md")
        os.environ.pop("GITHUB_STEP_SUMMARY", None)

    def tearDown(self):
        self.dir.cleanup()

    def write(self, relative, text):
        path = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_tool(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = metrics.main(list(args))
        return code, out.getvalue()

    def record(self, *args, cycle="C003", file=None):
        return self.run_tool("record", "--file", file or self.file, "--cycle", cycle, "--context", self.context,
                             "--at", AT, *args)

    def doc(self, path=None):
        with open(path or self.file, encoding="utf-8") as f:
            return json.load(f)


class RecordTests(MetricsTestCase):
    def test_first_record_creates_the_file_with_seq_and_time(self):
        code, out = self.record("--kit", "2.4.0", "--mode", "F", *INVOCATION)
        self.assertEqual(code, 0, out)
        doc = self.doc()
        self.assertEqual(doc["schema"], 1)
        self.assertEqual((doc["cycle"], doc["kit"], doc["mode"]), ("C003", "2.4.0", "F"))
        self.assertEqual(doc["events"], [{"seq": 1, "at": AT, "kind": "invocation", "agent": "architect",
                                          "step": "architecture", "level": "strongest", "model": "opus",
                                          "duration_s": 600, "tokens": 12345, "result": "done"}])

    def test_events_are_numbered_in_order(self):
        self.record(*INVOCATION)
        code, out = self.record("--kind", "gate", "--set", "gate=G2R", "--set", "round=1", "--set", "verdict=FAIL",
                                "--set", "findings=major:1,minor:2", "--set", "rules=ARCH-3,SEC-7")
        self.assertEqual(code, 0, out)
        events = self.doc()["events"]
        self.assertEqual([e["seq"] for e in events], [1, 2])
        self.assertEqual(events[1]["findings"], {"major": 1, "minor": 2})
        self.assertEqual(events[1]["rules"], ["ARCH-3", "SEC-7"])

    def test_every_kind_from_the_spec_is_accepted_as_json(self):
        events = [
            {"kind": "halt", "agent": "builder", "cause": "blueprint-gap"},
            {"kind": "rework", "from": "G2R", "to": "architect", "cause": "review-fail"},
            {"kind": "control", "control": "NC-3", "red": True, "green": True},
            {"kind": "escape", "defect": "DEF-3", "why": "assumption-fed-fake"},
            {"kind": "resume", "agent": "builder"},
        ]
        for event in events:
            code, out = self.record("--event", json.dumps(event))
            self.assertEqual(code, 0, out)
        self.assertEqual(len(self.doc()["events"]), 5)
        self.assertEqual(metrics.validate_doc(self.doc()), [])

    def test_booleans_from_set(self):
        code, out = self.record("--kind", "control", "--set", "control=NC-1", "--set", "red=true", "--set", "green=false")
        self.assertEqual(code, 0, out)
        self.assertIs(self.doc()["events"][0]["green"], False)

    def test_tokens_are_optional_never_estimated(self):
        code, out = self.record("--event", json.dumps({"kind": "invocation", "agent": "builder", "step": "build",
                                                         "level": "balanced", "model": "sonnet-4", "result": "done"}))
        self.assertEqual(code, 0, out)
        self.assertNotIn("tokens", self.doc()["events"][0])

    def test_free_text_is_refused_and_nothing_written(self):
        code, out = self.record("--kind", "halt", "--set", "agent=builder", "--set", "cause=the blueprint said nothing")
        self.assertEqual(code, 2)
        self.assertIn("nothing recorded", out)
        self.assertNotIn("blueprint said", out)   # refused text is not echoed either
        self.assertFalse(os.path.exists(self.file))

    def test_unknown_key_is_refused(self):
        code, out = self.record("--event", json.dumps({"kind": "resume", "agent": "builder", "note": "x"}))
        self.assertEqual(code, 2)
        self.assertIn("unknown key", out)

    def test_wrong_type_is_refused(self):
        code, _ = self.record("--event", json.dumps({"kind": "control", "control": "NC-1", "red": "yes", "green": True}))
        self.assertEqual(code, 2)
        code, _ = self.record("--event", json.dumps({"kind": "gate", "gate": "G1", "round": True, "verdict": "PASS"}))
        self.assertEqual(code, 2)

    def test_patterns_are_enforced(self):
        cases = [
            {"kind": "invocation", "agent": "builder", "step": "build", "level": "balanced", "model": "my model",
             "result": "done"},
            {"kind": "invocation", "agent": "builder", "step": "build", "level": "medium", "model": "m", "result": "done"},
            {"kind": "invocation", "agent": "coder", "step": "build", "level": "fast", "model": "m", "result": "done"},
            {"kind": "invocation", "agent": "builder", "step": "build", "level": "fast", "model": "m", "result": "done",
             "tokens": -1},
            {"kind": "gate", "gate": "G1", "round": 1, "verdict": "PASS", "rules": ["arch-3"]},
            {"kind": "gate", "gate": "G1", "round": 1, "verdict": "PASS", "findings": {"blocker": 1}},
            {"kind": "gate", "gate": "G9", "round": 1, "verdict": "PASS"},
            {"kind": "escape", "defect": "DEF-3", "why": "Fake_Assumed"},
            {"kind": "escape", "defect": "DEF-3", "why": "a" * 33},
            {"kind": "escape", "defect": "defect three", "why": "x"},
        ]
        for event in cases:
            code, out = self.record("--event", json.dumps(event))
            self.assertEqual(code, 2, (event, out))
        self.assertFalse(os.path.exists(self.file))

    def test_missing_required_key_is_refused(self):
        code, out = self.record("--kind", "gate", "--set", "gate=G1", "--set", "round=1")
        self.assertEqual(code, 2)
        self.assertIn("needs 'verdict'", out)

    def test_bad_cycle_and_at_are_usage_errors(self):
        code, _ = self.record(*INVOCATION, cycle="cycle-3")
        self.assertEqual(code, 2)
        code, _ = self.run_tool("record", "--file", self.file, "--cycle", "C003", "--context", self.context,
                                "--at", "2026-11-11 10:00", *INVOCATION)
        self.assertEqual(code, 2)

    def test_file_of_another_cycle_is_refused(self):
        self.record(*INVOCATION)
        code, out = self.record(*INVOCATION, cycle="C004")
        self.assertEqual(code, 2)
        self.assertIn("belongs to C003", out)
        self.assertEqual(len(self.doc()["events"]), 1)

    def test_corrupt_existing_file_is_not_overwritten(self):
        self.write("absd-project/metrics/C003.json", "{not json")
        code, _ = self.record(*INVOCATION)
        self.assertEqual(code, 2)
        with open(self.file, encoding="utf-8") as f:
            self.assertEqual(f.read(), "{not json")

    def test_kind_and_event_together_is_a_usage_error(self):
        code, _ = self.record("--kind", "resume", "--event", json.dumps({"kind": "resume", "agent": "builder"}))
        self.assertEqual(code, 2)

    def test_default_time_is_utc_now(self):
        code, out = self.run_tool("record", "--file", self.file, "--cycle", "C003", "--context", self.context,
                                  "--kind", "resume", "--set", "agent=tester")
        self.assertEqual(code, 0, out)
        self.assertRegex(self.doc()["events"][0]["at"], metrics.AT)

    def test_no_temp_file_left_behind(self):
        self.record(*INVOCATION)
        self.assertEqual(os.listdir(os.path.dirname(self.file)), ["C003.json"])


class TelemetryOffTests(MetricsTestCase):
    def test_off_in_section_14_is_a_noop(self):
        self.write("absd-project/context.md", "# Project Context\n## 14. Conventions\n- **Telemetry:** OFF\n## 15. Done\n")
        code, out = self.record(*INVOCATION)
        self.assertEqual(code, 0)
        self.assertIn("Telemetry off", out)
        self.assertFalse(os.path.exists(self.file))

    def test_on_or_the_seed_choice_line_records(self):
        for line in ("Telemetry: on", "`Telemetry: on | off` (default on)"):
            self.write("absd-project/context.md", f"## 14. Conventions\n{line}\n")
            self.assertFalse(metrics.telemetry_off(self.context), line)

    def test_off_outside_section_14_does_not_count(self):
        self.write("absd-project/context.md", "## 13. Findings\nTelemetry: off\n## 14. Conventions\nTelemetry: on\n")
        self.assertFalse(metrics.telemetry_off(self.context))

    def test_missing_context_leaves_telemetry_on(self):
        self.assertFalse(metrics.telemetry_off(os.path.join(self.root, "nope.md")))


class LoaderTests(MetricsTestCase):
    def test_load_raises_on_invalid_file(self):
        path = self.write("m/C001.json", json.dumps({"schema": 2, "cycle": "C001", "events": []}))
        with self.assertRaises(ValueError) as caught:
            metrics.load(path)
        self.assertIn("C001.json", str(caught.exception))

    def test_seq_gaps_are_invalid(self):
        doc = {"schema": 1, "cycle": "C001", "events": [{"seq": 2, "at": AT, "kind": "resume", "agent": "builder"}]}
        self.assertTrue(any("seq must be 1" in p for p in metrics.validate_doc(doc)))

    def test_unknown_top_level_key_is_invalid(self):
        doc = {"schema": 1, "cycle": "C001", "events": [], "owner": "someone"}
        self.assertTrue(metrics.validate_doc(doc))

    def test_load_all_reads_sorted_files(self):
        for cycle in ("C002", "C001"):
            self.record("--kind", "resume", "--set", "agent=builder", cycle=cycle,
                        file=os.path.join(self.root, "m", f"{cycle}.json"))
        docs = metrics.load_all([os.path.join(self.root, "m", "*.json")])
        self.assertEqual([d["cycle"] for d in docs], ["C001", "C002"])
        self.assertEqual(metrics.load_all(os.path.join(self.root, "none", "*.json")), [])


class ValidateTests(MetricsTestCase):
    def test_valid_and_invalid_files(self):
        self.record(*INVOCATION)
        code, out = self.run_tool("validate", os.path.join(self.root, "absd-project", "metrics", "*.json"))
        self.assertEqual(code, 0, out)
        self.write("absd-project/metrics/C004.json", json.dumps({"schema": 1, "cycle": "C4", "events": []}))
        code, out = self.run_tool("validate", os.path.join(self.root, "absd-project", "metrics", "*.json"))
        self.assertEqual(code, 1)
        self.assertIn("::error file=", out)

    def test_glob_matching_nothing_is_a_notice(self):
        code, out = self.run_tool("validate", os.path.join(self.root, "nothing", "*.json"))
        self.assertEqual(code, 0)
        self.assertIn("::notice::", out)


PLAYBOOK = """# Topic
**ARCH-1** — Do a thing.
**ARCH-2** — Retired in 2.1.0: superseded by ARCH-3.
**ARCH-3** — Do another thing.
**SEC-7** — Secure it.
**SEC-8** — Never cited.
"""


class ReportTests(MetricsTestCase):
    def cycle(self, cycle, events):
        path = os.path.join(self.root, "absd-project", "metrics", f"{cycle}.json")
        for event in events:
            code, out = self.record("--event", json.dumps(event), cycle=cycle, file=path)
            self.assertEqual(code, 0, out)

    def seed(self):
        self.cycle("C001", [
            {"kind": "invocation", "agent": "architect", "step": "architecture", "level": "strongest", "model": "opus",
             "duration_s": 600, "tokens": 1000, "result": "done"},
            {"kind": "invocation", "agent": "builder", "step": "build", "level": "balanced", "model": "sonnet",
             "duration_s": 300, "result": "halt"},
            {"kind": "halt", "agent": "builder", "cause": "blueprint-gap"},
            {"kind": "gate", "gate": "G2R", "round": 1, "verdict": "FAIL", "findings": {"major": 1, "minor": 2},
             "rules": ["ARCH-3", "SEC-7"]},
            {"kind": "rework", "from": "G2R", "to": "architect", "cause": "review-fail"},
            {"kind": "gate", "gate": "G2R", "round": 2, "verdict": "PASS", "rules": ["ARCH-3"]},
            {"kind": "control", "control": "NC-1", "red": True, "green": True},
            {"kind": "control", "control": "NC-2", "red": False, "green": True},
            {"kind": "escape", "defect": "DEF-3", "why": "assumption-fed-fake"},
        ])
        self.cycle("C002", [
            {"kind": "invocation", "agent": "architect", "step": "architecture", "level": "strongest", "model": "opus",
             "duration_s": 400, "tokens": 500, "result": "done"},
            {"kind": "gate", "gate": "G2R", "round": 1, "verdict": "PASS", "findings": {"critical": 0}},
        ])
        self.write("playbook/engineering/x.md", PLAYBOOK)

    def report(self, *extra):
        out_json = os.path.join(self.root, "report.json")
        code, out = self.run_tool("report", "--metrics", os.path.join(self.root, "absd-project", "metrics", "*.json"),
                                  "--playbook", os.path.join(self.root, "playbook"), "--json", out_json, *extra)
        with open(out_json, encoding="utf-8") as f:
            return code, out, json.load(f)

    def test_totals_per_step_agent_level_model(self):
        self.seed()
        code, out, report = self.report()
        self.assertEqual(code, 0, out)
        architecture = report["by"]["step"]["architecture"]
        self.assertEqual((architecture["invocations"], architecture["duration_s"], architecture["tokens"],
                          architecture["tokens_unknown"]), (2, 1000, 1500, 0))
        self.assertEqual(report["by"]["model"]["sonnet"]["tokens_unknown"], 1)
        self.assertEqual(report["by"]["level"]["balanced"]["invocations"], 1)

    def test_gate_rates_and_findings(self):
        self.seed()
        _, _, report = self.report()
        gate = report["gates"]["G2R"]
        self.assertEqual((gate["rounds"], gate["fail"], gate["instances"], gate["first_pass"]), (3, 1, 2, 1))
        self.assertEqual(gate["first_pass_rate"], 0.5)
        self.assertEqual(report["findings"], {"critical": 0, "major": 1, "minor": 2})

    def test_repass_is_not_a_round_and_blocked_is_a_result(self):
        self.seed()
        self.cycle("C002", [
            {"kind": "gate", "gate": "G2R", "round": 1, "verdict": "PASS", "repass": True},
            {"kind": "invocation", "agent": "tester", "step": "facts", "level": "balanced", "model": "sonnet",
             "result": "blocked"},
        ])
        code, out, report = self.report()
        self.assertEqual(code, 0, out)
        gate = report["gates"]["G2R"]
        self.assertEqual((gate["rounds"], gate["repasses"], gate["first_pass"]), (3, 1, 1))
        self.assertIn("| G2R | 3 | 1 |", out)

    def test_steps_and_causes_the_shelf_benchmark_needed_are_accepted(self):
        self.seed()
        self.cycle("C002", [
            {"kind": "invocation", "agent": "analyst", "step": "catalogue-apply", "level": "balanced", "model": "m",
             "result": "done"},
            {"kind": "invocation", "agent": "designer", "step": "design-system", "level": "strongest", "model": "m",
             "result": "done"},
            {"kind": "invocation", "agent": "builder", "step": "fix", "level": "balanced", "model": "m", "result": "done"},
            {"kind": "rework", "from": "G3", "to": "builder", "cause": "minor-routed"},
            {"kind": "rework", "from": "G1", "to": "analyst", "cause": "user-answer"},
        ])
        code, out, report = self.report()
        self.assertEqual(code, 0, out)
        self.assertEqual(report["rework"]["G3→builder (minor-routed)"], 1)
        self.assertEqual(report["rework"]["G1→analyst (user-answer)"], 1)

    def test_rules_halts_rework_controls_escapes(self):
        self.seed()
        _, out, report = self.report()
        self.assertEqual(report["rules_cited"], {"ARCH-3": 2, "SEC-7": 1})
        self.assertEqual(report["halts"], {"blueprint-gap": 1})
        self.assertEqual(report["rework"], {"G2R→architect (review-fail)": 1})
        self.assertEqual(report["controls"], {"total": 2, "ok": 1, "not_ok": ["C001 NC-2"]})
        self.assertEqual(report["escapes"], {"assumption-fed-fake": 1})
        self.assertIn("### Pipeline telemetry", out)

    def test_never_cited_only_after_enough_cycles_and_skips_tombstones(self):
        self.seed()
        _, out, report = self.report()
        self.assertIsNone(report["never_cited"])
        self.assertIn("listed from 5 cycles on", out)
        _, out, report = self.report("--never-cited-after", "2")
        self.assertEqual(report["never_cited"], ["ARCH-1", "SEC-8"])

    def test_summary_is_appended_to_the_step_summary(self):
        self.seed()
        target = os.path.join(self.root, "step.md")
        self.write("step.md", "earlier\n")
        os.environ["GITHUB_STEP_SUMMARY"] = target
        try:
            self.report()
        finally:
            os.environ.pop("GITHUB_STEP_SUMMARY")
        with open(target, encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.startswith("earlier\n"))
        self.assertIn("| Gate | Rounds |", text)

    def test_no_files_is_exit_1_and_invalid_file_is_exit_2(self):
        code, out = self.run_tool("report", "--metrics", os.path.join(self.root, "none", "*.json"))
        self.assertEqual(code, 1)
        self.assertIn("nothing to report", out)
        self.write("absd-project/metrics/C001.json", "[]")
        code, _ = self.run_tool("report", "--metrics", os.path.join(self.root, "absd-project", "metrics", "*.json"))
        self.assertEqual(code, 2)

    def test_real_playbook_has_rules(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "playbook")
        ids = metrics.playbook_rules(root)
        self.assertIn("ESC-5", ids)
        self.assertTrue(all(metrics.ID.match(i) for i in ids))


class SpecExampleTests(unittest.TestCase):
    def test_example_file_from_the_design_validates_with_rules_6_severities(self):
        doc = {"schema": 1, "cycle": "C003", "kit": "2.4.0", "mode": "F", "events": [
            {"seq": 1, "at": AT, "kind": "invocation", "agent": "architect", "step": "architecture",
             "level": "strongest", "model": "opus", "duration_s": 600, "tokens": 12345, "result": "done"},
            {"seq": 2, "at": AT, "kind": "gate", "gate": "G2R", "round": 1, "verdict": "FAIL",
             "findings": {"critical": 0, "major": 1, "minor": 2}, "rules": ["ARCH-3", "SEC-7"]}]}
        self.assertEqual(metrics.validate_doc(doc), [])


if __name__ == "__main__":
    unittest.main()
