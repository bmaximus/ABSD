# Foundation cycle brief (Mode B)

The first cycle of every product — and the first v2 cycle of a brownfield or v1 project — builds the frame, the walking
skeleton and the quality harness before any feature. It is traced like a feature cycle: its requirements are the
quality capabilities `QC-n` below, so every gate has something to check. Definition of done:
`absd/playbook/process/definition-of-done.md` (Foundation). The Manager enters it while `context.md` §1 still holds a
`<…>` placeholder or §15 has no Foundation row: greenfield or brownfield by the code; a "v1 Foundation-delta" (missing
steps only, each gated) when `absd-project/archive/` holds pre-v2 cycle folders.

## Steps

| # | Owner | Produces | Gate |
|---|---|---|---|
| 0 | User | Before the Manager exists: from a kit checkout runs `python3 <kit>/absd/tooling/absd_sync.py install` (a v1 project: `migrate-v1` first), commits the result on the default branch with the trailer the tool prints (`ABSD-Sync: install <version>`; a fresh repository gets it as its first commit), then starts the Manager | — |
| 1 | Manager | Verifies the install with `absd_sync.py check` (never runs install), writes the `context.md` frame with the user: profiles, audiences and devices (phone tests for web-ui and native-app on unless waived), principals and entitlement states, external systems, deploy target, area codes (not reserved), Locale & Time Profile, Data Volume Profile, merge policy. Opens `cycle.md` and the branch. After Gate 2R copies ADR-001/002/003 into `context.md` §2–§4 and the build and test commands into the allow list in `.claude/settings.json` (the ownership hook stays installed); after Gate T adds the `TESTING.md` commands to §4 and the allow list. | — |
| 2 | Analyst | `analysis.md` for the selected `QC-n` (+ any walking-skeleton requirement), actor × capability matrix for the whole product as known today, inherited behaviour inventory (brownfield: the WHOLE product), first `catalogue.md` | Gate 1 |
| 2a | Tester | Facts, when the skeleton or a selected `QC-n` touches an external system: recordings, independent sources, `EXTERNAL-FACTS.md` rows (`ABSD:EXT-4`); no production code | — |
| 3 | Designer | `design-system.md` per profile (web/native: tokens, type scale, colour roles with contrast, spacing, motion, components, states; cli: output style guide; library: API naming guide; data: contract style) + `design.md` for the skeleton's surface | Gate UX |
| 4 | Architect | ADR-001 stack · ADR-002 source layout and path ownership (the "Source Layout & Ownership" table; test dependencies, runner, coverage, mutation and test-lint settings in standalone Tester-owned files, else listed shared sections; grants as code to the builder; built-in paths never listed) · ADR-003 test stack per profile (runners, coverage format Cobertura/LCOV, JUnit XML reports, mutation tool, e2e driver, fakes) · walking skeleton blueprint · quality gates & CI, split into Builder and Tester workflow files · WP list | Gate 2 → 2R |
| 5 | Tester | Baseline, then Plan & Bind: fills the seeded `TESTING.md` (applicability decided once), `EXTERNAL-FACTS.md` sections for every external system, the harness, the gates and the Tester's workflow file, `test_plan.md` with RED tests for every QC and every skeleton requirement | Gate T |
| 6 | Builder | Walking skeleton: one trivial vertical slice through every declared interface, deployable (cli, library: publishable and installable), with the Builder's build/deploy workflow; brownfield: a WP moves the test and gate jobs out of a mixed workflow file once the Tester's workflow runs them | — |
| 7 | Tester | Verify: every gate shown RED once by a negative control, then GREEN (evidence in `test_report.md`); a QC that is a gate or drill is proven by an acceptance test that runs it on a planted-failure fixture (RED) and on a clean fixture (GREEN), linked `[QC-n]`, a drill through a scripted job that emits JUnit XML (`ABSD:TRACE-1`); every suite smoke-run locally or in CI at the product SHA | — |
| 8 | Designer ∥ Auditor | Design QA of the skeleton · audit incl. L7 operability and L8 process, both at one product SHA | Gate 3 |
| 9 | Manager | Harvest · archive · merge; the Foundation row in `context.md` §15 ends Bootstrap | — |

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
- Tester *Baseline* (step 5): inventory existing tests against `TESTING.md`'s matrix → gap list (DEBT items);
  characterization tests for behaviour users rely on, labelled `CHAR` — never specification until the user confirms it.
- Untested-unit allowlist seeded with every currently untested unit, reason "baseline pre-ABSD — DEBT-n"; burn it down.
- Coverage floor starts at the measured value and only rises.
- New operations need access rules from day 1; existing ones are marked "unverified" in the matrix until covered.
- Seeds go where `context.md` §3 says: the Tester moves a seeded file to the real test root (e.g. the allowlist next
  to an existing one) and merges duplicates.
- Inherited test docs (testing guide, escaped-defects log, exploratory notes, external facts) are converted to the
  template headers; old escape rows get a DEF id, a why-missed class and the gate that should have caught them.
- A duplicate requirement registry (e.g. a requirements file the tests link to): after Catalogue apply the Analyst
  maps its ids to catalogue ids and the Tester relinks the tests through the linking helper, then retires it.
- Tests without `TC-nnnn` ids get them, or a dated brownfield exemption in `TESTING.md` §4 with a burn-down.

## v1 projects (Foundation-delta)
- The user runs `migrate-v1`, then `install` (step 0); `context.md` and the archive move into `absd-project/`.
- In-flight v1 work is parked (Mode P) and its intake redone as the first cycle after the delta; numbering continues
  after the highest v1 cycle, the parked one included.
- `CLAUDE.md` or other guidance that conflicts with `absd/RULES.md` (merge, branch or direct-fix authorizations) moves
  into the `context.md` §1 merge policy, or is deleted.
- Lasting v1 gate decisions become catalogue business rules through the Analyst; their history stays in the archive;
  `context.md` is restructured to the template sections and trimmed to ≤ 25 KB.
- Mode X waits until the Foundation-delta has closed.
