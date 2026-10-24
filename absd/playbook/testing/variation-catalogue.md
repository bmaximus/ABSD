# Variation catalogue — dimensions and when they are mandatory

Code **VAR**. The catalogue VAR-1 applies to every in-scope requirement, rule, state machine, data flow and risk —
dimension, values, technique, when Gate T makes it mandatory — and the dimension rules VAR-21 to VAR-25: caches, ranges
and intervals, update semantics, overrides vs recomputation, data-source and channel parity. Techniques VAR-1 to VAR-20:
`absd/playbook/testing/test-design.md`; expected values: ORACLE (`absd/playbook/testing/oracles.md`).

## Checklist

- [ ] Every catalogue row per plan item: covered → TC ids, or N/A with reason (VAR-1)
- [ ] Caches: miss then hit, negative-result policy, each invalidation trigger, TTL on the fake clock (VAR-21)
- [ ] Intervals: overlap at start and at end, containment, identical, touching, gap, empty, open-ended (VAR-22)
- [ ] Updates: omitted ≠ null; children new, existing, absent, duplicate; re-applied without a second effect (VAR-23)
- [ ] Overrides and protected subsets survive every recomputation trigger; clearing restores the computed value (VAR-24)
- [ ] Every source and entry channel: same outcome, same stored result, specified precedence (VAR-25)

## Rules

**VAR-21** — Test every cache — in-process memo, shared cache, HTTP or client query cache, edge cache — against its
specified policy: a miss then a hit (the second read makes no call to the source, counted as FAKE-8 counts calls); the
negative-result policy (an empty, not-found or failed answer cached for its stated time, or never); each invalidation
trigger `architecture.md` names (a write through the product, a change at the source, a setting or flag change, sign-out
or an entitlement change: the next read is fresh); TTL expiry on the fake clock at T−ε, T and T+ε (INTEG-5). A cached
value never crosses principals or tenants (ACCESS-10).
- *Why:* hit after miss, negative caching, invalidation triggers and expiry were mined as untested dimensions; a stale
  or cross-principal cached answer passes every test that reads once (LL-57).
- *Check:* a cache row per cached read in the plan's dimension table; source call counts asserted on the hit and after
  each trigger; expiry tested on the clock seam, never by real waits.
- *Applies when:* the product caches anything read from a store, an owned service or an external system.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)

**VAR-22** — For every rule over ranges or intervals (validity periods, bookings, schedules, bands, version ranges),
test each relation of a second interval to the first: overlap at the start, overlap at the end, containment both ways,
identical, adjacency (one ends where the next starts — touching, with the spec's inclusive or exclusive end named,
VAR-3), a gap of one smallest step, an empty or zero-length interval and an open-ended one; assert the specified outcome
per relation (conflict, merge, split, accept).
- *Why:* overlap at one end, containment and touching ranges were mined as missing cases; a rule tested on disjoint and
  fully overlapping ranges only fails at the edges (LL-57).
- *Check:* a relation table per interval rule, a TC per row; comparison mutants killed (GATE-5).
- *Applies when:* a rule compares, merges, allocates or splits ranges, periods or intervals.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)

**VAR-23** — For every update that may be partial or nested (patch, merge, upsert, import, sync), test the specified
meaning of each field state — omitted (unchanged), explicitly null or empty (cleared, or refused), present — and of each
child in a nested collection: a new child (created), an existing child (updated by its key, never recreated: id and
history kept), a child absent from the update (kept or deleted, as specified), a duplicate key (refused); then apply the
same update again and assert identical state and no second side effect (VAR-13).
- *Why:* omitted vs explicitly null fields and new vs existing children were mined as untested; a merge that recreates
  children loses their ids and history (LL-57).
- *Check:* a field-state × child-state table per update operation; each row re-read at the source of truth (VAR-20).
- *Applies when:* partial updates, nested writes, upserts, imports, synchronisation.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)

**VAR-24** — Where a manual override or a protected subset (locked, manually settled, approved, frozen) coexists with a
computed value, list every recomputation trigger — scheduled job, import or late correction from the source, edit of an
input, rule or setting change, migration or backfill, a manual "recompute" — and test each one: overridden and
protected items keep their value and marker, every other item recomputes; clearing the override returns the item to
the computed value; the audit entry names who overrode (INTEG-9).
- *Why:* "an override survives every recomputation trigger" and "protected subsets survive" were mined requirements no
  test walked; one forgotten trigger silently reverts manual decisions (LL-57).
- *Check:* a trigger × {overridden, protected, ordinary} table per computed value; each cell a TC asserting the
  persisted value.
- *Applies when:* manual overrides, locks or protected records exist beside automatic computation.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)

**VAR-25** — When one fact or operation has several sources or entry channels — a verified source vs manual entry, a
feed vs an import, a screen, the API, the cli, a file upload, a model extraction — test parity: the same input through
every channel gives the same outcome, the same stored result (field by field, except the declared source and channel
markers), the same validation errors and the same side effects; when sources disagree the specified precedence holds
(a verified value replaces a manual one, or never does), and the source marker shows where the spec says.
- *Why:* verified vs manual sources and the same action through several channels were mined as untested; a channel that
  skips one validation stores a different result (LL-57).
