# Requirements — elicitation and analysis lenses

Code **ELIC**. The questions the Manager asks at intake (`brd.md`) and the lenses the Analyst applies in `analysis.md`,
so that no principal, state, rule, fact or flow is left for users to discover. Every lens has a home section in
`analysis.md` (skeleton: the Analyst manual); Gate 1 checks presence and the user's sign-off; the Tester turns each
lens into test cases (VAR, ACCESS, ORACLE in `absd/playbook/testing/`). Every interface profile.

## Checklist

- [ ] Mode S eligibility questions asked at intake; answers and reasons in `cycle.md` (ELIC-1)
- [ ] Actor × capability matrix over the whole product: every principal, every capability, no blank cell, sourced (ELIC-2)
- [ ] Visibility table per caller-dependent read: principal × data state × time → records and fields (ELIC-3)
- [ ] Role value check: top three reasons per role → requirement ids; gaps raised (ELIC-4)
- [ ] Inherited behaviour inventory: INH Keep/Change/Remove/Unknown; Unknowns and suspected bugs decided before Gate 2 (ELIC-5)
- [ ] CRUD + lifecycle table per touched entity, every verb decided; every needed read specified (ELIC-6)
- [ ] State table per lifecycle: state × event incl. invalid events, terminal states, order after removal (ELIC-7)
- [ ] Time: zones, calendar, boundary instants, inclusivity, DST, examples at 23:59 / 00:00 (ELIC-8)
- [ ] Money: unit, precision, rounding, signs, zero cases, tie-breaks; derived values recomputed, never declared (ELIC-9)
- [ ] External facts UNVERIFIED unless evidenced; failure mode → user outcome table per system (ELIC-10)
- [ ] Device and runtime classes per journey; phone in scope unless waived (ELIC-11)
- [ ] Data Volume Profile per collection: typical, max observed, real ordering (ELIC-12)
- [ ] Privacy: personal data inventory, retention, deletion, export, consent, never-log list (ELIC-13)
- [ ] Operability defaults and flag semantics present, or waived by the user (ELIC-14)
- [ ] Notifications: trigger, recipient, channel, content, locale, retry duplicates, channel failure (ELIC-15)
- [ ] Audit trail: actions, fields, real actor, readers, retention; reads record nothing (ELIC-16)
- [ ] Concurrency: every multi-writer record and exactly-once action has a specified outcome (ELIC-17)
- [ ] ACs with concrete values; thresholds state inclusivity; worked numbers; NF = dataset + environment + threshold (ELIC-18)
- [ ] Assumptions and open questions owned; contradictions with decisions and invariants listed (ELIC-19)
- [ ] Catalogue delta with permanent ids; area codes not reserved (ELIC-20)
- [ ] User sign-off of matrix, value check and inventory recorded in brd Decisions (ELIC-21)

## Rules

### Intake

**ELIC-1** — At intake, before writing `brd.md`, ask the Mode S eligibility questions literally and record each answer
with its reason in `cycle.md`: does the change touch a principal, role or permission; an external integration;
persistent schema or a migration; a public interface element (screen, endpoint, command, public symbol, message or event
contract); money or calculation logic; date, time or zone logic; auth or session logic; delete or retention logic; a
background job; a config key or feature flag; more than 10 production files? Any "yes" or "not sure" → Mode F.
- *Why:* with only a heavy route, a whole test suite and about a dozen fixes were made outside the pipeline (LL-27).
- *Check:* `cycle.md` holds all eleven answers; the Auditor compares them with the real diff (XCA-11).
- *Applies when:* every intake (Modes F, S, D, C).
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

### Whole-product lenses

**ELIC-2** — Keep an Actor × Capability matrix over the whole product, not only this cycle: rows = every principal
(anonymous, each role, each privileged role acting as an ordinary member, each entitlement state, system jobs, service
identities, inbound callers such as webhooks); columns = every capability; each cell Yes / No / N/A with its source
(brd section, Decision D-n, catalogue id). Ask of every privileged role: "does this person also use the product as a
member?"
- *Why:* admins could not take part as ordinary members because nobody wrote the requirement (LL-5).
- *Check:* at Gate 1 the Manager finds no blank cell; rows equal `context.md` Principals; every Yes cites a requirement.
- *Applies when:* always (library: callers and configurations; data-pipeline: stages and service identities).
- *Provenance:* LL-5 (KatenatsioTipster, 2026-10)

