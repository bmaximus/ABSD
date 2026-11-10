# Audits — evidence, levels, probes, severity

Code **XCA**. How the Auditor reaches independent technical verdicts in the cycle audit and the defect-scoped audit
(`audit.md`, levels L1–L8): independence, evidence, probes, finding proof, plan-versus-diff reconciliation and
severity. Reviews by mode (Gate 2R, Mode S, cross-cycle, security review, second auditor):
`absd/playbook/process/audit-modes.md`. The Auditor runs everything itself, sets scope and severity, and fixes nothing;
the Manager routes findings and never overrides them (`absd/RULES.md` §3 rule 10; finding rows: §6).

## Checklist

- [ ] Scope set by the Auditor, never narrowed; security sweeps cover the whole repository and its history (XCA-1)
- [ ] Every suite and gate run by the Auditor in a clean checkout of the product SHA before reading the Tester's report (XCA-2)
- [ ] Executed = planned, skipped = 0, counts per file reconciled; anything not run → BLOCKED (XCA-2)
- [ ] L1–L8 each with verdict and evidence; Overall PASS / FAIL / BLOCKED by the verdict rule (XCA-3)
- [ ] Every test change since the first T-SHA cites a Gate T amendment or a logged mechanical correction (XCA-4)
- [ ] Fault injected per money/time/access rule, each caught; 3 fresh cases per money/time rule; sweeps rerun (XCA-5)
- [ ] No rule violation rationalized; improvised deviations and "resolved inline" notes raised as findings (XCA-6)
- [ ] Severity per the calibration table; same class, same severity across cycles (XCA-7)
- [ ] Every finding proven: `file:line`, trigger, outcome, why guards miss it; security: reachability; none padded (XCA-14)
- [ ] Each WP's planned files, symbols, keys and dependencies reconciled with its commit's diff (XCA-15)
- [ ] Accepted findings: user-accepted, dated, expiring; re-raised at Mode X and R (XCA-8)
- [ ] Every product change after the audit re-verified and re-audited; iteration history appended in `audit.md` (XCA-9)

## Rules

### Independence and evidence

**XCA-1** — Set the audit's scope and severity yourself; a brief may widen scope, never narrow it. Secret, security and
invariant sweeps always cover the whole repository — legacy folders, scripts, docs, CI files and full history — whatever
the brief says; an instruction to narrow is itself recorded as a process finding.
- *Why:* the orchestrator limited a secret search to two folders and the same key survived in a legacy file (LL-43).
- *Check:* `audit.md` states the scope and the commands run over the whole tree and history; the brief in `cycle.md`
  contains no narrowing.
- *Applies when:* every 2R, audit and cross-cycle audit.
- *Provenance:* LL-43 (KatenatsioTipster, 2026-10)

**XCA-2** — Before reading `test_report.md`, run every suite and gate yourself in a clean checkout (a worktree outside
the project) of the product SHA under audit (`absd/RULES.md` §6) — every device and zone/locale project, recorded
contracts, access matrix, coverage, traceability, mutation, ownership checks and the `trace_check.py gate` presets of
the gates in the `cycle.md` ledger only, with `--external-facts` at the `context.md` path; then reconcile test case by
test case: executed = planned, skipped = 0, counts per file. A CI run substitutes only at that product SHA with its
job logs pulled and reconciled by you. The evidence stays valid while
`git diff --quiet <product SHA> HEAD -- . ':!absd-project'` holds: pipeline commits (artifacts, evidence, a parallel
Design QA) are never a reason to restart; a changed product path is. Anything you cannot run makes the verdict
BLOCKED, never PASS; the limitation becomes a RISK, never a design decision.
- *Why:* audits certified backend tests they had never run because "CI is the designated gate" (LL-24); measurable
  criteria passed by code reading (LL-45); "audited SHA = HEAD" broke at the next hand-off commit (LL-55).
- *Check:* `audit.md` records the product SHA and each command with exit code and counts, then a reconciliation table
  against `test_report.md`.
- *Applies when:* every audit (cycle, defect, cross-cycle).
- *Provenance:* LL-24, LL-45 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

**XCA-3** — Report each level below with a verdict (PASS, FAIL, BLOCKED, or N/A with its reason) and evidence.
Overall PASS only when no level is FAIL or BLOCKED and 0 Critical and 0 Major are open (new, carried or re-raised);
any BLOCKED level makes Overall BLOCKED.
- *Why:* per-level checks that read code passed four cycles whose missing migrations, untested criteria and broken
  defaults surfaced later (LL-14, LL-21, LL-45); tests written by the code author were never judged (LL-29).
- *Check:* eight level sections; each N/A by profile (`TESTING.md` X) or an absent subject (no jobs, flags, secrets,
  state) with the evidence; `Overall: PASS | FAIL | BLOCKED` outside any table (gate3 requires PASS, no open finding).
- *Applies when:* every audit.
- *Provenance:* LL-14, LL-21, LL-29, LL-45 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

