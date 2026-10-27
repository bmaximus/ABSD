# Architecture review (Gate 2R)

Code **ARCH** (review side) with XCA-10: the checklist the Auditor applies to `architecture.md` at Gate 2R
(`arch_review.md`), on the full blueprint in Mode F and on the delta in Modes S, D and C. The rules themselves live in
`absd/playbook/engineering/architecture.md`; the review procedure, independence and severity calibration in
`absd/playbook/process/audits.md` (XCA-7, XCA-10). The post-build audit reads only the 2R resolution table (L1).

## Checklist

The Auditor checks each row against its rules, records each miss as an AR citing `ABSD:ARCH-n`, may raise a severity,
never lowers one; `arch_review.md` states `Verdict: PASS | FAIL | N/A` on a line outside any table.

| Item | Severity if missing | Rules |
|---|---|---|
| Dependency direction | Major | ARCH-1, ARCH-2 |
| Decisions honoured | Major | ARCH-7 |
| Blueprint | Major | ARCH-8 |
| Reads | Major | ARCH-9 |
| Derived values | Critical on money, else Major | ARCH-3 |
| Seams & harness; TSEAM answered by kind; test tooling in Tester-owned files or listed shared sections | Major | ARCH-11, ARCH-12, GATE-7 |
| Migrations | Major | ARCH-15 |
| Error catalogue | Major | ARCH-13 |
| Access matrix | Critical | ARCH-20 |
| Threat model | Major; Critical for auth, money, personal data | ARCH-20 |
| External facts | Critical | ARCH-14, ARCH-19 |
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
