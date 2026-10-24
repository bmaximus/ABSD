# Architecture Excellence

Code **ARCH**: what `architecture.md` must specify. The Architect applies it, Gate 2 checks presence, the Auditor
judges quality at Gate 2R (`absd/playbook/engineering/architecture-review.md`) and at audit L1, L7. Related: CODE,
SEC, PRIV, INTEG, FAKE, EXT, ACCESS, VAR.

## Checklist

- [ ] Inward dependencies + architecture test; config types reachable without a cycle (ARCH-1, ARCH-2)
- [ ] Pure decision core; derived values server-side (ARCH-3)
- [ ] SOLID per component; patterns cite forces; YAGNI for features only (ARCH-4, ARCH-5, ARCH-6)
- [ ] Gate decisions honoured; blueprint standard + self-verification (ARCH-7, ARCH-8)
- [ ] Non-mutating reads; data flows as numbered steps (ARCH-9, ARCH-10)
- [ ] Seam register; test architecture, overrides, test tooling in Tester files; TSEAM by kind (ARCH-11, ARCH-12)
- [ ] Error catalogue; config typed, fail-fast, one source per world fact (ARCH-13, ARCH-14)
- [ ] Schema, indexes, expand/contract migrations (ARCH-15)
- [ ] Concurrency register + idempotency table; job table; flag register, off = inert (ARCH-16, ARCH-17, ARCH-18)
- [ ] Ports cite EXT ids; UNVERIFIED → off, fail closed (ARCH-19)
- [ ] Deny by default; access matrix; threat model; observability and audit catalogue (ARCH-20, ARCH-21)
- [ ] ADRs with ≥ 2 options; suppression markers listed (ARCH-22, ARCH-23)
- [ ] Ordered WPs, ≤ ~15 files each; module per profile, design names verbatim (ARCH-24, ARCH-25)

## Rules

**ARCH-1** — Point dependencies inward: inner (domain, application) layers own their ports and reference no framework, persistence, transport, UI or vendor type; only the composition root wires concrete types; a layer table the Tester binds as an architecture test.
- *Why:* an inner layer using an outer-layer type forced a class move to break a cycle (LL-42).
- *Check:* layer → may-reference table traced per component at 2R; the push-lane test bans clock, random, network and storage calls outside adapters (e.g. ArchUnit, NetArchTest, import-linter).
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-2** — Place each configuration type where every consuming layer reaches it without a cycle (innermost consumer or a shared contracts module), bound at the composition root.
- *Why:* the Builder moved a misplaced options type, not halting (LL-42).
- *Check:* the config table's "consumed by (layer)" column matches the ARCH-1 table.
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-3** — Decide money, eligibility, ranking, locking and state legality in pure, total core functions ("now" passed in; no I/O, clock or randomness); compute each derived value server-side by one function on every path, never from client input.
- *Why:* a client-declared profit was trusted against the server-recompute rule (LL-48).
- *Check:* the domain model marks fields server- or client-owned and names each derived field's function; agreement TC per query re-expressing one; forged-value TC per server-owned input.
- *Applies when:* always.
- *Provenance:* LL-48 (KatenatsioTipster, 2026-10)

**ARCH-4** — Answer SOLID per component; fix each "no" or justify it (ADR): **S** one reason to change (one sentence, no "and"); **O** a new variant (provider, rule, permission) edits no existing branch; **L** each port implementation, Null/off included, honours the contract incl. errors; **I** no consumer depends on unused members; **D** inner layers own abstractions.
- *Why:* a port exposing the ORM query API tied the application to one engine.
- *Check:* answers for ≥ 5 components at 2R, incl. every money/time/access one.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-5** — Name every pattern (e.g. repository, outbox, strategy, state machine as data, saga) with its force (requirement id, REQ-NF or RISK) and cost; no force, no pattern.
- *Why:* unforced patterns add files, seams and failure paths.
- *Check:* each pattern cites a force id; none = Minor AR, Major with an untested path.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-6** — Apply YAGNI to features only (nothing beyond `analysis.md`); fully specify every declared rule, invariant, operability default in its OPS scope (RULES rule 8), security control, migration and test seam; deferring one needs the user's RISK acceptance, never an architecture note.
- *Why:* a client-declared value stayed "YAGNI" against a rule (LL-48); "no migrations" stood three cycles (LL-21).
- *Check:* each "YAGNI", "deferred", "later", "out of scope" maps to a feature (fine) or a rule/safety mechanism (Major; Critical on money or access); a default out of OPS scope is N/A citing it.
- *Applies when:* always.
- *Provenance:* LL-48, LL-21 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**ARCH-7** — Open with "Gate decisions honoured": each brd Decision `D-n`, Gate 1 and Gate UX resolution and catalogue invariant the cycle touches → implementing section; nothing contradicts one (changes go to the owner via the Manager).
- *Why:* a note ("missing values become 0") reversed a Gate 1 decision unnoticed (LL-44).
- *Check:* diff the list with brd Decisions and `analysis.md` BRs; read each section; contradiction or omission = Major.
- *Applies when:* always.
- *Provenance:* LL-44 (KatenatsioTipster, 2026-10)

