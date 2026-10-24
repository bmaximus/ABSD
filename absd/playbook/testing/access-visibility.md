# Access & Visibility Matrix

Code **ACCESS**. How to specify and prove, for every operation the product exposes and every principal that can reach
it, the outcome (status, exit code or error) and exactly which records and fields come back. The Architect writes the
matrix in `architecture.md` (security section); the Tester turns it into one data table plus executable tests at Plan &
Bind; the Auditor checks completeness and the negative cells. Applicability (`absd/playbook/testing/strategy.md`):
**M** web-ui, native-app, http-api · **R** cli (credentials/profiles) · **M** data-pipeline (service identity × dataset)
· **X** library (the host application owns access). Production-side rules (deny by default, object-level checks) are SEC
rules in `absd/playbook/security/baseline.md`; variation techniques are VAR rules in `absd/playbook/testing/test-design.md`.

## Checklist

- [ ] Every operation has a row; the build fails on an unruled operation or a stale row (ACCESS-1)
- [ ] Principals: anonymous, each role, an unknown role, expired at the boundary instant, suspended with a live token, impersonated, other owner, other tenant, service identity, admin-as-member (ACCESS-2)
- [ ] Permission-based access: each grant and deny override, and grant + deny on one principal in both orders (ACCESS-2)
- [ ] Every cell asserts status/exit AND visible records and fields; forbidden ones asserted absent (ACCESS-3)
- [ ] No allowed call ever ends in a 5xx, crash or unhandled error (ACCESS-3)
- [ ] One machine-readable matrix in one place, read by every test and report (ACCESS-4)
- [ ] Exports, reports, aggregates, search, files, subscriptions, webhooks, cached responses, job outputs are rows (ACCESS-5)
- [ ] Operations enumerated from the running system's own registry, never a hand list (ACCESS-6)
- [ ] Probe layer: unknown id + malformed body, stops before mutating, exact refusals, all failing cells reported (ACCESS-7)
- [ ] One refusal taxonomy per profile; no "A or B" oracle (ACCESS-8)
- [ ] Every id-bearing operation attacked by same-role other owner and other tenant; owner/role over-posting refused (ACCESS-9)
- [ ] Visibility table per read model: viewer × state × time, incl. every must-not-see cell (ACCESS-10)
- [ ] Truncated lists: below, at and above the limit; ties at the cut; the withheld count asserted (ACCESS-10)
- [ ] Suspend / downgrade / revoke / role change / delete / logout: the live token is refused on its next use (ACCESS-11)
- [ ] Impersonation: marker, refused account actions, way back, audit with real actor (ACCESS-12)
- [ ] Service identities reach only their declared datasets and operations (ACCESS-13)
- [ ] UI hides denied controls but the server still refuses; principal switch clears device data (ACCESS-14)
- [ ] A forbidden screen's URL or deep link opened directly, and back after sign-out, show no data (ACCESS-14)

## Rules

**ACCESS-1** — Give every operation a row in the Access & Visibility Matrix, and keep a build-time completeness test that fails when an operation exists without a row or a row names an operation that no longer exists.
- *Why:* authorization spread over annotations is forgotten on the next new operation, and a stale row hides a renamed one; the practice that worked was one table of every operation × every role with a build-failing completeness test (LL-35).
- *Check:* the test runs on every push in the default suite, diffs both directions and prints every missing and stale key; it is shown RED once by a negative control (an unruled operation) at Foundation; rows marked public equal the code's explicit allow-anonymous set. Brownfield: pre-existing operations may be `unverified` (DEBT burn-down); a new operation never is.
- *Applies when:* ACCESS is M or R in `TESTING.md`; with a single role the matrix is still required (anonymous vs signed-in).
- *Provenance:* LL-35 (KatenatsioTipster, 2026-10)

