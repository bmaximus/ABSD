# Oracles — where expected values come from

Code **ORACLE**. The source, form and life of every expected value: allowed sources and their precedence, independent
calculation, red before green, amendments and disputes, characterization of inherited behaviour, and mutation as
proof that oracles can fail. Which cases to write: VAR (`absd/playbook/testing/test-design.md`); mutation
thresholds and flake policy: GATE (`absd/playbook/testing/gates.md`); fakes: FAKE
(`absd/playbook/testing/contracts-and-fakes.md`); external facts: EXT (`absd/playbook/testing/external-facts.md`).

## Checklist

- [ ] Every TC row: concrete inputs → concrete expected values → a prefixed source that resolves (ORACLE-1)
- [ ] No oracle comes from code, its output, a log or a person's word about an external system (ORACLE-1)
- [ ] Every expected value changed since T-SHA cites an approved Gate T amendment (ORACLE-2)
- [ ] Every new TC RED for its stated reason at the tests commit; the evidence commit is T-SHA (ORACLE-3)
- [ ] Red isolated by WP: compile/collection red only in a unit keyed to the WP adding the symbol (ORACLE-3)
- [ ] No expected value or arranged input comes from calling production code (ORACLE-4)
- [ ] Golden files: Designer-approved (human-facing output) or citing an Analyst example table (ORACLE-4)
- [ ] Money/time/ranking oracles show worked arithmetic or an outside reference (ORACLE-5)
- [ ] Computational ACs carry worked numbers and inclusivity; gaps are blocking spec defects (ORACLE-6)
- [ ] Business oracles cite analysis/design, never architecture; conflicts raised, not resolved (ORACLE-7)
- [ ] Every failing TC and TC-CONFLICT has exactly one class and a route (ORACLE-8)
- [ ] Mode D Gate T: one class per DEF; each TC red or `binds at re-bind` (ORACLE-8)
- [ ] Assertions are strong: whole record, exact money, which rule failed, forbidden data absent (ORACLE-9)
- [ ] Relational oracles only in addition to literals on money/time/ranking/access paths (ORACLE-10)
- [ ] FACT oracles only from VERIFIED facts; UNVERIFIED → fail-closed behaviour asserted (ORACLE-11)
- [ ] CHAR tests labelled, tied to INH ids, never specification before the user decides (ORACLE-12)
- [ ] Tests written after the code shown able to fail; faults injected outside the project (ORACLE-13)
- [ ] Every surviving mutant on money/time/access is killed by a spec-sourced TC or justified (ORACLE-14)
- [ ] A rule implemented in several tiers reads one shared golden-vector file (ORACLE-15)

## Rules

**ORACLE-1** — Take every expected value from an allowed source and cite it with its prefix in the oracle table (TC →
concrete inputs → concrete expected values → source): `SPEC:<REQ>[.ACn]` — business behaviour from the requirement
source (`analysis.md`; Mode S/D: `brd.md`, `defect.md`) or the catalogue, incl. an Analyst example table of expected
output; `SPEC:<UJ-n|SCR-n>[.<state>]` — experience in `design.md`; `SPEC:architecture §x` — internal units only, on
rows citing no requirement; `FACT:EXT-<SYS>-n` — VERIFIED external facts (ORACLE-11); `CHAR:INH-n` — inherited
behaviour the user confirmed (ORACLE-12). Code, its output, logs, the Builder's explanation and a person's statement
about an external system are never sources; money, time and ranking oracles show an independent calculation (ORACLE-5).
- *Why:* oracles written after and from the code made every cycle need a second build (LL-29); a field's meaning taken
  from a person's word shipped a dormant blocker (LL-2); measurable criteria passed audits by code reading (LL-45); a
  check of the prefix alone let invented ids and unverified facts pass as sources (LL-57).
- *Check:* `trace_check gate gateT` resolves each source (SPEC in the requirement source, catalogue or `design.md`;
  FACT VERIFIED in `--external-facts`, form only without a register; CHAR to an INH id of the requirement source) and
  rejects `SPEC:architecture` on a row citing a requirement; the Auditor checks the cited text supports the value —
  100% of money/time/access oracles, a sample of the rest (L6).
