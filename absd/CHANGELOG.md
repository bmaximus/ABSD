# Changelog

Newest first. Every entry cites the ledger lessons (`LL-n`) and product proposals it answers. Versioning: MAJOR =
artifact structure, ids, gates or routes (with migration notes); MINOR = rules added or changed; PATCH = wording.

## 2.0.0 — 2026-10-14

The first version built from a real product's lessons (KatenatsioTipster, ABSD 1.x: four cycles, a cross-cycle audit,
and the escaped defects and test suite that followed). Ledger: LL-1 … LL-54.

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

**Migration from 1.x:** `absd_sync.py migrate-v1` moves `context.md` and the archive into `absd-project/`; then
`absd_sync.py install`; the Manager restructures `context.md` to the v2 sections and runs a Foundation-delta cycle.
