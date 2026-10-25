# Quality gates — thresholds, ownership, proof that gates fail

Code **GATE**. The mechanical checks that decide merge, Gate 3 and deploy: a check that did not run, untested units,
coverage, static checks, mutation, flakes, ownership of gate configuration and test tooling, gates proven able to fail
and the gate register. CI job graph, readable failures, hermetic CI, migration, secret-canary, pipeline-integrity and
deploy gates (GATE-9..15): `absd/playbook/testing/ci-and-release-gates.md`. Lane contents: STRAT-7, STRAT-8
(`absd/playbook/testing/strategy.md`); post-deploy checks and rollback: OPS (`absd/playbook/testing/nonfunctional.md`);
tools: `absd/tooling/`. Thresholds and invocations are indexed in the Tester's `TESTING.md` §2.

## Checklist

- [ ] Every mandated check missing, skipped, cancelled or without its credential is RED (GATE-1)
- [ ] Every report glob matches a non-empty report; plan gates without an active cycle print a notice, never a skip (GATE-1)
- [ ] No unit that no test runs, except allowlist lines `<unit>  # <reason> · <owner> · <expires>` (GATE-2)
- [ ] `--fail-on-stale` in the push lane; allowlist additions user-approved (GATE-2)
- [ ] Merged coverage of every production language ≥ floor, one `--reports` glob per language (GATE-3)
- [ ] `--min-layer` floors on the money, time and access layers; floors rise on headroom (GATE-3)
- [ ] Strict compile/type check, warnings as errors, lint, format, workflow/script lint, layer test: 0 findings (GATE-4)
- [ ] Mutation: changed code ≥ threshold; 100% of money/time/access rules killed or negative-controlled (GATE-5)
- [ ] Retries 0 (unit, component, integration, contract, setup), ≤ 1 (e2e); a pass-on-retry is a finding of the cycle owning the test (GATE-6, ESC-11)
- [ ] No gate loosened without the user's approval recorded as a Gate T amendment (GATE-6)
- [ ] Gate configuration lives in Tester-owned paths indexed in `TESTING.md` §2 (GATE-7)
- [ ] Test tooling in a file the Tester does not own is a `TSEAM-n` of kind `tooling` (GATE-7)
- [ ] Every gate shown RED once by its negative control, then GREEN; gate scripts have tests (GATE-8)
- [ ] Negative controls: local in a worktree under `$TMPDIR`, never committed; CI ones on an unmerged `absd/neg-…` branch, deleted after (GATE-8)

## Rules

**GATE-1** — Treat a mandated check that did not run as RED: a missing secret or credential, an unset environment
variable, a skipped, cancelled or timed-out required job, a missing or empty report (a `--junit` glob matching no file
with a test case, a `--reports` glob matching no report with a coverable line: exit 2), zero tests collected, a focus
marker or CI-only filter that drops tests, a test skipped at run time, or a harness that reached no verdict fails the
run with its reason — never exit 0 with a warning. Lanes select tests by declared category, never by skipping. A check outside its *Applies when* is not a skip: the plan gates
need `absd-project/working/test_plan.md` and, with no active cycle, print the notice "no active cycle" (GATE-14);
the catalogue gate runs on every push. Merge, Gate 3 and deploy conditions require each check's success, not the
absence of its failure.
- *Why:* audits certified suites they had never run (LL-24); the nightly live-contract job printed a warning and exited
  0 when its credential was missing (LL-25); a mistyped report glob left a language ungated, and plan gates re-run
  after the archive failed every push between cycles (LL-55, LL-57).
- *Check:* negative controls include "input missing" (a glob that matches nothing) and "credential missing" (GATE-8);
  the Auditor reconciles executed = planned and skipped = 0 per lane in a clean checkout (XCA-2); CI conditions name
  every required job.
- *Applies when:* always — every lane, every profile.
- *Provenance:* LL-24, LL-25 (KatenatsioTipster, 2026-10); LL-55, LL-57 (ABSD v2 kit review, 2026-10)

