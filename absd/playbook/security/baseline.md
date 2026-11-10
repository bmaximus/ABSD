# Security Baseline

Code **SEC**: production-side security controls per interface profile, plus products that call a model and the agent
configuration that builds them. The Architect designs them (ARCH-20, ARCH-21), the Builder implements, the Tester
proves each triggered rule with a TC, the Auditor judges at 2R and L5 (XCA-3, XCA-16). Privacy: PRIV
(`absd/playbook/security/privacy.md`); access tests: ACCESS rules, linked, not repeated; canary gate: GATE-13;
requirement lenses: ELIC-13, ELIC-23.

## Checklist

- [ ] Vetted identity provider or adaptive salted hashes; no enumeration (SEC-1)
- [ ] Lifetimes stated; claims validated; account state re-checked per request (SEC-2)
- [ ] Secret checks, metered calls rate-limited by a trusted key; safe lockout (SEC-3)
- [ ] Deny by default; owner/tenant scoped in the query; no mass assignment (SEC-4)
- [ ] Derived and server-owned values never from a client (SEC-5)
- [ ] Allow-list validation at every boundary, canonicalised; sizes capped (SEC-6)
- [ ] Parameterised queries, argument arrays, context encoding; fetches and paths per the hostile-input sets (SEC-7)
- [ ] Secrets only in a secret store, never in source, history, URLs, logs; leaks rotated (SEC-8)
- [ ] Settings printed by name; redaction tested; canary in every secret input (SEC-9)
- [ ] Transport and header baseline per profile, tested and scanned (SEC-10)
- [ ] Error bodies without internals; debug off in production (SEC-11)
- [ ] Security events logged with actor, correlation id, nothing secret (SEC-12)
- [ ] SCA, SAST, image scans; digests and commit hashes pinned; SBOM (SEC-13)
- [ ] Threat model per changed boundary: threat → mitigation → TC or RISK; parallel duplicate request (SEC-14)
- [ ] Model output untrusted: schema-checked, no own privilege, server-side approval before side effects (SEC-15)
- [ ] Agent configuration treated as code: no hidden characters, no remote fetch, pinned servers (SEC-16)

## Rules

### Identity and abuse

**SEC-1** — Prefer a vetted identity provider (ADR); checking passwords, store only an adaptive salted hash (Argon2id, scrypt, bcrypt or PBKDF2 at recommended cost, rehashed when raised), accept 8 to ≥ 64 characters without composition rules, refuse breached passwords, answer unknown account and wrong password identically in status, body and timing, draw temporary secrets from a CSPRNG; a credential change or reset refuses the old one and ends other sessions.
- *Why:* enumeration plus offline cracking turn one leaked store into many accounts.
- *Check:* TCs: hash format and cost; byte-equal unknown/wrong answers; breached password refused; old credential and other sessions refused (ACCESS-11).
- *Applies when:* the product authenticates principals.
- *Provenance:* industry baseline

**SEC-2** — State every token and session lifetime in `architecture.md` (defaults: access token ≤ 60 min, refresh token rotated with reuse detection, session idle ≤ 30 min, absolute ≤ 24 h); validate a pinned algorithm (never `none`), issuer, audience, expiry, not-before (≤ 60 s skew); signing and validation keys derived at one site from the secret store, rotated by key id; re-check account state (active, role, permissions, must-change) per request so suspension, downgrade and logout bite at once.
- *Why:* signer and validator derived the key apart; default-config sign-in broke (LL-22).
- *Check:* ACCESS-11 TCs (tampered, unsigned, wrong audience, expired at T, old token after a change); a blank key outside dev fails start-up.
- *Applies when:* tokens, sessions or API keys exist.
- *Provenance:* LL-22 (KatenatsioTipster, 2026-10)

**SEC-3** — Rate-limit every anonymous secret check, enumeration-prone lookup and metered dependency (OCR/LLM, mail, SMS, paid APIs) by a trustworthy key (account, API key, client address only via declared trusted proxies), answering 429 + `Retry-After` (cli, library: a typed error); after 5–10 consecutive failures back off exponentially or lock ≤ 15 min, keyed by account and client so nobody locks a victim out; notify the holder.
- *Why:* unlimited sign-in is a guessing oracle; uncapped metered calls a cost attack.
- *Check:* TCs at limit and limit + 1, production limits (FAKE-4); lockout, unlock; untrusted forwarding headers ignored.
- *Applies when:* http-api, web-ui, native backends; cli, library calling metered services.
- *Provenance:* industry baseline

