# Requirements — elicitation and analysis lenses

Code **ELIC**. The questions the Manager asks at intake (`brd.md`) and the lenses the Analyst applies in `analysis.md`
(skeleton: `absd/templates/artifacts/analysis.md`), so nothing is left for users to discover. Gate 1 checks presence
and the user's sign-off; the Tester turns each lens into test cases (VAR, ACCESS, ORACLE). Every interface profile.

## Checklist

- [ ] Mode S questions asked literally; answers + reasons in `cycle.md` (ELIC-1)
- [ ] Actor × capability matrix, whole product, admin-as-member rows, no blank cell (ELIC-2)
- [ ] Visibility table per caller-dependent read: principal × data state × time → records, fields (ELIC-3)
- [ ] Role value check: top three reasons per role → requirement ids; gaps raised (ELIC-4)
- [ ] INH Keep/Change/Remove/Unknown; Unknowns and suspected bugs decided before Gate 2 (ELIC-5)
- [ ] CRUD per touched entity, every verb decided; every needed read specified (ELIC-6)
- [ ] State table: state × event incl. invalid events, terminal states, order after removal (ELIC-7)
- [ ] Time: zones, calendar, boundary instants, inclusivity, DST, examples at 23:59 / 00:00 (ELIC-8)
- [ ] Money: unit, precision, rounding, signs, zero, tie-breaks; derived values recomputed (ELIC-9)
- [ ] Money movements: collection, refunds, timing, failure, idempotency, reconciliation, disputes, holder (ELIC-22)
- [ ] External facts UNVERIFIED unless evidenced; EXT ids reserved; Facts after Gate 1; failure → outcome (ELIC-10)
- [ ] Device/runtime classes per journey; phone in scope (web-ui, native-app) unless waived (ELIC-11)
- [ ] Data Volume Profile per collection: typical, max observed, real ordering (ELIC-12)
- [ ] Privacy: inventory, retention, deletion, export, consent, never-log list (ELIC-13)
- [ ] Operability defaults where OPS applies, or user-waived; flag semantics (ELIC-14)
- [ ] Notifications: trigger, recipient, channel, content, locale, retries, channel failure (ELIC-15)
- [ ] Audit trail: actions, fields, real actor, readers, retention; reads record nothing (ELIC-16)
- [ ] Concurrency: each multi-writer record and exactly-once action has an outcome (ELIC-17)
- [ ] ACs with values; inclusive thresholds; worked numbers; NF = dataset + environment + threshold (ELIC-18)
- [ ] A/OQ owned; contradictions with decisions and invariants listed (ELIC-19)
- [ ] Catalogue delta with permanent ids; area codes not reserved (ELIC-20)
- [ ] User sign-off of matrix, value check and inventory in brd Decisions (ELIC-21)

## Rules

### Intake

**ELIC-1** — At intake, before `brd.md`, ask the Mode S questions literally and record each answer and its reason in
`cycle.md`: does the change touch a principal, role or permission; an external integration; schema or a migration;
does it add or remove a screen, endpoint, command or public symbol, or change an interface contract (API, message,
event, file format); money or calculation; date, time or zone; auth or session; delete or retention; a background job;
a config key or flag; more than 10 production files? Any "yes" or "not sure" → Mode F; copy and layout on an existing
screen stay eligible.
- *Why:* with only a heavy route, a test suite and a dozen fixes bypassed the pipeline (LL-27); "touches a screen"
  sent every copy change to Mode F (LL-55).
- *Check:* `cycle.md` holds all eleven answers; the Auditor compares them with the real diff (XCA-11).
- *Applies when:* every intake (Modes F, S, D, C).
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

### Whole-product lenses

**ELIC-2** — Keep an Actor × Capability matrix over the whole product: rows = every principal (anonymous, each role,
each privileged role acting as an ordinary member, each entitlement state, system jobs, service identities, inbound
callers such as webhooks); columns = every capability; each cell Yes / No / N/A with its source (brd section, D-n,
catalogue id).
- *Why:* nobody wrote that admins also take part as members (LL-5).
- *Check:* Gate 1: no blank cell; rows = `context.md` Principals; every Yes cites a requirement.
- *Applies when:* always (library: callers and configurations; data-pipeline: stages and service identities).
- *Provenance:* LL-5 (KatenatsioTipster, 2026-10)

**ELIC-3** — For every read whose content differs by caller or over time, write a visibility table: principal × data
state (draft, open, locked, settled, deleted …) × time (before, at, after each boundary) → visible records and fields,
with a must-not-see cell for every principal below a paid, private or not-yet-public tier.
- *Why:* free accounts got paid content in a response they could call (LL-10); paying members could not see what they
  paid for (LL-18).