**ELIC-3** — For every read whose content differs by caller or over time, write a visibility table: principal × data
state (draft, open, locked, settled, deleted …) × time (before, at, after each boundary) → visible records and fields,
with an explicit must-not-see cell for every principal below a paid, private or not-yet-public tier.
- *Why:* free accounts received paid content in a response they were allowed to call (LL-10); paying members could not
  see what they paid for (LL-18).
- *Check:* each cell becomes an ACCESS-10 row; Gate 1 rejects a caller-dependent read without a table.
- *Applies when:* any read whose content depends on principal, entitlement, ownership or time.
- *Provenance:* LL-10, LL-18 (KatenatsioTipster, 2026-10)

**ELIC-4** — Run a role value check: per role, the top three reasons it uses or pays for the product, each mapped to the
requirement ids that deliver it; a reason without a requirement is a gap raised to the user before Gate 1.
- *Why:* paying members could not see the content they paid for; the role's core value was never checked (LL-18).
- *Check:* three rows per role, each citing an active or new catalogue id; signed off per ELIC-21.
- *Applies when:* more than one principal, or any paid tier.
- *Provenance:* LL-18 (KatenatsioTipster, 2026-10)

**ELIC-5** — Inventory inherited behaviour (prototype, legacy system, spreadsheet, port) as `INH-n`: every visible
control, output, rule and default on the touched surfaces (Mode B: the whole product), each Keep → requirement id,
Change → new requirement, Remove, or Unknown → ask. Flag every suspected bug; the user decides every Unknown and
suspected bug before Gate 2 — nothing is ported "for parity".
- *Why:* a prototype's "clear all" filled a grid with blank rows (LL-6); a suspected bug in a legacy formula was ported
  verbatim and corrected later (LL-50).
- *Check:* no INH is Unknown at Gate 2; each Keep cites a requirement; decisions sit in brd Decisions; CHAR tests pair
  with INH ids (ORACLE-12).
- *Applies when:* brownfield adoption, ports, rewrites, anything built on a prototype.
- *Provenance:* LL-6, LL-50 (KatenatsioTipster, 2026-10)

### Per-feature lenses

**ELIC-6** — Walk every touched entity through create, read (one and list), update, delete, archive, restore, export and
import, per principal; decide each verb (a requirement, or "not offered" with the user's reason). Every read a screen,
command, report or downstream stage needs is its own non-mutating requirement.
- *Why:* a screen needed a read nobody specified, so a mutating update served as the read and wrote phantom audit rows
  (LL-42).
- *Check:* the CRUD table has no blank cell; each verb maps to a requirement or a recorded "not offered".
- *Applies when:* any persistent entity.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ELIC-7** — Specify every lifecycle as a state table: every state × every event → next state, side effects (audit row,
notification, recompute) and who may trigger it; every invalid event → its error, state unchanged; terminal states; for
ordered sets (ranks, positions, queues) the order and derived values after an insert, removal or disqualification, with
a worked example.
- *Why:* prize positions were wrong after a disqualification because re-slotting was never specified (LL-9); a "delete
  then insert" step was half-built (LL-51).
- *Check:* no blank state × event cell; each ordered set has a removal example; VAR-5 rows derive from the table.
- *Applies when:* status fields, workflows, queues, rankings.
- *Provenance:* LL-9, LL-51 (KatenatsioTipster, 2026-10)

**ELIC-8** — State time explicitly: per timestamp its zone at origin, in storage and on display (`context.md` Locale &
Time Profile); per deadline, expiry or bucket ("today", month, season) the boundary instant and its inclusivity; the
calendar that decides which day a record belongs to and which periods a source serves; DST behaviour; examples at 23:59,
00:00 and the boundary instant in every relevant zone.
- *Why:* a feed's local timestamps were read as UTC, so every deadline was 8 hours late (LL-1); the provider's calendar
  left "Today" always empty (LL-3); a clock labelled UTC showed the viewer's time (LL-13).
- *Check:* Gate 1 rejects "local time" or "midnight" without a zone and a threshold without inclusivity; VAR-8 instants
  come from these examples.
- *Applies when:* any date, time, deadline, schedule or period.
- *Provenance:* LL-1, LL-3, LL-13 (KatenatsioTipster, 2026-10)

**ELIC-9** — Pin every calculation: unit and currency, precision, rounding rule and the step it applies at, sign
convention, zero and divide-by-zero results, a deterministic tie-break per ranking; every derived value (total, profit,
status, rank) is recomputed by the system from its source facts — a value declared by a client or user is never stored
as derived truth.
- *Why:* a client-declared profit was trusted against a rule that derived values are recomputed (LL-48); tied entrants
  were ranked by input order (LL-49).
- *Check:* each computational BR states every item and a worked example (ELIC-18); a requirement accepting a derived
  value from a caller fails Gate 1.
- *Applies when:* money, scores, rankings, quotas, any derived figure.
- *Provenance:* LL-48, LL-49 (KatenatsioTipster, 2026-10)

**ELIC-10** — Record every fact about an external system (format, zone, calendar, served periods, field meaning, order,
volume, errors, limits, sync or async) as UNVERIFIED until `EXTERNAL-FACTS.md` holds it VERIFIED (EXT-2); a person's
statement, the owner's included, is an UNVERIFIED candidate with a verification owner. Per system, write a failure
mode → user outcome table (what the user sees, what the system does, retry or not). A feature resting on an UNVERIFIED
fact is specified flag-off and fail-closed (EXT-1).
- *Why:* the owner's description of a results field was taken as fact and half-time scores were settled as final
  (LL-2); served days were never asked (LL-3); service failures showed "Server error" (LL-11).
- *Check:* no AC states an external fact without an EXT id or UNVERIFIED tag; every failure mode has an outcome.
- *Applies when:* any external system, deploy and CI platforms included (EXT-3).
- *Provenance:* LL-2, LL-3, LL-11 (KatenatsioTipster, 2026-10)

**ELIC-11** — Ask who uses each journey on which device or runtime class (phone portrait and landscape, tablet,
desktop, touch or pointer; terminal, shell and width; runtime versions) and record it per requirement; a web UI's phone
class is in scope unless the user waives it in brd Decisions.
- *Why:* a gesture that reloaded the app and a hover-only control reached phone users while desktop tests passed
  (LL-4, LL-16).
- *Check:* journey requirements name device classes matching `context.md` Audiences and devices; a waiver is a Decision.
- *Applies when:* every human-facing profile; runtime classes for cli and library.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10)

