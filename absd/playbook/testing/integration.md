# Integration Testing — Real Boundaries

Code **INTEG**. Tests that run the product's own composition root against the real things it owns at its boundary —
database engine, broker, filesystem, child processes, its own transport — with only external systems (those in
`EXTERNAL-FACTS.md`) and time replaced. Applicability (`absd/playbook/testing/strategy.md`): **M** web-ui, native-app,
http-api, cli, data-pipeline · **R** library (when it does I/O); chain tests **M** except library (**R**). Fakes are
FAKE rules in `absd/playbook/testing/contracts-and-fakes.md`, recorded facts EXT rules in
`absd/playbook/testing/external-facts.md`; access cells are ACCESS rules in `absd/playbook/testing/access-visibility.md`;
migration gates (from empty, previous-release upgrade, drift) are GATE-12 in
`absd/playbook/testing/ci-and-release-gates.md`; test-code hygiene is TCQ in `absd/playbook/testing/test-code.md`.

## Checklist

- [ ] The shipped entry point runs over its real transport against the production engine; nothing internal is mocked (INTEG-1)
- [ ] Stores are built only by the shipped migrations and seeders; one seeded fact asserted (INTEG-2)
- [ ] Throwaway store per run (per worker; managed: an ephemeral namespace), unique name, dropped after; no registry pull in CI (INTEG-3)
- [ ] Isolation strategy declared; tests assert only on their own data; doubles reset automatically (INTEG-4)
- [ ] Time only through an injectable clock; every time rule at T−ε, T, T+ε and long after (INTEG-5)
- [ ] Only external systems, time and randomness replaced; shipped settings; every other override has a reason (INTEG-6)
- [ ] Data arranged through public operations as the real actor; no minted tokens, no dev-auth (INTEG-7)
- [ ] Exact status/exit on every call; negative tests assert the error code; error bodies schema-checked (INTEG-8)
- [ ] Emitted codes = catalogue, both ways; clients map every code or show the cause-neutral generic message (INTEG-8)
- [ ] Audited actions: exactly one entry with action, actor, real actor, subject, time (INTEG-9)
- [ ] Every data flow: chain test from a recorded real payload to the persisted AND displayed outcome (INTEG-10)
- [ ] Every specified step of a flow asserted on the persisted end state (INTEG-11)
- [ ] Exactly-once rules raced; stale writes rejected; refused bulk writes change nothing (INTEG-12)
- [ ] Every job cycle, import, handler and retryable create run twice — no second effect (INTEG-13)
- [ ] Jobs: run-once seam; schedule, no overlap, crash → retry, poison item, flag off (INTEG-14)
- [ ] Notifications checked at a protocol-level fake: recipient, content, locale, exactly once (INTEG-15)

## Rules

**INTEG-1** — Boot the product's shipped entry point (the composition root production runs) and drive it through its real transport, against real instances of everything the product owns at its boundary: the production database engine and major version, the broker, the filesystem and child processes.
- *Why:* tests with mocked persistence never run the real schema, engine-specific queries, middleware order, serialization or the auth pipeline; code that no test ran shipped broken (LL-2).
- *Check:* the Auditor rejects integration tests that mock persistence, repositories or internal services, or swap in an in-memory engine; `test_plan.md` names the harness and every replaced dependency with its EXT id.
- *Applies when:* Integration is M or R in `TESTING.md`.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)
- Illustration: e.g. ASP.NET `WebApplicationFactory`, Spring `@SpringBootTest`, FastAPI `TestClient`, supertest for Express.

| Profile | Drive through | Real at the boundary |
|---|---|---|
| http-api; web-ui / native-app backends | the host over real HTTP (in-process or local port) | DB, broker, cache, filesystem, auth pipeline |
| native-app (client) | the app's data layer on an emulator or device | on-device database, platform storage, background scheduler |
| cli | a subprocess: argv, env, stdin, temp working dir and home | filesystem, config precedence (flag > env > file > default), exit code, child processes |
| library (I/O) | the public API of the built package | filesystem, loopback sockets |
| data-pipeline | the real stage entry point | store, broker topics, serialization format, schema registry |

