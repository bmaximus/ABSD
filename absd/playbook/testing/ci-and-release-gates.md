# CI and release gates — job graph, hermetic runs, integrity, deploy

Code **GATE** (shared with `absd/playbook/testing/gates.md`, home of GATE-1..8 and the gate register). This file: the CI
job graph, readable failures, hermetic CI, the migration gates, the secret canary, the pipeline-integrity checks and
deploy gating. Lane contents: STRAT-7, STRAT-8 (`absd/playbook/testing/strategy.md`); post-deploy checks and rollback:
OPS (`absd/playbook/testing/nonfunctional.md`); tools: `absd/tooling/`. Every gate here has a gate-register row with
its negative control (GATE-8), and its invocation and thresholds are indexed in the Tester's `TESTING.md` §2.

## Checklist

- [ ] Job graph declared; push jobs required; nightly random + parallel; live jobs off the push path (GATE-9)
- [ ] A red scheduled job blocks the next cycle start; one not run yet is triggered, not routed to Mode D (GATE-9)
- [ ] Every red run shows cause and remedy on the run page; reports only from real results (GATE-10)
- [ ] No unnecessary external pulls; exact tool versions; a throwaway store per run and worker (GATE-11)
- [ ] Every push: migrate from empty, upgrade previous release with data, drift, empty-infrastructure boot (GATE-12)
- [ ] A canary in every secret input; none in any log, report, artifact or diff (GATE-13)
- [ ] ownership_check with `--base` and the whole T-SHA chain; catalogue report on every push (GATE-14)
- [ ] Plan gates (trace_check, plan conformance) run while a cycle is active; else the "no active cycle" notice (GATE-14)
- [ ] Merge: CI green at the Gate 3 product SHA; later commits only `absd-project/` or Log-step Lesson cells (GATE-14)
- [ ] Ownership hook installed from the settings template (GATE-14)
- [ ] Deploy only the exact commit of a green push-triggered run, one release at a time (GATE-15)

## Rules

**GATE-9** — Declare the CI job graph in `architecture.md` "Quality gates & CI" and `TESTING.md`: per job its lane
(STRAT-7, STRAT-8), trigger, owner (Tester: test, gate and nightly workflows; Builder: build, package, deploy), time
limit and required status; every push-lane job is a required check for merge. The nightly runs the whole suite in random
order with a printed, replayable seed, ≥ 2 parallel workers with a store each and every test repeated, in a concurrency
group no push cancels. Live contract jobs (FAKE-10) run on schedule and on demand, never as a push dependency. A red
scheduled job alerts a named owner and blocks the next cycle start (Mode D first); one that has not run yet — the first
nightly after Foundation — is triggered, and its result decides (STRAT-8).
- *Why:* date bugs hide until a run happens while UTC and local dates differ (LL-40); a missing credential left the live
  job silently green (LL-25); an order-dependent test passed only in the runner's default order (INTEG-4); the first
  cycle after Foundation had no nightly yet, and Mode D cannot fix "not run" (LL-55).
- *Check:* workflow triggers, concurrency and time limits match `TESTING.md`; nightly logs show seed and workers; the
  Manager's cycle-start record cites the last green nightly and live runs, or the run it triggered.
- *Applies when:* always.
- *Provenance:* LL-25, LL-40 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

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

**GATE-14** — Run the pipeline-integrity checks in a Tester-owned workflow. On every push of a cycle branch:
`absd/tooling/ownership_check.py --base <default branch from context.md §1>` (on the default branch itself, `--range`
instead), once Gate T passed every T-SHA of the `cycle.md` chain oldest first (`--t-sha <first> --t-sha <amendment> …`),
`--strict` once Source Layout covers the tree. On every push: the `absd/tooling/traceability_report.py` catalogue run
(TRACE-6). Only while `absd-project/working/test_plan.md` exists (an active cycle): the plan-conformance run (TRACE-9)
and `absd/tooling/trace_check.py` with the invocation recorded for each gate `cycle.md` lists as passed, so an edit
reopening a passed gate turns CI red; without one the step prints the notice "no active cycle" — an *Applies when*
condition, not a skip (GATE-1). The merge needs CI green at the Gate 3 product SHA, and every later commit changes only
`absd-project/` (harvest, archive) or, in the Tester's Log commit, only the Lesson cells of `ESCAPED-DEFECTS.md`
(`absd/RULES.md` §5). Keep `absd/tooling/ownership_hook.py` installed as the blocking write-time hook from the
settings template.
- *Why:* the orchestrator wrote other agents' artifacts and code after session limits (LL-26); tests written by the code
  author after the code had no independent oracle (LL-29); a catalogue report exposed untested requirements (LL-36);
  plan gates re-run after the archive had emptied `working/` exited 2 on the default branch, and a re-bind's new T-SHA
  turned earlier work-package commits into "production before Gate T" (LL-55).
- *Check:* the steps sit in a Tester-owned workflow; a Builder-attributed commit to a test path on a throwaway branch
  turns ownership_check RED; the plan step's condition tests for the plan file; the `--t-sha` list equals the
  `cycle.md` chain; the Manager checks the post-Gate-3 commits before merging; the Auditor confirms the hook is
  configured (L8).
- *Applies when:* always; the plan gates while a cycle is active.
- *Provenance:* LL-26, LL-29, LL-36 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

**GATE-15** — Start a deploy only from a verification run that concluded green as a whole at the exact commit released,
triggered by a push to the release branch — never a schedule, pull request or other branch — with the operator's
auto-deploy switch on; release that run's tested artifact (OPS-2); run releases one at a time, queued and never
cancelled midway; keep manual dispatch as the audited override with validated inputs and a dry-run mode.
- *Why:* scheduled CI runs would have triggered the release workflow every night (LL-33).
- *Check:* a decision-table test of the release condition (event × conclusion × branch × switch), or the logic in a
  tested script (GATE-8); release concurrency queues; the Auditor matches the released commit to the tested one.
- *Applies when:* the product deploys or publishes automatically.
- *Provenance:* LL-33 (KatenatsioTipster, 2026-10)
