# Architecture Excellence

Code **ARCH**. What `architecture.md` must specify and how its quality is judged: dependency direction, SOLID and
patterns, YAGNI vs correctness, gate decisions, the blueprint standard, seams and test architecture, error catalogue,
configuration, persistence, concurrency, jobs, flags, external adapters, security, observability, data flows, ADRs,
work packages and profile modules. The Architect applies it; Gate 2 checks presence; the Auditor judges quality at Gate
2R with the closing checklist and re-checks at audit L1 and L7. Code-level rules: CODE
(`absd/playbook/engineering/code-quality.md`); security: SEC, PRIV (`absd/playbook/security/baseline.md`); test-side
counterparts: INTEG, FAKE, EXT, ACCESS, VAR in `absd/playbook/testing/`.

## Checklist

- [ ] Layer table; dependencies point inward; rules bound as an architecture test (ARCH-1)
- [ ] Every config type reachable from each consuming layer without a cycle (ARCH-2)
- [ ] Money/eligibility/ranking/state rules in a pure core; derived values server-side, one function (ARCH-3)
- [ ] SOLID questions answered per component; every pattern cites its force (ARCH-4, ARCH-5)
- [ ] YAGNI for features only; no rule, invariant or safety mechanism deferred (ARCH-6)
- [ ] "Gate decisions honoured" lists every D-n and invariant; nothing contradicts one (ARCH-7)
- [ ] Blueprint standard: no vague phrase; `path:line` verified; self-verification both ways (ARCH-8)
- [ ] Every consumer data need has a non-mutating read; reads write nothing (ARCH-9)
- [ ] Every data flow in numbered, testable steps incl. deletions (ARCH-10)
- [ ] Seam register: clock, ids, randomness, external ports, flags, config (ARCH-11)
- [ ] Testability & Test Architecture: harness, migrations-only stores, overrides register (ARCH-12)
- [ ] Error catalogue with message key and log level; no 5xx business outcome (ARCH-13)
- [ ] Every config key typed, validated, fail-fast; one source per world fact (ARCH-14)
- [ ] Schema + indexes; tool-generated migrations in the same WP; expand/contract (ARCH-15)
- [ ] Concurrency register + idempotency table (ARCH-16)
- [ ] Job table: schedule, no overlap, run-once seam, retry, flag-off inert, liveness (ARCH-17)
- [ ] Flag register: default per env, hot/restart, gate placement, removal (ARCH-18)
- [ ] External systems behind ports citing EXT ids; UNVERIFIED → flag off, fail closed (ARCH-19)
- [ ] Deny by default, access matrix, threat model → TC or RISK (ARCH-20)
- [ ] Logs, correlation id, health + version, metrics, alerts, audit with real actor (ARCH-21)
- [ ] ADRs with ≥ 2 options and consequences; suppression markers listed or "none" (ARCH-22, ARCH-23)
- [ ] Ordered WPs, ≤ ~15 files, compile alone, TCs listed (ARCH-24)
- [ ] One module per declared profile (ARCH-25)

## Rules

### Structure

**ARCH-1** — Point every dependency inward: domain and application layers reference no framework, persistence, transport, UI or vendor type; they own the ports they need, outer layers implement them, and only the composition root wires concrete types; publish the rules as a layer table the Tester binds as an architecture test.
- *Why:* a type specified in the outer layer but consumed by an inner one forced the Builder to move a class to break a cycle and log it "resolved inline" (LL-42).
- *Check:* layer table (layer → may reference); the Auditor traces each component spec against it at 2R; the push-lane test also bans clock, randomness, network and storage calls outside their adapters (e.g. ArchUnit, NetArchTest, import-linter, dependency-cruiser).
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-2** — Place every configuration and options type where each consuming layer can reference it without a cycle (the innermost consumer or a shared contracts module), bound at the composition root.
- *Why:* an options type placed in infrastructure was consumed by an application service; the Builder moved it instead of halting (LL-42).
- *Check:* the configuration table has a "consumed by (layer)" column checked against the ARCH-1 layer table.
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-3** — Put every rule deciding money, eligibility, ranking, locking or state legality in a pure, total core function (inputs and "now" in, result out; no I/O, clock read or randomness), and compute each derived value with exactly one such function on the server for every read and write path — never accept it from a client.
- *Why:* a client-declared profit was trusted against the rule that derived fields are always recomputed server-side (LL-48).
- *Check:* the domain model marks each field server- or client-owned and names each derived field's function; a query re-expressing a function gets an agreement TC; each server-owned input field gets a forged-value TC.
- *Applies when:* always.
- *Provenance:* LL-48 (KatenatsioTipster, 2026-10)

