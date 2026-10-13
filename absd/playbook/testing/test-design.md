# Test design — variation catalogue and techniques

Code **VAR**. How the Tester turns requirements, rules, state machines, data flows and risks into test cases before
code exists — the HOW behind every Gate T obligation. Expected values: ORACLE (`absd/playbook/testing/oracles.md`);
principals: ACCESS (`absd/playbook/testing/access-visibility.md`); harness: INTEG (`absd/playbook/testing/integration.md`).

## Checklist

- [ ] Each catalogue dimension per plan item: TC ids or N/A with reason (VAR-1)
- [ ] One parameterised row per equivalence class and variant (VAR-2)
- [ ] Every limit: below/at/above, inclusivity named, other representation (VAR-3)
- [ ] Interacting rules → decision table; one tie per tie-break level (VAR-4)
- [ ] Every valid transition with side effects; every invalid one rejected (VAR-5)
- [ ] Every device/runtime class is its own target (VAR-6)
- [ ] Data at Data Volume Profile max; the special item never first (VAR-7)
- [ ] Zone midnights, DST, period ends; one foreign zone/locale run (VAR-8)
- [ ] ≥ 3 parameters → all pairs; full product on money/time/access (VAR-9)
- [ ] Principal grid; every hat; entitlement changes seen live (VAR-10)
- [ ] Absent, malformed, hostile, forged values: tested meaning (VAR-11)
- [ ] Races forced deterministically; late responses ignored (VAR-12)
- [ ] Re-runnable operations run twice; no duplicate side effects (VAR-13)
- [ ] Every failure mode and error-catalogue entry injected (VAR-14)
- [ ] Property-based tests on invariants; seed printed, failures kept (VAR-15)
- [ ] Metamorphic tests on every unordered or partitioned source (VAR-16)
- [ ] Idle budget; edits outlive the longest timer (VAR-17)
- [ ] Every data flow has a chain TC from a recorded payload (VAR-18)
- [ ] Every flag: both states, toggle semantics, shipped defaults (VAR-19)
- [ ] Mutations re-read; side effects counted with actor (VAR-20)

## Rules

**VAR-1** — Apply the variation catalogue (below) to every in-scope requirement, rule, state machine, data flow and
risk: `test_plan.md` marks each relevant dimension "covered → TC ids" or "N/A — reason" and names the technique used.
- *Why:* interacting rules, midnights, re-runs and volume each slipped because nobody walked a list (LL-9, LL-45).
- *Check:* Gate T: no blank cell in the plan's dimension table; the Auditor samples N/A reasons.
- *Applies when:* every test plan (Modes F, S, D, B).
- *Provenance:* LL-9, LL-45 (KatenatsioTipster, 2026-10)

**VAR-2** — Partition every input and rule outcome into equivalence classes from the specification (each valid and
invalid class, enum member, rule variant); test one representative per class as a row of one parameterised test
(e.g. xUnit `[Theory]`, pytest `parametrize`, Jest `test.each`) reviewable against the spec table. When behaviour forks
by type, plan or category, run each scenario under every variant.
- *Why:* an enum branch without a row, or a variant run by another variant's rule, is the cheapest defect to miss.
- *Check:* rows diffed against the spec's classes; branch-removal mutants killed (GATE-5).
- *Applies when:* ≥ 3 input classes, or a fork on type, plan, category or enum.
- *Provenance:* industry baseline

**VAR-3** — For every comparison against a limit, test exactly at it and the smallest step on each side for its type
(1 tick, cent, day, byte), name "inclusive"/"exclusive" in the test name, and add the same value in another
representation (UTC offset, unit, locale format, encoding). Ranges: min−1, min, max, max+1. Validity dates: open-ended,
last valid day, first invalid day. Rounding: a value needing it and an exact midpoint; magnitudes 0, negative, largest
valid, first overflow. Assert the spec's value, never the code's constant.
- *Why:* deadlines read in the wrong offset stayed open for hours (LL-1); threshold criteria never became cases (LL-45).
- *Check:* boundary table with three rows + a representation row per limit; relational and rounding mutants killed.
- *Applies when:* any `<`, `≤`, until, before, at least, max, deadline, expiry, quota, page size, rounding.
- *Provenance:* LL-1, LL-45 (KatenatsioTipster, 2026-10)

**VAR-4** — When conditions or rules interact (precedence, override, dominance, eligibility + ordering, roll-up of
child states), write a decision table in `test_plan.md` — every combination, or collapsed rows with the reason — and
test each row. Roll-ups: each state alone, each adjacent dominance pair, all-weakest, empty. Orderings: one constructed
tie per tie-break level (assert the tie, then the order) down to a unique key; eligibility tested apart from order.
- *Why:* ranking, disqualification and prize split, each tested alone, together gave wrong prize positions (LL-9).
- *Check:* every BR citing another BR has a table; rows map to TCs; statement-reorder mutants are killed.
- *Applies when:* interacting BRs, derived statuses, rankings, permission overrides.
- *Provenance:* LL-9 (KatenatsioTipster, 2026-10)

