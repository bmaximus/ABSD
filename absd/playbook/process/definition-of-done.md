# Definition of done — cycles, defects, foundation, release, upgrade, park

Code **DOD**. When each kind of work is finished, as tables the Manager ticks at the mode's close and the Auditor
verifies against evidence at the product SHA — the last commit that changes a path outside `absd-project/`
(`absd/RULES.md` §6; GATE-1, XCA-2). Routes and modes: `absd/RULES.md` §2; Builder and Tester steps: their manuals. A
row is done only with linked evidence; only the user waives one. A row conditioned by a profile or subject ("when …")
is N/A, without a waiver, where its condition does not hold, stated with the evidence (the Auditor verifies).

## Checklist

- [ ] Every row of the mode's table holds at the product SHA with linked evidence; waivers are user Decisions with a RISK (DOD-1)
- [ ] Feature cycle (F, S): gates, verified catalogue, green lanes, Design QA, audit, living docs, harvest, log, archive, merge (DOD-2)
- [ ] Each work package compiles with the test units of done WPs, fast suite green or TC-CONFLICT declared, committed (DOD-3)
- [ ] Defect (D): contained if live Critical; red first at the right level; why-missed fixed; sweep verified; logged; lesson closed (DOD-4)
- [ ] Foundation (B): kit installed by the user; frame, ADRs, QCs verified, every gate RED by a negative control then GREEN, skeleton shipped (DOD-5)
- [ ] Brownfield: ratchets seeded from measured values and only tightening; inventory over the whole product (DOD-6)
- [ ] Release readiness run at every trigger, not only before users get a build (DOD-7)
- [ ] Release checklist complete; any open row blocks the release (DOD-8)
- [ ] Upgrade (U): between cycles, CHANGELOG read, baseline against new rules, gaps as DEBT, version recorded (DOD-9)
- [ ] Park (P): archived `_abandoned` with `cycle.md` intact, nothing merged, risks and lessons recorded (DOD-10)

## Rules

**DOD-1** — Declare a cycle, defect or mode done only when every row of its table holds at one product SHA, each
linked from `cycle.md` to its evidence (command output or a CI run at that product SHA, artifact section, commit).
Evidence taken at product SHA S stays valid while `git diff --quiet S HEAD -- . ':!absd-project'` holds; pipeline
commits (artifacts, evidence, reports, archive) never invalidate it. A row that could not be checked is open. Only the
user waives a row: a brd Decision plus a RISK in `context.md`.
- *Why:* audits certified tests they never ran (LL-24); post-audit fixes were never re-audited, so "done" rested on the
  orchestrator's word (LL-46); "at the exact HEAD" could never hold, since every hand-off is a commit (LL-55).
- *Check:* the close section of `cycle.md` links every row; the Auditor re-runs what it cites (XCA-2).
- *Applies when:* always.
- *Provenance:* LL-24, LL-46 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

**DOD-2** — Close a feature cycle (Mode F, or Mode S on its delta route) only when every row holds.
- *Why:* every pre-v2 cycle closed with criteria nobody tested (LL-45) and fixes nobody re-audited (LL-46).
- *Check:* the Manager ticks rows 1–8 and 12 at Gate 3, rows 9–11 once Harvest has updated the living docs, the Risk
  register and `lessons.md`, row 14 after the Tester's Log, and records row 13 in `context.md` §15 after the merge;
  the Auditor verifies rows 2–7 and 12.
- *Applies when:* Modes F and S.
- *Provenance:* LL-45, LL-46 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

