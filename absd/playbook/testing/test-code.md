# Test code — tests that prove what they claim

Code **TCQ**. The quality of the test code itself, at every level and in every profile: never weakening a test,
naming with ids, shape, builders, unique data, determinism and waiting, isolation and parallel safety, fixture
lifetimes, diagnostics, outcome assertions, tested helpers, independence from production code, test-only seams, and
the review checklist. Which cases to write: VAR; expected values: ORACLE; harness: INTEG, E2E; retries, flakes and
static checks on test code: GATE; escaped defects and flakes as defects: ESC.

## Checklist

- [ ] No test skipped, disabled, focused, commented out, weakened or quarantined; one that cannot run is RED (TCQ-1)
- [ ] Each test named as a behaviour sentence; TC id and requirement ids in the name or report properties (TCQ-2)
- [ ] Arrange → act → assert; one behaviour per test; tables for variations; no logic computing expectations (TCQ-3)
- [ ] One builder per input type with valid, neutral defaults; tests state only what matters (TCQ-4)
- [ ] Created names and keys unique per run and attempt; assertions only on the test's own data (TCQ-5)
- [ ] Clock, ids and randomness injected; seeds printed and replayable; no host zone, locale or order reliance (TCQ-6)
- [ ] No sleeps: waits on states, bounded, with a message; fixed time only when time is the subject (TCQ-7)
- [ ] Passes alone, in random order and repeated; resets automatic, never by hand (TCQ-8)
- [ ] Parallel-safe: ephemeral ports, temp dirs, store per worker, no process-global mutation (TCQ-9)
- [ ] Every shared fixture declares scope, ownership and teardown; shared ones read-only or self-resetting (TCQ-10)
- [ ] Failures state rule, expected, actual and context; tables report every failing row; traces kept (TCQ-11)
- [ ] Assert outcomes; interaction checks only at external boundaries or for specified side effects (TCQ-12)
- [ ] Builders, fakes, matchers, readers and scripts with logic have their own tests (TCQ-13)
- [ ] Expected sides, fakes and helpers call no production logic, mapper, parser or constant (TCQ-14)
- [ ] Test-only hooks in production only via TSEAM, unreachable when shipped; no reflection into internals (TCQ-15)
- [ ] Every added or changed test passes the review checklist before hand-off and at audit (TCQ-16)

## Rules

### Integrity

**TCQ-1** — Never skip, disable, weaken, quarantine or comment out a test to get green, and never leave a path through
a test that passes without asserting. Banned: skip or ignore markers (e.g. xUnit `Skip=`, JUnit `@Disabled`,
pytest `mark.skip`, Jest `it.skip`), expected-failure markers, committed focus markers (`.only`, `fit`), an early
return when a dependency or credential is missing, an assertion behind `if (found)`, an assertion deleted, loosened or
wrapped in a catch that ignores it. Lanes select tests by declared category (GATE-1). A test that cannot run is a RED
finding with its reason; a wrong test changes only through its route (ORACLE-2 amendment; flakes as ESC-11).
- *Why:* audits certified suites they had never run (LL-24); a live contract job printed a warning and exited 0 when
  its credential was missing (LL-25).
- *Check:* a test-tree lint fails on skip, ignore, focus and expected-failure markers and on caught assertions; the
  runner fails on zero tests collected; the Auditor reconciles executed = planned, skipped = 0 (XCA-2) and reads every
  test change since T-SHA.
- *Applies when:* always — every level, lane and profile.
- *Provenance:* LL-24, LL-25 (KatenatsioTipster, 2026-10)

### Shape

**TCQ-2** — Name each test as a sentence of behaviour in domain words — subject, condition, outcome, and the wrong
behaviour it rules out when that sharpens it ("exactly at the deadline the entry is locked"; "an empty feed is
reported as unavailable, not as an unknown event") — never `test1`, a method name or "works". Carry its `TC-nnnn` and
the requirement ids it proves in the name or as report properties through the shared linking helper (TRACE-3,
TRACE-5); a regression test adds `(DEF-n, date: what broke)` (ESC-3). Each test file opens with one comment saying
what it proves and how.
- *Why:* a red name must tell the next agent which rule broke without opening the code; a lost id leaves a
  requirement looking untested while the test silently proves it (LL-36).
- *Check:* the traceability report finds every TC id exactly once; lint rejects names without a TC token or matching
  the generic-name list.
- *Applies when:* always.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10)

