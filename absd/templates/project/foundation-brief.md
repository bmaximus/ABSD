# Foundation cycle brief (Mode B)

The first cycle of every product — and the first v2 cycle of a brownfield or v1 project — builds the frame, the walking
skeleton and the quality harness before any feature. It is traced like a feature cycle: its requirements are the
quality capabilities `QC-n` below, so every gate has something to check. Definition of done:
`absd/playbook/process/definition-of-done.md` (Foundation).

## Steps

| # | Owner | Produces | Gate |
|---|---|---|---|
| 1 | Manager | Seeds product-owned files (`absd/tooling/absd_sync.py install`), writes the `context.md` frame with the user: profiles, audiences and devices (phone tests on unless waived), principals and entitlement states, external systems, deploy target, area codes (not reserved), Locale & Time Profile, Data Volume Profile, merge policy. Opens `cycle.md` and the branch. After ADR-001/003, adds the build and test commands of `context.md` §4 to the allow list in `.claude/settings.json` (the ownership hook stays installed). | — |
| 2 | Analyst | `analysis.md` for the selected `QC-n` (+ any walking-skeleton requirement), actor × capability matrix for the whole product as known today, inherited behaviour inventory (brownfield: the WHOLE product), first `catalogue.md` | Gate 1 |
| 3 | Designer | `design-system.md` per profile (web/native: tokens, type scale, colour roles with contrast, spacing, motion, components, states; cli: output style guide; library: API naming guide; data: contract style) + `design.md` for the skeleton's surface | Gate UX |
| 4 | Architect | ADR-001 stack · ADR-002 source layout and path ownership (the "Source Layout & Ownership" table) · ADR-003 test stack per profile (runners, coverage format Cobertura/LCOV, JUnit XML reports, mutation tool, e2e driver, fakes) · walking skeleton blueprint · quality gates & CI · WP list | Gate 2 → 2R |
| 5 | Tester | `TESTING.md` (applicability decided once), `EXTERNAL-FACTS.md` sections for every external system, the harness, the gates, `test_plan.md` with RED tests for every QC and every skeleton requirement | Gate T |
| 6 | Builder | Walking skeleton: one trivial vertical slice through every declared interface, deployable, with build/deploy pipelines | — |
| 7 | Tester | Verify: every gate shown RED once by a negative control, then GREEN (evidence in `test_report.md`); every suite smoke-run locally or in CI at HEAD | — |
| 8 | Designer ∥ Auditor | Design QA of the skeleton · audit incl. L7 operability and L8 process | Gate 3 |

## Quality capabilities (select per profile; each becomes a catalogue entry `QC-n` and gets tests)

| QC | Capability | Profiles |
|---|---|---|
| QC-1 | CI fails when an operation has no access-and-visibility rule (completeness test) | web-ui, native-app, http-api, data-pipeline, cli (if credentials) |
| QC-2 | End-to-end tests fail on any unexpected error signal | all |
| QC-3 | The acceptance report lists every catalogue requirement as verified / failing / untested; unknown ids fail | all |
| QC-4 | Test-plan conformance: every planned TC exists and passes | all |
| QC-5 | Coverage floor (ratchet) and no unit no test runs, with a reasoned allowlist | all |
| QC-6 | Test databases are built only by the shipped migrations; migrate-from-empty and drift checks in CI | products with persistent state |
| QC-7 | The shipped artifact boots on empty infrastructure with production configuration | all deployable |
| QC-8 | Deploy with version-aware health, post-deploy smoke and automatic rollback (incl. while the platform is busy) | all deployable; library/cli: publish + install smoke + withdraw/yank |
| QC-9 | Configuration agreement across code defaults, config files, deployment manifests and env examples | all |
| QC-10 | Recorded contract tests per external fact; live checks nightly; a missing credential is RED | products with external systems |
| QC-11 | Phone (and every declared device/runtime class) projects; one foreign time zone/locale project | web-ui, native-app; runtime matrix for cli/library |
| QC-12 | Accessibility scan of every screen state (0 serious/critical) | web-ui, native-app |
| QC-13 | Ownership and ordering checks (`absd/tooling/ownership_check.py`) and gate traces (`absd/tooling/trace_check.py`) in CI | all |
| QC-14 | Secret canaries: no configured secret value appears in any log, artifact or diff | all |
| QC-15 | Backup → restore drill | products with persistent state |
| QC-16 | Fresh clone → running from the docs | all |

## Brownfield ratchet (existing codebases and v1 ABSD projects)
- Tester *Baseline*: inventory existing tests against `TESTING.md`'s matrix → gap list (DEBT items); characterization
  tests for behaviour users rely on, labelled `CHAR` — never specification until the user confirms it.
- Untested-unit allowlist seeded with every currently untested unit, reason "baseline pre-ABSD — DEBT-n"; burn it down.
- Coverage floor starts at the measured value and only rises.
- New operations need access rules from day 1; existing ones are marked "unverified" in the matrix until covered.
- v1 projects: `absd_sync.py migrate-v1` moves `context.md` and the archive into `absd-project/`; the Manager
  restructures `context.md` to the v2 sections and continues cycle numbering.