### Authorization, input

**SEC-4** — Deny by default: a fallback policy demands an authenticated principal; anonymous access is an explicit allow-list equal to the matrix's public rows; one enforcing layer per rule (ARCH-20); owner and tenant scoped inside the store query, never filtered after fetch; input bound only to explicit input models, so owner, tenant, role, price and status cannot be mass-assigned.
- *Why:* per-endpoint, per-role access let an allowed call return paid content to free users (LL-10).
- *Check:* ACCESS-1, ACCESS-3, ACCESS-9, ACCESS-11 prove it; the Auditor diffs the anonymous allow-list with the matrix.
- *Applies when:* any principal distinction; library: the host enforces, the library validates inputs.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**SEC-5** — Never accept a derived or server-owned value from a client: totals, prices, scores, outcomes, statuses, authoritative times, owners, permissions come from their one server-side source (ARCH-3); a client copy is ignored or refused; contracts mark them server-owned.
- *Why:* a client-declared profit was trusted against a recompute rule; an audit rationalised it (LL-48).
- *Check:* forged-value TC per server-owned field (VAR-11); the Auditor reads each derived field's writes (XCA-6).
- *Applies when:* inputs carry derived, price, time, status or ownership fields.
- *Provenance:* LL-48 (KatenatsioTipster, 2026-10)

**SEC-6** — Validate every input where it enters (request parts, uploads, messages, webhooks, arguments, environment, config files, imports, external responses) against an allow-list schema (type, length, range, format, enum, cross-field) after canonicalising (Unicode, case, paths); reject with a catalogue code, never repair or default; cap request, file, page and decompressed sizes; deserialise only declared types (no type names from input, no XML entities); webhook signatures verified within a replay window; uploads checked by content.
- *Why:* "missing numbers fail validation" became "missing values become 0", past every gate (LL-44).
- *Check:* TC per validation rule; VAR-11 degenerate and hostile rows; size TCs at limit + 1; one validator per entry point.
- *Applies when:* always.
- *Provenance:* LL-44 (KatenatsioTipster, 2026-10)

**SEC-7** — Keep data out of code at every sink: parameterised queries only (SQL, document, search, directory; raw ORM queries too); processes started with argument arrays, never shell strings; CI and script inputs passed as environment data, never interpolated; template encoding per context (HTML, attribute, script, URL, CSS), raw-markup sinks only behind a sanitiser `architecture.md` lists; CR/LF stripped from header and mail fields; exported cells neutralise formulas; redirects allow-listed. A server-side fetch of an input URL parses it, allows only
listed schemes and hosts, refuses embedded credentials, checks every resolved address against private, loopback,
link-local and metadata ranges after resolution and again on each redirect (redirects off by default). A path from input
is canonicalised, then must stay under its base directory: absolute paths, `..`, NUL, links leaving the base and
reserved device names are refused.
- *Why:* one concatenated query or interpolated input turns data into action; an unchecked fetch reaches internal
  services and cloud metadata.
- *Check:* CODE-2 banned APIs, SAST at 0 (SEC-13); a hostile-payload TC per sink type (VAR-11), with the sets below.
- *Applies when:* always; the fetch and path sets when a sink takes a URL or path from input.
- *Provenance:* industry baseline; LL-65 (ECC evaluation, 2026-11)

| Sink | Hostile-input set (one TC each, all refused) |
|---|---|
| Server-side fetch | loopback name and address; `169.254.169.254`; private ranges; IPv6, decimal and octal forms of an internal address; `user:pass@host`; an unlisted scheme; a redirect to a private address; a host that resolves public, then private (fake resolver) |
| File path | `../` and encoded `..%2f`; absolute path; NUL byte; a link pointing outside the base; reserved device names; mixed separators |

### Secrets