**ARCH-4** — Answer the SOLID questions for every component and fix each "no" or justify it in an ADR: **S** one reason to change, stated in one sentence without "and"; **O** the next variant (provider, rule, permission) needs no edit to existing branches; **L** every port implementation, Null/off adapter included, honours the contract and its errors; **I** no consumer depends on members it never calls (e.g. a persistence port leaking the ORM query API); **D** inner layers own the abstractions.
- *Why:* a persistence port exposing the ORM's query surface tied the application layer to one engine and removed its fast unit seam.
- *Check:* the Auditor records answers for ≥ 5 components at 2R, every money/time/access component included.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-5** — Name every pattern (e.g. repository, outbox, strategy, decorator, state machine as data, saga) with the force that requires it — a requirement id, REQ-NF or RISK — and its cost; no pattern without a force; prefer the simplest structure meeting it.
- *Why:* unforced patterns add files, seams and failure paths that must be specified, tested and audited.
- *Check:* each pattern line cites a force id; none is a Minor AR, Major when it adds an untested path.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-6** — Apply YAGNI to features only: no capability, option or extension point beyond `analysis.md`, but every declared rule, invariant, operability default (RULES rule 8), security control, migration and test seam is specified in full; deferring one needs the user's acceptance as a RISK, never an architecture note.
- *Why:* a client-declared value was kept "YAGNI" against a business rule (LL-48); "no migrations" stood for three cycles and the schema lost ~60% of its columns (LL-21).
- *Check:* the Auditor maps every "YAGNI", "deferred", "later" and "out of scope" to a feature (fine) or a rule or safety mechanism (Major; Critical on money or access).
- *Applies when:* always.
- *Provenance:* LL-48, LL-21 (KatenatsioTipster, 2026-10)

### Blueprint

**ARCH-7** — Open with "Gate decisions honoured": every brd Decision `D-n`, Gate 1 and Gate UX resolution and catalogue invariant the cycle touches, with the section implementing it; no section, default or residual assumption contradicts one — a needed change goes back to its owner through the Manager.
- *Why:* a Gate 1 decision (missing numbers fail validation) was reversed by an architecture note (missing values become 0) and every gate passed (LL-44).
- *Check:* the Auditor diffs the list against brd Decisions and `analysis.md` BRs and reads each section; a contradiction or omission is Major.
- *Applies when:* always.
- *Provenance:* LL-44 (KatenatsioTipster, 2026-10)

**ARCH-8** — Meet the blueprint standard: a code generator with no prior knowledge implements every component without a question — paths, signatures in the project's language, types, constants, order, every success and failure path; "handle appropriately", "as needed", "etc.", "similar to", "TBD" and an existing helper without `path:line` are failures; record self-verification in the artifact.
- *Why:* blueprint gaps were filled by Builder improvisation logged as notes instead of halts (LL-42).
- *Check:* the Auditor greps the phrases and opens every `path:line`; self-verification covers both directions — structure ↔ specs ↔ registrations, diagram nodes ↔ specs, one meaning per field across sections, cardinality of every "the X of Y" field, requirement → section → component → test level → WP.
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-9** — Give every read a consumer needs (screen, panel, dialog, command output, report, downstream stage) a non-mutating operation, and every operation a consumer; reads write nothing — no audit row, counter or side effect.
- *Why:* a detail panel had no read endpoint, so a mutating update served as a read and every view wrote a phantom audit row (LL-42).
- *Check:* the profile module maps data need → operation; the Auditor walks both directions; a need without a read is Major.
- *Applies when:* any profile with a consumer-facing interface.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-10** — Specify every data flow as numbered steps from the outermost boundary input (external payload, request, file, message), each naming input, component, persisted effect (rows inserted, updated, deleted), output and failure behaviour.
- *Why:* "delete provisional rows, insert final rows" was half-implemented and passed checks that named things, not steps (LL-51).
- *Check:* each step maps to a CHAIN or step TC (INTEG-10, INTEG-11, VAR-18); the Auditor walks each step to code at L1.
- *Applies when:* any flow crossing a boundary or persisting state.
- *Provenance:* LL-51 (KatenatsioTipster, 2026-10)

### Testability

