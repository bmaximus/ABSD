# Traceability — requirements to tests to results

Code **TRACE**. How each requirement is tied to its tests and their results: catalogue, links, load-time helpers,
verdicts, clause coverage, plan conformance and the id checks behind every gate. Tools:
`absd/tooling/traceability_report.py` (test results), `absd/tooling/trace_check.py` (artifacts). Test ids: STRAT-11;
CI wiring: GATE-14 (`absd/playbook/testing/ci-and-release-gates.md`).

## Checklist

- [ ] Every active requirement has ≥ 1 acceptance-level test; runs report verified/failing/untested (TRACE-1)
- [ ] QC rows proven by their gate on a planted-failure (RED) and a clean (GREEN) fixture (TRACE-1)
- [ ] A link to an unknown or retired id fails the run (TRACE-1)
- [ ] One catalogue table, header kept, Analyst-only; ids permanent; Status `active`/`retired`, successor named (TRACE-2)
- [ ] Every test carries its `TC-nnnn`, every proving test its `[AREA-n]`; links proven in each runner's XML (TRACE-3)
- [ ] Reserved prefixes are references, never requirement links (TRACE-4)
- [ ] One load-time helper per stack refuses unknown and retired ids before tests run (TRACE-5)
- [ ] Both report runs on every push and at Verify; every `--junit` glob holds test cases; summaries published (TRACE-6)
- [ ] Every AC, BR boundary and NF criterion maps to a TC; linked tests assert the clause they claim (TRACE-7)
- [ ] Only first-attempt passes prove; a pass-on-retry or a skip proves nothing (TRACE-8)
- [ ] Plan conformance over index + parts in a cycle: none missing (red run: later-WP units, §14) or failing; unplanned reconciled (TRACE-9)
- [ ] Artifacts end with a Traceability table; trace_check output recorded per gate in `cycle.md` (TRACE-10)
- [ ] A changed or retired requirement has its tests relinked or removed in the same cycle (TRACE-11)
- [ ] Gate 3: every in-scope requirement verified; untested exempt only on a shrinking brownfield DEBT list (TRACE-12)

## Rules

**TRACE-1** — Link every active catalogue requirement to ≥ 1 acceptance-level test — one exercising it through a
public interface of the running product: an E2E form (E2E-2), the real-transport host for a business rule (INTEG-1),
or the measuring test a REQ-NF names; a unit test alone never qualifies — and report it on every run as
**verified** (every linked test that ran passed), **failing** (any linked test failed) or **untested** (no linked test
ran). A link to an id the catalogue lacks or retired fails the run. A `QC-n` row is proven by an acceptance-level test
running its gate on a planted-failure fixture (expects RED) and a clean one (expects GREEN), linked `[QC-n]`; a drill
(restore, rollback) proves its row through a scripted job that emits JUnit XML.
- *Why:* admins could not act as members because no requirement or acceptance test claimed it (LL-5); declared links
  and a verified/failing/untested report made unproven requirements visible (LL-36); Foundation QC rows were CI steps
  and drills, never tests, so every Foundation Gate 3 failed (LL-57).
- *Check:* the TRACE-6 runs; Foundation negative control — a test linking an unknown id turns the run red (GATE-8);
  each QC row has its fixture pair or drill job; the Auditor re-runs the report at the product SHA (XCA-2).
- *Applies when:* always.
- *Provenance:* LL-5, LL-36 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**TRACE-2** — Keep one requirement catalogue, `absd-project/catalogue.md`, owned by the Analyst: one Markdown table with
the template's header kept exactly (`| ID | Area | Role | Story | Source | Status |`), one row per requirement in users'
terms — `AREA-n`, `AREA-NF-n` (measurable), `AREA-BR-n` (with its boundary values) — its source cycle, and Status
exactly `active` or `retired` (the linking helpers compare the whole cell). Ids are permanent: next = highest in
catalogue and archive + 1, never reused or renumbered; area codes are never reserved codes (TRACE-4). The Analyst
changes the file only by applying the Gate 1 Catalogue delta in its own commit; a superseded or removed requirement
keeps its row, Status `retired`, its successor named in Source.
- *Why:* a catalogue kept by hand beside archived analyses drifted from them, with nothing comparing the two (LL-36).
- *Check:* trace_check gate1 (every requirement in `analysis.md` is in the catalogue); traceability_report exits 2 on a
  duplicate id; ownership_check shows only Analyst commits on the file (GATE-14).
- *Applies when:* always.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10)

