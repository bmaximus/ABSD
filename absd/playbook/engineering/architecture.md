# Architecture Excellence

Code **ARCH**: what `architecture.md` must specify (skeleton: `absd/templates/artifacts/architecture.md`). The Architect
applies it, Gate 2 checks presence, the Auditor judges quality at Gate 2R with the checklist in
`absd/playbook/engineering/architecture-review.md` and at audit L1, L7. Related: CODE
(`absd/playbook/engineering/code-quality.md`), SEC, PRIV (`absd/playbook/security/baseline.md`), test-side INTEG, FAKE,
EXT, ACCESS, VAR.

## Checklist

- [ ] Inward dependencies; architecture test (ARCH-1)
- [ ] Config types reachable without a cycle (ARCH-2)
- [ ] Pure decision core; derived values server-side (ARCH-3)
- [ ] SOLID per component; patterns cite forces (ARCH-4, ARCH-5)
- [ ] YAGNI for features only, never for rules or safety (ARCH-6)
- [ ] Gate decisions honoured (ARCH-7)
- [ ] Blueprint standard; self-verification (ARCH-8)
- [ ] Non-mutating reads (ARCH-9)
- [ ] Data flows as numbered steps (ARCH-10)
- [ ] Seam register; TSEAM answered by kind (ARCH-11)
- [ ] Test architecture + overrides register; test tooling in Tester-owned files (ARCH-12)
- [ ] Error catalogue (ARCH-13)
- [ ] Config typed, fail-fast; one source per world fact (ARCH-14)
- [ ] Schema, indexes, expand/contract migrations (ARCH-15)
- [ ] Concurrency register + idempotency table (ARCH-16)
- [ ] Job table; flag off = inert (ARCH-17)
- [ ] Flag register (ARCH-18)
- [ ] Ports cite EXT ids; UNVERIFIED → off, fail closed (ARCH-19)
- [ ] Deny by default; access matrix; threat model (ARCH-20)
- [ ] Observability and audit catalogue (ARCH-21)
- [ ] ADRs with ≥ 2 options; suppression markers listed (ARCH-22, ARCH-23)
- [ ] Ordered WPs, ≤ ~15 files each (ARCH-24)
- [ ] Module per declared profile; the design's public names adopted verbatim (ARCH-25)

## Rules

**ARCH-1** — Point dependencies inward: domain and application layers own their ports and reference no framework, persistence, transport, UI or vendor type; outer layers implement them; only the composition root wires concrete types; publish a layer table the Tester binds as an architecture test.
- *Why:* an outer-layer type used by an inner layer forced a class move to break a cycle (LL-42).
- *Check:* table (layer → may reference) traced per component at 2R; the push-lane test also bans clock, random, network and storage calls outside adapters (e.g. ArchUnit, NetArchTest, import-linter).
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-2** — Place each configuration type where every consuming layer reaches it without a cycle (innermost consumer or a shared contracts module), bound at the composition root.
- *Why:* the Builder moved a misplaced options type instead of halting (LL-42).
- *Check:* the config table's "consumed by (layer)" column agrees with the ARCH-1 table.
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-3** — Decide money, eligibility, ranking, locking and state legality in pure, total core functions ("now" passed in; no I/O, clock or randomness); compute each derived value server-side with exactly one function on every path, never from client input.
- *Why:* a client-declared profit was trusted against the server-recompute rule (LL-48).
- *Check:* domain model marks fields server- or client-owned, names each derived field's function; agreement TC per query re-expressing one; forged-value TC per server-owned input.
- *Applies when:* always.
- *Provenance:* LL-48 (KatenatsioTipster, 2026-10)

**ARCH-4** — Answer SOLID per component; fix each "no" or justify it in an ADR: **S** one reason to change (one sentence, no "and"); **O** a new variant (provider, rule, permission) edits no existing branch; **L** each port implementation, Null/off included, honours the contract incl. errors; **I** no consumer depends on unused members; **D** inner layers own abstractions.
- *Why:* a port exposing the ORM query API tied the application layer to one engine, losing its unit seam.
- *Check:* answers recorded for ≥ 5 components at 2R, all money/time/access ones included.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-5** — Name every pattern (e.g. repository, outbox, strategy, state machine as data, saga) with its force (requirement id, REQ-NF or RISK) and cost; no force, no pattern; prefer the simplest structure.
- *Why:* unforced patterns add files, seams and failure paths to specify, test and audit.
- *Check:* each pattern cites a force id; none = Minor AR, Major if it adds an untested path.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-6** — Apply YAGNI to features only (nothing beyond `analysis.md`); fully specify every declared rule, invariant, operability default whose OPS *Applies when* covers a declared profile (RULES rule 8), security control, migration and test seam; deferring one needs the user's acceptance as a RISK, never an architecture note.
- *Why:* a client-declared value stayed "YAGNI" against a business rule (LL-48); "no migrations" stood three cycles (LL-21).
- *Check:* each "YAGNI", "deferred", "later", "out of scope" maps to a feature (fine) or a rule/safety mechanism (Major; Critical on money or access); an operability default outside its *Applies when* is N/A citing the rule, no waiver.
- *Applies when:* always.
- *Provenance:* LL-48, LL-21 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**ARCH-7** — Open with "Gate decisions honoured": each brd Decision `D-n`, Gate 1 and Gate UX resolution and catalogue invariant the cycle touches → implementing section; no section, default or residual assumption contradicts one (changes go to the owner via the Manager).
- *Why:* an architecture note ("missing values become 0") reversed a Gate 1 decision; every gate passed (LL-44).
- *Check:* diff the list with brd Decisions and `analysis.md` BRs, read each section; contradiction or omission = Major.
- *Applies when:* always.
- *Provenance:* LL-44 (KatenatsioTipster, 2026-10)

