# ABSD playbook

The kit's knowledge base: rules with permanent ids that agents apply and cite, each with the failure it prevents, how it
is checked, where it applies and where it came from. `absd/RULES.md` is the canonical rule set and wins any
disagreement; the agent manuals (`.claude/agents/*.md`) say who does what and when; the playbook says how to do it well
and how to prove it was done. Vendored and read-only in products; changed only through enrichment.

## How agents use the playbook

- Before working, read every playbook file your manual's "Read first" list names. Each opens with a one-screen
  checklist: use it as your self-check, and open the full rule whenever an item applies.
- Cite every rule you apply, enforce or find broken as `ABSD:CODE-n`: in artifacts, the "Rule cited" column of finding
  rows, oracle sources, ADRs and commit messages. Tests cite rules as `ABSD:CODE-n`, never in brackets (TRACE-4).
- *Applies when* sets a rule's scope: interface profiles (web-ui, native-app, http-api, cli, library, data-pipeline, as
  declared in `absd-project/context.md`) and conditions; "always" means every product and profile.
- A manual and a rule that disagree are reported, never settled locally: a worker names it in its reply to the
  Manager; the Manager records a lesson (ENR-1). `absd/RULES.md` applies meanwhile.
- Products never edit the playbook (hash-checked by `absd/tooling/absd_sync.py check`). Project conventions go to
  `absd-project/context.md` §14; improvements go through enrichment (ENR-4).

## Routing table — one home per topic

Find the topic, then its code and file. Every topic has exactly one home; other files link to it. A new topic gets its
row here in the same change that adds its first rule (ENR-6).