**ACCESS-2** — Build the principal dimension as role × entitlement state: anonymous; each role; an unknown role (a value the product does not define — from a stale token, an old directory entry or a hand-edited record — gets the least privilege, never a default role); each entitlement expired at the boundary instant (T−ε allowed, T as specified); suspended or deactivated while holding a valid token, session or key; impersonated; same-role other owner; other tenant; each service identity; an admin acting as an ordinary member. Where access is permission-based, each grant and deny override is a principal beside the role defaults, and a principal holding a grant and a deny for the same operation is tested with them applied in both orders (deny wins unless the spec says otherwise).
- *Why:* role-only matrices pass when the leak sits in the entitlement state or the owner relation — free accounts received paid content (LL-10); admins could not take part as members because nobody listed that principal (LL-5); unknown roles and override order were mined as untested dimensions (LL-57).
- *Check:* the matrix's principals equal `analysis.md`'s Actor × Capability principals × the entitlement states the product has (trace_check); each state is produced through real operations and the movable clock, never a forged token; absent states are N/A with a one-line reason; the unknown-role cell and both override orders have TCs. cli: principals are credential profiles (none, expired, read-only scope, full scope; flag vs env vs config file).
- *Applies when:* ACCESS applies; override order where access is permission-based.
- *Provenance:* LL-10, LL-5 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ACCESS-3** — Assert in every cell the outcome (status, exit code or error type) AND the visible records and fields; assert forbidden records and fields absent; an allowed call never produces a server error, crash or unhandled exception.
- *Why:* access was checked by status code per role while the response body of an allowed call carried paid content; read leaks are silent — nothing fails on screen (LL-10).
- *Check:* one TC per cell group (Gate T) with explicit contains / not-contains on record ids and field names; the Auditor rejects status-only cells and negative cells without an absence assertion; any 5xx, crash or non-documented exit on an allowed call fails the suite (as E2E-1 does end to end); removing any single authorization check or visibility filter makes ≥ 1 cell fail (GATE-5 mutation scope; Auditor fault injection per XCA rules in `absd/playbook/process/audits.md`).
- *Applies when:* ACCESS applies.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**ACCESS-4** — Keep the matrix as data in exactly one place in the test tree, with columns operation · principal · owner relation · resource state · flag state · expected outcome · visible records · visible and forbidden fields · requirement id; tests, the completeness check and the readable report all read that one table.
- *Why:* copies drift; a single reviewable table made the access policy auditable at a glance (LL-35).
- *Check:* one definition (grep); operation keys agree with `architecture.md`'s matrix (trace_check); expected outcomes are literals from analysis/design (ORACLE-1), never read back from the production policy configuration.
- *Applies when:* ACCESS applies.
- *Provenance:* LL-35 (KatenatsioTipster, 2026-10)
- Illustration: e.g. xUnit `[MemberData]` over a dictionary, pytest `parametrize` over a YAML file, Jest `test.each` over a JSON table.

**ACCESS-5** — Give its own row to every read and write, and also to exports and downloads, reports and aggregates (counts, totals, rankings), search and autocomplete, file and media links (incl. signed links), subscriptions and push channels (socket, server-sent events, topics), callbacks the product receives, responses served from any cache, and outputs a job sends to a principal (mail, notifications, generated files).
- *Why:* the leak was inside a response the role was allowed to fetch; side doors (an aggregate, an export, a cached body) are exactly where a per-endpoint check never looks (LL-10).
- *Check:* the Auditor compares the matrix with `architecture.md`'s interface inventory and with the ACCESS-6 enumeration; a list, report or export without a visibility row is Major.
- *Applies when:* ACCESS applies.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**ACCESS-6** — Enumerate operations for the completeness test from the running system's own registry (table below), never from a hand-kept list, and list any excluded category with a reason.
- *Why:* a hand list misses exactly the operation nobody remembered; even runtime enumeration had holes for routes without a verb restriction and routes outside the versioned prefix (LL-35).
- *Check:* the Auditor reads the enumeration code: runtime reflection, every method, every prefix, every fallback route; the negative control of ACCESS-1 proves it.
- *Applies when:* ACCESS applies.
- *Provenance:* LL-35 (KatenatsioTipster, 2026-10)
- Illustration: route tables via ASP.NET `EndpointDataSource`, Spring `RequestMappingHandlerMapping` or FastAPI/Express router lists; command trees via click, cobra or System.CommandLine.

