# Testing — what runs, where, and when

> Living, owned by the Tester, NEVER archived. Seeded at install; filled by the Tester at Foundation step 5 (Baseline);
> re-decided only in Mode C or U (`ABSD:STRAT-1`). `test_plan.md` cites this file and never re-argues applicability.
> Every automated suite runs in its lane; a deploy happens only after the push lane passes and is rolled back if the
> live system then fails its smoke test. Every value a gate reads is indexed in §2 with its `file:line` (`ABSD:GATE-7`).

## 1. Applicability (interface profiles: <…>)

One column per declared profile: M = mandatory · R = required when a requirement, rule or named risk triggers it ·
X = not applicable. Trigger ids: for R, the triggering ids or "no trigger (checked: <ids>)"; for X, the reason. N/A
only in X cells or where the row's subject is absent (no persistent state, jobs, flags, secrets …), stated with the
evidence (`ABSD:STRAT-4`); turning an M into N/A needs an ADR that passed Gate 2R. Matrix and rules:
`absd/playbook/testing/strategy.md`. Lane: push · nightly · post-deploy · per cycle · release.

| Type | <profile> M/R/X | <profile …> | Trigger ids | Home | Command | Report | Lane |
|---|---|---|---|---|---|---|---|
| Unit | M | | | `<…>` | `<…>` | `<junit path>` | push |
| Component (`ABSD:STRAT-13`) | | | | | | | push |
| Integration (real boundary) | | | | | | | push |
| Contract — recorded | | | | | | | push |
| Contract — live | | | | | | | nightly |
| Model eval set (`ABSD:FAKE-13`) | | | | | | | push (recorded) + nightly (live eval) |
| Access & visibility matrix | | | | | | | push |
| Chain (boundary input → persisted + shown outcome) | | | | | | | push |
| End-to-end — functional (per device / runtime project) | | | | | | | push |
| End-to-end — acceptance journeys | | | | | | | push |
| End-to-end — foreign time zone / locale project | | | | | | | push |
| Acceptance traceability | M | | | | | | push |
| Device / runtime matrix (phone for web-ui, native-app unless waived) | | | | | | | push; real devices: release |
| Accessibility scan + keyboard | | | | | | | push |
| Visual / golden output + Design QA | | | | | | | push; Design QA per cycle |
| Performance budgets + query count | | | | | | | push (budget) + nightly (full) |
| Load, stress, soak (`ABSD:PERF-4`) | | | | | | | nightly |
| Interface compatibility (`ABSD:COMPAT-1` … `ABSD:COMPAT-3`) | | | | | | | push (snapshot) + nightly |
| Security (beyond access) | | | | | | | push + nightly |
| Migrations: from empty, from previous release, drift; boot shipped artifact on empty infrastructure | | | | | | | push |
| Backup → restore drill | | | | | | | release |
| Post-deploy smoke + rollback | | | | | | | push (CI stack) + every deploy |
| Regression (one test per escaped defect, at the level that should have caught it) | M | | | | | | push + nightly |
| Mutation (changed code; money/time/access rules) | | | | | | | push or Verify + nightly |
| Characterization (`CHAR`, inherited behaviour) | | | | | | | Baseline, then push |
| Exploratory (agent + human) | | | | | | | per cycle / release |

## 2. Gate register (all fail the build; each RED once by its negative control at Foundation, `ABSD:GATE-8`)

Plan gates (test-plan conformance, artifact coverage) run only with an active cycle; without one they print the notice
"no active cycle" — an *Applies when* condition, not a skip (`ABSD:GATE-1`).

