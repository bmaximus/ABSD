# Code Quality

Code **CODE**. The rules production code meets before a work package is done (DOD-3): compiler strictness, formatter
and linter with a banned-API list, size and complexity limits, domain naming, no dead code, tracked TODOs, named
constants, error handling, async and cancellation, resource release, immutability, dependency hygiene, suppression
markers and commit hygiene — plus the Auditor's L4 review checklist. The Architect fixes tools, rule sets and
thresholds in `architecture.md` "Quality gates & CI" and lists every suppression marker (ARCH-23); the Builder writes
code that passes them and halts rather than bypass one; GATE-4 runs them on every push; the Auditor judges them at L4
(XCA-3). Test code: TCQ (`absd/playbook/testing/test-code.md`); security: SEC, PRIV (`absd/playbook/security/baseline.md`).

## Checklist

- [ ] Strictest compile/type mode set once at repository level; warnings, nullability and deprecation are errors (CODE-1)
- [ ] One formatter in check mode and one linter with a committed rule set at 0 findings, banned APIs included (CODE-2)
- [ ] Functions, files, parameters, nesting, complexity and duplication within the limits table (CODE-3)
- [ ] Names in the catalogue's domain language; units and intent in names; comments say why (CODE-4)
- [ ] No unreachable, unused or commented-out code; no dead configuration; no flag past removal (CODE-5)
- [ ] Every TODO/FIXME carries an open DEBT or RISK id; none stands in for a required control (CODE-6)
- [ ] Every literal with business or world meaning is a named constant or setting citing its id (CODE-7)
- [ ] No swallowed error, empty or broad catch, silent default or fallback; log once at the boundary (CODE-8)
- [ ] I/O asynchronous; cancellation and deadlines passed end to end; no blocking or fire-and-forget (CODE-9)
- [ ] Every resource released on every path; long-lived clients reused; no captive request state (CODE-10)
- [ ] Values, messages and configuration immutable; mutation only inside invariant-enforcing methods (CODE-11)
- [ ] Dependencies listed in architecture, pinned, lockfile committed, licence allowed, none unused, scanned (CODE-12)
- [ ] Suppression markers only as listed in `architecture.md`, with rule and reason inline (CODE-13)
- [ ] One work package per commit; ABSD trailers in the single final paragraph (CODE-14)

## Rules

### Static checks

**CODE-1** — Compile or type-check every production language in its strictest practical mode, configured once at repository level so every new project inherits it: warnings are errors; null-safety on (non-nullable by default, every nullable declared and handled); no implicit dynamic or `any`, unchecked casts or unchecked index access; matches over closed sets (enums, unions, sealed types) exhaustive; use of deprecated or obsolete APIs is an error; the analyser level is the newest the toolchain offers.
- *Why:* warnings pile up and hide null dereferences and ignored results; an obsolete persistence API specified in a blueprint compiled only because deprecation was not an error; a per-project setting lets a new project opt out silently.
- *Check:* GATE-4 static job at 0; grep finds the flags in the repository-level file only, never overridden per project; a planted unused variable and a planted null dereference each turn the job RED (GATE-8).
- *Applies when:* always — scripts and build files included (GATE-4).
- *Provenance:* industry baseline
- Illustration: e.g. C# `Nullable` + `TreatWarningsAsErrors` + `AnalysisLevel=latest-all`, TypeScript `strict` + `noUncheckedIndexedAccess`, Python `mypy --strict`, Kotlin `allWarningsAsErrors`, Go `go vet` + staticcheck, Rust `-D warnings` + clippy.

**CODE-2** — Enforce one formatter in check mode and one linter with a committed rule set at zero findings, including a banned-API list with the replacement for each entry: wall clock, randomness, environment, network, file and store access outside their adapters (ARCH-11); string-built queries, shell strings and raw-markup sinks (SEC-7); weak hashes and ciphers; dynamic code evaluation; deserialisation of input into arbitrary types; console printing in service and library code.
- *Why:* formatting drift buries real changes in diffs; banned calls are where seams leak — a wall-clock read in an entity default gives mixed timestamps under a moved test clock — and where injection enters.
- *Check:* the formatter rewrites nothing and the linter reports 0 in the push lane and in a pre-commit hook; a planted wall-clock call outside the clock adapter turns the job RED (GATE-8); the Auditor reads the banned list against SEC-7.
- *Applies when:* always.
- *Provenance:* industry baseline
- Illustration: e.g. Prettier + ESLint `no-restricted-imports`, Ruff format + Ruff banned-api, C# BannedApiAnalyzers, gofmt + golangci-lint `forbidigo`.

