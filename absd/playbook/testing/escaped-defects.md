# Escaped defects — every slip improves the tests

Code **ESC**. What happens when a defect gets past the check that should have caught it: the main rule, what counts as
an escape, the regression test and where it lives, the why-missed taxonomy, root-cause routing, the same-weakness sweep,
the log, closing the loop into the kit, recurrence, flakes and batching. Route: Mode D (`absd/RULES.md` §2). Log:
`ESCAPED-DEFECTS.md` (Tester; template `absd/templates/project/ESCAPED-DEFECTS.md`). User-visible regression tests:
E2E-17. Harvest: ENR-1. Over time the tests must catch what people used to find.

## Checklist

- [ ] Done only when: a test fails without the fix, the kind of test that missed it is fixed, swept, logged (ESC-1)
- [ ] Every escape is a DEF in `defect.md` on Mode D; nothing is fixed outside a mode (ESC-2)
- [ ] Regression test RED on the pre-fix commit, at the lowest level that shows the mechanism (ESC-3)
- [ ] Plus a regression test at the surface (screen, output, response) when it reached one (ESC-3)
- [ ] Title carries `(DEF-n, date: what broke)`, tag `regression`, TC id and requirement ids (ESC-3)
- [ ] Asserts the mechanism with a discriminating input; unreproducible trigger → mechanism + its undo (ESC-4)
- [ ] Why-missed: taxonomy class with evidence; a kind of test changed, not only a case added (ESC-5)
- [ ] Root-cause class proposed with artifact citations; the gate that should have stopped it named (ESC-6)
- [ ] Sweep over the whole repository: searches, hits and dispositions recorded; the Auditor reruns it (ESC-7)
- [ ] Log row added after Gate 3 with every column filled (ESC-8)
- [ ] Every log row closed in `lessons.md`: playbook change or enforcement change (ESC-9)
- [ ] A class seen before gets a mechanical control, not one more case (ESC-10)
- [ ] Pass-on-retry, order-only or parallel-only failure → DEF, reproduced deterministically, cause fixed (ESC-11)
- [ ] A batch holds only DEFs with one root-cause class and route; each keeps its own records (ESC-12)

## Rules

**ESC-1** — The main rule: an escaped defect is fixed only when (1) a test fails without the fix, (2) the reason the
existing tests missed it is named from the taxonomy below and that kind of test is fixed — not only a case added,
(3) the same weakness is searched for everywhere and covered, and (4) the slip is logged in `ESCAPED-DEFECTS.md` with
the ABSD gate or rule that should have caught it. Gate 3 of a Mode D cycle fails while steps 1–3 lack evidence; the
archive is refused until step 4's row exists.
- *Why:* about ten escapes in two days after go-live came from systemic test-design weaknesses — fakes answering the
  team's assumption, desktop-only runs, three-item lists, a reader no test ran — not from single missing cases (LL-1,
  LL-2, LL-4).
- *Check:* per DEF the Auditor finds red evidence at the pre-fix commit, a why-missed entry naming a changed kind of
  test, a sweep record and the log row (ESC-3, ESC-5, ESC-7, ESC-8).
- *Applies when:* every escaped defect, every profile, from the first one.
- *Provenance:* LL-1, LL-2, LL-4 (KatenatsioTipster, 2026-10)

**ESC-2** — Treat as an escape every defect found after the change that introduced it passed its own push lane: by a
user, the live system, an exploratory session outside the cycle's scope, the nightly or live lane, CI on a later
change, an audit, or reasoning. The Manager opens it as `DEF-n` in `defect.md` (found by, evidence, severity) and it
runs through Mode D, however small; nothing is fixed outside a mode. A failure caught by the change's own push lane or
by Verify is a TF of that cycle, not an escape.
- *Why:* a whole test suite and about a dozen fixes were made outside the pipeline, with no route, audit or record
  (LL-27); the one slip CI caught before release — a filter overwritten by a late reload — shows the target: the
  suite, not people, finds it (LL-20).
- *Check:* every commit on the default branch belongs to a cycle (`ABSD-Cycle` trailer, ownership_check); every closed
  DEF has a log row; EXPL-6 routes exploratory findings here.
- *Applies when:* always.
- *Provenance:* LL-27, LL-20 (KatenatsioTipster, 2026-10)

**ESC-3** — In Mode D Reproduce, write the regression test before any fix, at the lowest level that can show the
mechanism (STRAT-6) — unit for a rule, integration for a boundary, contract for an external reading, chain for a flow —
plus, when the defect reached a screen or other user-visible output, a regression test at that surface on the device
class, zone, locale and data volume where it slipped (E2E-17). Show each RED on the pre-fix commit for the stated
reason (ORACLE-3). Title it with the behaviour and `(DEF-n, YYYY-MM-DD: what broke)`, tag it `regression`, link the
requirement it protects and its `TC-nnnn` (STRAT-11, TRACE-3); a test moved to another level keeps its id.
- *Why:* a results reader with no test at all sat behind flows that passed (LL-2); a phone-only failure needed a test
  at phone size, not one more desktop test (LL-4).
