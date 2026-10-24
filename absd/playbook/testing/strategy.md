# Test strategy — types, applicability, suite shape

Code **STRAT**. Which test types a product runs per interface profile, what each answers, where and when it runs,
how `TESTING.md` decides that once, test ids, component tests. Cases: VAR; expected
values: ORACLE; thresholds and gate mechanics: GATE.

## Checklist

- [ ] `TESTING.md`: a row per type (M/R/X per profile, home, command, lane), none blank, each home run (STRAT-1)
- [ ] `test_plan.md` cites `TESTING.md` and re-argues nothing (STRAT-1)
- [ ] Several profiles: the strictest cell applies; each profile's own form of the test exists (STRAT-2)
- [ ] Every R row names its triggering ids, or "no trigger" with the ids checked (STRAT-3)
- [ ] N/A only in X cells or for an absent subject, with evidence, Auditor-verified; M → N/A by ADR (STRAT-4)
- [ ] End-to-end row = the profile's E2E form driving the shipped artifact (STRAT-5)
- [ ] Pinned at the lowest level that sees it AND where its user sees it; e2e not in coverage (STRAT-6)
- [ ] Push lane holds every listed type; blocks merge, Gate 3, deploy (STRAT-7)
- [ ] Nightly at a divergence hour (else foreign zone + pinned midnights), never deploys; all lanes exist (STRAT-8)
- [ ] Cycle start: red → Mode D; not run yet → trigger it; credential missing → user or FAKE-10 waiver (STRAT-8)
- [ ] No check moved to a slower lane without a user-approved amendment; push lane within budget (STRAT-9)
- [ ] Every REQ-NF has a measurable TC: dataset, environment, metric, threshold (STRAT-10)
- [ ] Flat `TC-nnnn`; one TC = one oracle row (per data row when parametrized); level is an attribute (STRAT-11)
- [ ] Adoption/upgrade: existing suites mapped onto the matrix; missing M rows are DEBT, not N/A (STRAT-12)
- [ ] web-ui, native-app: each SCR component × state in a component harness, queried by role (STRAT-13)

## Rules

**STRAT-1** — Decide applicability once, at Bootstrap, in `TESTING.md`: per matrix row (below), M/R/X per declared
profile, the home (path, runner, command, report) and the lane; re-decide only in Mode C (a profile, external
system or persistent store added or removed) or Mode U. `test_plan.md` cites the rows it relies on and never re-argues
them. A home that never ran at a recorded commit does not count as present (GATE-1).
- *Why:* nobody had decided which kinds of test the product needed, so its suite was built later outside the pipeline;
  per-cycle re-arguing pastes "N/A" forward (LL-27).
- *Check:* `TESTING.md` §1 has no blank cell; its history shows edits only in Foundation, Mode C or Mode U cycles; every
  `test_plan.md` has an applicability citation and no per-cycle N/A argument.
- *Applies when:* always.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

**STRAT-2** — A product with several profiles applies, per row, the strictest cell of any declared profile
(M > R > X), and every declared profile still gets its own form of that test (an http-api black-box access test AND the
web-ui flow on the same data).
- *Why:* free accounts received paid data in an API response no screen showed; only a test of the API saw it (LL-10).
- *Check:* `TESTING.md` lists one home per (row × declared profile) where the cell is M or triggered R.
- *Applies when:* `context.md` declares more than one profile.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**STRAT-3** — An R cell becomes mandatory as soon as a requirement, business rule, REQ-NF or named RISK triggers it;
`test_plan.md` lists, per R row, the triggering ids and their TCs, or "no trigger" with the ids it checked.
- *Why:* a visual-regression requirement was written in every cycle and never automated (LL-53).
- *Check:* the Auditor searches `analysis.md`, `design.md` and the RISK register for performance, load, golden-output,
  compatibility, accessibility, security and device terms; each hit maps to an R row with TCs.
- *Applies when:* any R cell in the matrix for a declared profile.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10)

**STRAT-4** — Mark N/A only in X cells, or where the row's subject is absent (no persistent state, jobs, flags or
secrets — the footnoted conditions), stated with the evidence that shows it absent; neither needs a user waiver. An M
cell becomes N/A only through an ADR that passed Gate 2R. Never valid: slow, flaky, hard to set up, "covered by unit
tests", "no UI" while another interface exists, "the environment cannot run it" (a RISK and BLOCKED evidence, never a
decision). The Auditor — not the Manager — verifies every N/A at 2R and at audit.
- *Why:* a sandbox unable to run the migration tool became an architecture instruction (LL-21); audits certified
  suites they never ran (LL-24); "N/A only by profile" left no honest N/A for a product without jobs (LL-56).
