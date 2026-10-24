<!-- ABSD skeleton: copy to absd-project/working/design_review.md; keep every heading (tools read them).
Owner: designer. -->

# Design review — C### <slug>
Cycle: C### | Mode: F | S | D | B | … | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Product SHA reviewed: <S — the gallery's, from test_report.md> (valid while `git diff --quiet <S> HEAD -- . ':!absd-project'` holds) · gallery index: test_report.md @<sha> · design.md @<sha> · design-system.md @<sha> · iteration <n>

Verdict: <PASS | FAIL | BLOCKED | N/A>

Findings open: Critical <n> · Major <n> · Minor <n>
Progress: [ ] coverage [ ] images [ ] cross-screen [ ] golden [ ] rubric [ ] baselines [ ] findings [ ] commit

## 1. Scope
Profiles with a visual or human-facing output surface · SCR × state × device × theme in scope · golden files in scope
(cli human output, reports, rendered documents) · excluded (reason) · N/A: <why no visual or output surface is in scope>

## 2. Coverage (rows = matrix cells × device class × theme)
| SCR | State | Device | Theme | Image / golden path | SHA-256 | Reviewed | Result: OK / DQ-n |
|---|---|---|---|---|---|---|---|

Missing cells or a product path changed since S: <none | list → Verdict BLOCKED>

## 3. Observations per screen or command
### SCR-n — hierarchy (squint) · grid alignment · type and colour counts · copy vs deck · formats · label maps · truncation · states · targets · focus · safe areas · motion

## 4. Copy and format diff
| Image | Rendered text | design.md key / literal | Match |
|---|---|---|---|

## 5. Rubric — design score vs rendered score (one row per dimension and declared profile, DSN-19)
| Dimension | Profile | design.md §20 | Rendered | Evidence (image paths, golden files, measurements) |
|---|---|---|---|---|

## 6. Baselines and golden files
| SCR / command / output | State / variant | Device | Theme | Path | SHA-256 | Decision: approved / rejected — reason | Intended by (design.md §18 · CR-n) |
|---|---|---|---|---|---|---|---|

## 7. Findings
| ID | Severity | Category | Rule cited | Evidence | Proposed route | Status |
|---|---|---|---|---|---|---|
| DQ-n | Critical / Major / Minor | <category> | ABSD:<CODE-n>, <AREA-n> | `<image or golden path>`: <what is wrong> | Tester · failing TC → Builder · Fix / Designer · Design delta | open |
<!-- e.g. | DQ-1 | Major | raw value shown | ABSD:LOC-1, <AREA-n> | `absd-project/working/evidence/tester/screens/SCR-3_populated_phone_dark.png`: status column shows the enum name | Tester · failing TC → Builder · Fix | open | -->

## 8. Proposed register rows (the Manager records them)
| Kind: RISK / DEBT / DEF | Statement | Source | Blocks |
|---|---|---|---|

## Iteration <n> — reviewed product SHA <sha> · trigger: fix pass <n>   (append-only)
| Finding | Severity | Result: RESOLVED / CARRIED / ACCEPTED / NEW | Status | Evidence |
|---|---|---|---|---|

## Traceability
| UJ / SCR | Images reviewed | Findings |
|---|---|---|
