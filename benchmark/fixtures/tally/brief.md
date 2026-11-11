# Tally — what I (the product owner) want

Product: Tally, a small Python library (import name tally) and a command-line tool (tally) that totals expense lines from plain text files — one line per expense, e.g. "2026-10-01; groceries; 23.40" — by category and by month, and prints a table or JSON. People run the CLI in a terminal; other scripts import the library.
Interfaces: cli and library (built as a wheel, installed with pip).
Users: me and a few friends on Linux and macOS terminals; scripts in pipelines use --json.
Locale: amounts are EUR with 2 decimals (never floating-point rounding errors); dates ISO 8601 (dates only, no times or zones); output in English with a decimal point.
Principals: none — a local tool with no accounts and no secrets.
Data volume: input files up to 100 000 lines.
External systems: none.
Deploy: build a wheel into dist/; a release is a wheel file plus a git tag; no package index and no CI service — run everything locally.
Stack: Python 3.13 in a venv, standard library only at runtime; tests with pytest and pytest-cov (pip works).
Design: CLI grammar "tally <command> [options]"; friendly, precise error messages that name the file and line; honours NO_COLOR; stable exit codes.
Repository: local git only, default branch main, no remote. Merge policy: standing authorization — merge a cycle branch into local main once Gate 3 passes.
Requirement area codes: TALLY (totals), PARSE (input parsing), OUT (output formats), BUDG (budgets, second cycle).
Standing answers: approve what the Manager recommends when its checks pass; I never accept a Critical or Major finding — fix them; technical choices are the team's; keep everything as small as the requirements allow.

## Feature for the first feature cycle

Totals by category and by month (area TALLY, with the PARSE and OUT basics it needs).

- `tally totals FILE...` reads one or more expense files and prints one row per month (YYYY-MM) and category with its
  total, sorted by month and then category, and a grand total line at the end. `--json` prints the same totals as JSON
  for my scripts.
- Input lines are `date; category; amount`. The amount is a positive number with exactly two decimals (23.40, not
  23.4). Blank lines and lines starting with `#` are skipped; any other line that does not fit is an error that names
  the file and the line number.
- "Groceries" and "groceries" are the same category — I type them both ways and I don't want two rows for my own
  typing.
- Refunds are written as negative amounts, e.g. `2026-10-03; groceries; -5.00`, and they reduce that category's total.
- I keep some of my files on my Windows laptop (I edit them in Notepad there) and copy them over, so those files have
  to work exactly like the others.
- A file with no expense lines prints an empty table and exits 0.
