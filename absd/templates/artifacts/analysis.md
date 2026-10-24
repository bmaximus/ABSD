<!-- ABSD skeleton: copy to absd-project/working/analysis.md; keep every heading (tools read them).
Owner: analyst. -->

# Analysis — C### <slug>
Cycle: C### | Mode: F/S/D/C/B | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Inputs: brd.md @<sha> | defect.md @<sha> · catalogue.md @<sha> · context.md @<sha> · EXTERNAL-FACTS.md @<sha> · archived analysis: <path>
Profiles: <…> · Area codes: <AREA = meaning> · Scope: full | delta (§…) · Parts: <analysis/NN-*.md | none>
Next ids at start: <AREA>-n · <AREA>-NF-n · <AREA>-BR-n · INH-n · EXT-<SYS>-n per system (highest in EXTERNAL-FACTS.md, context.md §7 and the archive + 1)
Progress: [ ] inputs [ ] §1 [ ] §2–4 [ ] §5–6 [ ] §7–11 [ ] §12–14 [ ] §15–16 [ ] self-check [ ] Traceability

## 0. Routed items answered (revision rounds; else "none")
| Kind (G1 note · user answer · spec defect · upstream issue · finding · DEF · CR · CLR · Facts result) | Item (D-n, C###/F-n, …) | Answer | Sections changed |
|---|---|---|---|

## 1. Requirements
### 1.1 Functional
#### <AREA>-n — <title> · new
- Source: brd §<x> | D-n | DEF-n | CR-n | INH-n · Implicit: no | yes — needed by <id / brd §>
- Actors: <§2 rows> · Device / runtime classes: <…> · Preconditions: <…>
- Behaviour: <one behaviour, observable, business terms>
- Change (changed / removed / re-verify): <old → new · why removed, successor · why re-proved>
| AC | GIVEN (concrete values) | WHEN | THEN (observable outcome, exact values) | Status |
|---|---|---|---|---|
| <AREA>-n.AC1 | <…> | <…> | <…> | new |
- Edge cases (each an AC above or N/A — reason): empty · malformed · not permitted · not found · duplicate · concurrent · boundary instants · max volume · external failures · flag off

### 1.2 Non-functional
#### <AREA>-NF-n — <title> · new
- Source · Quality: <…> · Metric and threshold: <e.g. p95 ≤ 300 ms, inclusive> · Dataset: <size, ordering — §8 row>
- Environment: <…> · Verification level for the Tester: <integration | end-to-end | performance | accessibility scan | drill | contract>

### 1.3 Business rules
#### <AREA>-BR-n — <title> · new
- Verbatim: "<the user's words>" (brd §4 row <n>) · Clarified: <precise rule> · Invariant: yes (every cycle) | no
- Interacts with: <AREA>-BR-m (precedence → decision table) | none
| # | Input | Value | Result | Inclusivity |
|---|---|---|---|---|
| 1 | <below / at / above each limit> | <…> | <…> | <inclusive | exclusive> |
- Worked example: <inputs → arithmetic step by step, rounding step named → result>

### 1.4 Cross-cutting lenses ("none" per table when absent)
Time (ELIC-8)
| # | Timestamp, deadline or bucket | Zone at origin · storage · display | Boundary instant, inclusivity | Calendar, DST | Examples at 23:59 · 00:00 · boundary, per zone | Ids |
|---|---|---|---|---|---|---|
Money and calculations (ELIC-9)
| # | Figure | Unit, currency | Precision | Rounding rule and step | Sign; zero; divide-by-zero | Tie-break | Recomputed from | Ids |
|---|---|---|---|---|---|---|---|---|
Money movements (ELIC-22) — one row per collection, refund (full · partial), payout, forfeit or transfer; an unanswered cell is an OQ, never a default
| # | Movement | Trigger and amount (BR id · worked example) | Payer → payee | System holding or moving the money (§7) | Timing: charge, refund deadline and delay (zone) | Failure and retry → outcome | Idempotency (no double charge or refund) | Reconciliation with that system | Disputes, chargebacks | Ids |
|---|---|---|---|---|---|---|---|---|---|---|
Expected output for a recorded input (ELIC-18) — datasets, reports, extractions, model outputs; the golden or eval file cites this table (ORACLE-4)
| # | Input (recording path @sha · EXT id · or the user's sample, UNVERIFIED) | Input excerpt (rows or fields, verbatim) | Expected output (rows or fields, exact values, units, zones, order) | Not compared (field — why) | Ids |
|---|---|---|---|---|---|
Notifications (ELIC-15)
| # | Trigger | Recipient rule (opted out, suspended, deleted) | Channel | Content, locale | Timing, zone | No duplicate on retry | Channel failure | Ids |
|---|---|---|---|---|---|---|---|---|
Audit trail (ELIC-16)
| # | Action | Fields: actor · real actor · subject · time · before → after | Readers | Retention | Ids |
|---|---|---|---|---|---|
Concurrency (ELIC-17)
| # | Record or action | Competing actors | Winner; what the other sees | Exactly-once? | Ids |
|---|---|---|---|---|---|

## 2. Actor × Capability matrix (whole product; ELIC-2)
Rows: every `context.md` §1 principal × entitlement state, anonymous, each privileged role acting as a member, jobs,
service identities, inbound callers. Cell: `Yes <id>` | `No <id or D-n>` | `N/A — <reason>`; cells this cycle
changes end `(new)` / `(changed)`. Many capabilities → one table per area, same rows. No blank cell.
| Principal \ Capability | <capability> | <capability> |
|---|---|---|
| anonymous | <…> | <…> |

## 3. Data visibility (ELIC-3) — one table per caller- or time-dependent read
### Read: <capability> (<AREA>-n)
| Principal | Data state | Time (before · at · after <boundary>) | Visible records | Visible fields | Must not see |
|---|---|---|---|---|---|

## 4. Role value check (ELIC-4)
| Role | Reason it uses or pays (top 3) | Delivered by (ids) | Gap → §12 |
|---|---|---|---|

## 5. State machines (ELIC-7)
### <Entity> lifecycle — terminal: <states>
| State ↓ · Event → | <event> | <event> |
|---|---|---|
| <STATE> | → <STATE> (#1) | ✗ <error outcome>; state unchanged |
| # | Transition | Who may | Guard | Side effects in order (audit, notification, recompute) | Ordered-set effect + worked example |
|---|---|---|---|---|---|

## 6. Inherited Behaviour Inventory (ELIC-5)
| INH | Source (prototype · legacy · port; where) | Behaviour observed (concrete) | Keep → id · Change → id · Remove · Unknown → OQ | Suspected bug? (why) | User decision |
|---|---|---|---|---|---|

## 7. External interfaces and facts (ELIC-10)
### <SYS> — <system> (context.md §7)
| # | Fact needed | Used by (ids) | EXT id (existing, or reserved new: highest + 1 — the Tester adopts it) | Status (VERIFIED · UNVERIFIED) | Statement source (who · document) | Flag (UNVERIFIED driving time, money, security or lifecycle) |
|---|---|---|---|---|---|---|
| # | Failure (timeout · refused credentials · rate limit · server error · malformed · empty · late or duplicate · unconfigured) | What the user sees | What the system does (retry? state?) | AC |
|---|---|---|---|---|
An UNVERIFIED fact driving time, money, security or lifecycle blocks enabling its feature: the requirement is
flag-off and fail-closed, with a §12 row "blocks flag:<name>". A new or changed system or fact here → Facts needed (reply).

## 8. Data Volume Profile deltas (ELIC-12)
| Collection | Typical | Max observed (source) | Real ordering: first · default · earliest | vs context.md §6 |
|---|---|---|---|---|

## 9. Privacy (ELIC-13)
| Personal field or dataset | Purpose | Basis | Seen by (§2 rows) | Retention | Deletion | Export | Never in (logs · analytics · URLs · third parties) | Ids / D-n |
|---|---|---|---|---|---|---|---|---|
- Consent capture and withdrawal → <ids | none> · account deletion → <id> · data export → <id>

## 10. Operability defaults (RULES rule 8; ELIC-14)
| Default | Requirement id | This cycle: new · changed · re-verify · unaffected — why · N/A by Applies when — why · waived D-n |
|---|---|---|
| deploy · same-version redeploy | | |
| rollback while busy · after a migration | | |
| backup → restore drill | | |
| first start on empty infrastructure · fresh clone → running from the docs | | |
| health and version · log levels · alerting | | |
| flag semantics (hot or restart, per flag) | | |
| profile extras (cli, library: publish, install, withdraw · data-pipeline: replay, backfill) | | |

## 11. Domain model (conceptual)
| Entity | Meaning (users' words) | Key attributes | Relationships | Lifecycle (§5) | Personal data (§9) |
|---|---|---|---|---|---|
| Entity · verb (create · read one · list · update · delete · archive · restore · export · import) | Principal | Requirement id, or "not offered — <reason> (D-n)" |
|---|---|---|

## 12. Assumptions and open questions (ELIC-19) — each one unresolved at archive becomes a RISK
| Kind (assumption · question) | Id (A-n · OQ-n) | Statement | Source | Owner | Blocking? — blocks Gate 1 · Gate 2 · flag:<name> · none | Status (open · answered D-n · verified EXT-…) |
|---|---|---|---|---|---|---|

## 13. Challenges to the BRD
| brd § | Challenge (error handling · authorization · validation · state · data · security · privacy · scope) | Example showing why | Question for the user | Blocking? |
|---|---|---|---|---|

## 14. Contradictions with catalogue BRs, invariants and decisions
| # | This cycle's item | Contradicts (catalogue BR · invariant · D-n · gate resolution) | Conflict shown by example | Decision needed (§12 id) |
|---|---|---|---|---|

## 15. Catalogue delta (rows exactly as they will read in catalogue.md)
### Add
| ID | Area | Role | Story | Source | Status |
|---|---|---|---|---|---|
| <AREA>-n | <area> | <principal> | <one sentence in users' terms; NF measurable; BR with its boundary values> | C### | active |
### Change (whole new row)
| ID | Area | Role | Story | Source | Status |
|---|---|---|---|---|---|
### Retire
| ID | Area | Role | Story | Source | Status |
|---|---|---|---|---|---|
| <AREA>-n | <…> | <…> | <story unchanged> | C### → <successor id> | retired |

## 16. Summary
| Item | New | Changed | Removed | In scope |
|---|---|---|---|---|
| <one row each: functional · ACs · NF · BR · INH · Unknown INH · suspected bugs · facts · UNVERIFIED facts · reserved EXT ids · money movements · expected-output tables · A · OQ · blocking OQ · challenges · contradictions> | | | | |
| Lens (ELIC-2 to ELIC-17, ELIC-22) | Section | Applies? (yes · N/A — reason) |
|---|---|---|

## Traceability
| Requirement | Status (new · changed · removed · re-verify) | Source (brd § · D-n · DEF-n · CR-n · INH-n) | ACs | Linked (BR · NF · EXT · INH · flags) | Catalogue delta (add · change · retire) |
|---|---|---|---|---|---|
