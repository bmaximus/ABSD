# Test design — variation catalogue and techniques

Code **VAR**. How the Tester turns each requirement, rule, state machine, data flow and risk into test cases before
code exists: which dimensions to vary, which values to use, and which technique yields the cases — the HOW behind every
Gate T obligation. Expected values: ORACLE in `absd/playbook/testing/oracles.md`. Principals: ACCESS in
`absd/playbook/testing/access-visibility.md`. Harness and chain plumbing: INTEG in `absd/playbook/testing/integration.md`.

## Checklist

- [ ] `test_plan.md` marks each relevant catalogue dimension per item: covered (TC ids) or N/A with reason (VAR-1)
- [ ] Every input and outcome is partitioned; one parameterised row per class and per variant (VAR-2)
- [ ] Every limit: below / at / above, inclusivity named, + one other representation; spec value asserted (VAR-3)
- [ ] Interacting rules → decision table; dominance pairs; one constructed tie per tie-break level (VAR-4)
- [ ] Every state machine: every valid transition with side effects, every invalid one rejected, terminal states (VAR-5)
- [ ] Every device/runtime class is its own target; input-mode hazards tested (VAR-6)
- [ ] Data at Data Volume Profile max, more than one page; the special item is never first (VAR-7)
- [ ] Time at zone midnights, DST, month/year/season ends; one foreign zone/locale run (VAR-8)
- [ ] ≥ 3 independent parameters → all pairs; full product on money/time/access (VAR-9)
- [ ] Principal grid from the matrix; every hat; entitlement changes seen live (VAR-10)
- [ ] Absent, malformed, hostile and forged values have a tested, named meaning (VAR-11)
- [ ] Concurrent writers, double submits, late responses, overlapping jobs forced deterministically (VAR-12)
- [ ] Re-runnable operations run twice: same state, zero changes, no duplicate side effects (VAR-13)
- [ ] Every dependency failure mode and error-catalogue entry injected; message, state and log level asserted (VAR-14)
- [ ] Property-based tests on invariants; seed printed; failing seeds kept (VAR-15)
- [ ] Metamorphic tests on every unordered or partitioned source (VAR-16)
- [ ] Idle budget: no unexpected activity; edits outlive the longest timer (VAR-17)
- [ ] Every data flow has a chain TC from a recorded payload; every step asserted (VAR-18)
- [ ] Every flag and switch: both states, toggle semantics, shipped defaults per environment (VAR-19)
- [ ] Every mutation re-read at the source of truth; side effects counted with their actor (VAR-20)

## Rules

**VAR-1** — Apply the variation catalogue (below) to every in-scope requirement, business rule, state machine, data
flow and risk: `test_plan.md` marks each relevant dimension "covered → TC ids" or "N/A — reason" and names the technique
that produced the cases.
- *Why:* interacting rules, midnights, re-runs and volume each slipped because nobody walked a list (LL-9, LL-45).
- *Check:* Gate T: the plan's dimension table has no blank cell; the Auditor samples N/A reasons against `analysis.md`.
- *Applies when:* every test plan (Modes F, S, D, B).
- *Provenance:* LL-9, LL-45 (KatenatsioTipster, 2026-10)

**VAR-2** — Partition every input and every rule outcome into equivalence classes from the specification (each valid
class, each invalid class, each enum member, each variant of the rule) and test one representative per class as a row of
one parameterised test (e.g. xUnit `[Theory]`, pytest `parametrize`, Jest `test.each`) reviewable against the spec
table. When behaviour forks by type, plan or category, run each scenario under every variant (no empty grid cell
without an N/A reason).
- *Why:* an enum branch with no row and a variant settled by another variant's rule are the cheapest defects to miss.
- *Check:* the Auditor diffs rows against the spec's classes; branch-removal mutants are killed (GATE-5).
- *Applies when:* a rule has ≥ 3 input classes or forks on a type, plan, category or enum.
- *Provenance:* industry baseline