**ARCH-11** — Put every nondeterministic or outside-world dependency behind an injected seam — clock (the only time source, entity defaults included), id generation, randomness, each external system (port with real, Null/off and fake implementations), flags, configuration — listed in a seam register: seam, production implementation, test double, fidelity rule (EXT ids), substitution point.
- *Why:* wall-clock reads in entity defaults and one service made boundaries untestable while the rest was seamed.
- *Check:* the ARCH-1 test bans direct clock, random and I/O calls outside adapters; each TSEAM-n the Tester raises is a gap in this register.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-12** — Write the Testability & Test Architecture section: levels cited from `TESTING.md`; harness = the production composition root over its real transport, stores built only by shipped migrations (INTEG-2), fakes answering like the real thing (FAKE-1), seeding via public operations, e2e environment, ports and device projects; an overrides register (endpoints and credentials only); a run-one-cycle seam per job; test hooks unreachable in production configuration; the access matrix as data; test-tree paths.
- *Why:* no blueprint had a test section and tests auto-created the schema, so a migration missing ~60% of columns passed four audits (LL-21); tests written after code cost two build iterations per cycle (LL-29).
- *Check:* no subsection blank or N/A on an M row (STRAT-4); the Auditor diffs harness overrides with the register (INTEG-6).
- *Applies when:* always.
- *Provenance:* LL-21, LL-29 (KatenatsioTipster, 2026-10)

### Errors, configuration, persistence

**ARCH-13** — Keep one error catalogue — failure → code → status, exit code or error type → body → user message key (`design.md`) → log level → recovery — with the taxonomy stated once (INTEG HTTP table), each operation's codes drawn from it, persistence conflicts, uniqueness violations and dependency failures mapped explicitly, machine code apart from human text, and expected client errors logged below error level.
- *Why:* refusals and validation errors were logged as server errors with stack traces (LL-15); external failures reached users as "Server error" (LL-11).
- *Check:* a TC per entry incl. "expected 4xx logs no error" (INTEG-8); the Auditor flags uncatalogued codes, catch-all mappings, 5xx business outcomes and stack traces in bodies. cli: exit codes + stderr; library: typed errors; data-pipeline: dead-letter reasons.
- *Applies when:* always.
- *Provenance:* LL-15, LL-11 (KatenatsioTipster, 2026-10)

**ARCH-14** — Specify every configuration key — name, type, default or required, validation, secret, hot or restart, consuming layer, every place it is set (code, config file, manifest, env example) — validate all at start-up and refuse to start listing every missing or invalid key, unresolvable world facts (zone ids, locales, currencies, certificates) included; no fallback or "safe default" for an unverified world fact; one source of truth per world fact and per secret-derived value.
- *Why:* an unknown provider zone fell back to UTC and every deadline was 8 hours late (LL-1); a dev key derived twice broke sign-in and docs contradicted real defaults (LL-22).
- *Check:* agreement TC per multi-place key (FAKE-3); three fail-fast TCs per world-fact key (FAKE-12); each world-fact default cites a VERIFIED EXT id.
- *Applies when:* always.
- *Provenance:* LL-1, LL-22 (KatenatsioTipster, 2026-10)

**ARCH-15** — Specify the schema with exact types, constraints and indexes (each query: predicate → index, round trips, no N+1), back each uniqueness rule with a constraint of identical semantics, and change it only through migrations the tool generates in the WP that changes the model — never hand-edited snapshots — as expand/contract so the previous release runs on the new schema (rollback after migration).
- *Why:* migrations were forbidden because a sandbox could not run the tool; tests auto-created the schema and a snapshot missing ~60% of columns passed four audits (LL-21); start-up crashed on a store that did not exist yet (LL-14).
- *Check:* CI migrates from empty and from the previous release, checks model ↔ migration drift and boots on empty infrastructure (GATE rules, `absd/playbook/testing/gates.md`); each migration names its rollback; an environment that cannot run the tool is a RISK, never a design choice.
- *Applies when:* the product owns persistent state.
- *Provenance:* LL-21, LL-14 (KatenatsioTipster, 2026-10)
- Illustration: e.g. EF Core migrations, Alembic, Flyway; drift: EF `has-pending-model-changes`, Django `makemigrations --check`.

### Concurrency, jobs, flags, integrations

**ARCH-16** — Keep a concurrency register — each aggregate with more than one writer (person, job, second admin): token or lock, each writer's conflict answer (retry, skip, 409 + re-fetch; never 5xx), the serialisation of each check-then-act invariant — and an idempotency table: each mutating operation's second-call outcome, idempotency keys for retried creates, messages emitted only when their transaction commits.
- *Why:* idempotent re-runs were written as criteria yet never designed or tested (LL-45); unserialised "last admin" checks break under two admins.
- *Check:* race TC per register row (VAR-12, INTEG-12), run-twice TC per table row (VAR-13, INTEG-13); the Auditor finds every writer of each entity in the register.
- *Applies when:* concurrent writers, retries, jobs, imports or natural keys exist.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10)

