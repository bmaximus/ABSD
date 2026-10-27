# End-to-end tests — every interface profile, plus smoke

Code **E2E**. Proving the product through the interface its users touch, in each profile's form (STRAT-5): the error
tripwire, user-like selectors, device and zone projects, real time, simultaneous principals, smoke and regression
tests. The per-profile harnesses (E2E-11 to E2E-15) are in `absd/playbook/testing/end-to-end-profiles.md`. **M** in
every profile; never counted by coverage gates (GATE-2). Related: VAR, ORACLE, FAKE, EXT, INTEG, ACCESS, DSN, VIS, OPS.

## Checklist

- [ ] Any unexpected error signal fails the test; provoked ones allowlisted per test with a reason; never a 5xx (E2E-1)
- [ ] Shipped entry point; elements by role + name, label or text; an unreachable control is a product finding (E2E-2)
- [ ] Shipped build, own processes, fresh migrated store (managed: own namespace), shipped settings; only externals faked; no reuse in CI (E2E-3)
- [ ] Bound at Plan & Bind from `design.md` names, copy and public surface; RED first; a later mismatch is a finding (E2E-4)
- [ ] One type per test: functional, journey, regression or smoke; every UJ has a journey (E2E-5)
- [ ] One project per device class and audience rendering engine (web-ui phone ON unless waived); gallery captured; un-automatable triggers listed (E2E-6)
- [ ] Audience zone and locale pinned; one foreign zone/locale project; literal expected strings (E2E-7)
- [ ] Each time-driven lifecycle crossed once in real time against scheduled fake events (E2E-8)
- [ ] Cross-principal rules seen in simultaneous isolated sessions on the same device profile (E2E-9)
- [ ] Seed once via the public interface, never retried, hand-derivable; a new TC arranges its own data; mutating tests own theirs (E2E-10)
- [ ] Each profile's harness per `absd/playbook/testing/end-to-end-profiles.md` (E2E-11–E2E-15)
- [ ] Smoke: read-only (pipeline: canary into an isolated namespace, then dropped), version-aware, every tier, negative canary, least-privilege, exit 0/1/2 (E2E-16)
- [ ] A surface-level regression test per escaped defect, where it slipped (E2E-17)

## Rules

### Every profile

**E2E-1** — Fail every end-to-end test on any unexpected error signal — page or console error, 5xx, crash, non-zero
exit, unexpected stderr, error-level log, dead letter (table) — even when its own assertions pass: one shared harness
(auto fixture, wrapper or runner hook) watches every session, process and log the test opens and fails it at teardown. A
test provoking an error on purpose allowlists it for itself (narrow pattern + reason); a refusal the interface handles
(a 4xx shown as the designed message) is no signal; a 5xx is never allowlisted (INTEG HTTP status table), an error-level
log line only where the error catalogue gives the provoked failure that level (ARCH-13).
- *Why:* assertions check only what their author thought of; a shared tripwire caught silent page errors and 500s behind
  correct screens (LL-37); refusals logged as server errors went unseen (LL-15).
- *Check:* lint: e2e files take the test function only from the harness; Foundation negative control (planted console
  error, stderr line, error log → red); the Auditor reviews each allowlist entry.
- *Applies when:* always.
- *Provenance:* LL-15, LL-37 (KatenatsioTipster, 2026-10)

| Profile | Signals (all profiles: an error-level line in any log of a process the test started) |
|---|---|
| web-ui | page or console error; ≥ 500 from the product's origin |
| native-app | crash, hang, unhandled exception |
| http-api | ≥ 500; a body off the contract or error catalogue |
| cli | unexpected exit code or stderr; a stack trace anywhere |
| library | unexpected exception, warning or console output |
| data-pipeline | dead letter, unexpected reject, input ≠ output + rejected |

**E2E-2** — Drive the system as its user does, through the shipped artifact's real entry point — a browser or device,
HTTP from outside, the cli as a subprocess, the installed package, the pipeline's real trigger (STRAT E2E forms): find
elements by role + accessible name, label or visible text exactly as `design.md` names them; a test id only for a
container with no role or name, with a reason; never a CSS class, XPath, index or internal id; never a dev server,
mocked API, in-process host or `main`, the source tree or a stage called as a function. A control unreachable by role
and name is an accessibility defect of the product (a finding), not a reason for a structural selector. After each
navigation assert real content (shell mounted, main region with meaningful text); wait on states, never fixed time (TCQ,
`absd/playbook/testing/test-code.md`).
- *Why:* tests fed a computation its own inputs, so a component misreading a provider field was on no tested path
  (LL-2); a suite working around unlinked labels hid an accessibility defect (LL-19).
- *Check:* lint bans class, XPath and index selectors (reasoned allowlist); every name used is in `design.md`; each
  E2E home starts the built artifact (STRAT-5).
- *Applies when:* always.
- *Provenance:* LL-2, LL-19 (KatenatsioTipster, 2026-10)