| Gate | Tool / command and flags | Threshold | Value at `file:line` | Runs | Owner of the threshold |
|---|---|---|---|---|---|
| Coverage floor (ratchet: only rises) | `absd/tooling/coverage_gate.py --reports <glob per language> --min-total <n>` — every `--reports` glob must match a report holding coverable lines | <n>% | `<file:line>` | push | Tester (lowering needs the user) |
| Per-layer floors | same, `--layer <NAME>=<regex> --min-layer <NAME>=<pct>` for the money, time and access layers | <pct> each | `<file:line>` | push | Tester |
| No unit no test runs | same, `--untested-allowlist <path> --fail-on-stale` | 0 new, 0 stale | `<allowlist path>` | push | Tester |
| Requirement catalogue | `absd/tooling/traceability_report.py --junit <glob> … --catalogue absd-project/catalogue.md --fail-on failing,unknown,untested` — every `--junit` glob must match a file holding test cases | 0 failing, 0 unknown, 0 untested (brownfield: untested only until the adoption baseline is burned down) | `<workflow file:line>` | every push, always | Tester |
| Test-plan conformance | same, `--plan absd-project/working/test_plan.md` (index + parts) | 0 missing, 0 failing (Plan & Bind red run: `--fail-on unknown,unplanned`, missing only in later-WP units) | `<workflow file:line>` | push, only with an active cycle | Tester |
| Artifact coverage | `absd/tooling/trace_check.py gate <gate> --external-facts <path>` per gate in the `cycle.md` ledger | PASS | `<workflow file:line>` | push, only with an active cycle | Tester |
| Ownership + order | `absd/tooling/ownership_check.py --base <default branch> [--t-sha <first> --t-sha <next> …]` | 0 errors | `<workflow file:line>` | push | Tester |
| Access & visibility completeness | <the matrix test> | 0 unruled operations | `<file:line>` | push | Tester |
| Error signals in end-to-end | <the shared fixture> | 0 unexpected | `<file:line>` | push | Tester |
| Mutation score | <tool> | <n>% on changed code; 100% of money/time/access rules | `<file:line>` | push or Verify | Tester |
| Flake policy | runner config | retries 0 (unit/component/integration/contract, setup), ≤ 1 (e2e); pass-on-retry = finding of the cycle owning the test (`ABSD:ESC-11`) | `<file:line>` | push | Tester |
| Accessibility | <scanner> | 0 serious/critical | `<file:line>` | push | Tester |
| Visual | <comparator> | tolerance per §5 | `<file:line>` | push | Tester |
| Performance budgets | <budget tests> | p95 <ms> at max volume; ≤ <n> queries per operation | `<file:line>` | push + nightly | Tester |
| Load, stress, soak (`ABSD:PERF-4`) | <load tool and script> | concurrency <n>, arrival rate <n/s>, duration <min>; p95 / p99 <ms>; error rate 0; soak ≥ 30 min with memory, handles, threads, pools, queue depth flat after warm-up | `<file:line>` | nightly | Tester |
| Interface compatibility (`ABSD:COMPAT-1`) | <contract snapshot diff> | 0 breaking changes without a MAJOR version or ADR | `<file:line>` | push | Tester |
| Model eval (`ABSD:FAKE-13`) | <eval job> | accuracy ≥ <pct> and refusal rate ≤ <pct> per category; k = <n> repeats; per-item pass rate ≥ <pct> | `<file:line>` | nightly + every prompt or model change | Tester |
| Migrations (`ABSD:GATE-12`, when the product owns persistent state) | <migration steps>: from empty, from the previous release with data, model ↔ migration drift | 0 errors, 0 data lost, 0 drift | `<file:line>` | push | Tester |
| Empty-infrastructure boot (`ABSD:OPS-1`) | shipped artifact, production configuration, empty store and volumes | ready on its version within <s>; a missing setting refused by name | `<file:line>` | push + first deploy to a new environment | Tester |
| Deploy condition (`ABSD:GATE-15`, when deploying automatically) | release trigger + its decision-table test | push to <release branch>, run green as a whole at that commit, auto-deploy switch on; queued, never cancelled | `<workflow file:line>` | every deploy; its test: push | Builder (release workflow); its test: Tester |
| Secret canary | <scan> | 0 canaries in logs, reports, artifacts, diffs | `<file:line>` | push | Tester |
| Live contract | <scheduled job> | 0 broken facts; a missing credential is RED | `<file:line>` | nightly | Tester |
| Warnings as errors, lint, format, type check | <…> | 0 | `<file:line>` | push | Builder (per architecture) |

## 3. Running them
```bash
<fast suite>                       # what the Builder runs after every work package (unit + component + integration + recorded contract + access)
<unit>
<integration>
<end-to-end>                       # starts fakes + the real service on a fresh database built by the shipped migrations
<one folder / one test by title>
<show the report: screenshots, steps, traces>
<smoke against a running system>
<live contract check (needs the real credential; missing credential = RED, not a warning)>
```

## 4. Rules of thumb (project-specific additions to the ABSD playbook)
- A bug fix comes with a test that fails without the fix (`ESCAPED-DEFECTS.md`).
- A new operation needs a row in the access & visibility matrix; the build fails until it has one.
- A new requirement goes into `absd-project/catalogue.md` (Analyst) and gets an acceptance test that links it.
- Fakes answer like the real thing (`EXTERNAL-FACTS.md`); tests run with shipped settings.
- <project additions — each harvested lesson that is project-specific lands here or in context.md §14>

## 5. Budgets & policies
| Policy | Value | Rule |
|---|---|---|
| Push-lane wall-time budget | <min> (parallel workers, shards; never by dropping cases) | `ABSD:STRAT-9` |
| Isolation strategy | <fresh store per worker / transaction rollback / namespace per test> | `ABSD:INTEG-4` |
| Serial groups (tests that cannot run in parallel, and why) | <group → tests → reason> | `ABSD:TCQ-9` |
| Override allowlist (test-only settings: endpoints and credentials only) | <key → reason> | `ABSD:FAKE-4` |
| Pixel tolerance per visual project | <px or %> | `ABSD:VIS-2` |
| Volatile fields masked in golden output (timestamps, ids) | <field → mask> | `ABSD:VIS-3` |
