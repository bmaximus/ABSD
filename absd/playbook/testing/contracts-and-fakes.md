# Contracts, Fakes and External Facts

Codes **FAKE** (fakes, recordings, contract and live checks, shipped settings, configuration agreement) and **EXT**
(external facts: evidence, status, fail-closed). An external system is anything the product does not control: data
feeds, payment, identity, mail, push, OCR/LLM, and the platforms it is built, deployed and run on (CI, registry, host or
container platform). Facts live in the Tester's living `EXTERNAL-FACTS.md` as `EXT-<SYS>-n`; plans cite them as
`FACT:EXT-<SYS>-n` (ORACLE-1). Contract tests are **M** in every profile once any external system exists
(data-pipeline: every source and sink; `absd/playbook/testing/strategy.md`). Harness: INTEG rules in `absd/playbook/testing/integration.md`; nightly and live
jobs: GATE rules in `absd/playbook/testing/gates.md`; secret canaries: SEC rules in `absd/playbook/security/baseline.md`.

## Checklist

- [ ] Every external system, platforms included, has an `EXTERNAL-FACTS.md` section with the full fact checklist (EXT-2, EXT-3)
- [ ] Evidence = recorded real response + independent source; never a statement, a default or a fake (EXT-2)
- [ ] Behaviour on an UNVERIFIED fact sits behind a flag that is off everywhere and fails closed (EXT-1)
- [ ] A fact becomes VERIFIED in one change: recording, source, contract TC, fakes, live check (EXT-4)
- [ ] Each fact pinned by a contract test running the shipped adapter on a committed recording (FAKE-2)
- [ ] Every fake reproduces every VERIFIED fact, incl. volume, ordering, errors and asynchrony (FAKE-1)
- [ ] One contract suite runs against the real system on schedule and against every fake on every push (FAKE-5)
- [ ] Recordings dated, scrubbed, error and empty answers included; adapter skips zero real records (FAKE-6)
- [ ] Failure-mode matrix per call; each class → designed message + TC; unconfigured → no call (FAKE-7)
- [ ] Requests and call budgets asserted for paid or limited systems (FAKE-8)
- [ ] External-format parsers: property-based + DST gap/overlap cases (FAKE-9)
- [ ] Nightly live check per system; missing credential or inconclusive streak = RED (FAKE-10)
- [ ] End-to-end fakes expose ground truth; e2e asserts against it (FAKE-11)
- [ ] Suites use shipped settings; only endpoints and credentials redirected (FAKE-4)
- [ ] Every multi-place setting agrees across code, config files, manifests and env examples (FAKE-3)
- [ ] Startup refuses unresolvable settings; the built artifact holds its runtime facts (FAKE-12)
- [ ] Integration replaced → sweep of UI, docs, config, fakes and health checks (EXT-5)

## Rules

**FAKE-1** — Make every fake answer like the real system — format and encoding, time zone, calendar and served periods, ordering, production volume, empty answers, error answers with their real status and body, credential rejection, limits, synchronous vs asynchronous behaviour — and mark any behaviour still resting on an UNVERIFIED fact with its EXT id.
- *Why:* fakes answered with the team's assumptions — UTC instead of UTC+8, every day served, three groups instead of hundreds, synchronous deploys — and every test passed while production was wrong (LL-1, LL-3, LL-4, LL-7).
- *Check:* each fake behaviour carries a comment citing its EXT id; `test_plan.md` has a fact × stand-in parity matrix (recording, contract test, unit fake, HTTP fake, e2e fake) with no empty cell; volume reaches the Data Volume Profile max with adversarial ordering (VAR-7); the Auditor flags behaviour without an EXT source as invented.
- *Applies when:* any fake, stub or simulator of an external system at integration or end-to-end level.
- *Provenance:* LL-1, LL-3, LL-4, LL-7 (KatenatsioTipster, 2026-10)

**FAKE-2** — Record each world fact from the real system as a dated response committed in the test tree, check its meaning against an independent source, and pin it with a contract test that runs the shipped adapter, with shipped settings, on that recording.
- *Why:* nobody compared one record with an official publication, so an 8-hour zone error shipped (LL-1); a reader written from a description took the half-time field for the final score (LL-2).
- *Check:* each EXT row names recording path, independent source, date and contract TC; ≥ 2 oracle rows per semantic fact, from different zones or units so one wrong offset cannot satisfy both; expected values are never computed by the code under test or copied from the recording; every constant or default encoding a fact carries a comment with the fact, evidence, date checked and pinning TC.
- *Applies when:* the product consumes any external API, feed, file, callback or model output.
- *Provenance:* LL-1, LL-2 (KatenatsioTipster, 2026-10)

