# Load and compatibility — performance budgets, load, previous versions

Codes **PERF** (performance budgets, round trips per operation, payload budgets; load, stress and soak) and **COMPAT**
(compatibility of the product's own interfaces: published-contract snapshot diff, previous clients, previous stored and
queued data). Each turns a REQ-NF — or a default trigger named in *Applies when* — into a measurable TC (STRAT-10) whose
threshold is indexed in `TESTING.md` §2. Related: VAR-7 (volume), VAR-17 (idle), E2E-14 (library package), GATE-12
(migration gates), OPS-3 (rollback onto the new schema).

## Checklist

- [ ] Budgets: metric, percentile, volume-max data, environment, threshold; breach = RED (PERF-1)
- [ ] Round trips constant from 1 item to volume max (no N+1); indexes used (PERF-2)
- [ ] Payload and bundle sizes budgeted; idle traffic = specified polling only (PERF-3)
- [ ] Nightly load at the stated concurrency (p95, error rate 0); stress past it; soak ≥ 30 min flat (PERF-4)
- [ ] Published contracts snapshotted; a breaking diff needs a MAJOR version or an ADR (COMPAT-1)
- [ ] The previous release's clients pass against the new server (COMPAT-2)
- [ ] The new version reads N-1 stored and queued data; during a rollout N-1 reads what N writes (COMPAT-3)

## Rules

### Performance (PERF)

**PERF-1** — Turn every performance REQ-NF and every list, search, report or batch operation into a budget TC — metric,
percentile, dataset (Data Volume Profile max, adversarial order, VAR-7), environment, threshold from `analysis.md`
(none = a spec defect at Plan & Bind) — measured where the user waits (http-api p95 per operation; web-ui and
native-app time to usable content and input response on the throttled phone project; cli wall time; library time per
call; data-pipeline throughput and lag) after warm-up over a stated sample: per push a smoke of deterministic proxies
and a generous ceiling, nightly the full sample on a fixed environment; a breach is RED, never re-run to pass (GATE-6).
- *Why:* performance-at-volume criteria passed audits by code reading (LL-45); three-item fixtures hid what volume broke
  (LL-4).
- *Check:* budget rows in `test_plan.md` carry all five fields; reports show sample, percentile, environment and trend.
- *Applies when:* a triggered Performance row; always for lists, search, reports and batches.
- *Provenance:* LL-4, LL-45 (KatenatsioTipster, 2026-10)

**PERF-2** — Count round trips to stores and owned services per list, search, report and batch operation at 1 item and
at the Data Volume Profile max, and assert the specified constant at both sizes (no N+1); at max volume, assert each
budgeted query uses the index `architecture.md` names (ARCH-15) on the production engine.
- *Why:* per-row queries and missing indexes stay invisible at fixture size.
- *Check:* a count assertion per operation via a statement interceptor or log; a query-plan check nightly.
- *Applies when:* the product owns a store or calls owned services per item.
- *Provenance:* industry baseline

**PERF-3** — Budget what crosses the wire: response bytes at max volume with the maximum page size enforced, initial and
per-route bundle size (web-ui), package size (library); and idle traffic from the network log (VAR-17): no request on a
settled screen except specified polling, counted exactly per interval (DSN-12).
- *Why:* consoles re-fetched every second while idle and wiped a dialog being typed in (LL-12).
- *Check:* size assertions per operation and build; an idle TC per screen with timers, window > its longest timer.
- *Applies when:* http-api, web-ui, native-app, library; the idle part wherever timers or polling exist.
- *Provenance:* LL-12 (KatenatsioTipster, 2026-10)