**E2E-3** — Run against the real stack: shipped build, the product's own processes, the production store engine on a
fresh store per run built by shipped migrations (INTEG-2, INTEG-3). Fake only external systems, answering like them
(FAKE-1) at production volume in adversarial order (VAR-7), exposing ground truth (FAKE-11). Use shipped settings
(FAKE-4) plus a reasoned override allowlist (endpoints, credentials). A managed store (hosted database, warehouse,
object storage) is a real store, never faked: each run gets its own ephemeral namespace in the real service (schema,
dataset or prefix), built by shipped migrations and dropped after; its behaviour facts (quotas, consistency, dialect)
have an `EXTERNAL-FACTS.md` section (EXT-3). A documented reuse mode attaches to a running stack for local iteration;
CI never enables it.
- *Why:* a brand-new store exposed a start-up crash (LL-14); an assumed-zone fake plus a test-only zone override hid
  deadlines 8 h late (LL-1); a three-item fake hid a phone defect (LL-4); a managed warehouse was neither a store nor
  an external system (LL-56).
- *Check:* CI builds once and runs e2e on that artifact; e2e environment = override allowlist; no reuse flag in CI;
  managed-store namespaces carry the run id and none survives the run.
- *Applies when:* always; the store parts when the product owns persistent state.
- *Provenance:* LL-1, LL-4, LL-14 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**E2E-4** — Write end-to-end tests at Plan & Bind, before the interface exists: names, copy, focus targets and formats
verbatim from `design.md` — for cli, http-api and library also the public surface it names (commands and flags;
resources, fields, error bodies, example requests and responses; public symbols and error types), each example bound as
a TC; routes and operation keys as `architecture.md` §5.0 binds those names. Each in-scope UJ, SCR × state, command,
public symbol and pipeline flow gets a TC, RED because the element, route, command or output is missing (ORACLE-3).
A later mismatch is design drift (finding → Builder) or a design defect (spec defect → Designer); a selector or literal
changes only by amendment (ORACLE-2).
- *Why:* tests written after the code by its author cost every cycle a second build (LL-29); measurable criteria
  nobody turned into tests passed audits (LL-45).
- *Check:* Gate T red evidence per e2e TC; every public name a test uses is in `design.md`; the Auditor diffs e2e
  selectors and literals since the first T-SHA with amendments.
- *Applies when:* Plan & Bind (Modes F, S); Reproduce (Mode D).
- *Provenance:* LL-29, LL-45 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

**E2E-5** — Give each end-to-end test one type, by folder and tag (table). A journey takes one business object from
creation to its terminal state through every principal touching it, steps named as business sentences, each hand-off
asserted from the receiver's view; every UJ has one on each device class it runs on (E2E-6).
- *Why:* rules that each passed alone gave wrong prize positions together (LL-9); a capability nobody wrote down had no
  journey that could fail (LL-5).
- *Check:* trace_check gateT (UJ → TC); lint rejects untagged tests, journeys without steps, smoke that writes.
- *Applies when:* always.
- *Provenance:* LL-5, LL-9 (KatenatsioTipster, 2026-10)

| Type | Scope | Principals, data | Asserts |
|---|---|---|---|
| Functional | one screen, command, operation | one + negative observer; arrange via API | validation, persistence (VAR-20), absence |
| Journey | a lifecycle across its UJ steps | every one it touches, simultaneous; fresh actors | hand-offs, transitions, money, audit |
| Regression | one escaped defect (E2E-17) | as it happened, where it slipped | the behaviour, or mechanism + undo |
| Smoke | alive on the expected version | anonymous + least-privilege; read-only | version, render, negative canary |

### Devices, time, principals, data

**E2E-6** — Run one project per device class in `context.md` (VAR-6): web-ui desktop and phone (touch, small viewport;
ON unless the user waived it), tablet and landscape when declared, and one per rendering engine the `context.md`
audiences use (e.g. Chromium, Gecko, WebKit), the phones' engine in the push lane; every journey on every class except one the user
waived for it in brd Decisions (DSN-8); helpers work on every project. Test each input mode on that mode, asserting the
user outcome: hover-free controls, swipes past scroll edges, on-screen keyboard, touch targets (DSN-9, DSN-10). When
automation cannot produce a trigger (native browser gesture, OS dialog), assert the preventing mechanism and its undo
(lock → unlock) and list the trigger for real devices (EXPL-9). These projects capture the VIS-1 gallery through the
real interface: each SCR × state × device class × theme reached by a test, never by stubbed rendering.
- *Why:* desktop-only runs let a swipe reload the app on phones and a hover-only control ship (LL-4, LL-16); one
  browser engine emulated every phone until release (LL-57).
- *Check:* CI projects = `context.md` classes × engines; each UJ runs per listed class; mechanism tests cite an EXPL-9
  item.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**E2E-7** — Pin the audience's locale and display zone (Locale & Time Profile) in runner configuration, never machine
defaults, and run one project whose client zone and locale differ on purpose (negative UTC offset with DST, another
number format) over every test showing or bucketing time, dates or numbers. Expected strings are literals from
`design.md` (LOC-15) or a fake's ground truth, never formatted by the product or the client.
- *Why:* a clock labelled UTC showed client time, invisible in the audience's own zone (LL-13); date bugs appear when
  UTC and local dates differ (LL-40).
