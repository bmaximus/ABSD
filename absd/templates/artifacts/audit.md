<!-- ABSD skeleton: copy to absd-project/working/audit.md; keep every heading (tools read them).
     Owner: auditor. -->
# Audit — C### <slug>
Cycle: C### | Mode: F | S | C | D | B | X | R | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Scope: cycle (C###) | defect (DEF-n, …) | cross-cycle (C00a–C00b) · widened by: <brief | none> · narrowing refused: <quote | none>
Audited product SHA: <sha> (last commit changing a path outside `absd-project/`; run in a clean checkout of <commit>)
Start <sha> · T-SHA chain (oldest first): <sha, …> · Builder pass <n>/3 · iteration <n>
Overall: <PASS | FAIL | BLOCKED>
Findings open: Critical <n> · Major <n> · Minor <n> — new <n> · resolved <n> · re-raised <n>
Progress: [ ] runs [ ] reconcile [ ] report [ ] L1–L8 [ ] test changes [ ] probes [ ] sweeps [ ] findings [ ] commit

<!-- The Overall line stays outside every table; gate3 reads the first line starting "Overall:" and passes only PASS.
     Set it last: until then it keeps its <…> placeholder, which gate3 reads as missing. A section the mode does not
     use reads "N/A — <mode>"; never delete a heading. -->

## 1. Scope and inputs
Profiles · in-scope requirement ids · artifacts read (path @ sha) · trace_check presets run = the gates in the `cycle.md` ledger, with `--external-facts <path>` · whole-repository sweeps (always) · Mode S / D / X specifics

## 2. Execution evidence (run before reading `test_report.md`)
| # | Suite / gate | Command (`context.md` §4) | Where: clean checkout / CI run URL | Commit (product paths = audited product SHA) | Exit | Executed | Passed | Failed | Skipped | Retried | Output |
|---|---|---|---|---|---|---|---|---|---|---|---|

## 3. Reconciliation
Plan: planned <n> · executed <n> · first-attempt pass <n> · missing <TC ids> · skipped 0 · pass-on-retry 0
`test_report.md` product SHA: <sha> — equals the audited product SHA: yes / no → F-n

| Test file | Tests now | At start SHA | Δ explained by: amendment / Verify addition / retired id |
|---|---|---|---|

| `test_report.md` claim | Own result (#) | Agrees |
|---|---|---|

## 4. Levels
| Level | Verdict: PASS / FAIL / BLOCKED / N/A — profile or absent-subject reason, with evidence | Evidence # | Findings |
|---|---|---|---|
| L1 Architecture · L2 Design · L3 Requirements · L4 Code · L5 Security & privacy · L6 Test suite · L7 Operability · L8 Process — one row each | | | |

### L1 … ### L8 — one subsection each: executed, read, observations, finding ids

### L7 Operability defaults (RULES rule 8)
| Default (rule id) | Its *Applies when* covers a declared profile: yes / no (N/A, no waiver) — condition quoted | Evidence # or the user's waiver D-n | Verdict |
|---|---|---|---|

### L8 Artifacts changed after their gate
| Artifact | Gate passed at (sha) | Changed in (commit) | Only appends to an append-only section: yes / no | gateT re-run in `cycle.md` | Verdict |
|---|---|---|---|---|---|

### L8 Mode S eligibility (XCA-11)
| Criterion (ELIC-1) | Diff evidence (#) | Touched: yes / no |
|---|---|---|

## 5. Test changes since the first T-SHA (XCA-4)
Chain: `ownership_check.py --base <default branch> --t-sha <first> --t-sha <amendment> …` (#n) · review-list rows <n>

| Commit | File | Change: expected value / assertion / skip / retry / threshold / structure | Source: amendment (plan §16 + `cycle.md` approval) / Verify addition (plan §17) / correction-log ref | Verdict |
|---|---|---|---|---|

## 6. Probes — throwaway worktree outside the repository, removed; product paths unchanged (`git diff --quiet <product SHA> HEAD -- . ':!absd-project'`)
| Rule (id) | Fault (patch #) | Failing TCs | Verdict: caught / survived → F-n |
|---|---|---|---|

| Rule (id) | Fresh case: inputs → expected, worked from `analysis.md` | Actual (#) | Verdict |
|---|---|---|---|

| Sweep (ESC-7, replaced integration, deviation wording, markers, secrets) | Searches | Hits | Disposition |
|---|---|---|---|

## 7. Defect scope (Mode D)
| DEF | Class | RED at pre-fix <sha> (#) | GREEN at audited (#) | Kind of test fixed | Sweep rerun (#) | Original fault caught | Verdict |
|---|---|---|---|---|---|---|---|

External-fact change at Reproduce (EXT-4: recording, independent source, contract TC, fakes, live check, `EXTERNAL-FACTS.md` row; no production code): <# | not this class>
"Binds at re-bind" TCs red in a later T-SHA of the chain before the fix: <TC ids, # | none>
Design QA (`design_review.md`): required — fix changes a visual or output surface / UX gap: <yes / no> · present: <yes / no>
Containment of a live Critical: <D-n + RISK-n | none>

## 8. Cross-cycle (Mode X, R)
| Lens (XCA-13) | Commands / evidence # | Verdict | Findings |
|---|---|---|---|

| Accepted finding (`context.md` §13) | Accepted on / expiry | Re-raised as |
|---|---|---|

## 9. Findings
| ID | Severity | Category | Rule cited | Evidence | Proposed route | Status |
|---|---|---|---|---|---|---|
<!-- e.g. | F-1 | Critical | L6 money rule unguarded | ABSD:XCA-5, <AREA-BR-n> | #14: `>=` → `>` at <path:line> survived every TC | Tester: failing TC, then Builder Fix | open |
     Status: open · resolved — <evidence #, product SHA> · accepted-by-user (<context.md §13 row or D-n>).
     Only Status starts with a closing word (fixed, resolved, accepted-by-user); Proposed route never does. -->

## 10. Proposed register rows (the Manager records them)
| Kind: RISK / DEBT / DEF (`context.md` §16 backlog) / LEDGER candidate | Statement | Source (finding, limitation) | Blocks |
|---|---|---|---|

## Iteration <n> — audited product SHA <sha> · trigger: fix pass <n> / close-out edit / merge · product diff <sha>..<sha>   (append-only)
Runs (§2 format) · levels (§4 format) · fix-diff review · probes on touched rules

| Finding | Severity | Result: RESOLVED / ACCEPTED / CARRIED / NEW / PRE-EXISTING | Failing TC before the fix (#) | Status | Evidence # |
|---|---|---|---|---|---|

New and pre-existing findings: full rows in the §9 format, new ids.

## Traceability
| Requirement / AC / BR / NF in scope | TCs | Result at audited product SHA (#) | Findings |
|---|---|---|---|
