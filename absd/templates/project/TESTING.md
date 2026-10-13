# Testing — what runs, where, and when

> Living, owned by the Tester, NEVER archived. Decided at Bootstrap (Foundation cycle), re-decided only in Mode C or U
> (`ABSD:STRAT-*`). `test_plan.md` cites this file and never re-argues applicability. Every automated suite runs on
> every push; a deploy happens only after they pass and is rolled back if the live system then fails its smoke test.

## 1. Applicability (interface profiles: <…>)

M = mandatory · R = required when a requirement, rule or named risk triggers it · X = not applicable. Only X cells may
be N/A; turning an M into N/A needs an ADR that passed Gate 2R. Matrix and rules: `absd/playbook/testing/strategy.md`.

| Test type | Applies | Reason (for R/X) | Home (path) | Runs when |
|---|---|---|---|---|
| Unit | M | | `<…>` | every push |
| Integration (real boundary) | | | | every push |
| Contract — recorded | | | | every push |
| Contract — live | | | | nightly |
| Access & visibility matrix | | | | every push |
| Chain (boundary input → persisted + shown outcome) | | | | every push |
| End-to-end — functional | | | | every push |
| End-to-end — acceptance journeys (incl. phone / device classes) | | | | every push |
| End-to-end — foreign time zone / locale project | | | | every push |
| Smoke (also after every deploy, with automatic rollback) | | | | push + deploy |
| Regression (one test per escaped defect, at the level that should have caught it) | M | | | every push + nightly |
| Accessibility scan + keyboard | | | | every push |
| Visual / golden output | | | | every push |
| Performance budgets + query count | | | | <…> |
| Security (beyond access) | | | | <…> |
| Migrations: from empty, from previous release, drift; boot shipped artifact on empty infrastructure | | | | every push |
| Backup → restore drill | | | | <…> |
| Mutation (changed code; money/time/access rules) | | | | <…> |
| Exploratory (agent + human) | | | | per cycle / before release |

## 2. Gates (all fail the build)
| Gate | Tool / command | Threshold | Owner of the threshold |
|---|---|---|---|
| Coverage floor (ratchet: only rises) | `absd/tooling/coverage_gate.py` | <n>% | Tester (lowering needs the user) |
| No unit no test runs | same, `--untested-allowlist <path>` | 0 new | Tester |
| Requirement catalogue | `absd/tooling/traceability_report.py --catalogue …` | 0 failing, 0 unknown | Tester |
| Test-plan conformance | same, `--plan absd-project/working/test_plan.md` | 0 missing, 0 failing | Tester |
| Access & visibility completeness | <the matrix test> | 0 unruled operations | Tester |
| Error signals in end-to-end | <the shared fixture> | 0 unexpected | Tester |
| Mutation score | <tool> | <n>% on changed code; 100% of money/time/access rules | Tester |
| Flake policy | runner config | retries 0 (unit/integration/contract), ≤ 1 (e2e); pass-on-retry = finding | Tester |
| Warnings as errors, lint, format, type check | <…> | 0 | Builder (per architecture) |

## 3. Running them
```bash
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
