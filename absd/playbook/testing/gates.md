# Quality gates — thresholds, CI wiring, release gating

Code **GATE**. The mechanical checks that decide merge, Gate 3 and deploy: a check that did not run, untested units,
coverage, static checks, mutation, flakes, ownership of gate configuration, gates proven able to fail, the CI job graph,
readable failures, hermetic CI, migration, secret-canary and pipeline-integrity gates, deploy gating. Lane contents:
STRAT-7, STRAT-8 (`absd/playbook/testing/strategy.md`); post-deploy checks and rollback: OPS
(`absd/playbook/testing/nonfunctional.md`); tools: `absd/tooling/`. Thresholds and invocations are indexed in the
Tester's `TESTING.md` §2.

## Checklist

- [ ] Every mandated check missing, skipped, cancelled or without its credential is RED (GATE-1)
- [ ] No unit that no test runs, except reasoned allowlist entries; no stale entry; additions user-approved (GATE-2)
- [ ] Merged coverage of every production language ≥ floor; the floor rises when the gate reports headroom (GATE-3)
- [ ] Strict compile/type check, warnings as errors, lint, format, workflow/script lint, layer test: 0 findings (GATE-4)
- [ ] Mutation: changed code ≥ threshold; 100% of money/time/access rules killed or negative-controlled (GATE-5)
- [ ] Retries 0 (unit, integration, contract, setup), ≤ 1 (e2e); each pass-on-retry is a Major TF (GATE-6)
- [ ] No gate loosened without the user's approval recorded as a Gate T amendment (GATE-6)
- [ ] Gate configuration lives in Tester-owned paths indexed in `TESTING.md` §2 (GATE-7)
- [ ] Every gate shown RED once by its negative control, then GREEN; gate scripts have tests (GATE-8)
- [ ] Job graph declared; push jobs required; nightly random + parallel; live jobs off the push path (GATE-9)
- [ ] Every red run shows cause and remedy on the run page; reports only from real results (GATE-10)
- [ ] No unnecessary external pulls; exact tool versions; a throwaway store per run and worker (GATE-11)
- [ ] Every push: migrate from empty, upgrade previous release with data, drift, empty-infrastructure boot (GATE-12)
- [ ] A canary in every secret input; none in any log, report, artifact or diff (GATE-13)
- [ ] ownership_check, traceability_report and trace_check in CI; ownership hook installed (GATE-14)
- [ ] Deploy only the exact commit of a green push-triggered run, one release at a time (GATE-15)

## Rules

**GATE-1** — Treat a mandated check that did not run as RED: a missing secret or credential, an unset environment
variable, a skipped, cancelled or timed-out required job, a missing or empty report, zero tests collected, a focus
marker or CI-only filter that drops tests, a test skipped at run time, or a harness that reached no verdict fails the
run with its reason — never exit 0 with a warning. Lanes select tests by declared category, never by skipping. Merge,
Gate 3 and deploy conditions require each check's success, not the absence of its failure.
- *Why:* audits certified suites they had never run (LL-24); the nightly live-contract job printed a warning and exited
  0 when its credential was missing (LL-25).
- *Check:* negative controls include "input missing" and "credential missing" (GATE-8); the Auditor reconciles
  executed = planned and skipped = 0 per lane in a clean checkout (XCA-2); CI conditions name every required job.
- *Applies when:* always — every lane, every profile.
- *Provenance:* LL-24, LL-25 (KatenatsioTipster, 2026-10)

**GATE-2** — Fail the build on any production unit no test executes — a class in class-based languages, else a file or
module (`absd/tooling/coverage_gate.py --untested-allowlist <path>`, `--min-lines` ≤ 5) — unless the Tester's allowlist
names it with a valid reason. An entry without a reason fails; a stale entry (unit now tested or gone) is removed in the
same change; a new entry is an exclusion needing a user-approved Gate T amendment (GATE-6), except the Mode B Baseline
seeding ("baseline pre-ABSD — DEBT-n", burned down). Only unit, integration and contract reports count (STRAT-6).
- *Why:* a results reader shipped with 0% coverage behind a total floor and read half-time as the final score; the sweep
  this gate forced found six more untested areas (LL-2).
- *Check:* push-lane step; valid reasons: schema seam without behaviour, design-time factory, development-only shim off
  in tests and production, generated code — "hard to test", "trivial", "covered elsewhere" are rejected (Auditor); Gate
  3 lists every allowlist change.
