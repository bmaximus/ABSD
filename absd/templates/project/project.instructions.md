---
applyTo: "<source and test globs from absd-project/context.md §3, e.g. src/**,tests/**>"
---

# Code in this repository

Follow, in this order:
1. `absd-project/context.md` §14 **Conventions** (naming, error model, API style, copy tone) and §3 **Source Layout &
   Ownership** (which agent owns which path).
2. The approved blueprint for the active cycle: `absd-project/working/architecture.md` — exact names, signatures,
   files and behaviour; any deviation is a halt, never an improvisation.
3. The ABSD playbook rules the blueprint cites (`absd/playbook/engineering/code-quality.md`,
   `absd/playbook/security/baseline.md`, and for tests `absd/playbook/testing/test-code.md`).

Never: suppression markers not listed in the architecture, secrets in source, expected values computed by calling
production code, skipped or weakened tests.