**CODE-3** — Keep every production function and module within the limits below as the linter measures them; an exception exists only as a listed suppression (CODE-13) on that one symbol naming metric, value and reason; generated code is excluded by path in the linter configuration, never per symbol; money, time and access rules get no exception.
- *Why:* long, branching functions are where boundary cases hide untested — each branch is a row the test plan must enumerate — and duplicated rule logic drifts: one copy is fixed, the other is not.
- *Check:* linter thresholds equal the table or are stricter; raising one is a loosening (GATE-6); the Auditor lists every exception and diffs it with `architecture.md`. Valid reasons: a declarative table (state transitions, lookups) or an exhaustive match with one statement per arm.
- *Applies when:* always.
- *Provenance:* industry baseline

| Metric | Limit |
|---|---|
| Function or method body | ≤ 40 lines of code |
| Cyclomatic complexity | ≤ 10 per function; cognitive complexity ≤ 15 where measured |
| Parameters | ≤ 4; beyond that a parameter object or value type |
| Nesting depth | ≤ 3 blocks |
| File or module | ≤ 400 lines of code; one public type per file where the language has types |
| Boolean operators in one condition | ≤ 3; otherwise extract a named predicate |
| Duplicated block | none ≥ 10 lines or 50 tokens in production code |

### Naming and content

**CODE-4** — Name every type, function, variable, table, column, file and log field in the domain language of `catalogue.md` and `analysis.md` — one term per concept in code, schema, interface, logs and copy keys; names carry intent and the unit when the type does not (`timeoutSeconds`, `amountCents`); booleans read as predicates (`isLocked`); no abbreviation outside the glossary; physical names follow the one convention per store and interface that `context.md` Conventions declares; comments say why, never what.
- *Why:* a schema filter written in one naming convention failed on a store that used another; synonyms for one concept split one rule across two code paths.
- *Check:* naming lint rules; the Auditor samples ≥ 10 new symbols against catalogue terms and every raw query and migration against the declared convention.
- *Applies when:* always; library: public names follow the API naming guide in `design-system.md` (DSN-18).
- *Provenance:* industry baseline

**CODE-5** — Ship no dead code: no unreachable branch, unused symbol, parameter, import or setting, no commented-out code, no configuration or policy registered but never applied, no flag branch past its removal condition (ARCH-18); history lives in version control, not in comments.
- *Why:* dead code is untested by definition, hides from the untested-unit gate inside tested files (GATE-2) and misleads the next reader; dead configuration looks like a control that is not there.
- *Check:* unused and unreachable lint rules at 0; a commented-code detector; the Auditor greps for blocks of commented statements and for registrations nothing consumes.
- *Applies when:* always.
- *Provenance:* industry baseline

**CODE-6** — Allow `TODO`, `FIXME`, `HACK` or `XXX` in production paths only as `TODO(DEBT-n)` or `TODO(RISK-n)` whose row is open in `context.md`; never for a rule, check, migration, test seam or security control the cycle must deliver — that is a halt to `clarification_needed.md`.
- *Why:* a "verify before trusting in production" caveat lived only as a note, died when the cycle was archived, and the unverified default shipped enabled (LL-1).
- *Check:* a push-lane grep fails on a marker without an id or with an id that is closed or absent in `context.md`; the Auditor confirms each marker is removed in the change that closes its row.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