| # | Done when | Evidence |
|---|---|---|
| 1 | Every gate on the route passed for the current revision; no artifact changed after its gate without re-passing — appends to the plan's red-evidence index, amendments, Verify additions and iteration rows excepted, with `trace_check gate gateT` re-run after each | `cycle.md` gate ledger; trace_check per gate |
| 2 | The first T-SHA (Plan & Bind evidence commit) is an ancestor of every production change; each approved amendment or re-bind is in the T-SHA chain; no cross-owner commit | ownership_check `--t-sha` per chain entry |
| 3 | Every in-scope catalogue requirement verified at the Gate 3 product SHA: 0 failing, 0 untested, 0 unknown; plan conformance 0 missing (TRACE-12) | traceability_report |
| 4 | Every push-lane suite and gate green at that product SHA, all device and zone/locale projects included; 0 skipped; 0 pass-on-retry | `test_report.md`, CI at the product SHA |
| 5 | Coverage floor met and raised on headroom; 0 new untested units; mutation threshold met, 100% on money/time/access rules | coverage_gate, mutation report |
| 6 | Design QA PASS for every profile with a visual or human-facing output surface, at the same product SHA | `design_review.md` |
| 7 | Audit PASS (0 Critical, 0 Major open) at the same product SHA; every in-cycle F/DQ finding fixed through a failing TC, Builder Fix and Verify; every post-audit change re-verified and re-audited (XCA-9) | `audit.md` iterations |
| 8 | Agent exploratory pass on every device or runtime class wherever `TESTING.md` requires it; each finding routed, out-of-scope ones as DEF rows in `context.md` §16 (EXPL-6) | `EXPLORATORY.md` |
| 9 | Living docs current: catalogue, design system, `TESTING.md`, `EXTERNAL-FACTS.md`, `context.md` (current state only, §16 backlog included) | diffs |
| 10 | Risk register holds every unresolved assumption, open question, UNVERIFIED fact and environment limitation (ELIC-19) | `context.md` §11 |
| 11 | Harvest done: a `lessons.md` row per lesson (ENR-1) | `lessons.md` |
| 12 | Mode S: eligibility confirmed against the real diff (XCA-11) | `audit.md` L8 |
| 13 | Archived in one Manager commit (`git mv absd-project/working/*` → `absd-project/archive/NNN_…/`); merged per the merge policy when CI is green at the Gate 3 product SHA and every later commit changes only `absd-project/` | archive folder, merge commit, `context.md` §15 |
| 14 | When escaped defects were logged: Tester Log done, no `ESCAPED-DEFECTS.md` row of the cycle reads `pending H` (ESC-8) | the rows |

**DOD-3** — Finish a work package only when it compiles with every test unit whose work package is done (units keyed
to later work packages stay `pending WP-m`, test_plan §12) and nothing green at the work-package start turned red;
warnings-as-errors, lint, format and type checks are clean; the fast suite is green, or each remaining failure is
declared `TC-CONFLICT-n` (test, failing assertion, cited architecture or analysis section, why the code is right); no
suppression marker outside the `architecture.md` list; no deviation from the blueprint (one would have been a halt);
one commit with trailers.
- *Why:* interrupted builders left half-written code that others finished (LL-26); deviations were "resolved inline"
  instead of halting (LL-42); one new symbol failed a whole compiled test project, so "compiles with every test
  project" could not hold at WP-1 (LL-57).
- *Check:* `build_log.md` WP row links commit and command outputs; the Auditor greps for markers and deviation notes.
- *Applies when:* every Builder pass (Build and Fix).
- *Provenance:* LL-26, LL-42 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**DOD-4** — Close a defect (Mode D, one or a batch of DEF of one class) only when every row holds; the main rule is
ESC-1.
- *Why:* about a dozen fixes were made outside the pipeline with no regression test, sweep or log (LL-27); the sweep
  after one unread reader found six more untested units (LL-2).
- *Check:* the Auditor (defect scope) verifies rows 1–5; the Manager refuses archive without rows 7–8.
- *Applies when:* Mode D.
- *Provenance:* LL-2, LL-27 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

| # | Done when | Evidence |
|---|---|---|
| 1 | Regression test RED at the pre-fix commit for the stated reason, at the lowest level that should have caught it, plus a user-visible test if it reached a surface (ESC-3, E2E-17); an external-fact mechanism verified at Reproduce (EXT-4) | red evidence; test names carry DEF-n |
| 2 | Why-missed class named and that kind of test fixed, not only a case added (ESC-5); one root-cause class per DEF at Gate T | Reproduce section of `test_plan.md` |
| 3 | Same-weakness sweep recorded; every hit covered or a DEF row in the `context.md` §16 backlog; the Auditor reran it (ESC-7, XCA-5) | sweep table |
| 4 | Fixed in the earliest faulty artifact by its owner (root-cause class route); green at the Gate 3 product SHA as DOD-2 rows 4–5 | `cycle.md` route; CI at the product SHA |
| 5 | Audit (defect scope) PASS; Design QA PASS when the fix changes a visual or output surface, always for a UX gap | `audit.md`, `design_review.md` |
| 6 | A Critical on a live system: contained first by the user (shipped rollback or flag off), recorded as a D-n and a RISK; re-enabling is a Mode R trigger (DOD-7) | `defect.md`, `context.md` §11 |
| 7 | `ESCAPED-DEFECTS.md` row complete at Verify (Lesson `pending H`), incl. the ABSD gate or rule that should have caught it; Lesson filled by the Tester's Log step after Harvest (ESC-8) | the row |
| 8 | `lessons.md` row closes it: a proposed playbook change or "rule existed, not followed → enforcement change" (ESC-9) | `lessons.md` |