| Profile | Source of operations | Row key |
|---|---|---|
| http-api, web-ui / native-app backends | router table at runtime: every method, verb-less and non-prefixed routes, socket hubs | `METHOD /route` |
| native-app | backend routes + deep links / intents the app registers | `link pattern` |
| cli | command registry: every command and subcommand touching credentials or protected data | `cmd sub --flag` |
| messaging | handler registry: every message type consumed or published | `topic:type` |
| data-pipeline | stage/job registry × datasets read and written (from the DAG or config) | `stage → dataset:mode` |
| library | X — public symbols only if the library itself enforces authorization | `Namespace.Symbol` |

**ACCESS-7** — Probe every cell over the real transport with inputs that cannot change state (an unknown id, a malformed body), so allowed callers stop in validation or lookup before any mutation while denied callers get the exact refusal; report every failing cell of an operation in one message.
- *Why:* one table then drives hundreds of real probes without building valid data per operation and without side effects, and proves authorization runs before validation; a never-5xx check on garbage input comes free (LL-35).
- *Check:* allowed → neither a refusal nor a 5xx; denied → the exact ACCESS-8 value; store snapshot (row counts) unchanged after the probe run. The probe proves access only: ACCESS-3 visibility and every allowed operation's behaviour still need tests on real seeded data.
- *Applies when:* the operation has a transport (http-api, backends, cli, messaging).
- *Provenance:* LL-35 (KatenatsioTipster, 2026-10)

**ACCESS-8** — Pin one refusal taxonomy per profile in `architecture.md`'s error catalogue (who are you? / not allowed this kind of operation / not yours or not visible) and assert the exact value, never "A or B"; "not yours" is indistinguishable from "does not exist".
- *Why:* mixing the meanings leaks existence ("this id exists but is not yours") or breaks clients; a test that accepted "404 or 403" pinned nothing.
- *Check:* the Auditor greps for alternative-status oracles; the other-owner answer is compared with the unknown-id answer (same status, same body shape). http-api: 401 / 403 / 404 (also flag off); cli: documented exit codes + stderr naming the fix, nothing on stdout; messaging and data-pipeline: refusal or dead letter with a documented reason code.
- *Applies when:* ACCESS applies.
- *Provenance:* industry baseline

**ACCESS-9** — For every operation that takes the id of an owned resource — in path, query, body, header, nested child or batch list — test a caller holding the permission but not the ownership (same role, other owner) and a caller from another tenant, expecting the "not yours" outcome and no change; forged owner, tenant or role fields in any body are ignored or refused.
- *Why:* a role matrix proves "members may edit entries", not "only their own"; insecure direct object references and self-escalation through self-service updates live at the instance level.
- *Check:* `test_plan.md` derives one object-level row per id-bearing operation and the Auditor counts them; stored owner and role unchanged after each attempt; sequential or guessable ids are tried.
- *Applies when:* resources have owners or tenants.
- *Provenance:* industry baseline

