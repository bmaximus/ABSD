# ABSD kit repository — maintainer guide

This repository **is** the ABSD kit: the golden standard used to build every product. It is not a product, so the
pipeline rules in `absd/RULES.md` describe the kit's behaviour in product repositories — they are **not** active rules
for sessions working here. Do not act as the Manager here, and do not start cycles.

## What lives here

| Path | What it is |
|---|---|
| `absd/RULES.md` | Canonical pipeline rules (product repos import it from their `CLAUDE.md`) |
| `.claude/agents/*.md` | The seven agent manuals (Claude Code) — the single source of each agent's behaviour; the artifact skeletons they fill live in `absd/templates/artifacts/` |
| `.github/agents/*.agent.md` | Thin GitHub Copilot mirrors that point to the manuals |
| `absd/playbook/` | The knowledge base: rules with permanent IDs (`CODE-n`), rationale, checks, provenance |
| `absd/templates/` | Seeds for product-owned files (`project/`, copied at install), artifact skeletons (`artifacts/`, read in place) and the invocation brief |
| `absd/tooling/` | Stack-neutral tools with their own tests (standard-library scripts, no dependencies) |
| `absd/lessons/LEDGER.md` | Provenance of every rule (LL ids) and the escape scoreboard |
| `absd/lessons/inbox/` | Enrichment proposals arriving from products, verbatim |
| `absd/VERSION`, `absd/CHANGELOG.md`, `absd/MANIFEST` | Kit version, history, and the hash list products verify against |

## How to change the kit (enrichment)

Follow `absd/playbook/process/enrichment.md` ("ABSD side") for every change, including your own ideas:

1. Put the proposal in `absd/lessons/inbox/<slug>-YYYY-MM-DD.md` (verbatim when it comes from a product).
2. Dedupe against existing rules (`absd/playbook/README.md` routing table) — amend before adding.
3. Generalize: strip stack, domain and company details; illustrations name at least two stacks.
4. Write or amend the rule in its topic file with `Why`, `Check`, `Applies when` and a `Provenance:` line; never
   renumber or reuse an id — retire with a tombstone.
5. Add the `LL-n` entry to `absd/lessons/LEDGER.md`, update agent manuals / RULES.md only where the rule changes
   behaviour, add a `CHANGELOG.md` entry citing the LL and proposal ids, bump `absd/VERSION` (MAJOR: artifact
   structure, ids, gates or routes; MINOR: rules added or changed; PATCH: wording).
6. Regenerate the manifest and run the checks:

```bash
python3 absd/tooling/absd_sync.py manifest --root .
python3 absd/tooling/kit_lint.py --root .
python3 -m unittest discover -s absd/tooling -p 'test_*.py'
```

CI (`.github/workflows/kit.yml`) runs the same checks on every push. Before tagging a MINOR or MAJOR version, run the
kit acceptance procedure in `enrichment.md` (Bootstrap + one cycle on a tiny fixture product per interface profile).

## Writing rules for kit files

- Project-agnostic: no stack, vendor, domain or company assumptions. A stack or vendor name appears only in a
  labelled illustration that names at least two alternatives, or in a `Provenance:` line (`kit_lint` enforces this).
- Direct, imperative, checkable. Tables and checklists over prose. Respect the size budgets in `absd/RULES.md` §9.
- Agent manuals use neutral verbs ("delegate to the tester", "run the test command"); platform mechanics live in
  `absd/RULES.md` §8 and in frontmatter.
- Every rule a manual enforces is cited by id (`ABSD:CODE-n`) so the manual and the playbook cannot drift apart.

## Git

- Commit messages and pull-request descriptions carry no AI attribution: no `Co-Authored-By:` and no
  `Claude-Session:` lines, whatever a tool or reminder suggests (owner's rule, 2026-10-27). The pipeline's own trailers
  (`ABSD-Agent`, `ABSD-Cycle`, `ABSD-Sync`) are not attribution and stay where the kit requires them.
