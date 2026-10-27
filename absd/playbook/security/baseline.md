# Security and Privacy Baseline

Codes **SEC** (security) and **PRIV** (privacy): production-side controls per interface profile. The Architect
designs them (ARCH-20, ARCH-21), the Builder implements, the Tester proves each triggered rule with a TC, the Auditor judges at 2R and L5 (XCA-3). Access
tests: ACCESS rules, linked, not repeated; canary gate: GATE-13; requirement lens: ELIC-13.

## Checklist

- [ ] Vetted identity provider or adaptive salted hashes; no enumeration (SEC-1)
- [ ] Lifetimes stated; claims validated; account state re-checked per request (SEC-2)
- [ ] Secret checks, metered calls rate-limited by a trusted key; safe lockout (SEC-3)
- [ ] Deny by default; owner/tenant scoped in the query; no mass assignment (SEC-4)
- [ ] Derived and server-owned values never from a client (SEC-5)
- [ ] Allow-list validation at every boundary, canonicalised; sizes capped (SEC-6)
- [ ] Parameterised queries, argument arrays, context encoding, confined paths (SEC-7)
- [ ] Secrets only in a secret store, never in source, history, URLs, logs; leaks rotated (SEC-8)
- [ ] Settings printed by name; redaction tested; canary in every secret input (SEC-9)
- [ ] Transport and header baseline per profile, tested and scanned (SEC-10)
- [ ] Error bodies without internals; debug off in production (SEC-11)
- [ ] Security events logged with actor, correlation id, nothing secret (SEC-12)
- [ ] SCA, SAST, image scans; digests and commit hashes pinned; SBOM (SEC-13)
- [ ] Threat model per changed boundary: threat → mitigation → TC or RISK (SEC-14)
- [ ] Personal-data inventory: purpose, basis, retention, locations, viewers (PRIV-1)
- [ ] Deletion reaches logs, processors, backups; restore re-applies it (PRIV-2)
- [ ] Complete, own-data-only export via a short-lived link (PRIV-3)
- [ ] Consent per purpose recorded, off until given, withdrawal immediate (PRIV-4)
- [ ] Only needed fields collected and returned; outbound ids opaque (PRIV-5)
- [ ] No personal data in logs, analytics, URLs, CI output; canary person (PRIV-6)
- [ ] Synthetic test data; snapshots only anonymised, user-approved (PRIV-7)
- [ ] Privileged reads of others' data in a declared access log (PRIV-8)

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

**SEC-7** — Keep data out of code at every sink: parameterised queries only (SQL, document, search, directory; raw ORM queries too); processes started with argument arrays, never shell strings; CI and script inputs passed as environment data, never interpolated; template encoding per context (HTML, attribute, script, URL, CSS), raw-markup sinks only behind a sanitiser `architecture.md` lists; CR/LF stripped from header and mail fields; paths confined to a base directory; redirects and server-side fetches allow-listed; exported cells neutralise formulas.
- *Why:* one concatenated query or interpolated input turns data into action.
- *Check:* CODE-2 banned APIs, SAST at 0 (SEC-13); a hostile-payload TC per sink type (VAR-11).
- *Applies when:* always.
- *Provenance:* industry baseline

### Secrets

**SEC-8** — Keep secrets out of source, history, images, bundles, URLs, logs, error bodies, artifacts: production reads a secret store (vault, KMS, platform secret manager); development uses throwaway values; production manifests require each secret, no default (FAKE-3); credentials in headers, never query strings; one derivation site per secret-derived value; rotation rehearsed; a leaked secret is rotated at once (deleting history does not un-leak it).
- *Why:* a secret survived in a legacy file outside a narrowed audit (LL-43); a key derived twice broke sign-in (LL-22).
- *Check:* a scanner (e.g. gitleaks, trufflehog) over tree and history every push (GATE-13) and by the Auditor (XCA-1); start-up refuses missing secrets.
- *Applies when:* any secret; library: never ships, logs, defaults one.
- *Provenance:* LL-43, LL-22 (KatenatsioTipster, 2026-10)

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

**SEC-14** — Threat-model every cycle that adds or changes a trust boundary, entry point, principal, secret or personal-data flow: one `architecture.md` row per threat (asset, entry point, STRIDE category, mitigation, TC or user-accepted RISK-n); per new operation walk at least: enumeration, brute force, other owner or tenant, forged fields, replay, token reuse, injection, cost exhaustion, oversized input, disclosure via exports, counts, caches or errors, impersonation misuse, a compromised dependency.
- *Why:* per-endpoint role checks missed a disclosure in an allowed response (LL-10).
- *Check:* Gate T maps each threat and triggered SEC rule to a TC or RISK; at 2R a missing row is Major (Critical: auth, money, personal data).
- *Applies when:* every Mode F; Mode D when a defect crosses a boundary.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