**VAR-5** — For every state machine test every state × event: each valid transition (new state and side effects —
audit row, notification, renumbering of an ordered set), each invalid one rejected with the specified error and the
state unchanged, each terminal state rejecting every event, each guard at its boundary (VAR-3); walk each lifecycle
once end to end through every role that touches it.
- *Why:* re-slotting after a removal was untested (LL-9); a specified step was half-implemented (LL-51).
- *Check:* from × to matrix = `analysis.md` state tables; every illegal-transition code asserted.
- *Applies when:* lifecycles, workflows, status fields, job states.
- *Provenance:* LL-9, LL-51 (KatenatsioTipster, 2026-10)

**VAR-6** — Treat every supported device or runtime class as a separate target with its own project and result:
web-ui phone (touch, small viewport; ON unless waived in `context.md`) ≠ desktop, tablet or landscape when declared;
native-app each platform and device class; cli each OS, shell, terminal width, TTY vs pipe; library each supported
runtime or language version; http-api and data-pipeline each declared deployment runtime. Per input mode test what
only it breaks: hover-only affordances, touch targets, overscroll in scroll containers, on-screen keyboard, keyboard-only.
- *Why:* on a phone a swipe reloaded the app and lost input, and a hover-only control was unreachable (LL-4, LL-16).
- *Check:* each class in `context.md` has a project and each journey runs in it; gestures emulation misses are on
  the Mode R real-device list.
- *Applies when:* the device/runtime row is M or triggered R.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10)

**VAR-7** — Build test data, fakes and seeds at production volume — at least the Data Volume Profile max per collection,
always more than one page — ordered adversarially: the special item (default, earliest, highest, the one under test)
is never first; "first", "earliest" and "default" are different items; sort keys disagree; near-duplicates exist.
Assert the full order, not only the first element.
- *Why:* a three-group fake (real: hundreds) always put the special item first, hiding a wrong default and a
  phone-only failure (LL-4).
- *Check:* fake/seed counts match the plan, special item not first; max-volume list TCs also assert latency and
  query count (PERF in `absd/playbook/testing/nonfunctional.md`).
- *Applies when:* lists, search, grouping, pagination, ranking, defaults, batches.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**VAR-8** — Test every date bucketing, deadline, expiry, schedule and "today" at real boundaries: midnight in the
display zone, UTC and every provider zone; both DST transitions (missing and repeated hour); month end/start, year
rollover, leap day, season or fiscal pivot and the day before. Use instants with different UTC offsets (one where local
and UTC order differ) and a negative-offset zone. Run one e2e project, and the unit suite once, in a process or browser
zone and locale unlike the Locale & Time Profile. Below e2e, time comes from the clock seam; e2e runs each
time-driven lifecycle once in real time.
- *Why:* UTC+8 provider timestamps read as UTC (LL-1), a provider calendar hiding "today" (LL-3) and a clock
  labelled UTC showing local time (LL-13) all passed tests run in one zone.
- *Check:* the plan lists each zone in the chain (provider, server, storage, display, client) and the instants per
  rule; UTC-only time tests are rejected; CI shows the foreign-zone project and date-divergence nightly (LL-40).
- *Applies when:* behaviour depends on now, dates, zones or calendars.
- *Provenance:* LL-1, LL-3, LL-13, LL-40 (KatenatsioTipster, 2026-10)

**VAR-9** — When an operation has ≥ 3 independent parameters of ≥ 2 values, cover at least all pairs with a generator
(e.g. PICT, ACTS, allpairspy) plus the full product for combinations touching money, time or access; record the model,
constraints and seed in the plan.
- *Why:* full products explode, so suites test defaults only; most interaction defects need two factors.
- *Check:* model and generated rows in the plan; money/time/access subset complete.
- *Applies when:* option-rich operations, filters, multi-field forms, cli flag sets.
- *Provenance:* industry baseline

**VAR-10** — Expand the principal dimension (ACCESS-2) into operation × principal × owner relation × resource state;
test each role in every hat it wears (admin as ordinary member, owner vs peer, impersonator vs impersonated); observe
each entitlement change in the affected live session both ways (grant → effect → revoke, expire or suspend → refused
on the next request). Expectations per ACCESS-3.
- *Why:* admins could not act as members (LL-5); free accounts got paid data from an allowed call (LL-10).
- *Check:* grid generated from the Access & Visibility Matrix; each Actor × Capability Yes/No has a positive/negative TC.
- *Applies when:* the access row is M or triggered R.
- *Provenance:* LL-5, LL-10, LL-35 (KatenatsioTipster, 2026-10)