**INTEG-2** — Build every test store only through the migrations and seeders the product ships and assert at least one fact they seed; never create the schema from the model, auto-create, or use an in-memory provider.
- *Why:* development and tests built the schema by auto-create, so a migration snapshot missing ~60% of the columns passed four audits; production migration would have broken (LL-21).
- *Check:* the Auditor greps the harness for schema-create shortcuts and migrate-off switches; a "schema from migrations" smoke TC exists; an environment that cannot run the migration tool makes the evidence BLOCKED (XCA-2), never an architecture change.
- *Applies when:* the product owns persistent state with a managed schema (incl. document stores with migrations and on-device databases).
- *Provenance:* LL-21 (KatenatsioTipster, 2026-10)
- Illustration: e.g. EF Core migrations, Flyway, Alembic, Prisma Migrate.

**INTEG-3** — Give each test run, and each parallel worker, its own throwaway store with a unique name, created at start and force-dropped after, runnable locally (disposable container) and in CI (a preinstalled service) without per-run registry pulls; a managed store the product runs on gets an ephemeral namespace per run in the real service instead (E2E-3).
- *Why:* CI broke with no code change when an image registry's anonymous pull limit was hit (LL-30); shared stores leak state between runs.
- *Check:* store names carry the run and worker id; no store survives the suite; the CI definition shows a service, not a pull per run.
- *Applies when:* the integration suite uses a store or broker.
- *Provenance:* LL-30 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)
- Illustration: e.g. Testcontainers or Docker Compose locally; GitHub Actions service containers or GitLab CI services.

**INTEG-4** — Declare the isolation strategy in `TESTING.md` and enforce it: one shared host per run with unique data per test, or per-test isolation (transaction rollback, schema or store per test) where cheap; tests assert only on data they created; global aggregates run in their own tenant or store, or assert relative to a snapshot taken during arrange; clock, fakes and environment reset automatically after every test.
- *Why:* a top-N visibility test passed only because the runner happened to order it before a test that created a larger value; manual resets in `finally` blocks leak the day one is forgotten.
- *Check:* the nightly run in randomized order with parallel workers passes (GATE rules in `absd/playbook/testing/gates.md`); the Auditor rejects global-count assertions in a shared store, fixed ports (ephemeral only) and unbounded waits; serial groups exist only for documented process-global state.
- *Applies when:* always.
- *Provenance:* industry baseline

**INTEG-5** — Let production read time only through an injectable clock (and ids and randomness through seams); in tests the clock is real by default, pinned per test and reset automatically; test every time rule just before, exactly at (expected side specified), just after and long after its boundary; take payload timestamps from the test clock, never the wall clock.
- *Why:* written criteria about midnight boundaries were never turned into tests (LL-45); a deadline read in the wrong zone opened 8 hours late (LL-1).
- *Check:* the Auditor greps production code for direct system-clock reads outside the clock implementation; `test_plan.md` has a boundary row per time rule; calendar instants per VAR-8; inferred states ("finished after N hours") get the same triple plus a far-future point.
- *Applies when:* a requirement mentions a deadline, expiry, schedule, period, date or "after X".
- *Provenance:* LL-45, LL-1 (KatenatsioTipster, 2026-10)
- Illustration: e.g. .NET `TimeProvider`, Java `java.time.Clock`, an injected `now()` in Python or TypeScript.

**INTEG-6** — Replace only what lies outside the product — systems in `EXTERNAL-FACTS.md`, time, randomness — with fakes that obey FAKE-1, and run the host with the settings it ships (production profile; a flag leaves its shipped default only in TCs of that flag state); any other override is limited to endpoints and credentials or carries an adjacent comment naming what it disables and the TC that tests that behaviour instead.
- *Why:* a test-only zone override hid an 8-hour defect (LL-1); suites ran under a development profile, so shipped defaults such as flags off and fail-closed startup were never exercised.
- *Check:* the Auditor lists every harness override; one without reason and pointer is Major; an override of a world fact breaks FAKE-4; a rate limit raised for the suite points to a dedicated limit+1 → refusal test on the shipped value.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