**TRACE-3** — Put every link where the tools read it — the run's report XML in the JUnit format (e.g. pytest
`--junitxml`, Jest or Playwright junit reporters, xUnit junit loggers): the test's `TC-nnnn`
(≥ 4 digits, STRAT-11) and, on each test that proves a requirement, its `[AREA-n]`, `[AREA-NF-n]` or `[AREA-BR-n]`
tokens, in the display name or as `<property name="tc">` / `<property name="requirement">` (repeatable or
comma-separated). Name the acceptance criterion asserted (`AREA-n.ACk`) in the title or an `ac` property. Write ids
whole, with hyphens, exactly as defined (`test_tc_0042` is not read). Where a runner rewrites names (spaces to
underscores defeat a bare `TC-0042`), bracket it — `[TC-0042]` — or use properties; a runner carrying neither gets
its XML post-processed from a Tester-owned map. At Foundation, prove with one real report per runner that every link
survives into the XML.
- *Why:* a lost annotation or a typo leaves a requirement looking untested while a test silently proves nothing (LL-36).
- *Check:* the TC tokens found in the reports equal the TCs of the test tree; Foundation evidence per runner.
- *Applies when:* always.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10)

**TRACE-4** — Never let a reserved prefix count as a requirement link: tokens whose code is a reserved code
(`absd/playbook/README.md`: every playbook code and TC, DEF, CR, ADR, UJ, SCR, DEBT, RISK, LL, AR, TF, DQ, F, CLR, WP,
INH, TSEAM, CHAR, C, A, OQ, D, UXQ, UXA) are references — `[DEF-12]` on a regression test, `UJ-3` in a journey title —
and no area code may be one. `QC` is not reserved: it is the Foundation quality capabilities' fixed area code. Cite
playbook rules in tests as `ABSD:CODE-n`, never bracketed.
- *Why:* a regression test citing its defect must not read as a requirement link, nor fail the run as a typo; this
  list once differed from the tools' (LL-57).
- *Check:* a test titled `[DEF-n]` stays out of the catalogue report; the Analyst checks new area codes against the
  reserved list at Gate 1 (ELIC-20); kit lint keeps the tools' sets equal to the README's.
- *Applies when:* always.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)

**TRACE-5** — Give each test stack one shared linking helper that reads the catalogue when tests are collected or
defined and refuses — before any test runs — a link to an unknown or retired id, then writes the links as report
properties (illustrations below); tests link only through it (lint bans raw annotation strings). A stack without
collection hooks (e.g. xUnit or NUnit) gets one test that reflects over every test's names and traits and fails on
an unknown id.
- *Why:* a load-time throw made a typo'd id fail at once instead of leaving a requirement silently untested (LL-36).
- *Check:* Foundation negative controls per stack: an unknown id and a retired id each stop the run (GATE-8).
- *Applies when:* always.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10)

**TRACE-6** — Run `traceability_report.py` on every push and at Verify, twice (usage below): over the suites
`TESTING.md` marks acceptance-level (E2E forms, real-transport integration, REQ-NF measuring suites) with `--fail-on
failing,unknown,untested`, proving TRACE-1; and over every suite with `--plan` while a cycle is active (TRACE-9) and
`--fail-on failing,unknown,missing`, so a failing unit test also turns its requirement red. One `--junit` glob per
suite: a glob matching no file with a test case is a suite that did not run — exit 2, RED (GATE-1). Publish both summaries on the run
page (GATE-10) and in `test_report.md` with the run's SHA.
- *Why:* a report that only warned on untested requirements let one lose its last test with CI green; a report the
  owner could read made proof visible without reading code (LL-36).
- *Check:* both invocations sit in a Tester-owned workflow (GATE-14); the Auditor re-runs them at the product SHA.
- *Applies when:* always; the `--plan` run while a cycle is active.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**TRACE-7** — Cover clauses, not stories: every AC `<ID>.AC<n>`, every BR boundary and every NF criterion maps to ≥ 1 TC
in `test_plan.md` (trace_check gateT), and a requirement counts as verified for the cycle only when each of its in-scope
clauses has a passing TC (TRACE-9) — on each device class it runs on (E2E-6). A test links a requirement only if it
asserts one of its clauses — a link to a requirement it merely passes through is tag drift, a finding; a requirement
with ≥ 2 ACs and one linked test is reviewed for unproven clauses.
- *Why:* one passing test "verified" a requirement whose other clauses (won, lost, back to open) were never run;
  measurable criteria nobody turned into tests passed audits (LL-45).
- *Check:* gateT AC coverage (TC rows only); each device project's results are a separate `--junit` glob that must
  match, and its per-project pass is read in `test_report.md` §2; the Auditor samples linked tests against ACs (L3).
