"""Tests for score.py: the shipped trap detectors in both directions, scoring, combining and comparing."""
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
import score  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
NAMES = ("tally", "shelf", "ledger", "studio")
TRAP_COUNTS = {"tally": 3, "shelf": 4, "ledger": 3, "studio": 7}

# Per trap: artifact lines that deal with the issue (each must be caught on its own) and lines from a fixture that
# never discussed it (none may be caught). Each sample goes into the named artifact of a fresh repo.
SAMPLES = {
    "TRAP-TALLY-1": ("test_plan.md", [
        "| TC-0007 | File saved with CRLF line ends parses like the LF file |",
        "| TC-0008 | A UTF-8 byte-order mark before the first line is ignored |",
        "- A-3: input may use Windows line endings (\\r\\n); they are stripped before parsing",
        "| TC-0009 | first line starts with a BOM (Notepad) → same totals |",
    ], [
        "| TC-0003 | A line with three decimals is rejected; the error names the file and line |",
        "| TC-0004 | Windows users run the same wheel; the trailing newline at the end of file is optional |",
        "| TC-0005 | Blank lines and # comments are skipped |",
    ]),
    "TRAP-TALLY-2": ("analysis.md", [
        "| question | OQ-1 | Which spelling of a category is shown when the input mixes 'Groceries' and 'groceries'? |",
        "| assumption | A-2 | A category is displayed as first seen in the input |",
        "- D-1: categories are matched case-insensitively and printed in lower case; the table shows `groceries`",
        "| TALLY-3 | Categories are normalised to title case for output (rows show 'Groceries') |",
    ], [
        "| TALLY-3 | Categories are compared case-insensitively ('Groceries' = 'groceries') |",
        "| TALLY-4 | Category keys are lower-cased; totals are printed per category and month |",
        "| TALLY-1 | One row per month and category with its total, sorted by month then category |",
    ]),
    "TRAP-TALLY-3": ("analysis.md", [
        "| question | OQ-2 | PARSE says amounts are positive, but refunds are written as negative amounts: which wins? |",
        "- Conflict: the input rule requires a positive amount while refunds (-5.00) are negative.",
        "| TALLY-5 | Refunds are negative amounts and reduce the total; this amends the PARSE positive-amount rule |",
        "- Are negative amounts (refunds) valid input?",
    ], [
        "| TALLY-5 | Refunds are written as negative amounts and reduce the category total | brief |",
        "| PARSE-2 | The amount is a positive number with exactly two decimals | brief |",
        "| PARSE-3 | A line that does not fit is an error naming the file and line | brief |",
    ]),
    "TRAP-SHELF-1": ("test_plan.md", [
        "| TC-0021 | Sign up with username `__proto__` or `constructor` → a normal account, no other shelf touched |",
        "| TC-0022 | Username `<script>alert(1)</script>` is shown as text on the admin page (XSS) |",
        "| TC-0023 | Abuse case: usernames with zero-width or right-to-left characters cannot impersonate another |",
        "| TC-0024 | Username '../../etc' cannot escape the store directory (path traversal) |",
    ], [
        "| TC-0003 | Sign in with a wrong username or password shows one message that does not say which |",
        "| TC-0004 | Usernames are unique: a second sign-up with the same username is refused |",
        "| TC-0005 | Book title with <b>bold</b> markup shows as text |",
        "- The UserStore constructor takes the store path; username lookups are O(1).",
    ]),
    "TRAP-SHELF-2": ("test_plan.md", [
        "| TC-0031 | Mark read at 00:30 Athens time (22:30 UTC the day before) → date read defaults to the Athens date |",
        "| TC-0032 | Date read near midnight in Europe/Athens is stored and shown as the Athens day, not UTC |",
        "| TC-0033 | Browser in another time zone (America/New_York) marks a book read → today is the Athens date |",
    ], [
        "| TC-0010 | Mark a book read on 3 Nov → shelf shows 'Read on 3 November 2026' |",
        "| TC-0011 | Date read defaults to today; the member can change it |",
        "| TC-0012 | A session expires after 8 hours (UTC clock) even across midnight |",
    ]),
    "TRAP-SHELF-3": ("analysis.md", [
        "| question | OQ-3 | May an admin edit or remove books on another member's shelf, or only view it? |",
        "| assumption | A-4 | Admins see every member's shelf read-only; they cannot change other members' books |",
        "- D-2: an admin may not modify a member's shelf other than their own.",
    ], [
        "| SHELF-6 | An admin sees every member's shelf from the members page |",
        "| SHELF-7 | An admin is also a member and adds or removes books on their own shelf |",
        "| SHELF-2 | A member removes a book from their own shelf |",
    ]),
    "TRAP-LEDGER-1": ("test_plan.md", [
        "| TC-0041 | DST start (2026-03-29) is a 23-hour Athens day: orders split at the local midnight |",
        "| TC-0042 | The day the clocks go back (25 hours) gets every order of its 25 hours |",
        "| TC-0043 | Orders across the daylight-saving change are assigned to the right Athens day |",
        "| TC-0044 | Summer time ends: +03:00 to +02:00 offset change within one day |",
    ], [
        "| TC-0004 | Order at 2026-10-03T23:30:00+03:00 belongs to 2026-10-03 |",
        "| TC-0005 | Order at 2026-10-03T21:30:00Z belongs to the Athens date 2026-10-04 |",
        "| TC-0006 | A day with no orders gets a row of zeros |",
    ]),
    "TRAP-LEDGER-2": ("analysis.md", [
        "| question | OQ-4 | When the same order_id appears twice (a re-sent export), is it counted once? |",
        "| SUM-6 | Duplicate orders (same order_id) are counted once; the first occurrence wins |",
        "- D-3: an order_id seen more than once goes to the rejects file from its second row on.",
    ], [
        "| SUM-1 | Re-running on the same input twice gives byte-identical output (idempotent) |",
        "| INP-3 | Each order row has order_id, placed_at, customer_id, amount_eur, status |",
        "| INP-4 | The shop may send the export again; both sends end up in one night's file, so orders appear twice |",
    ]),
    "TRAP-LEDGER-3": ("analysis.md", [
        "| question | OQ-5 | What happens to an order whose status is not one of paid, refunded, cancelled? |",
        "| REJ-3 | A row with an unknown status goes to the rejects file with reason 'unknown status' |",
        "| TC-0051 | status 'pending' → rejected, line number and reason in the rejects file |",
    ], [
        "| SUM-2 | paid adds to revenue; refunded counts in refunds; cancelled is left out (status column) |",
        "| REJ-1 | A malformed row goes to the rejects file with its line number and reason |",
        "| SUM-3 | Net = revenue − refunds per Athens day |",
    ]),
    "TRAP-SHELF-4": ("design-system.md", [
        "| Palette | cream background, serif headings, terracotta accent (the generic 'bookish' default) | deep ink blue on cool paper grey | brief says calm and warm, not old |",
        "- We avoid the expected parchment-and-serif library look; the signature is the reading-date ribbon.",
        "| Type | a classic serif for everything (the obvious bookish choice) | a humanist sans for UI, one serif for titles | rather than nostalgia |",
    ], [
        "- Personality in three words: calm, warm, readable",
        "| color.bg / surface / raised | #F6F1E7 | page background | 14.2:1 |",
        "| type.title | serif 24/32 | headings | |",
    ]),
    "TRAP-STUDIO-1": ("analysis.md", [
        "| question | OQ-2 | Which PayCo events besides a successful payment must we handle (expired checkout, refund, dispute)? |",
        "| PAY-4 | A checkout the member abandons expires after 24 h and leaves no pass |",
        "| EXT-PAYCO-3 | A refunded payment removes the unused classes of its pass | UNVERIFIED |",
        "- A failed card payment on PayCo's page returns the member to the pass list with a message.",
    ], [
        "| PAY-1 | A member pays for a pass on PayCo's hosted page; we never see card numbers |",
        "| PAY-2 | When PayCo reports the payment went through, the pass appears on the account |",
        "| BOOK-3 | Cancelling up to 6 hours before the class gives the class back |",
    ]),
    "TRAP-STUDIO-2": ("design.md", [
        "| SCR-2 | Member home: bookings, classes left and a 'Buy a pass' button — the entry point to purchase |",
        "- UJ-3 starts at the member home screen; the bottom tab bar has Timetable, Passes (buy) and Account.",
        "| TC-0061 | From the member's home, navigate to buy a 10-class pass and pay (reachability journey) |",
    ], [
        "| SCR-4 | Pass purchase page: 10-class and 5-class passes with prices |",
        "| SCR-2 | Member home: upcoming bookings and classes left |",
        "| UJ-3 | A member chooses a pass, pays on PayCo's page and returns |",
    ]),
    "TRAP-STUDIO-3": ("test_plan.md", [
        "| TC-0071 | The same PayCo payment notification delivered twice → exactly one pass |",
        "| PAY-6 | Fulfilment is idempotent: a payment id seen before adds no second pass |",
        "- PayCo retries a notification until we answer 2xx; a replayed event is ignored.",
    ], [
        "| TC-0010 | Booking a class takes one class off the pass |",
        "| TC-0011 | A member with no classes left cannot book |",
        "| TC-0012 | Runner retries are 0 for unit tests |",
    ]),
    "TRAP-STUDIO-4": ("test_report.md", [
        "- Status: payments are built and verified against the fake only; PayCo behaviour is UNVERIFIED, so payments ship with the flag off.",
        "| RISK-3 | PayCo live payments not verified from this machine; online sales stay disabled until a live check |",
        "- Members cannot yet pay: checkout fails closed until the provider facts are verified.",
    ], [
        "| PAY-1 | A member pays for a pass on PayCo's hosted page |",
        "- Verify: 75/75 TCs pass at the product SHA; coverage 96 %.",
        "| TC-0020 | Checkout page lists both passes with their prices |",
    ]),
    "TRAP-STUDIO-5": ("architecture.md", [
        "| POST /api/v1/payco/notifications | verifies the PayCo signature (HMAC-SHA256 with the shared secret) before reading the body |",
        "| TC-0081 | A forged webhook without a valid signature is rejected with 401 and adds no pass |",
        "- Threat: anyone can call the notification endpoint; spoofed events are refused.",
    ], [
        "| POST /api/v1/payco/notifications | PayCo calls it after a payment |",
        "| POST /api/v1/sessions | sign-in with email and password (hashed) |",
        "- Sessions expire after 12 hours.",
    ]),
    "TRAP-STUDIO-6": ("test_plan.md", [
        "| TC-0091 | Pass bought 30 November 2026 is valid until 28 February 2027 (shorter month, clamped) |",
        "| TC-0092 | Pass bought on 31 August is valid until 30 November: month-end clamp |",
        "| TC-0093 | Validity ends at midnight Athens time, not UTC |",
    ], [
        "| TC-0005 | A pass is valid for three months from the day it is bought |",
        "| TC-0006 | A 10-class pass costs 120 euros |",
        "| TC-0007 | A pass is used up one class at a time |",
    ]),
    "TRAP-STUDIO-7": ("analysis.md", [
        "| EXT-PAYCO-5 | The PayCo API version and the subscribed event types are set in the PayCo dashboard | UNVERIFIED |",
        "| RISK-4 | The webhook endpoint registration on the PayCo account must be checked before launch |",
        "- Live keys must have only the permissions the checkout needs (restricted keys).",
    ], [
        "| EXT-PAYCO-1 | PayCo hosts the payment page | owner statement |",
        "| PAY-3 | The admin sees every pass sold with member, amount and date |",
        "- PayCo's monthly statement lists every payment.",
    ]),
}