- *Check:* each cell is an ACCESS-10 row; Gate 1 rejects a caller-dependent read without a table.
- *Applies when:* any read whose content depends on principal, entitlement, ownership or time.
- *Provenance:* LL-10, LL-18 (KatenatsioTipster, 2026-10)

**ELIC-4** — Run a role value check: per role, the top three reasons it uses or pays for the product, each mapped to the
requirement ids that deliver it; a reason without a requirement is a gap raised to the user before Gate 1.
- *Why:* paying members could not see what they paid for (LL-18).
- *Check:* three rows per role, each citing a catalogue id; signed off per ELIC-21.
- *Applies when:* more than one principal, or any paid tier.
- *Provenance:* LL-18 (KatenatsioTipster, 2026-10)

**ELIC-5** — Inventory inherited behaviour (prototype, legacy system, spreadsheet, port) as `INH-n`: every visible
control, output, rule and default on the touched surfaces (Mode B: the whole product), each Keep → requirement id,
Change → new requirement, Remove, or Unknown → ask. Flag every suspected bug; the user decides each Unknown and
suspected bug before Gate 2; nothing is ported "for parity".
- *Why:* a prototype's "clear all" filled a grid with blank rows (LL-6); a suspected legacy bug was ported verbatim
  (LL-50).
- *Check:* no INH Unknown at Gate 2; each Keep cites a requirement; decisions in brd Decisions; CHAR tests carry INH
  ids (ORACLE-12).
- *Applies when:* brownfield adoption, ports, rewrites, prototypes.
- *Provenance:* LL-6, LL-50 (KatenatsioTipster, 2026-10)

### Per-feature lenses

