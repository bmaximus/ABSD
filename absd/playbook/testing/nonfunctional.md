# Non-functional testing — accessibility, performance, resilience, visual, operability

Codes **A11Y** (accessibility), **PERF** (performance budgets), **RESIL** (behaviour when dependencies fail), **VIS**
(gallery, visual regression, golden output), **OPS** (first start, deploy, rollback, backup, docs, logs, alerts). Each
turns a REQ-NF — RULES rule 8's operability defaults included — into a measurable TC (STRAT-10). Related: DSN, LOC,
VAR-14 (fault injection), FAKE-7 (failure classes), GATE (`absd/playbook/testing/gates.md`).

## Checklist

- [ ] Every SCR × state × device class × theme scanned: 0 serious/critical (A11Y-1)
- [ ] Every journey keyboard-only, with designed focus and linked labels (A11Y-2)
- [ ] Rendered contrast per state and theme; zoom, reflow and reduced-motion runs (A11Y-3)
- [ ] CLI: no escape codes under `NO_COLOR` or a pipe; no colour-only meaning (A11Y-4)
- [ ] Budgets: metric, percentile, volume-max data, environment, threshold; breach = RED (PERF-1)
- [ ] Round trips constant from 1 item to volume max (no N+1); indexes used (PERF-2)
- [ ] Payload and bundle sizes budgeted; idle traffic = specified polling only (PERF-3)
- [ ] Timeouts on every outbound call; safe retries only, backoff with jitter (RESIL-1)
- [ ] Partial failure specified per batch and step; reruns complete without duplicates (RESIL-2)
- [ ] Dependency down: the rest works, dependents degrade, unsure decisions refuse (RESIL-3)
- [ ] Gallery of every SCR × state × device class × theme for Design QA (VIS-1)
- [ ] Protected screens match approved baselines; none regenerated to pass (VIS-2)
- [ ] CLI and data golden outputs compared exactly after declared normalisations (VIS-3)
- [ ] Shipped artifact boots on empty infrastructure with production configuration (OPS-1)
- [ ] Deployed digest = tested digest; runtime facts checked in it (OPS-2)
- [ ] Deploys verified (settled, version, smoke, journey, error rate); failure → safe rollback + DEF (OPS-3)
- [ ] Deploy scripts tested against a stateful platform fake; dry runs show no secret (OPS-4)
- [ ] Named storage; verified backup before risky deploys; restore drill per release (OPS-5)
- [ ] Fresh clone → running by following the docs literally (OPS-6)
- [ ] Expected client errors never logged at error level (OPS-7)
- [ ] Every alert fires once past its threshold; usage budgets per metered dependency (OPS-8)

## Rules

### Accessibility (A11Y)

**A11Y-1** — Scan every rendered state — each SCR × state × device class × theme of the component–state matrix, dialogs,
menus and errors open — with an automated WCAG 2.2 AA engine in the end-to-end run: 0 serious or critical violations,
every other one a TF, no rule disabled globally; an unscanned state is RED (GATE-1).
- *Why:* unnamed controls and unlinked form labels reached users because no scan ran (LL-19).
- *Check:* scanned states match the gallery index one-to-one (VIS-1); counts by impact in `test_report.md`.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)
- Illustration: e.g. axe-core, Pa11y (browser); Espresso checks (Android), XCUITest audits (iOS).

**A11Y-2** — Run every journey keyboard-only on each device class with a keyboard: Tab order follows `design.md`; focus
stays visible and lands after each step where the step says (DSN-7); dialogs take focus, trap it, close on Escape and
restore it (DSN-14); fields are reached by their linked label and controls by unique accessible names — an unlabeled
element is a TF, never a workaround selector (E2E-2).
- *Why:* unlinked labels shipped because the suite worked around them; a screen did not advance after a key action
  (LL-19).
