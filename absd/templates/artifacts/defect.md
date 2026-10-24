<!-- ABSD skeleton: copy to absd-project/working/defect.md; keep every heading (tools read them).
     Owner: manager. -->
# Defects — C### <slug>
Cycle: C### | Mode: D | Status: IN-PROGRESS/COMPLETE | Date: YYYY-MM-DD
- Class (one for the whole batch; proposed by the Tester at Reproduce, set at Gate T — ABSD:ESC-6, ABSD:ESC-12):
  <implementation | architecture gap | external-fact gap | UX gap | requirements gap | test-only gap | not yet>
- Route after Gate T: <manager.md 4.4 row for the class> · Design QA: <yes — visual or output surface changes / UX gap | no — reason>

| DEF | Title | Found by (user / live / exploratory / audit / nightly / CI / sweep) | Found on (date, environment, product SHA) | Principal × device/runtime | Severity | Backlog row (context.md §16) / source (C###/F-n, sweep) | Ids (requirement / AC / SCR / EXT) | Status (open / fixed / removed — moved to C###) |
|---|---|---|---|---|---|---|---|---|

## Containment (a Critical on a live system — before Reproduce)
| DEF | Live since | Contained by the user (rollback to <version> / flag <name> off / none possible — why) | Done at (date, time) | Decision D-n | RISK-n (context.md §11) | Mode R before re-enabling (ABSD:DOD-7) |
|---|---|---|---|---|---|---|

## DEF-n — <title>
- Observed: steps with concrete values → actual result
- Expected: <behaviour> — source: catalogue id / AC / SCR / EXT id, or "unspecified → decision D-n"
- Evidence: <paths under absd-project/working/evidence/manager/, logs, the reporter's words verbatim>
- Reproducibility: always / n of m / once · Impact: who, how many, money, data, security
- Mechanism suspected in an external fact? <no | yes — EXT id or system> (the Tester verifies it at Reproduce, ABSD:EXT-4)
- Class: <proposed at Reproduce → set at Gate T> · Moved to: <— | C###>

## Decisions (answered by the user only)
| D | Question | User's answer | Date |
|---|---|---|---|

## Traceability
| DEF | Requirement / AC / EXT ids |
|---|---|
