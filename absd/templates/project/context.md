# Project Context

> Living product memory — owned by the Manager, read by every agent, NEVER archived. Current state only (≤ 25 KB);
> history lives in `absd-project/archive/`. Machine-read sections (Source Layout & Ownership, Execution Environment)
> keep their table headers exactly as below. Fill every `<…>`; write "none" rather than leaving a section empty.

## 1. Product frame
- Product: <name — one-line purpose>
- Repository: <owner/repo> · default branch: <main> · merge policy: <"ask the user at every Gate 3" | "standing authorization for …">
- ABSD version: <x.y.z> (see `absd/VERSION`) · active cycle: <C### slug | none>
- Interface profiles: <web-ui | native-app | http-api | cli | library | data-pipeline — one or more>
- Audiences and devices: <who uses it, on what: e.g. members on phones (portrait), admins on desktop> · phone tests waived: <no | yes — user's decision, date>
- Principals: <every role and identity: anonymous, each role, admin-as-member, service identities, jobs>
- Entitlement states: <e.g. active, expired, suspended, impersonated — or none>
- Requirement area codes: <AREA = meaning; must not collide with the reserved codes in `absd/playbook/README.md`>

## 2. Technology stack (ADR-001)
- Language / runtime: <…>
- Frameworks: <…>
- Data stores: <…>
- Interfaces: <UI framework / CLI framework / API style / pipeline engine>
- Test stack per profile (ADR-003): <unit, integration, contract, e2e, a11y, mutation, coverage format (Cobertura/LCOV), report format (JUnit XML)>
- Key libraries: <…>

## 3. Source Layout & Ownership (ADR-002)
First matching row wins. Owners: builder, tester, manager, analyst, designer, architect, auditor, shared.

| Path | Owner | Purpose |
|---|---|---|
| `<src/**>` | builder | production source |
| `<migrations/**>` | builder | schema migrations |
| `<.github/workflows/build.yml>` | builder | build, package, deploy |
| `<tests/**>` | tester | all tests, fakes, fixtures, seeds, recordings |
| `<.github/workflows/tests.yml>` | tester | test, gate and nightly jobs |
| `<test runner / coverage / mutation configs>` | tester | thresholds, retries, reporters |
| `docs/testing/**` | tester | TESTING, ESCAPED-DEFECTS, EXPLORATORY, EXTERNAL-FACTS |
| `<README.md, docs/**>` | shared | product docs |

## 4. Execution Environment
| Suite / gate | Command | Runs locally here? | CI job |
|---|---|---|---|
| build | `<…>` | <yes/no — why> | <job> |
| unit | `<…>` | | |
| integration | `<…>` | | |
| contract (recorded) | `<…>` | | |
| contract (live, nightly) | `<…>` | | |
| access & visibility | `<…>` | | |
| end-to-end (per profile/device) | `<…>` | | |
| coverage gate | `python3 absd/tooling/coverage_gate.py …` | | |
| traceability | `python3 absd/tooling/traceability_report.py …` | | |
| mutation | `<…>` | | |
| lint / format / type check | `<…>` | | |

A suite that cannot run here is proven only by a CI run at the exact commit (`ABSD:GATE-1`). Environment limitations
go to the Risk register, never into the architecture.

## 5. Locale & Time Profile
- Display time zone(s): <…> · server zone: <UTC> · provider zones: <EXT ids>
- Clock: <24h | 12h> · date format: <…> · number / currency format: <…> · languages: <…>
- Calendar boundaries that matter: <day, week, month, season, fiscal year…>

## 6. Data Volume Profile (product-wide)
| Collection | Typical | Max observed | Real ordering | Source |
|---|---|---|---|---|

## 7. External systems (facts live in `docs/testing/EXTERNAL-FACTS.md`)
| System | Purpose | Interface | Facts (EXT ids) | Unverified facts → feature flag |
|---|---|---|---|---|

## 8. Feature flag register
| Flag | Default per environment | Hot or restart | Owner | Removal condition | Tests (both states) |
|---|---|---|---|---|---|

## 9. Interfaces (current)
- Operations / endpoints / commands / public symbols: <table or link to the generated list — each with its access rule>
- Data stores and key tables/collections: <…>
- Screens (SCR ids) and journeys (UJ ids): <…>
- Product invariants: the business rules `AREA-BR-n` in `absd-project/catalogue.md` hold across every cycle (e.g.
  "derived amounts are always recomputed server-side, never client-supplied"); the Analyst flags any contradiction,
  the Tester keeps an invariant test for each.

## 10. Architecture decisions (index)
| ADR | Title | Cycle | Status |
|---|---|---|---|

## 11. Risk & Assumption register
| RISK | Statement | Source (A/OQ/EXT/env) | Blocks (release / flag:<name> / none) | Owner | Status |
|---|---|---|---|---|---|

## 12. Technical debt
| DEBT | Item | Origin | Burn-down plan |
|---|---|---|---|

## 13. Accepted findings (expire at the next Mode X or R)
| Finding | Severity | Accepted by user on | Reason | Re-raise at |
|---|---|---|---|---|

## 14. Conventions (the single home for project conventions)
- <naming, error model, API style, commit style, copy tone, UI language…>

## 15. Completed cycles
| Cycle | Date | Mode | Module | Gate 3 | Archive |
|---|---|---|---|---|---|