- *Check:* the Auditor maps each N/A in `TESTING.md` and `test_plan.md` to an X cell, an absent subject with its
  evidence, or an ADR with a 2R PASS; an invalid reason is a Major finding (L6).
- *Applies when:* always.
- *Provenance:* LL-21, LL-24 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**STRAT-5** — Satisfy the End-to-end row only with the profile's E2E form (below) driving the shipped artifact through
its real entry point; in-process, unit or mocked-boundary tests never stand in for it.
- *Why:* tests fed a computation its own inputs, so the reader that misread a provider's field ran on no tested path
  (LL-2).
- *Check:* each E2E home in `TESTING.md` names the form; the Auditor runs it and sees the built artifact start (E2E-2).
- *Applies when:* always (the row is M for every profile).
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**STRAT-6** — Pin every behaviour at the lowest level that can observe it (rule → unit, boundary → integration,
external reading → contract) AND where its user observes it (chain or end-to-end); neither substitutes for the other.
End-to-end and device tests never count towards coverage or the no-untested-unit gate (GATE-2); component tests do
(STRAT-13).
- *Why:* a results reader with 0% coverage sat behind flows that "passed" (LL-2); a specified delete step was
  half-implemented while per-cycle checks passed (LL-51).
- *Check:* trace: each BR has a unit or integration TC and each AC/UJ an acceptance-level TC; the coverage gate's
  inputs exclude end-to-end reports.
- *Applies when:* always.
- *Provenance:* LL-2, LL-51 (KatenatsioTipster, 2026-10)

**STRAT-7** — Run the push lane on every push at the exact commit; it blocks merge, Gate 3 and deploy. Every M or
triggered R type is in it unless `TESTING.md` names another lane with a reason (cost, live credentials, real devices),
and such a type keeps a push-lane counterpart (recorded contract for live, emulated for real device, budget smoke for
full performance); changed-code mutation runs per push or, at the latest, at Verify on the cycle's product SHA.
- *Why:* empty-infrastructure boot and migrate-from-empty never ran per push, so a missing-database crash and a schema
  missing ~60% of its columns surfaced only in audits (LL-14, LL-21).
- *Check:* test workflows contain each push-lane job; the Auditor reconciles the `TESTING.md` lane column with their
  triggers.
- *Applies when:* always.
- *Provenance:* LL-14, LL-21 (KatenatsioTipster, 2026-10)

**STRAT-8** — Run the nightly lane at an hour when UTC and the display zone are on different dates; with no such hour
(a UTC+0 display zone) or several display zones, also run the date-sensitive suites with the process zone set to the
foreign project's zone and the clock pinned at each display zone's local midnight ± 1 min. It never deploys. At cycle
start and Mode R: a red nightly or live run → Mode D first; not run yet → trigger it, its result decides; a live
credential missing → the user supplies it, or a FAKE-10 waiver `D-n` + RISK. The post-deploy, per-cycle and release
lanes run as § "Lanes" says.
- *Why:* date bugs hide unless dates differ during the run (LL-40), and a UTC+0 zone never differs (LL-57); a live job
  exited 0 without its credential (LL-25); a health check passed on a blank page (LL-32); the first cycle had no
  nightly and no credential, which Mode D cannot fix (LL-55, LL-56).
- *Check:* the schedule falls in a divergence window of the Locale & Time Profile zones, or pinned-midnight runs exist
  per display zone; the cycle-start record cites the last green nightly and live runs, the triggered run, or the waiver.
- *Applies when:* always; post-deploy whenever the product deploys or publishes.
- *Provenance:* LL-25, LL-32, LL-40 (KatenatsioTipster, 2026-10); LL-55, LL-56, LL-57 (ABSD v2 kit review, 2026-10)

**STRAT-9** — Treat moving a check to a slower lane, sampling it, or dropping a device/runtime project from the push
lane as loosening a gate: it needs a user-approved Gate T amendment. Keep the push lane within the wall-time budget in
`TESTING.md` by parallel workers, sharding, an isolated environment per worker and moving cases to a lower level —
never by dropping cases.
- *Why:* a lane thinned for speed leaves M cells untested with no recorded decision.
- *Check:* `git diff` of test workflows and the `TESTING.md` lane column against Gate T amendments; push-lane duration
  trend in CI.
- *Applies when:* always.
- *Provenance:* industry baseline