**VAR-11** — Give every input that may be absent or wrong a test named after its specified meaning: null, empty,
whitespace, garbage, case variants, numeric or combined enum spellings, diacritics and Unicode normalisation
forms, NaN/Infinity, zero denominator (finite result), parts exceeding the whole, max length + 1, a hostile payload per
sink (markup, path incl. backslash, header CRLF, query, shell), a forged value for every server-derived field (the
server's value wins). Expect the most conservative state the spec defines (pending, deny, zero, reject) — never
success, never a silent default.
- *Why:* "missing numbers fail validation" became "missing → 0" downstream (LL-44); a client-declared derived value was
  trusted (LL-48).
- *Check:* degenerate-input column per operation; missing garbage rows or forged-field TCs are findings. Payloads per
  sink: SEC (`absd/playbook/security/baseline.md`).
- *Applies when:* boundary inputs, parsers, normalisers, ratios, derived fields.
- *Provenance:* LL-44, LL-48 (KatenatsioTipster, 2026-10)

**VAR-12** — Force every race deterministically (barriers, controllable fakes, held responses — never sleeps):
concurrent writers of one record (one wins, the other gets the specified conflict, no corruption), double submit (one
effect), overlapping job runs (prevented or safe), conflicting actions inside a debounce or latency window (last intent
wins; late responses ignored), concurrent first cache access, cancellation.
- *Why:* a filter clicked right after typing was overwritten by the delayed search reload (LL-20).
- *Check:* each writable record, job and async input has a race TC; nightly repeat runs stay green.
- *Applies when:* shared records, jobs, async UI, caches, multiple instances, consumers.
- *Provenance:* LL-20 (KatenatsioTipster, 2026-10)

**VAR-13** — Run every operation specified as re-runnable (retry, job, recompute, import, migration, backfill, message
handler, replayed batch, PUT-style update) twice: snapshot the full state, rerun, assert identical state, zero changes
and no duplicate side effect (audit row, notification, message, file, charge). Reads write nothing. Migrations and
backfills also get applies / exempt / out-of-scope cases on legacy-shaped rows; pipelines get duplicate and late records.
- *Why:* idempotent re-run criteria were never tested (LL-45); a read built on a mutating call wrote audit rows (LL-42).
- *Check:* every operation marked idempotent upstream has a run-twice TC.
- *Applies when:* jobs, retries, migrations, handlers, imports, approvals.
- *Provenance:* LL-42, LL-45 (KatenatsioTipster, 2026-10)

**VAR-14** — Inject every failure mode in each dependency's fact sheet and every error-catalogue entry: timeout, connection
reset, error status or exit code, rate limit, malformed, partial or empty payload, slow answer, pending
async work, rejected credential, full disk, crash mid-operation. Assert the message key, status or exit code, persisted
state (nothing half-written; resumable), retry behaviour and log level (expected client errors never at error level).
Invalid input makes zero external calls; jobs crash and retry from every step.
- *Why:* external failures showed "Server error" (LL-11); a synchronous fake hid an asynchronous platform (LL-7);
  rejected passwords were logged as server errors (LL-15).
- *Check:* each failure mode and catalogue code maps to ≥ 1 TC; the fakes can produce each mode (FAKE-1).
- *Applies when:* external systems, fallible dependencies, jobs, error-catalogue entries.
- *Provenance:* LL-7, LL-11, LL-15 (KatenatsioTipster, 2026-10)

**VAR-15** — Back example tests with property-based tests wherever a rule has an invariant: parsers and normalisers
(idempotent, round trip), money (conservation, rounding once), rankings (ranks permute 1..n), period generators (no gap
or overlap). Generators include the VAR-2, VAR-3 and VAR-11 classes; the
seed is fixed and printed; each shrunk failure becomes a literal example row (e.g. FsCheck, Hypothesis, fast-check).
- *Why:* hand-picked examples miss inputs nobody imagined; one invariant checks thousands.
- *Check:* CI output shows each seed; kept failing seeds exist as example rows.
- *Applies when:* parsers, normalisers, money, ranking, date generation, serialisation.
- *Provenance:* industry baseline

**VAR-16** — Test every computation over an unordered or partitioned source with metamorphic relations as well as
literals: permuted input → identical output (all permutations for n ≤ 4, seeded shuffles above), duplicated input,
split vs merged batches, irrelevant records added, equivalent representations, the same events replayed.
- *Why:* tied entrants were ranked by input order (LL-49).
- *Check:* every ranking, aggregation, merge, dedupe and report total has a relation TC.
- *Applies when:* queries without a total order, sets, maps, parallel or streamed results.
- *Provenance:* LL-49 (KatenatsioTipster, 2026-10)

**VAR-17** — Assert an idle budget: a settled, untouched screen (web-ui, native-app) makes no request over a window
longer than its longest timer except specified polling (counted exactly); an idle service, worker, cli watcher or
pipeline writes nothing and logs no error; an open dialog or unsaved edit outlives the longest background timer.
- *Why:* consoles refetched every second, wiping a dialog mid-typing (LL-12).
- *Check:* each screen or process with timers has an idle TC with window and expected count.
- *Applies when:* timers, polling, live clocks, subscriptions, schedulers.
- *Provenance:* LL-12 (KatenatsioTipster, 2026-10)

**VAR-18** — For every data flow in `architecture.md`, write ≥ 1 chain test from the outermost boundary input — a
recorded real payload (FAKE-2) — through every specified step to the persisted end state and the displayed or emitted
outcome, faking only the external system; assert each step's effect (rows inserted, updated, deleted), not only the end.
- *Why:* tests fed a computation its own inputs, so the reader misreading a provider field was on no path (LL-2);
  "delete provisional, insert final" never deleted (LL-51).
- *Check:* trace_check data flow → chain TC; the chain's input is a committed recording; harness per INTEG rules.
- *Applies when:* every data flow.
- *Provenance:* LL-2, LL-51 (KatenatsioTipster, 2026-10)

**VAR-19** — Test every feature flag and behaviour-changing setting in both states — off is fully inert (no route,
screen, command, job or side effect) — plus its registered toggle semantics (hot: the next request sees it; restart:
tested after restart); run the suite once with each environment's shipped defaults.
- *Why:* a flag turned on at runtime did not rewire the provider; the off path was untested (LL-23).
- *Check:* each flag-register entry maps to on, off and toggle TCs.
- *Applies when:* flags, kill switches, behaviour-changing configuration.
- *Provenance:* LL-23 (KatenatsioTipster, 2026-10)

**VAR-20** — After every mutation assert at the source of truth (re-read through the public interface or reload);
after a delete assert absence. Count side effects with attributes: one audit row per action naming the real actor
(also under impersonation), none on reads; each notification's recipient, content, locale, no duplicate on retry.
- *Why:* a mutating call used as a read wrote phantom audit rows (LL-42).
- *Check:* mutating TCs re-read; audit and notification TCs assert actor, target and count.
- *Applies when:* mutations, admin actions, notifications.
- *Provenance:* LL-42 (KatenatsioTipster, 2026-10)

## Variation catalogue

| Dimension | Values | Technique | Mandatory when (Gate T) |
|---|---|---|---|
| Input classes | valid/invalid classes, enum members, variants | EP (VAR-2) | every AC, BR |
| Limits | below/at/above, min−1…max+1, validity dates, representation | BVA (VAR-3) | every BR with a limit |
| Numbers, money | rounding midpoint, 0, negative, overflow, zero divisor | VAR-3, VAR-11 | every calculation |
| Interacting rules | combinations, dominance pairs, ties per level | decision table (VAR-4) | interacting BRs |
| Lifecycle | state × event, valid + invalid, terminal, guards | state transitions (VAR-5) | every state machine |
| Device, runtime | phone, desktop; OS, shell, width, TTY; runtimes | projects (VAR-6) | every UJ, desktop + phone |
| Volume, order | 0, 1, page, profile max; special item not first | VAR-7 | lists, queries |
| Time | zone midnights, DST, period ends, leap day, foreign zone | VAR-8 | every date/time rule |
| Parameter mix | all pairs; full product on money/time/access | pairwise (VAR-9) | ≥ 3 parameters |
| Principal | role × entitlement × owner × state; hats | VAR-10, ACCESS | every operation |
| Absent, hostile, forged | null, garbage, Unicode, sink payloads, forged field | VAR-11 | inputs, derived fields |
| Concurrency | writers, double submit, late response, job overlap | VAR-12 | shared records, jobs |
| Repetition | run twice, replay, duplicate delivery | VAR-13 | jobs, retries, handlers |
| Dependency failure | each fact-sheet failure mode, crash mid-step | fault injection (VAR-14) | every EXT, error code |
| Generated inputs | seeded random inputs vs invariants | property-based (VAR-15) | parsers, money, ranking |
| Order, partition | permutation, duplication, split/merge | metamorphic (VAR-16) | unordered sources |
| Idle | untouched > longest timer | idle budget (VAR-17) | timers, polling |
| Data flow | recorded payload → persisted → shown | chain (VAR-18) | every data flow |
| Flags, config | off, on, toggle, shipped defaults | VAR-19 | every flag |
| Side effects | re-read, absence, audit actor, notifications | VAR-20 | mutations, admin actions |
| Locale, format | each locale; 24 h; number, currency, sign | EP + LOC rules | every displayed value |
| UI state | empty, loading, error, partial, max | E2E, VIS rules | every SCR |