**FAKE-3** — Pin every setting that lives in more than one place (code default, settings file, deployment manifest default, environment example, infrastructure code) with a test asserting every copy equals one literal whose comment names its evidence or decision owner; a missing copy fails.
- *Why:* fixing the provider zone in code alone would have changed nothing live because the manifest passed its own default (LL-1); docs and deployment-file comments contradicted the real defaults (LL-22).
- *Check:* `architecture.md`'s configuration table lists every location per key and each multi-place row has an agreement TC; generic checks: every manifest key binds to a real setting, every non-secret setting appears in the environment example, every setting a feature needs is settable through the documented surface, production manifests default to nothing unsafe (development mode, sample passwords or keys); files parsed with a real parser, not a regex.
- *Applies when:* configuration is duplicated across code and deployment artefacts.
- *Provenance:* LL-1, LL-22 (KatenatsioTipster, 2026-10)

**FAKE-4** — Run every suite with the settings the product ships: redirect only endpoints and credentials, never override a fact about the outside world (zones, formats, units, day numbering, paths), and give every other override an adjacent reason plus the TC that covers what it disables.
- *Why:* browser tests overrode the provider zone to UTC and every test passed while every deadline was 8 hours late; after the fix a test helper still defaulted to UTC (LL-1).
- *Check:* the Auditor greps hosts, helpers and e2e environments for overrides; helpers default to the shipped value; CI diffs e2e environment keys against an allowlist.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

**FAKE-5** — Keep one source per fact and one contract suite with two targets — the real system on schedule (FAKE-10) and every fake (in-process, HTTP, e2e) on every push — and change recording, contract test and every fake in the same commit when a fact is learned or changes.
- *Why:* the same fact was encoded separately in each fake and the live suite could target the fake but never did, so fakes drifted from reality (LL-1).
- *Check:* a CI "fake conformance" job lists each fake as a target; fakes read a shared fact file or schema where possible; the Auditor diffs fake behaviour against EXT rows.
- *Applies when:* any fake of an external system exists.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)
- Illustration: e.g. a JSON Schema, an OpenAPI document, or Pact or Spring Cloud Contract consumer contracts validated by both the fake and the live check.

**FAKE-6** — Name recordings `<system>-<operation>-<params>-<capture-date>` with capture metadata (who, how, redactions), scrub secrets and personal data, record empty and error answers as well as success, assert the shipped adapter reads every record of a real response (raw count = parsed count) even where production tolerates bad rows, and derive rare edge cases from real recordings by minimal mutation guarded by `mutated != original`.
- *Why:* recordings carry quirks nobody invents; a tolerant reader can drop a whole format variant silently, and a mutation that fails to apply makes a test vacuous.
- *Check:* secret and personal-data scan over the recordings directory; every skip, default and catch branch in an adapter has a test that triggers it plus a contract assertion that real data does not; recorded error bodies beat invented ones; a re-record procedure is documented.
- *Applies when:* recordings exist.
- *Provenance:* industry baseline

**FAKE-7** — For every external call, state in the port contract and test the behaviour per failure class — transport error, timeout, cancellation, 400, 401, 403, 404, 409 or busy, 429, 5xx, success status with an error body, unparsable body, wrong shape, empty, oversized — and map each class that reaches a person to a distinct designed message; an unconfigured integration calls nobody and names the missing setting.
- *Why:* OCR/LLM failures showed "Server error" because failure modes were never enumerated, so no message was designed or tested (LL-11).
- *Check:* failure-mode matrix per system in `test_plan.md`; message assertions use a substring unique to their branch; retries and fallbacks asserted by exact call sequence (target, count, order) for first-ok, later-ok and none-ok; "not configured": the spy saw zero requests and the message names the key; an outage is distinguishable from "no data" in logs and health.
- *Applies when:* any outbound dependency.
- *Provenance:* LL-11 (KatenatsioTipster, 2026-10)