**TCQ-3** — Shape each test as arrange → act → assert, visibly separated, with one behaviour per test: one act on the
subject, any number of assertions about its one outcome. Variations of one rule go in a parametrized table with a
name per row (e.g. xUnit `[Theory]`, pytest `parametrize`, Jest `test.each`). No branching or computation in a test
body beyond iterating its table; an assertion inside arrange only as a named precondition ("precondition: tied on
profit").
- *Why:* a test that does several things fails for several reasons and pins none; a conditional in a test leaves a
  path that never asserts.
- *Check:* lint flags `if`/`switch` in test bodies and more than one act on the subject; review checklist.
- *Applies when:* always; an end-to-end journey is one behaviour told in named steps (E2E-5).
- *Provenance:* industry baseline

**TCQ-4** — Build inputs with one builder per domain object, request or message type, kept in a shared test-data
module: defaults valid, neutral and far from every boundary, so a test states only the fields its behaviour depends on
(`anOrder().withQuantity(3)`; copy-with-change of a record); domain helpers read like the spec (`paidInFull()`); no
near-duplicate payload literals across files; a builder never fills derived fields by calling production code
(ORACLE-4).
- *Why:* one request payload existed in four drifting shapes and one object had three different builders, so a
  contract change rippled unevenly and some tests kept the old shape.
- *Check:* the Auditor greps for repeated payload literals of one type; builders with logic have tests (TCQ-13).
- *Applies when:* always.
- *Provenance:* industry baseline

**TCQ-5** — Make every created name, key and address unique per run and per attempt (run id plus counter or random
suffix — randomness in names only, never in inputs that decide an outcome); assert only on records the test created,
found by those keys (INTEG-4); remove leftovers of globally unique constraints before acting; never mutate shared seed
data (E2E-10); never assert a global count in a shared store.
- *Why:* a top-N test passed only while no other test created a larger value; retries tripped over the previous
  attempt's data until each attempt created fresh principals.
- *Check:* the suite passes twice in a row on one store and with every test repeated (nightly, GATE-9); the Auditor
  flags fixed names in mutating tests.
- *Applies when:* tests share a store, account space, file system or fake.
- *Provenance:* industry baseline

### Determinism and isolation

**TCQ-6** — Make every result independent of when, where and in what order it runs: time from the injected clock or
from fixed instants written with their zone (INTEG-5); ids and randomness through seams; generated and property-based
tests print their seed and replay it from an argument; the runner pins process zone and locale (one project
deliberately foreign, E2E-7) and tests pass zones explicitly; nothing depends on the order of unordered collections,
directory listings or maps, on machine speed, or on wall-clock dates inside payloads.
- *Why:* tests running in the audience's own zone hid code that relied on the host zone (LL-13); payload dates taken
  from the wall clock instead of the test clock made boundary tests depend on the hour they ran.
- *Check:* the nightly runs while UTC and display dates differ (STRAT-8) and in random order; lint bans wall-clock and
  unseeded random calls in the test tree outside seam helpers; a failing generated test prints its replay seed.
- *Applies when:* always.
- *Provenance:* LL-13 (KatenatsioTipster, 2026-10)

**TCQ-7** — Never sleep to wait: wait on a state — auto-retrying assertions, a poll with an interval and a bounded
timeout, the awaited response, event, exit or domain signal ("save disabled = nothing left to save"); each wait's
failure message names what it waited for. A fixed duration only when elapsed time is the behaviour under test (an idle
window, a debounce, a deadline), taken from the spec and named as such. Every test has a timeout justified by its
content; a long journey raises its own, with the reason.
- *Why:* a fixed sleep is too short on a slow runner (a flake) or wastes time on every run; an unbounded wait hangs
  the lane with no verdict.
- *Check:* lint flags sleep and fixed-delay calls in the test tree outside a reasoned list of time-subject tests; the
  flake report (GATE-6) stays empty.
- *Applies when:* always; strictest in integration and end-to-end tests.
- *Provenance:* industry baseline

**TCQ-8** — Make every test pass alone, in any order and repeated: it creates what it needs and leaves nothing the next
test can see; clock, fakes, flags, environment and culture are reset by automatic fixture teardown, never by hand in a
`finally`; no static mutable state in test code; no test reads another's output. The nightly run in random order with
a printed seed and every test repeated proves it (GATE-9); a test failing only there is a DEF (ESC-11).
- *Why:* a visibility test passed only because the runner happened to order it before a test that created a larger
  value; hand-written resets leak the day one is forgotten (INTEG-4).
- *Check:* the nightly random-order and repeat run is green; the Auditor greps for resets in `finally` blocks and
  static mutable fields in the test tree.
- *Applies when:* always.
- *Provenance:* industry baseline

**TCQ-9** — Write every test to pass under parallel workers, even while its lane runs serially: ephemeral ports, a
temporary directory per test, a store or tenant per worker (INTEG-3), no mutation of process-global state
(environment variables, working directory, culture, static singletons, the system clock). A test that must own
process-global state sits in a declared serial group with its reason in `TESTING.md`.
- *Why:* a suite written for one worker hides coupling until the first attempt to speed it up turns it red.
- *Check:* the nightly runs ≥ 2 workers (GATE-9); serial groups are listed with reasons; lint bans fixed ports.
- *Applies when:* always.
- *Provenance:* industry baseline

**TCQ-10** — Give each shared fixture an explicit lifetime and owner: scope (test · class · worker · run), what it
creates, what tests may change, and its teardown, which also runs after a failure. Expensive fixtures (host, store,
browser, fake server) are shared per run or worker and are read-only to tests or reset by the fixture itself; setup and
seed fixtures are never retried and fail the run loudly (E2E-10); no lazily created hidden state outside a fixture
(e.g. per-principal clients cached in a static field).
- *Why:* principal clients cached in statics and fakes reset by hand let one forgotten reset leak into later classes.
- *Check:* each fixture's scope is declared in code; an interrupted run leaves no store, process or file behind
  (INTEG-3); review checklist.
- *Applies when:* any fixture used by more than one test.
- *Provenance:* industry baseline

### Diagnostics, assertions and helpers

**TCQ-11** — Make every failure explain itself: the message states the rule, expected and actual, and the context —
status and body for a call, stdout, stderr and exit code for a command, the ids of the records involved; table-driven
and matrix checks collect every failing row and report them at once; traces, screenshots, logs and recordings of
failed tests are kept as run artifacts (GATE-10); no bare boolean assertion without a message.
- *Why:* failing output posted on the run page made failures readable without raw logs, which agents often cannot
  fetch (LL-31).
- *Check:* a forced failure per suite shows rule, expected, actual and context in the message and its artifacts on the
  run.
- *Applies when:* always.
- *Provenance:* LL-31 (KatenatsioTipster, 2026-10)

**TCQ-12** — Assert observable outcomes — return values, state re-read through the public interface (VAR-20), output,
messages a protocol fake received — not internal calls. Interaction assertions only at external boundaries (what the
product asks, FAKE-8) or where the side effect is the specification (a notification, an audit row). Mock only ports
the product owns, prefer stateful fakes to scripted mocks, never mock the unit under test or a plain value object.
- *Why:* tests pinned to internal calls break on every refactor and stay green while the outcome is wrong.
- *Check:* the Auditor samples interaction assertions; each names a boundary or a specified side effect.
- *Applies when:* always.
- *Provenance:* industry baseline

**TCQ-13** — Test every piece of test code that has logic — builders that derive, fakes with state or format rules,
readers of output, custom matchers, wait helpers, linking helpers, report and gate scripts — with its own tests in the
test tree (gate scripts: GATE-8; fake parity: FAKE-5). A defect in a helper is a test defect, classified and fixed
like any other (ORACLE-8).
- *Why:* the gate that now fails on units no test runs was itself tested before it could guard the build (LL-2); the
  phone sweep found a race inside a navigation helper, not in the product (LL-4).
- *Check:* the Auditor lists helpers, fakes and matchers with branches and finds a test for each.
- *Applies when:* always.
- *Provenance:* LL-2, LL-4 (KatenatsioTipster, 2026-10)

**TCQ-14** — Keep the expected side independent of production code in the code itself: expected-value helpers,
builders and fakes may construct and read production types but never call production logic that computes, maps,
parses or serializes; a fake emits the recorded external format and never reuses the production adapter's mapper or
serializer to build its answers; limits and copy are literals from the spec, never production constants or resource
files (ORACLE-4); a rule implemented in several tiers is checked against one golden-vector file (ORACLE-15).
- *Why:* downstream tests were fed the computation's own outputs, so a reader misreading a field stayed invisible
  (LL-2); fakes built from the team's assumption agreed with the product and hid a zone error (LL-1).
- *Check:* an architecture test over the test tree bans calls into production logic from fakes, builders and
  expected-value helpers (reasoned allowlist of types); the Auditor greps expected sides (ORACLE-4).
- *Applies when:* always; strictest on money, time, ranking and access.
- *Provenance:* LL-1, LL-2 (KatenatsioTipster, 2026-10)

**TCQ-15** — Reach the product only through its interfaces and the seams `architecture.md` declares (ARCH-11, ARCH-12).
The Tester never edits production code: a missing hook (clock control, run-one-cycle trigger, reset or control
operation, test host entry point) is a `TSEAM-n` in `test_plan.md` that fails Gate T until the Architect specifies it.
Every test-only hook is unreachable with shipped settings, proven by a test; no reflection, private access,
monkeypatching or widened visibility into production internals; no development auth shortcut (INTEG-7).
- *Why:* a hook added ad hoc by whoever needed it ships enabled; reflection into internals tests what no user reaches
  and breaks on every refactor.
- *Check:* ownership_check (no Tester commit in production paths); the Auditor greps the test tree for reflection and
  private-access calls and shipped settings for enabled hooks; each hook has its "absent when shipped" TC.
- *Applies when:* always.
- *Provenance:* industry baseline

**TCQ-16** — Review every test added or changed in the cycle against the checklist below: the Tester before each
hand-off, the Auditor at L6 on every test of a money, time or access rule plus a sample of the rest. A failed item is
a finding citing its rule id; test code meets the same static bar as production code (GATE-4).
- *Why:* nobody reviewed test quality, so weak oracles (`> 0`, loose ranges, status-only checks) and an
  order-dependent test sat in a suite that looked green.
- *Check:* `test_report.md` records the self-review; `audit.md` L6 lists the tests reviewed and the findings.
- *Applies when:* every cycle with test changes.
- *Provenance:* industry baseline

## Test-code review checklist

| # | Question | Rule |
|---|---|---|
| 1 | Was it seen failing for its stated reason (red before code, killed mutant or negative control)? | ORACLE-3, ORACLE-13 |
| 2 | Is every expected value a literal from the oracle table, with its source cited? | ORACLE-1, ORACLE-4 |
| 3 | Did any expected value change since T-SHA, and is the amendment cited? | ORACLE-2 |
| 4 | Is the assertion discriminating: whole record, exact money, full order, forbidden data absent? | ORACLE-9 |
| 5 | Is there any skip, focus, expected-failure, silent-pass branch or swallowed assertion? | TCQ-1 |
| 6 | Does the name state the behaviour and carry TC and requirement ids? | TCQ-2 |
| 7 | One behaviour, arrange → act → assert, no logic beyond a table? | TCQ-3 |
| 8 | Does arrange use builders and show only the fields that matter? | TCQ-4 |
| 9 | Unique data, assertions only on own records, no global counts? | TCQ-5 |
| 10 | Any wall clock, host zone or locale, unseeded randomness or unordered iteration? | TCQ-6 |
| 11 | Any sleep, unbounded wait or unexplained timeout? | TCQ-7 |
| 12 | Does it pass alone, in random order, repeated and in parallel? | TCQ-8, TCQ-9 |
| 13 | Are fixture scope, ownership and teardown explicit? | TCQ-10 |
| 14 | Would its failure message tell the next agent what broke? | TCQ-11 |
| 15 | Outcomes asserted, not internal calls? | TCQ-12 |
| 16 | Are new helpers, fakes and matchers with logic tested? | TCQ-13 |
| 17 | Does any expected side, builder or fake call production logic? | TCQ-14 |
| 18 | Any test-only hook outside a TSEAM, or reflection into internals? | TCQ-15 |
| 19 | Shipped settings only, no override of a world fact? | FAKE-4 |
| 20 | End-to-end: real entry point, user-like selectors, error tripwire on? | E2E-1, E2E-2 |

## Illustration — one behaviour, two stacks

```csharp
[Fact(DisplayName = "TC-0042 [BOOK-BR-3] exactly at the deadline the booking is locked")]
public void Exactly_at_the_deadline_the_booking_is_locked()
{
    var clock = new FixedClock(Instant("2026-10-25T18:00:00+03:00"));             // arrange
    var booking = ABooking().WithDeadline(clock.Now).Build();
    var editable = new BookingLock(clock).CanEdit(booking);                       // act
    Assert.False(editable, "BOOK-BR-3: editable before the deadline, locked at it"); // assert
}
```

```python
@pytest.mark.parametrize("qty,price,expected", [(3, "19.99", "59.97"), (7, "0.15", "1.05")],
                         ids=["TC-0043 [ORD-BR-1] 3 x 19.99", "TC-0044 [ORD-BR-1] 7 x 0.15"])
def test_line_total_is_quantity_times_unit_price(qty, price, expected):
    line = an_order_line(qty=qty, unit_price=Decimal(price))         # arrange
    total = line_total(line)                                         # act
    assert total == Decimal(expected), f"ORD-BR-1 {qty} x {price}"   # assert: literal from the oracle table
```