| Level | What it checks (execute, then read) |
|---|---|
| L1 Architecture | Code = `architecture.md`: components, signatures, operations, wiring, config keys, each numbered data-flow step's persisted effect, 2R resolutions honoured, `build_log.md` free of improvisation |
| L2 Design | Built surfaces = `design.md` + design system: copy, states, formatters, accessible names, device behaviour; every DQ finding resolved |
| L3 Requirements | Catalogue report at the product SHA: every in-scope requirement verified on first attempt; every AC, BR clause and NF has an executed TC; "logic exists" never counts |
| L4 Code | CODE rules: analysers, warnings, complexity, dead code, dependencies; suppression markers only as listed in `architecture.md` (grep) |
| L5 Security & privacy | SEC, PRIV rules; whole-repo and history secret scan; canary gate; access matrix complete; threat-model TCs; personal data in logs |
| L6 Test suite | Oracle independence (no expected value from production code; 3 expected values checked against `analysis.md` examples); XCA-4; mutation score; 0 skipped; error-signal fixture used; flake report; allowlist diff; every N/A an X cell or an absent subject, with evidence (STRAT-4) |
| L7 Operability | Each default where its OPS *Applies when* covers a declared profile (an N/A by *Applies when* verified, no waiver needed): migrate from empty and from the previous release, drift check; shipped artifact boots on empty infrastructure; default-config run; config agreement; log levels; health and version; deploy and rollback tests; fresh clone → running from the docs |
| L8 Process | ownership_check (trailers, owners, kit-sync commits, T-SHA chain ancestry); clean hand-offs; gate ledger complete; no artifact written by a non-owner; every artifact changed after its gate re-passed it (appends to the append-only plan and report sections excepted, gateT re-run recorded: DOD-2 row 1); Mode S eligibility (XCA-11) |

**XCA-4** — List every test-path change after the first T-SHA of the chain in `cycle.md` (the Plan & Bind evidence
commit; each approved amendment or re-bind appends its own); each changed expected value, assertion, skip, retry or
threshold must cite an approved Gate T amendment, or be a mechanical correction in the Tester's log that changes no
expected value. Anything else is Major (Q1); a loosened gate is Critical.
- *Why:* when tests come after code, triage by whoever sees the code turns oracles into echoes of it (LL-29); one
  T-SHA made every re-bind "production before Gate T" or unamended test changes (LL-55).
- *Check:* `ownership_check.py --base <default branch> --t-sha <first> --t-sha <next> …` (oldest first) proves every
  Builder commit descends from the first and lists test files changed after it outside T-SHA commits; the Auditor
  reconciles the list with the amendments in `test_plan.md` §16.
- *Applies when:* every cycle with a T-SHA.
- *Provenance:* LL-29 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

### Adversarial stance

**XCA-5** — Probe, do not only read: in a throwaway worktree outside the project (under `$TMPDIR`, never
committed), inject at least one fault per money, time and access rule (flip a comparison, drop a filter, swap a field,
shift a zone) and confirm a test fails; derive three fresh cases per money and time rule from `analysis.md` and run
them; rerun every same-weakness sweep (ESC-7). Leave the audited tree byte-identical (`git status` clean, same HEAD). A
surviving fault is a missing test: Critical on these paths.
- *Why:* settlement tests fed settlement its own scores, so a misread field passed every test (LL-2); a client-declared
  value was trusted against a rule (LL-48); a sweep missed a status card naming a replaced provider (LL-17).
- *Check:* `audit.md` Probes table: rule → fault → failing TC (or "survived" → finding); fresh case → result; sweep →
  hits.
- *Applies when:* every audit touching money, time or access rules; sweeps in every Mode D audit.
- *Provenance:* LL-2, LL-17, LL-48 (KatenatsioTipster, 2026-10)

**XCA-6** — Never rationalize a violation: code or tests contradicting a catalogue BR, invariant, recorded decision or
playbook rule are a finding even when "backward compatible", "safe default", "YAGNI" or "same behaviour as before"; a
deviation from the blueprint noted as "resolved inline" or improvised (a mutating call used as a read, a class moved) is a
Major process finding plus the defect it hides.
- *Why:* an audit called a client-trusted value "the correct backward-compatible interpretation" (LL-48); the Builder
  improvised around a missing read and a dependency cycle instead of halting (LL-42); a decision was reversed (LL-44).
- *Check:* the Auditor greps `build_log.md` and code comments for deviation wording and maps each to a finding.
- *Applies when:* always.
- *Provenance:* LL-42, LL-44, LL-48 (KatenatsioTipster, 2026-10)

**XCA-7** — Grade every finding by the table: by its worst effect on any principal or data, not by likelihood; when two
rows fit, the higher wins; the same class gets the same severity in every cycle; only the finder sets it and the
Manager never downgrades it. A security finding's sink no shipped entry point reaches is graded per XCA-14.
- *Why:* a missing test for a money rule was Major in one cycle, Minor in another (LL-47).
- *Check:* each finding cites its table row; the Auditor compares classes with earlier audits.
- *Applies when:* every finding (AR, TF, DQ, F).
- *Provenance:* LL-47 (KatenatsioTipster, 2026-10); LL-65 (ECC evaluation, 2026-11)