**VAR-3** — For every comparison against a limit, test exactly at the limit and the smallest step on each side for its
type (1 tick, 1 cent, 1 day, 1 byte or character), name "inclusive"/"exclusive" in the test name, and add one case
with the same value in another representation (another UTC offset, unit, locale format, encoding). Ranges: min−1, min,
max, max+1. Date validity: open-ended (null), last valid day, first invalid day. Sizes: 0, 1, limit−1, limit, limit+1.
Rounding sites: a value needing rounding and an exact midpoint; magnitudes 0, negative, largest valid, first overflow.
Assert the spec's value (5 MiB), never the production constant.
- *Why:* deadlines read in the wrong offset stayed open for hours (LL-1); measurable midnight and threshold criteria
  were never turned into cases (LL-45).
- *Check:* the plan's boundary table has the three rows plus a representation row per threshold; relational and
  rounding-mode mutants are killed (GATE-5).
- *Applies when:* any `<`, `≤`, until, before, at least, max, deadline, expiry, quota, page size, rounding.
- *Provenance:* LL-1, LL-45 (KatenatsioTipster, 2026-10)

**VAR-4** — When two or more conditions or rules interact (precedence, override, dominance, eligibility + ordering,
roll-up of child states), write a decision table in `test_plan.md` — every combination, or collapsed rows with the
reason — and test each row. Roll-ups: each state alone, each adjacent dominance pair, all-weakest, empty. Orderings:
one constructed tie per tie-break level (assert the tie, then the order) down to a unique final key; eligibility tested
separately from order.
- *Why:* ranking, disqualification and prize split were tested alone; together they produced wrong prize positions (LL-9).
- *Check:* every BR that references another BR has a table id; the Auditor maps rows to TCs; statement-reorder mutants
  are killed.
- *Applies when:* interacting BRs (Gate T), derived statuses, rankings, permission overrides.
- *Provenance:* LL-9 (KatenatsioTipster, 2026-10)

**VAR-5** — For every state machine test every state × event: each valid transition (resulting state and its side
effects — audit row, notification, renumbering of an ordered set), each invalid transition rejected with the specified
error and the state unchanged, each terminal state rejecting every event, each guard at its boundary (VAR-3); walk each
lifecycle once end to end through every role that touches it.
- *Why:* re-slotting after a removal was an untested transition (LL-9); a specified flow step was half-implemented (LL-51).
- *Check:* the plan's from × to matrix equals the state tables in `analysis.md`; each illegal-transition error code
  appears in a test.
- *Applies when:* any lifecycle, workflow, status field or job state.
- *Provenance:* LL-9, LL-51 (KatenatsioTipster, 2026-10)

**VAR-6** — Treat every supported device or runtime class as a separate target with its own project and its own
result: web-ui phone (touch, small viewport; ON unless the user waived it in `context.md`) ≠ desktop, plus tablet or
landscape when declared; native-app each platform and device class; cli each supported OS, shell, terminal width, TTY vs
pipe; library each supported runtime or language version; http-api and data-pipeline each declared deployment runtime.
Per input mode, test what only it breaks: hover-only affordances, touch targets, swipe and overscroll in scroll
containers, on-screen keyboard, keyboard-only path.
- *Why:* a swipe reloaded the app and lost input on a phone, and a hover-only control was unreachable by touch — both
  invisible at desktop size (LL-4, LL-16).
- *Check:* the `TESTING.md` device/runtime row lists the classes in `context.md`; every journey TC runs in each relevant
  project; the CI report shows per-project results; gestures emulation cannot reproduce go to the Mode R real-device list.
- *Applies when:* the device/runtime row is M or triggered R.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10)

**VAR-7** — Build test data, fakes and seeds at production volume — at least the Data Volume Profile's max per
collection and always more than one page — and order it adversarially: the special item (default, earliest, highest,
the one under test) is never first; "first", "earliest" and "default" are different items; sort keys disagree;
duplicates and near-duplicates exist. Assert the full order, not only the first element.
- *Why:* a fake with three groups where the real source has hundreds hid a wrong default selection and a phone-only
  failure, because the special item was always first (LL-4).
- *Check:* the plan's data section states volume per collection against `analysis.md`; the Auditor counts fake and
  seed records and checks the special item's position; list/query TCs at max volume also assert latency and query
  count (PERF rules in `absd/playbook/testing/nonfunctional.md`).