- *Applies when:* always, every profile.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**GATE-3** — Gate total line coverage merged across every unit, integration and contract suite of every production
language (a line is covered if any suite ran it; Cobertura XML or LCOV) against a floor that only rises: brownfield
starts at the measured value, greenfield at the Foundation's value (80% recommended). When the gate reports ≥ 1 point of
headroom, the Tester raises the floor in the same cycle. Exclusions are reviewed path patterns for generated code only,
listed in `TESTING.md`.
- *Why:* a static floor lets coverage slide unnoticed; a production language that emits no report is invisible.
- *Check:* `coverage_gate.py --reports <glob per language> --min-total <floor> --layer <name=regex>`, per-layer table in
  the run summary; a language without a report is RED (GATE-1); the floor's history never decreases without an approved
  amendment.
- *Applies when:* always.
- *Provenance:* industry baseline

**GATE-4** — Compile and type-check every language — tests, scripts and build files included — in its strictest
practical mode with warnings as errors, and run linters, formatters in check mode, workflow and shell-script linters and
the layer-rule test (ARCH-1) as push-lane gates with zero findings; settings live once at repository level so new
projects inherit them; production code carries a suppression marker only where `architecture.md` lists it (ARCH-23).
- *Why:* warnings pile up and hide defects (null dereferences, ignored results, injection in workflow expressions);
  per-project settings let a new project opt out silently.
- *Check:* one planted warning turns the static job RED (GATE-8); the Auditor greps suppression markers against
  `architecture.md`; rule sets per CODE rules in `absd/playbook/engineering/code-quality.md`.