**ARCH-17** — Specify each background job: trigger and schedule with zone, interval bounds, no overlap (single instance stated, or a lock or lease), a thin scheduler calling a run-one-cycle use case that returns what it did, per-item idempotency and failure isolation, crash/retry semantics, cancellation, the flag checked in scheduler and body (off = no calls, writes or messages), liveness (last success, failures) with an alert.
- *Why:* a flag-off path had no coverage and turning the flag on at runtime did not rewire the provider bound at start-up (LL-23).
- *Check:* INTEG-14 TCs per job; no blank job-table cell.
- *Applies when:* schedulers, pollers, queues or recurring work.
- *Provenance:* LL-23 (KatenatsioTipster, 2026-10)

**ARCH-18** — Register every flag: purpose, default per environment, hot or restart (how adapters rewire on a hot change), gate placement before authorization and validation (off = absent: 404, unknown command, no job run), client exposure, owner, removal condition; a flag guarding an UNVERIFIED fact is off everywhere (EXT-1).
- *Why:* a "live" flag did not rewire a provider bound at start-up and only one state was tested (LL-23); a feature on an unverified zone shipped enabled (LL-1).
- *Check:* on, off and toggle TCs per entry (VAR-19); register defaults equal every config location (FAKE-3).
- *Applies when:* flags, kill switches, behaviour-changing settings.
- *Provenance:* LL-23, LL-1 (KatenatsioTipster, 2026-10)

**ARCH-19** — Reach every external system only through an application-owned port; cite the EXT id of each fact an adapter relies on; per call specify timeout, retries and the catalogue code of each failure class (FAKE-7); never specify external behaviour from a description — an UNVERIFIED fact puts its behaviour behind a flag off everywhere that fails closed.
- *Why:* an unverified zone shipped as a "safe default" (LL-1); a reader written from a description took half-time for final (LL-2); external failures showed "Server error" (LL-11).
- *Check:* trace_check gate2 finds every EXT of `analysis.md`; the Auditor confirms enabled paths use only VERIFIED facts and no inner layer references an infrastructure client.
- *Applies when:* any external system, deploy platforms included.
- *Provenance:* LL-1, LL-2, LL-11 (KatenatsioTipster, 2026-10)

### Security and observability

**ARCH-20** — Design security, not prose: deny by default; one enforcing layer per rule; the Access & Visibility Matrix over every operation with visible records and fields (ACCESS-1, ACCESS-2, ACCESS-3); a threat model (spoofing, tampering, repudiation, disclosure, denial, elevation) → mitigation → TC or user-accepted RISK; rate limits on anonymous secret checks and metered dependencies; restricted-state allowlists declared on operations, never by path matching.
- *Why:* access designed per endpoint and role let an allowed call return paid content to free accounts (LL-10).
- *Check:* matrix rows equal operations; the Auditor rejects a threat without TC or RISK and a rule enforced in two disagreeing layers (SEC rules).
- *Applies when:* always (library: input validation and secret handling).
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**ARCH-21** — Specify observability: structured logs, levels from the error catalogue, a never-log list (secrets, keys in URLs, personal data); a correlation id through requests, jobs, messages and audit rows; request logs with the status sent; readiness (store, migrations, dependencies) and a version endpoint or output for version-aware smoke; metrics per operation, job and external budget; alerts with threshold and first action; an audit catalogue — action → operation, same transaction, real actor under impersonation, append-only below the application, never on reads.
- *Why:* expected refusals were logged as errors (LL-15); a version-blind health check passed an unchanged deploy (LL-32); a read wrote audit rows (LL-42).
- *Check:* OPS TCs (`absd/playbook/testing/nonfunctional.md`); INTEG-9 per audited action.
- *Applies when:* always; cli and library: logs, exit codes, version output.
- *Provenance:* LL-15, LL-32, LL-42 (KatenatsioTipster, 2026-10)

### Decisions and delivery

