# ABSD kit repository — Copilot instructions (maintainers)

This repository **is** the ABSD kit, not a product: `absd/RULES.md` describes how the agents behave in product
repositories and is not an active rule set here. Do not start pipeline cycles in this repository.

When changing the kit, follow `CLAUDE.md` (maintainer guide) and `absd/playbook/process/enrichment.md` ("ABSD side"):
proposal in `absd/lessons/inbox/`, rule with id and provenance, ledger entry, changelog, version bump, then

```bash
python3 absd/tooling/absd_sync.py manifest --root .
python3 absd/tooling/kit_lint.py --root .
python3 -m unittest discover -s absd/tooling -p 'test_*.py'
```

The product-side Copilot instructions are the template `absd/templates/project/copilot-instructions.md`.
