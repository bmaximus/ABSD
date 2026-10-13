# Test strategy — types, applicability, suite shape

Code **STRAT**. Which kinds of test a product runs for its interface profiles (web-ui, native-app, http-api, cli,
library, data-pipeline), what each kind answers, where and when it runs, how that is decided once in `TESTING.md`, and
how tests are identified. Deriving cases: VAR in `absd/playbook/testing/test-design.md`. Expected values: ORACLE in
`absd/playbook/testing/oracles.md`. Thresholds, flake policy and gate mechanics: GATE in `absd/playbook/testing/gates.md`.

## Checklist

- [ ] `TESTING.md` has one row per matrix type: M/R/X per declared profile, home, command, lane — no blank cell (STRAT-1)
- [ ] Every home has run at a recorded commit; `test_plan.md` cites `TESTING.md` and re-argues nothing (STRAT-1)
- [ ] Several profiles: the strictest cell applies, and each profile's own form of the test exists (STRAT-2)
- [ ] Every R row names its triggering ids, or "no trigger" with the ids checked (STRAT-3)
- [ ] N/A only in X cells; an M turned N/A cites an ADR that passed Gate 2R (STRAT-4)
- [ ] No N/A rests on an invalid reason; the Auditor verified every N/A (STRAT-4)
- [ ] The End-to-end row uses the profile's E2E form, driving the shipped artifact (STRAT-5)
- [ ] Each rule is pinned at the lowest level that sees it AND where its user sees it (STRAT-6)
- [ ] End-to-end tests are not counted towards unit coverage gates (STRAT-6)
- [ ] The push lane holds every listed type and blocks merge, Gate 3 and deploy (STRAT-7)
- [ ] The nightly lane runs at a UTC/display-date divergence hour and never deploys; red or not run blocks (STRAT-8)
- [ ] Post-deploy smoke with automatic rollback; per-cycle and release lanes present (STRAT-8)
- [ ] No check moved to a slower lane without a user-approved Gate T amendment (STRAT-9)
- [ ] The push lane meets its wall-time budget without dropping cases (STRAT-9)
- [ ] Every REQ-NF has a measurable TC: dataset, environment, metric, threshold (STRAT-10)
- [ ] TC ids are flat `TC-nnnn`; level, purpose, device, lane and requirement ids are attributes (STRAT-11)
- [ ] Adoption/upgrade: existing suites mapped onto the matrix; missing M rows are DEBT, not N/A (STRAT-12)

## Rules

**STRAT-1** — Decide test applicability once per product, at Bootstrap, in `TESTING.md`: for every row of the
applicability matrix (below) record M/R/X per declared profile, the home (path, runner, command, report location) and
the lane; re-decide only in Mode C (a profile, external system or persistent store is added or removed) or Mode U.
`test_plan.md` cites the `TESTING.md` rows it relies on and never re-argues applicability. A home that has never run at
a recorded commit does not count as present (GATE-1).
- *Why:* the source product's whole suite was built later, outside the pipeline, because no one had decided which kinds
  of test it needed; re-arguing per cycle lets "N/A" be pasted forward (LL-27).
- *Check:* `TESTING.md` §1 has no blank cell; its git history shows edits only in Foundation, Mode C or Mode U cycles;
  every `test_plan.md` has an applicability citation and no per-cycle N/A argument.
- *Applies when:* always.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

**STRAT-2** — A product with several profiles applies, per row, the strictest cell of any declared profile
(M > R > X), and every declared profile still gets its own form of that test (an http-api black-box access test AND the
web-ui flow over the same data).
- *Why:* a web product's API is an interface of its own: free accounts received paid data in an API response no
  screen showed, so only a test of the API itself could see it (LL-10).
- *Check:* `TESTING.md` lists one home per (row × declared profile) where the cell is M or triggered R.
- *Applies when:* `context.md` declares more than one profile.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**STRAT-3** — An R cell becomes mandatory as soon as a requirement, business rule, REQ-NF or named RISK triggers it;
`test_plan.md` lists, per R row, the triggering ids and their TCs, or "no trigger" with the ids it checked.
- *Why:* a visual-regression requirement was written in every cycle and never automated (LL-53).
- *Check:* the Auditor searches `analysis.md`, `design.md` and the RISK register for performance, golden-output,
  accessibility, security and device terms and confirms each hit maps to an R row with TCs.
