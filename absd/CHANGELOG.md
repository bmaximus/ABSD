# Changelog

Newest first. Every entry cites the ledger lessons (`LL-n`) and product proposals it answers. Versioning: MAJOR =
artifact structure, ids, gates or routes (with migration notes); MINOR = rules added or changed; PATCH = wording.

## 2.2.0 — 2026-11-10

Harvest from a read-only evaluation of an external agent-pipeline kit (proposal ecc-evaluation-2026-11-10, accepted:
the shortlist and the structural ideas). Ledger: LL-65.

- **Deduped first.** Already covered, no change: per-WP checkpoint for resume (WP rows, Progress line, Resume steps
  of the Builder, ARCH-24 check); `model:` already set in every manual's frontmatter (now documented, below);
  `git commit --no-verify` / `-n` already denied in the settings template, so no kit tool was added (a hook would mix
  a command check into the file-ownership hook). Gaps confirmed: RULES §6 had no proof standard for findings;
  plan-versus-diff ran only in Mode S (XCA-11); nothing on piped exit status.
- **XCA-14** (new): a finding names location, trigger, outcome and why guards miss it; security findings carry
  reachability (unreachable sink → Minor, a condition on **XCA-7**, amended); zero findings is valid, never padded.
  RULES §6 states the Evidence content.
- **XCA-15** (new): every cycle reconciles each WP's planned files, symbols, keys and dependencies with its commit.
- **XCA-16** (new): the security review procedure (`absd/playbook/procedures/security-review.md`): part A at Gate 2R
  (threat coverage, walk list incl. race, fetch, paths, model input; matrix and deny by default; sinks and secrets;
  declared CI scanners; WP security sections), part B at L5 (scanner results, threat and abuse-case TCs, parallel
  duplicate-request TCs, access completeness, reachability-graded manual pass, canaries).
- **XCA-17** (new): optional second independent audit on money or permission paths, on the user's choice.
- **SEC-7** (amended): server-side fetch and file-path rules with hostile-input sets. **SEC-14** (amended): walk list
  adds concurrent duplicate request, fetch, path and model input; a parallel-request TC per money, entitlement or
  permission change asserts one effect. **SEC-15** (new): products calling a model. **SEC-16** (new): agent
  configuration as supply chain, kit and products.
- **ELIC-23** (new): abuse cases for features touching sign-in, money, personal data, uploads, model calls or external
  input. **ARCH-24** (amended): each WP carries a security section. **CODE-15** (new): one state per lifecycle,
  invalid combinations unconstructible (Architect, 2R, L4). **CODE-16** (new): callers and data shapes found by search
  before editing an existing file. **GATE-17** (new): piped gate and test commands keep their exit status.
- **ENR-17** (new) and README "Procedures": on-demand procedure files in `absd/playbook/procedures/`, cited by their
  triggering rule at the step that needs them; RULES §9 points to them.
- RULES §8: a worker's final reply is the deliverable (nothing left pending in background work); model tier per role —
  strongest tier for judgement roles and every security review, the Builder optionally on a faster tier for mechanical
  WPs when the user records it (never money, permission or security WPs); kit default unchanged (strongest everywhere).
- Splits (ids unchanged): PRIV-1 … PRIV-8 moved to `absd/playbook/security/privacy.md`; XCA-10 … XCA-13 moved to
  `absd/playbook/process/audit-modes.md` with XCA-16 and XCA-17.
- Settings template: deny reads of secret paths (SSH, cloud and cluster credentials, `.env`, keys), pipe-to-shell and
  remote copy.
- `kit_lint`: check 10 refuses invisible and bidirectional control characters in kit Markdown and the project seeds
  (SEC-16 on the kit itself); check 1 refuses a rule defined in a procedure file (ENR-17); tests added.
- Manuals: Auditor (procedure parts A/B, XCA-14, XCA-15, XCA-17, reads `audit-modes.md`), Manager (Gate 3 finding
  proof, second audit), Architect (CODE-15, SEC-7/14/15, WP security section), Analyst (ELIC-23), Builder (CODE-16).
- Review follow-up (same version; additions these rules already required): templates — `audit.md` L1 planned-vs-actual
  table (XCA-15), L5 part B rows (XCA-16), Second audit section (XCA-17); `analysis.md` abuse-case table (ELIC-23);
  `architecture.md` §8.7 model calls (SEC-15), §8.4 SEC-15/16, §20 WP security column (ARCH-24); `arch_review.md`
  part A rows (XCA-16); `build_log.md` §1 caller table (CODE-16); `context.md` §14 Builder model tier and second-audit
  choice. Manuals cite GATE-17 and SEC-16; Auditor L4/L5 ranges reach CODE-16 and SEC-16; Tester row 21 adds ELIC-23
  and SEC-15; Manager offers XCA-17, passes the Builder tier per invocation (RULES §8 Model tier row joined to its
  table). Procedure inputs and playbook routing rows completed; README corrections.
  Copilot mirrors unchanged (they point to the manuals).