**FAKE-8** — Assert what the product asks, not only what it gets back — path, parameters, identifiers, credential placement (a header, never the query string when the provider allows) — and, for paid or rate-limited systems, the number of calls per operation against a stated budget with usage and cost alerts specified.
- *Why:* a wrong parameter returns plausible data; paid feeds and model APIs have quotas that end a feature silently, and keys in URLs reach logs.
- *Check:* request-spy assertions per call; a call-count TC per paid use case (incl. cache hits); secret canaries scanned in logs (SEC rules); budget alerts listed under observability in `architecture.md`.
- *Applies when:* calls are parameterised, paid, rate-limited or cached.
- *Provenance:* industry baseline

**FAKE-9** — Test every parser of an external format with property-based or fuzz inputs and with the cases real data produces: local times inside a DST gap and a DST overlap, non-whole-hour offsets, unpadded or reordered fields, records dated by the provider's calendar.
- *Why:* provider-dated records crossed UTC day boundaries and were grouped under the wrong day (LL-3); a configurable-zone parser can turn one DST-gap time into a failed request.
- *Check:* properties in the default run — round-trip, never throws on any input, good records survive one bad record; DST rows per VAR-8.
- *Applies when:* the product parses an external format itself.
- *Provenance:* LL-3 (KatenatsioTipster, 2026-10)
- Illustration: e.g. FsCheck, Hypothesis, fast-check, jqwik.

**FAKE-10** — Check every external system that correctness depends on with a scheduled live contract job, off the push path, using the shipped adapter and settings: raw shape, zero records skipped, ≥ 1 invariant between fields, a plausibility window with an explicit inconclusive threshold, a summary line every run, credentials never printed; a missing credential, a skipped run or an inconclusive streak is RED (GATE-1).
- *Why:* the live job printed a warning and exited 0 for lack of a credential (LL-25); invariants such as half-time ≤ final catch swapped fields on any day (LL-2).
- *Check:* `TESTING.md` lists one live job per system or a user-approved waiver; failures alert an owner; the live field set is diffed against the recording (schema drift); the Manager checks the last live run at cycle start and Mode R.
- *Applies when:* a sandbox, test credential or safe read-only access exists.
- *Provenance:* LL-25, LL-2 (KatenatsioTipster, 2026-10)

**FAKE-11** — Give each end-to-end fake a test-only control channel that reveals the ground truth behind what it serves (decoded instants, amounts, states) and answers non-2xx when it cannot, and assert user-visible output against that truth, never against values recomputed with the product's own helpers.
- *Why:* only an oracle independent of the product's conversion code catches a wrong zone end to end (LL-1); real-time journeys need the fake to schedule events seconds apart and say when it runs out (LL-38).
- *Check:* the Auditor checks that e2e assertions on transformed external data cite a control-channel value or an independent literal; the channel is unreachable with production configuration.
- *Applies when:* the product transforms external data and shows it.
- *Provenance:* LL-1, LL-38 (KatenatsioTipster, 2026-10)

**FAKE-12** — Validate at start-up every setting whose wrong value would be plausible but harmful (time zone ids, currencies, units, URLs, schedules, percentages) and refuse to start with a message naming the key and a valid example; test the shipped default, a valid non-default and an invalid value through the real composition root, and check that the built artifact contains the runtime facts it needs (zone database entries, locales, CA bundle, fonts).
- *Why:* an unknown zone read silently as UTC moves every deadline (LL-1); the product crashed at start-up on infrastructure nobody had booted it against (LL-14), and fail-fast on a slim image without zone data turns a correct setting into an outage.
- *Check:* fail-fast keys marked in `architecture.md`'s configuration table, three TCs each; a CI step runs the shipped image or package and checks each runtime fact; boot on empty infrastructure per OPS rules in `absd/playbook/testing/nonfunctional.md`.
- *Applies when:* settings encode facts, or the product ships as an image or package.
- *Provenance:* LL-1, LL-14 (KatenatsioTipster, 2026-10)

**EXT-1** — Put behaviour that depends on an UNVERIFIED external fact behind a flag that is off in every environment, and make it fail closed: refuse with a designed "not available" outcome instead of acting on a guessed default.
- *Why:* an unknown provider zone, flagged as a blocking open question, shipped as a "safe default" with the feature on, and the caveat died when the cycle was archived (LL-1).
- *Check:* each UNVERIFIED fact has a Risk register row `blocks: flag:<name>` in `context.md`; a TC proves the flag-off path inert and the fail-closed outcome; Mode R blocks on any UNVERIFIED fact behind an enabled feature; the Auditor greps for defaults standing in for unverified facts.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