**SEC-8** — Keep secrets out of source, history, images, bundles, URLs, logs, error bodies, artifacts: production reads a secret store (vault, KMS, platform secret manager); development uses throwaway values; production manifests require each secret, no default (FAKE-3); credentials in headers, never query strings; one derivation site per secret-derived value; rotation rehearsed; a leaked secret is rotated at once (deleting history does not un-leak it). Synthetic test secrets
(passwords, keys, tokens in tests and fixtures) come from named constants carrying a recognisable marker the secret
scan's reviewed allowlist names, never a realistic literal; evidence, reports and audit notes quote a scanner match
redacted (rule, file, line — never the value).
- *Why:* a secret survived in a legacy file outside a narrowed audit (LL-43); a key derived twice broke sign-in (LL-22).
- *Check:* a scanner (e.g. gitleaks, trufflehog) over tree and history every push (GATE-13) and by the Auditor (XCA-1); start-up refuses missing secrets.
- *Applies when:* any secret; library: never ships, logs, defaults one.
- *Provenance:* LL-43, LL-22 (KatenatsioTipster, 2026-10); LL-66 (ENR-14 acceptance of 2.2.0, 2026-11-10: audit
  evidence quoting test passwords tripped the repository's own scan)

**SEC-9** — Print configuration by name, never by value: every path printing settings, URLs, traces, environment, diffs or dry-run plans emits names, hashes, changed markers or values of an allow-list of non-secret keys (never a deny-list); framework logging of full URLs and headers off; every secret in every config input (env, files, manifests, CI variables) has a test canary; a canary in any log, report, artifact, diff or summary fails GATE-13.
- *Why:* a manifest secret reached a CI log via a dry-run diff (LL-8).
- *Check:* redaction TC per printing path; secrets planted as `k: v`, `k=v`, quoted, in a connection string, block scalar, auth header, beside a reference.
- *Applies when:* the product or its pipeline handles a secret.
- *Provenance:* LL-8 (KatenatsioTipster, 2026-10)

### Transport, errors, logs

**SEC-10** — Apply the baseline row of each declared profile (table), proven on the CI stack and post-deploy smoke.
- *Why:* clients enforce only what servers declare.
- *Check:* a TC per header and cookie attribute; no CORS grant to an unlisted origin; plain HTTP refused or redirected; a baseline scan (e.g. ZAP baseline, Nuclei) at 0 high.
- *Applies when:* per row of each declared profile.
- *Provenance:* industry baseline

| Profile | Baseline |
|---|---|
| all | TLS 1.2+ on every hop incl. stores; certificate checks never off by default; personal data encrypted at rest |
| web-ui | HSTS ≥ 1 year `includeSubDomains`; CSP with nonces or hashes, no `unsafe-inline`/`unsafe-eval`, `object-src 'none'`, `frame-ancestors` listed; `nosniff`; strict referrer policy; cookies `Secure` `HttpOnly` `SameSite` `__Host-`; CSRF defence on cookie-authenticated writes; no tokens in browser storage |
| http-api | CORS exact-origin allow-list, never `*` with credentials or a reflected origin; `no-store` on authenticated responses; strict content types; no version banner |
| native-app | platform transport security, no cleartext; tokens only in the OS keystore; pinning where the threat model names interception |
| cli | credentials from env, keychain or a user-only file, never in arguments or echoed; TLS verification on; insecure switches explicit, warned on stderr |
| library | safe defaults: verification on, timeouts set; insecure options opt-in, named so |
| data-pipeline | identity per stage (ACCESS-13); personal datasets encrypted in transit and at rest |

**SEC-11** — Return errors without internals: an unexpected failure answers the catalogue's generic body with a correlation id (ARCH-13), never a stack trace, query, path, class, internal id or version; debug pages, API explorers and verbose errors off in production; "not yours" equals "not found" (ACCESS-8).
- *Why:* internals in errors map the system for attackers.
- *Check:* TC per error class in production config: body schema, no internals, debug off.
- *Applies when:* every interface; cli: stderr names the fix; traces only behind a debug flag.
- *Provenance:* industry baseline

**SEC-12** — Log security events, nothing secret: sign-in outcomes, lockouts, refusals, entitlement changes, impersonation, key rotation, privileged writes, each with actor, real actor, subject, outcome, correlation id; never passwords, tokens, keys, session ids, payment data, personal data beyond a pseudonymous id (PRIV-6); structured fields, CR/LF in user values encoded; refusals below error level (OPS-7).
- *Why:* refusals logged as errors hid real faults (LL-15); a secret reached a CI log (LL-8).
- *Check:* log-capture TC per event type; SEC-9, PRIV-6 canaries; OPS-7 level TCs.
- *Applies when:* always.
- *Provenance:* LL-15, LL-8 (KatenatsioTipster, 2026-10)

### Supply chain, threats

**SEC-13** — Scan and pin the supply chain: dependency (SCA) and static (SAST) scans every push and nightly, failing on any fixable Critical or High (an exception is a RISK-n with expiry); images from minimal bases pinned by digest, non-root, no secret in a layer, scanned before release; an SBOM per release; third-party CI steps pinned by commit hash; least-privilege workflow tokens; untrusted contributions never run with secrets; updates enter through a mode (S; D for a vulnerability).
- *Why:* vulnerabilities appear without code changes; an unpinned step or image changes under a green commit.
- *Check:* scan reports at the audited product SHA attached at L5; every CI step pinned by hash, every image by digest (grep).
- *Applies when:* always; library: scans, SBOM of the published package.
- *Provenance:* industry baseline
- Illustration: e.g. CodeQL or Semgrep, Trivy or Grype, Dependabot or Renovate, CycloneDX or SPDX.

**SEC-14** — Threat-model every cycle that adds or changes a trust boundary, entry point, principal, secret or personal-data flow: one `architecture.md` row per threat (asset, entry point, STRIDE category, mitigation, TC or user-accepted RISK-n); per new operation walk at least: enumeration, brute force, other owner or tenant, forged fields, replay, token reuse, injection, cost exhaustion, oversized input, disclosure via exports, counts, caches or errors, impersonation misuse, a compromised dependency, a concurrent duplicate request (race, double spend, check-then-act),
server-side fetch and file path (SEC-7), injected model input (SEC-15). The Auditor runs the security review procedure
on it (XCA-16).
- *Why:* per-endpoint role checks missed a disclosure in an allowed response (LL-10); a balance checked without a lock
  pays twice under parallel requests (LL-65).
- *Check:* Gate T maps each threat and triggered SEC rule to a TC or RISK; at 2R a missing row is Major (Critical: auth, money, personal data); each money, entitlement or permission change has a TC that sends the same request in parallel and asserts exactly one effect (VAR-12).
- *Applies when:* every Mode F; Mode D when a defect crosses a boundary.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10); LL-65 (ECC evaluation, 2026-11)