- *Applies when:* any R cell in the matrix for a declared profile.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10)

**STRAT-4** — Mark N/A only in X cells. An M cell becomes N/A only through an ADR that passed Gate 2R. Never valid:
slow, flaky, hard to set up, "covered by unit tests", "no UI" while another interface exists, "the environment cannot
run it" (that is a RISK and BLOCKED evidence, never a decision). The Auditor — not the Manager — verifies every N/A at
2R and at audit.
- *Why:* a sandbox that could not run the migration tool became an architecture instruction and test databases were
  auto-created for four cycles (LL-21); audits certified suites they never ran (LL-24).
- *Check:* the Auditor maps each N/A in `TESTING.md` and `test_plan.md` to an X cell or an ADR with a 2R PASS; an N/A
  on an invalid reason is a Major finding (L6).
- *Applies when:* always.
- *Provenance:* LL-21, LL-24 (KatenatsioTipster, 2026-10)

**STRAT-5** — Satisfy the End-to-end row only with the profile's E2E form (§ "Applicability matrix", E2E forms) driving
the shipped artifact through its real entry point; in-process, unit or mocked-boundary tests never stand in for it.
- *Why:* tests fed a computation its own inputs, so the component that misread a provider's field was on no tested
  path (LL-2).
- *Check:* each E2E home in `TESTING.md` names the form; the Auditor runs it and confirms it starts the built artifact
  (E2E-2).
- *Applies when:* always (the row is M for every profile).
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**STRAT-6** — Pin every behaviour at the lowest level that can observe it (rule → unit, boundary → integration,
external reading → contract) AND at the level where its user observes it (chain or end-to-end). Neither substitutes for
the other; end-to-end, device and browser tests never count towards unit coverage or the no-untested-unit gate (GATE-2).
- *Why:* a results reader with 0% coverage sat behind flows that "passed" (LL-2); a specified delete step was
  half-implemented while per-cycle checks passed (LL-51).
- *Check:* trace: each BR has a unit or integration TC and each AC/UJ an acceptance-level TC; the coverage gate's
  inputs exclude end-to-end reports.
- *Applies when:* always.
- *Provenance:* LL-2, LL-51 (KatenatsioTipster, 2026-10)

**STRAT-7** — Run the push lane on every push at the exact commit; it blocks merge, Gate 3 and deploy (§ "Lanes").
Every M or triggered R type is in it unless `TESTING.md` names another lane with a reason (cost, live credentials, real
devices), and such a type keeps its push-lane counterpart (recorded contract for live, emulated device for real device,
budget smoke for full performance); changed-code mutation runs per push or, at the latest, at Verify on the cycle HEAD.
- *Why:* booting the shipped artifact on empty infrastructure and migrating from empty were never run per push, so a
  missing-database crash and a schema missing ~60% of its columns surfaced only in audits (LL-14, LL-21).
- *Check:* the Tester-owned test workflows contain each push-lane job; the Auditor reconciles the `TESTING.md` lane
  column with workflow triggers.
- *Applies when:* always.
- *Provenance:* LL-14, LL-21 (KatenatsioTipster, 2026-10)

**STRAT-8** — Run the nightly lane (§ "Lanes") at an hour when UTC and the display zone are on different calendar
dates; it never deploys. A red or not-run nightly blocks the next cycle start (Mode D first) and Mode R. Every deploy
runs the post-deploy lane; every cycle runs the per-cycle lane; every release runs the release lane.
- *Why:* date bugs hide unless a run happens when dates differ (LL-40); a live job warned and exited 0 without its
  credential (LL-25); a health check passed while the page was blank (LL-32).
- *Check:* the nightly schedule, converted to the Locale & Time Profile zones, falls in a divergence window; the
  Manager's cycle-start record cites the last green nightly and live runs.
- *Applies when:* always; post-deploy whenever the product deploys or publishes.
- *Provenance:* LL-25, LL-32, LL-40 (KatenatsioTipster, 2026-10)