- *Applies when:* any list, search, grouping, pagination, ranking, default selection, aggregation or batch.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**VAR-8** — Test every date bucketing, deadline, expiry, schedule and "today" at real boundaries: midnight in the display
zone, UTC midnight and midnight in every provider zone; both DST transitions (the missing and the repeated hour); month
end/start, year rollover, leap day, season or fiscal pivot and the day before it. Feed instants carrying different UTC
offsets (one where local and UTC order differ) and include a negative-offset zone. Run one e2e project, and the unit
suite once, with process/browser zone and locale deliberately unlike the Locale & Time Profile. Control time through the
clock seam below e2e; run each time-driven lifecycle once in real time at e2e (E2E rules).
- *Why:* a provider's UTC+8 timestamps read as UTC made every deadline hours late (LL-1); a provider calendar hid
  "today" (LL-3); tests in the audience's own zone hid a clock showing local time as UTC (LL-13).
- *Check:* the plan's time table lists every zone in the chain (provider, server, storage, display, client) and the
  instants per rule; time logic tested only at UTC is rejected; CI shows the foreign-zone project and the
  date-divergence nightly (LL-40).
- *Applies when:* behaviour depends on now, dates, zones or calendars.
- *Provenance:* LL-1, LL-3, LL-13, LL-40 (KatenatsioTipster, 2026-10)

**VAR-9** — When an operation has ≥ 3 independent parameters with ≥ 2 values each, cover at least all pairs with a
generator (e.g. PICT, ACTS, allpairspy) and the full product for every combination touching money, time or access;
record generator, constraints and seed in the plan.
- *Why:* full products explode, so suites silently test defaults only; most interaction defects need two factors.
- *Check:* the plan shows the parameter model and the generated rows; the Auditor checks the money/time/access subset.
- *Applies when:* configuration-, option- or flag-rich operations, filters, multi-field forms, CLI flag sets.
- *Provenance:* industry baseline

**VAR-10** — Expand the principal dimension (ACCESS-2) into the grid operation × principal × owner relation × resource
state; test each role in every hat it can wear (admin as ordinary member, owner vs peer of the same role, impersonator vs
impersonated); observe each entitlement change in the affected principal's live session in both directions (grant →
effect → revoke, expire or suspend → refused on the next request). Expectations follow ACCESS-3.
- *Why:* admins could not act as members because nobody tested that hat (LL-5); free accounts got paid data from a call
  they were allowed to make (LL-10).
- *Check:* the grid is generated from the Access & Visibility Matrix; each Actor × Capability "Yes" has a positive TC
  and each "No" a negative one.
- *Applies when:* the access row is M or triggered R.
- *Provenance:* LL-5, LL-10, LL-35 (KatenatsioTipster, 2026-10)

**VAR-11** — Give every input that may be absent or wrong a test whose name states its specified meaning: null,
missing, empty, whitespace, garbage, case variants, numeric or combined enum spellings, diacritics and Unicode
normalisation forms, NaN/Infinity, zero denominator (result finite), parts exceeding the whole, max length + 1, a
hostile payload per sink (markup, path incl. backslash, header CRLF, query, shell), and a forged value for every
server-derived field (the server's value wins). Expect the most conservative state the spec defines (pending, deny,
zero, reject) — never success, never a silent default.
- *Why:* "missing numbers fail validation" became "missing → 0" downstream (LL-44); a client-declared derived value was
  trusted (LL-48).
- *Check:* the plan has a degenerate-input column per operation; a parser without garbage rows or a derived field
  without a forged-value TC is a finding; hostile payloads per sink: SEC rules in `absd/playbook/security/baseline.md`.
- *Applies when:* every boundary input, parser, normaliser, ratio and derived field.
- *Provenance:* LL-44, LL-48 (KatenatsioTipster, 2026-10)

**VAR-12** — For every record two actors can write, every job that can start twice and every async or debounced
control, force the race deterministically (barriers, controllable fakes, paused responses — never sleeps): concurrent
writers (one wins, the other gets the specified conflict, no corruption), double submit (one effect), overlapping job
instances (prevented or safe as specified), conflicting user actions inside the debounce or latency window (last intent
wins; late responses ignored), concurrent first access to a cache, cancellation propagation.
- *Why:* a filter clicked right after typing was overwritten by the delayed search reload (LL-20).
- *Check:* the plan lists writable records, jobs and async inputs with a race TC each; the nightly repeat runs keep them
  stable.
- *Applies when:* shared records, jobs, async UI, caches, multi-instance services, stream consumers.
- *Provenance:* LL-20 (KatenatsioTipster, 2026-10)

