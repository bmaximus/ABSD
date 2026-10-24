<!-- ABSD skeleton: copy to absd-project/working/cycle.md; keep every heading (tools read them).
     Owner: manager. -->
# Cycle C### — <slug>
Cycle: C### | Mode: <one letter: F/S/D/B/X/R/U/P — a CR keeps the cycle's letter> | Status: IN-PROGRESS/COMPLETE/PARKED | Date: YYYY-MM-DD
- Scale: <F | S> · Profiles in scope: <…> · ABSD version: <x.y.z> · Trigger (D/R/X/U): <…>
- Branch: `absd/C###-<slug>` · Default branch: <name, context.md §1> · Start SHA: <sha>
- T-SHA chain: <first T-SHA | not yet> → <later links, see "T-SHA chain"> · G3 product SHA: <sha | not yet>
- Start checks (manager.md 6.1): kit check <green> · nightly/live <green | run triggered <date> | waiver D-n + RISK-n> ·
  Mode X due <no | ran in C###> · backlog reviewed <date>

## Mode S eligibility (ABSD:ELIC-1; any yes or not sure → Mode F)
| # | Touches … | Answer | Reason |
|---|---|---|---|
| 1 | a principal, role or permission | <no> | <…> |
| 2 | an external integration | | |
| 3 | persistent schema or a migration | | |
| 4 | adds or removes a screen, endpoint, command or public symbol, or changes an interface contract | | |
| 5 | money or calculation logic | | |
| 6 | date, time or zone logic | | |
| 7 | auth or session logic | | |
| 8 | delete or retention logic | | |
| 9 | a background job | | |
| 10 | a config key or feature flag | | |
| 11 | more than 10 production files | | |

## Route
| Step | Agent · mode | Gate | Status (pending / running / done / skipped — reason) |
|---|---|---|---|

## Gate ledger
| Gate | Round | Verdict | Product SHA | Date | trace_check invocation | Notes (spot checks, ownership_check invocation, D-n) |
|---|---|---|---|---|---|---|

## T-SHA chain (oldest first; ownership_check takes every link: `--t-sha <first> --t-sha <next> …`)
| # | T-SHA (evidence commit) | Tests commit it ran at | Cause (Plan & Bind / Reproduce / amendment / re-bind after CLR-n, TSEAM-n or CR-n) | Date |
|---|---|---|---|---|

## gateT re-runs (after every approved amendment and every Verify)
| After (amendment TC-nnnn / Verify iteration n) | Product SHA | Invocation | Result | Date |
|---|---|---|---|---|

## Counters
- Builder passes 0/3 · gate rounds G1 0/3, GUX 0/3, G2·2R 0/3, GT 0/3, Design QA 0/3 · halts 0/3 · resumes 0/2

## Invocation log
| # | Time | Agent | Mode | Brief summary | Reply status | Commit |
|---|---|---|---|---|---|---|

## Resume point
- Next action: <exact next step> · Waiting for: <agent reply | user answer to … | nothing>
- In flight: <agent · mode · log # | none>

## Pending routes
| Item (finding, CLR, CR, TSEAM, TC-CONFLICT, spec defect, amendment awaiting approval) | Owner | Route | Status |
|---|---|---|---|

## Amendment approvals (Gate T, ABSD:ORACLE-2)
| TC | Old → new | Reason and source | Decision (approved / rejected — why) | Date |
|---|---|---|---|---|

## Decisions (process; product decisions live in brd §9 or defect.md)
- <date> — <decision> — <who>

## Close (DOD rows)
| Row | Holds | Evidence (command output, CI run at the product SHA, artifact §, commit) |
|---|---|---|