- *Check:* one keyboard TC per UJ; positional or class selectors standing in for labels are findings.
- *Applies when:* web-ui; native-app where keyboard or switch access is declared.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**A11Y-3** — Check perception on the rendered product, not only on tokens: contrast of rendered text and controls in
every theme and in dimmed, disabled, focus and hover states; DSN-15's target-size, 200% zoom and 320 px reflow checks as
runs; a reduced-motion run with no non-essential motion in which every journey completes (DSN-6).
- *Why:* token ratios miss text over images and dimmed states; shipped targets were smaller than specified (LL-19).
- *Check:* zoom and reduced-motion projects in `TESTING.md` and CI; measured values in `test_report.md`.
- *Applies when:* web-ui, native-app (platform text size, reduce motion).
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**A11Y-4** — Keep cli output usable without colour or a terminal: with `NO_COLOR` set or stdout not a TTY, no ANSI
escape, cursor or spinner sequence; every coloured meaning also has a word or symbol; data on stdout, diagnostics and
progress on stderr; prompts only on a TTY (DSN-17).
- *Why:* colour-only status and escape codes in piped output defeat screen readers, logs and scripts.
- *Check:* subprocess TCs per command × {TTY, pipe, `NO_COLOR`} assert no escape bytes and the textual marker (VIS-3).
- *Applies when:* cli with human-facing output.
- *Provenance:* industry baseline

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

### Resilience (RESIL)

**RESIL-1** — Give every outbound call — external system, owned service, store — connect and total timeouts inside its
caller's budget, and retry only safe operations (idempotent, or creates with an idempotency key) with bounded attempts
and exponential backoff with jitter — never on refusals or invalid input, on throttling only after the advised wait.
Test on a controllable clock: a response held past the timeout (the specified failure class, FAKE-7, in time; nothing
hung or half-written; cancellation propagated), k failures then success (k + 1 calls, one effect), permanent failure
(max attempts, then the specified outcome).
- *Why:* a missing timeout turns one slow dependency into exhausted workers; unsafe retries duplicate effects;
  jitter-free retries synchronise clients into a storm.
- *Check:* `architecture.md`'s per-call timeouts and retries (ARCH-19) map to these TCs; second effects per VAR-13; the
  Auditor greps for unbounded waits.
- *Applies when:* any outbound dependency or retry (clients, jobs, consumers, scripts).
- *Provenance:* industry baseline

**RESIL-2** — Specify and test partial failure of every batch, multi-step and multi-target operation: all-or-nothing (a
failed item leaves the before-snapshot) or per-item isolation (good items committed, failures reported with reasons,
poison items set aside); a crash injected after each step leaves a state a rerun completes without duplicates.
- *Why:* a crash between steps leaves data no rerun repairs unless each step boundary is designed and tested.
- *Check:* a TC per step boundary and batch policy on the persisted end state (INTEG-11, INTEG-13).
- *Applies when:* batches, imports, multi-step flows, jobs, pipelines, deploy and migration scripts.
- *Provenance:* industry baseline

**RESIL-3** — When a dependency fails in any class of its fact sheet (FAKE-7), degrade what is safe and fail closed on
the rest: unrelated journeys keep working; dependent features show their designed state (DSN-13) — last-known data
labelled with its age (LOC-6) or "not available" with what to do; health says degraded; money, access and deadline
decisions lacking verified data refuse or stay pending (EXT-1), never act on a default, an empty answer or a guess.
- *Why:* external failures showed "Server error" (LL-11); an unverified zone shipped as a "safe default" (LL-1); a
  missing value silently became 0 (LL-44).
- *Check:* with each dependency down, independent journeys pass and dependent ones show their message, state unchanged;
  the Auditor flags defaults on money, access and time paths.
- *Applies when:* any dependency that can be unavailable.
- *Provenance:* LL-1, LL-11, LL-44 (KatenatsioTipster, 2026-10)

### Visual and golden output (VIS)