**VAR-13** — Run every operation specified as re-runnable (retry, job, recompute, import, migration or backfill,
message handler, replayed batch, PUT-style update) twice: snapshot the full state, run again, assert identical state, a
zero change count and no duplicate side effect (audit row, notification, message, file, charge). Reads write nothing.
Migrations and backfills also get applies / exempt / out-of-scope cases on legacy-shaped rows; pipelines get duplicate
and late-arriving records.
- *Why:* idempotent re-run criteria were written and never tested (LL-45); a read implemented with a mutating call wrote
  phantom audit rows (LL-42).
- *Check:* every operation `analysis.md` or `architecture.md` marks idempotent has a run-twice TC.
- *Applies when:* background jobs, retries, migrations, handlers, imports, approvals.
- *Provenance:* LL-42, LL-45 (KatenatsioTipster, 2026-10)

**VAR-14** — Inject every failure mode of every dependency in its fact sheet and every error-catalogue entry: timeout,
refused or reset connection, error status or exit code, rate limit, malformed, partial or empty payload, slow answer,
still-pending async work, rejected credential, full disk, crash mid-operation. Assert the user-facing message key,
status or exit code, persisted state (nothing half-written; resumable), retry behaviour and log level (expected client
errors never at error level). Invalid input makes zero external calls; jobs crash and retry from every step.
- *Why:* external failures surfaced as "Server error" (LL-11); a synchronous fake hid an asynchronous platform (LL-7);
  rejected passwords were logged as server errors (LL-15).
- *Check:* each fact-sheet failure mode and catalogue code maps to ≥ 1 TC; the fakes can produce each mode (FAKE-1).
- *Applies when:* any external system, fallible dependency, job or error-catalogue entry.
- *Provenance:* LL-7, LL-11, LL-15 (KatenatsioTipster, 2026-10)

**VAR-15** — Back example tests with property-based tests wherever a rule has an invariant: parsers and normalisers
(idempotent, round trip), money (conservation, rounding once), rankings (ranks are a permutation of 1..n), period
generators (tile with no gap or overlap), validator vs domain (accepted ⇒ processable). Generators include the classes of
VAR-2, VAR-3 and VAR-11; the seed is fixed per run and printed; each shrunk failing case becomes a literal example row
(e.g. FsCheck, Hypothesis, fast-check).
- *Why:* hand-picked examples miss the inputs nobody imagined; invariants check thousands at the cost of one.
- *Check:* property tests print their seed in CI output; kept failing seeds exist as example rows.
- *Applies when:* parsers, normalisers, money, ranking, date generation, serialisation.
- *Provenance:* industry baseline

**VAR-16** — Test every computation over an unordered or partitioned source with metamorphic relations, in addition to
literals: permuted input → identical output (all permutations for n ≤ 4, seeded shuffles above), duplicated input,
split vs merged batches, irrelevant records added, equivalent representations, the same events replayed.
- *Why:* tied entrants were ranked by input order, so standings changed between recomputes (LL-49).
- *Check:* every ranking, aggregation, merge, dedupe, report total and sequentially applied override list has a relation TC.
- *Applies when:* inputs come from queries without a total order, sets, maps, parallel or streamed results.
- *Provenance:* LL-49 (KatenatsioTipster, 2026-10)

**VAR-17** — Assert an idle budget: a settled, untouched screen (web-ui, native-app) makes no request over a window
longer than its longest timer except specified polling (count it exactly); an idle service, worker, cli watcher or
pipeline with no input writes nothing and logs no error; an open dialog or unsaved edit survives longer than the longest
background timer or refresh.
- *Why:* consoles refetched every second and wiped a dialog while a reason was being typed (LL-12).
- *Check:* each screen or process with timers has an idle TC with its window and expected count.
- *Applies when:* timers, polling, live clocks, subscriptions, reactive re-renders, schedulers.
- *Provenance:* LL-12 (KatenatsioTipster, 2026-10)

**VAR-18** — For every data flow in `architecture.md`, write ≥ 1 chain test from the outermost boundary input — a
recorded real payload (FAKE-2) — through every specified step to the persisted end state and the displayed or emitted
outcome, faking only the external system; assert each step's effect (rows inserted, updated, deleted), not only the end
screen. Harness: INTEG rules.
- *Why:* tests fed the computation its own inputs, so the reader that took a half-time field as final was on no path
  (LL-2); "delete provisional, insert final" never deleted (LL-51).