| Severity | Finding classes | Examples |
|---|---|---|
| Critical | Wrong money, result, deadline, ranking or stored data; data loss; another principal's or paid data visible; auth or permission bypass; secret or personal data exposed | half-time score settled as final (LL-2); paid content in a free response (LL-10); secret in a CI log (LL-8) |
| Critical | A money, time, access or security rule with no test that fails when it breaks; a fault surviving XCA-5; a gate loosened without amendment; a mandated check silently not run | reader at 0% coverage on the money path (LL-2); live check exiting 0 without its credential (LL-25) |
| Major | Wrong behaviour elsewhere; a failure shown as a generic error; input lost to a refresh or gesture; a principal missing its core value | "Server error" for a service failure (LL-11); a dialog wiped every second (LL-12); admins unable to act as members (LL-5) |
| Major | Missing test for any other AC, BR, NF, state transition, access cell, flag state or data-flow step; untested oracle change (XCA-4); repeated class without a mechanical control (ESC-10) | step "delete provisional rows" never run (LL-51); flag-off path at 0% (LL-23) |
| Major | Drift from architecture, design or a recorded decision without sign-off; improvised deviation; schema, config or docs not reproducible from what ships; ownership or ordering breach; Mode S misclassified; N/A without basis | migrations missing ~60% of columns (LL-21); broken default dev config (LL-22) |
| Minor | Cosmetic, wording or layout with no wrong information | mixed number formats on one screen (LL-19) |

**XCA-8** — Let only the user accept a finding: the acceptance is recorded in `context.md` §13 with date, reason and
expiry (the next Mode X or R); a Critical needs the user's written risk acceptance there. At every Mode X and Mode R
re-raise each accepted finding as open until the user accepts it again; never carry it as "previously accepted, not
re-raised".
- *Why:* accepted findings that are never revisited become permanent, invisible debt.
- *Check:* every ACCEPTED row in `audit.md` matches a §13 row; Mode X and R audits list each one as re-raised.
- *Applies when:* every accepted finding.
- *Provenance:* industry baseline

**XCA-9** — Re-verify and re-audit every product change made after an audit — a fix pass, a "trivial" close-out edit,
a merge conflict resolution — before Gate 3: the Tester's Verify on the new product SHA, then a scoped re-audit that
also audits the fix diff for new defects. An in-cycle F-n or DQ-n is a finding of the cycle, never an escape: a
failing TC first (ESC-2). Append each re-audit to `audit.md` as "Iteration n" listing every earlier finding as
RESOLVED (evidence), ACCEPTED (by user, date), NEW or PRE-EXISTING; never overwrite an earlier iteration. A commit touching only `absd-project/`, or the Tester's Log commit (only Lesson
cells of `ESCAPED-DEFECTS.md`), needs no re-audit.
- *Why:* post-audit fixes were never re-audited, and fix passes introduced new defects three times (LL-46); a finding
  routed straight to a fix landed with no failing test (LL-55).
- *Check:* the last iteration's product SHA S is the one verified (`test_report.md`) and QA'd (`design_review.md`), and
  `git diff --quiet S HEAD -- . ':!absd-project'` holds at Gate 3; earlier iterations remain.
- *Applies when:* every iteration ≥ 2 and any post-audit product change.
- *Provenance:* LL-46 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

### Finding proof and scope drift

**XCA-14** — Raise a finding only with its proof: `file:line` (or artifact section), the trigger (input, state or
sequence), the bad outcome, and why the existing guards — types, validation, framework, caller — do not stop it; a
Critical or Major missing any of the four is demoted or dropped. Label each security finding with its reachability:
entry point → sink and the principal needed; a sink no shipped entry point reaches is Minor (hardening), a reachable
one is graded by XCA-7. A level with no finding reports PASS with its evidence; never pad a report.
- *Why:* speculative or manufactured findings spend fix rounds against the 3-iteration cap and bury the real ones.
- *Check:* at Gate 2R and Gate 3 the Manager returns any finding row whose Evidence cell lacks location, trigger,
  outcome or guard analysis (security: reachability) to the Auditor.
- *Applies when:* every finding (AR, TF, DQ, F).
- *Provenance:* LL-65 (ECC evaluation, 2026-11)

**XCA-15** — Reconcile every work package with its commit in every cycle: the files, public symbols, operations,
config keys, migrations and dependencies `architecture.md` lists for the WP against `git diff --stat` and the code of
that commit; each unplanned item is a Major finding (scope drift, XCA-6), each planned item missing is a Major L1
finding.
- *Why:* scope drift outside the blueprint evades the coverage-only Gate 2; Mode S compared the real diff, full cycles
  did not.
- *Check:* `audit.md` L1 holds a WP → planned vs actual table with the commit of each WP.
- *Applies when:* every audit with Builder commits (Mode S: XCA-11 as well).
- *Provenance:* LL-65 (ECC evaluation, 2026-11)