**INTEG-7** — Arrange data through the product's public operations, as the principal who would really perform them (accounts via the admin operation, sign-in via the real login, ids read back through the interface); write to storage directly only for states the interface cannot produce, each with a justification comment; never mint tokens or enable development auth shortcuts.
- *Why:* arranging through the interface proves onboarding works, survives schema changes and keeps authorization in the path.
- *Check:* the Auditor greps interface-level tests for direct inserts and auth-bypass switches; one shared builder per request type with defaults, no near-duplicate payloads.
- *Applies when:* integration, chain and end-to-end tests.
- *Provenance:* industry baseline

**INTEG-8** — Assert the exact outcome of every call, arrange steps included, and in every negative test also the machine-readable error code from `architecture.md`'s error catalogue — never only the human message, never "A or B" — and validate every error body against the catalogue's schema. Prove completeness both ways: a test compares the codes the product can emit (its error types or code registry, read from the built product) with the catalogue — an emitted code missing from the catalogue fails, as does an entry no TC raises; every client (web-ui, native-app, cli, SDK) maps each code to its designed message or shows the generic one, and a fallback chosen by status alone never names a specific cause.
- *Why:* same-status refusals with different causes let a test pass for the wrong reason; expected client errors were logged as server errors with stack traces (LL-15); completeness ran one way only, and a client guessing from the status named the wrong cause for an illegal transition (LL-57).
- *Check:* the Auditor flags status-only negative assertions and alternative-status oracles; one TC per catalogue entry, incl. "an expected 4xx produces no error-level log" (OPS rules in `absd/playbook/testing/nonfunctional.md`); the completeness TC reports both differences; each client has a mapping TC per code plus an unknown code → generic message. cli: exit-code table + stderr, stdout clean on error; library: documented error type + code; data-pipeline: dead-letter reason code.
- *Applies when:* always; the table below for http-api; the client part wherever a client shows catalogue errors.
- *Provenance:* LL-15 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

### HTTP status semantics (http-api)

| Status | Meaning (pinned once in the error catalogue) | Assert besides the status |
|---|---|---|
| 200 / 201 / 204 | read or update / created / done without body | body shape; location of the new resource |
| 400 | malformed: unparsable body, wrong type, format or range, missing field | error code + offending field |
| 401 | who are you: missing, invalid, expired or revoked credential | no data in the body |
| 403 | known principal, not allowed this kind of operation | error code, no data |
| 404 | does not exist **for you**: unknown id, other owner or tenant, flag off | identical to the unknown-id answer |
| 409 | state conflict: stale version, duplicate natural key, locked or closed state, busy | error code; state unchanged |
| 422 | well-formed request that breaks a business rule | the rule's error code |
| 429 | rate or quota limit | retry hint |
| 5xx | never expected: any 5xx fails the test (ACCESS-3, E2E-1) | — |

Error bodies follow one problem-details shape (RFC 9457): `application/problem+json`, `type` or code, `title`, `status`,
user-safe `detail`, trace id — never a stack trace, query text or internal path.

**INTEG-9** — For every audited action (at least every mutating admin action) assert exactly one audit entry — action, actor, real actor when impersonating, subject, time from the test clock, details — read through the interface an auditor would use, and assert that reads and refused actions write what the spec says (normally nothing).
- *Why:* a mutating call used as a read produced phantom audit rows (LL-42); an audit check by substring could not prove who acted.
- *Check:* `test_plan.md` matches the audited-action catalogue to TCs; assertions are field-level, incl. the impersonation variant (ACCESS-12).
- *Applies when:* the product has admin actions or audit, compliance or accountability requirements.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