- *Applies when:* always.
- *Provenance:* LL-2, LL-29, LL-45 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ORACLE-2** — Change an oracle only through a Gate T amendment in `test_plan.md` (TC, old → new expected value, reason,
new source, Manager approval line). Disputes follow the citation: a failing TC goes to the owner of its cited source
(Analyst for analysis, Designer for design, Architect for architecture, Tester for EXT facts, the user for CHAR), never
to whoever finds the test inconvenient. The Builder never edits a test; the Tester never edits an expected value to
match the code without an amendment.
- *Why:* a test asserted a rule contradicting an earlier one and an audit rationalized it (LL-48); oracles bent to the
  code cannot catch it (LL-29).
- *Check:* the Auditor reviews every test change `ownership_check.py --t-sha <first> --t-sha <amendment> …` lists for
  the `cycle.md` chain: each changed expected value or assertion maps to an approved amendment, else Major (Q1); no
  Builder commit touches test paths.
- *Applies when:* every TC after Gate T, in every mode.
- *Provenance:* LL-29, LL-48 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

**ORACLE-3** — Show every new test RED for its stated reason before the production code exists: commit the tests and
plan, run them at that commit, commit the output under `absd-project/working/evidence/tester/` with plan §14 — that
evidence commit is T-SHA; each approved amendment or re-bind repeats this and appends its T-SHA to the `cycle.md` chain.
Red means the asserted behaviour missing or wrong (assertion failure, unknown route, missing command, absent field).
Isolate red by work package: tests touching a symbol new in WP-n sit in a compilation or collection unit keyed to WP-n
(own test project, module or file, or imports inside the test body), mapped unit → WP in plan §12; a compile or
collection failure is red evidence only there; every other unit compiles and stays green at T-SHA, and a new TC
arranges its own data, never in the shared seed. A test that passes before the code exists, or fails for another
reason, is repaired before Gate T. Mode D exception: `binds at re-bind` (ORACLE-8).
- *Why:* tests written by the code's author after the code were never seen failing (LL-29); criteria nobody turned
  into failing tests passed as "satisfiable" (LL-45); evidence could not be "run at T-SHA" inside T-SHA itself (LL-55);
  one missing symbol broke a whole compiled test project (LL-57).
- *Check:* Gate T: red evidence per new TC, its reason matching the TC; plan §12 maps units to WPs, all others green at
  T-SHA; the Auditor confirms the first T-SHA is an ancestor of every production commit (`ownership_check.py --t-sha`).
- *Applies when:* Plan & Bind (Modes F, S), Reproduce (Mode D), every approved amendment and re-bind.
- *Provenance:* LL-29, LL-45 (KatenatsioTipster, 2026-10); LL-55, LL-57 (ABSD v2 kit review, 2026-10)

**ORACLE-4** — Never compute an expected value by calling production code — directly, through a production helper,
constant, copy or re-implementation of its algorithm, by pasting the running system's output, or by arranging the
inputs under test with production functions (deriving a field with the production calculator, then asserting on it).
The expected side is a literal from the oracle table or an independent reference; a limit's value comes from the spec
(5 MiB), not from the production constant. Snapshot and golden files are oracles only once approved against the spec:
the Designer approves human-facing output (screens, cli output, reports, rendered documents); any other golden file
(datasets, machine formats) cites the Analyst's example table of expected output for its recorded input in
`analysis.md` (`SPEC:`). Re-recording one to get green changes an oracle (ORACLE-2).
- *Why:* downstream tests were fed the computation's own outputs, so a misreading component stayed invisible (LL-2);
  one pipeline's golden dataset had three named approvers (LL-56).
- *Check:* the Auditor greps expected sides and arrange blocks on money/time/ranking/access paths for production
  symbols (L6); any hit without a recorded reason is Major.
