<!-- ABSD skeleton: copy to absd-project/working/test_report.md; keep every heading (tools read them).
     Owner: tester. -->
# Test report — C### <slug>
Cycle: C### | Mode: … | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Product SHA: <sha> — the last commit outside `absd-project/` this report verified; every result was taken there (valid while `git diff --quiet <sha> HEAD -- . ':!absd-project'`)
T-SHA chain: <sha, …> · Builder pass <n>/3 · Verify iteration <n>
Findings: Critical <n> · Major <n> · Minor <n>
Progress: [ ] conflicts [ ] suites [ ] additions [ ] gates [ ] gallery [ ] exploratory [ ] docs [ ] tests commit [ ] evidence run [ ] report commit

Append-only: §17 iteration rows.

## 1. Evidence index
| # | Command or CI job | Product SHA | Exit | Output path or run URL |
|---|---|---|---|---|

## 2. Results by suite and project
| Suite | Project (device / zone / runtime) | Planned | Executed | Passed | Failed | Skipped (0) | Passed on retry (0) | Evidence # |
|---|---|---|---|---|---|---|---|---|

## 3. Catalogue — verified <n> · failing <n> · untested <n> · unknown <n>; in-scope ids with state; untested trend
## 4. Plan conformance (one run over index + parts) — planned <n> · passing · missing · failing · unplanned (each: earlier cycle or Verify addition)
## 5. Coverage — total <x>% vs floor <y>% · per layer vs its floor · floor raised to · untested units · allowlist diff with reasons; stale lines removed
## 6. Mutation — changed code <x>% vs <t>% · per money/time/access rule: mutants, killed, controls · survivors → resolution

## 7. Flakes
| Test | Added or changed this cycle? | Symptom: retry / order / parallel / host | Deterministic reproduction (seed, repetition, workers, held response, clock) | Cause: harness (seeded red → green evidence) / product race | TF / proposed DEF |
|---|---|---|---|---|---|

## 8. Gates: a11y, performance, visual, access completeness, error signals, migrations, boot, smoke, canaries, ownership, trace
| Gate | Command | Result (counts, measured values) | Evidence # |
|---|---|---|---|

## 9. External facts
| EXT | Recorded contract TC | Last live run (date, product SHA) | Status | Flag depending on it |
|---|---|---|---|---|

## 10. Conflicts and failures
| Item (TC-CONFLICT-n or TC) | Failing assertion | Class | Evidence | Route |
|---|---|---|---|---|

## 11. Findings
| ID | Severity | Category | Rule cited | Evidence | Proposed route | Status |
|---|---|---|---|---|---|---|

A row reads: `TF-1 | Critical | implementation (wrong money) | ORD-BR-3.AC2 | TC-0042: 53.98, expected 53.97 (evidence #4) | Builder Fix | open`

Status: open · fixed — verified at <product sha> by <TCs> · accepted-by-user (context.md §13)

## 12. Test corrections since T-SHA
| Commit | File | Diff summary | Why no expected value or assertion meaning changed |
|---|---|---|---|

## 13. Exploratory
| Charter | Device | Minutes | Findings → TF / DEF / decision | EXPLORATORY.md entry |
|---|---|---|---|---|

## 14. Gallery / golden outputs (rows = component–state matrix cells)
| SCR or output | State | Device | Theme | Path | Golden source (`SPEC:` example table; human-facing: Designer row) |
|---|---|---|---|---|---|

## 15. Proposed register rows (the Manager records them; DEF rows go to the `context.md` defect backlog)
| Kind: RISK / DEBT / DEF | Statement (DEF: title, XCA-7 level, proposed class) | Source | Blocks |
|---|---|---|---|

## 16. Open risks and blocked evidence

## 17. Iterations (append-only)
| Iteration | Product SHA | TFs fixed | new | still open |
|---|---|---|---|---|

## Facts (Facts mode)
| EXT (reserved id adopted) | System | Checklist row | Status: VERIFIED / UNVERIFIED / N/A — reason | Recording (scrubbed path) | Independent source | Proposed RISK `blocks: flag:<name>` |
|---|---|---|---|---|---|---|

## Baseline (Baseline mode)
| Matrix row | Existing home | Ran at product SHA | Result | Gap → proposed DEBT |
|---|---|---|---|---|

| Inherited asset (living doc, registry, allowlist, workflow, test without TC id) | Action: converted / relinked / moved / retrofitted / exemption <YYYY-MM-DD> | Evidence |
|---|---|---|

## Negative controls (Foundation; whenever a gate changes)
| Gate | Control | RED evidence | GREEN evidence |
|---|---|---|---|

## Release (Mode R)
Last nightly and live runs · restore drill · fresh clone · UNVERIFIED facts vs enabled flags · human sessions · checklist

## Traceability
| Requirement / AC | TCs | Result at the product SHA | Evidence # |
|---|---|---|---|