| Topic | Code | File |
|---|---|---|
| Test types, applicability matrix per profile, N/A rules | STRAT | `absd/playbook/testing/strategy.md` |
| Lanes (push, nightly, per cycle, release) and what runs in each | STRAT | `absd/playbook/testing/strategy.md` |
| Test case ids and attributes; every REQ-NF as a measurable test case; adoption baseline of existing suites | STRAT | `absd/playbook/testing/strategy.md` |
| Equivalence classes, boundaries, decision tables, pairwise, principal × operation expansion | VAR | `absd/playbook/testing/test-design.md` |
| State-transition coverage (every state × event, invalid ones rejected) | VAR | `absd/playbook/testing/test-design.md` |
| Device and runtime classes as separate targets | VAR | `absd/playbook/testing/test-design.md` |
| Test data at production volume with adversarial ordering | VAR | `absd/playbook/testing/test-design.md` |
| Time instants: midnights per zone, DST, month and season ends, foreign zone run | VAR | `absd/playbook/testing/test-design.md` |
| Absent and invalid inputs, races, re-runs, failure injection, property-based and metamorphic cases | VAR | `absd/playbook/testing/test-design.md` |
| Idle-screen network budget; flags and settings in both states; assert at the source of truth | VAR | `absd/playbook/testing/test-design.md` |
| Oracle sources, independent calculation, worked numbers, source precedence | ORACLE | `absd/playbook/testing/oracles.md` |
| Red before green, oracle amendments, dispute protocol, failure classification | ORACLE | `absd/playbook/testing/oracles.md` |
| Characterization (CHAR) tests of inherited behaviour; oracle strength | ORACLE | `absd/playbook/testing/oracles.md` |
| Access & Visibility Matrix, build-time completeness, entitlement states | ACCESS | `absd/playbook/testing/access-visibility.md` |
| Visible records and fields, object-level access, impersonation, service identities, UI reflecting the matrix | ACCESS | `absd/playbook/testing/access-visibility.md` |
| Real-boundary harness; test stores only via shipped migrations; isolation | INTEG | `absd/playbook/testing/integration.md` |
| Test clock and seams in tests; arranging data through public operations; exact outcome assertions | INTEG | `absd/playbook/testing/integration.md` |
| Chain tests from recorded payloads; data-flow step tests; audit-entry assertions | INTEG | `absd/playbook/testing/integration.md` |
| Background jobs, exactly-once races and notifications at the real boundary; HTTP status semantics | INTEG | `absd/playbook/testing/integration.md` |
| Fake fidelity, recorded responses, contract tests, live contract checks, fake control channels | FAKE | `absd/playbook/testing/contracts-and-fakes.md` |
| Configuration agreement, shipped settings only, start-up validation of plausible-but-harmful settings | FAKE | `absd/playbook/testing/contracts-and-fakes.md` |
| External call failure classes, request assertions, parser fuzzing | FAKE | `absd/playbook/testing/contracts-and-fakes.md` |
| External facts: evidence, UNVERIFIED → flag off and fail closed, platforms as external systems, replacement sweep | EXT | `absd/playbook/testing/contracts-and-fakes.md` |
| End-to-end per profile: browser, native app, HTTP black box, CLI subprocess, installed library, pipeline run | E2E | `absd/playbook/testing/end-to-end.md` |
| Error-signal fixture, user-like selectors, device and zone/locale projects, real-time lifecycles, seeding | E2E | `absd/playbook/testing/end-to-end.md` |
| Post-deploy smoke suite design; user-visible regression tests | E2E | `absd/playbook/testing/end-to-end.md` |
| Requirement catalogue, test linking, verified/failing/untested report, plan conformance | TRACE | `absd/playbook/testing/traceability.md` |
| Trace tables in artifacts; retired requirements; reserved prefixes in tests | TRACE | `absd/playbook/testing/traceability.md` |
| A check that did not run is RED; coverage floor ratchet; no-untested-unit gate and allowlist | GATE | `absd/playbook/testing/gates.md` |
| Strict compilation, mutation and flake gates; gate configuration ownership; gates proven able to fail | GATE | `absd/playbook/testing/gates.md` |
| CI job graph, readable failures, hermetic CI; migration, secret-canary, pipeline-integrity and deploy gates | GATE | `absd/playbook/testing/gates.md` |
| Escaped defects: main rule, why-missed taxonomy, root-cause class, same-weakness sweep, log, recurrence, flakes | ESC | `absd/playbook/testing/escaped-defects.md` |
| Exploratory charters and sessions (agent and human), finding routing, manual acceptance checklist, real devices | EXPL | `absd/playbook/testing/exploratory.md` |
| Accessibility scans, keyboard paths, rendered contrast, CLI output without colour | A11Y | `absd/playbook/testing/nonfunctional.md` |
| Performance budgets, round trips per operation (N+1), payload budgets | PERF | `absd/playbook/testing/nonfunctional.md` |
| Timeouts and retries, partial failure, degradation and fail-closed behaviour | RESIL | `absd/playbook/testing/nonfunctional.md` |
| Screenshot gallery, visual regression, golden outputs | VIS | `absd/playbook/testing/nonfunctional.md` |
| Boot on empty infrastructure, build once, deploy verification and rollback, deploy-script tests, backup and restore, fresh clone from the docs, log levels, alerting | OPS | `absd/playbook/testing/nonfunctional.md` |
| Test code: naming with ids, shape, builders, determinism, waiting, isolation, parallel safety, never weakening a test | TCQ | `absd/playbook/testing/test-code.md` |
| Design deliverables per profile, visual language, minimal effort, component–state matrix, motion | DSN | `absd/playbook/design/excellence.md` |
| Journeys, device classes, no hover-only affordance, touch and scroll behaviour, long lists and default selection | DSN | `absd/playbook/design/excellence.md` |
| User state surviving refresh, error message design per failure mode, accessible names, contrast and target sizes | DSN | `absd/playbook/design/excellence.md` |
| CLI and machine-surface design, design rubric, Design QA, protected baselines | DSN | `absd/playbook/design/excellence.md` |
| Label maps (never raw enums), one formatter per kind, machine-output formats | LOC | `absd/playbook/design/content-and-locale.md` |
| Clock style, display zones, label truthfulness, date buckets, number style, truncation | LOC | `absd/playbook/design/content-and-locale.md` |
| Copy deck, tone, empty states, action and error wording, localisation readiness, format lint | LOC | `absd/playbook/design/content-and-locale.md` |
| Dependency direction, configuration type placement, pure core rules, SOLID, patterns, YAGNI vs correctness | ARCH | `absd/playbook/engineering/architecture.md` |
| Gate decisions honoured, blueprint standard, non-mutating reads, numbered data flows | ARCH | `absd/playbook/engineering/architecture.md` |
| Seams and test architecture, error catalogue, configuration keys, schema and migrations design | ARCH | `absd/playbook/engineering/architecture.md` |
| Concurrency register, background job specification, flag register, external ports | ARCH | `absd/playbook/engineering/architecture.md` |
| Security design and observability in the blueprint, ADRs, suppression-marker list, work packages, profile modules | ARCH | `absd/playbook/engineering/architecture.md` |
| Architecture review checklist (Gate 2R) | ARCH | `absd/playbook/engineering/architecture.md` |
| Static analysis, warnings as errors, formatting, complexity, naming, dead code, dependency hygiene, suppression markers in code | CODE | `absd/playbook/engineering/code-quality.md` |
| Authentication, authorization (deny by default, object level), input validation, secret handling, headers, logging hygiene, dependency scanning, threat model | SEC | `absd/playbook/security/baseline.md` |
| Personal data inventory, retention, deletion and export, consent, personal data in logs | PRIV | `absd/playbook/security/baseline.md` |
| Elicitation lenses: actor × capability, visibility, role value, inherited behaviour, CRUD, states, time, money, external facts, devices, volume, privacy, operability, notifications, audit trail, concurrency | ELIC | `absd/playbook/process/requirements.md` |
| Specification by example, assumptions and contradictions, catalogue delta, Gate 1 sign-off, Mode S intake questions | ELIC | `absd/playbook/process/requirements.md` |
| Definition of done: feature cycle, work package, defect, Foundation, brownfield ratchet, release readiness, upgrade, park | DOD | `absd/playbook/process/definition-of-done.md` |
| Audit scope and independence, evidence rule, levels L1–L8, test changes since T-SHA, adversarial probes | XCA | `absd/playbook/process/audits.md` |
| Severity calibration, finding acceptance and expiry, re-audit and iteration history | XCA | `absd/playbook/process/audits.md` |
| Architecture review procedure (Gate 2R), Mode S eligibility audit, cross-cycle audit and its lenses | XCA | `absd/playbook/process/audits.md` |
| Harvest, lessons ledger, proposals, local kit edits (product side) | ENR | `absd/playbook/process/enrichment.md` |
| Kit change procedure: inbox, dedupe, generalize, decide, LEDGER, rule text, CHANGELOG, semver, checks, kit acceptance, provenance | ENR | `absd/playbook/process/enrichment.md` |