- *Applies when:* always.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**TRACE-8** — Count only first-attempt passes as proof. The report XML records a pass-on-retry as a plain pass, so the
job producing acceptance results fails on any pass-on-retry — the runner's option where it exists
(e.g. Playwright `--fail-on-flaky-tests`; pytest without a rerun plugin; Jest without `retryTimes`) or a step reading
the runner's retry-aware report — and `test_report.md` lists the requirement as failing; the flake is routed per ESC-11
(GATE-6), and an older test's flake turning this job red blocks the merge until Mode D fixes it. A skip proves
nothing: a requirement whose linked tests all skipped is untested, and the skip itself is RED (GATE-1).
- *Why:* an acceptance report counted a test that passed on retry as verified; a live check that could not run
  exited 0 (LL-25).
- *Check:* runner flags of the acceptance job; Foundation negative control — a test failing only on its first attempt
  turns the job red (GATE-8).
- *Applies when:* any runner with retries (GATE-6 allows ≤ 1 for e2e).
- *Provenance:* LL-25 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**TRACE-9** — Check plan conformance with `--plan absd-project/working/test_plan.md` on every push of the cycle branch
after Gate T and at Verify, once over the index and its `test_plan/` parts (a plan with no TC exits 2). Each planned TC
exists as a test that ran and passed (`missing` = no test or only skipped ones; `failing`) — red by design until the
work packages turn it green; each `unplanned` TC id is an earlier cycle's (archived plan) or a "Verify addition"
appended to the plan with its source; any other is a finding. The Plan & Bind red run uses
`--fail-on unknown,unplanned`; each TC it reports missing belongs to a unit keyed to a later WP (plan §12) and is
listed in §14 — else a plan defect. With no active cycle the step prints "no active cycle" (GATE-14).
- *Why:* measurable criteria never became tests (LL-45); tests written after the code had no plan to conform to
  (LL-29); a split plan's index planned 0 TCs and passed, and plan gates re-run after the archive failed every push
  (LL-55, LL-57).
- *Check:* the plan-conformance section of `test_report.md`: planned, passing, missing, failing, unplanned + reason.
- *Applies when:* `absd-project/working/test_plan.md` exists (an active cycle).
- *Provenance:* LL-29, LL-45 (KatenatsioTipster, 2026-10); LL-55, LL-57 (ABSD v2 kit review, 2026-10)

**TRACE-10** — End every pipeline artifact with a Traceability section `trace_check.py` reads: a table whose first cell
holds the upstream id (requirement, AC, UJ, SCR, EXT, TC) and whose other cells name the downstream ids, every id whole
and exactly as defined. Defining tables carry a Status column (new / changed / removed) — without one the word
"removed" or "retired" anywhere in a row excludes it — and an id the cycle drops keeps its row marked `removed`, so
downstream coverage stops demanding it. At each gate the Manager runs the preset (table below), records invocation and
output in the `cycle.md` gate ledger, and fails the gate on any ✗; the artifact's owner fixes it, never the Manager.
The Manager re-runs gateT after each Gate T amendment and after Verify; CI re-runs every recorded invocation while the
cycle is active (GATE-14).
- *Why:* criteria vanished between analysis and tests without anyone noticing (LL-45); the orchestrator wrote other
  agents' artifacts to get past a stop (LL-26).
- *Check:* each gate-ledger row carries trace_check output; the CI job re-runs the recorded invocations.
- *Applies when:* every gate of every mode.
- *Provenance:* LL-26, LL-45 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

**TRACE-11** — When a requirement changes or retires, settle its tests in the same cycle: Plan & Bind lists every
existing test whose oracle changes (ORACLE-2) and every test linking a retired id, and relinks each to the successor
or removes it with the reason in `test_plan.md`; links to retired ids fail the run (TRACE-1).
- *Why:* a still-passing test of a replaced rule would report "verified" for behaviour that no longer exists.
- *Check:* `unknown` = 0 in the report after retiring; amendments list the relinked tests.
- *Applies when:* Modes F, S, C, D with catalogue changes.
- *Provenance:* industry baseline

**TRACE-12** — Hold Gate 3 to verified: every requirement in the cycle's scope is verified at the Gate 3 product SHA (0
failing, 0 untested, every clause per TRACE-7) and the catalogue report has no unknown link. Only in brownfield
adoption may `untested` stay out of the push lane's `--fail-on`, while every untested id has a DEBT row with a
burn-down (STRAT-12) and the untested count never rises; it joins `--fail-on` when the count reaches 0.
- *Why:* with the suite built outside the pipeline, nobody knew which requirements had no proof (LL-27).
- *Check:* the catalogue section of `test_report.md` (counts per state, in-scope list); the Auditor compares the
  untested count with the previous cycle's (L3).
