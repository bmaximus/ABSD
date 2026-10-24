<!-- ABSD skeleton: copy to absd-project/working/build_log.md; keep every heading (tools read them).
     Owner: builder. -->
# Build log — C### <slug>
Cycle: C### | Mode: F/S/D/C/B | Status: IN-PROGRESS | COMPLETE | COMPLETE-WITH-CONFLICTS | HALTED | BLOCKED | Date: YYYY-MM-DD
Inputs: architecture.md @<sha> (2R PASS round <n>) · design.md @<sha> · test_plan.md @<latest T-SHA> · context.md @<sha>
Branch: absd/C###-<slug> · start <sha> · T-SHA chain <first sha, …> · Builder pass <n>/3 · halts <n>/3
Progress: [ ] read [ ] scan [ ] baseline run [ ] WP-1 … WP-n [ ] close   (Fix: [ ] <finding ids> [ ] close)

## 1. Pre-generation scan (builder manual §6.1)
| Check | Items checked (n) | Result: ✓ / CLR-n / TC-CONFLICT-n |
|---|---|---|

## 2. Baseline run at <sha>
| Suite · test unit | Keyed to (test_plan.md §12: WP-n · none) | Green (must stay green) | Red (cycle TCs) | Not compiling: pending WP-m | Evidence # |
|---|---|---|---|---|---|

## 3. Work packages
| WP | Purpose (architecture §20) | Files (n) | WP-start SHA | Commit | Build | Static | Test units: compiled · pending WP-m | Fast suite: pass / fail / pending | TCs turned green | TC-CONFLICT | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|

Status: pending · in-progress · committed · halted · blocked

## 4. Files produced
| # | Path | Action: create / modify / delete | WP | Architecture § | Owner glob (context.md §3) |
|---|---|---|---|---|---|

## 5. Migrations
| Migration | WP | Tool command (verbatim) | Generated files | Data steps added (architecture §4) | From-empty run | Evidence # |
|---|---|---|---|---|---|---|

## 6. Evidence
| # | WP / fix | Command (context.md §4) or CI job | Product SHA | Exit / conclusion | Output path or run URL |
|---|---|---|---|---|---|

## 7. TC-CONFLICT
| TC-CONFLICT | TC · test (file:line) | Failing assertion: expected → actual (verbatim), or compiler error | Test's cited source | Your citation (architecture § · analysis id · design id) | Why the code is right | WP | Evidence # |
|---|---|---|---|---|---|---|---|

## 8. Fix passes
### Pass <n>/3 — YYYY-MM-DD — findings: <C###/TF-n, DQ-n, F-n, DEF-n>
| Finding | Severity | Failing TC (red before the fix) | Root cause (file:line) | Change (files) | Fix-start SHA | Commit | TCs green | Evidence # | Outcome: fixed / TC-CONFLICT-n / CLR-n |
|---|---|---|---|---|---|---|---|---|---|

## 9. Notes (facts only)
- <observation> — never a decision, assumption, workaround or suggestion: a deviation would have been a halt

## 10. Statistics
Files created <n> · modified <n> · deleted <n> · migrations <n> · WPs <n>/<n> · TCs turned green <n> ·
TC-CONFLICT <n> · CLR <n> · suppression markers added <n> (all in architecture §19) ·
dependencies added <n> (all in the architecture's dependency table)

## 11. Traceability
| Upstream id (requirement · AC · QC · DEF — architecture §20 "Delivers") | WP / fix | Files | Commit | TCs green at that commit |
|---|---|---|---|---|
