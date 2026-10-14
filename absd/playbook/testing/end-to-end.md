# End-to-end tests — every interface profile, plus smoke

Code **E2E**. Proving the product through the interface its users touch, in each profile's form (STRAT-5): the error
tripwire, user-like selectors, device and zone projects, real time, simultaneous principals, per-profile harnesses,
smoke and regression tests. **M** in every profile; never counted by coverage gates (GATE-2). Related: VAR, ORACLE,
FAKE, EXT, INTEG, ACCESS, DSN, VIS, OPS.

## Checklist

- [ ] Any unexpected error signal fails the test; provoked ones allowlisted per test with a reason; never a 5xx (E2E-1)
- [ ] Shipped entry point; elements by role + name, label or text; an unreachable control is a product finding (E2E-2)
- [ ] Shipped build, own processes, fresh migrated store, shipped settings; only externals faked; no reuse in CI (E2E-3)
- [ ] Bound at Plan & Bind from `design.md` names and copy; RED first; a later mismatch is a finding (E2E-4)
- [ ] One type per test: functional, journey, regression or smoke; every UJ has a journey (E2E-5)
- [ ] One project per device class, phone ON unless waived; gallery captured; un-automatable triggers listed (E2E-6)
- [ ] Audience zone and locale pinned; one foreign zone/locale project; literal expected strings (E2E-7)
- [ ] Each time-driven lifecycle crossed once in real time against scheduled fake events (E2E-8)
- [ ] Cross-principal rules seen in simultaneous isolated sessions on the same device profile (E2E-9)
- [ ] Seed once via the public interface, never retried, hand-derivable; mutating tests own their data (E2E-10)
- [ ] native-app: release build per platform × device class; interruptions covered (E2E-11)
- [ ] http-api: built artifact driven from another process; contract-checked bodies; log watched (E2E-12)
- [ ] cli: subprocess; TTY and pipe, `NO_COLOR`, width; exact stdout, stderr, exit code (E2E-13)
- [ ] library: built package in a clean environment per runtime; public surface only (E2E-14)
- [ ] data-pipeline: recorded real-volume run + replay, duplicate, late, malformed, empty; counts reconcile (E2E-15)
- [ ] Smoke: read-only, version-aware, every tier, negative canary, least-privilege, exit 0/1/2 (E2E-16)
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
(FAKE-4) plus a reasoned override allowlist (endpoints, credentials). A documented reuse mode attaches to a running
stack for local iteration; CI never enables it.
- *Why:* a brand-new store exposed a start-up crash (LL-14); an assumed-zone fake plus a test-only zone override hid
  deadlines 8 h late (LL-1); a three-item fake hid a phone defect (LL-4).
- *Check:* CI builds once and runs e2e on that artifact; e2e environment = override allowlist; no reuse flag in CI.
- *Applies when:* always; the store parts when the product owns persistent state.
- *Provenance:* LL-1, LL-4, LL-14 (KatenatsioTipster, 2026-10)

**E2E-4** — Write end-to-end tests at Plan & Bind, before the interface exists: names, copy, focus targets and formats
verbatim from `design.md`; routes, commands, flags and public symbols from `architecture.md`. Each in-scope UJ, SCR ×
state, command, public symbol and pipeline flow gets a TC, RED because the element, route, command or output is
missing (ORACLE-3). A later mismatch is design drift (finding → Builder) or a design defect (spec defect → Designer); a
selector or literal changes only by amendment (ORACLE-2).
- *Why:* tests written after the code by its author cost every cycle a second build (LL-29); measurable criteria
  nobody turned into tests passed audits (LL-45).
- *Check:* Gate T red evidence per e2e TC; the Auditor diffs e2e selectors and literals since T-SHA with amendments.
- *Applies when:* Plan & Bind (Modes F, S); Reproduce (Mode D).
- *Provenance:* LL-29, LL-45 (KatenatsioTipster, 2026-10)

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
ON unless the user waived it), tablet and landscape when declared; every journey on every class except one the user
waived for it in brd Decisions (DSN-8); helpers work on every project. Test each input mode on that mode, asserting the
user outcome: hover-free controls, swipes past scroll edges, on-screen keyboard, touch targets (DSN-9, DSN-10). When
automation cannot produce a trigger (native browser gesture, OS dialog), assert the preventing mechanism and its undo
(lock → unlock) and list the trigger for real devices (EXPL-9). These projects capture the VIS-1 gallery through the
real interface: each SCR × state × device class × theme reached by a test, never by stubbed rendering.
- *Why:* desktop-only runs let a swipe reload the app on phones and a hover-only control ship (LL-4, LL-16).
- *Check:* CI projects = `context.md` classes; each UJ runs per listed class; mechanism tests cite an EXPL-9 item.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10)

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
data via the public API, act on the subject via the interface. A mutating test owns its data (fresh principals, unique
names per attempt, uniqueness leftovers cleaned first); no test writes shared seed data.
- *Why:* a half-seeded store yields confusing failures; direct inserts skip the validation and bootstrap users hit.
- *Check:* seed retries 0, every project depends on it; the suite passes twice on one stack; the Auditor flags
  assertions not derivable from the seed.
- *Applies when:* tests share data or mutate state.
- *Provenance:* industry baseline

### Profile harnesses