- Kit acceptance run (ENR-14): not yet run for this version — required before tagging 2.2.0.
- **Next (planned, not in this release):** move other long situation-triggered sequences out of the manuals into
  procedures, one per release, each cited by a rule: brownfield adoption and v1 migration (Manager, Tester Baseline),
  Mode X lenses (Auditor 4.5), Gate 2R probes (Auditor 4.1 step 3), flake triage (Tester), kit upgrade (Manager Mode
  U). Target: every manual below 30 000 characters, budgets unchanged.

## 2.1.0 — 2026-11-07

Payments reported "implemented" while members could not pay (KatenatsioTipster, proposal
katenatsiotipster-2026-11-07, accepted). Ledger: LL-59 … LL-64.

- **DOD-11** (new, LL-59): a status answer names the level a capability reached — specified, built, reachable,
  verified, live — with evidence and known gaps; never a bare yes.
- **E2E-18** (new, LL-60): every user-facing capability has a journey from the role's real navigation; a capability
  only a test can open is not built.
- **EXT-6** (new, LL-61, LL-62): providers that move money, identity or messages get their whole event lifecycle
  mapped to requirements and tests, and their provider-side configuration verified read-only before release readiness.
- **GATE-16** (new, LL-63, LL-64): with several writers to the default branch, diff the tip against the release tree
  before pushing and rebuild on a moved tip; full suites after every merge or conflict resolution.
- Manuals: Analyst cites EXT-6; Manager cites GATE-16 and DOD-11 (Mode R and status answers); Auditor's Mode R rows
  add EXT-6 and E2E-18.
- Scoreboard: KatenatsioTipster 31 → 37.

## 2.0.0 — 2026-10-14

The first version built from a real product's lessons (KatenatsioTipster, ABSD 1.x: four cycles, a cross-cycle audit,
and the escaped defects and test suite that followed). Ledger: LL-1 … LL-58.

**Acceptance review fixes (LL-58, proposal acceptance-review-2026-10-25)**
- `trace_check.py gateT` passes a Mode D plan whose every DEF binds at re-bind (no TC yet) and fails a TC id defined
  twice; `traceability_report.py --plan` accepts the same re-bind-only plan and refuses duplicate TC ids.
- `coverage_gate.py` keys an unqualified class name (Go's `-` and receiver types, grcov's file stems) by its file and
  resolves Cobertura file names against the report's `<source>` roots, so per-package monorepo reports stay distinct
  (GATE-2).