**STRAT-9** — Treat moving a check to a slower lane, sampling it, or dropping a device/runtime project from the push
lane as loosening a gate: it needs a Gate T amendment the user approved. Keep the push lane within the wall-time budget
recorded in `TESTING.md` by parallel workers, sharding, an isolated environment per worker and moving cases to a lower
level — never by dropping cases.
- *Why:* a lane quietly thinned for speed turns M cells into untested ones without any recorded decision.
- *Check:* `git diff` of test workflows and `TESTING.md` lane column against Gate T amendments; push-lane duration
  trend in CI.
- *Applies when:* always.
- *Provenance:* industry baseline

**STRAT-10** — Map every REQ-NF at Gate T to ≥1 TC with a measurable assertion: dataset (size and ordering, VAR-7),
environment, metric and threshold (e.g. "p95 ≤ 300 ms and ≤ 3 queries at 10 000 rows"). "Reviewed", "logic exists" or a
screenshot kept for humans is not a test.
- *Why:* measurable criteria (UTC offsets, idempotent re-runs, volume, midnights) passed audits by code reading
  (LL-45); visual regression was promised and never compared (LL-53).
- *Check:* trace_check REQ-NF → TC; each such TC asserts a number or an exact comparison.
- *Applies when:* any REQ-NF, including the default operability REQ-NFs.
- *Provenance:* LL-45, LL-53 (KatenatsioTipster, 2026-10)

**STRAT-11** — Give tests flat, product-scoped ids (`TC-nnnn`, ≥ 4 digits, never reused; next = highest in repo and
archive + 1). Level (unit · integration · contract · e2e), purpose (acceptance · access · chain · smoke · regression
`DEF-n` · nfr · char `INH-n` · a11y · visual · perf · security · migration), profile and device/runtime class, lane and
requirement ids are attributes — a name token or a report property (e.g. JUnit XML `<property>`, TRX trait) — never
parts of the id. A test moved to another level keeps its id.
- *Why:* a level inside the id forces a rename when an escaped defect moves a test to the level that should have caught
  it (ESC-1), and traceability breaks.
- *Check:* traceability_report rejects duplicate or malformed TC tokens; tokens and properties per TRACE rules in
  `absd/playbook/testing/traceability.md`.
- *Applies when:* always.
- *Provenance:* industry baseline

**STRAT-12** — In Mode B (adopt) and Mode U, map every existing suite onto the matrix (row → existing home or "none")
and record each M or triggered R row without a suite as DEBT with a burn-down; absence is a gap, never an N/A.
Inherited behaviour is pinned by CHAR tests (ORACLE rules).
- *Why:* fixes and the whole test suite were added outside any route, so nobody knew which kinds of test were missing
  (LL-27).
- *Check:* the Baseline section of `test_report.md` has one line per matrix row; each gap has a DEBT id in `context.md`.
- *Applies when:* brownfield adoption, v1 migration, kit upgrade.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

## Test types

| Type | Answers | Runs against | Lane | Rules |
|---|---|---|---|---|
| Unit | Is each rule right in isolation (calculation, decision, parsing, permission, validation)? | in-process; clock, ids, randomness injected | push | VAR, ORACLE |
| Integration | Does code behave on the real boundary (store built by shipped migrations, broker, fs, subprocess, request pipeline)? | real local dependencies; only external systems faked | push | INTEG |
| Contract — recorded | Do we read each external system right (format, zone, calendar, empty, errors, sync/async)? | committed real responses + independently checked facts | push | FAKE, EXT |
| Contract — live | Does the real system still answer as recorded? | live system, real credential (missing = RED) | nightly | FAKE, GATE-1 |
| Access & visibility | Does each principal get exactly the right status and data per operation? | running service | push | ACCESS |
| Chain | Does a real boundary payload reach the persisted and shown outcome through every step? | all real except the external system | push | INTEG, VAR-18 |
| End-to-end | Does each feature (functional) and each journey across roles (acceptance) work through the real interface? | shipped build, per device/runtime project | push | E2E |
| Acceptance traceability | Is each catalogue requirement verified, failing or untested? | the run's test reports | push | TRACE |
| Device / runtime | Does each supported class work as a target of its own? | one project per class; real devices at Mode R | push | VAR-6 |
| Accessibility | Can everyone operate it (scan + keyboard path)? | every rendered state | push | A11Y |
| Visual / golden + Design QA | Does it look or print exactly as designed? | screenshots, golden output/datasets | push; Design QA per cycle | VIS, DSN |
| Performance | Is it fast enough at Data Volume Profile max (latency, query count, size)? | production-volume data | push (budget) + nightly (full) | PERF |
| Security | Does it resist misuse beyond access rules (injection, secret canary, dependencies)? | code, artifacts, running service | push + nightly | SEC |
| Migrations / backup–restore | Does state survive migrate-from-empty, upgrade from previous release, drift, empty-infra boot, restore? | shipped artifact + real store | push; drill per release | INTEG, OPS |
| Smoke + rollback | Is the deployed system alive on the expected version; does failure roll back? | deployed system, read-only | push (CI stack) + every deploy | E2E, OPS |
| Regression | Did a change break what worked? A purpose tag, not a level: one test per escaped defect at the level that should have caught it | all levels | push + nightly | ESC-1 |
| Mutation | Can the tests fail? | changed code; money/time/access rules | push or Verify (changed) + nightly (full) | GATE-5, ORACLE |
| Characterization | What does inherited code do today? | existing code | Baseline, before touching it | ORACLE |
| Exploratory | What did nobody think to test? | running product (agent + human) | per cycle (agent), release (human, real devices) | EXPL |