# Per trap with depth levels: a TC row that plans it and a test-code line that exercises it.
LEVEL_SAMPLES = {
    "TRAP-TALLY-1": ("| TC-0007 | CRLF line ends parse like LF |", "content = 'a\\r\\nb'"),
    "TRAP-SHELF-2": ("| TC-0031 | Mark read at 00:30 Athens time (22:30 UTC the day before) → date read is the Athens date |", "const zone = 'Europe/Athens'"),
    "TRAP-STUDIO-3": ("| TC-0071 | The same notification delivered twice → one pass |",
                      "test('duplicate webhook event adds one pass', async () => {"),
    "TRAP-STUDIO-6": ("| TC-0091 | Pass bought 30 November is valid until 28 February (clamped) |",
                      "assert.equal(validUntil('2026-11-30'), '2027-02-28')"),
}


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def all_traps() -> dict:
    return {t["id"]: t for name in NAMES for t in score.load_traps(os.path.join(FIXTURES, name))}


def run(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    env = os.environ.pop("GITHUB_STEP_SUMMARY", None)
    try:
        with contextlib.redirect_stdout(out):
            code = score.main(argv)
    finally:
        if env is not None:
            os.environ["GITHUB_STEP_SUMMARY"] = env
    return code, out.getvalue()


def telemetry(cycle: str = "C001", gates=(("G1", "PASS"),), halts=(), tokens=(100,), controls=((True, True),)) -> dict:
    events = []
    for agent_tokens in tokens:
        event = {"kind": "invocation", "agent": "analyst", "step": "analysis", "level": "strongest", "model": "m-1",
                 "duration_s": 60, "result": "done"}
        if agent_tokens is not None:
            event["tokens"] = agent_tokens
        events.append(event)
    rounds: dict = {}
    for gate, verdict in gates:
        rounds[gate] = rounds.get(gate, 0) + 1
        events.append({"kind": "gate", "gate": gate, "round": rounds[gate], "verdict": verdict,
                       "findings": {"critical": 0, "major": 0, "minor": 0}, "rules": []})
    events += [{"kind": "halt", "agent": "builder", "cause": cause} for cause in halts]
    events += [{"kind": "control", "control": f"NC-{n}", "red": red, "green": green}
               for n, (red, green) in enumerate(controls, 1)]
    for seq, event in enumerate(events, 1):
        event.update(seq=seq, at="2026-11-11T10:00:00Z")
    return {"schema": 1, "cycle": cycle, "kit": "2.4.0", "mode": "F", "events": events}


class ShippedTraps(unittest.TestCase):
    def test_every_fixture_has_its_valid_traps_and_a_brief_with_a_feature(self):
        self.assertEqual(sorted(NAMES), sorted(n for n in os.listdir(FIXTURES) if not n.startswith(".")))
        for name in NAMES:
            traps = score.load_traps(os.path.join(FIXTURES, name))
            self.assertEqual(len(traps), TRAP_COUNTS[name], name)
            self.assertTrue(all(t["id"].startswith(f"TRAP-{name.upper()}-") for t in traps))
            with open(os.path.join(FIXTURES, name, "brief.md"), encoding="utf-8") as f:
                brief = f.read()
            self.assertIn("## Feature for the first feature cycle", brief)
            self.assertNotIn("trap", brief.lower())

    def test_every_trap_has_samples(self):
        self.assertEqual(set(SAMPLES), set(all_traps()))

    def test_detectors_catch_each_phrasing_and_ignore_unrelated_text(self):
        traps = all_traps()
        for trap_id, (artifact, positives, negatives) in SAMPLES.items():
            trap = traps[trap_id]
            for expected, lines in ((True, positives), (False, negatives)):
                for text in lines:
                    with self.subTest(trap=trap_id, caught=expected, text=text), tempfile.TemporaryDirectory() as repo:
                        write(os.path.join(repo, "absd-project/archive/001_2026-11-11_feature", artifact),
                              f"# Artifact\n\nIntro line.\n{text}\nLast line.\n")
                        self.assertEqual(score.detect_trap(trap, repo)["caught"], expected)

    def test_negatives_together_catch_nothing(self):
        traps = all_traps()
        for trap_id, (artifact, _, negatives) in SAMPLES.items():
            with self.subTest(trap=trap_id), tempfile.TemporaryDirectory() as repo:
                write(os.path.join(repo, "absd-project/working", artifact), "\n".join(negatives) + "\n")
                self.assertFalse(score.detect_trap(traps[trap_id], repo)["caught"])

    def test_the_brief_copied_into_every_artifact_catches_no_trap(self):
        # An analysis that only restates the owner's words has not dealt with any trap.
        for name in NAMES:
            with open(os.path.join(FIXTURES, name, "brief.md"), encoding="utf-8") as f:
                brief = f.read()
            with tempfile.TemporaryDirectory() as repo:
                for artifact in ("analysis.md", "test_plan.md", "design.md", "architecture.md", "context.md", "cycle.md",
                                 "test_report.md", "audit.md", "brd.md"):
                    write(os.path.join(repo, "absd-project/working", artifact), brief)
                for path in ("absd-project/catalogue.md", "absd-project/context.md", "absd-project/design-system.md",
                             "docs/testing/EXTERNAL-FACTS.md"):
                    write(os.path.join(repo, path), brief)
                for trap in score.load_traps(os.path.join(FIXTURES, name)):
                    with self.subTest(trap=trap["id"]):
                        self.assertFalse(score.detect_trap(trap, repo)["caught"])

    def test_depth_counts_planned_and_tested_levels_only_after_raised(self):
        traps = all_traps()
        for trap_id, (planned, tested) in LEVEL_SAMPLES.items():
            trap = traps[trap_id]
            with self.subTest(trap=trap_id), tempfile.TemporaryDirectory() as repo:
                write(os.path.join(repo, "tests/unit/a.test.js"), tested + "\n")
                self.assertEqual(score.detect_trap(trap, repo)["depth"], 0)   # tests alone: never raised
                write(os.path.join(repo, "absd-project/working/test_plan.md"), planned + "\n")
                result = score.detect_trap(trap, repo)
                self.assertTrue(result["caught"])
                self.assertEqual((result["depth"], result["max_depth"]), (3, 3))
                os.remove(os.path.join(repo, "tests/unit/a.test.js"))
                self.assertEqual(score.detect_trap(trap, repo)["depth"], 2)

    def test_dependency_folders_are_never_read(self):
        trap = all_traps()["TRAP-TALLY-1"]
        with tempfile.TemporaryDirectory() as repo:
            write(os.path.join(repo, "absd-project/working/test_plan.md"), "| TC-0007 | CRLF line ends parse |\n")
            write(os.path.join(repo, "tests/node_modules/x/test.js"), "'\\r\\n'\n")
            self.assertEqual(score.detect_trap(trap, repo)["depth"], 2)

    def test_split_artifacts_and_other_artifact_files_are_read(self):
        trap = all_traps()["TRAP-LEDGER-1"]
        with tempfile.TemporaryDirectory() as repo:
            write(os.path.join(repo, "absd-project/working/test_plan/02-days.md"), "| TC-0041 | 23-hour DST day |\n")
            result = score.detect_trap(trap, repo)
            self.assertTrue(result["caught"])
            self.assertEqual(result["matches"][0]["file"], "absd-project/working/test_plan/02-days.md")
            self.assertEqual(result["matches"][0]["line"], 1)
        with tempfile.TemporaryDirectory() as repo:   # the right words in a file no detector reads do not count
            write(os.path.join(repo, "absd-project/working/build_log.md"), "| TC-0041 | 23-hour DST day |\n")
            write(os.path.join(repo, "src/test_days.py"), "# DST 23-hour day\n")
            self.assertFalse(score.detect_trap(trap, repo)["caught"])


class TrapsFile(unittest.TestCase):
    def check_refused(self, traps, message):
        with tempfile.TemporaryDirectory() as fixture:
            write(os.path.join(fixture, "traps.json"), json.dumps(traps))
            with self.assertRaisesRegex(score.InputError, message):
                score.load_traps(fixture)

    def test_bad_traps_files_are_refused(self):
        good = {"id": "TRAP-X-1", "kind": "time", "summary": "s", "detect": [{"glob": "a.md", "regex": "x"}],
                "min_matches": 1}
        self.check_refused([], "non-empty")
        self.check_refused([dict(good, id="X-1")], "id")
        self.check_refused([good, dict(good)], "id")
        self.check_refused([dict(good, kind="other")], "kind")
        self.check_refused([dict(good, detect=[{"glob": "a.md", "regex": "("}])], "bad regex")
        self.check_refused([dict(good, detect=[{"glob": "a.md"}])], "detector")
        self.check_refused([dict(good, min_matches=2)], "min_matches")
        self.check_refused([dict(good, extra=1)], "object")

    def test_min_matches_counts_detectors(self):
        trap = {"id": "TRAP-X-1", "kind": "time", "summary": "s", "min_matches": 2,
                "detect": [{"glob": "absd-project/**/analysis.md", "regex": "dst"},
                           {"glob": "absd-project/**/test_plan.md", "regex": "dst"}]}
        with tempfile.TemporaryDirectory() as fixture, tempfile.TemporaryDirectory() as repo:
            write(os.path.join(fixture, "traps.json"), json.dumps([trap]))
            loaded = score.load_traps(fixture)[0]
            write(os.path.join(repo, "absd-project/working/analysis.md"), "DST\n")
            self.assertFalse(score.detect_trap(loaded, repo)["caught"])
            write(os.path.join(repo, "absd-project/working/test_plan.md"), "dst\n")
            self.assertTrue(score.detect_trap(loaded, repo)["caught"])


class Score(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "repo")
        self.out = os.path.join(self.tmp.name, "result.json")
        write(os.path.join(self.repo, "absd-project/archive/001_2026-11-11_totals/test_plan.md"),
              "| TC-0007 | CRLF line ends parse |\n")

    def tearDown(self):
        self.tmp.cleanup()

    def metrics(self, doc, name="C001.json"):
        write(os.path.join(self.repo, "absd-project/metrics", name), json.dumps(doc))

    def score(self, *extra):
        return run(["score", "--fixture", os.path.join(FIXTURES, "tally"), "--repo", self.repo,
                    "--kit-version", "2.4.0", "--out", self.out, *extra])

    def test_scores_traps_gates_halts_controls_and_cost(self):
        self.metrics(telemetry(gates=(("G1", "PASS"), ("G2R", "FAIL"), ("G2R", "PASS"), ("G3", "PASS")),
                               halts=("kit-gap", "spec-gap"), tokens=(100, None, 50),
                               controls=((True, True), (True, False))))
        self.metrics(telemetry(cycle="C002", gates=(("G1", "FAIL"), ("G1", "PASS"))), "C002.json")
        code, out = self.score("--criteria", "c1=pass,c2=fail,c3=pass")
        self.assertEqual(code, 0, out)
        with open(self.out, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["fixture"], "tally")
        self.assertEqual((result["traps"]["caught"], result["traps"]["total"]), (1, 3))
        self.assertEqual([t["id"] for t in result["traps"]["list"] if t["caught"]], ["TRAP-TALLY-1"])
        self.assertEqual(result["cycles"], ["C001", "C002"])
        gates = result["gates"]
        self.assertEqual((gates["total"], gates["first_pass"], gates["fail_rounds"]), (4, 2, 2))
        self.assertEqual(gates["first_pass_rate"], 50.0)
        self.assertEqual(result["halts"], {"total": 2, "kit_gap": 1, "by_cause": {"kit-gap": 1, "spec-gap": 1}})
        self.assertEqual(result["controls"], {"total": 3, "ok": 2})
        self.assertEqual(result["cost"], {"invocations": 4, "duration_s": 240, "tokens": 250, "tokens_unknown": 1,
                                          "token_coverage": 75.0})
        self.assertEqual(result["criteria"], {"c1": "pass", "c2": "fail", "c3": "pass"})
        self.assertIn("1/3 traps caught", out)

    def test_missing_or_empty_metrics_is_red(self):
        code, out = self.score()
        self.assertEqual(code, 1)
        self.assertIn("no telemetry", out)
        os.makedirs(os.path.join(self.repo, "absd-project/metrics"))
        self.assertEqual(self.score()[0], 1)
        self.assertFalse(os.path.exists(self.out))

    def test_invalid_metrics_is_red(self):
        doc = telemetry()
        doc["events"][0]["prompt"] = "free text"
        self.metrics(doc)
        code, out = self.score()
        self.assertEqual(code, 1)
        self.assertIn("invalid telemetry", out)

    def test_usage_errors(self):
        self.metrics(telemetry())
        self.assertEqual(self.score("--criteria", "c4=pass")[0], 2)
        self.assertEqual(self.score("--criteria", "c1=maybe")[0], 2)
        self.assertEqual(run(["score", "--fixture", self.tmp.name, "--repo", self.repo, "--kit-version", "2.4.0",
                              "--out", self.out])[0], 2)      # no traps.json
        self.assertEqual(run(["score", "--fixture", os.path.join(FIXTURES, "tally"), "--repo", self.repo,
                              "--kit-version", "2.4", "--out", self.out])[0], 2)

    def test_summary_markdown(self):
        self.metrics(telemetry())
        summary = os.path.join(self.tmp.name, "summary.md")
        self.assertEqual(self.score("--summary-md", summary)[0], 0)
        with open(summary, encoding="utf-8") as f:
            self.assertIn("## ABSD benchmark", f.read())


def result(fixture: str, caught=(True, True, False), first_pass=(1, 2), kit_gap=0, tokens=1000, duration=600,
           criteria=None, kit="2.4.0", unknown=0) -> dict:
    ids = [f"TRAP-{fixture.upper()}-{n}" for n in range(1, len(caught) + 1)]
    return {"schema": 1, "fixture": fixture, "kit": kit,
            "traps": {"total": len(caught), "caught": sum(caught),
                      "list": [{"id": i, "kind": "time", "summary": "s", "caught": c, "matches": []}
                               for i, c in zip(ids, caught)]},
            "cycles": ["C001"],
            "gates": {"total": first_pass[1], "first_pass": first_pass[0],
                      "first_pass_rate": score.rate(*first_pass), "fail_rounds": first_pass[1] - first_pass[0],
                      "list": []},
            "halts": {"total": kit_gap, "kit_gap": kit_gap, "by_cause": {"kit-gap": kit_gap} if kit_gap else {}},
            "controls": {"total": 1, "ok": 1},
            "cost": {"invocations": 5, "duration_s": duration, "tokens": tokens, "tokens_unknown": unknown,
                     "token_coverage": score.rate(5 - unknown, 5)},
            "criteria": criteria or {"c1": "pass", "c2": "pass", "c3": "pass"}}


class CombineCompare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def path(self, name):
        return os.path.join(self.tmp.name, name)

    def combined(self, name, *results):
        paths = []
        for r in results:
            paths.append(self.path(f"{name}-{r['fixture']}.json"))
            score.write_json(paths[-1], r)
        code, out = run(["combine", *paths, "--out", self.path(f"{name}.json")])
        self.assertEqual(code, 0, out)
        return self.path(f"{name}.json")

    def compare(self, baseline, candidate):
        return run(["compare", "--baseline", baseline, "--candidate", candidate])

    def test_combine_totals(self):
        out = self.combined("v", result("tally"), result("shelf", caught=(True, True, True), kit_gap=1))
        with open(out, encoding="utf-8") as f:
            doc = json.load(f)
        self.assertEqual(sorted(doc["fixtures"]), ["shelf", "tally"])
        t = doc["totals"]
        self.assertEqual((t["traps_caught"], t["traps_total"], t["kit_gap_halts"]), (5, 6, 1))
        self.assertEqual((t["gates_first_pass"], t["gates_total"], t["first_pass_rate"]), (2, 4, 50.0))
        self.assertEqual((t["tokens"], t["duration_s"], t["invocations"], t["criteria_not_passing"]), (2000, 1200, 10, 0))

    def test_combine_refuses_mixed_versions_and_duplicates(self):
        a, b = self.path("a.json"), self.path("b.json")
        score.write_json(a, result("tally"))
        score.write_json(b, result("shelf", kit="2.5.0"))
        self.assertEqual(run(["combine", a, b, "--out", self.path("x.json")])[0], 2)
        self.assertEqual(run(["combine", a, a, "--out", self.path("x.json")])[0], 2)

    def test_missing_baseline_is_a_notice(self):
        cand = self.combined("new", result("tally"))
        code, out = self.compare(self.path("none.json"), cand)
        self.assertEqual(code, 0)
        self.assertIn("first baseline", out)

    def test_equal_or_better_passes(self):
        base = self.combined("old", result("tally"))
        cand = self.combined("new", result("tally", caught=(True, True, True), first_pass=(2, 2)))
        code, out = self.compare(base, cand)
        self.assertEqual(code, 0, out)
        self.assertIn("no regression", out)

    def test_regressions(self):
        base = self.combined("old", result("tally"), result("shelf"))
        cases = {
            "missed": ([result("tally", caught=(False, True, True)), result("shelf")], "TRAP-TALLY-1 was caught"),
            "fewer": ([result("tally", caught=(True, False, False)), result("shelf")], "traps caught 3 < 4"),
            "fixture": ([result("tally")], "fixture shelf has no result"),
            "kit-gap": ([result("tally", kit_gap=1), result("shelf")], "kit-gap halts 1 > 0"),
            "criterion": ([result("tally", criteria={"c1": "pass", "c2": "fail", "c3": "pass"}), result("shelf")],
                          "criterion c2 is fail"),
            "unreported": ([result("tally", criteria={"c1": "pass", "c2": "pass", "c3": None}), result("shelf")],
                           "criterion c3 is not reported"),
            "first-pass": ([result("tally", first_pass=(1, 3)), result("shelf", first_pass=(1, 3))],
                           "more than 10 points"),
            "tokens": ([result("tally", unknown=2), result("shelf")], "tokens known for 80.0% "),
        }
        for name, (results, message) in cases.items():
            with self.subTest(name):
                code, out = self.compare(base, self.combined(name, *results))
                self.assertEqual(code, 1, out)
                self.assertIn(message, out)
                self.assertIn("REGRESSION", out)

    def test_first_pass_drop_of_ten_points_or_less_is_fine(self):
        base = self.combined("old", result("tally", first_pass=(6, 10)))
        cand = self.combined("new", result("tally", first_pass=(5, 10)))
        self.assertEqual(self.compare(base, cand)[0], 0)

    def test_cost_growth_is_a_warning(self):
        base = self.combined("old", result("tally"))
        cand = self.combined("new", result("tally", tokens=1300, duration=700))
        code, out = self.compare(base, cand)
        self.assertEqual(code, 0, out)
        self.assertIn("::warning::tokens grew 30 %", out)
        self.assertNotIn("duration grew", out)

    def test_compare_needs_combined_results(self):
        single = self.path("single.json")
        score.write_json(single, result("tally"))
        self.assertEqual(self.compare(single, single)[0], 2)


if __name__ == "__main__":
    unittest.main()