**ACCESS-10** — For every read model that filters by caller, write a visibility table viewer class × resource state × time (before, at and after each boundary) and test every cell that differs, including every must-not-see cell; the list, detail, search, counts, totals, exports, notifications and cached copies obey the same table. Where a principal sees a truncated list (top-N, a free-tier preview, a page limit), test below, at and above the limit, ties at the cut (the spec's tie rule decides who is shown), and the withheld count the principal is told — or that none is revealed.
- *Why:* free accounts saw paid content in a list they were allowed to read; counts reveal hidden records; a shared cache keyed without the principal serves one user's data to another (LL-10); cut-offs were tested without ties or the withheld count (LL-57).
- *Check:* a not-contains assertion exists per restricted viewer; boundary cells pin the clock at T−ε, T, T+ε (INTEG rules in `absd/playbook/testing/integration.md`, VAR-8); export content equals on-screen visibility for the same principal; principal A fetches, then principal B fetches the same resource and sees none of A's data, and private responses are marked non-shareable for caches; filters apply before pagination at Data Volume Profile max (VAR-7), and page counts reveal no hidden totals; metamorphic: where the spec orders tiers, a higher tier's visible set contains the lower tier's.
- *Applies when:* any read returns different content to different callers or over time; the truncation cases wherever a principal sees a limited list.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)

**ACCESS-11** — Make every entitlement change apply on the principal's next request: after suspend, deactivate, delete, downgrade, role change, permission revoke, credential reset or logout, the already-issued token, session, key or open subscription is refused (or served at the new level) on its next use, and restoration re-opens exactly what it should.
- *Why:* checks that trust claims inside an issued token keep a suspended or downgraded principal in until expiry; overrides were never proven to bite on a live session.
- *Check:* one TC per entitlement-changing action: obtain token → change → same token → expected refusal or reduced visible set; an open push channel stops delivering; a grant opens exactly the intended operations and nothing more; expiry at T−ε accepted, at T refused; tampered, wrong-audience, unsigned and expired tokens refused.
- *Applies when:* entitlements, roles or credentials can change while a session is live.
- *Provenance:* industry baseline

**ACCESS-12** — For impersonation, delegation or support access, test that the "acting as" marker is visible; account-level and security actions (credentials, keys, MFA, payment details, further impersonation) are refused while acting; self, nested and inactive-target impersonation are refused; the way back restores the original identity; the impersonation token expires as specified; and every action taken while acting is audited with both real actor and subject.
- *Why:* support access is a privilege-escalation path, and an audit check by substring could not prove who acted.
- *Check:* "impersonated" is a principal column for every operation, not one test; audit entries are asserted field by field (INTEG rules in `absd/playbook/testing/integration.md`).
- *Applies when:* the product lets one principal act as another.
- *Provenance:* industry baseline

**ACCESS-13** — Give every service identity (scheduled job, worker, integration, pipeline stage, deploy or CI token) its own least-privilege principal and test both what it may do and that it is refused everything else; pipeline outputs carry only the rows and columns each consumer may see.
- *Why:* jobs running as a superuser hide authorization defects and turn any job bug into a cross-tenant write.
- *Check:* data-pipeline matrix service identity × dataset × mode (read, write, delete); writing an undeclared dataset fails; downstream exports asserted free of forbidden columns (personal data per PRIV rules in `absd/playbook/security/baseline.md`).
- *Applies when:* data-pipeline (M), or any product with background work or machine credentials.
- *Provenance:* industry baseline

**ACCESS-14** — In web-ui and native-app, prove that the interface reflects the matrix without using it as the access test: a denied operation's control is absent (or disabled with the reason `design.md` specifies) while the server probe still refuses; a forbidden screen opened directly by URL or deep link shows the designed refusal and no data, not even briefly; switching principal clears rendered data, device caches and offline stores of the previous one, and back or forward after sign-out shows none of it.
- *Why:* a hidden button is not authorization, and screens or offline stores survive a principal switch unless a test says otherwise; deep links to forbidden screens and back after sign-out were mined as never automated (LL-57).
- *Check:* per-role e2e assertions by accessible name (E2E-2); one direct-URL or deep-link test per forbidden screen and principal class; a sign-out → back → sign-in-as-another test, online and offline, finds none of the previous principal's data.
- *Applies when:* web-ui, native-app.
- *Provenance:* industry baseline; LL-57 (ABSD v2 kit review, 2026-10)
