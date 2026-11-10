# Privacy Baseline

Code **PRIV**: personal-data controls for every interface profile. The Analyst lists the delta (ELIC-13), the Architect
designs locations and mechanisms (ARCH-20, ARCH-21), the Builder implements, the Tester proves each triggered rule with
a TC, the Auditor judges at 2R and L5 (XCA-3). Security controls: SEC (`absd/playbook/security/baseline.md`); access
tests: ACCESS rules.

## Checklist

- [ ] Personal-data inventory: purpose, basis, retention, locations, viewers (PRIV-1)
- [ ] Deletion reaches logs, processors, backups; restore re-applies it (PRIV-2)
- [ ] Complete, own-data-only export via a short-lived link (PRIV-3)
- [ ] Consent per purpose recorded, off until given, withdrawal immediate (PRIV-4)
- [ ] Only needed fields collected and returned; outbound ids opaque (PRIV-5)
- [ ] No personal data in logs, analytics, URLs, CI output; canary person (PRIV-6)
- [ ] Synthetic test data; snapshots only anonymised, user-approved (PRIV-7)
- [ ] Privileged reads of others' data in a declared access log (PRIV-8)

## Rules

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
