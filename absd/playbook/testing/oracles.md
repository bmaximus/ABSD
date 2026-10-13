# Oracles — where expected values come from

Code **ORACLE**. The source, form and life of every expected value: allowed sources and their precedence, independent
calculation, red before green, amendments and disputes, characterization of inherited behaviour, and how mutation
testing proves that oracles can fail. Which cases to write: VAR (`absd/playbook/testing/test-design.md`); mutation
thresholds and flake policy: GATE (`absd/playbook/testing/gates.md`); external facts: FAKE, EXT
(`absd/playbook/testing/contracts-and-fakes.md`).

## Checklist

- [ ] Every TC row in `test_plan.md`: concrete inputs → concrete expected values → allowed source (ORACLE-1)
- [ ] No oracle comes from code, its output, a log or a person's word about an external system (ORACLE-1)
- [ ] Every expected value changed since T-SHA cites an approved Gate T amendment (ORACLE-2)
- [ ] Every new TC was RED for its stated reason before code; evidence attached (ORACLE-3)
- [ ] No expected value or arranged input comes from calling production code (ORACLE-4)
- [ ] Snapshot/golden files are oracles only after their owner approved them (ORACLE-4)
- [ ] Money/time/ranking oracles show worked arithmetic or an outside reference (ORACLE-5)
- [ ] Computational ACs carry worked numbers and inclusivity; gaps are blocking spec defects (ORACLE-6)
- [ ] Business oracles cite analysis/design, never architecture; conflicts raised, not resolved (ORACLE-7)
- [ ] Every failing TC and TC-CONFLICT has exactly one class and a route (ORACLE-8)
- [ ] Assertions are strong: whole record, exact money, which rule failed, forbidden data absent (ORACLE-9)
- [ ] Relational oracles only in addition to literals on money/time/ranking/access paths (ORACLE-10)
- [ ] FACT oracles only from VERIFIED facts; UNVERIFIED → fail-closed behaviour asserted (ORACLE-11)
- [ ] CHAR tests labelled, tied to INH ids, never specification before the user decides (ORACLE-12)
- [ ] Tests written after the code are shown able to fail (ORACLE-13)
- [ ] Every surviving mutant on money/time/access is killed by a spec-sourced TC or justified (ORACLE-14)

## Rules

**ORACLE-1** — Take every expected value from an allowed source and cite it in the oracle table (TC → concrete inputs →
concrete expected values → source): `SPEC:<ID>.AC<n>` or a `design.md` id for business and experience behaviour;
`SPEC:architecture §x` only for internal units with no business meaning; `FACT:EXT-<SYS>-<n>` for what an external
system does; `CHAR:INH-<n>` only for inherited behaviour the user confirmed. Code, its current output, logs, the
Builder's explanation and a person's statement about an external system are never sources. Every money, time and
ranking oracle shows an independent calculation (ORACLE-5).
- *Why:* oracles written after and from the code made every cycle need a second build (LL-29); a field's meaning taken
  from a person's word shipped a dormant blocker (LL-2); measurable criteria passed audits by code reading (LL-45).
- *Check:* trace_check: every TC row has a source of an allowed form whose id exists; the Auditor checks 100% of
  money/time/access oracles and a sample of the rest against the cited text (L6).
- *Applies when:* always.
- *Provenance:* LL-2, LL-29, LL-45 (KatenatsioTipster, 2026-10)

**ORACLE-2** — Change an oracle only through a Gate T amendment in `test_plan.md` (TC, old → new expected value, reason,
new source, Manager approval line). Disputes follow the citation: a failing TC goes to the owner of its cited source
(Analyst for analysis, Designer for design, Architect for architecture, Tester for EXT facts, the user for CHAR), never
to whoever finds the test inconvenient. The Builder never edits a test; the Tester never edits an expected value to
match the code without an amendment.
- *Why:* a test asserted the wrong behaviour — keeping client-declared figures against an earlier rule — and an audit
  rationalized it (LL-48); oracles bent to the code cannot catch it (LL-29).
- *Check:* the Auditor diffs `<T-SHA>..HEAD` over the Tester's globs: every changed expected value or assertion maps to
  an approved amendment, else Major (Q1); ownership_check shows no Builder commit on test paths.
- *Applies when:* every TC after Gate T, in every mode.
- *Provenance:* LL-29, LL-48 (KatenatsioTipster, 2026-10)

**ORACLE-3** — Show every new test RED for its stated reason before the production code exists: run it at T-SHA and
attach the output under `evidence/`; the failure must be the asserted behaviour missing or wrong (assertion failure,
unknown route, missing command, absent field). A compile or import failure counts only for types or symbols that
`architecture.md` lists as new. A test that passes before the code exists, or fails for another reason, is repaired
before Gate T.
- *Why:* tests specified by the architecture and written by the code's author after the code were never seen failing
  (LL-29); criteria nobody turned into failing tests passed as "satisfiable" (LL-45).