- *Applies when:* always; strictest on money, time, ranking and access.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**ORACLE-5** — Derive money, time and ranking expectations by an independent calculation and show it: worked arithmetic
in the oracle table and as a comment beside the assertion (TC-0042 below), or a reference outside the system — a
published table, an official schedule, another party's calculation, the fake's ground-truth record of what it served.
A disagreement with the Analyst's worked example is a spec defect blocking Gate T; the Tester never picks a side.
- *Why:* prize positions after a disqualification were wrong in a way only a hand calculation of the interacting rules
  exposed (LL-9).
- *Check:* each money/time/ranking TC carries a derivation; the Auditor recomputes three fresh cases per money/time BR
  from `analysis.md` as adversarial probes.
- *Applies when:* money, prices, quotas, scores, rankings, dates and durations.
- *Provenance:* LL-9 (KatenatsioTipster, 2026-10)

**ORACLE-6** — Consume worked-number acceptance criteria verbatim: each computational AC and BR carries concrete inputs
and outputs ("pool 1000 split 50/30/20 → 500/300/200"), and each
threshold states its inclusivity. Missing numbers, missing inclusivity or arithmetic that does not add up is a blocking
spec defect routed to the Analyst; the Tester does not invent the business answer.
- *Why:* measurable criteria (offsets, re-runs, volume, midnight boundaries) existed but nobody turned them into
  expected values (LL-45).
- *Check:* every TC citing a computational AC reuses its numbers; no blocking spec defect is open at Gate T (gateT).
- *Applies when:* every computational rule, threshold or time boundary.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10)

**ORACLE-7** — Apply source precedence: VERIFIED external facts decide what external systems do; `analysis.md` with
recorded gate decisions and existing catalogue invariants decides business behaviour; `design.md` decides experience
(copy, states, formats, focus); `architecture.md` decides only addresses (routes, signatures, payload shapes, error
codes) and internal units. When sources disagree — architecture vs analysis, a new rule vs an existing invariant,
design vs analysis — raise a spec defect to their owners; never build the oracle from the lower or the newer text alone.
- *Why:* a Gate 1 decision was reversed by an architecture note and every gate passed (LL-44); a test encoded a rule
  contradicting an earlier one (LL-48).
- *Check:* `trace_check gate gateT` rejects `SPEC:architecture` on a row citing a requirement id and fails on any open
  blocking spec-defect row of `test_plan.md`.
- *Applies when:* always.
- *Provenance:* LL-44, LL-48 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ORACLE-8** — Classify every failing TC and every TC-CONFLICT, with evidence, into exactly one class in
`test_report.md`: product defect (TF → Builder fix, counted as an iteration) · spec defect (→ owner of the cited source,
then amendment) · oracle contradicts its unchanged cited source (→ amendment request the Tester proposes and the
Manager approves; Analyst or user only if the source itself is unclear) · obsolete oracle (amendment citing the changed
requirement; none exists → Analyst or user) · harness defect (test code fixed, expected value unchanged) · flaky
(ESC-11; never skipped, TCQ-1). The Gate T after Mode D Reproduce classifies: one root-cause class per DEF (ESC-6);
each TC has red evidence or reads `binds at re-bind` (a requirements, UX or external-fact gap with no source yet — red
at the re-bind after the delta).
- *Why:* when the party that can only edit tests triages failures alone, "fix the test to match the code" becomes the
  default (LL-29); an oracle mis-copied from an unchanged design ("9:00 AM" for "09:00") fitted no class (LL-55); a
  Mode D Gate T could not pass for a gap with no source yet (LL-56).
- *Check:* every red TC in the report has one class and a route; harness fixes leave expected values byte-identical;
  an amendment request quotes the source line the oracle contradicts.
- *Applies when:* Verify, Reproduce, every TC-CONFLICT.
- *Provenance:* LL-29 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

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
- *Check:* `trace_check gate gateT --external-facts` resolves every `FACT:` source to a row whose
  Status starts with VERIFIED; each UNVERIFIED fact has a fail-closed TC.
