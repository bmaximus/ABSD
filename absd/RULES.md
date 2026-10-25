# ABSD Rules — Artifact-Based Software Development

The canonical rules for every ABSD agent, on every platform. Agent manuals (`.claude/agents/*.md`) implement them; the
playbook (`absd/playbook/`) explains them; nothing overrides them except the user, through the Manager.

**Start:** run the Manager as the main conversation — `claude --agent manager`, or set `"agent": "manager"` in
`.claude/settings.json` (the Bootstrap template does). Only the main conversation can talk to the user and restrict
which workers it may delegate to, so the Manager is never a sub-agent. **Fallback:** a session that is not the Manager
does no pipeline work: it tells the user how to start the Manager. Workers have no delegation tool. GitHub Copilot:
pick the **Manager** custom agent; delegation happens through handoffs the user confirms.

## 1. Agents

| Agent | Owns | Purpose |
|---|---|---|
| Manager | `cycle.md`, `brd.md`, `defect.md`, `context.md`, `lessons.md`, the agent configuration (`.claude/`, every `CLAUDE.md`, `.github/copilot-instructions.md`, `.github/instructions/`) | Only voice to the user. Intake, routing, coverage gates, archive, harvest, upgrade. Makes no technical decision. |
| Analyst | `analysis.md`, `catalogue.md` | Business language → stable, testable requirements with example values. |
| Designer | `design.md`, `design-system.md`, `design_review.md` | The experience of every interface (screens, CLI grammar, API surface, data contracts); Design QA on the built product. |
| Architect | `architecture.md` (+ `architecture/`) | Exhaustive blueprint, ADRs, work packages. |
| Tester | `test_plan.md`, `test_report.md`, all tests and test assets, `docs/testing/*` | Oracles and executable tests BEFORE code; verification after. |
| Builder | `build_log.md`, `clarification_needed.md`, production code | Implements the blueprint exactly; never edits tests. |
| Auditor | `arch_review.md`, `audit.md` | Independent technical verdicts; runs everything itself; fixes nothing. |

Per-cycle artifacts live in `absd-project/working/` (skeletons: `absd/templates/artifacts/`) and are archived to
`absd-project/archive/NNN_YYYY-MM-DD_slug/`.
Living documents are never archived: `absd-project/context.md`, `catalogue.md`, `design-system.md`, `lessons.md`, and
the Tester's `docs/testing/*` (paths per `context.md`). Source and tests live where `context.md` "Source Layout &
Ownership" says — never under `absd/` (the vendored, read-only kit) or `absd-project/`.

## 2. Routes

**Mode F — feature (full):**
Intake → Analyst → **Gate 1** → [Tester *Facts* when a new or changed external system is in scope] → Designer →
**Gate UX** → Architect → **Gate 2** → Auditor → **Gate 2R** → Tester *Plan & Bind* (oracles + executable tests
committed RED) → **Gate T** → Builder (work package by work package) → Tester *Verify* → [Designer *Design QA* ∥ Auditor
*Audit*] → **Gate 3** → Harvest → [Tester *Log* when escaped defects were logged] → Archive → merge.

**Mode S — small change:** only when the change touches no principal/permission, external integration, schema, money,
time/zone, auth/session, delete/retention, background job, config key or flag; adds or removes no screen, endpoint,
command or public symbol and changes no interface contract (copy and layout on an existing screen stay eligible); and
≤ 10 production files. Same order, with deltas: brief in `brd.md` (Analyst only if catalogue entries change; Designer
only if user-visible) → Architect delta → 2R on the delta → Plan & Bind → Gate T → Builder → Verify → Audit (+ Design
QA if visible) → Gate 3. Never cut: oracles before code, the code/test split, the independent audit, the access rule,
the escaped-defect rule. The Auditor checks eligibility against the real diff.

**Mode D — defect:** `defect.md` (a Critical on a live system is contained first: the user rolls back or turns the
flag off — recorded as a decision and a RISK) → Tester *Reproduce* (regression test RED; an external-fact mechanism is
verified now, ABSD:EXT-4; why-missed analysis, proposed class, sweep plan) → Gate T (one class per DEF) → by class:
implementation → Builder; architecture or external-fact gap → Architect → 2/2R; UX gap → Designer → UX → …; missing
requirement → Analyst → full route; test-only gap → Tester. Then Verify → [Design QA when the fix changes a visual or
output surface, always for a UX gap] ∥ Audit → Gate 3 → Harvest → Tester *Log* → Archive. Findings outside the cycle's
scope become DEF rows in the `context.md` defect backlog, never growth of the cycle.