- *Check:* Gate T: red evidence per new TC; the Auditor confirms `test_plan.md` and the red tests are ancestors of the
  first production commit and that each red reason matches its TC.
- *Applies when:* Plan & Bind (Modes F, S) and Reproduce (Mode D).
- *Provenance:* LL-29, LL-45 (KatenatsioTipster, 2026-10)

**ORACLE-4** — Never compute an expected value by calling production code: not directly, not through a production
helper or constant, not through a copy of the production formula, not by running the system and pasting its output,
and not by arranging the inputs under test with production functions (e.g. deriving a field with the production
calculator, then asserting on it). The expected side is a literal from the oracle table or an independent reference;
limits are asserted as the spec states them (5 MiB), not as `MAX + 1`. Snapshot and golden files are oracles only once
their owner approved them against the spec (Designer for screens and output, Analyst for datasets); re-recording a
snapshot to get green is changing an oracle (ORACLE-2).
- *Why:* downstream tests were fed the computation's own outputs, so a misreading component stayed invisible (LL-2).
- *Check:* the Auditor greps expected sides and arrange blocks on money/time/ranking/access paths for production
  symbols (L6); any hit without a recorded reason is Major.
- *Applies when:* always; strictest on money, time, ranking and access.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**ORACLE-5** — Derive money, time and ranking expectations by an independent calculation and show it: worked arithmetic
in the oracle table and as a comment beside the assertion (`// 3 × 19.99 = 59.97; × 0.90 = 53.973 → 53.97`), or a
reference outside the system — a published table, an official schedule, a calculation by another party, the fake's
ground-truth record of what it served. Disagreement with the Analyst's worked example is a spec defect that blocks
Gate T; the Tester never picks a side.
- *Why:* prize positions after a disqualification were wrong in a way only a hand calculation of the interacting rules
  exposed (LL-9).
- *Check:* each money/time/ranking TC carries a derivation; the Auditor recomputes three fresh cases per money/time BR
  from `analysis.md` as adversarial probes.
- *Applies when:* money, prices, quotas, scores, rankings, dates and durations.
- *Provenance:* LL-9 (KatenatsioTipster, 2026-10)

**ORACLE-6** — Consume worked-number acceptance criteria verbatim: each computational AC and BR carries concrete inputs
and outputs ("pool 1000 split 50/30/20 → 500/300/200"; "12 entries over 6 days vs minimum 10/5 → qualified"), and each
threshold states its inclusivity. Missing numbers, missing inclusivity or arithmetic that does not add up is a blocking
spec defect routed to the Analyst; the Tester does not invent the business answer.
- *Why:* measurable criteria (offsets, re-runs, volume, midnight boundaries) existed but nobody turned them into
  expected values (LL-45).
- *Check:* every TC citing a computational AC reuses its numbers; the spec-defect list in `test_plan.md` is empty of
  blocking items at Gate T.
- *Applies when:* every computational rule, threshold or time boundary.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10)

**ORACLE-7** — Apply source precedence: VERIFIED external facts decide what external systems do; `analysis.md` with
recorded gate decisions and existing catalogue invariants decides business behaviour; `design.md` decides experience
(copy, states, formats, focus); `architecture.md` decides only addresses (routes, signatures, payload shapes, error
codes) and internal units. When sources disagree — architecture vs analysis, a new rule vs an existing invariant,
design vs analysis — raise a spec defect to their owners; never build the oracle from the lower or the newer text alone.
- *Why:* a Gate 1 decision ("missing numbers fail validation") was reversed by an architecture note and every gate passed
  (LL-44); a test encoded a rule contradicting an earlier business rule (LL-48).
- *Check:* no business TC cites `SPEC:architecture`; spec defects in `test_plan.md` are resolved before Gate T.
- *Applies when:* always.
- *Provenance:* LL-44, LL-48 (KatenatsioTipster, 2026-10)

**ORACLE-8** — Classify every failing TC and every TC-CONFLICT, with evidence, into exactly one class in
`test_report.md`: product defect (TF → Builder fix, counts as an iteration) · spec defect (→ owner of the cited source,
then amendment) · obsolete oracle (amendment citing the changed requirement; none exists → Analyst or user) · harness
defect (test code fixed, expected value unchanged) · flaky (root cause under GATE-6; never skipped, TCQ-1).
- *Why:* when the party that can only edit tests triages failures alone, "fix the test to match the code" becomes the
  default (LL-29).
- *Check:* every red TC in the report has one class and a route; harness fixes leave expected values byte-identical.
- *Applies when:* Verify, Reproduce, every TC-CONFLICT.
- *Provenance:* LL-29 (KatenatsioTipster, 2026-10)

**ORACLE-9** — Make every oracle discriminating: assert the whole result record of a calculation, exact decimal money,
a tolerance only where the spec states a precision, which rule failed (error code or field) rather than "invalid", the
status AND the returned records and fields (ACCESS-3), forbidden data asserted absent, exact copy from `design.md` for
user-facing text, the full order of a list, and side effects with actor and count.
- *Why:* access was checked by status code while paid data travelled in the body (LL-10).
- *Check:* the Auditor flags single-field assertions on multi-output calculations, bare "is invalid" checks, and
  status-only access tests.
