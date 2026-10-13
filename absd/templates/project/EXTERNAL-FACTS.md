# External facts — what we know about every system we do not control

> Living, owned by the Tester, NEVER archived (`ABSD:FAKE-2`, `ABSD:EXT-1`, `ABSD:EXT-2`). Every external system the
> product talks to — data feeds, payment, mail, push, OCR/LLM, identity providers, **and the platforms we deploy and run
> on** (CI, container platform, registry, hosting) — has a section here. A fact is **VERIFIED** only with a recorded
> real response committed in the test tree **and** an independent source (official documentation, a published
> schedule, a known real event). A person's statement or a configuration default is not evidence. Behaviour that
> depends on an UNVERIFIED fact ships disabled and fails closed. Fakes answer exactly as the VERIFIED facts say.

## <SYS> — <system name>
- Purpose: <what we use it for> · interface: <HTTP API / file drop / SMTP / SDK / CLI> · version: <…>
- Owner/contact and terms (rate limits, cost per call, quota alerts): <…>
- Fake used in tests: <path> · live check: <job name, schedule>

| EXT | Fact | Status | Evidence (recording path + independent source) | Date checked | Contract TC | Live check |
|---|---|---|---|---|---|---|
| EXT-<SYS>-1 | Format and encoding of <resource> | UNVERIFIED | — | — | — | — |
| EXT-<SYS>-2 | Time zone of every timestamp field | | | | | |
| EXT-<SYS>-3 | Calendar and day boundaries (which day a record belongs to; which days/periods are served) | | | | | |
| EXT-<SYS>-4 | Ordering of results | | | | | |
| EXT-<SYS>-5 | Volume per period (typical / max) and pagination | | | | | |
| EXT-<SYS>-6 | Empty / "no data" answer | | | | | |
| EXT-<SYS>-7 | Error answers: 401, 403, 404, 429, 5xx, timeout, malformed body | | | | | |
| EXT-<SYS>-8 | Usage, rate and cost limits | | | | | |
| EXT-<SYS>-9 | Synchronous vs asynchronous behaviour (e.g. accepted-then-processed) | | | | | |
| EXT-<SYS>-10 | Field semantics that are easy to misread (e.g. which score is final, which amount is gross) | | | | | |
| EXT-<SYS>-11 | Late corrections, duplicates and idempotency | | | | | |
| EXT-<SYS>-12 | Version / change signalling | | | | | |

Failure modes → user-facing behaviour (each needs a test, Gate T):
| EXT | Failure | What the user sees / what the system does | TC |
|---|---|---|---|