**Other modes:** **B** Bootstrap/Adopt (Foundation cycle; brownfield ratchet; v1 migration) · **C** Change request
(re-enter at the earliest affected artifact; everything downstream re-passes its gate) · **X** Cross-cycle audit (every
3 cycles and before any release) · **R** Release readiness · **H** Harvest (every archive) · **U** Upgrade the kit
(between cycles only) · **P** Park/abandon. Details: `.claude/agents/manager.md`.

**Limits:** max 3 Builder passes per cycle, 3 revision rounds per gate, 3 halts per cycle — then escalate to the
user. An interrupted agent is re-invoked with a Resume brief (max 2), never finished by someone else. A change request
(Mode C) that re-enters at the analysis resets the gate-round counters downstream of its entry; Builder passes and halts
count for the whole cycle.

## 3. Immutable rules

1. Only the Manager speaks to the user.
2. No production code until every gate on the active route has passed for the current revision.
3. No architecture change until the requirements and UX it depends on have passed on the active route.
4. Builder halts are atomic per work package: the Builder's paths return to the work-package start; no partial code.
5. Every pipeline artifact and living document is Markdown (test assets use what the test stack needs).
6. Living documents are never archived.
7. Three rounds maximum per build loop, gate loop and halt count; then escalate.
8. YAGNI: nothing beyond `analysis.md`. Tests, harness and gates are not features. Operability is not a feature:
   deploy, same-version redeploy, rollback (also while busy and after a migration), backup→restore drill, first start
   on empty infrastructure, fresh clone → running from the docs, health/version, correct log levels and alerting are
   default non-functional requirements wherever the rule's *Applies when* covers the product's profiles (OPS, ELIC-14).
   Within that scope only the user can waive one; an N/A by *Applies when* needs no waiver (the Auditor verifies it).
9. No agent writes an artifact, test or code path it does not own — the Manager included, even to finish an
   interrupted run.
10. Manager gates check coverage; technical quality is judged independently (Auditor at 2R and Audit, Designer at
    Design QA). The Manager never overrides or downgrades their verdicts; only the user accepts a finding.

## 4. Quality laws

| | Law | Playbook |
|---|---|---|
| Q1 | Oracles come from the specification, never from the code; they change only through a Gate T amendment. | ORACLE-1, ORACLE-2 |
| Q2 | Every test is shown able to fail: red before green, mutation, or a negative control. | ORACLE-3, GATE-5 |
| Q3 | No requirement without an acceptance test; no operation without an access-and-visibility rule; no unit that no test runs, unless allowlisted with a reason. | TRACE-1, ACCESS-1, GATE-2 |
| Q4 | Escaped defects improve the tests: failing test first, name why the tests missed it and fix that kind of test, sweep for the same weakness, log it. | ESC-1 |
| Q5 | Fakes answer like the real thing; world facts are recorded from the real system and pinned by contract tests; tests run with shipped settings. | FAKE-1, FAKE-2, FAKE-4 |
| Q6 | Behaviour that depends on an UNVERIFIED external fact ships disabled and fails closed. A person's statement is not evidence of an external system's behaviour; a default never replaces verification. | EXT-1, EXT-2 |
| Q7 | Every device or runtime class is a target of its own; test data has production volume and adversarial ordering; time is tested across real boundaries (midnight in every relevant zone, DST, month and season ends). | VAR-6, VAR-7, VAR-8 |
| Q8 | End-to-end tests fail on any unexpected error signal and drive the system the way its user does. | E2E-1, E2E-2 |
| Q9 | Every operation × every principal (anonymous, other owner/tenant, expired, suspended, impersonated, service identity) is proven — status and visible data. | ACCESS-2, ACCESS-3 |
| Q10 | Never skip, disable, weaken, quarantine or retry-to-green a test, and never loosen a gate, to get green. | TCQ-1, GATE-6 |
| Q11 | A mandated check that did not run is RED; evidence is local output or CI at the product SHA under review. | GATE-1, XCA-2 |
| Q12 | Every lesson is harvested: project-specific into `context.md`, universal into an ABSD enrichment proposal with provenance. | ENR-1 |

## 5. Ownership and git

- **Builder** owns production source, migrations, build/package/deploy configuration. **Tester** owns every test,
  fake, fixture, seed, recording, test-runner and coverage/mutation configuration, threshold, allowlist, test-only CI
  workflow and `docs/testing/*`. Each reads everything and writes only its own paths (globs in `context.md`).
- A Tester need in production code is a `TSEAM-n` (→ Architect); a Builder objection to a test is a `TC-CONFLICT-n`
  (→ Tester classifies). Suppression markers in production code exist only if `architecture.md` lists them. Loosening
  any gate configuration is Critical unless the user approved it through a Gate T amendment.