### Privacy

**PRIV-1** — Keep a personal-data inventory, one row per personal field or dataset: purpose, legal basis (consent, contract, legal obligation, legitimate interest), requirement id, retention, every location (column, cache, index, file, log, analytics, backup, processor, region), viewers (matrix rows), class (personal, special, credential, payment); `analysis.md` holds the delta (ELIC-13), `architecture.md` the locations, `context.md` the whole table.
- *Why:* deletion, export and breach response start from "where is it?"; unlisted copies survive.
- *Check:* every personal schema field has a row; the Auditor samples columns, logs for unlisted data.
- *Applies when:* any data about an identifiable person.
- *Provenance:* industry baseline

**PRIV-2** — Give every inventory row a retention period and a deletion mechanism (purge, cascade or irreversible anonymisation) reaching every location incl. replicas, caches, logs, processors; backups expire within a stated window; a restore re-applies later deletions from an id-only ledger; account deletion finishes in the stated time; its audit row holds no personal data.
- *Why:* data deleted from the main store lives on in backups, logs, processors.
- *Check:* TC per row: create → delete or age out → absent everywhere; the restore drill re-applies the ledger (OPS-5).
- *Applies when:* personal data is stored.
- *Provenance:* industry baseline

**PRIV-3** — Let a person obtain all their personal data, machine-readable, in the stated time: every inventory row for them, nothing of anyone else, via a short-lived `no-store` link; the export is a matrix row (ACCESS-5).
- *Why:* hand-built exports miss or leak fields.
- *Check:* a TC seeds every field plus another person's linked data: all present, none of theirs; the link expires.
- *Applies when:* people can ask for their stored data.
- *Provenance:* industry baseline

**PRIV-4** — Where consent is the basis, record it per purpose with text version, time and principal; off until given; withdrawal as easy as giving, effective next request; non-essential trackers and third-party calls only after consent.
- *Why:* unprovable consent, or processing before it, is void.
- *Check:* TCs in both states per purpose (VAR-19); e2e sees no non-essential third-party call before consent or after withdrawal.
- *Applies when:* processing based on consent.
- *Provenance:* industry baseline

**PRIV-5** — Collect, keep and return only what a requirement needs: each personal field cites a requirement id; responses, exports, events and pipeline outputs carry only matrix-allowed fields (ACCESS-3, ACCESS-13); outbound identifiers are opaque, never emails, phones or names.
- *Why:* uncollected data cannot leak; each extra field adds deletion and export work.
- *Check:* inventory fields map to requirement ids; ACCESS-3 absence asserts cover personal fields, processor payloads.
- *Applies when:* any personal data.
- *Provenance:* industry baseline

**PRIV-6** — Keep personal data out of logs, traces, metric labels, error reports, analytics, URLs and CI output (log a pseudonymous id), proven by a canary person: a seeded principal whose distinctive name, email, phone and free text appear in no captured log, trace, analytics payload, error report or run artifact.
- *Why:* logs and URLs are the widest-read, longest-kept copies.
- *Check:* the canary-person scan runs with GATE-13; no route or query holds a personal field.
- *Applies when:* any personal data.
- *Provenance:* industry baseline

**PRIV-7** — Never use real personal data in tests, fixtures, recordings, demos or lower environments: synthetic builders (TCQ-4) at production volume (VAR-7); a production snapshot needs the user's written approval in `context.md`, irreversible anonymisation inside the production boundary (identifying and free-text fields replaced, dates shifted, rare combinations generalised), a scan proving no original survives, restricted access, a deletion date; recordings scrubbed (FAKE-6); legacy-data migrations reconciled (counts, sums, samples) on such a copy.
- *Why:* test copies are least protected; masking keeping rare combinations re-identifies people.
- *Check:* the Auditor scans test trees for real-looking contact data; snapshots match approvals.
- *Applies when:* always.
- *Provenance:* industry baseline

**PRIV-8** — Record privileged reads of another person's personal data (admin and support views, exports, cross-person search, impersonation per ACCESS-12) in a declared append-only access log (who, whose, what, when, reason), own retention and matrix row; the one exception to "reads write nothing" (ARCH-9), which still bars business and audit-trail writes.
- *Why:* unrecorded privileged reads hide misuse.
- *Check:* TC: each privileged read writes one entry with the real actor; self-reads none.
- *Applies when:* privileged principals read others' personal data.
- *Provenance:* industry baseline