Severity scale and finding schema: `absd/RULES.md` §6 (calibration: XCA). Routes, gates and modes: `absd/RULES.md` §2.

## Rule format

Each file: `# Title`; a scope paragraph naming its code(s); `## Checklist` (one screen, each item ending with its rule
ids in parentheses); `## Rules` (optional `### topic` subsections, tables after a rule's bullets); then optional
reference sections. At most 5k tokens (about 20 000 characters) per file (`absd/RULES.md` §9): split by topic when it
grows — ids move with their rules.

```markdown
**CODE-n** — <imperative, checkable sentence>.
- *Why:* <the failure it prevents, citing the lesson: LL-n>
- *Check:* <how a reviewer, test, tool or CI step verifies it>
- *Applies when:* <profiles and conditions, or "always">
- *Provenance:* LL-n[, LL-m] (<project slug>, YYYY-MM)        or:  - *Provenance:* industry baseline
```

Stack, vendor and tool names appear only in labelled illustrations naming at least two alternatives (e.g. pytest
`parametrize`, JUnit `@ParameterizedTest`), in fenced code, or behind an LL id; never as an assumption.

## Ids, numbering and tombstones

- A code is a permanent topic namespace, not a file name: one file may host several codes; when a file splits, its
  rules keep their ids and only the routing table changes.
- Rule ids are `CODE-n`, unpadded, numbered from 1 within each code; next = highest + 1; never reused, never
  renumbered.
- Pinned ids — the ones `absd/RULES.md` cites in its quality laws — keep their meaning; changing one is a MAJOR
  version (ENR-12).
- Retire, never delete. A tombstone keeps the id and its four bullets, and no new text may cite it:

```markdown
**CODE-n** — Retired in x.y.z: superseded by CODE-m (or: no successor — <reason>).
- *Why:* <unchanged> · *Check:* <unchanged>
- *Applies when:* never — retired
- *Provenance:* <unchanged, plus the LL that retired it>
```

- Products and artifacts cite `ABSD:CODE-n`; product and cycle ids follow `absd/RULES.md` §7.

Reserved codes: `STRAT` `VAR` `ORACLE` `ACCESS` `INTEG` `FAKE` `EXT` `E2E` `TRACE` `GATE` `ESC` `EXPL` `A11Y` `PERF` `RESIL` `VIS` `OPS` `TCQ` `DSN` `LOC` `ARCH` `CODE` `SEC` `PRIV` `ELIC` `DOD` `XCA` `ENR` `TC` `DEF` `CR` `ADR` `UJ` `SCR` `DEBT` `RISK` `LL` `AR` `TF` `DQ` `F` `CLR` `WP` `INH` `TSEAM` `CHAR` `C` `A` `OQ` `D` `UXQ` `UXA`

`QC` is the one fixed area code every product shares: the Foundation quality capabilities (`QC-n` catalogue rows,
Area "Quality"). No product area code (`absd-project/context.md` §1) may be a reserved code: the Analyst checks at Gate 1 (ELIC-20), and
the tools read these prefixes as references, never as requirement links (TRACE-4).

## Provenance

- Every rule ends with one Provenance line: the LEDGER lessons (`absd/lessons/LEDGER.md`) that produced or changed
  it, or `industry baseline` — widely accepted practice adopted before any project hit the failure. A later lesson
  adds its LL id to the line; a contradicting one adds a condition, never a silent override (ENR-8).
- Project specifics (stack, vendors, domain, people, data) live only in the LEDGER behind LL ids; projects appear by
  slug, pseudonymous for client products (ENR-15).
- The LEDGER scoreboard counts escapes and findings per project and kit version by the gate that should have caught
  them; it is how the kit proves it improves (ENR-9).

## Changing the playbook

Products: harvest lessons into `absd-project/lessons.md` and send universal ones as proposals (ENR-1 to ENR-4). The ABSD
repository: apply `absd/playbook/process/enrichment.md` "ABSD side" (ENR-5 to ENR-16) as the maintainer guide
(`CLAUDE.md`) describes — inbox, dedupe against this routing table, generalize, LEDGER, rule, CHANGELOG, version,
manifest, `kit_lint` and tooling tests green, kit acceptance run before every MINOR or MAJOR tag.
