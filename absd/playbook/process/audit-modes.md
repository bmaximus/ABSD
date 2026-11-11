# Audit modes — architecture review, small change, cross-cycle, security, second auditor

Code **XCA** (reviews by mode). The Gate 2R architecture review (`arch_review.md`), the Mode S eligibility audit, the
cross-cycle audit (Mode X), the security review procedure at 2R and L5, and the optional second independent audit.
Evidence, levels, probes and severity: `absd/playbook/process/audits.md`.

## Checklist

- [ ] Gate 2R run on `absd/playbook/engineering/architecture-review.md`; the cycle audit reads only the resolution table (XCA-10)
- [ ] Mode S eligibility checked against the real diff, incl. added or removed public surface (XCA-11)
- [ ] Mode X held every 3 archived cycles and before every release, executed on the running system (XCA-12)
- [ ] Every cross-cycle lens applied with execution evidence (XCA-13)
- [ ] Security review procedure run: part A at 2R, part B at L5, each step with evidence (XCA-16)
- [ ] Money or permission cycle: second independent audit when the user chose it (XCA-17)

## Rules

**XCA-10** — At Gate 2R judge the blueprint against every row of the review checklist in
`absd/playbook/engineering/architecture-review.md` (technical excellence, security, testability, operability,
consistency with `analysis.md` and every recorded decision) and write AR findings with a resolution table. The post-build audit reads only that resolution table, not the 2R reasoning, and may raise new
architecture findings. The Architect may contest one AR with an ADR; if still disputed, the user decides.
- *Why:* nobody judged architecture quality, so a missing read, a dependency cycle and a reversed decision reached the
  Builder (LL-42, LL-44).
- *Check:* `arch_review.md` cites checklist items per AR; `audit.md` L1 cites the resolution table.
- *Applies when:* every Gate 2R (Mode S: on the delta).
- *Provenance:* LL-42, LL-44 (KatenatsioTipster, 2026-10)

**XCA-11** — In every Mode S audit compare the change with each eligibility criterion (ELIC-1) using the real diff — files
touched, schema, operations, config keys, flags, jobs, time and money code, and every screen, endpoint, command or
public symbol added or removed or interface contract changed — not the brief; copy and layout on an existing screen
stay eligible. Misclassification is a Major process finding and a LEDGER
candidate, and the cycle re-enters Mode F at the earliest affected artifact.
- *Why:* a light route without a mechanical check invites bypass by relabelling (LL-27); "touches a screen" made
  every honest visible Mode S a finding (LL-55).
- *Check:* `audit.md` L8 holds the criterion × diff evidence table.
- *Applies when:* Mode S.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10); LL-55 (ABSD v2 kit review, 2026-10)

**XCA-12** — Hold a cross-cycle audit (Mode X, `Scope: cross-cycle (C00a–C00b)`) every 3 archived cycles, before every
release (DOD-8) and on request. Inputs: the integration seams list, `context.md`, the code at HEAD and the catalogue —
not every archive. Execute, do not only read: run the product with each environment's default configuration, the
recorded contracts, the chain tests and the device projects; apply every lens of XCA-13.
- *Why:* a snapshot missing ~60% of the columns passed four per-cycle audits (LL-21); a static cross-cycle audit
  missed every defect needing real data, devices or responses (LL-1, LL-4).
- *Check:* `cycle.md` and `context.md` §15 show a Mode X within every 3 archived cycles and before each release.
- *Applies when:* ≥ 3 archived cycles since the last Mode X; before any release; after brownfield adoption (a v1
  project: once its Foundation-delta has closed).
- *Provenance:* LL-1, LL-4, LL-21 (KatenatsioTipster, 2026-10)

**XCA-13** — Apply each lens below with execution evidence and record a verdict per lens. Per-cycle audits compare code
with one cycle's spec, so a defect built from many correct-looking steps — a deferral repeated every cycle, a file no
agent owns, a default nobody runs, a binding made at start-up — only shows across the whole.
- *Why:* deferred migrations (LL-21), drifted docs and defaults (LL-22), a flag bound at start-up (LL-23), a
  half-implemented step (LL-51) and a stale context file (LL-54) were visible only across cycles.
- *Check:* `audit.md` has one section per lens with commands, outputs and findings.
- *Applies when:* every Mode X.
- *Provenance:* LL-21, LL-22, LL-23, LL-51, LL-54 (KatenatsioTipster, 2026-10)

| Lens | Execute | Accumulation it catches |
|---|---|---|
| Business chain trace | Each end-to-end chain (input → stored → derived → shown) run with a fresh case on the running system | steps specified once and lost later (LL-51) |
| Permissions sweep | Operations enumerated from the running system; matrix complete and run, incl. admin-as-member, impersonation, service identities | operations added cycle by cycle, checked by reading |
| Flags | Every flag at shipped defaults (off = inert) and in both states; toggles match the register's hot or restart | provider bound at start-up (LL-23) |
| Security & secrets | Whole repo + history scan, dependency audit, rotation of anything ever committed | a key outside a narrowed scope (LL-43) |
| Data invariants & migrations | Migrate from empty and from the previous release; model ↔ migration drift; constraints and invariant tests per catalogue BR | schema not reproducible (LL-21); derived value trusted (LL-48) |
| Runtime wiring | Boot the shipped artifact per environment's defaults; registrations, lifetimes, error handling, jobs scheduled once | broken default sign-in key (LL-22) |
| Interface cohesion | Gallery and outputs from different cycles side by side; one design system, formatter and convention set | mixed number formats (LL-19) |
| Docs, config & context drift | Fresh clone → running from the docs; config agreement; `context.md` vs repo (commands, stack, debt, cycles) | contradicting docs (LL-22); stale context (LL-54) |

### Security review, second auditor

**XCA-16** — Run the security review procedure (`absd/playbook/procedures/security-review.md`) on every cycle that
SEC-14 triggers: part A on the blueprint at Gate 2R, part B on the built product at L5; each step gets a verdict with
evidence in `arch_review.md` or `audit.md`, and a missing step is BLOCKED, never PASS.
- *Why:* security judged by a free-form read misses races, fetches, paths and model input; a checklist with evidence
  makes the review repeatable.
- *Check:* `arch_review.md` and `audit.md` L5 hold one row per procedure step with its evidence.
- *Applies when:* every cycle SEC-14 applies to (Mode S: on the delta).
- *Provenance:* LL-65 (ECC evaluation, 2026-11)

**XCA-17** — When the user chooses it (a brd Decision or `context.md` §14) for a cycle that changes money or
permission paths, run a second independent audit: a fresh Auditor invocation with the same brief and product SHA that
must not read the first audit's findings until its own are written, appended to `audit.md` as `## Second audit`; the
union of findings counts, and a class graded differently takes the higher severity (XCA-7). Model choice per PIPE-1:
a different strongest-level model when `context.md` §14 names two, else the same model in that fresh invocation.
- *Why:* one auditor's blind spot on the highest-cost paths survives every gate; independent review with the same
  rubric exposes it.
- *Check:* `audit.md` holds both audits at one product SHA; the second's evidence predates its reading of the first.
- *Applies when:* optional — money or permission changes, on the user's choice.
- *Provenance:* LL-65 (ECC evaluation, 2026-11); LL-68 (benchmark 2.4.0, 2026-11-11)
