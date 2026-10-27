# Requirement catalogue

> Living, owned by the Analyst (applied at Gate 1 from `analysis.md` "Catalogue delta"), NEVER archived.
> One row per product requirement in users' terms. Ids are permanent: never reused or renumbered — a superseded
> requirement gets Status `retired` and its successor id in the Source column. Tests link to these ids (`[AREA-n]` in the test name
> or a `requirement` property); `absd/tooling/traceability_report.py` reports each as verified, failing or untested,
> and fails on links to unknown or retired ids (`ABSD:TRACE-1`). Keep the header row exactly as below.

| ID | Area | Role | Story | Source | Status |
|---|---|---|---|---|---|
| <AREA-1> | <Area name> | <Principal> | <What the user can do / what must hold, in one sentence> | <C###> | active |
| <AREA-NF-1> | <Area name> | <Principal> | <Measurable quality: e.g. "answers within 500 ms at the max volume of the Data Volume Profile"> | <C###> | active |
| <AREA-BR-1> | <Area name> | <Principal> | <Business rule, stated with its boundary values> | <C###> | active |