**ELIC-6** — Walk every touched entity through create, read (one and list), update, delete, archive, restore, export and
import, per principal; decide each verb (a requirement, or "not offered" with the user's reason). Every read a screen,
command, report or downstream stage needs is its own non-mutating requirement.
- *Why:* an unspecified read was served by a mutating update writing phantom audit rows (LL-42).
- *Check:* no blank CRUD cell; each verb → a requirement or a recorded "not offered".
- *Applies when:* any persistent entity.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ELIC-7** — Specify every lifecycle as a state table: every state × every event → next state, side effects (audit row,
notification, recompute) and who may trigger it; every invalid event → its error, state unchanged; terminal states; for
ordered sets (ranks, positions, queues) the order and derived values after an insert, removal or disqualification, with
a worked example.
- *Why:* positions were wrong after a disqualification: re-slotting was unspecified (LL-9); a "delete then insert"
  step was half-built (LL-51).
- *Check:* no blank state × event cell; each ordered set has a removal example; VAR-5 rows derive from it.
- *Applies when:* status fields, workflows, queues, rankings.
- *Provenance:* LL-9, LL-51 (KatenatsioTipster, 2026-10)

**ELIC-8** — State time explicitly: per timestamp its zone at origin, in storage and on display (`context.md` Locale &
Time Profile); per deadline, expiry or bucket ("today", month, season) the boundary instant and its inclusivity; the
calendar that decides which day a record belongs to and which periods a source serves; DST behaviour; examples at 23:59,
00:00 and the boundary instant in every relevant zone.
- *Why:* a feed's local timestamps read as UTC made deadlines 8 hours late (LL-1); the provider's calendar left
  "Today" always empty (LL-3); a clock labelled UTC showed the viewer's time (LL-13).
- *Check:* Gate 1 rejects "local time" or "midnight" without a zone, a threshold without inclusivity; VAR-8 instants
  come from these examples.
- *Applies when:* any date, time, deadline, schedule or period.
- *Provenance:* LL-1, LL-3, LL-13 (KatenatsioTipster, 2026-10)

**ELIC-9** — Pin every calculation: unit and currency, precision, rounding rule and the step it applies at, sign
convention, zero and divide-by-zero results, a deterministic tie-break per ranking; every derived value (total, profit,
status, rank) is recomputed from its source facts, never stored as a client or user declared it.
- *Why:* a client-declared profit was trusted against the recompute rule (LL-48); ties were ranked by input order
  (LL-49).
- *Check:* each computational BR states every item and a worked example (ELIC-18); accepting a derived value from a
  caller fails Gate 1.
- *Applies when:* money, scores, rankings, quotas, any derived figure.
- *Provenance:* LL-48, LL-49 (KatenatsioTipster, 2026-10)

**ELIC-22** — Give every money movement (collection, full or partial refund, payout, forfeit, transfer) a row in the
`analysis.md` §1.4 "Money movements" table: trigger and amount, payer and payee, the external system holding or moving
the money, timing (charge, refund deadline and delay), failure and retry, idempotency (no double charge or refund),
reconciliation with that system, disputes and chargebacks; an unanswered cell is an OQ, never a default.
- *Why:* "a late cancellation forfeits the deposit" passed Gate 1 with no collection or refund flow and no payment
  system in `context.md`: only calculations were prompted (LL-55).
- *Check:* Gate 1: each requirement moving money cites a full row or an OQ; each money system is in `context.md` §7
  and `analysis.md` §7; `brd.md` §6 holds the intake answers.
- *Applies when:* money is collected, refunded, paid out, transferred or held, or such movements are recorded.
- *Provenance:* LL-55 (ABSD v2 kit review, 2026-10)

**ELIC-10** — Record every fact about an external system (format, zone, calendar, served periods, field meaning, order,
volume, errors, limits, sync or async) as UNVERIFIED until `EXTERNAL-FACTS.md` holds it VERIFIED (EXT-2); a person's
statement, the owner's included, is an UNVERIFIED candidate. Reserve each new fact's id `EXT-<SYS>-n` in
`analysis.md` §7 (highest in `EXTERNAL-FACTS.md` and `context.md` §7 + 1; the Tester adopts it). Per system, a failure
mode → user outcome table (what the user sees, what the system does, retry or not). A feature on an UNVERIFIED
fact is specified flag-off and fail-closed (EXT-1). A new or changed system or fact → the Tester's Facts mode right
after Gate 1 (EXT-4), before design.
- *Why:* an owner's description of a field settled half-time scores as final (LL-2); served days were never asked
  (LL-3); failures showed "Server error" (LL-11); new facts had no id before Gate 2, were verified after design (LL-55,
  LL-56).
- *Check:* every external fact in an AC has an EXT id or UNVERIFIED tag; every failure mode has an outcome; `cycle.md`
  shows Facts before the Designer's brief when §7 adds or changes a system.
- *Applies when:* any external system, deploy and CI platforms included (EXT-3).
- *Provenance:* LL-2, LL-3, LL-11 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

**ELIC-11** — Ask who uses each journey on which device or runtime class (phone portrait and landscape, tablet,
desktop, touch or pointer; terminal, shell and width; runtime versions) and record it per requirement; for web-ui and
native-app the phone class is in scope unless the user waives it in brd Decisions.
- *Why:* a reloading gesture and a hover-only control reached phone users while desktop tests passed (LL-4, LL-16).
- *Check:* journey requirements name device classes from `context.md` Audiences and devices; a waiver is a Decision.
- *Applies when:* every human-facing profile; runtime classes for cli and library.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10)

**ELIC-12** — Give every collection a Data Volume Profile row: typical count, maximum observed in the real source (not
guessed) and real ordering (what comes first; which item is "default" or "earliest"), so test data can make first,
earliest and default different items.
- *Why:* a fake held three groups where the real feed has hundreds, so the default selection opened off-screen in
  production (LL-4).
- *Check:* every list, search or grouping requirement cites a row with a sourced max; VAR-7 data reaches it.
- *Applies when:* any list, feed, import, batch or collection.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**ELIC-13** — Apply the privacy lens: personal data inventory (field, purpose, basis, who sees it), retention and
deletion per item, account deletion and export flows, consent capture and withdrawal, and the personal data that must
never reach logs, analytics or third parties — each a requirement or a recorded user decision (PRIV rules).
- *Why:* deletion, export and retention added late touch every store.
- *Check:* every personal field in the domain model is in the inventory with retention and deletion answered.
- *Applies when:* any personal data.
- *Provenance:* industry baseline

**ELIC-14** — Carry each operability default of `absd/RULES.md` rule 8 (deploy, same-version redeploy, rollback while
busy and after a migration, backup → restore, start on empty infrastructure, fresh clone → running, health and version,
log levels, alerting) as a REQ-NF wherever its OPS rule's *Applies when* covers a declared profile, plus hot-or-restart
semantics per flag. In that scope only the user waives one (a brd Decision); outside it, N/A citing the rule.
- *Why:* a refused rollback (LL-7), a crash on an empty database (LL-14), a broken default config (LL-22), a lost
  registry (LL-34), a flag needing a restart (LL-23): flows nobody specified.
