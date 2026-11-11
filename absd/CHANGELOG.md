# Changelog

Newest first. Every entry cites the ledger lessons (`LL-n`) and product proposals it answers. Versioning: MAJOR =
artifact structure, ids, gates or routes (with migration notes); MINOR = rules added or changed; PATCH = wording.

## 2.4.0 — 2026-11-11

The pipeline measured: model levels per role, per-cycle telemetry, and a scored benchmark of the agents (owner request,
proposal telemetry-benchmark-models-2026-11-11). Ledger: LL-67.

- **PIPE** (new code, `absd/playbook/process/pipeline-operations.md`):
  - **PIPE-1** model levels (`strongest`, `balanced`, `fast`) per role and step, with floors no product lowers
    (architecture, Gate 2R, Plan & Bind, every audit and security review, money/permission/security WPs) and a
    level → model map in `context.md` §14; a second audit (XCA-17) runs on the strongest model that did not build.
  - **PIPE-2** the Manager passes the model per invocation and names `<level> → <model>` in the brief (new `Model`
    field); frontmatter `model:` is only the fallback. RULES §8 "Model level" row replaces the Builder-only tier.
  - **PIPE-3** `absd-project/metrics/C###.json` per cycle, written only by `absd/tooling/metrics.py record`:
    invocations, gate rounds and verdicts with finding counts and cited rules, halts, rework, negative controls,
    escapes, resumes; tokens only when the platform reports them.
  - **PIPE-4** telemetry is local, never sent, numbers/enums/ids only (the tool refuses free text and unknown keys);
    `Telemetry: off` in §14 switches it off.
  - **PIPE-5** Mode H runs `metrics.py report`: cost per step, level and model; FAIL rounds per gate; rules that catch
    most and kit rules never cited; rework and halts by cause.
  - **PIPE-6** + **ENR-14** (amended): the acceptance run is the benchmark — `benchmark/` at the kit root (fixtures
    tally, shelf, ledger with three seeded traps each; `score.py score | combine | compare`); a release must not catch
    fewer traps, halt more on kit gaps, fail a criterion or lose more than 10 points of first-pass gates; cost growth
    above 25 % is a warning here. Model-map experiments use the same comparison.