**STRAT-10** — Map every REQ-NF at Gate T to ≥ 1 TC with a measurable assertion: dataset (size and ordering, VAR-7),
environment, metric and threshold (e.g. "p95 ≤ 300 ms and ≤ 3 queries at 10 000 rows"). "Reviewed", "logic exists" or
a screenshot kept for humans is not a test.
- *Why:* measurable criteria passed audits by code reading (LL-45); visual regression was promised and never compared
  (LL-53).
- *Check:* trace_check REQ-NF → TC; each such TC asserts a number or an exact comparison.
- *Applies when:* any REQ-NF, including the default operability REQ-NFs.
- *Provenance:* LL-45, LL-53 (KatenatsioTipster, 2026-10)

**STRAT-11** — Give tests flat, product-scoped ids (`TC-nnnn`, ≥ 4 digits, never reused; next = highest in repo and
archive + 1). One TC = one oracle-table row; a parametrized test carries the TC per data row (e.g. pytest
`pytest.param(…, marks=proves(…))`, Jest `test.each` with a TC column, xUnit the TC as first theory argument)
and spans rows only when its oracle row holds the input table. Level (unit · component · integration · contract · e2e),
purpose (acceptance · access · chain · smoke · regression `DEF-n` · nfr · char `INH-n` · a11y · visual · perf ·
security · migration), profile, device/runtime class, lane and requirement ids are attributes — a name token or report
property (e.g. JUnit XML `<property>`, TRX trait) — never part of the id; a moved test keeps its id.
- *Why:* a level in the id forces a rename when an escape moves the test (ESC-1); with parametrized tests nobody knew
  whether a TC meant a function or a row (LL-57).
- *Check:* traceability_report lists planned TCs with no test and unplanned TC ids; the Auditor (L6) and, if the
  stack has one, the test-tree lint check each planned TC is on ≥ 1 testcase of exactly one test function (TCQ-2).
- *Applies when:* always.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)

**STRAT-12** — In Mode B (adopt) and Mode U, map every existing suite onto the matrix (row → existing home or "none")
and record each M or triggered R row without a suite as DEBT with a burn-down; absence is a gap, never an N/A.
Inherited behaviour is pinned by CHAR tests (ORACLE-12).
- *Why:* fixes and the whole suite came outside any route; nobody knew which kinds of test were missing (LL-27).
- *Check:* the Baseline section of `test_report.md` has one line per matrix row; each gap has a DEBT id in `context.md`.
- *Applies when:* brownfield adoption, v1 migration, kit upgrade.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

**STRAT-13** — Test each screen component of `design.md`'s component–state matrix in every cell, in a component
harness (DOM emulation, or the platform's emulator or instrumented runner) with the network faked at the HTTP boundary
and shaped by the published contract (FAKE-1), never by stubbing the product's own modules. Query by role and
accessible name; assert `design.md` copy literally (`SPEC:SCR-n.<state>`). Component reports count for GATE-2 and
GATE-3; a component test never replaces the end-to-end journey (E2E-5).
- *Why:* with e2e kept out of coverage (STRAT-6) every UI component was an untested unit, yet no rule said how to test
  one (LL-57).
- *Check:* each SCR × state cell has a component TC citing it; component reports feed `coverage_gate.py`; the Auditor
  samples role + name queries and literal copy.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)
- Illustration: e.g. Testing Library with Vitest or Jest; Espresso or XCUITest.

## Test types

| Type | Answers | Runs against | Rules |
|---|---|---|---|
| Unit | Is each rule (calculation, decision, parsing, permission) right in isolation? | in-process; clock, ids, randomness injected | VAR, ORACLE |
| Component | Does each screen component render every designed state, copy and role? | DOM or emulator harness, network faked | STRAT-13 |
| Integration | Does code behave on the real boundary (store, broker, fs, subprocess)? | real local dependencies; only external systems faked | INTEG |
| Contract — recorded | Do we read each external system right (format, zone, calendar, empty, errors, sync/async)? | committed recordings + VERIFIED facts | FAKE, EXT |
| Contract — live | Does the real system still answer as recorded? | live system, real credential (missing = RED) | FAKE, GATE-1 |
| Access & visibility | Does each principal get exactly the right status and data? | running service | ACCESS |
| Chain | Does a real boundary payload reach the persisted and shown outcome? | all real except the external system | INTEG, VAR-18 |
| End-to-end | Does each feature and cross-role journey work through the real interface? | shipped build, per device/runtime project | E2E |
| Acceptance traceability | Is each catalogue requirement verified, failing or untested? | the run's test reports | TRACE |
| Device / runtime | Does each supported class work as a target of its own? | one project per class; real devices at Mode R | VAR-6 |
| Accessibility | Can everyone operate it (scan + keyboard path)? | every rendered state | A11Y |
| Visual / golden + Design QA | Does it look or print exactly as designed? | screenshots, golden output/datasets | VIS, DSN |
| Performance | Is it fast enough at Data Volume Profile max (latency, queries, size)? | production-volume data | PERF |
| Load, stress, soak | Does it hold a concurrency/throughput REQ-NF and stay flat over time? | production-like stack, scripted load | PERF-4 |
| Interface compatibility | Is a breaking change versioned; do N-1 clients and messages still work? | contract snapshot, N-1 clients and messages | COMPAT |
| Security | Does it resist misuse beyond access (injection, secret canary, dependencies)? | code, artifacts, running service | SEC |
| Migrations / backup–restore | Does state survive migrate-from-empty, upgrade from previous release, drift, empty-infra boot, restore? | shipped artifact + real store | INTEG, OPS |
| Smoke + rollback | Is the deployed system alive on its version; does failure roll back? | deployed system, read-only (pipeline: isolated canary) | E2E, OPS |
| Regression | Did a change break what worked? (a purpose tag: one test per escape, ESC-3) | all levels | ESC-1 |
| Mutation | Can the tests fail? | changed code; money/time/access rules | GATE-5, ORACLE |
| Characterization | What does inherited code do today? | existing code, at Baseline | ORACLE |
| Exploratory | What did nobody think to test? | running product (agent + human) | EXPL |