- *Check:* each default is a requirement, a waiver Decision or an N/A citing its OPS *Applies when* (Auditor-verified).
- *Applies when:* always, each default as OPS scopes it (cli, library: publish, install, withdraw; data-pipeline:
  replay, backfill).
- *Provenance:* LL-7, LL-14, LL-22, LL-23, LL-34 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**ELIC-15** — Specify each notification or outbound message: trigger, recipient rule (incl. opted-out, suspended and
deleted recipients), channel, content and locale, timing and zone, no duplicate on retry, behaviour when the channel
fails.
- *Why:* retries duplicate messages and channel failures lose them silently.
- *Check:* each notification requirement answers all seven; INTEG-15 rows derive from it.
- *Applies when:* any mail, push, SMS, webhook or event the product emits.
- *Provenance:* industry baseline

**ELIC-16** — Specify the audit trail: recorded actions (at least every mutating privileged one), fields (action, actor,
real actor under impersonation, subject, time, before → after), readers, retention; reads record nothing.
- *Why:* a read built as an update wrote phantom audit rows (LL-42).
- *Check:* every mutating privileged Yes cell of the ELIC-2 matrix is covered; INTEG-9 rows derive from it.
- *Applies when:* privileged actions, impersonation, money movements.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ELIC-17** — Specify concurrency in business terms: for every record two actors can change (two people, a person and a
job, a retry and its original) who wins and what the other sees; which actions are exactly-once (double submit, double
approval, re-run); for fast successive inputs, that the latest intent wins.
- *Why:* a late search response overwrote a filter clicked right after typing (LL-20).
- *Check:* each multi-writer entity and exactly-once action has an AC with its outcome (VAR-12, VAR-13).
- *Applies when:* shared records, jobs, retries, approvals, debounced inputs.
- *Provenance:* LL-20 (KatenatsioTipster, 2026-10)

### Specification quality

**ELIC-18** — Specify by example: every AC GIVEN/WHEN/THEN with concrete values; every threshold with its inclusivity
("at 18:00:00 exactly the entry is locked"); every computational BR with ≥ 1 worked example computed by hand; every
REQ-NF with dataset (size, ordering), environment and threshold, and the verification level to plan.
- *Why:* measurable criteria passed audits by code reading, never tested (LL-45); "no visual regression" was never
  automated (LL-53).
- *Check:* Gate 1 rejects an AC without values, a threshold without inclusivity, a computational BR without numbers, an
  NF missing any of the three; ORACLE-6 reuses them verbatim.
- *Applies when:* always.
- *Provenance:* LL-45, LL-53 (KatenatsioTipster, 2026-10)

**ELIC-19** — Give every assumption (A-n) and open question (OQ-n) an owner and a blocking flag; list every
contradiction with brd Decisions, earlier gate resolutions and catalogue BRs (invariants), never resolved silently or by
a "safe default". At archive the Manager copies each unresolved item to the `context.md` Risk register with what it
blocks (release, a flag, none).
- *Why:* a blocking zone question died with its analysis while "UTC" shipped as a safe default (LL-1); a later note
  reversed a Gate 1 decision (LL-44).
- *Check:* after archive the Risk register holds every unresolved A/OQ; each contradiction names its decision.
- *Applies when:* always.
- *Provenance:* LL-1, LL-44 (KatenatsioTipster, 2026-10)

**ELIC-20** — Change the catalogue only through the Catalogue delta in `analysis.md`: rows to add, change or retire
exactly as they will read in `catalogue.md`, in users' terms; ids are permanent (next = highest in catalogue and archive
+ 1; never reused; a retired row names its successor); area codes from `context.md`, never reserved codes (TRACE-2,
TRACE-4).
- *Why:* a hand-kept catalogue drifted from the archived analyses (LL-36).
- *Check:* `trace_check.py gate gate1` passes; the delta lands in its own Analyst commit after Gate 1.
- *Applies when:* every cycle that adds, changes or retires a requirement.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10)

**ELIC-21** — At Gate 1 the Manager shows the user the actor × capability matrix, the role value check and the inherited
behaviour inventory (every Unknown and suspected bug) and records the dated sign-off and a D-n per decision in brd
Decisions; Gate 1 never passes on the Manager's own reading.
- *Why:* missing requirements (LL-5, LL-18) and inherited behaviour (LL-6) passed a gate judged by the brief's author.
- *Check:* brd Decisions holds the sign-off line; `cycle.md` links the gate1 trace output.
- *Applies when:* every Gate 1 (Mode S: when catalogue entries change).
- *Provenance:* LL-5, LL-6, LL-18 (KatenatsioTipster, 2026-10)