- **Tooling:** `metrics.py` (record, validate, report) with tests; `benchmark/score.py` with tests, run by CI.
- **Benchmark findings** (LL-68, proposal benchmark-2-4-0-2026-11-11):
  - **TRACE-9 / DOD-8:** a planned TC no host or CI of the pipeline can run is passed as `--deferred TC-nnnn=D-n`
    (a user Decision plus RISK, never a deleted AC): it may be missing, still fails if it fails, an unplanned one is
    `unknown`, and it must pass in the release lane before Mode R. `traceability_report.py --deferred`, with tests.
  - **ARCH-8:** each WP's lint, type and format commands name only paths that exist once it is done, and dictated code
    passes the project's own static rules (both benchmark Builder halts).
  - **Tester Verify:** the exploratory pass runs before the gate run, so its log joins commit (a).
  - **PIPE-3:** gate events take `repass` (a re-run after a decision or CLR, not a review round); invocation result
    `blocked`. `metrics.py` and `score.py` skip re-passes when counting rounds.
  - RULES §7: `D-n` is a product-scope id. `cycle.md`: Mode S eligibility is "N/A" outside Modes F and S.
  - **EXT-1:** an input the product reads and validates needs no flag when it fails closed (non-conforming input
    rejected with an alerting exit); its facts keep a RISK row and a real sample is due before Mode R.
  - **Limits:** reaching a limit (the 3rd pass, FAIL round or halt) escalates before the next one starts.
  - **Gate 1:** the ledger records `G1 approved` before catalogue apply, then PASS after `gate1` (no circular wait).
  - **trace_check gateT:** in a TC table with a Requirement column only the Requirement and Source cells count as
    coverage (an id in Inputs is not); with tests.
  - **TRACE-7:** one assertion per AC clause; a TC needing an environment feature asserts it is present (fails,
    never skips). **ELIC-10:** file inputs list encoding, byte-order mark, line ends, empty and header-only files.
    **GATE-2:** the untested-unit control plants a unit of at least `--min-lines`. Foundation brief: QC-1 only with
    principals, QC-14 only with secrets (as DOD-5). **ARCH-8:** no two WPs produce the same path.
  - **Shelf run:** GATE-13 — artifacts, reports and evidence cite a secret-shaped match by file and line, never
    quote it; stored control output is redacted. GATE-5 — a mutant's id is position range + mutator + replacement; a
    row is stale only for a unit the run mutated; child-process code gets the mutant selector, browser code
    applied-copy mutants. `absd_sync.py` install and upgrade add `absd/**/__pycache__/` to the product's `.gitignore`
    (the push lane's kit tests left the tree dirty), with tests. Architecture template §9: configuration files a WP
    creates are given in full. `metrics.py`: steps `design-system`, `catalogue-apply`, `fix`; rework causes
    `minor-routed`, `user-answer`; `resume` defined (PIPE-3). Tester: a new screen's first visual baseline is
    `pending first baseline`, not a TC-CONFLICT. Auditor re-audit cites the last clean mutation run when production
    code, mutation configuration and equivalents are unchanged. XCA-17 / PIPE-1: with one strongest model, the second
    audit is a fresh invocation of it. Manager Gate 1: an answered blocking OQ gets an Analyst delta before catalogue
    apply.
- Kit acceptance run (ENR-14 / PIPE-6), 2026-11-11, one agent playing every role, Bootstrap + one feature cycle per
  fixture, telemetry on: **9/9 seeded traps caught**, criteria c1–c3 pass on all three fixtures, kit-gap halts 0,
  negative controls 51/51 red then green, first-pass gate rate 86.1% (tally 12/12, ledger 10/12, shelf 9/12 — Gate 3
  failed rounds on mutation identity and secret citation, fixed above). First scored baseline:
  `benchmark/results/2.4.0.json`; later MINOR and MAJOR versions compare against it (PIPE-6). Findings: proposal
  `benchmark-2-4-0-2026-11-11`, LL-68.

## 2.3.0 — 2026-11-10

Fixes from the kit acceptance run (ENR-14) of 2.2.0 on three fixture products — tally (cli + library), shelf (web-ui +
http-api), ledger (data pipeline), each a Foundation plus one or two feature or defect cycles; proposal
acceptance-2-2-0-2026-11-10 (reports verbatim). Ledger: LL-66.

- **GATE-18** (new, blocker in tally, major in shelf): every agent stages only its own paths (never the whole tree) and
  runs `ownership_check --range HEAD~1..HEAD` on each new commit; a committed foreign-path change is repaired, never
  rewritten — a Manager commit restores the foreign files with `ABSD-Repair: <sha> D-<n>` after the user's decision
  (`procedures/ownership-repair.md`); all seven manuals' commit steps cite it; the settings template denies
  `git add -A/--all/-u` and `git commit -a`. RULES §5 notes that the write-time hook does not see staging.
- **ownership_check**: an empty range passes with a notice (the default branch was red after every merge); the
  `ABSD-Repair` trailer turns the repaired commit's errors into notices when the repair touches exactly its foreign
  files. **GATE-14** and the TESTING template follow.
- **traceability_report `--inherited-plan`** + **TRACE-9** (all three runs): archived plans make earlier cycles' TCs
  inherited — never unplanned or missing, still failing if they fail; the red run stays `--fail-on unknown,unplanned`.
- **trace_check**: gateT resolves earlier cycles' `SPEC:` ids through the catalogue; `open_findings` reads a `Result`
  column; the audit template's Status cell starts with its state word; push-lane gate checks run only for gates whose
  latest ledger row is PASS.
- **GATE-5 / ORACLE-14**: equivalent mutants are recorded (id, location, reason, reviewer) and the gate asserts on the
  survivor list — never on a mutation tool's exit status alone (one such gate could never fail).
- **Rounds** (RULES §2, Manager 4.13, `cycle.md` counters): a round is a review with a FAIL verdict; re-passes from
  upstream gaps, spec defects, halts or CLRs are logged, not counted; a resumed halted Build is the same pass.
- **DOD-3**, Builder, Architect: a lint/type/format finding on code the blueprint dictates may be a TC-CONFLICT; the
  Architect lists lint scopes for entry-point scripts. Test-tool versions live only in the Tester's files, so a
  security bump is a Tester change, not a Gate 2 round. **GATE-3 / DOD-2**: living docs are committed before the
  evidence run; a coverage-floor raise is recorded at Verify and applied at the next Plan & Bind.
- **Foundation and park**: the brd skeleton allows `Mode: B`, the Manager proposes the QC set and the user signs it
  off as a D-n; a parked Foundation keeps its brief's QC and ADR ids (**DOD-10**); `procedures/park.md` with a
  clean-tree check; a shared root ignore file where each agent adds its own lines; the merge commit is recorded in
  the next cycle's start commit.
- **DOD-5**: a product without a CI service runs a local gate script at each hand-off (ADR + RISK); `context.md` gains
  Deploy target and CI service rows. TESTING template: the fast suite must not abort on a later WP's collection or
  compile failure. Designer: a data pipeline's trigger surface is named in design §17.
- **SEC-8** (amended): synthetic test secrets use marked constants; evidence redacts scanner matches. Architecture
  template §12 pre-fills the secret, static, dependency and agent-configuration scan rows.
- Kit acceptance run (ENR-14), 2026-11-10, one agent playing every role (independence not exercised):

  | Fixture | Profiles | 2.2.0 run (full: Foundation + cycles) | 2.3.0 re-run (upgrade + replay of every failure) |
  |---|---|---|---|
  | tally | cli, library | FAIL: criteria 2, 3 (blocker K1, K2) | PASS: upgrade + sync check; empty-range check on the default branch passes; whole history passes; K1 replayed — the GATE-18 self-check flags the foreign file, the repair commit turns it into a notice and keeps the Manager's own file |
  | shelf | web-ui, http-api | FAIL: criterion 3 (rounds) | PASS: upgrade + sync check; empty range and whole history pass; round counting now stated |
  | ledger | data-pipeline | PASS with caveats (red run, rounds) | PASS: the C002 red run replayed on its own evidence — 2.2.0 command fails on 59 inherited TCs, the 2.3.0 command passes (59 inherited, 0 unplanned) |
  | — | native-app | not run (no emulator in the run environment) | not run |

  Criterion 1 (negative controls) passed in all three 2.2.0 runs and no gate tool's red behaviour changed. The
  2.3.0 re-run replays the failures on the fixtures' real histories; it is not a new full cycle per profile.

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
- Kit acceptance run (ENR-14): run 2026-11-10 on three fixtures; it **failed** (one blocker, majors in every run), so
  2.2.0 was never tagged. Its fixes are 2.3.0.
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