**GATE-2** — Fail the build on any production unit no test executes — a class in class-based languages (named nested
types are units of their own; only compiler-generated types fold into their declaring type; an unqualified class name,
such as a Go converter's `-` or receiver type or a file stem, is a unit within its file), else a file or module
(`absd/tooling/coverage_gate.py --untested-allowlist <path> --fail-on-stale`, `--min-lines` ≤ 5) — unless the Tester's
allowlist names it with a valid reason, one line per unit: `<unit>  # <reason> · <owner> · <expires YYYY-MM-DD>`. An
entry without a reason fails; a stale entry (unit now tested or gone) fails the push lane, which reads every report, and
is removed in the same change; an entry past its expiry is a finding until tested or renewed; a new entry is an
exclusion needing a user-approved Gate T amendment (GATE-6), except the Mode B Baseline seeding ("baseline pre-ABSD —
DEBT-n", burned down). Only unit, component (STRAT-13), integration and contract reports count (STRAT-6).
- *Why:* a results reader shipped with 0% coverage behind a total floor and read half-time as the final score; the sweep
  this gate forced found six more untested areas (LL-2); stale entries that only warned outlived their units (LL-57);
  keyed by a bare class or file name, a whole package that no test ran merged into a tested one (LL-58).
- *Check:* push-lane step with `--fail-on-stale`; the tool requires the reason after `#`, the Auditor checks owner,
  expiry and validity — valid reasons: schema seam without behaviour, design-time factory, development-only shim off in
  tests and production, generated code; "hard to test", "trivial", "covered elsewhere" are rejected; Gate 3 lists
  every allowlist change.
- *Applies when:* always, every profile.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10); LL-58 (ABSD v2 acceptance
  review, 2026-10)

**GATE-3** — Gate total line coverage merged across every unit, component, integration and contract suite of every
production language (a line is covered if any suite ran it; Cobertura XML or LCOV) against a floor that only rises:
brownfield starts at the measured value, greenfield at the Foundation's value (80% recommended). Pass one `--reports`
glob per production language, and give each layer holding money, time or access rules a `--layer NAME=regex` with its
own `--min-layer NAME=pct` floor. When the gate reports ≥ 1 point of headroom, the Tester raises the floor in the same
cycle. Exclusions are reviewed path patterns for generated code only, listed in `TESTING.md`.
- *Why:* a static floor lets coverage slide unnoticed; a production language that emits no report is invisible; a
  mistyped glob silently left one language ungated, and a total floor lets a thin money layer hide behind well-covered
  plumbing (LL-57).
- *Check:* `coverage_gate.py --reports <glob per language> --min-total <floor> --layer <name=regex> --min-layer
  <name=pct>`, per-layer table in the run summary; a glob matching no report with a coverable line exits 2 and a layer
  matching nothing fails (RED, GATE-1); the Auditor maps every language in `context.md` Source Layout to a glob; the
  floor's history never decreases without an approved amendment.
- *Applies when:* always; `--min-layer` wherever money, time or access rules exist.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)

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
  the Auditor injects ≥ 1 fault per such rule in a throwaway worktree outside the project (ORACLE-13) and sees a test
  fail (XCA-2).
- *Applies when:* always; the 100% clause wherever money, time or access rules exist.
- *Provenance:* industry baseline
- Illustration: e.g. Stryker (C#, JavaScript), PIT (JVM), mutmut (Python), cargo-mutants (Rust).

**GATE-6** — Set retries explicitly in every runner configuration: 0 for unit, component, integration and contract tests
and for setup or seed steps, at most 1 for end-to-end. Report every pass-on-retry from the runner's retry-aware report as
a finding of the cycle that owns the test (ESC-11): in a test added or changed this cycle, a TF now — reproduced
deterministically, then the harness fixed or, when the product races, a Builder Fix; in an older test, a DEF in the
`context.md` §16 backlog, and a TF too only if it leaves an in-scope requirement unverified. An older flake that turns
the acceptance job red (TRACE-8) blocks the merge until fixed through Mode D. A pass-on-retry never verifies a
requirement. Never loosen a gate — threshold down, retries up, exclusion or allowlist entry added, check moved to a
slower lane (STRAT-9), baseline or golden file regenerated to pass, gate step removed — without the user's approval
recorded as a Gate T amendment.
- *Why:* one silent retry turns a flaky proof green and the acceptance report counts it as verified; a gate relaxed to
  get green guards nothing.
- *Check:* runner configs in Tester paths show the values; `test_report.md`'s flake report maps each retried test to
  its TF or DEF; the Auditor diffs gate configuration since the cycle start against approved amendments — an
  unapproved loosening is Critical.
- *Applies when:* always.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)