**EXT-2** — Accept as evidence of an external fact only a recorded real response plus an independent source (official documentation, a published schedule, a known real event); a person's statement, a default value or a fake is not evidence; give every external system the full fact checklist below, each row VERIFIED, UNVERIFIED or N/A with a reason.
- *Why:* the requirements accepted the owner's statement about a field's meaning (LL-2); served days and the provider calendar were never asked (LL-3); failure modes were never listed (LL-11).
- *Check:* an `EXTERNAL-FACTS.md` section per system in `context.md`, no blank checklist row; `analysis.md` cites EXT ids or UNVERIFIED candidates; Gate T: one CONTRACT TC per fact and one user-facing TC per failure mode.
- *Applies when:* the product talks to any external system.
- *Provenance:* LL-2, LL-3, LL-11 (KatenatsioTipster, 2026-10)

| # | Fact | Verify | Trap it prevents |
|---|---|---|---|
| 1 | Format & encoding | types, date and number formats, charset, field-name case, extra fields, markup inside values | a format variant dropped silently |
| 2 | Time zone | zone and DST of every timestamp field | provider-local time read as UTC (LL-1) |
| 3 | Calendar, day boundaries, served periods | whose calendar numbers days; which days or periods are served; when "today" appears | an always-empty "Today" (LL-3) |
| 4 | Ordering | natural order, stability, tie order | first listed ≠ earliest (LL-4) |
| 5 | Volume & pagination | typical and max per period, page size, cursor, end of list | three-item fakes (LL-4) |
| 6 | Empty answers | exact status and body of "no data" | outage read as "no data" |
| 7 | Error answers | 401, 403, 404, 429, 5xx, timeout, malformed — real status and body | "Server error" (LL-11) |
| 8 | Limits & cost | rate limit, quota, price per call, alert threshold | a feature dies at the quota |
| 9 | Sync vs async | accepted-then-processing, busy or conflict answers, completion signal | rollback refused while busy (LL-7) |
| 10 | Field semantics | which value is final, gross or net, units, sign, status codes, irregular events (postponed, cancelled) | half-time read as final (LL-2) |
| 11 | Late corrections & duplicates | corrections, replays, out-of-order and duplicate deliveries, idempotency keys, callback signatures | double processing |
| 12 | Version | version id, change signalling, deprecation | silent schema drift |

**EXT-3** — Treat the platforms the product is built, deployed, run and talks through — CI, registry, host or container platform, mail, push, OCR/LLM, payment, identity — as external systems with fact sheets, fakes and live checks, and fake a platform with a stateful model of its real semantics (asynchrony, busy or conflict answers, auth failures, partial failures, strict request validation) plus one safety invariant asserted across all scenarios.
- *Why:* the fake deploy platform deployed synchronously, so a same-version redeploy was smoke-tested mid-restart and the rollback was refused (LL-7); a stateful platform fake made the deploy script testable (LL-39); CI broke on a registry pull limit (LL-30).
- *Check:* every deploy or ops script branch has a scenario; when production reveals behaviour the fake lacked, the fake is fixed first and the incident becomes a scenario (ESC-1); the fake is compared with the real platform on a schedule.
- *Applies when:* the product uses platform APIs or custom deploy and ops automation.
- *Provenance:* LL-7, LL-39, LL-30 (KatenatsioTipster, 2026-10)

**EXT-4** — Verify a fact in one Tester change that adds the recording, the independent source, the contract TC, the updated fakes and the live check and turns the `EXTERNAL-FACTS.md` row VERIFIED; only after it may the guarding flag be turned on, by its owner through Mode R; until then the fact stays UNVERIFIED in the living register and the Risk register, never only in an archived artifact.
- *Why:* the zone caveat lived only in an archived analysis and was lost with it (LL-1).
- *Check:* git history shows the five parts in one commit set; the Auditor confirms every enabled flag depends only on VERIFIED facts.
- *Applies when:* always.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

**EXT-5** — When an external system is replaced or removed, sweep UI copy, status and health indicators, docs, configuration keys, environment examples, manifests, fakes, recordings, flags and allowlists for the old one, and point health checks at what the new provider really serves.
- *Why:* after a feed was replaced, a status card still named the old provider, then reported "no data" because it asked for a day the new feed never serves (LL-17).
- *Check:* `test_plan.md` lists the sweep (search terms, places) and a TC on the health indicator; the Auditor re-runs the search.
- *Applies when:* an integration is replaced, renamed or retired.
- *Provenance:* LL-17 (KatenatsioTipster, 2026-10)
