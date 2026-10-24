<!-- ABSD skeleton: copy to absd-project/working/arch_review.md; keep every heading (tools read them).
     Owner: auditor. -->
# Architecture review — C### <slug>
Cycle: C### | Mode: F | S | C | D | B | R | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Reviewed: `architecture.md` at <sha> · round <n>/3 · scope: full | delta (§…) | Foundation ADRs | none (route without Gate 2R)
Verdict: <PASS | FAIL | N/A — no architecture change on this route (<mode or class>)>
Findings open: Critical <n> · Major <n> · Minor <n> (resolved <n>)
Progress: [ ] decisions [ ] checklist [ ] probes [ ] findings [ ] resolution [ ] commit

<!-- The Verdict line stays outside every table; gate3 reads the first line starting "Verdict:" (PASS or N/A passes).
     Set it last: until then it keeps its <…> placeholder, which gate3 reads as missing. -->

## 1. Inputs and scope
brd Decisions D-1…D-n · `analysis.md` <sha> · `design.md` <sha> · profiles · sections reviewed (delta: + what they touch)

## 2. Gate decisions honoured (ARCH-7)
| Decision / resolution / BR | Source | Implementing section | Verdict: honoured / contradicted → AR-n / missing → AR-n |
|---|---|---|---|

## 3. Review checklist (`absd/playbook/engineering/architecture-review.md`, in its order; no blank row)
| Item | Rules | Evidence (section, quote, path:line) | Verdict: OK / AR-n / N/A — profile or absent-subject reason |
|---|---|---|---|

## 4. Probes (one row per probe of the auditor manual §4.1 step 3, in its order)
| Probe | Method | Result (evidence #) |
|---|---|---|

| Component (SOLID sample) | Layer | S | O | L | I | D | Patterns → force |
|---|---|---|---|---|---|---|---|

## 5. Findings
| ID | Severity | Category | Rule cited | Evidence | Proposed route | Status |
|---|---|---|---|---|---|---|
<!-- e.g. | AR-1 | Major | Reads | ABSD:ARCH-9 | §5.2: SCR-4 history view has no read; only the mutating update | Architect delta | open |
     Status: open · resolved — <round, sha> · accepted-by-user (<D-n>). Only Status starts with a closing word. -->

## 6. Resolution table (the post-build audit reads only this)
| AR | Severity | Resolution (section / ADR) | Verified at (sha, round) | Status |
|---|---|---|---|---|

## 7. Disputes (XCA-10)
| AR | Architect's ADR | Auditor's position | Outcome: resolved — withdrawn on ADR-n / user decides → D-n |
|---|---|---|---|

## 8. Rounds
| Round | Architecture SHA | Verdict | New | Resolved | Still open |
|---|---|---|---|---|---|

## Traceability
| Requirement / UJ / SCR / EXT (every id in scope) | Architecture section | AR ids or none |
|---|---|---|