### Models and agents

**SEC-15** — Treat a model's output as untrusted input: validate every returned value against a declared schema and
size (SEC-6) before it reaches a sink, a state change or a user; the model and its tools hold no credential or
permission beyond the calling principal's; where untrusted content, private data and an outbound channel meet, a
server-side allow-list or approval step stands between model and side effect — never a prompt instruction; money,
access and destructive actions never depend on model output alone.
- *Why:* instructions hidden in documents, mail, pages, images or tool results turn read access into actions.
- *Check:* `architecture.md` lists each model call with input sources, output schema and allowed side effects; TCs: an
  injected-instruction fixture (hidden text, invisible characters, inside an image or document) causes no out-of-schema
  output and no side effect; oversized or off-schema output is refused; eval sets per FAKE-13.
- *Applies when:* the product calls a model or exposes tools to one.
- *Provenance:* LL-65 (ECC evaluation, 2026-11)

**SEC-16** — Treat agent instructions and configuration (agent manuals, instruction files, procedures, hook and
permission settings, tool-server configuration, prompt templates) as code under SEC-13: no invisible or bidirectional
control characters and no hidden comment payloads; no hook or tool-server command that fetches or runs remote content;
tool servers, packages and images pinned by exact version or digest (a tag or bare name is High, a range Medium); no
setting that auto-approves project tool servers or redirects the model endpoint; the settings deny-list covers secret
paths, pipe-to-shell and remote copy.
- *Why:* agent configuration runs with the developer's rights; a hidden instruction or an unpinned server changes
  behaviour under a green commit.
- *Check:* a scan in CI and at L5 over those files for U+200B–U+200D, U+2060, U+FEFF, U+202A–U+202E, U+2066–U+2069,
  for fetch-and-run commands and for unpinned selectors; the kit runs the same scan on itself (`kit_lint`).
- *Applies when:* always — products and the kit.
- *Provenance:* LL-65 (ECC evaluation, 2026-11)