**ARCH-22** — Record each decision with real alternatives as `ADR-n`: context (forces, requirement ids), ≥ 2 options with trade-offs, decision, consequences (tests, operations, migration, cost), status; an M cell turned N/A, a deferred default REQ-NF and a contested AR each need one.
- *Why:* unrecorded choices get re-litigated or silently reversed in later cycles.
- *Check:* the Auditor rejects one-option or consequence-free ADRs; the ADR index in `context.md` matches.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-23** — List every suppression marker production code may carry (coverage exclusion, lint or warning disable, type ignore) with file, rule, reason and expiry — or "none"; never on money, time or access paths.
- *Why:* one exclusion attribute removes a unit from the no-untested-unit gate (GATE-2) without touching a test.
- *Check:* the Auditor greps production code and diffs with the list; unlisted = Major (CODE rules).
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-24** — Cut the build into ordered work packages `WP-n`, each ≤ ~15 files, compiling and running its fast suite alone (no reference to a later WP), listing files, generated migrations and the TCs it turns green; first the public surface the red tests compile against.
- *Why:* monolithic builds hit session limits and the orchestrator finished the code itself (LL-26).
- *Check:* trace_check gate2 finds ≥ 1 WP; each file in exactly one WP; no forward reference; the Builder commits per WP and resumes at the first WP without a commit.
- *Applies when:* always.
- *Provenance:* LL-26 (KatenatsioTipster, 2026-10)

**ARCH-25** — Add a module per declared profile (table); none is N/A while its interface exists.
- *Why:* web-only assumptions left CLI grammar, exit codes and other non-web surfaces unspecified (LL-41).
- *Check:* `context.md` profiles map to modules; examples run as consumer tests (DSN-19).
- *Applies when:* always.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

| Profile | Module specifies |
|---|---|
| http-api | per operation: method, path, auth, schemas (server-owned fields marked), status per outcome, error codes; one error body (RFC 9457); stable-order pagination, max page size; versioning + deprecation; idempotency keys; machine-readable contract (e.g. OpenAPI, JSON Schema) |
| web-ui, native-app | screen → components → read operations → client state; caching and refresh (no polling unless specified); formatter per value; principal switch clears data |
| cli | command tree → handler; precedence flag > env > file > default; stdout/stderr; exit-code table; `--json` schema; TTY vs pipe |
| library | every public symbol's signature and errors; semver (what breaks), deprecation window, runtimes; public-surface snapshot |
| data-pipeline | dataset schemas (types, units, zones, nullability, keys); idempotent writes; duplicate and late data; replay, backfill, dead letter |

## Architecture review checklist (Gate 2R)

The Auditor walks every row, records each miss as an AR citing `ABSD:ARCH-n`, may raise a severity, never lowers one.

| Item | What to look for | Severity if missing |
|---|---|---|
| Dependency direction | layer table; inward references; config types reachable (ARCH-1, ARCH-2) | Major |
| Decisions honoured | every D-n and invariant listed and implemented; no contradiction (ARCH-7) | Major |
| Blueprint | no vague phrase; `path:line` exists; self-verification both ways (ARCH-8) | Major |
| Reads | every data need → non-mutating read (ARCH-9) | Major |
| Derived values | one server-side function; nothing client-declared (ARCH-3) | Critical on money, else Major |
| Seams & harness | seam register; overrides register; run-once seams; test DB only via migrations (ARCH-11, ARCH-12) | Major |
| Migrations | tool-generated, same WP, expand/contract, rollback, drift gate, constraints (ARCH-15) | Major |
| Error catalogue | codes per operation; no 5xx outcome; expected 4xx below error level (ARCH-13) | Major |
| Access matrix | every operation × ACCESS-2 principal; fields; one enforcing layer (ARCH-20) | Critical |
| Threat model | each threat → mitigation → TC or RISK (ARCH-20) | Major; Critical for auth, money, personal data |
| External facts | EXT cited; UNVERIFIED → flag off, fail closed; no unverified default (ARCH-14, ARCH-19) | Critical |
| Configuration | typed, validated, fail-fast; one source per world fact (ARCH-14) | Major |
| Flags | register complete; gate placement; hot/restart (ARCH-18) | Major |
| Concurrency & idempotency | every multi-writer aggregate, invariant, second call; jobs (ARCH-16, ARCH-17) | Major; Critical on money |
| Observability | logs, correlation, health + version, alerts, audit actor (ARCH-21) | Major |
| Data flows | numbered testable steps incl. deletions (ARCH-10) | Major |
| Work packages | ordered, ≤ ~15 files, compile alone, TCs listed (ARCH-24) | Major |
| YAGNI vs correctness | nothing beyond analysis; no rule or safety mechanism deferred (ARCH-5, ARCH-6) | Major; Critical on money or access |
| N/A vs applicability | each N/A in an X cell or an ADR (STRAT-4, ARCH-22) | Major |
| Profiles, ADRs, markers | module per profile; ≥ 2 options; markers listed (ARCH-22, ARCH-23, ARCH-25) | Major |
