# Changelog

Newest first. Every entry cites the ledger lessons (`LL-n`) and product proposals it answers. Versioning: MAJOR =
artifact structure, ids, gates or routes (with migration notes); MINOR = rules added or changed; PATCH = wording.

## 2.0.0 — 2026-10-14

The first version built from a real product's lessons (KatenatsioTipster, ABSD 1.x: four cycles, a cross-cycle audit,
and the escaped defects and test suite that followed). Ledger: LL-1 … LL-57.

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