## Applicability matrix

M mandatory · R required when a requirement, rule or named risk triggers it · X not applicable.

| Test type | web-ui | native-app | http-api | cli | library | data-pipeline |
|---|---|---|---|---|---|---|
| Unit | M | M | M | M | M | M |
| Integration (real boundary: DB, broker, fs, subprocess) | M | M | M | M | R (if it does I/O) | M |
| Contract (external systems)¹ | M | M | M | M | M | M (every source + sink) |
| Access & visibility (operation × principal) | M | M | M | R (credentials/profiles) | X | M (service identity × dataset) |
| Chain (outer boundary input → persisted + shown outcome) | M | M | M | M | R | M |
| End-to-end | M | M | M | M | M | M |
| Acceptance traceability | M | M | M | M | M | M |
| Device / runtime matrix | M (phone unless waived) | M | X | R (OS/shell/width) | M (runtime versions) | X |
| Accessibility (automated scan + keyboard) | M | M | X | R (NO_COLOR, no colour-only meaning) | X | X |
| Visual / golden output + Design QA | M | M | X | R (golden output) | X | R (golden datasets) |
| Performance budgets | R | R | R | R | R | R |
| Security tests (beyond access) | M | M | M | R | R | M |
| Migrations / backup–restore² | M | M | M | X | X | M |
| Post-deploy smoke + rollback | M | M (store/channel) | M | M (install + withdraw) | M (registry install + yank/patch) | M (canary/replay) |
| Exploratory (agent + human) | M | M | R | M | R (API usability) | M (output vs source of truth) |

¹ when the product talks to any external system, including deploy platforms, CI, mail, OCR/LLM, payment.
² when the product owns persistent state.

**E2E forms** — web-ui: real browser, desktop + phone projects · native-app: device/emulator automation per platform ·
http-api: black-box requests against the running service · cli: subprocess, args/stdin/env → stdout/stderr/exit
code/files, TTY and pipe · library: consumer code against the INSTALLED built package in a clean environment ·
data-pipeline: a recorded real-volume dataset through the real entry point, incl. replay, duplicates and late data.

## Lanes

| Lane | When | Contents | Blocks |
|---|---|---|---|
| Push | every push, exact commit | unit · integration · recorded contract · access + completeness · chain · e2e on every device/runtime project + the foreign zone/locale project · a11y · visual/golden · performance budgets · security tests + secret canary · migrations from empty, from previous release, drift · boot shipped artifact on empty infra · config agreement · smoke on the CI stack · traceability + plan conformance · coverage + no-untested-unit · static checks | merge, Gate 3, deploy |
| Nightly | at a UTC/display-date divergence hour; never deploys | whole suite in random order with parallel workers · repeat runs · live contracts · full mutation · performance at volume · dependency scans | next cycle start, Mode R |
| Post-deploy | every deploy or publish | version-aware health · read-only smoke · synthetic journey · error-rate watch; failure → automatic rollback | the release |
| Per cycle | Tester Verify | changed-code mutation (if not per push) · screenshot/golden gallery → Design QA · agent exploratory pass | Gate 3 |
| Release | Mode R | human exploratory on real devices · manual acceptance checklist · backup → restore drill | the release |