**ARCH-8** — Meet the blueprint standard: a code generator with no prior knowledge builds every component without asking (paths, signatures in the project's language, types, constants, order, all success and failure paths); "handle appropriately", "as needed", "etc.", "similar to", "TBD" and a helper without `path:line` fail; record self-verification in the artifact.
- *Why:* Builder improvisation filled gaps, logged as notes instead of halts (LL-42).
- *Check:* grep the phrases, open each `path:line`, verify both ways: structure ↔ specs ↔ registrations, diagram ↔ specs, one meaning per field, cardinality of "the X of Y" fields, requirement → section → component → test level → WP.
- *Applies when:* always.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-9** — Give every consumer data need (screen, dialog, command output, report, downstream stage) a non-mutating read and every operation a consumer; reads write nothing (no audit row, counter or side effect).
- *Why:* a panel lacking a read endpoint used a mutating update; each view wrote a phantom audit row (LL-42).
- *Check:* the profile module maps need → operation, walked both ways; a need without a read = Major.
- *Applies when:* any consumer-facing interface.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**ARCH-10** — Specify each data flow as numbered steps from the outermost boundary input (payload, request, file, message), each naming input, component, persisted effect (rows inserted, updated, deleted), output, failure behaviour.
- *Why:* "delete provisional, insert final" was half-built; checks named things, not steps (LL-51).
- *Check:* each step → a CHAIN or step TC (INTEG-10, INTEG-11, VAR-18), walked to code at L1.
- *Applies when:* any flow crossing a boundary or persisting state.
- *Provenance:* LL-51 (KatenatsioTipster, 2026-10)

**ARCH-11** — Inject a seam for every nondeterministic or external dependency — clock (sole time source, entity defaults included), ids, randomness, each external system (port with real, Null/off, fake), flags, config — in a seam register: seam, production implementation, test double, fidelity rule (EXT ids), substitution point.
- *Why:* wall-clock reads in entity defaults left boundaries untestable.
- *Check:* the ARCH-1 test bans clock, random and I/O calls outside adapters; each TSEAM-n of kind `seam` is a register gap (kind `tooling`: ARCH-12).
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-12** — Write the Testability & Test Architecture section: levels from `TESTING.md`; harness = production composition root over real transport, stores built only by shipped migrations (INTEG-2), faithful fakes (FAKE-1), seeding via public operations; e2e environment, ports, devices; overrides register (endpoints, credentials only); run-one-cycle seam per job; test hooks unreachable in production; access matrix as data; test paths, with a compilation or collection unit per work package where new symbols need one (ORACLE-3); test tooling: ADR-002 puts test dependencies, runner, coverage, mutation and test-lint configuration in standalone Tester-owned files where the stack allows, otherwise lists the sections of each shared file the Tester may change. A TSEAM-n has a kind: `seam` (production code, ARCH-11) or `tooling` (a test dependency or setting in a file the Tester does not own) — answered here and in ADR-002, never by the Builder editing a gate.
- *Why:* no test section; auto-created test schemas let a migration missing ~60% of columns pass four audits (LL-21); tests after code cost two build rounds a cycle (LL-29); test dependencies and runner settings sat in Builder-owned build files, so the Tester's Foundation work was refused by the ownership hook (LL-57).
- *Check:* no subsection blank or N/A on an M row (STRAT-4); overrides diffed with the register (INTEG-6); every test tooling setting sits in a Tester-owned file or a listed shared section (GATE-7).
- *Applies when:* always.
- *Provenance:* LL-21, LL-29 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ARCH-13** — Keep one error catalogue (failure → code → status, exit code or error type → body → `design.md` message key → log level → recovery) on one taxonomy (INTEG HTTP table), each operation's codes drawn from it; map conflicts, uniqueness and dependency failures explicitly; machine code apart from human text; expected client errors logged below error level.
- *Why:* refusals logged as server errors with stack traces (LL-15); external failures shown as "Server error" (LL-11).
- *Check:* a TC per entry incl. "expected 4xx logs no error" (INTEG-8); flag uncatalogued codes, catch-alls, 5xx business outcomes, stack traces in bodies.
- *Applies when:* always (cli: exit codes + stderr; library: typed errors; data-pipeline: dead-letter reasons).
- *Provenance:* LL-15, LL-11 (KatenatsioTipster, 2026-10)

**ARCH-14** — Specify each config key (name, type, default or required, validation, secret, hot/restart, consuming layer, every place set: code, config, manifest, env example); validate at start-up, refusing to start and listing every missing or invalid key incl. unresolvable world facts (zone ids, locales, currencies, certificates); no fallback or default for an unverified world fact; one source per world fact and secret-derived value.
- *Why:* an unknown zone fell back to UTC, making deadlines 8 hours late (LL-1); a dev key derived twice broke sign-in (LL-22).
- *Check:* agreement TC per multi-place key (FAKE-3); three fail-fast TCs per world-fact key (FAKE-12); world-fact defaults cite a VERIFIED EXT id.
- *Applies when:* always.
- *Provenance:* LL-1, LL-22 (KatenatsioTipster, 2026-10)

**ARCH-15** — Specify the schema with exact types, constraints and indexes (per query: predicate → index, round trips, no N+1); back each uniqueness rule with an identical constraint; change it only by tool-generated migrations in the WP changing the model (no hand-edited snapshots), expand/contract so the previous release runs on the new schema.
- *Why:* a sandbox lacking the tool got migrations banned and the snapshot drifted (LL-21); start-up crashed on a missing store (LL-14).
- *Check:* CI migrates from empty and the previous release, gates model ↔ migration drift (e.g. EF Core `has-pending-model-changes`, Django `makemigrations --check`), boots on empty infrastructure (GATE rules); each migration names its rollback; an environment unable to run the tool is a RISK, never a design choice.
- *Applies when:* the product owns persistent state.
- *Provenance:* LL-21, LL-14 (KatenatsioTipster, 2026-10)

**ARCH-16** — Keep a concurrency register (per multi-writer aggregate — person, job, second admin: token or lock; each writer's conflict answer: retry, skip or 409 + re-fetch, never 5xx; serialisation of each check-then-act invariant) and an idempotency table (second-call outcome per mutating operation, keys for retried creates, messages sent only on commit).
- *Why:* idempotent re-runs were criteria, never designed or tested (LL-45); unserialised "last admin" checks fail under two admins.
- *Check:* race TC per register row (VAR-12, INTEG-12), run-twice TC per table row (VAR-13, INTEG-13); every writer of each entity is listed.
- *Applies when:* concurrent writers, retries, jobs, imports or natural keys exist.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10)

**ARCH-17** — Specify each background job: trigger, schedule with zone, interval bounds; no overlap (single instance, lock or lease); thin scheduler over a run-one-cycle use case reporting what it did; per-item idempotency and failure isolation; crash/retry; cancellation; flag checked in scheduler and body (off = no calls, writes, messages); liveness (last success, failures) with an alert.
- *Why:* the flag-off path had no coverage (LL-23).
- *Check:* INTEG-14 TCs per job; no blank job-table cell.
- *Applies when:* schedulers, pollers, queues or recurring work.
- *Provenance:* LL-23 (KatenatsioTipster, 2026-10)

**ARCH-18** — Register every flag: purpose, default per environment, hot or restart (how adapters rewire when hot), gate before authorization and validation (off = absent: 404, unknown command, no job run), client exposure, owner, removal condition; flags guarding UNVERIFIED facts are off everywhere (EXT-1).
- *Why:* a flag flip did not rewire a start-up-bound provider; one state was tested (LL-23); a feature on an unverified zone shipped on (LL-1).
- *Check:* on, off and toggle TCs per flag (VAR-19); defaults equal every config location (FAKE-3).
- *Applies when:* flags, kill switches, behaviour-changing settings.
- *Provenance:* LL-23, LL-1 (KatenatsioTipster, 2026-10)

**ARCH-19** — Reach each external system only via an application-owned port; cite the EXT id of every fact an adapter relies on; per call specify timeout, retries and each failure class's catalogue code (FAKE-7); never specify external behaviour from a description; UNVERIFIED-fact behaviour sits behind a flag off everywhere and fails closed.
- *Why:* an unverified zone shipped as a "safe default" (LL-1); a reader built from a description read half-time as final (LL-2); external failures showed "Server error" (LL-11).
- *Check:* trace_check gate2 finds every EXT of `analysis.md`; enabled paths use only VERIFIED facts; no inner layer references an infrastructure client.
- *Applies when:* any external system, deploy platforms included.
- *Provenance:* LL-1, LL-2, LL-11 (KatenatsioTipster, 2026-10)

**ARCH-20** — Design security: deny by default; one enforcing layer per rule; an Access & Visibility Matrix of every operation with visible records and fields (ACCESS-1, ACCESS-2, ACCESS-3); STRIDE threat model → mitigation → TC or user-accepted RISK; rate limits on anonymous secret checks and metered dependencies; restricted-state allowlists per operation, not path matching; service-identity grants as code, Builder-owned in ADR-002 (ACCESS-13).
- *Why:* per-endpoint, per-role access let an allowed call return paid content to free accounts (LL-10).
- *Check:* matrix rows = operations; reject a threat without TC or RISK and a rule enforced in two disagreeing layers (SEC rules).
- *Applies when:* always (library: input validation, secret handling).
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**ARCH-21** — Specify observability: structured logs at catalogue levels; never-log list (secrets, URL keys, personal data); correlation id across requests, jobs, messages, audit rows; request logs with status sent; readiness (store, migrations, dependencies) + version endpoint/output for version-aware smoke; metrics per operation, job, external budget; alerts with threshold and first action; audit catalogue (action → operation, same transaction, real actor under impersonation, append-only below the application, never on reads).
- *Why:* refusals logged as errors (LL-15); a version-blind health check passed an unchanged deploy (LL-32); reads wrote audit rows (LL-42).
- *Check:* OPS TCs (`absd/playbook/testing/nonfunctional.md`); INTEG-9 per audited action.
- *Applies when:* always; cli and library: logs, exit codes, version output.
- *Provenance:* LL-15, LL-32, LL-42 (KatenatsioTipster, 2026-10)

**ARCH-22** — Record each decision with real alternatives as `ADR-n`: context (forces, requirement ids), ≥ 2 options with trade-offs, decision, consequences (tests, operations, migration, cost), status; required for an M cell turned N/A, a deferred default REQ-NF, a contested AR.
- *Why:* unrecorded choices get re-litigated or silently reversed.
- *Check:* one-option or consequence-free ADRs are rejected; the `context.md` ADR index matches.
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-23** — List every suppression marker in production code (coverage exclusion, lint or warning disable, type ignore) with file, rule, reason and expiry, or "none"; none on money, time or access paths.
- *Why:* one exclusion attribute drops a unit from the no-untested-unit gate (GATE-2) with no test touched.
- *Check:* grep production code against the list; unlisted = Major (CODE rules).
- *Applies when:* always.
- *Provenance:* industry baseline

**ARCH-24** — Cut the build into ordered work packages `WP-n` of ≤ ~15 files, each compiling and running its fast suite alone (no later-WP reference) and listing files, generated migrations, the new public symbols it introduces (their test units are keyed to it, ORACLE-3) and the TCs it turns green; first the public surface the red tests compile against; Foundation includes the split of CI into Builder and Tester workflow files.
- *Why:* monolithic builds hit session limits and the orchestrator finished the code itself (LL-26).
- *Check:* trace_check gate2 finds ≥ 1 WP; each file in exactly one WP; no forward reference; the Builder commits per WP and resumes at the first uncommitted one.
- *Applies when:* always.
- *Provenance:* LL-26 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ARCH-25** — Add a module per declared profile (table); none is N/A while its interface exists. For cli, http-api and library adopt the public names `design.md` gives (commands and flags; resources, fields, error body and named examples; public symbols and error types) verbatim and bind each to its route, operation key or handler in the §5.0 binding table; a name that cannot be bound goes back to the Designer through the Manager, never renamed here.
- *Why:* web-only assumptions left CLI grammar and exit codes unspecified (LL-41); with neither agent allowed to name the public surface, design examples had no operations to bind to (LL-55, LL-56).
- *Check:* `context.md` profiles map to modules; every public name in `design.md` appears verbatim in §5.0 with its binding; examples run as consumer tests (DSN-18).
- *Applies when:* always; the naming clause for cli, http-api, library.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

| Profile | Module specifies |
|---|---|
| http-api | per operation: method, path, auth, schemas (server-owned fields marked), status per outcome, error codes; one error body (RFC 9457); stable pagination, max page size; versioning, deprecation; idempotency keys; contract file (e.g. OpenAPI, JSON Schema) |
| web-ui, native-app | screen → components → reads → client state; caching, refresh (no unspecified polling); formatter per value; principal switch clears data |
| cli | command tree → handler; precedence flag > env > file > default; stdout/stderr; exit codes; `--json` schema; TTY vs pipe |
| library | public signatures and errors; semver (what breaks), deprecation window, runtimes; public-surface snapshot |
| data-pipeline | dataset schemas (types, units, zones, nullability, keys); idempotent writes; duplicate, late data; replay, backfill, dead letter |
