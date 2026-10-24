<!-- ABSD skeleton: copy to absd-project/working/brd.md; keep every heading (tools read them).
     Owner: manager. -->
# BRD — C### <slug>
Cycle: C### | Mode: F/S/C | Status: IN-PROGRESS/COMPLETE | Date: YYYY-MM-DD

## 1. Outcome
- Problem · who has it · desired outcome · observable success signal

## 2. Principals and devices
| Principal (context.md §1) | Affected how | Device / runtime classes | Source |
|---|---|---|---|

## 3. Capabilities (business language)
### 3.n <capability> — <principal>
- Need · value · the user's examples with concrete values · lifecycle and states · rules (§4 rows)

## 4. Business rules (verbatim)
| # | Rule as the user stated it | Worked example (inputs → result) | Boundaries and inclusivity |
|---|---|---|---|

## 5. Inherited behaviour to consider
| Source (prototype, legacy …) | Behaviour | Keep / change / remove / unknown | Suspected bug? |
|---|---|---|---|

## 6. External systems and facts
| System | Fact needed | Statement, by whom | UNVERIFIED / VERIFIED (EXT id) | Verification owner |
|---|---|---|---|---|

Money movements (ABSD:ELIC-22) — ask for every movement of money in scope (collection, refund full or partial,
payout, forfeit, fee); none → write "none — <reason>".

| Movement | Who pays whom, when | Refund (full / partial) and its timing | Failure and retry | Idempotency (same request twice) | Reconciliation (what is matched, how often) | Disputes / chargebacks | External system holding the money |
|---|---|---|---|---|---|---|---|

## 7. Quality expectations
- Volumes (max observed, real ordering) · speed (dataset, threshold) · privacy · notifications · audit trail ·
  concurrency · operability defaults wherever their *Applies when* covers the profiles (RULES rule 8), kept unless
  waived in §9

## 8. Out of scope

## 9. Decisions (answered by the user only)
| D | Question | Options shown | User's answer (verbatim) | Date | Affects |
|---|---|---|---|---|---|
- Gate 1 sign-off: actor × capability matrix, role value check, inherited behaviour inventory reviewed by the user on
  <date> — D-n … (ABSD:ELIC-21)

## 10. Open questions
| OQ | Question | Owner | Blocking? | Status |
|---|---|---|---|---|

## 11. Mode S brief (Mode S only)
| AC | GIVEN / WHEN / THEN with example values | Catalogue id |
|---|---|---|

## 12. Change Log
| CR | Date | Change (user's words) | Earliest affected artifact | Re-entry gate | Status |
|---|---|---|---|---|---|

## Traceability
| brd item | Requirement / AC ids (from analysis.md at G1) |
|---|---|