**DOD-5** — Close the Foundation cycle (Mode B; `absd/templates/project/foundation-brief.md`) only when every row holds.
- *Why:* a live check exited 0 without its credential (LL-25), a gate nobody has seen fail proves nothing; the shipped
  artifact had never booted on empty infrastructure (LL-14); kit, state and code locations were mixed (LL-28); the
  install commit failed its own ownership check and web-only rows bound libraries and CLIs (LL-55, LL-56); gate-type
  quality capabilities could never show as verified (LL-57).
- *Check:* `test_report.md` holds a negative-control table (gate → control → RED output → GREEN output).
- *Applies when:* Mode B (greenfield, adoption, v1 migration as Foundation-delta).
- *Provenance:* LL-14, LL-25, LL-28 (KatenatsioTipster, 2026-10); LL-55, LL-56, LL-57 (ABSD v2 kit review, 2026-10)

| # | Done when |
|---|---|
| 1 | `context.md` frame complete: profiles, audiences and devices, principals and entitlement states, external systems, deploy target, area codes (not reserved), Locale & Time Profile, Data Volume Profile, merge policy, Source Layout & Ownership, Execution Environment |
| 2 | ADR-001 stack, ADR-002 layout and ownership (test tooling in Tester-owned files; Builder and Tester CI workflows split), ADR-003 test stack passed Gate 2 and 2R; `design-system.md` exists per profile |
| 3 | `TESTING.md` applicability decided with no blank cell (STRAT-1); `EXTERNAL-FACTS.md` has a section per external system, deploy and CI platforms included (EXT-3) |
| 4 | Every selected `QC-n` is a catalogue entry verified by its tests; a gate or drill QC by a planted-failure fixture RED and a clean fixture GREEN, linked `[QC-n]` (TRACE-1) |
| 5 | Every gate shown RED once by a negative control, then GREEN: untested unit, unexpected error signal, unknown requirement id, missing planned TC, foreign-owner commit to a test path; when operations have principals: unruled operation; when an external system exists: missing live credential; when the product has secrets: secret canary in a log |
| 6 | Every suite has run locally or in CI at the product SHA; Execution Environment says where each runs |
| 7 | Walking skeleton: one trivial slice through every declared interface; deployables: deployed by the pipeline with version-aware health, smoke and a rehearsed rollback, booting on empty infrastructure; cli, library: built once, published and installed with install smoke and withdraw or yank (OPS-1, OPS-3); fresh clone → running from the docs (OPS-6) |
| 8 | Kit installed by the user on the default branch (`ABSD-Sync: install <version>` commit) and `absd_sync.py check` green; ownership hook installed; ownership_check and trace_check in CI; the settings allow list holds the `context.md` commands |

**DOD-6** — Adopt an existing codebase with ratchets that only tighten: seed the untested-unit allowlist with every
currently untested unit (reason "baseline pre-ABSD — DEBT-n"; entries only removed), start the coverage floor at the
measured value, give new operations access rules from day 1 and mark existing ones "unverified" until covered, map
every existing suite onto the matrix (STRAT-12), inventory inherited behaviour over the whole product (ELIC-5) and pin
relied-on behaviour with CHAR tests that are never specification until the user confirms (ORACLE-12). A v1 project:
the user runs `absd_sync.py migrate-v1`, then `install`; the project keeps its cycle numbers and runs a
Foundation-delta first, with the v1 steps of `absd/templates/project/foundation-brief.md` (in-flight work parked,
conflicting guidance moved or deleted, `context.md` restructured to ≤ 25 KB, inherited test docs converted).
- *Why:* switching every gate on at once over hundreds of untested units turns the build red on day one and invites
  disabling gates; prototype behaviour shipped unspecified (LL-6) and work moved outside the pipeline (LL-27); a
  migrated project met duplicate registries, a mixed CI file and v1 standing authorizations nobody had to clear (LL-56).
- *Check:* the allowlist only shrinks in history; the floor never decreases; every DEBT has a burn-down row.
- *Applies when:* Mode B on an existing codebase or a v1 ABSD project.
- *Provenance:* LL-6, LL-27 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**DOD-7** — Run release readiness (Mode R) before users get a build and at every trigger: first use of real credentials
for any external system; a flag turned on in a user-facing environment, or turned off for containment (Mode D); an
external system's version or contract change; an infrastructure change (host, platform, region, store major version,
deploy tooling). `cycle.md` records the trigger and the scope it puts under DOD-8.
- *Why:* the escapes clustered on the first day the real feed credential was used (LL-1, LL-3); a platform's change to
  asynchronous deploys broke redeploy and rollback (LL-7); a flag turned on at runtime did not rewire (LL-23); a live
  Critical had no containment step while the defect route ran (LL-56).