- *Check:* red evidence per regression TC at the pre-fix SHA; its level matches the why-missed class; a surface test
  exists for every row marked "reached a surface".
- *Applies when:* every DEF.
- *Provenance:* LL-2, LL-4 (KatenatsioTipster, 2026-10)

**ESC-4** — Test the mechanism, not the symptom: assert the rule, mapping or conversion that was wrong, with an input
where the known-wrong reading gives a different answer (a provisional field read as the final one; an instant whose
provider-zone date differs from its UTC date). When the test environment cannot reproduce the trigger (a touch
gesture, an OS dialog, hardware, a store-channel install), assert the mechanism that prevents it, that the mechanism is
undone when it should be (lock → unlock), and the user-visible outcomes; say in the test which part is simulated.
- *Why:* scores chosen so that the wrong field gives a different settlement pinned the half-time misreading (LL-2);
  headless emulation cannot pull-to-refresh, so the fix's overscroll containment and page lock were asserted (LL-4).
- *Check:* adversarial probe — the Auditor reverts the fix in a throwaway worktree and the test fails; a symptom-only
  assertion ("no error shown") on a reproducible trigger is Major.
- *Applies when:* every regression test.
- *Provenance:* LL-2, LL-4 (KatenatsioTipster, 2026-10)

**ESC-5** — Name why the tests missed it: one primary taxonomy class per DEF (table below) and any secondary ones, each
with evidence — the fake, setting, device list, fixture, coverage line, oracle or catalogue gap that let it through
(path:line) — then fix that kind of test so the whole class is caught: the fake, the harness, the device projects, the
data volume, the gate or the plan template, and only then the case. "A case was missing" is not a class. Record it in
the DEF's Reproduce section of `test_plan.md`.
- *Why:* fakes answered as the team assumed, so the real fix was the fakes' fidelity plus contract tests, not one more
  test in the right zone (LL-1); the same fakes also served a day the feed never serves (LL-3).
- *Check:* the log's "How the tests improved" names a fake, harness, project, volume, gate or template change besides
  the new TCs; the Auditor checks the evidence path shows the weakness.
- *Applies when:* every DEF.
- *Provenance:* LL-1, LL-3 (KatenatsioTipster, 2026-10)

**ESC-6** — Propose the root-cause class with artifact citations, so the Manager routes without judging technology:
implementation (code ≠ architecture: section + diverging line) · architecture gap (blueprint silent or wrong) · UX
gap (`design.md` silent or wrong) · requirements gap (no catalogue entry, empty actor × capability cell, inherited
behaviour never decided) · test-only gap (product meets its spec; only the tests missed it). Name the gate whose
checklist should have stopped it and the ABSD rule, or "none — gap" when no rule covers it.
- *Why:* admins who could not take part and a "clear all" that filled blank rows were requirement gaps; a code fix and
  a test alone would have left the catalogue wrong (LL-5, LL-6).
- *Check:* Mode D Gate T reads one class per DEF with citations; a requirements gap routed straight to the Builder is a
  Major process finding.
- *Applies when:* every DEF.
- *Provenance:* LL-5, LL-6 (KatenatsioTipster, 2026-10)