**ELIC-12** — Give every collection a Data Volume Profile row: typical count, maximum observed in the real source (not
guessed) and real ordering (what comes first; which item is "default" or "earliest"), so designs and test data can
make first, earliest and default different items.
- *Why:* a fake held three groups where the real feed has hundreds, so the special item was always first and the
  default selection opened off-screen in production (LL-4).
- *Check:* every list, search or grouping requirement cites a row with a source for its max; VAR-7 data reaches it.
- *Applies when:* any list, feed, import, batch or collection.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**ELIC-13** — Apply the privacy lens: personal data inventory (field, purpose, consent or other basis, who sees it),
retention and deletion per item, account deletion and data export flows, consent capture and withdrawal, and the
personal data that must never reach logs, analytics or third parties — each a requirement or a recorded user decision
(PRIV rules in `absd/playbook/security/baseline.md`).
- *Why:* deletion, export and retention are flows people and regulators expect; added late they touch every store.
- *Check:* every personal field in the domain model appears in the inventory with retention and deletion answered.
- *Applies when:* any personal data.
- *Provenance:* industry baseline

**ELIC-14** — Carry the operability defaults as REQ-NFs (`absd/RULES.md` rule 8): deploy, same-version redeploy,
rollback while the platform is busy and after a migration, backup → restore drill, first start on empty infrastructure,
fresh clone → running from the docs, health and version, log levels, alerting; plus hot-or-restart semantics per flag.
Only the user waives one, as a brd Decision.
- *Why:* a refused rollback (LL-7), a crash on an empty database (LL-14), a broken default configuration (LL-22), a
  registry that lost its images (LL-34) and a flag that needed a restart (LL-23) were flows nobody specified.
- *Check:* each default is a requirement or a waiver Decision in every analysis that touches deployables.
- *Applies when:* always (cli, library: publish, install, withdraw; data-pipeline: replay, backfill).
- *Provenance:* LL-7, LL-14, LL-22, LL-23, LL-34 (KatenatsioTipster, 2026-10)