**VIS-1** — Capture the Design QA gallery at every Verify: one screenshot per SCR × state × device class × theme of
`design.md`'s component–state matrix, from the real build with production-volume data at the specified default scroll
and selection, named `SCR-n_<state>_<device>_<theme>.png` in `absd-project/working/evidence/tester/screens/` and indexed
in `test_report.md`.
- *Why:* raw enums, mixed number formats and truncated names were on screen while fidelity audits read code (LL-19).
- *Check:* index rows = matrix cells; a missing cell makes Design QA BLOCKED (DSN-20).
- *Applies when:* web-ui, native-app; cli and data-pipeline use golden output (VIS-3).
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**VIS-2** — Compare every protected screen (DSN-21) on every push with its Designer-approved baseline per device class,
theme and engine, rendered deterministically (bundled fonts, settled motion, pinned data and displayed time, masks only
where `design.md` marks content dynamic) within the pixel tolerance in `TESTING.md`; a difference fails with baseline,
actual and diff images; a baseline changes only with a Designer approval row, never regenerated to pass (GATE-6).
- *Why:* "no visual regression" was required every cycle and never automated (LL-53).
- *Check:* baseline hashes equal the approved rows in `design_review.md`; the Auditor diffs baseline changes since
  T-SHA.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10)

**VIS-3** — Pin cli and data outputs with owner-approved golden files (ORACLE-4): cli stdout, stderr and exit code per
command × {TTY, pipe, `NO_COLOR`, narrow, `--json`}; data-pipeline the output of a recorded input dataset (rows, keys,
types, units, zones, specified order); compare exactly after normalising only the volatile fields `TESTING.md` lists;
never regenerate to pass (GATE-6).
- *Why:* unreviewed snapshots copy whatever the code printed into the oracle.
- *Check:* an approval row per golden file (Designer for human output, Tester citing the spec otherwise); failing runs
  show the diff.
- *Applies when:* cli, data-pipeline (golden row triggered); library example output.
- *Provenance:* industry baseline

### Operability (OPS)

**OPS-1** — Boot the shipped artifact on empty infrastructure with production configuration — no schema, no data, fresh
named volumes, only secrets and endpoints supplied: it creates or migrates what it owns, reports ready on its version
within budget and serves one read; missing a required setting, it refuses to start, naming every missing key (FAKE-12).
Run it every push (GATE-12) and before a first deploy to a new environment.
- *Why:* the service crashed at start-up on a database that did not exist yet (LL-14).
- *Check:* the log shows the empty store, production profile and version; one removed key yields a refusal naming it.
- *Applies when:* every deployed or installed artifact (cli: a clean home; library: import in a clean environment).
- *Provenance:* LL-14 (KatenatsioTipster, 2026-10)

**OPS-2** — Build each deployable once and deploy the digest that was tested (image digest, package hash, binary
checksum): the push lane runs boot, smoke and the runtime-fact checks — zone data, locales, CA bundle, fonts (FAKE-12) —
on it, the release promotes it without rebuilding, and its version output names the source commit.
- *Why:* a release-time rebuild makes production the first test of the real artifact (LL-33); an image without zone data
  breaks a correct fail-fast setting (LL-14).
- *Check:* the released digest equals the green push run's; the release job has no build step.
- *Applies when:* the product deploys, publishes or installs an artifact.
- *Provenance:* LL-14, LL-33 (KatenatsioTipster, 2026-10)

**OPS-3** — Verify every deploy and roll back safely: wait until the platform reports the deploy settled; check health
and readiness on the new version — also on a same-version redeploy, where equal versions prove nothing; run the smoke
(E2E rules, `absd/playbook/testing/end-to-end.md`), a synthetic journey and an error-rate watch against the previous
version. A product failure (smoke exit 1, a failed journey, error rate over threshold) rolls back automatically — after
the platform settles, never writing while it is busy, onto a schema the previous release runs on (expand/contract,
ARCH-15) — re-verifies the previous version with the same checks, reports what it cannot undo and raises a DEF; a
refused rollback prints the manual command; "could not run" (exit 2) keeps the deploy, marked unverified (RED, GATE-1),
and alerts.
- *Why:* a 200-only health check passed an unchanged deploy beside a blank page (LL-32); a same-version redeploy was
  smoke-tested mid-restart and its rollback refused while the platform was busy (LL-7).
- *Check:* the deploy log shows each step with the expected version; a push-lane job runs the previous release on the
  new schema through its smoke; busy, timeout and refusal scenarios per OPS-4.