- *Check:* runner config shows both; the foreign project runs per push (STRAT-7) and nightly (STRAT-8).
- *Applies when:* any profile showing time, dates or numbers to people.
- *Provenance:* LL-13, LL-40 (KatenatsioTipster, 2026-10)

**E2E-8** — Cross every user-visible time-driven lifecycle (deadline, lock, expiry, schedule) once end to end in real
time, on data whose boundary falls a short known time ahead — from the fake source's schedule (e.g. an event every 20 s
for an hour, non-2xx when exhausted) or created through the public interface with a near deadline: take a boundary at
least the pre-boundary steps' budget ahead, act, wait to the boundary plus a stated margin, re-read, assert every
observer. Exact instants (T−ε, T, T+ε) and long horizons (DST, month, season) stay on the movable clock below e2e
(INTEG-5, VAR-8); never fake one clock of several.
- *Why:* real-time journeys proved locking and settlement through every clock in the chain (LL-38).
- *Check:* the plan says how each side of each time rule is crossed; the wait is commented "time is the subject".
- *Applies when:* deadlines, expiries, locks or schedules users see.
- *Provenance:* LL-38 (KatenatsioTipster, 2026-10)

**E2E-9** — Test every rule where one principal's action changes what another sees or may do with simultaneous
sessions — one isolated context per principal (own cookies, storage, credentials) inheriting the project's device
profile, zone and locale, watched by E2E-1, closed at teardown — asserting the positive and negative observer at each
hand-off and entitlement changes in the affected, already-open session (VAR-10, ACCESS-11).
- *Why:* free accounts got paid content that only another principal's view exposed (LL-10).
- *Check:* an observer column per journey step; a visibility rule proven by one principal fails Gate T.
- *Applies when:* more than one principal, owner or tenant.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**E2E-10** — Seed shared reference data once per run, before every project, through the public interface as the real
principals would (INTEG-7, first-run bootstrap included): never retried, fails the whole run, idempotent; its data makes
each expected order, count, truncation and total derivable by hand, exported as named constants. Arrange non-subject
data via the public API, act on the subject via the interface. Data a TC added this cycle needs is arranged in that
TC, never in the shared seed: a seed calling an operation not built yet fails the whole run before its work package
lands (red by work package, ORACLE-3). A mutating test owns its data (fresh principals, unique names per attempt,
uniqueness leftovers cleaned first); no test writes shared seed data.
- *Why:* a half-seeded store yields confusing failures; direct inserts skip the validation and bootstrap users hit; a
  seed needing a new operation turned every older test red at T-SHA (LL-57).
- *Check:* seed retries 0, every project depends on it; the suite passes twice on one stack; the Auditor flags
  assertions not derivable from the seed and seed additions made for a TC of the cycle.
- *Applies when:* tests share data or mutate state.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)

### Smoke and regression

**E2E-16** — Design the smoke suite that OPS-3 runs after every deploy, and run it on the CI stack every push too:
read-only — a data-pipeline's one write is a canary record or batch through the real trigger into an isolated
namespace, reconciled at the output, then dropped; assert the build id the deploy expects (a bare 200 proves
nothing); reach every tier without writing — real content renders, the API answers through the public origin, the
store answers a negative canary (a wrong sign-in refused with the designed message); behind sign-in, render the main screens as a dedicated least-privilege account. Exit **0**
pass · **1** product failed · **2** could not run: the harness maps its own failures (missing tool, network, install,
missing smoke credential) to 2, never to 0, 1 or a skip; OPS-3 turns 1 into rollback and 2 into an unverified, RED
release (GATE-1). cli, library: install from the real channel, run the version and one read-only call; other forms per
the STRAT matrix.
- *Why:* a same-version redeploy let smoke hit the site mid-restart and the rollback was refused (LL-7); a
  version-blind health check passed an unchanged deploy while the page was blank (LL-32); "read-only" contradicted
  the pipeline's canary (LL-56).
- *Check:* the Auditor greps smoke for writes outside the canary namespace and for silent-pass branches; the harness's
  exit mapping has tests (tool or network missing → 2, product down → 1; GATE-8); smoke links an operations
  requirement.
- *Applies when:* every profile (post-deploy smoke is M).
- *Provenance:* LL-7, LL-32 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**E2E-17** — For every escaped defect that reached a user-visible surface (screen, output, response, published
package), add a regression test at that surface — on the device class, zone, locale and data volume where it slipped
— besides the lower-level test ESC-1 requires; title it with the behaviour and `(DEF-n, YYYY-MM-DD: what broke)`,
link the requirement it protects, and show it RED on the pre-fix build (Mode D Reproduce).
- *Why:* a phone reload, a console refetching every second and a filter overwritten by a late reload each reached a
  screen (LL-4, LL-12, LL-20).
- *Check:* each `ESCAPED-DEFECTS.md` row that reached a surface names an existing e2e TC; red evidence at the pre-fix product SHA.
- *Applies when:* every escaped defect, from the first.
- *Provenance:* LL-4, LL-12, LL-20 (KatenatsioTipster, 2026-10)