- *Applies when:* the product talks to any external system.
- *Provenance:* LL-1, LL-2, LL-3 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ORACLE-12** — Before changing inherited code (brownfield adoption, a port, prototype code), pin its observable
behaviour with characterization tests labelled `CHAR` and tagged with their `INH-n`. They are change detectors, not
specification: a failing CHAR test routes to the Analyst and the user, never to a silent edit. The user decides each INH
item: Keep → a requirement, and the test becomes a normal TC citing it; Change or Remove → the test is replaced by
amendment; Unknown → asked before build. A suspected bug on a money, time, access or data-integrity path is never kept
"for parity".
- *Why:* a prototype's "clear all" behaviour shipped unspecified (LL-6); a suspected bug in a legacy formula was ported
  verbatim (LL-50).
- *Check:* the Baseline report pairs CHAR TCs with INH ids; trace_check resolves each `CHAR:INH-n` in the requirement
  source; the Auditor confirms INH-n is a user-confirmed Keep.
- *Applies when:* Mode B adoption, ports, rewrites, behaviour copied from a prototype or spreadsheet.
- *Provenance:* LL-6, LL-50 (KatenatsioTipster, 2026-10)

**ORACLE-13** — Show every test written after the code exists — Verify white-box tests, CHAR tests, sweep tests,
gate negative controls — able to fail: a killed mutant on the asserted lines, or a negative control (inject the fault in
a throwaway worktree outside the project, under `$TMPDIR`, never committed; run, see red, remove it — the project tree
stays byte-identical), with the output attached.
- *Why:* tests that have never failed may assert nothing; tests written after the code were never seen red (LL-29); a
  worktree inside the project tripped the write-time ownership hook (LL-57).
- *Check:* `test_report.md` links one red run or killed mutant per such TC.
- *Applies when:* Verify, Baseline, sweeps, Foundation gate negative controls.
- *Provenance:* LL-29 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ORACLE-14** — Measure oracle strength with mutation testing (e.g. Stryker, PIT, mutmut) on changed code and on every
money, time and access rule: each surviving mutant is killed by a new TC whose expected value has a spec source — never
the mutant's or the code's output — or recorded as equivalent with a reason. Typical survivors: `>=`→`>`, rounding mode,
removed tie-break, removed branch, swapped precedence. Thresholds per GATE-5.
- *Why:* coverage shows lines ran, not that any assertion would notice them being wrong.
- *Check:* the mutation report in `test_report.md` lists survivors with their resolution; the Auditor samples them.
- *Applies when:* every Verify; money, time and access rules always.
- *Provenance:* industry baseline

**ORACLE-15** — When one rule is implemented in more than one place (client preview and server, two services, a report
and its export), keep one shared golden-vector file (inputs → expected, each row citing its spec source) in the test
tree and make every implementation's suite load all of it; editing the file is an oracle change (ORACLE-2) and runs
every consuming suite.
- *Why:* hand-copied, partly overlapping case lists let a preview show one number while the server pays another.
- *Check:* each duplicated rule listed in `architecture.md` has one vector file; CI fails if a consuming suite does not
  load it or if the file changes without all consumers running.
- *Applies when:* a business rule exists in two or more implementations.
- *Provenance:* industry baseline

## Oracle table (in `test_plan.md`)

| TC | Inputs | Expected | Source | Derivation |
|---|---|---|---|---|
| TC-0042 | 3 × unit price 19.99, discount 10 %, half-up to cents | total 53.97 | `SPEC:ORD-BR-3.AC2` | 3 × 19.99 = 59.97; × 0.90 = 53.973 → 53.97 |
| TC-0043 | event at 2026-03-28T23:30Z; display zone UTC+1, UTC+2 from 2026-03-29T01:00Z | listed under 29 March | `SPEC:CAL-4.AC1` | 23:30Z + 1 h = 00:30 on 29 March local; UTC date is 28 March |
| TC-0044 | provider record with local time 20:00 at UTC+8 | stored instant 12:00Z | `FACT:EXT-FEED-2` | 20:00 − 8 h = 12:00Z; checked against the provider's published schedule |
