# External facts — evidence, status, fail-closed

Code **EXT**. An external system is anything the product does not control: data feeds, payment, identity, mail, push,
OCR/LLM, and the platforms it is built, deployed and run on (CI, registry, host or container platform, managed stores —
which tests still use as real stores, E2E-3). Facts live in the Tester's living `EXTERNAL-FACTS.md` as `EXT-<SYS>-n`:
the Analyst reserves new ids in `analysis.md` §7 (highest + 1 across `EXTERNAL-FACTS.md` and `context.md` §7) and the
Tester adopts them; plans cite them as `FACT:EXT-<SYS>-n`, VERIFIED only (ORACLE-1, ORACLE-11). Fakes, recordings,
contract and live checks: FAKE rules in `absd/playbook/testing/contracts-and-fakes.md`.

## Checklist

- [ ] Every external system, platforms included, has an `EXTERNAL-FACTS.md` section with the full fact checklist (EXT-2, EXT-3)
- [ ] Evidence = recorded real response + independent source; never a statement, a default or a fake (EXT-2)
- [ ] Behaviour on an UNVERIFIED fact sits behind a flag that is off everywhere and fails closed (EXT-1)
- [ ] Behaviour on VERIFIED facts only — a fact corrected at Reproduce included — may ship enabled (EXT-1)
- [ ] Recording + independent source → VERIFIED, in a Tester change with no production code; contract TC, fakes, live check pin it (EXT-4)
- [ ] Facts verified in Facts mode before Design, at Reproduce for an external-fact defect, else at Plan & Bind (EXT-4)
- [ ] Integration replaced → sweep of UI, docs, config, fakes and health checks (EXT-5)

## Rules

**EXT-1** — Put behaviour that depends on an UNVERIFIED external fact behind a flag that is off in every environment, and make it fail closed: refuse with a designed "not available" outcome instead of acting on a guessed default. Behaviour resting only on VERIFIED facts needs no such flag: a defect fix whose fact was corrected and VERIFIED at Mode D Reproduce (EXT-4) may ship enabled.
- *Why:* an unknown provider zone, flagged as a blocking open question, shipped as a "safe default" with the feature on, and the caveat died when the cycle was archived (LL-1); a live Critical fix on a corrected fact could only ship disabled (LL-56).
- *Check:* each UNVERIFIED fact has a Risk register row `blocks: flag:<name>` in `context.md`; a TC proves the flag-off path inert and the fail-closed outcome; Mode R blocks on any UNVERIFIED fact behind an enabled feature; the Auditor greps for defaults standing in for unverified facts and accepts an enabled fix only when every fact it rests on is VERIFIED.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**EXT-2** — Accept as evidence of an external fact only a recorded real response plus an independent source (official documentation, a published schedule, a known real event); a person's statement, a default value or a fake is not evidence; give every external system the full fact checklist below, each row VERIFIED, UNVERIFIED or N/A with a reason.
- *Why:* the requirements accepted the owner's statement about a field's meaning (LL-2); served days and the provider calendar were never asked (LL-3); failure modes were never listed (LL-11).
- *Check:* an `EXTERNAL-FACTS.md` section per system in `context.md` §7, no blank checklist row; `analysis.md` §7 cites EXT ids, new ones reserved by the Analyst; Gate T: one CONTRACT TC per fact and one user-facing TC per failure mode.
- *Applies when:* the product talks to any external system.
- *Provenance:* LL-2, LL-3, LL-11 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

