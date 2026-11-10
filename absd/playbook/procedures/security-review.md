# Procedure — security review (Gate 2R and L5)

Loaded on demand: the Auditor opens this file when XCA-16 applies (a cycle SEC-14 triggers), not before. It defines
steps, never rules: each step cites the rules it checks. Part A runs on `architecture.md` at Gate 2R; part B on the
built product at the audited product SHA, inside L5. Record one row per step — step, verdict (OK, AR-n or F-n, N/A with
its reason), evidence — in `arch_review.md` §3 or `audit.md` L5. A step you could not run is BLOCKED, never PASS.

Inputs the Analyst and Architect provide: abuse cases per feature touching sign-in, money, personal data, uploads or
external input (ELIC-23); the threat table (SEC-14); the model-call table (SEC-15); the security section of each work
package (ARCH-24).

## Part A — design review at Gate 2R

| # | Step | Evidence | Rules |
|---|---|---|---|
| A1 | Threat coverage: every new or changed trust boundary, entry point, principal, secret and personal-data flow has a threat row; every row → mitigation → named TC or user-accepted RISK-n with expiry; every abuse case maps to a threat row | boundary list vs threat table; orphan rows | SEC-14, ELIC-23 |
| A2 | Walk list complete per new operation, including concurrent duplicate request (race, double spend), server-side fetch, file path, model output and injected content, compromised dependency | operation × walk-item table, no blank cell | SEC-14, SEC-7, SEC-15 |
| A3 | Access matrix: a row for every operation incl. exports, counts and aggregates; every entitlement state; deny by default stated with the anonymous allow-list | operations listed vs matrix rows | ACCESS-1, ACCESS-5, SEC-4 |
| A4 | Injection points: each sink names its parameterisation or encoding; each fetch and path sink its hostile-input set; server-owned values listed | sink list vs SEC-7 table | SEC-5, SEC-7 |
| A5 | Secrets: each has its store, is required at start and printed by name; no secret-derived value derived twice | secret list | SEC-8, SEC-9 |
| A6 | Model calls: input sources, output schema, allowed side effects, the approval step where untrusted content, private data and an outbound channel meet | model-call table | SEC-15 |
| A7 | CI declares dependency, static, secret, image and baseline dynamic scans plus the agent-configuration scan, each with its fail level | CI section of the blueprint | SEC-13, SEC-16 |
| A8 | Each work package names its security section: threat rows, sinks, secrets and model calls it touches | WP table | ARCH-24 |

## Part B — evidence at L5 (thin checklist, evidence over opinion)

| # | Step | Evidence | Rules |
|---|---|---|---|
| B1 | Scanner results at the audited product SHA: secret scan over tree and history, dependency, static and image scans at 0 open Critical/High (or a RISK), baseline dynamic scan at 0 high, agent-configuration scan clean | report paths, exit codes | SEC-8, SEC-13, SEC-16, XCA-1 |
| B2 | Every threat row's TC and every abuse case's TC exists and passed in your own run | threat → TC → result table | SEC-14, ELIC-23 |
| B3 | The parallel duplicate-request TC per money, entitlement or permission change asserts exactly one effect | TC ids, results | SEC-14, VAR-12 |
| B4 | Access completeness test enumerates the running system's operations; cells assert status and visible fields; a suspended principal's live token is refused | test output | ACCESS-3, ACCESS-6, ACCESS-11 |
| B5 | Manual pass over the diff's high-risk sinks (sign-in, money, uploads, fetches, files, model calls, webhooks): each finding proven and labelled by reachability | finding rows | XCA-14 |
| B6 | Planted secret canaries and the canary person absent from logs, error bodies, reports and CI output | canary scan output | SEC-9, GATE-13, PRIV-6 |

Report every finding with its rule id in the artifact; fix nothing (Auditor contract).
