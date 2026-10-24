<!-- ABSD skeleton: copy to absd-project/working/clarification_needed.md; keep every heading (tools read them).
     Owner: builder. -->
# Clarification needed — C### <slug>
Cycle: C### | Mode: … | Status: HALTED | ANSWERED | Date: YYYY-MM-DD
Inputs: architecture.md @<sha> · design.md @<sha> · test_plan.md @<latest T-SHA> · Builder pass <n>/3

## Halt <n>/3 — at WP-n (pre-generation scan | during WP-n | fix <ids>) — YYYY-MM-DD
- WP-start SHA: <sha> · your paths restored to it (`git diff --stat <sha> -- <globs>` and `git status --porcelain` empty)
- Kept (committed before the halt): WP-1 <sha> … | none · code of the halted WP: none

| CLR | Source (§ / id) | Quote (exact) | Kind | What is missing, contradictory or would have to deviate | Why you cannot proceed | Affects (WPs, files) | Owner of the cited text | Status |
|---|---|---|---|---|---|---|---|---|
| CLR-1 | architecture §6.4 step 3 | "round as appropriate" | vague | rounding mode and step unspecified for a money value | any choice decides a business rule | WP-2: <path> | Architect | open |

Kind: vague · missing · contradiction · impossible as written · unlisted need · unverified world fact
Status: open → answered <artifact> @<sha> §<x> (set by you on resume, after reading the answer)

## Summary
CLRs <n> (vague <n> · missing <n> · contradiction <n> · impossible <n> · unlisted <n> · unverified <n>) ·
Required: each owner answers in its own artifact; its gate re-passes (changed TCs: a re-bind adds a T-SHA to the
chain in cycle.md); the Manager re-invokes Build at WP-n.

## Traceability
| Upstream id (requirement · AC · UJ · SCR · EXT) | CLRs | WPs blocked |
|---|---|---|