**INTEG-10** — Give every data flow at least one chain test that starts from a recorded real boundary payload (FAKE-2), runs the shipped adapter, parser and domain logic, and asserts both the persisted state and the displayed or emitted outcome, with only the external system faked and inputs chosen so each plausible misreading (wrong field, zone or unit) produces a different outcome.
- *Why:* scoring tests fed the scorer its own scores, so the reader that took the half-time field for the final score was never in the path (LL-2).
- *Check:* Gate T maps every flow in `architecture.md` to a CHAIN TC; the Auditor rejects chains that bypass the adapter or inject pre-parsed values; the displayed outcome is read where the user reads it (read model, screen, CLI output, output dataset); data-pipeline chains also replay the batch and feed a duplicate and a late record per the data contract.
- *Applies when:* chain tests are M or R in `TESTING.md`.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**INTEG-11** — Test each step of every specified data flow on the persisted end state: every row inserted, updated or deleted, every counter and side effect `architecture.md` names, and the absence of what a step must remove.
- *Why:* "delete provisional rows, insert final rows" was half-implemented — provisional rows survived — because per-cycle checks named things, not steps (LL-51).
- *Check:* `test_plan.md` lists flow step × TC; the Auditor walks each step to an assertion.
- *Applies when:* `architecture.md` specifies multi-step flows.
- *Provenance:* LL-51 (KatenatsioTipster, 2026-10)

**INTEG-12** — Race every exactly-once or uniqueness rule (double submit, parallel approvals, a job racing a manual action, two writers on one record) behind a start barrier, never sleeps; a stale-version write is rejected (409 for http-api) with no lost update; a refused bulk or multi-row write leaves prior state byte-identical with the bad item first, middle and last.
- *Why:* concurrency paths are where "exactly once" quietly becomes "twice", and a partially applied bulk write is data loss.
- *Check:* one TC per exactly-once rule (concurrency technique: VAR rules in `absd/playbook/testing/test-design.md`); state snapshot compared before and after each refusal; races repeated N times in the nightly run; a message or event is emitted only if its transaction commits (crash between commit and publish tested).
- *Applies when:* concurrent writers, bulk writes or uniqueness rules exist.
- *Provenance:* industry baseline

**INTEG-13** — Run every job cycle, import, recompute, message or webhook handler, retryable create and create-by-natural-key twice and assert no second effect — state, reported change count, audit entries, outbound messages — plus the documented duplicate answer (same id, 409 or no-op); a retried request with the same idempotency key returns the original result.
- *Why:* idempotent re-runs were written as acceptance criteria and never tested (LL-45); jobs retry and pollers overlap, and double processing corrupts money and results.
- *Check:* a "run twice" TC per such operation; the Auditor rejects a job without one.
- *Applies when:* jobs, imports, retries, handlers or natural keys exist.
- *Provenance:* LL-45 (KatenatsioTipster, 2026-10)

**INTEG-14** — Give every background job a run-one-cycle seam that returns what it did, and test its schedule (next run at calendar boundaries), no overlap (a second instance while one runs does nothing), a crash mid-cycle followed by a retry that completes without duplicates, a poison item that does not block the rest, and full inertness with its flag off (no external calls, writes or messages); never wait on a real timer.
- *Why:* a flag-off path had no coverage, and turning the flag on at runtime did not rewire the provider bound at start-up (LL-23).
- *Check:* Gate T job rows; both flag states plus the toggle semantics recorded in the flag register (hot or restart).
- *Applies when:* schedulers, pollers, queues or recurring work exist.
- *Provenance:* LL-23 (KatenatsioTipster, 2026-10)

**INTEG-15** — Assert notifications and outbound messages at a local protocol-level fake (mail, push, webhook, topic) on an ephemeral port, decoding what actually left with an independent decoder: recipient, sender, subject and body in the recipient's locale, non-ASCII headers, attachments byte-exact, exactly one message per event across retries; cover server rejections (auth failed, recipient refused, unavailable) and every configured transport-security mode, with bounded waits.
- *Why:* unit tests only composed the message object; what leaves the process (encoding, headers, attachments, duplicates on retry) went unchecked.
- *Check:* Gate T notification rows (recipient, content, locale, no duplicates on retry); the Auditor rejects tests that inspect only the object before sending.
- *Applies when:* the product sends mail, push, webhooks, files or messages.
- *Provenance:* industry baseline
- Illustration: e.g. an in-test SMTP listener, Mailpit or smtp4dev for mail; a local HTTP receiver or WireMock for webhooks.