**CODE-7** — Name every literal with business or world meaning — limits, thresholds, percentages, durations, sizes, retry counts, zone ids, currencies, codes, status strings — as a constant or configuration key (ARCH-14) whose declaration cites the requirement, BR or EXT id it implements; only 0, 1, −1, empty and identity values stay inline; units travel in types or names.
- *Why:* a guessed time-zone literal stood in for an unverified provider fact and moved every deadline by 8 hours; nothing marked it as a guess (LL-1).
- *Check:* magic-number lint rule with the allowed set above; the Auditor samples constants for a cited id; every world-fact constant cites a VERIFIED EXT id (EXT-2).
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

### Behaviour

**CODE-8** — Never swallow an error: catch only the specific failure handled at that point; no empty catch and no catch-all except the one boundary handler that maps per the error catalogue and logs (ARCH-13); never turn a failure into a default value, empty result or warning and carry on — refuse per the catalogue; map a store failure by its constraint name or error code, never "any store error"; rethrow with the original as cause plus context; log each failure once, at the boundary.
- *Why:* "missing numbers fail validation" became "missing values become 0" in code and passed every gate (LL-44); an unknown provider zone fell back to UTC with a logged warning and every deadline was 8 hours late (LL-1).
- *Check:* empty- and broad-catch lint rules at 0; the Auditor greps catch blocks on money, time, access and parsing paths and fails any that default, continue or map broadly; VAR-11 rows prove each refusal.
- *Applies when:* always; data-pipeline: a bad record goes to dead letter with a reason code, never dropped or zeroed.
- *Provenance:* LL-44, LL-1 (KatenatsioTipster, 2026-10)

**CODE-9** — Make every I/O call asynchronous where the runtime supports it and pass the caller's cancellation or deadline from the entry point (request, command, message, job tick) through every layer to every store, network and file call; never block on asynchronous work, never substitute an empty token where the caller's exists, never start unsupervised work (fire-and-forget) — hand it to a job (ARCH-17) or an awaited task with error handling.
- *Why:* a dropped cancellation keeps work, locks and connections alive after the client left or shutdown began; blocking on async work starves pools under load; errors of unsupervised work vanish.
- *Check:* async and cancellation analysers at error level; the Auditor greps for blocking waits and empty tokens; timeout TCs (RESIL-1) and a crash- or cancel-mid-cycle TC per job (INTEG-14).
- *Applies when:* any I/O; library: every public I/O operation accepts a cancellation or deadline.
- *Provenance:* industry baseline

**CODE-10** — Release every resource on every path with the language's scoped construct (e.g. `using`, `with`, try-with-resources, `defer`) — connections, transactions, streams, files, locks, subscriptions, timers; create long-lived clients (HTTP, store pools) once per process through their factory, never per call; no object outlives a resource or request-scoped state it captured.
- *Why:* leaked connections and sockets fail only under load or after hours; a singleton holding request-scoped state serves stale or another principal's data.
- *Check:* resource-leak analysers at 0; the Auditor reviews the lifetime table in `architecture.md` dependency wiring for captive dependencies; repeated-run or soak TCs where PERF budgets exist.
- *Applies when:* always.
- *Provenance:* industry baseline

**CODE-11** — Make data immutable by default: value objects, DTOs, messages, events and configuration are read-only after construction; collections leave their owner read-only; state changes only inside the aggregate method that enforces its invariant; no mutable static or global state.
- *Why:* shared mutable state makes ordering and concurrency hidden inputs; an invariant enforced in one method is bypassed by a setter elsewhere.
- *Check:* analyser rules for public setters, mutable statics and exposed mutable collections; the Auditor samples domain and message types.
- *Applies when:* always.
- *Provenance:* industry baseline

### Dependencies, markers, commits

**CODE-12** — Admit a production dependency only when `architecture.md` lists it (ADR-001 stack or a component spec) with purpose and licence: pinned to an exact version, resolved through a committed lockfile that CI installs from in locked mode, licence on the product's allow-list, removed when unused, scanned per SEC-13; an import `architecture.md` does not list is a Builder halt.
- *Why:* floating versions make one commit build differently on two days; unused and unvetted packages widen the attack surface and the licence exposure.
- *Check:* lock-only installs fail on drift (e.g. `npm ci`, `dotnet restore --locked-mode`, `pip install --require-hashes`, `cargo build --locked`); licence and unused-dependency checks in the push lane at 0; the Auditor diffs the manifests with `architecture.md`.
- *Applies when:* always; library: declared ranges for consumers per its semver policy, the lockfile for its own CI.
- *Provenance:* industry baseline