## Applicability matrix

M mandatory · R required when a requirement, rule or named risk triggers it · X not applicable.

| Test type | web-ui | native-app | http-api | cli | library | data-pipeline |
|---|---|---|---|---|---|---|
| Unit | M | M | M | M | M | M |
| Component | M | M | X | X | X | X |
| Integration | M | M | M | M | R (if it does I/O) | M |
| Contract¹ | M | M | M | M | M | M (every source + sink) |
| Access & visibility | M | M | M | R (credentials/profiles) | X | M (service identity × dataset) |
| Chain | M | M | M | M | R | M |
| End-to-end | M | M | M | M | M | M |
| Acceptance traceability | M | M | M | M | M | M |
| Device / runtime | M (phone unless waived) | M | X | R (OS/shell/width) | M (runtime versions) | X |
| Accessibility | M | M | X | R (NO_COLOR, no colour-only meaning) | X | X |
| Visual / golden + Design QA | M | M | X | R (golden output) | X | R (golden datasets) |
| Performance budgets | R | R | R | R | R | R |
| Load, stress, soak | R | R | R | X | X | R |
| Interface compatibility³ | R | R | R | R | M (API snapshot) | R |
| Model eval set (FAKE-13) | R | R | R | R | R | R |
| Security (beyond access) | M | M | M | R | R | M |
| Migrations / backup–restore² | M | M | M | R⁴ | R⁴ | M |
| Post-deploy smoke + rollback | M | M (store/channel) | M | M (install + withdraw) | M (registry install + yank/patch) | M (canary in an isolated namespace, E2E-16) |
| Exploratory | M | M | R | M | R (API usability) | M (output vs source of truth) |

¹ when the product talks to any external system, including deploy platforms, CI, mail, OCR/LLM, payment. ² when the
product owns persistent state. ³ a published contract, or stored or queued messages that outlive a release.
⁴ local state, cache or configuration kept across versions.

**E2E forms** — web-ui: real browser, desktop + phone projects (E2E-6) · native-app E2E-11 · http-api E2E-12 · cli
E2E-13 · library E2E-14 · data-pipeline E2E-15 (`absd/playbook/testing/end-to-end-profiles.md`).

## Lanes

| Lane | When | Contents | Blocks |
|---|---|---|---|
| Push | every push, exact commit | every M or triggered R type (STRAT-7): e2e on every device/runtime project + the foreign zone/locale project · migrations from empty, from previous release, drift · secret canary · empty-infra boot · config agreement · smoke on the CI stack · traceability + plan conformance · coverage + no-untested-unit · static checks · changed-code mutation (or per cycle) | merge, Gate 3, deploy |
| Nightly | divergence hour or pinned midnights (STRAT-8); never deploys | whole suite in random order with parallel workers · repeat runs · live contracts · full mutation · performance at volume · load and soak · dependency scans | next cycle start, Mode R |
| Post-deploy | every deploy or publish | version-aware health · smoke (pipeline: isolated canary) · synthetic journey · error-rate watch; failure → automatic rollback | the release |
| Per cycle | Tester Verify | changed-code mutation (if not per push) · screenshot/golden gallery → Design QA · agent exploratory pass | Gate 3 |
| Release | Mode R | human exploratory on real devices · manual acceptance checklist · backup → restore drill | the release |