- *Applies when:* every deploy (cli, library: registry install, withdraw or yank; data-pipeline: canary or replay).
- *Provenance:* LL-7, LL-32 (KatenatsioTipster, 2026-10)

**OPS-4** — Test deploy, release and ops scripts against a stateful platform fake that deploys asynchronously and
refuses writes while busy (EXT-3), one scenario per outcome — healthy, product failure, platform failure, timeout, smoke
could not run, dry run, first deploy, already busy, bad credential, unsupported target, refused rollback, failed or
empty backup — asserting exact side effects and invariants across all scenarios (no write while busy, no secret in
output, nothing in use deleted); dry runs print setting names, never values, tested with planted secrets in every syntax
(quoted, `k=v`, connection strings, block scalars, headers).
- *Why:* a synchronous fake hid a refused rollback (LL-7); a secret reached a CI log through a dry-run diff (LL-8); a
  stateful fake made the deploy script testable (LL-39).
- *Check:* every script branch has a scenario; ephemeral ports, event-driven settling, no sleeps; incidents become
  scenarios first (ESC-1).
- *Applies when:* custom deploy, release, backup or ops automation exists.
- *Provenance:* LL-7, LL-8, LL-39 (KatenatsioTipster, 2026-10)

**OPS-5** — Protect persistent state: stateful services use named, backed-up storage (a manifest test rejects anonymous
volumes); a deploy that can change data first takes a verified backup (exit status, non-empty, restorable) or does not
start; retention keeps exactly N (tested at N − 1, N, N + 1); each release runs backup → wipe → restore on a scratch
environment and boots on the restored data with counts and sums reconciled.
- *Why:* a registry lost every image when its container was recreated on an anonymous volume (LL-34).
- *Check:* the manifest TC; drill evidence in the Mode R record; the backup-failure scenario (OPS-4).
- *Applies when:* the product owns persistent state.
- *Provenance:* LL-34 (KatenatsioTipster, 2026-10)

**OPS-6** — Prove "fresh clone → running from the docs": a scheduled job, and the Auditor at L7, follow the run guide
literally in a clean environment (no caches, no prior configuration, default development settings) and reach the
documented first success — sign-in, first command, first import; any deviation is a docs or configuration finding.
- *Why:* default development settings broke sign-in and the docs contradicted real defaults; nobody had tried a fresh
  clone (LL-22).
- *Check:* the transcript is attached per release; agreement TCs (FAKE-3) cover every documented key.
- *Applies when:* always (library: the documented install and first example).
- *Provenance:* LL-22 (KatenatsioTipster, 2026-10)

**OPS-7** — Assert log levels: across the access, validation and error-catalogue suites, expected client errors
(refusal, validation, not found, conflict) write no error-level entry or stack trace (ARCH-13); each server fault writes
one structured error entry with a correlation id and no secret or personal data, so alerts count real faults.
- *Why:* wrong passwords, refusals and validation errors were logged as server errors with stack traces (LL-15).
- *Check:* the harness fails on an unexpected error-level entry (E2E-1); a level TC per catalogue entry (INTEG-8).
- *Applies when:* always (cli: stderr and exit code; data-pipeline: dead-letter reasons).
- *Provenance:* LL-15 (KatenatsioTipster, 2026-10)

**OPS-8** — Test alerting: every alert in `architecture.md`'s observability section (ARCH-21) — error rate, health,
failed job, dead letters, and the usage and cost budget of each metered or capped dependency (paid API, OCR/LLM, mail,
SMS: a counter per period and principal, caps from `analysis.md`) — fires exactly once when a test drives its signal
past the threshold, names its first action and stays silent below it; per-user caps hold at cap − 1, cap and cap + 1,
and exhaustion fails closed with its designed message (RESIL-3); call counts per FAKE-8.
- *Why:* a quota ends a feature silently; an alert never seen firing stays silent when it matters.
- *Check:* each alert row maps to a firing TC and a below-threshold TC.
- *Applies when:* every deployed product; the usage part for paid, quota-limited or rate-limited dependencies.
- *Provenance:* industry baseline