- *Check:* trace_check data flow → chain TC; the chain's input is a committed recording.
- *Applies when:* every data flow (Gate T).
- *Provenance:* LL-2, LL-51 (KatenatsioTipster, 2026-10)

**VAR-19** — Test every feature flag and behaviour-changing setting in both states — off is fully inert (no route,
screen, command, job or side effect) — and its registered toggle semantics (hot: next request uses the new state;
restart: tested after restart); run the suite once per environment's shipped defaults.
- *Why:* turning a flag on at runtime did not rewire the provider, and the off path had no coverage (LL-23).
- *Check:* each flag-register entry maps to on, off and toggle TCs.
- *Applies when:* flags, kill switches, behaviour-changing configuration.
- *Provenance:* LL-23 (KatenatsioTipster, 2026-10)

**VAR-20** — After every mutation, assert at the source of truth (re-read through the public interface or reload the
screen); after a delete assert absence. Count side effects with their attributes: one audit row per action naming the
real actor (also under impersonation), zero on reads; each notification's recipient, content and locale, no duplicate
on retry.
- *Why:* a mutating call used as a read wrote phantom audit rows (LL-42).
- *Check:* mutating TCs contain a re-read; audit and notification TCs assert actor, target and count.
- *Applies when:* every mutation, admin action and notification (Gate T).
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

## Variation catalogue

| Dimension | Values to cover | Technique | Mandatory when |
|---|---|---|---|
| Input classes | each valid/invalid class, enum member, rule variant | EP (VAR-2) | every AC and BR |
| Limits | below/at/above; min−1…max+1; null/last valid/first invalid; other representation | BVA (VAR-3) | every BR with a limit |
| Numbers, money | needs rounding, exact midpoint, 0, negative, max, overflow, zero denominator | VAR-3, VAR-11 | every calculation |
| Interacting rules | combinations, dominance pairs, one tie per tie-break level | decision table (VAR-4) | interacting BRs |
| Lifecycle | state × event, valid + invalid, terminal, guards | state transitions (VAR-5) | every state machine |
| Device / runtime | phone, desktop, tablet; OS, shell, width, TTY; runtime versions | projects (VAR-6) | every UJ on desktop + phone; matrix M/R |
| Volume, order | 0, 1, page, Data Volume Profile max; special item not first | VAR-7 | lists, queries, aggregations |
| Time | zone midnights, both DST, month/year/season, leap day, offsets, foreign zone/locale | VAR-8 | every date/time rule |
| Parameter mix | all pairs; full product on money/time/access | pairwise (VAR-9) | ≥ 3 independent parameters |
| Principal | role × entitlement × owner relation × resource state; hats | VAR-10 + ACCESS | every operation |
| Absent, hostile, forged | null, empty, garbage, Unicode, per-sink payload, forged derived field | VAR-11 | inputs, parsers, derived fields |
| Concurrency | concurrent writers, double submit, late response, overlapping jobs | VAR-12 | shared records, jobs, async controls |
| Repetition | run twice, replay, duplicate delivery, retry | VAR-13 | jobs, retries, migrations, handlers |
| Dependency failure | each fact-sheet failure mode, crash mid-step | failure injection (VAR-14) | external systems, error-catalogue entries |
| Generated inputs | invariants over random inputs, seeded | property-based (VAR-15) | parsers, money, ranking, generators |
| Order, partition | permutations, duplication, split/merge, replay | metamorphic (VAR-16) | unordered sources |
| Idle | untouched window longer than the longest timer | idle budget (VAR-17) | timers, polling, schedulers |
| Data flow | recorded payload → persisted → shown | chain (VAR-18) | every data flow |
| Flags, config | off, on, toggle, shipped defaults per environment | VAR-19 | every flag |
| Side effects | re-read, absence after delete, audit actor, notifications | VAR-20 | mutations, admin actions, notifications |
| Locale, format | each supported locale; 24 h; number, currency, sign; case/diacritic-insensitive search | EP over locales + LOC (`absd/playbook/design/content-and-locale.md`) | every displayed value |
| UI state | each screen × state (empty, loading, error, partial, max volume) | E2E + VIS rules | every SCR |
| Secrets | canary value in every config input | SEC rules | always |