**PERF-4** — Run a scripted load test nightly on a fixed environment, with data at the Data Volume Profile max (VAR-7)
and principals arranged as users would (INTEG-7), driving the public interface: **load** at the stated concurrency and
arrival rate for a stated duration (p95 and p99 per operation within budget, error rate 0, no timeout); **stress**
ramped past it to saturation (the specified shedding — refusal with its designed outcome, back-pressure or queueing —
never a crash, lost or corrupted data or an unhandled error; recovery once the load drops); **soak** at the stated load
for at least 30 minutes (memory, handles, threads, connection pools and queue depth flat after warm-up; latency without
an upward trend). Thresholds live in `TESTING.md` §2; a breach is RED, never re-run to pass (GATE-6).
- *Why:* single-request budgets at maximum data volume never tested concurrent users, saturation or resource growth
  over time (LL-57).
- *Check:* each load row in `test_plan.md` names concurrency, arrival rate, duration, environment and thresholds; the
  nightly report shows percentiles, error rate and resource curves with the trend; a run that did not happen is RED
  (GATE-1).
- *Applies when:* a REQ-NF on concurrency, throughput or capacity; by default every deployed service (http-api, the
  backend of a web-ui or native-app, a streaming data-pipeline), with the expected concurrency from `analysis.md`
  (none = a spec defect at Plan & Bind).
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)
- Illustration: e.g. k6, Gatling or Locust for the scripts; the runtime's own metrics or a profiler for the soak curves.

### Compatibility (COMPAT)

**COMPAT-1** — Snapshot every published contract from the built artifact into the test tree — the HTTP schema (e.g. an
OpenAPI document or a GraphQL schema), message, event and file schemas, cli help, flags, exit codes and `--json`
schemas, a library's public API — and diff it on every push against the last release's snapshot: a breaking change
(an element removed or renamed, a type narrowed, an input newly required, a meaning, status or exit code changed) fails
unless the MAJOR version changes or an ADR accepts it with its migration path; an additive change updates the snapshot
in the same commit.
- *Why:* only libraries diffed their public surface; a renamed field or exit code breaks every consumer while the
  product's own tests, updated with it, stay green (LL-57).
- *Check:* the diff job names each breaking element; snapshots are generated from the artifact, never written by hand;
  the Auditor matches each accepted break to a MAJOR version or an ADR.
- *Applies when:* the product publishes an interface others consume: http-api, cli, library, data-pipeline outputs,
  and the API behind web-ui or native-app clients.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)
- Illustration: e.g. oasdiff or openapi-diff for HTTP schemas; API Extractor, japicmp or cargo-semver-checks for
  library surfaces.

**COMPAT-2** — Run the previous release's client suite against the new server, nightly and before every release: the
last release's built web client (still cached in open browsers), each still-supported installed app version, the N-1
SDK or cli. Its journeys and contract checks pass unchanged, or the break is a COMPAT-1 MAJOR change whose designed
upgrade path (forced-update screen, versioned route, deprecation notice) is itself tested.
- *Why:* the new server was tested only with the new client; a tab holding the old bundle or an installed app version
  breaks on release day (LL-57).
- *Check:* a job runs the last release tag's client tests and built client against the candidate server; the supported
  version window is stated in `context.md` or an ADR.
- *Applies when:* clients are not updated atomically with the server: web-ui (cached bundles), native-app, published
  SDKs or clis, other teams' consumers.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)

**COMPAT-3** — Prove that the new version reads every persisted or queued format the previous one wrote: fixtures
produced by the N-1 release's build — never hand-written — for stored documents and files, serialised cache entries,
local state and configuration (cli, library, native-app), and messages and events left in queues and topics, each read
with the specified result (migrated, defaulted, or refused with its designed message); while a rolling deploy runs both
versions, the N-1 consumer reads what N writes, or an ADR names the cut-over. Schema migrations: GATE-12.
- *Why:* consumers were tested only on data their own version wrote; messages in flight and files on disk outlive the
  release that wrote them (LL-57).
- *Check:* one fixture per format and version in the supported window, with capture metadata; a new format version adds
  its fixture in the same change; the read TCs run per push.
- *Applies when:* the product persists serialised data outside a migrated schema (cli, library: persistent local state,
  cache, config), or produces or consumes queued messages or events.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)