- *Check:* a channel × case table per operation; stored records compared across channels; a precedence TC per pair of
  sources that can disagree.
- *Applies when:* ≥ 2 sources for one fact, or ≥ 2 entry channels for one operation.
- *Provenance:* LL-57 (ABSD v2 kit review, 2026-10)

## Catalogue

VAR-1 walks every row for each plan item; "mandatory when" is the Gate T trigger.

| Dimension | Values | Technique | Mandatory when (Gate T) |
|---|---|---|---|
| Input classes | valid/invalid classes, enum members, variants | EP (VAR-2) | every AC, BR |
| Limits | below/at/above, min−1…max+1, validity dates, representation; cut-offs: ties at the cut, withheld count | BVA (VAR-3, ACCESS-10) | every BR with a limit |
| Numbers, money | rounding midpoint, 0, negative, overflow, zero divisor | VAR-3, VAR-11 | every calculation |
| Interacting rules | combinations, dominance pairs, ties per level, values equal by maths | decision table (VAR-4) | interacting BRs |
| Lifecycle | state × event, valid + invalid, terminal, guards | state transitions (VAR-5) | every state machine |
| Nested lifecycle | child action × child status × parent status | decision table (VAR-4, VAR-5) | child states under a stateful parent |
| Device, runtime | phone, desktop; rendering engines; OS, shell, width, TTY; runtimes | projects (VAR-6) | every UJ on each declared class |
| Volume, order | 0, 1, page, profile max; special item not first | VAR-7 | lists, queries |
| Per-parent cardinality | 0, 1, many and max children per parent; many parents | VAR-7 | one-to-many relations |
| Lookup outside the set | before the first, after the last, empty set, stale or deleted id, another owner's id | VAR-3, VAR-11, ACCESS-9 | lookups, next/previous, search |
| Time | zone midnights, DST, period ends, leap day, foreign zone | VAR-8 | every date/time rule |
| Parameter mix | all pairs; full product on money/time/access | pairwise (VAR-9) | ≥ 3 parameters |
| Principal | role × entitlement × owner × state; hats | VAR-10, ACCESS | every operation |
| Absent, hostile, forged | null, garbage, Unicode, sink payloads, forged field | VAR-11 | inputs, derived fields |
| Concurrency | writers, double submit, late response, job overlap; race detector | VAR-12 | shared records, jobs |
| Repetition | run twice, replay, duplicate delivery | VAR-13 | jobs, retries, handlers |
| Dependency failure | each fact-sheet failure mode, crash mid-step | fault injection (VAR-14) | every EXT, error code |
| Owned dependency failure | store or broker restart mid-request, pool exhausted, own disk full | RESIL-4 | owned stores, brokers, volumes |
| Network condition | offline, slow, aborted request, flaky, answer after navigating away | throttled and offline projects (VAR-12, VAR-14, RESIL-3) | web-ui, native-app: every SCR that loads data |
| Navigation | back, forward, refresh mid-flow, deep link, second tab, back after sign-out | e2e steps (DSN-12, ACCESS-14) | web-ui, native-app: every UJ |
| Generated inputs | seeded random inputs vs invariants; schema fuzz of every public operation | property-based, fuzz (VAR-15) | parsers, money, ranking; public operations |
| Order, partition | permutation, duplication, split/merge | metamorphic (VAR-16) | unordered sources |
| Idle | untouched > longest timer | idle budget (VAR-17) | timers, polling |
| Data flow | recorded payload → persisted → shown | chain (VAR-18) | every data flow |
| Flags, config | off, on, toggle, shipped defaults | VAR-19 | every flag |
| Background job | schedule, no overlap, rerun, crash/retry, flag off | VAR-12, VAR-13, VAR-14, VAR-19 | every job |
| Side effects | re-read, absence, audit actor, notifications | VAR-20 | mutations, admin actions |
| Cache | miss/hit, negative result, each invalidation, TTL, per principal | VAR-21 | every cache |
| Range, interval | overlap start/end, containment, touching, gap, empty, open-ended | VAR-22 | interval rules |
| Update semantics | omitted vs null; child new/existing/absent; re-apply | VAR-23 | partial or nested updates |
| Override, recompute | every recompute trigger × overridden/protected/ordinary | VAR-24 | overrides, protected subsets |
| Source, channel | verified vs manual; each entry channel; precedence | VAR-25 | ≥ 2 sources or channels |
| Load | stated concurrency, past saturation, soak | PERF-4 | concurrency/throughput REQ-NF; deployed services |
| Previous versions | contract diff, N-1 clients, N-1 stored and queued data | COMPAT-1, COMPAT-2, COMPAT-3 | published interfaces, persisted formats |
| Locale, format | each locale; 24 h; number, currency, sign | EP + LOC rules | every displayed value |
| UI state | empty, loading, error, partial, max | E2E, VIS rules | every SCR |
