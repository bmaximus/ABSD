<!-- ABSD skeleton: copy to absd-project/working/test_plan.md; keep every heading (tools read them).
     Owner: tester. -->
# Test plan — C### <slug>
Cycle: C### | Mode: F/S/D/B/C | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Inputs: analysis.md @<sha> · design.md @<sha> · architecture.md @<sha> (2R PASS, round <n>) · catalogue.md @<sha>
Profiles: <…> · Device/runtime projects: <…> · Foreign zone/locale: <…> · Next TC: TC-<nnnn>
Progress: [ ] inventory [ ] spec defects [ ] plan [ ] bind [ ] self-check [ ] tests commit [ ] red run [ ] evidence commit

Append-only after Gate T: §14, §16, §17 (incl. its iteration rows) — add rows; an earlier row changes only in its
Status cell.

## 1. Scope and applicability (cites TESTING.md §1; never re-argued)
| TESTING.md row | Cell M/R/X | R trigger ids, or "no trigger: <ids checked>" | TCs |
|---|---|---|---|

Out of scope: <ids — reason> (a mention here is not coverage)

## 2. Spec defects
| # | Blocking (yes/no) | Source (id / §) | Defect | Owner | Question | Status: open / answered <ref> / resolved / withdrawn |
|---|---|---|---|---|---|---|

## 3. TSEAM requests
| TSEAM | Kind: seam / tooling | What the test must control or observe (tooling: file and setting) | TCs waiting | Seam requested (behaviour, not code) | Status: open / specified <architecture §, sha> / withdrawn |
|---|---|---|---|---|---|

## 4. Variation coverage (VAR-1)
| Item (AC, BR, state machine, flow, risk) | Dimension (variation catalogue) | Technique | TCs, or "N/A — reason" |
|---|---|---|---|

## 5. Oracle table (### per area)
| TC | Level | Purpose | Profile / device | Requirement ids | Inputs | Expected (oracle) | Source | Derivation | Status (planned/removed) |
|---|---|---|---|---|---|---|---|---|---|

A row reads: `TC-0042 | unit | acceptance | — | ORD-BR-3 | 3 × 19.99, 10 % off, half-up | 53.97 | SPEC:ORD-BR-3.AC2 | 59.97 × 0.90 = 53.973 → 53.97 | planned`

Level: unit · component · integration · contract · e2e. Purpose: acceptance · access · chain · smoke · regression
DEF-n · nfr · char INH-n · a11y · visual · perf · security · migration. Source, always prefixed: `SPEC:<REQ>[.AC<n>]` ·
`SPEC:<UJ-n|SCR-n>[.<state>]` · `SPEC:architecture §<x>` (only rows citing no requirement id) · `FACT:EXT-<SYS>-<n>`
(VERIFIED) · `CHAR:INH-<n>` (user-confirmed Keep). Code is never a source. Status: `planned` · `removed — #<§16 row>`
(the row stays). A TC whose oracle is an input table gets a `### TC-<nnnn>` heading with the table under it.

### Decision tables (interacting BRs) · State transitions (state × event → next state, side effects, or error)

## 6. Access and visibility (data file: <path>)
| Operation | Principal (role × entitlement) | Owner relation | Resource state | Flag | Outcome | Visible records / fields | Forbidden — asserted absent | TC |
|---|---|---|---|---|---|---|---|---|

## 7. External facts and fakes
| EXT | Status | Contract TC | Parity: recording · unit fake · HTTP fake · e2e fake | Failure classes → message TC | Live check |
|---|---|---|---|---|---|

## 8. Chains and flow steps
| Flow step (architecture §) | Recorded payload | Asserted effect (persisted + shown) | TC |
|---|---|---|---|

## 9. Devices, zones, locales, volume, time
| Rule / screen | Projects | Volume + position of the special item | Instants (zone chain, DST, month/season ends) | Real-time crossing | TCs |
|---|---|---|---|---|---|

## 10. Non-functional
| REQ-NF or default | Metric | Dataset | Environment | Threshold | TC |
|---|---|---|---|---|---|

## 11. Existing tests affected (changed oracle, retired or relinked id)
| # | TC | Changed / retired id | Old oracle → new | Source | Action: relink / amend / remove |
|---|---|---|---|---|---|

## 12. Harness, data and gates
Builders · seeds (volume, order; data a new TC needs is arranged in that TC, never in the shared seed) · fakes,
recordings (EXT ids) · golden files (each citing its `analysis.md` example table) · golden vectors · error-signal
fixture · overrides (endpoints, credentials) · lanes, thresholds (TESTING.md §2; a change = amendment)

| Test unit (project / module / file) | WP that introduces its new symbols, or "none — green at T-SHA" | TCs |
|---|---|---|

## 13. Exploratory charters
| # | Principal | Device class | Mission: explore <target> with <data> to discover <risk> | Tours | Oracles | Targets |
|---|---|---|---|---|---|---|

## 14. Red evidence index (append-only)
| # | TC | Run at (tests commit) | Red reason · negative control · binds at re-bind (DEF class) | Evidence path |
|---|---|---|---|---|

## 15. Reproduce (Mode D) — ### DEF-n each
Regression TCs (level; surface) · red at <pre-fix product sha> · external fact verified now: EXT-<SYS>-<n> | n/a ·
why missed: #<n> <class> (+ secondary), <path:line> · kind of test fixed: <…> · proposed class + citations · should
have caught it: <gate> + ABSD:<rule> | none — gap · recurrence: <earlier rows | none> · binds at re-bind: <TCs, owner
delta | none>

| Search (pattern, tool) | Scope | Hits | Disposition: TC / at Verify / proposed DEF (backlog) |
|---|---|---|---|

## 16. Amendments (append-only)
| # | TC | Old → new oracle | Reason (ORACLE-8 class) | New source | Approval: cycle.md <ref>; user's for any loosening | Status: requested / approved / applied <tests sha> |
|---|---|---|---|---|---|---|

## 17. Verify additions (append-only)
| TC | Level | Purpose | Requirement ids | Inputs | Expected | Source | Why: untested unit / survivor / sweep / finding C###/F-n, DQ-n / flake | Status (planned/removed) |
|---|---|---|---|---|---|---|---|---|

### Iterations
| Verify iteration | Product SHA | TCs added | Amendments applied |
|---|---|---|---|

## 18. Traceability
| Upstream id (AC, BR, NF, UJ, SCR, EXT, operation, flow step, DEF) | TCs | Levels | Projects |
|---|---|---|---|