- *Applies when:* always.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**ORACLE-10** — Use relational oracles — invariants (`net = gross − fees`), metamorphic relations (VAR-16),
properties (VAR-15) — in addition to literal oracles, never instead of them on money, time, ranking or access paths; each
relation cites the rule it comes from.
- *Why:* only a permutation relation exposed entrants ranked by input order (LL-49), yet a relation alone accepts
  consistently wrong totals.
- *Check:* every money/time/ranking/access TC set contains at least one literal-oracle case.
- *Applies when:* derived values with algebraic relations; unordered inputs; generated inputs.
- *Provenance:* LL-49 (KatenatsioTipster, 2026-10)

**ORACLE-11** — Build FACT oracles only from VERIFIED external facts (recorded real response + independent source,
EXT-2). While a fact is UNVERIFIED, the test asserts the fail-closed behaviour — feature disabled, operation refused with
the designed message (EXT-1) — never the assumed value, and the fake never serves the assumption as truth (FAKE-1).
- *Why:* fakes served the team's assumed zone and every test passed while deadlines were hours late (LL-1); "the owner
  confirmed" a field's meaning (LL-2); the provider's served days were never checked (LL-3).
- *Check:* every `FACT:` source resolves to a VERIFIED entry in `EXTERNAL-FACTS.md`; each UNVERIFIED fact has a
  fail-closed TC.
- *Applies when:* the product talks to any external system.
- *Provenance:* LL-1, LL-2, LL-3 (KatenatsioTipster, 2026-10)

**ORACLE-12** — Before changing inherited code (brownfield adoption, a port, prototype code), pin its observable
behaviour with characterization tests labelled `CHAR` and tagged with their `INH-n`. They are change detectors, not
specification: a failing CHAR test routes to the Analyst and the user, never to a silent edit. The user decides each INH
item: Keep → a requirement, and the test becomes a normal TC citing it; Change or Remove → the test is replaced by
amendment; Unknown → asked before build. A suspected bug on a money, time, access or data-integrity path is never kept
"for parity".
- *Why:* a prototype's "clear all" behaviour shipped unspecified (LL-6); a suspected bug in a legacy formula was ported
  verbatim (LL-50).
- *Check:* the Baseline report pairs CHAR TCs with INH ids; no TC cites `CHAR:INH-n` unless INH-n is user-confirmed Keep.
- *Applies when:* Mode B adoption, ports, rewrites, behaviour copied from a prototype or spreadsheet.
- *Provenance:* LL-6, LL-50 (KatenatsioTipster, 2026-10)

**ORACLE-13** — Show every test written after the code exists — Verify white-box unit tests, CHAR tests, sweep tests,
gate negative controls — able to fail: a killed mutant on the asserted lines, or a negative control (inject the fault in
a throwaway worktree, run, see red, leave the tree byte-identical), with the output attached.
- *Why:* tests that have never failed may assert nothing; tests written after the code were never seen red (LL-29).
- *Check:* `test_report.md` links one red run or killed mutant per such TC.
- *Applies when:* Verify, Baseline, sweeps, Foundation gate negative controls.
- *Provenance:* LL-29 (KatenatsioTipster, 2026-10)

**ORACLE-14** — Measure oracle strength with mutation testing (e.g. Stryker, PIT, mutmut) on changed code and on every
money, time and access rule: each surviving mutant is killed by a new TC whose expected value has a spec source — never
the mutant's or the code's output — or recorded as equivalent with a reason. Typical survivors: `>=`→`>`, rounding mode,
removed tie-break, removed branch, swapped precedence. Thresholds per GATE-5.
- *Why:* coverage shows lines ran, not that any assertion would notice them being wrong.
- *Check:* the mutation report in `test_report.md` lists survivors with their resolution; the Auditor samples them.
- *Applies when:* every Verify; money, time and access rules always.
- *Provenance:* industry baseline

## Oracle table (in `test_plan.md`)

| TC | Inputs | Expected | Source | Derivation |
|---|---|---|---|---|
| TC-0042 | 3 × unit price 19.99, discount 10 %, half-up to cents | total 53.97 | `SPEC:ORD-BR-3.AC2` | 3 × 19.99 = 59.97; × 0.90 = 53.973 → 53.97 |
| TC-0043 | event at 2026-03-28T23:30Z; display zone UTC+1, UTC+2 from 2026-03-29T01:00Z | listed under 29 March | `SPEC:CAL-4.AC1` | 23:30Z + 1 h = 00:30 on 29 March local; UTC date is 28 March |
| TC-0044 | provider record with local time 20:00 at UTC+8 | stored instant 12:00Z | `FACT:EXT-FEED-2` | 20:00 − 8 h = 12:00Z; checked against the provider's published schedule |