**GATE-7** — Keep every gate's configuration — thresholds, retries, exclusions, allowlists, lane membership,
required-check list, runner and mutation settings, gate invocations in test workflows — in Tester-owned paths declared
in `context.md` "Source Layout & Ownership" and indexed in `TESTING.md` §2 (file and line per value). Compiler, analyzer
and formatter settings stay Builder-owned build configuration per `architecture.md`; weakening them is a loosening too
(GATE-6). The Builder raises a TC-CONFLICT instead of editing a gate. Test tooling — test dependencies, runner,
coverage, mutation and test-lint configuration — lives in standalone Tester-owned files where the stack allows
(ADR-002); a setting that must sit in a file the Tester does not own (a package manifest, a build file) is a `TSEAM-n`
of kind `tooling` (→ Architect delta), and ADR-002 then lists the shared file sections the Tester may change.
- *Why:* a gate owned by the agent it judges can be relaxed in the same commit that needs it relaxed; runner
  dependencies and the test-tree lint sat in build files the Tester could not write, so the write-time hook blocked the
  Foundation (LL-57).
- *Check:* `ownership_check.py` reports any non-Tester commit to these paths (GATE-14); every Tester change to a shared
  file falls in a section ADR-002 lists; the Auditor diffs them every cycle.
- *Applies when:* always.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)

**GATE-8** — Prove every gate can fail: the kit tools' own tests (`absd/tooling/test_*.py`) run in the push lane on the
product's interpreter; every product-specific gate, report or release script has tests for pass, fail, boundary,
malformed and missing input asserting exit code and message; in the Foundation cycle — and whenever a gate's invocation
or configuration changes — the Tester shows each gate RED with its negative control (Gate register), then GREEN, both
runs linked in `test_report.md`. A local control runs in a throwaway worktree outside the project (under `$TMPDIR`,
ORACLE-13) and is never committed. A control that needs CI runs on a branch `absd/neg-C###-<n>` that is never merged
and is deleted after the run; its run URL is the evidence, and it is never an ancestor of the cycle branch, so
`ownership_check.py` never sees it.
- *Why:* a buggy gate blocks good merges or lets everything through, silently; the live job that exited 0 without its
  credential had never been seen failing (LL-25); a control worktree inside the project tripped the write-time
  ownership hook (LL-57).
- *Check:* one red and one green run per register row; the project tree byte-identical after each local control
  (ORACLE-13); no `absd/neg-…` branch merged, kept after its run or an ancestor of the cycle branch.
- *Applies when:* always.
- *Provenance:* LL-25 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

## Gate register

Foundation DoD: every row RED once by its negative control, then GREEN (GATE-8). Rows cite rules here, in
`absd/playbook/testing/ci-and-release-gates.md` (GATE-9..15) and in the files of their codes.

| Gate | Mechanism | RED when | Negative control | Rule |
|---|---|---|---|---|
| Ran at all | CI conditions, exit codes | not run, skipped, no input, no credential | unset a required credential | GATE-1 |
| Untested unit | `coverage_gate.py --untested-allowlist` | unit no test runs; entry without reason | add an untested unit | GATE-2 |
| Coverage floor | `coverage_gate.py --min-total`, `--min-layer` | total or a layer below its floor; a glob without coverable lines | floor 1 point above measured | GATE-3 |
| Static | compilers, linters, layer test | any warning or finding | an unused variable; a layer breach | GATE-4 |
| Mutation | mutation tool, changed lines | score below threshold; rule survivor | delete one money-TC assertion | GATE-5 |
| Flake | runner retry report | a pass on retry | a test failing only on first attempt | GATE-6 |
| Access completeness | matrix completeness test | operation without row or row without operation | add an unruled operation | ACCESS-1 |
| Error signals | shared end-to-end fixture | page/console error, 5xx, stderr, error log | emit one console error | E2E-1 |
| Catalogue + plan | `traceability_report.py` | failing, unknown or untested id, missing planned TC, a glob without test cases | link an unknown id | TRACE-1 |
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