**CODE-13** — Carry a suppression marker (patterns below) only where `architecture.md` lists it — file, symbol, rule, reason, expiry (ARCH-23) — with the rule id and reason written inline; never on money, time or access paths, never to pass a gate the cycle must meet; the Builder halts instead of adding one.
- *Why:* one coverage-exclusion attribute or lint disable removes a unit from a gate without touching a test — the code author relaxes the check that judges the code.
- *Check:* the Auditor greps production paths with the patterns and diffs the hits with the list; unlisted is Major, Critical on money, time or access (XCA-7); an expired marker fails.
- *Applies when:* always.
- *Provenance:* industry baseline

**CODE-14** — Commit one work package per commit: subject `absd(C###): <stage> — <agent>`, a blank line, a body naming the WP and its TCs, and the trailers as the single final paragraph — `ABSD-Agent:`, `ABSD-Cycle:` and any co-author or session lines together with no blank line between them, because git reads trailers only from the last paragraph; no unrelated change, generated output or formatting churn; the tree builds and its fast suite runs at every commit.
- *Why:* interrupted builders left half-finished work that others completed; per-WP commits make resume, atomic halt and ownership checks mechanical (LL-26); a trailer separated by a blank line is invisible to the ownership check.
- *Check:* `git interpret-trailers --parse` shows both ABSD trailers on every cycle commit; ownership_check (GATE-14) fails a commit without them; the Auditor builds a sampled commit in isolation.
- *Applies when:* every commit on a cycle branch.
- *Provenance:* LL-26 (KatenatsioTipster, 2026-10)

## Suppression marker patterns (Auditor grep; extend per stack in `architecture.md`)

```text
git grep -nE "<pattern>" -- <production globs from context.md Source Layout>
pragma warning disable|SuppressMessage|ExcludeFromCodeCoverage|NOSONAR
eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|istanbul ignore|c8 ignore|v8 ignore
# noqa|# type: ignore|# pragma: no cover|# pylint: disable|# nosec
@SuppressWarnings|//nolint|#\[allow\(|rubocop:disable|coverage:ignore
```

## L4 review checklist (Auditor)

Run at the cycle HEAD in a clean checkout (XCA-2); record each miss as an F-n citing `ABSD:CODE-n`.

| Item | Evidence attached to `audit.md` | Severity if failing |
|---|---|---|
| Static job | GATE-4 output: 0 warnings, 0 lint or format findings (CODE-1, CODE-2) | Major |
| Strictness | flags in the repository-level file only; no per-project override (CODE-1) | Major |
| Banned APIs | linter list + grep for clock, random and I/O outside adapters (CODE-2) | Major; Critical on money or time |
| Limits | linter report; every exception a listed marker (CODE-3) | Minor; Major on money, time or access |
| Naming | 10 sampled symbols vs catalogue terms; physical names vs convention (CODE-4) | Minor |
| Dead code, TODOs | lint output; grep for commented code and id-less markers (CODE-5, CODE-6) | Minor; Major when a TODO replaces a required control |
| Constants | sampled constants cite ids; world facts cite VERIFIED EXT (CODE-7) | Major for world facts, else Minor |
| Error handling | catch-block grep on money, time, access and parsing paths (CODE-8) | Critical on money or access, else Major |
| Async, resources, immutability | analyser output; blocking waits; lifetimes; sampled types (CODE-9, CODE-10, CODE-11) | Major |
| Dependencies | manifests vs `architecture.md`; lockfile; licence, unused and scan output (CODE-12, SEC-13) | Major; Critical for a known exploitable vulnerability |
| Suppression markers | grep hits = `architecture.md` list (CODE-13, ARCH-23) | Major; Critical on money, time or access |
| Commits | trailers parse; one WP per commit; each builds (CODE-14) | Major |
| Blueprint fidelity | code = `architecture.md` signatures and steps; no improvisation in `build_log.md` (DOD-3) | Major |