- *Applies when:* always.
- *Provenance:* industry baseline
- Illustration: e.g. warnings-as-errors with nullable analysis (C#), `strict` (TypeScript), `mypy --strict` (Python); actionlint for workflows, shellcheck for scripts.

**GATE-5** — Run mutation testing on the production lines changed in the cycle — per push or at the latest at Verify on
the cycle HEAD, the whole codebase nightly — with a score threshold in `TESTING.md` (default ≥ 80% on changed code), and
require 100% of mutants on lines implementing money, time and access rules killed or, where no mutant can express the
fault, an explicit negative control per rule (ORACLE-13); equivalent mutants are recorded with a reason (ORACLE-14).
- *Why:* coverage proves lines ran, not that an assertion notices them being wrong; a test that runs a calculation
  without asserting its result satisfies every coverage gate.
- *Check:* `test_report.md` shows the changed-code score and, per money/time/access rule, mutants, killed and controls;
  the Auditor injects ≥ 1 fault per such rule in a throwaway worktree and sees a test fail (XCA-2).
- *Applies when:* always; the 100% clause wherever money, time or access rules exist.
- *Provenance:* industry baseline
- Illustration: e.g. Stryker (C#, JavaScript), PIT (JVM), mutmut (Python), cargo-mutants (Rust).

**GATE-6** — Set retries explicitly in every runner configuration: 0 for unit, integration and contract tests and for
setup or seed steps, at most 1 for end-to-end. Report every pass-on-retry from the runner's retry-aware report as a
Major TF until root-caused (fixing a flake is Mode D); it never counts as verifying a requirement. Never loosen a gate —
threshold down, retries up, exclusion or allowlist entry added, check moved to a slower lane (STRAT-9), baseline or
golden file regenerated to pass, gate step removed — without the user's approval recorded as a Gate T amendment.
- *Why:* one silent retry turns a flaky proof green and the acceptance report counts it as verified; a gate relaxed to
  get green guards nothing.
- *Check:* runner configs in Tester paths show the values; `test_report.md`'s flake report lists each retried test; the
  Auditor diffs gate configuration since the cycle start against approved amendments — an unapproved loosening is
  Critical.
- *Applies when:* always.
- *Provenance:* industry baseline

**GATE-7** — Keep every gate's configuration — thresholds, retries, exclusions, allowlists, lane membership,
required-check list, runner and mutation settings, gate invocations in test workflows — in Tester-owned paths declared
in `context.md` "Source Layout & Ownership" and indexed in `TESTING.md` §2 (file and line per value). Compiler, analyzer
and formatter settings stay Builder-owned build configuration per `architecture.md`; weakening them is a loosening too
(GATE-6). The Builder raises a TC-CONFLICT instead of editing a gate.
- *Why:* a gate owned by the agent it judges can be relaxed in the same commit that needs it relaxed.
- *Check:* `ownership_check.py` reports any non-Tester commit to these paths (GATE-14); the Auditor diffs them every
  cycle.
- *Applies when:* always.
- *Provenance:* industry baseline

**GATE-8** — Prove every gate can fail: the kit tools' own tests (`absd/tooling/test_*.py`) run in the push lane on the
product's interpreter; every product-specific gate, report or release script has tests for pass, fail, boundary,
malformed and missing input asserting exit code and message; in the Foundation cycle — and whenever a gate's invocation
or configuration changes — the Tester shows each gate RED with its negative control (Gate register) on a throwaway
branch, then GREEN, both runs linked in `test_report.md`.
- *Why:* a buggy gate blocks good merges or lets everything through, silently; the live job that exited 0 without its
  credential had never been seen failing (LL-25).
- *Check:* one red and one green run per register row; each control follows ORACLE-13 (tree byte-identical afterwards).
- *Applies when:* always.
- *Provenance:* LL-25 (KatenatsioTipster, 2026-10)

**GATE-9** — Declare the CI job graph in `architecture.md` "Quality gates & CI" and `TESTING.md`: per job its lane
(STRAT-7, STRAT-8), trigger, owner (Tester: test, gate and nightly workflows; Builder: build, package, deploy), time
limit and required status; every push-lane job is a required check for merge. The nightly runs the whole suite in random
order with a printed, replayable seed, ≥ 2 parallel workers with a store each and every test repeated, in a concurrency
group no push cancels. Live contract jobs (FAKE-10) run on schedule and on demand, never as a push dependency. A red or
not-run scheduled job alerts a named owner and blocks the next cycle start (STRAT-8).
- *Why:* date bugs hide until a run happens while UTC and local dates differ (LL-40); a missing credential left the live
  job silently green (LL-25); an order-dependent test passed only in the runner's default order (INTEG-4).
- *Check:* workflow triggers, concurrency and time limits match `TESTING.md`; nightly logs show seed and workers; the
  Manager's cycle-start record cites the last green nightly and live runs.
- *Applies when:* always.
- *Provenance:* LL-25, LL-40 (KatenatsioTipster, 2026-10)

**GATE-10** — Make every failure readable on the run page: each failing suite or gate posts the failing test, rule or
unit, its first failure messages and the remedy ("add a test, or list it with its reason in <file>") as annotations or a
run summary, and keeps its machine-readable result as a run artifact; badges and dashboards come only from the run's
real results, each claimed gate mapped to a job that passed.
- *Why:* failure output posted as annotations was readable without raw logs, which agents often cannot fetch (LL-31); a
  report card listed gates from a static list, whatever had run.
- *Check:* the Auditor finds a red run's cause and remedy without opening raw logs; kit tools write annotations and
  `--summary-md`.
- *Applies when:* always.
- *Provenance:* LL-31 (KatenatsioTipster, 2026-10)

**GATE-11** — Keep CI red only for reasons inside the change: no unauthenticated or per-run pulls of images or packages
a run does not need (preinstalled services, mirrors or caches instead), every tool, test runner and third-party CI step
at an exact immutable version shared with local and post-deploy runs, a throwaway store per run and worker (INTEG-3),
ephemeral ports and a time limit per job; an infrastructure failure is fixed at its root, never re-run until green.
- *Why:* CI broke with no code change when an image registry's anonymous pull limit was hit (LL-30).
- *Check:* the Auditor reads workflows for pulls and floating versions; a red run caused by infrastructure gets a DEF or
  DEBT row.
- *Applies when:* always.
- *Provenance:* LL-30 (KatenatsioTipster, 2026-10)

**GATE-12** — Run the migration gates on every push against the production engine and major version: (a) migrate from
empty with the shipped migrations; (b) upgrade a store at the previous release's schema holding representative data and
assert the data survives (counts, sums, sampled rows); (c) fail on model ↔ migration drift; (d) boot the shipped
artifact on empty infrastructure with production configuration (OPS-1). Every other test store is built only by
migrations (INTEG-2).
- *Why:* tests auto-created the schema, so a migration snapshot missing ~60% of the columns passed four audits (LL-21);
  the service crashed at start-up on a database that did not exist yet (LL-14).
- *Check:* four named push-lane steps; a model change without its migration turns (c) RED; the previous-release fixture
  is refreshed at every release.
- *Applies when:* the product owns persistent state; (d) for every deployed or installed artifact.
- *Provenance:* LL-14, LL-21 (KatenatsioTipster, 2026-10)
- Illustration: drift checks, e.g. EF Core `has-pending-model-changes`, Django `makemigrations --check`, Prisma `migrate diff --exit-code`.

**GATE-13** — Run a secret-canary gate in the push lane: give every secret input — environment, settings files,
deployment manifests, CI variables, test credentials — a unique canary value, run the suites, dry runs and deploy-script
tests, scan every log, report, artifact, diff and run summary, and fail on any canary; scan the repository and its
history for secrets on every push.
- *Why:* a secret pasted into a deployment manifest reached a CI log through a dry-run diff (LL-8).
- *Check:* canaries cover every secret key in `architecture.md`'s configuration table; a test printing a setting turns
  the gate RED (GATE-8); masking and rotation per SEC rules in `absd/playbook/security/baseline.md`.
- *Applies when:* the product or its pipeline handles any secret or credential.
- *Provenance:* LL-8 (KatenatsioTipster, 2026-10)

**GATE-14** — Run the pipeline-integrity checks on every push of a cycle branch: `absd/tooling/ownership_check.py`
(range from the default branch; `--t-sha` from `cycle.md` once Gate T passed; `--strict` once Source Layout covers the
tree), `absd/tooling/traceability_report.py` (catalogue and plan-conformance runs per TRACE rules in
`absd/playbook/testing/traceability.md`) and `absd/tooling/trace_check.py` with the invocation recorded for each gate
`cycle.md` lists as passed, so an edit reopening a passed gate turns CI red. Keep `absd/tooling/ownership_hook.py`
installed as the blocking write-time hook from the settings template.
- *Why:* the orchestrator wrote other agents' artifacts and code after session limits (LL-26); tests written by the code
  author after the code had no independent oracle (LL-29); a catalogue report exposed untested requirements (LL-36).
- *Check:* the steps sit in a Tester-owned workflow; a Builder-attributed commit to a test path on a throwaway branch
  turns ownership_check RED; the Auditor confirms the hook is configured (L8).
- *Applies when:* always.
- *Provenance:* LL-26, LL-29, LL-36 (KatenatsioTipster, 2026-10)

**GATE-15** — Start a deploy only from a verification run that concluded green as a whole at the exact commit released,
triggered by a push to the release branch — never a schedule, pull request or other branch — with the operator's
auto-deploy switch on; release that run's tested artifact (OPS-2); run releases one at a time, queued and never
cancelled midway; keep manual dispatch as the audited override with validated inputs and a dry-run mode.
- *Why:* scheduled CI runs would have triggered the release workflow every night (LL-33).
- *Check:* a decision-table test of the release condition (event × conclusion × branch × switch), or the logic in a
  tested script (GATE-8); release concurrency queues; the Auditor matches the released commit to the tested one.
- *Applies when:* the product deploys or publishes automatically.
- *Provenance:* LL-33 (KatenatsioTipster, 2026-10)

## Gate register

Foundation DoD: every row RED once by its negative control, then GREEN (GATE-8).

| Gate | Mechanism | RED when | Negative control | Rule |
|---|---|---|---|---|
| Ran at all | CI conditions, exit codes | not run, skipped, no input, no credential | unset a required credential | GATE-1 |
| Untested unit | `coverage_gate.py --untested-allowlist` | unit no test runs; entry without reason | add an untested unit | GATE-2 |
| Coverage floor | `coverage_gate.py --min-total` | merged total below floor; no report | floor 1 point above measured | GATE-3 |
| Static | compilers, linters, layer test | any warning or finding | an unused variable; a layer breach | GATE-4 |
| Mutation | mutation tool, changed lines | score below threshold; rule survivor | delete one money-TC assertion | GATE-5 |
| Flake | runner retry report | a pass on retry | a test failing only on first attempt | GATE-6 |
| Access completeness | matrix completeness test | operation without row or row without operation | add an unruled operation | ACCESS-1 |
| Error signals | shared end-to-end fixture | page/console error, 5xx, stderr, error log | emit one console error | E2E-1 |
| Catalogue + plan | `traceability_report.py` | failing, unknown or untested id, missing planned TC | link an unknown id | TRACE-1 |
| Artifact coverage | `trace_check.py gate <g>` | upstream id missing downstream | drop one AC from `test_plan.md` | GATE-14 |
| Ownership + order | `ownership_check.py` | foreign path, code before T-SHA, unattributed | Builder commit to a test path | GATE-14 |
| Migrations | empty, previous release, drift | error, data lost, drift | model change, no migration | GATE-12 |
| Empty-infra boot | shipped artifact, production config | not ready on its version in time | remove a required setting | OPS-1 |
| Secret canary | scan of logs, reports, artifacts, diffs | a canary appears | a test prints a secret setting | GATE-13 |
| Accessibility | scan per rendered state | serious or critical violation | remove one field label | A11Y-1 |
| Visual | baseline comparison | difference beyond tolerance | move one element 4 px | VIS-2 |
| Performance | budgets, query count | budget breached; N+1 | add a per-item query | PERF-1, PERF-2 |
| Live contract | scheduled job (FAKE-10) | fact broken; credential missing | run without the credential | GATE-1 |
| Deploy condition | release trigger | deploys from a non-push or red run | replay a scheduled-run event | GATE-15 |