**ELIC-15** — Specify each notification or outbound message: trigger, recipient rule (incl. opted-out, suspended and
deleted recipients), channel, content and locale, timing and zone, no duplicate on retry, behaviour when the channel
fails.
- *Why:* messages are user-visible side effects; retries duplicate them and channel failures lose them silently.
- *Check:* each notification requirement answers all seven; INTEG-15 rows derive from it.
- *Applies when:* any mail, push, SMS, webhook or event the product emits.
- *Provenance:* industry baseline

**ELIC-16** — Specify the audit trail: recorded actions (at least every mutating privileged action), fields (action,
actor, real actor under impersonation, subject, time, before → after), readers, retention; reads record nothing.
- *Why:* a read built as an update wrote phantom audit rows (LL-42).
- *Check:* every privileged Yes cell of the ELIC-2 matrix that mutates is covered; INTEG-9 rows derive from it.
- *Applies when:* privileged actions, impersonation, money movements.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ELIC-17** — Specify concurrency in business terms: for every record two actors can change (two people, a person and a
job, a retry and its original) who wins and what the other sees; which actions are exactly-once (double submit, double
approval, re-run); for fast successive inputs, that the latest intent wins.
- *Why:* a filter clicked right after typing a search was overwritten by the late search response (LL-20).
- *Check:* each multi-writer entity and exactly-once action has an AC with its outcome; VAR-12, VAR-13 rows derive.
- *Applies when:* shared records, jobs, retries, approvals, debounced inputs.
- *Provenance:* LL-20 (KatenatsioTipster, 2026-10)

### Specification quality

**ELIC-18** — Specify by example: every AC GIVEN/WHEN/THEN with concrete values; every threshold with its inclusivity
("at 18:00:00 exactly the entry is locked"); every computational BR with ≥ 1 worked example computed by hand; every
REQ-NF with dataset (size, ordering), environment and threshold, and the verification level the Tester should plan.
- *Why:* measurable criteria were never turned into tests and passed audits by code reading (LL-45); a "no visual
  regression" requirement was never automated (LL-53).
- *Check:* Gate 1 rejects an AC without values, a threshold without inclusivity, a computational BR without numbers or
  an NF missing any of the three; ORACLE-6 reuses them verbatim.
- *Applies when:* always.
- *Provenance:* LL-45, LL-53 (KatenatsioTipster, 2026-10)

**ELIC-19** — Give every assumption (A-n) and open question (OQ-n) an owner and a blocking flag; list every
contradiction with brd Decisions, earlier gate resolutions and catalogue BRs (invariants) — never resolve one silently or
by a "safe default". At archive the Manager copies each unresolved item to the `context.md` Risk register with what it
blocks (release, a flag, none).
- *Why:* a blocking zone question died with its archived analysis while "UTC" shipped as a safe default (LL-1); a Gate 1
  decision was reversed by a later note (LL-44).
- *Check:* the Risk register holds every unresolved A/OQ after archive; each contradiction names the decision it needs.
- *Applies when:* always.
- *Provenance:* LL-1, LL-44 (KatenatsioTipster, 2026-10)

**ELIC-20** — Change the catalogue only through the Catalogue delta in `analysis.md`: rows to add, change or retire
exactly as they will read in `catalogue.md`, in users' terms; ids are permanent (next = highest in catalogue and archive
+ 1; never reused or renumbered; a retired row names its successor); area codes come from `context.md` and are never
reserved codes (TRACE-2, TRACE-4).
- *Why:* a hand-kept catalogue drifted from the archived analyses (LL-36).
- *Check:* `trace_check.py gate gate1` passes; the delta lands in its own Analyst commit after Gate 1 (ownership_check).
- *Applies when:* every cycle that adds, changes or retires a requirement.
- *Provenance:* LL-36 (KatenatsioTipster, 2026-10)

**ELIC-21** — At Gate 1 the Manager shows the user the actor × capability matrix, the role value check and the inherited
behaviour inventory (every Unknown and suspected bug included) and records the sign-off with its date and a D-n per
decision in brd Decisions; Gate 1 never passes on the Manager's own reading.
- *Why:* missing requirements (LL-5, LL-18) and unspecified inherited behaviour (LL-6) passed a gate judged by the
  author of the brief.
- *Check:* brd Decisions holds the sign-off line; `cycle.md` links the gate1 trace output.
- *Applies when:* every Gate 1 (Mode S: when catalogue entries change).
- *Provenance:* LL-5, LL-6, LL-18 (KatenatsioTipster, 2026-10)