- *Applies when:* Gate 3 always; the exemption only during brownfield adoption.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

## Tool reference

```bash
# TRACE-6 run 1 — acceptance-level suites only (TRACE-1); one glob per device project
python3 absd/tooling/traceability_report.py --junit "e2e-results/desktop/*.xml" --junit "e2e-results/phone/*.xml" \
  --catalogue absd-project/catalogue.md --fail-on failing,unknown,untested --summary-md trace-acceptance.md
# TRACE-6 run 2 — every suite + plan conformance (TRACE-9)
python3 absd/tooling/traceability_report.py --junit "test-results/**/*.xml" --junit "e2e-results/**/*.xml" \
  --catalogue absd-project/catalogue.md --plan absd-project/working/test_plan.md \
  --fail-on failing,unknown,missing --json trace.json --summary-md trace.md
# TRACE-10 — gate preset (Manager), FACT sources resolved against the register
python3 absd/tooling/trace_check.py gate gateT --working absd-project/working --catalogue absd-project/catalogue.md \
  --external-facts docs/testing/EXTERNAL-FACTS.md
```

Both tools exit 0 pass · 1 a check or `--fail-on` category failed · 2 usage or input error (a `--junit` glob without
test cases, a duplicate catalogue id, a plan with no TC, a missing artifact).

| Preset | Run at | Fails when |
|---|---|---|
| `gate1` | Gate 1 | `analysis.md` defines no requirement; a functional one has no AC; one is missing from the catalogue |
| `gate-ux` | Gate UX | a UJ or SCR is missing from `design.md`'s Traceability section; it cites a requirement the catalogue lacks |
| `gate2` | Gate 2 | a requirement in scope, a `defect.md` DEF (Mode D), a UJ, SCR or source EXT is missing from `architecture.md`; no WP |
| `gateT` | Gate T | no TC; an in-scope AC, NF, BR, DEF, UJ, SCR or architecture EXT is in no TC row; a TC source is missing or does not resolve (ORACLE-1); a TSEAM or a blocking spec defect is open |
| `gate3` | Gate 3 | a report the route needs (`cycle.md` `Mode:`) is missing; a verdict line outside tables is not `Overall: PASS` (audit) or `Verdict: PASS`/`N/A`; a Critical or Major finding is open (not fixed, resolved or accepted-by-user) |

Requirement source: `analysis.md`, else `brd.md` (Mode S without the Analyst) or `defect.md` (Mode D), scoped to the
ACs and NF/BR ids they cite. Mentions outside TC rows (an "Out of scope" line) are not coverage.

## Linking helpers (TRACE-5), two stacks

```ts
// e2e/support/requirements.ts — e2e tests link only through proves(); config: junit reporter with
// { embedAnnotationsAsProperties: true }. Usage: test('[ACC-3] … (ACC-3.AC2)', proves('TC-0042', 'ACC-3'), async …)
import { readFileSync } from 'node:fs';
const rows = readFileSync('absd-project/catalogue.md', 'utf8').split('\n')
  .map(l => l.split('|').map(c => c.trim())).filter(c => /^[A-Z][A-Z0-9]*-(NF-|BR-)?\d+$/.test(c[1] ?? ''));
const active = new Set(rows.filter(c => c[6]?.toLowerCase() !== 'retired').map(c => c[1]));
export function proves(tc: string, ...ids: string[]) {
  for (const id of ids) if (!active.has(id)) throw new Error(`${tc}: unknown or retired requirement ${id}`);
  return { annotation: [{ type: 'tc', description: tc }, ...ids.map(id => ({ type: 'requirement', description: id }))] };
}
```

```python
# conftest.py — @pytest.mark.proves("TC-0042", "ACC-3"); run with --junitxml (and --strict-markers)
import re, pytest
ID = re.compile(r"[A-Z][A-Z0-9]*-(?:NF-|BR-)?\d+")

def pytest_configure(config):
    config.addinivalue_line("markers", "proves(tc, *ids): the TC id and the requirements it proves")

def pytest_collection_modifyitems(config, items):
    text = (config.rootpath / "absd-project/catalogue.md").read_text(encoding="utf-8")
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in text.splitlines() if l.startswith("|")]
    active = {r[0] for r in rows if ID.fullmatch(r[0]) and r[-1].lower() != "retired"}
    bad = []
    for item in items:
        for mark in item.iter_markers("proves"):
            tc, *ids = mark.args
            item.user_properties += [("tc", tc)] + [("requirement", i) for i in ids]
            bad += [f"{item.nodeid} -> {i}" for i in ids if i not in active]
    if bad:
        raise pytest.UsageError("unknown or retired requirement ids: " + "; ".join(bad))
```