- The tools never write `__pycache__` into the kit and never load bytecode the manifest does not cover; manifest
  hashes read CRLF as LF (Git for Windows' `core.autocrlf`).
- `ownership_check.py` checks a merge that carries changes of its own (conflict resolution, evil merge) and rejects a
  kit-sync commit inside a cycle; a kit sync may complete `.claude/settings.json` and `CLAUDE.md` and write the
  upgrade's local-edits record.
- `absd_sync.py install` completes an existing `.claude/settings.json` (agent, permission rules, ownership hook) and
  `CLAUDE.md` (imports) instead of silently keeping them; `upgrade` refuses while any `absd/C###-*` branch holds an
  IN-PROGRESS cycle, names seeds whose template changed, and orders its steps so the kit-sync commit comes first.
- The settings template denies force-push and amend variants (`git push * --force*`, `+refspec`, `--amend`, rebase).
- The Manager's session start finds an in-progress cycle on its branch from the default branch.

**Structure (MAJOR)**
- The kit moves into `absd/` (vendored, read-only in products, replaced on upgrade, hash-listed in `absd/MANIFEST`);
  product state moves into `absd-project/` (living `context.md`, `catalogue.md`, `design-system.md`, `lessons.md`,
  plus `working/` and `archive/`). Source code lives where `context.md` says, never in the kit (LL-28).
- `absd/RULES.md` is the canonical rule set; product `CLAUDE.md` imports it. This repository's `CLAUDE.md` becomes a
  maintainer guide.
- Requirement ids are permanent product ids (`AREA-n`, `AREA-NF-n`, `AREA-BR-n`, criteria `AREA-n.ACn`) kept in a
  living catalogue; test case ids are flat `TC-nnnn` with level and purpose as attributes.

**New agent: Tester** — owns every test and test asset; derives expected values from the specification and commits
executable tests that fail *before* the Builder starts (Plan & Bind); verifies after the build with coverage,
traceability, mutation, flake, accessibility and contract gates, a screenshot gallery and an exploratory pass
(LL-27, LL-29, LL-45).

**New gates and routes**
- Gate 2R: independent architecture review by the Auditor before any code (LL-42, LL-44).
- Gate T: test-plan coverage, red evidence and T-SHA before any code (LL-29, LL-45).
- Design QA: the Designer reviews the rendered product (LL-19, LL-52).
- Modes S (small change), D (defect, batchable), C (change request), X (cross-cycle audit), R (release readiness),
  H (harvest), U (upgrade), P (park) next to F (feature) and B (bootstrap/adopt incl. v1 migration) (LL-21, LL-27).
- Git protocol: a branch per cycle, a commit per hand-off with `ABSD-Agent`/`ABSD-Cycle` trailers, work packages,
  resume briefs; the Manager never writes another agent's artifact or code (LL-26, LL-46).

**New rules (playbook, all with provenance):** testing (STRAT, VAR, ORACLE, ACCESS, INTEG, FAKE, EXT, E2E, TRACE,
GATE, ESC, EXPL, A11Y, PERF, RESIL, VIS, OPS, TCQ), design (DSN, LOC), engineering (ARCH, CODE), security (SEC,
PRIV), process (ELIC, DOD, XCA, ENR). Twelve quality laws Q1–Q12 in RULES.md.

**New tooling (stdlib only, each with tests and mutation-probed):** `coverage_gate.py`, `traceability_report.py`,
`trace_check.py`, `ownership_check.py`, `ownership_hook.py`, `absd_sync.py`, `kit_lint.py`.

**Hardened by three adversarial reviews before release (LL-55 dry run, LL-56 profiles/defect route/v1 migration,
LL-57 testing):**
- Evidence is valid for a *product SHA* (the last commit outside `absd-project/`), so pipeline commits never invalidate
  it; merge needs CI green at the Gate 3 product SHA; plan gates apply only while a cycle is active (archive no longer
  deadlocks CI).
- Plan & Bind commits tests, runs them, then commits the red evidence — that commit is T-SHA; amendments and re-binds
  extend a T-SHA chain (`ownership_check.py --t-sha` repeats). Red tests are isolated per work package, so compiled
  stacks keep building.
- New Tester modes: *Facts* (verify a new external system after Gate 1, before design) and *Log* (fill the
  escaped-defects Lesson cells after Harvest). Mode D: containment first for a live Critical, an external-fact root
  cause class, a classification Gate T, Design QA when a visual surface changes, a defect backlog in `context.md`.
- The user installs and commits the kit (`ABSD-Sync` trailer); the Manager detects Bootstrap from the unfilled frame;
  `migrate-v1` parks an in-flight v1 cycle; kit-sync commits and the agent configuration (`.claude/`, `CLAUDE.md`,
  Copilot instructions) are protected by the ownership tools.
- Gates read what they claim: gateT counts ids only in TC rows, resolves every oracle source, fails on open blocking
  spec defects and reads `brd.md`/`defect.md` scopes; gate3 needs each report's verdict line; every missing coverage or
  JUnit report is RED; per-layer coverage floors; stale allowlist entries can fail; only compiler-generated types fold.
- Profiles: operability defaults scoped by *Applies when*, a design rubric per profile, the Designer names the public
  surface of cli/http-api/library, golden datasets come from the Analyst's example tables.
- New rules: STRAT-13 component tests; VAR-21..25 (caches, ranges, update semantics, overrides vs recomputation,
  source and channel parity); PERF-4 load and soak; COMPAT-1..3 interface compatibility (new code `COMPAT`); FAKE-13
  model-backed features; RESIL-4 owned-dependency failures; ELIC-22 money movements.
- Artifact skeletons move from the manuals to `absd/templates/artifacts/`; the playbook splits into
  `variation-catalogue.md`, `load-and-compatibility.md`, `external-facts.md`, `end-to-end-profiles.md`,
  `ci-and-release-gates.md`, `design/rubric-and-qa.md` and `engineering/architecture-review.md` (ids unchanged).

**Migration from 1.x:** `absd_sync.py migrate-v1` moves `context.md` and the archive into `absd-project/`; then
`absd_sync.py install`; the Manager restructures `context.md` to the v2 sections and runs a Foundation-delta cycle.