**ESC-7** — Sweep for the same weakness over the whole repository — production code, tests, fakes, settings, docs —
never a narrowed scope: from the class's sweep column list each search run (pattern or report, tool, scope), every hit
and its disposition: already covered (TC), covered now (new TC this cycle), or a new DEF (non-Critical → backlog;
Critical → this cycle with the user's agreement). After the fix the Auditor reruns the searches and checks every
disposition.
- *Why:* the sweep after the unread reader found six more units no test ran, from backup restore to password reset
  (LL-2); after an integration was replaced a status card still named the old one (LL-17); a narrowed audit search let
  a secret survive outside it (LL-43).
- *Check:* the Auditor's rerun finds no hit missing from the record; the log's sweep cell names what was found.
- *Applies when:* every DEF.
- *Provenance:* LL-2, LL-17, LL-43 (KatenatsioTipster, 2026-10)

**ESC-8** — Log every escape after Gate 3: the Tester adds one row per DEF to `ESCAPED-DEFECTS.md` (living, never
archived, newest first) with every column of the log format below filled; an empty finding says what was searched
("none found: …"), never a blank cell. Rows are never edited afterwards except to add the lesson and LL ids.
- *Why:* an order-dependent ranking regression was fixed but never logged, so its class left no trace for the next
  sweep (LL-49).
- *Check:* every DEF closed in Mode D has a row; its TC ids exist in the test tree; the Manager's archive step refuses
  a closed DEF without one.
- *Applies when:* every DEF.
- *Provenance:* LL-49 (KatenatsioTipster, 2026-10)

**ESC-9** — Close the loop at Harvest (Mode H): the Manager adds an `absd-project/lessons.md` row per new log row and
closes it with exactly one of: a playbook change proposed to ABSD through enrichment (a new or amended rule, taxonomy
class or checklist item; ENR-1), or "rule existed, not followed → enforcement change" — the gate, lint, hook, fixture
or template that makes the rule mechanical, with its commit. The log's last column cites the lesson id, then the LL id
once accepted; the kit maintainer counts the escape on the LEDGER scoreboard under the gate that missed it.
- *Why:* an escape log that names only the product's own test fix leaves the kit unchanged, so the next product
  repeats the class; a rule that relies on discipline fails again the same way.
- *Check:* archive is refused while a log row lacks a lesson id; the lesson's status is proposed, sent or accepted, or
  names the enforcement commit.
- *Applies when:* every Harvest.
- *Provenance:* industry baseline

**ESC-10** — Escalate recurrence: when a row's primary class already appears in an earlier row of this log or on the
LEDGER, the fix must be mechanical — a gate, lint, generator, shared fixture, fake-parity test or plan-template item
that fails on the whole class — and the row reports "rule existed, not followed" against that rule.
- *Why:* one class — a fake answering as the team assumed — escaped three times: a time zone, a calendar, and a
  deploy platform faked as synchronous (LL-1, LL-3, LL-7).
- *Check:* the Auditor groups log rows by class; a repeated class without a mechanical control in the same DEF is
  Major.
- *Applies when:* every DEF whose class recurs.
- *Provenance:* LL-1, LL-3, LL-7 (KatenatsioTipster, 2026-10)

**ESC-11** — Treat a flaky test as a defect: a pass-on-retry (GATE-6), a failure only in the random-order, repeated or
parallel nightly run, or only on one host opens a DEF in Mode D. Reproduce it deterministically first — replay the
printed order seed, repeat, parallelize, hold the response, pin the clock — and classify it: a product race (VAR-12
test, Builder fix) or a test defect (isolation, waits, injected time, unique data: TCQ rules in
`absd/playbook/testing/test-code.md`). Never retry, quarantine, skip or lengthen a timeout to get green (TCQ-1).
- *Why:* one silent retry turns a flaky proof green and the acceptance report counts it as verified; a visibility test
  passed only because the runner happened to order it first.
- *Check:* the flake report in `test_report.md` maps each retried test to a DEF; the DEF's red evidence is the
  deterministic reproduction.
- *Applies when:* any pass-on-retry, order-only, parallel-only or host-only failure.
- *Provenance:* industry baseline

**ESC-12** — Batch in one `defect.md` only DEFs with the same root-cause class and route; each keeps its own regression
tests, why-missed entry, sweep record and log row. Sweep findings that are not Critical become new DEFs on the backlog,
never scope growth; a batch whose items turn out to need different routes is split at Gate T.
- *Why:* the only route was the heavy feature route, so a day of escapes was fixed outside the pipeline (LL-27).
- *Check:* Mode D Gate T: one class and one route per `defect.md`; one log row per DEF.
- *Applies when:* Mode D with more than one DEF.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

## Why-missed taxonomy

| # | Class | Signature (what you find) | Fix that kind of test · sweep for | Rules |
|---|---|---|---|---|
| 1 | Assumption-fed fake | Fake answers in the assumed format, zone, calendar or timing; no recording behind it (LL-1, LL-3, LL-7) | Fake from recorded real answers + contract TC + parity check · every fake vs `EXTERNAL-FACTS.md` | FAKE-1, FAKE-2, EXT-3 |
| 2 | Test-only override of a world fact | Test settings set a zone, format, calendar or other world fact the product does not ship with (LL-1) | Delete it; shipped settings; overrides register · every override in test settings | FAKE-4, FAKE-3 |
| 3 | Single device class | Fails on a device, runtime, OS, shell or width no project runs (LL-4, LL-16) | Project per class, journeys run there · journey × device list | VAR-6, E2E-6 |
| 4 | Tiny or friendly-ordered data | 1–3 items; the special item first (LL-4) | Data Volume Profile max, adversarial order · every fake and seed vs the profile | VAR-7, DSN-11 |
| 5 | Unit no test runs | Unit at 0% in the coverage report (LL-2) | No-untested-unit gate; unit + contract TCs · the whole report | GATE-2, GATE-3 |
| 6 | Oracle derived from code | Expected value from a production call, constant or pasted output; wrong rule asserted (LL-48) | Re-derive from spec; mutation on the rule · expected sides naming production symbols | ORACLE-1, ORACLE-4, ORACLE-14 |
| 7 | Test fed its own inputs | Downstream tested with hand-made values; the reader or adapter never in the path (LL-2) | Chain test from a recorded payload to stored + shown outcome · every flow without one | INTEG-10, VAR-18 |
| 8 | Missing requirement | No catalogue entry or AC; empty actor × capability cell (LL-5, LL-18) | Requirements route; acceptance TC · matrix cells, role value check | TRACE-1, ELIC (`absd/playbook/process/requirements.md`) |
| 9 | Unspecified inherited behaviour | Prototype or legacy behaviour kept, never decided (LL-6, LL-50) | INH item decided by the user; CHAR then spec TC · inherited controls on touched surfaces | ORACLE-12 |
| 10 | Unverified external fact | Fact from a person, a document or a default; no recording (LL-1, LL-2) | Fact row, flag off and fail closed until VERIFIED · every fact without evidence | EXT-1, EXT-2, EXT-4 |
| 11 | Interacting rules untested | Each rule passes alone; the combination is wrong (LL-9) | Decision table; state × event incl. reordering · rules sharing a state or order | VAR-4, VAR-5 |
| 12 | Payload not asserted | Status or count asserted; wrong data in the body (LL-10) | Records and fields asserted, forbidden ones absent · status-only assertions | ACCESS-3, ORACLE-9 |
| 13 | Idle or real-time behaviour untested | Tests act and finish at once; timers, polling, re-render loops unseen (LL-12) | Idle budget; dialog outlives the longest timer; real-time lifecycle · every timer and poll | VAR-17, E2E-8, DSN-12 |
| 14 | Foreign zone or locale untested | Runs only in the audience's zone and locale; host-zone reliance hidden (LL-13) | Foreign zone/locale project; boundary instants · every date, time and number formatter | VAR-8, E2E-7, LOC-5 |
| 15 | Race or late response | An action inside a debounce or latency window is lost (LL-20) | Deterministic race TC with held responses · every debounced or async input | VAR-12 |
| 16 | Environment limitation turned into design | "Cannot run X here" became "do not do X"; store auto-created (LL-21) | RISK + BLOCKED evidence; store via migrations; migration gates · specs and harness workarounds | INTEG-2, GATE-12, GATE-1 |
| 17 | Retry-to-green flake | Passes on retry; fails only in random order, repeated or parallel | Retries 0; random + parallel nightly; isolation fixed (ESC-11) · retry report, nightly seeds | GATE-6, GATE-9, INTEG-4 |
| 18 | Default-config path never run | Shipped defaults, flag-off path or first start never executed (LL-14, LL-22, LL-23) | Shipped artifact on empty infrastructure; both flag states · every flag and default | OPS-1, VAR-19, FAKE-4 |
| 19 | Docs drift | Run guide, examples or comments contradict the product (LL-17, LL-22) | Fresh clone → running from the docs; config agreement · docs, examples, env templates | OPS-6, FAKE-3, EXT-5 |
| 20 | Check that did not run | Required job skipped, credential missing, exit 0 with a warning (LL-24, LL-25) | Missing = RED; "input missing" negative control · every job's run conditions | GATE-1, GATE-8 |
| 21 | Assertion that cannot fail | `> 0`, loose range, broad pattern, symptom only; mutants survive | Discriminating oracle; mutation on the rule · surviving mutants, weak matchers | ORACLE-9, GATE-5 |
| 22 | Specified step untested | One step of a flow half-done while the flow passes (LL-51) | Test per step on the persisted end state · every numbered flow step | INTEG-11 |

A defect fitting no class gets "new class" plus a proposed row; ESC-9 sends it to the kit.

## Log format (`ESCAPED-DEFECTS.md`)

| Column | Write |
|---|---|
| DEF | `DEF-n` (its `defect.md` lives in the cycle archive) |
| Date | the date it was found |
| What slipped | symptom and impact in the user's terms; "dormant" if a flag or default hid it |
| Found by | user · live system · exploratory · nightly or live lane · CI on a later change · audit · reasoning |
| Why the tests missed it (taxonomy) | primary class `#n name`, secondary classes, evidence path |
| How the tests improved | the kind of test changed (fake, harness, project, volume, gate, template) + regression TC ids |
| Same weakness looked for elsewhere | searches, hits and new DEF ids — or "none found: <searches>" |
| ABSD gate/rule that should have caught it | gate or lane (Gate 1, UX, 2, 2R, T, 3; push, nightly) + `ABSD:CODE-n`, or "none — gap" |
| Lesson / rule changed | `<slug>-L<n>` → `LL-n`, or "enforcement: <control, commit>" |