**ARCH-8** — Meet the blueprint standard: a code generator with no prior knowledge builds every component without asking (paths, signatures in the project's language, types, constants, order, all success and failure paths); "handle appropriately", "as needed", "etc.", "similar to", "TBD" and a helper without `path:line` fail; self-verification recorded.
- *Why:* Builder improvisation filled gaps, logged as notes (LL-42).
- *Check:* grep the phrases, open each `path:line`, verify both ways: structure ↔ specs ↔ registrations, diagram ↔ specs, one meaning per field, "the X of Y" cardinality, requirement → section → component → test level → WP.
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-9** — Give every consumer data need (screen, dialog, command output, report, downstream stage) a non-mutating read and every operation a consumer; reads write nothing (no audit row, counter, side effect).
- *Why:* a panel without a read used a mutating update; each view wrote a phantom audit row (LL-42).
- *Check:* the profile module maps need → operation both ways; a need without a read = Major.
- *Applies when:* any consumer-facing interface.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-10** — Specify each data flow as numbered steps from the outermost boundary input (payload, request, file, message), each naming input, component, persisted effect (rows inserted, updated, deleted), output, failure.
- *Why:* "delete provisional, insert final" was half-built; checks named things, not steps (LL-51).
- *Check:* each step → a chain or step TC (INTEG-10, INTEG-11, VAR-18), walked to code at L1.
- *Applies when:* any flow crossing a boundary or persisting state.
- *Provenance:* LL-51 (KatenatsioTipster, 2026-10)

**ARCH-11** — Inject a seam for every nondeterministic or external dependency — clock (sole time source, entity defaults included), ids, randomness, each external system (port with real, Null/off, fake), flags, config — in a register: seam, production implementation, test double, fidelity rule (EXT ids), substitution point.
- *Why:* wall-clock entity defaults left boundaries untestable.
- *Check:* the ARCH-1 test bans clock, random and I/O calls outside adapters; each TSEAM-n of kind `seam` is a register gap.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-12** — Write the Testability & Test Architecture section: levels from `TESTING.md`; harness = production composition root over real transport, stores built only by shipped migrations (INTEG-2), faithful fakes (FAKE-1), seeding via public operations; e2e environment, ports, devices; overrides register (endpoints, credentials only); run-one-cycle seam per job; test hooks unreachable in production; access matrix as data; test paths, with a unit per WP where new symbols need one (ORACLE-3); test dependencies, runner, coverage, mutation and test-lint settings in standalone Tester-owned files, else listed sections of a shared file (ADR-002; TSEAM kind `tooling`).
- *Why:* auto-created test schemas let a migration missing ~60% of columns pass four audits (LL-21); tests after code cost two build rounds (LL-29); test settings in Builder files blocked the Tester (LL-57).
- *Check:* no subsection blank or N/A on an M row (STRAT-4); overrides diffed with the register (INTEG-6); test settings only in Tester files or listed sections (GATE-7).
- *Applies when:* always.
- *Provenance:* LL-21, LL-29 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ARCH-13** — Keep one error catalogue (failure → code → status, exit code or error type → body → `design.md` message key → log level → recovery) on one taxonomy (INTEG HTTP table), each operation's codes drawn from it; map conflicts, uniqueness and dependency failures explicitly; machine code apart from human text; expected client errors below error level.
- *Why:* refusals logged as server errors with stack traces (LL-15); external failures shown as "Server error" (LL-11).
- *Check:* a TC per entry incl. "expected 4xx logs no error" (INTEG-8); uncatalogued codes, catch-alls, 5xx business outcomes, stack traces flagged.
- *Applies when:* always (cli: exit codes + stderr; library: typed errors; data-pipeline: dead-letter reasons).
- *Provenance:* LL-15, LL-11 (KatenatsioTipster, 2026-10)

**ARCH-14** — Specify each config key (name, type, default or required, validation, secret, hot/restart, consuming layer, every place set: code, config, manifest, env example); validate at start-up, refusing to start and listing every missing or invalid key incl. unresolvable world facts (zone ids, locales, currencies, certificates); no default for an unverified world fact; one source per world fact and secret-derived value.
- *Why:* an unknown zone fell back to UTC, deadlines 8 h late (LL-1); a dev key derived twice broke sign-in (LL-22).
- *Check:* agreement TC per multi-place key (FAKE-3); three fail-fast TCs per world-fact key (FAKE-12); world-fact defaults cite a VERIFIED EXT id.
- *Applies when:* always.
- *Provenance:* LL-1, LL-22 (KatenatsioTipster, 2026-10)

**ARCH-15** — Specify the schema with exact types, constraints and indexes (per query: predicate → index, round trips, no N+1); back each uniqueness rule with an identical constraint; change it only by tool-generated migrations in the WP changing the model (no hand-edited snapshot), expand/contract so the previous release runs on the new schema.
- *Why:* a sandbox lacking the tool banned migrations; the snapshot drifted (LL-21); start-up crashed on a missing store (LL-14).
- *Check:* CI migrates from empty and the previous release, gates model ↔ migration drift (e.g. EF Core `has-pending-model-changes`, Django `makemigrations --check`), boots on empty infrastructure; each migration names its rollback; a tool-less environment is a RISK, never a design choice.
- *Applies when:* the product owns persistent state.
- *Provenance:* LL-21, LL-14 (KatenatsioTipster, 2026-10)

**ARCH-16** — Keep a concurrency register (per multi-writer aggregate — person, job, second admin: token or lock; each writer's conflict answer: retry, skip or 409 + re-fetch, never 5xx; serialisation of each check-then-act invariant) and an idempotency table (second-call outcome per mutating operation, keys for retried creates, messages only on commit).
- *Why:* idempotent re-runs were criteria, never designed or tested (LL-45); an unserialised "last admin" check fails with two admins.
- *Check:* race TC per register row (VAR-12, INTEG-12), run-twice TC per table row (VAR-13, INTEG-13); every writer of each entity listed.
- *Applies when:* concurrent writers, retries, jobs, imports or natural keys exist.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10)

**ARCH-17** — Specify each background job: trigger, schedule with zone, interval bounds; no overlap (single instance, lock or lease); a thin scheduler over a run-one-cycle use case reporting what it did; per-item idempotency and failure isolation; crash/retry; cancellation; flag checked in scheduler and body (off = no calls, writes, messages); liveness with an alert.
- *Why:* the flag-off path had no coverage (LL-23).
- *Check:* INTEG-14 TCs per job; no blank job-table cell.
- *Applies when:* schedulers, pollers, queues or recurring work.
- *Provenance:* LL-23 (KatenatsioTipster, 2026-10)

**ARCH-18** — Register every flag: purpose, default per environment, hot or restart (how adapters rewire when hot), gate before authorization and validation (off = absent: 404, unknown command, no job run), client exposure, owner, removal condition; flags guarding UNVERIFIED facts are off everywhere (EXT-1).
- *Why:* a flag flip did not rewire a start-up-bound provider; one state was tested (LL-23); an unverified-zone feature shipped on (LL-1).
- *Check:* on, off and toggle TCs per flag (VAR-19); defaults equal every config location (FAKE-3).
- *Applies when:* flags, kill switches, behaviour-changing settings.
- *Provenance:* LL-23, LL-1 (KatenatsioTipster, 2026-10)

**ARCH-19** — Reach each external system only via an application-owned port; cite the EXT id of every fact an adapter relies on; per call specify timeout, retries and each failure class's catalogue code (FAKE-7); never specify external behaviour from a description; UNVERIFIED-fact behaviour sits behind a flag off everywhere and fails closed.
- *Why:* an unverified zone shipped as a "safe default" (LL-1); a reader built from a description read half-time as final (LL-2); failures read "Server error" (LL-11).
- *Check:* trace_check gate2 finds every EXT of `analysis.md`; enabled paths use only VERIFIED facts; no inner layer uses an infrastructure client.
- *Applies when:* any external system, deploy platforms included.
- *Provenance:* LL-1, LL-2, LL-11 (KatenatsioTipster, 2026-10)

**ARCH-20** — Design security: deny by default; one enforcing layer per rule; an Access & Visibility Matrix of every operation with visible records and fields (ACCESS-1, ACCESS-2, ACCESS-3); STRIDE threat model → mitigation → TC or user-accepted RISK; rate limits on anonymous secret checks and metered dependencies; restricted-state allowlists per operation, not path matching.
- *Why:* per-endpoint, per-role access let an allowed call return paid content to free accounts (LL-10).
- *Check:* matrix rows = operations; reject a threat without TC or RISK, a rule enforced in two disagreeing layers (SEC).
- *Applies when:* always (library: input validation, secret handling).
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**ARCH-21** — Specify observability: structured logs at catalogue levels; never-log list (secrets, URL keys, personal data); correlation id across requests, jobs, messages, audit rows; request logs with status sent; readiness (store, migrations, dependencies) + version for version-aware smoke; metrics per operation, job, external budget; alerts with threshold and first action; audit catalogue (action → operation, same transaction, real actor under impersonation, append-only, never on reads).
- *Why:* refusals logged as errors (LL-15); a version-blind health check passed a stale deploy (LL-32); reads wrote audit rows (LL-42).
- *Check:* OPS TCs; INTEG-9 per audited action.
- *Applies when:* always; cli and library: logs, exit codes, version output.
- *Provenance:* LL-15, LL-32, LL-42 (KatenatsioTipster, 2026-10)

**ARCH-22** — Record each decision with real alternatives as `ADR-n`: context (forces, requirement ids), ≥ 2 options with trade-offs, decision, consequences (tests, operations, migration, cost), status; required for an M cell turned N/A, a deferred default REQ-NF, a contested AR.
- *Why:* unrecorded choices get re-litigated or silently reversed.
- *Check:* one-option or consequence-free ADRs rejected; `context.md` ADR index matches.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-23** — List every suppression marker in production code (coverage exclusion, lint or warning disable, type ignore) with file, rule, reason, expiry, or "none"; none on money, time or access paths.
- *Why:* one exclusion attribute drops a unit from GATE-2 with no test touched.
- *Check:* grep production code against the list; unlisted = Major (CODE rules).
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-24** — Cut the build into ordered work packages `WP-n` of ≤ ~15 files, each compiling and running its fast suite alone (no later-WP reference), listing files, generated migrations, new public symbols (their test units keyed to it, ORACLE-3) and TCs it turns green; first the public surface the red tests compile against.
- *Why:* monolithic builds hit session limits; the orchestrator coded (LL-26).
- *Check:* trace_check gate2 finds ≥ 1 WP; each file in exactly one WP; no forward reference; the Builder commits per WP, resumes at the first uncommitted one.
- *Applies when:* always.
- *Provenance:* LL-26 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ARCH-25** — Add a module per declared profile (table); none is N/A while its interface exists. For cli, http-api and library adopt `design.md`'s public names (commands, flags; resources, fields, error body, named examples; public symbols, error types) verbatim, each bound in the §5.0 table; an unbindable one returns to the Designer.
- *Why:* web-only assumptions left CLI grammar and exit codes unspecified (LL-41); nobody could name the public surface, so examples had nothing to bind to (LL-55, LL-56).
- *Check:* profiles map to modules; every `design.md` public name is in §5.0, bound; examples run as consumer tests (DSN-18).
- *Applies when:* always; naming for cli, http-api, library.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

| Profile | Module specifies |
|---|---|
| http-api | per operation: method, path, auth, schemas (server-owned fields marked), status per outcome, error codes; one error body (RFC 9457); stable pagination, max page size; versioning, deprecation; idempotency keys; contract file (e.g. OpenAPI, JSON Schema) |
| web-ui, native-app | screen → components → reads → client state; caching, refresh (no unspecified polling); formatter per value; principal switch clears data |
| cli | command tree → handler; precedence flag > env > file > default; stdout/stderr; exit codes; `--json` schema; TTY vs pipe |
| library | public signatures and errors; semver (what breaks), deprecation window, runtimes; public-surface snapshot |
| data-pipeline | dataset schemas (types, units, zones, nullability, keys); idempotent writes; duplicate, late data; replay, backfill, dead letter |