- *Check:* every flag change, credential change and infrastructure change in history has a Mode R record (a
  containment: right after it).
- *Applies when:* always.
- *Provenance:* LL-1, LL-3, LL-7, LL-23 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**DOD-8** — Release only when every row holds for the release candidate commit; an open row blocks the release.
- *Why:* the blocking zone and calendar facts and the phone defects were found by people on the live system (LL-1,
  LL-4); a version-blind health check passed a blank page (LL-32); a registry lost every image (LL-34).
- *Check:* the Mode R record in `cycle.md` links each row's evidence; the user's go is a recorded Decision; a
  conditioned row whose condition does not hold reads N/A with the evidence.
- *Applies when:* Mode R.
- *Provenance:* LL-1, LL-4, LL-32, LL-34 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

| # | Done when |
|---|---|
| 1 | Mode X PASS on the release candidate (no production change since it ran); every accepted finding re-raised and re-decided (XCA-8, XCA-12) |
| 2 | Last nightly and live contract runs green at the candidate; one that did not run is RED (GATE-1) |
| 3 | No enabled feature depends on an UNVERIFIED external fact (EXT-1, EXT-4) |
| 4 | Every in-scope requirement verified; open DEF and RISK items reviewed with the user; a Critical only with written risk acceptance |
| 5 | Human-facing profiles: human sessions per affected principal × device or runtime class (EXPL-4) and the manual acceptance checklist ticked (EXPL-8); web-ui, native-app: real-device checks (EXPL-9) |
| 6 | When the product owns persistent state (a cli's or library's local state and config included): migrations from empty and from the previous release with data; the previous release runs on the new schema |
| 7 | When the product owns persistent state: backup → restore drill current; a backup is taken right before the deploy (OPS-5) |
| 8 | Deployables: the tested digest (OPS-2), version-aware health, smoke, synthetic journey, error-rate watch, automatic rollback rehearsed (OPS-3), who watches and for how long; cli, library: the tested package published, install smoke, withdraw or yank rehearsed (OPS-3) |
| 9 | Production secrets only in the secret store; canary gate green; anything ever committed rotated |
| 10 | Every operability default within its OPS *Applies when* verified or waived by the user (ELIC-14) |
| 11 | Release notes generated from the catalogue report; the user's go recorded |

**DOD-9** — Finish a kit upgrade (Mode U) only when every row holds.
- *Why:* a project that adapts the kit in prose instead of upgrading it forks, and its lessons stop flowing back
  (LL-28).
- *Check:* `context.md` ABSD version equals `absd/VERSION`; `absd_sync.py check` is green; the gap list exists.
- *Applies when:* Mode U.
- *Provenance:* LL-28 (KatenatsioTipster, 2026-10)

| # | Done when |
|---|---|
| 1 | No active cycle; `absd_sync.py upgrade` ran clean and was committed on the default branch with its `ABSD-Sync: upgrade <version>` trailer, or local edits were recorded and each became a lesson (ENR-4) |
| 2 | The Manager read every CHANGELOG entry between the installed and new versions and updated `lessons.md` outcomes (ENR-16) |
| 3 | The Tester baselined the product against every new or changed rule → gap list; each gap is DEBT or a Foundation-delta cycle; `TESTING.md` re-decided where the matrix changed |
| 4 | MAJOR: every migration note applied (artifact structure, ids, gates, routes) |
| 5 | `context.md` ABSD version bumped; every suite and gate green at the product SHA with the new kit |

**DOD-10** — Park or abandon a cycle (Mode P) only when every row holds; nothing else of it reaches the default branch.
- *Why:* interrupted runs without saved state were finished by the wrong agent or lost (LL-26).
- *Check:* the archive folder name ends `_abandoned`; its `cycle.md` names the branch and resume point.
- *Applies when:* Mode P.
- *Provenance:* LL-26 (KatenatsioTipster, 2026-10)

| # | Done when |
|---|---|
| 1 | `cycle.md` records the user's decision and date, the last gate passed, the resume point and the branch, which is kept unmerged |
| 2 | Archived as `absd-project/archive/NNN_YYYY-MM-DD_slug_abandoned/` with every artifact and `cycle.md` intact |
| 3 | Only the archive folder and the Manager's living-doc updates reach the default branch; ids used stay consumed |
| 4 | Risk register and DEBT updated with unresolved questions, UNVERIFIED facts and partial work |
| 5 | Lessons harvested, including why the cycle stopped; `context.md` active cycle: none |