**E2E-11** — native-app: install the release-configuration build, signed as shipped, on emulators and devices per
platform × device class × supported OS (e.g. XCUITest, Espresso, Appium, Maestro), locating elements by the
accessibility identifiers and labels `design.md` names; cover background and resume, process death and restore,
rotation, permissions granted and denied, offline and flaky network, deep links, notification taps, on-screen
keyboard, safe areas, both themes, large text.
- *Why:* phone-only defects reached users while one device class ran (LL-4); debug builds hide shipped behaviour.
- *Check:* CI device matrix = `context.md`; release configuration under test; interruption cases per journey.
- *Applies when:* native-app.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**E2E-12** — http-api: start the built image or binary with shipped configuration and drive it from another process
over the network as a consumer: documented versioned routes only; the real sign-in flow, never minted tokens; each
status, header and body checked against the HTTP contract, each error body against the error catalogue; pagination
walked to the end at Data Volume Profile max in stable order; journeys across principals; service log watched (E2E-1).
- *Why:* free accounts got paid data in an API response no screen showed (LL-10); refusals were logged as errors
  (LL-15).
- *Check:* the job targets the started artifact, not a test host; contract checks on every call; log capture on.
- *Applies when:* http-api, and the service behind a web-ui or native-app.
- *Provenance:* LL-10, LL-15 (KatenatsioTipster, 2026-10)

**E2E-13** — cli: run the built or installed executable as a subprocess with explicit args, stdin, environment and a
clean home and config directory per test; assert stdout, stderr, exit code (DSN-17 table; stderr empty unless
expected; never a stack trace) and files written. Run each command under a pseudo-terminal and through a pipe
(colour, prompts, progress only on a TTY; destructive commands need `--yes` without one), with `NO_COLOR` set and
unset, at narrow and wide widths; `--json` matches its schema; an interrupt exits with the documented code and cleans
up; one run per supported OS and shell (VAR-6); golden human output per VIS-3.
- *Why:* in-process calls skip argument parsing, terminal detection and exit-code mapping — the cli's real interface.
- *Check:* pty and pipe modes in the harness; three streams asserted per case; OS/shell matrix = `context.md`.
- *Applies when:* cli.
- *Provenance:* industry baseline

**E2E-14** — library: build the distributable exactly as the release does, install it into a fresh isolated
environment per supported runtime (lowest and highest allowed dependency versions too) and run consumer tests using
only the public surface: documented examples run as tests (DSN-18), errors arrive as documented types, no unexpected
warning. Check package contents (licence, types; no tests, secrets, build leftovers) and diff the public API with
the previous release: a break without a MAJOR version is a finding.
- *Why:* source-tree suites pass while the package lacks files, leaks private names or breaks on a runtime.
- *Check:* no source path importable in the test environment; runtime matrix = `context.md`; API diff reported.
- *Applies when:* library.
- *Provenance:* industry baseline

**E2E-15** — data-pipeline: run the real entry point over a recorded real-volume dataset (dated, scrubbed, Data Volume
Profile max; FAKE-6) against real stores and brokers, then: the input replayed (identical output, no duplicates),
duplicated and out-of-order records, records past the contract's lateness window, malformed records (quarantined with
a reason), an empty input. Reconcile counts and sums (input = output + rejected); compare output record by record with
an Analyst-approved golden dataset (ORACLE-4, VIS-3) or the source of truth, zones and units included.
- *Why:* a provider-zone time read as UTC and a half-time field read as the final result were data-contract defects
  only real recorded input exposes (LL-1, LL-2).
- *Check:* dataset capture metadata; a reconciliation assertion per run; all six input cases present.
- *Applies when:* data-pipeline, and batch imports or event consumers in any profile.
- *Provenance:* LL-1, LL-2 (KatenatsioTipster, 2026-10)

### Smoke and regression

**E2E-16** — Design the smoke suite that OPS-3 runs after every deploy, and run it on the CI stack every push too:
read-only; assert the build id the deploy expects (a bare 200 proves nothing); reach every tier without writing — real
content renders, the API answers through the public origin, the store answers a negative canary (a wrong sign-in refused
with the designed message); behind sign-in, render the main screens as a dedicated least-privilege account. Exit **0**
pass · **1** product failed · **2** could not run: the harness maps its own failures (missing tool, network, install,
missing smoke credential) to 2, never to 0, 1 or a skip; OPS-3 turns 1 into rollback and 2 into an unverified, RED
release (GATE-1). cli, library: install from the real channel, run the version and one read-only call; other forms per
the STRAT matrix.
- *Why:* a same-version redeploy let smoke hit the site mid-restart and the rollback was refused (LL-7); a
  version-blind health check passed an unchanged deploy while the page was blank (LL-32).
- *Check:* the Auditor greps smoke for writes and silent-pass branches; the harness's exit mapping has tests (tool
  or network missing → 2, product down → 1; GATE-8); smoke links an operations requirement.
- *Applies when:* every profile (post-deploy smoke is M).
- *Provenance:* LL-7, LL-32 (KatenatsioTipster, 2026-10)

**E2E-17** — For every escaped defect that reached a user-visible surface (screen, output, response, published
package), add a regression test at that surface — on the device class, zone, locale and data volume where it slipped
— besides the lower-level test ESC-1 requires; title it with the behaviour and `(DEF-n, YYYY-MM-DD: what broke)`,
link the requirement it protects, and show it RED on the pre-fix build (Mode D Reproduce).
- *Why:* a phone reload, a console refetching every second and a filter overwritten by a late reload each reached a
  screen (LL-4, LL-12, LL-20).
- *Check:* each `ESCAPED-DEFECTS.md` row that reached a surface names an existing e2e TC; red evidence at pre-fix SHA.
- *Applies when:* every escaped defect, from the first.
- *Provenance:* LL-4, LL-12, LL-20 (KatenatsioTipster, 2026-10)
