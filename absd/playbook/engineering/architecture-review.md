# Architecture review (Gate 2R)

Code **ARCH** (review side) with XCA-10: the checklist the Auditor applies to `architecture.md` at Gate 2R
(`arch_review.md`), on the full blueprint in Mode F and on the delta in Modes S, D and C. The rules themselves live in
`absd/playbook/engineering/architecture.md`, except ARCH-26 (the loop's convergence, below); the review procedure,
independence and severity calibration in
`absd/playbook/process/audits.md` (XCA-7) and `absd/playbook/process/audit-modes.md` (XCA-10, XCA-16). The post-build audit reads only the 2R resolution table (L1).

## Checklist

The Auditor checks each row against its rules, records each miss as an AR citing `ABSD:ARCH-n`, may raise a severity,
never lowers one; `arch_review.md` states `Verdict: PASS | FAIL | N/A` on a line outside any table.

| Item | Severity if missing | Rules |
|---|---|---|
| Dependency direction | Major | ARCH-1, ARCH-2 |
| Decisions honoured | Major | ARCH-7 |
| Worked-number ACs replayed through the specified algorithm, every reachable order and edge, same result | Major; Critical on money | ARCH-7, ORACLE-6 |
| Blueprint | Major | ARCH-8 |
| Reads | Major | ARCH-9 |
| Derived values | Critical on money, else Major | ARCH-3 |
| Seams & harness; TSEAM answered by kind; test tooling in Tester-owned files or listed shared sections | Major | ARCH-11, ARCH-12, GATE-7 |
| Migrations | Major | ARCH-15 |
| Error catalogue | Major | ARCH-13 |
| Access matrix | Critical | ARCH-20 |
| Threat model | Major; Critical for auth, money, personal data | ARCH-20 |
| Security review procedure part A (walk list incl. race, fetch, paths, model input; matrix; sinks; secrets; CI scanners) | Major; Critical for auth, money, personal data | XCA-16, SEC-14, SEC-15, SEC-16 |
| Entity states: one state per lifecycle, invalid combinations unconstructible | Major; Critical on money | CODE-15 |
| Security section per WP | Major | ARCH-24 |
| External facts (none left to be verified by a WP or by the Builder) | Critical | ARCH-14, ARCH-19, ARCH-26 |
| Configuration | Major | ARCH-14 |
| Flags | Major | ARCH-18 |
| Concurrency, idempotency, jobs | Major; Critical on money | ARCH-16, ARCH-17 |
| Observability | Major | ARCH-21 |
| Data flows | Major | ARCH-10 |
| Work packages | Major | ARCH-24 |
| YAGNI vs correctness; every operability default in its OPS scope specified or user-waived | Major; Critical on money or access | ARCH-5, ARCH-6 |
| N/A vs applicability | Major | STRAT-4, ARCH-22 |
| Public names of cli, http-api, library adopted verbatim from `design.md` and bound in §5.0 | Major | ARCH-25, DSN-18 |
| Profiles, ADRs, markers | Major | ARCH-22, ARCH-23, ARCH-25 |
| Round ≥ 2: each new AR tagged with its origin; fix-added mechanism named in §0.3 | Major | ARCH-26 |

## Rules

**ARCH-26** — Make the Gate 2R loop converge. The Architect answers an AR with the smallest change that closes it:
narrow or remove behaviour before adding mechanism, and list each component, state, file, job or recovery path a fix
adds in §0.3 as "added mechanism". After a delta it re-reads every edited section end to end (numbering, lists,
cross-references). From round 2 the Auditor tags each new AR with its origin: `fix` (text the previous delta added),
`missed` (text an earlier round passed) or `upstream` (a changed input). When half or more of a round's new Critical
and Major ARs are `fix`, the loop is diverging: the Manager escalates at once (RULES §2), and the options include
simplifying — the Analyst narrows the requirement that drives the mechanism (for example a documented manual recovery
step instead of automatic crash recovery), recorded as a decision. A blueprint never defers an external fact's
verification to a work package or to the Builder; an unverified fact is behind a flag off everywhere, or it is an AR.
- *Why:* in the 2.7.0 benchmark one fixture failed Gate 2R five rounds running; each fix (a restore journal, then its
  recovery, then recovery of an unreadable journal) added text the next round faulted, and the cycle was parked. A
  deferred fact check passed the gate and halted the Builder (LL-75).
- *Check:* every round ≥ 2 AR row carries an origin; `cycle.md` shows an escalation with a simplify option at the
  first diverging round; §0.3 lists added mechanism per AR; no section says a fact is verified "by WP-n".
- *Applies when:* every Gate 2R with more than one round; the deferral clause at every Gate 2R.
- *Provenance:* LL-75 (ABSD 2.7.0 benchmark, 2026-11-18)
