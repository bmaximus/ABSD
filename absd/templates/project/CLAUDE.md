@absd/RULES.md
@absd-project/context.md

# <Product name>

This repository is built with the ABSD pipeline (`absd/`, vendored and read-only — upgrade it with
`absd/tooling/absd_sync.py`, never edit it here).

**To build anything, run the Manager as the main conversation:** `claude --agent manager` (or keep
`"agent": "manager"` in `.claude/settings.json`). A session that is not the Manager does not change product code or
tests: it tells the user how to start the Manager. Workers (analyst, designer, architect, tester, builder, auditor) are
invoked only by the Manager with an invocation brief.

Product-specific guidance for humans and agents goes below this line; conventions belong in
`absd-project/context.md` §14 (single home).
