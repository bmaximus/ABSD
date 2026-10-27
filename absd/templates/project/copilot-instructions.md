# <Product name> — Copilot instructions

This repository is built with the **ABSD pipeline**. Before any work, read `absd/RULES.md` (the canonical rules) and
`absd-project/context.md` (the product's living memory: stack, source layout and ownership, conventions).

- Pipeline work starts from the **Manager** custom agent (`.github/agents/Manager.agent.md`); the other agents are
  invoked only through the Manager's handoffs, each with an invocation brief (`absd/templates/briefs/invocation-brief.md`).
- Production code is written only by the Builder, tests only by the Tester, per the ownership table in
  `absd-project/context.md` §3 — never both by the same agent.
- No production code before Gates 2, 2R and T have passed; tests and their expected values come before code.
- `absd/` is the vendored kit: read-only here. Improvements go into `absd-project/lessons.md` as enrichment proposals.
- Conventions live in `absd-project/context.md` §14 — follow them; do not restate them here.