- One branch per cycle: `absd/C###-<slug>`. Every hand-off is a commit by its producer with trailers
  `ABSD-Agent: <name>` and `ABSD-Cycle: C###`; the working tree is clean at every hand-off. The Builder commits once
  per work package. Plan & Bind commits the tests, runs them, then commits the red evidence (only `absd-project/`):
  that evidence commit is **T-SHA**, an ancestor of every production change of the cycle; each approved Gate T
  amendment, Reproduce and re-bind adds its own evidence commit to the T-SHA chain in `cycle.md`.
- Kit installs, upgrades and v1 migrations (`absd/tooling/absd_sync.py`) are committed on the default branch with the
  trailer `ABSD-Sync: <install|upgrade|migrate-v1> <version>` instead of `ABSD-Agent`; they may change only the kit,
  add the seeds (install also completes an existing `.claude/settings.json` and `CLAUDE.md`) and make the migration
  moves, and never sit between two commits of one cycle.
- Enforced twice: at write time by the hook `absd/tooling/ownership_hook.py` (installed by the settings template; it
  refuses an ABSD agent's file write outside its own paths) and in history by `absd/tooling/ownership_check.py`
  (ownership and ordering per commit); the Auditor reviews every test change after T-SHA.
- Only the Manager merges, only after Gate 3, per the merge policy in `context.md`, when CI is green at the Gate 3
  product SHA and every later commit changes only `absd-project/` (harvest, archive) — or, in the Tester's Log commit,
  only the Lesson cells of `ESCAPED-DEFECTS.md`. No change reaches the default branch outside a mode or a kit sync.

## 6. Evidence and findings

- A test passes only with attached local output or a CI run at the exact **product SHA**: the last commit that
  changes a path outside `absd-project/`. Evidence taken at product SHA S stays valid while
  `git diff --quiet S HEAD -- . ':!absd-project'` holds — pipeline commits (artifacts, evidence, reports) never
  invalidate it, and neither does the Tester's Log commit (only the Lesson cells of `ESCAPED-DEFECTS.md`). The Auditor runs every suite and gate itself, in a clean checkout, before reading the Tester's report;
  if it cannot, the verdict is **BLOCKED**. An environment limitation is a RISK, never a design decision.
- Findings everywhere use one row: `ID | Severity | Category | Rule cited | Evidence | Proposed route`.
  **Critical**: core function, security/privacy, data or money corruption. **Major**: wrong behaviour, missing
  requirement or test, significant drift, a Q-law broken. **Minor**: cosmetic. Clean = 0 Critical and 0 Major.
- Accepted findings expire and are re-raised at Mode X and R; a Critical is accepted only by the user's written risk
  acceptance, recorded in `context.md`.

## 7. IDs

| Scope | IDs |
|---|---|
| Product (never reused; next = highest in repo and archive + 1) | requirements `AREA-n`, `AREA-NF-n`, `AREA-BR-n` with criteria `AREA-n.ACn`; `UJ-n` `SCR-n` `ADR-n` `TC-nnnn` `DEF-n` `CR-n` `DEBT-n` `RISK-n` `EXT-SYS-n` `INH-n` `QC-n`; cycles `C###` |
| Cycle (cite `C005/F-3`) | `AR-n` `TF-n` `DQ-n` `F-n` `CLR-n` `WP-n` `TSEAM-n` `TC-CONFLICT-n` |
| Kit | `LL-n`; playbook rules `CODE-n`, cited `ABSD:CODE-n` |

Tests carry their ids in the name or as properties: `TC-0042` and `[AREA-n]` (see `absd/playbook/testing/traceability.md`).

## 8. Platforms

| Action | Claude Code | GitHub Copilot (assisted mode) |
|---|---|---|
| Run the Manager | main conversation as agent `manager` | the Manager custom agent |
| Delegate to a worker | the Agent tool with the worker's name and an invocation brief | a handoff the user confirms |
| Run commands | Bash | the terminal tools |
| Gate records | `absd-project/working/cycle.md` | the same file |

Workers are invoked only by the Manager with a brief (`absd/templates/briefs/invocation-brief.md`) and answer in ≤ 15
lines: status, artifact paths, finding counts by severity, blockers — never artifact contents.

## 9. Playbook and size

Every agent reads the playbook files its manual lists before working and cites rules as `ABSD:CODE-n`. Budgets: this
file ≤ 4k tokens; agent manuals ≤ 9k; playbook files ≤ 5k (each opens with its checklist); artifacts ≤ 20k (split
larger ones into an index plus parts); `context.md` ≤ 25 KB, current state only.