| # | Fact | Verify | Trap it prevents |
|---|---|---|---|
| 1 | Format & encoding | types, date and number formats, charset, field-name case, extra fields, markup inside values | a format variant dropped silently |
| 2 | Time zone | zone and DST of every timestamp field | provider-local time read as UTC (LL-1) |
| 3 | Calendar, day boundaries, served periods | whose calendar numbers days; which days or periods are served; when "today" appears | an always-empty "Today" (LL-3) |
| 4 | Ordering | natural order, stability, tie order | first listed ≠ earliest (LL-4) |
| 5 | Volume & pagination | typical and max per period, page size, cursor, end of list | three-item fakes (LL-4) |
| 6 | Empty answers | exact status and body of "no data" | outage read as "no data" |
| 7 | Error answers | 401, 403, 404, 429, 5xx, timeout, malformed — real status and body | "Server error" (LL-11) |
| 8 | Limits & cost | rate limit, quota, price per call, alert threshold | a feature dies at the quota |
| 9 | Sync vs async | accepted-then-processing, busy or conflict answers, completion signal | rollback refused while busy (LL-7) |
| 10 | Field semantics | which value is final, gross or net, units, sign, status codes, irregular events (postponed, cancelled) | half-time read as final (LL-2) |
| 11 | Late corrections & duplicates | corrections, replays, out-of-order and duplicate deliveries, idempotency keys, callback signatures | double processing |
| 12 | Version | version id, change signalling, deprecation | silent schema drift |

**EXT-3** — Treat the platforms the product is built, deployed, run and talks through — CI, registry, host or container platform, mail, push, OCR/LLM, payment, identity — as external systems with fact sheets, fakes and live checks, and fake a platform with a stateful model of its real semantics (asynchrony, busy or conflict answers, auth failures, partial failures, strict request validation) plus one safety invariant asserted across all scenarios.
- *Why:* the fake deploy platform deployed synchronously, so a same-version redeploy was smoke-tested mid-restart and the rollback was refused (LL-7); a stateful platform fake made the deploy script testable (LL-39); CI broke on a registry pull limit (LL-30).
- *Check:* every deploy or ops script branch has a scenario; when production reveals behaviour the fake lacked, the fake is fixed first and the incident becomes a scenario (ESC-1); the fake is compared with the real platform on a schedule.
- *Applies when:* the product uses platform APIs or custom deploy and ops automation.
- *Provenance:* LL-7, LL-39, LL-30 (KatenatsioTipster, 2026-10)

**EXT-4** — Verify facts in Tester changes that touch no production code: the recording and the independent source turn the `EXTERNAL-FACTS.md` row VERIFIED, under the id the Analyst reserved, and the contract TC, the updated fakes and the live check pin it in the same change — for an adapter not built yet, at Plan & Bind, the contract TC RED until its work package lands. Verify when the fact is first needed: in *Facts* mode right after Gate 1 when the scope adds or changes an external system or fact (recording, source, rows; no TCs yet), so the Designer and the Architect work from recorded samples and VERIFIED facts; at Mode D *Reproduce* when the defect's mechanism is an external fact (external-fact gap, ESC-6), all five parts at once, so the regression TC has a `FACT:` source; otherwise at Plan & Bind or Baseline. A flag guarding behaviour on a fact turns on only once all five parts exist and pass, by its owner through Mode R (a corrected fact's fix: EXT-1). A fact not yet verified stays UNVERIFIED in the living register and the Risk register, never only in an archived artifact.
- *Why:* the zone caveat lived only in an archived analysis and was lost with it (LL-1); facts verified only at Plan & Bind came after Design and Architecture needed them, and a wrong fact found in Mode D left its regression test without a VERIFIED source (LL-56).
- *Check:* git history shows each verification as a Tester commit set touching no production path, all five parts present by T-SHA; on a route adding an external system the Facts commit precedes `design.md`; the Auditor confirms every enabled flag depends only on facts whose five parts exist and pass.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

**EXT-5** — When an external system is replaced or removed, sweep UI copy, status and health indicators, docs, configuration keys, environment examples, manifests, fakes, recordings, flags and allowlists for the old one, and point health checks at what the new provider really serves.
- *Why:* after a feed was replaced, a status card still named the old provider, then reported "no data" because it asked for a day the new feed never serves (LL-17).
- *Check:* `test_plan.md` lists the sweep (search terms, places) and a TC on the health indicator; the Auditor re-runs the search.
- *Applies when:* an integration is replaced, renamed or retired.
- *Provenance:* LL-17 (KatenatsioTipster, 2026-10)
