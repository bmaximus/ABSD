# Ledger — what I (the product owner) want

Product: Ledger, a one-stage batch data pipeline: each night it reads a CSV export of shop orders (order_id, placed_at ISO 8601 with offset, customer_id, amount_eur with 2 decimals, status) and writes a daily sales summary CSV per shop day (Europe/Athens calendar day): orders, revenue, refunds, net.
Interfaces: data pipeline (input file → output file); run from the command line by a scheduler.
Users: the shop owner reads the output in a spreadsheet; the scheduler only checks the exit code.
Rules: money in integer cents, never floats; a malformed row goes to a rejects file with its line number and reason, the run still succeeds unless more than 1% of rows are rejected; re-running on the same input gives byte-identical output (idempotent).
Principals: none (local files). External systems: none. Data volume: up to 200 000 rows per night.
Deploy: a versioned folder run locally; no CI service — run everything locally.
Stack: Python 3.13 standard library only at runtime; tests with pytest (pip works).
Repository: local git only, default branch main, no remote. Merge policy: standing authorization — merge a cycle branch into local main once Gate 3 passes.
Requirement area codes: SUM (summary), INP (input), REJ (rejects), RET (returns handling, second cycle).
Standing answers: approve what the Manager recommends when its checks pass; I never accept a Critical or Major finding — fix them; technical choices are the team's; keep everything as small as the requirements allow.

## Feature for the first feature cycle

The nightly daily summary (areas SUM, INP and REJ).

- `ledger summarise INPUT.csv --out summary.csv --rejects rejects.csv` reads the export and writes one row per Athens
  calendar day, from the day of the earliest order to the day of the latest, with columns date, orders, revenue,
  refunds, net (EUR with 2 decimals in the file). A day with no orders gets a row of zeros, so the spreadsheet has no
  holes.
- The day an order belongs to is the Athens date of its placed_at, whatever offset the export wrote it with.
- Statuses: `paid` counts as an order and adds to revenue; `refunded` counts in refunds (the export writes the amount
  as a positive number); `cancelled` is left out. Those are the statuses the shop uses today. Net = revenue − refunds.
- When the upload to me fails half-way, the shop system sends the export again and both sends end up in the same
  night's file, so some orders appear in it twice.
- The rejects file lists line number, reason and the raw line; the run exits 1 when more than 1% of the rows are
  rejected, otherwise 0.
