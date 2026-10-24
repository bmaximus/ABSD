# Enrichment — every product makes the kit better

Code **ENR**. How lessons flow from products into the kit and back. Product side: harvest into `absd-project/lessons.md`,
proposals, local kit edits. ABSD side: inbox → dedupe → generalize → decide → LEDGER → rule → manuals → CHANGELOG →
version → manifest and checks → kit acceptance run. Escaped defects reach `lessons.md` through ESC-9. A session in the
ABSD repository follows this file as maintainer (its `CLAUDE.md`), never as the Manager.

## Checklist

- [ ] Every finding class, escape, halt, conflict, extra gate round and user correction harvested and classified (ENR-1)
- [ ] Every `ESCAPED-DEFECTS.md` row closed: playbook change proposed, or enforcement change (ENR-1)
- [ ] `lessons.md` rows keep permanent ids, evidence, target and one of the five statuses; nothing deleted (ENR-2)
- [ ] Universal rows cut into a proposal file at Harvest, delivered to the inbox, marked sent (ENR-3)
- [ ] No local kit edit survives; each became a lesson and the file returned to the kit version (ENR-4)
- [ ] Every kit change starts from an inbox file; product text verbatim, Outcome appended (ENR-5)
- [ ] Topic home found in the routing table; existing rule amended before a new one is added (ENR-6)
- [ ] Rule generalized: no stack, vendor, domain or product names; illustrations name ≥ 2 stacks; profile-aware (ENR-7)
- [ ] One decision per lesson; conflicts resolved by conditions with both provenances (ENR-8)
- [ ] LL entry written and the scoreboard updated under the gate that should have caught it (ENR-9)
- [ ] Rule in kit format with checklist line; ids never reused or renumbered; retired by tombstone (ENR-10)
- [ ] Manuals, RULES.md, templates, tooling changed only where behaviour changes; manuals cite, never restate (ENR-11)
- [ ] CHANGELOG cites LL ids and every proposal with its outcome; VERSION bumped by the semver table (ENR-12)
- [ ] Manifest regenerated; kit_lint and tooling tests green (ENR-13)
- [ ] MINOR or MAJOR: kit acceptance run on a fixture product per profile, results in the CHANGELOG (ENR-14)
- [ ] Provenance pseudonymous; no client data in kit text (ENR-15)
- [ ] Products update proposal outcomes from the CHANGELOG in Mode U (ENR-16)

## Rules

### Product side

**ENR-1** — Harvest every lesson at every archive (Mode H), at project end and after every upgrade: each finding class
(AR, TF, DQ, F), escaped defect (ESC-9), exploratory finding, halt, TC-CONFLICT, gate round beyond the first, resume,
user correction and practice that worked becomes a row in `absd-project/lessons.md`, classified **project** (true only
for this product's stack, domain or people → `context.md` §14 Conventions or `TESTING.md` §4) or **universal** (another
product with another stack and domain could repeat it → an enrichment proposal with provenance). Every
`ESCAPED-DEFECTS.md` row is closed there with a proposed playbook change or "rule existed, not followed → enforcement
change", and the Tester's Log step writes the row's lesson id into its Lesson cell (ESC-9).
- *Why:* the source project's testing system and its lessons were built outside the kit and never flowed back (LL-27);
  its kit adaptations lived only as prose in the product (LL-28).
- *Check:* archive is refused while a finding, escape or halt of the cycle has no `lessons.md` row or a log row reads
  `pending H`; every universal row reaches `proposed` or later by the next Harvest.
- *Applies when:* always.
- *Provenance:* LL-27, LL-28 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**ENR-2** — Keep `lessons.md` as a ledger: ids `<slug>-L<n>` never reused; per row cycle, lesson (what happened → what
we learned), evidence ids, class, target (`ABSD:CODE-n` to amend, or a new rule in a named file) and status `local`,
`proposed`, `sent`, `accepted → LL-n` or `rejected: <reason>`. Rows are never deleted; a lesson already sent is never
re-sent — a new observation amends it by reference.
- *Why:* a per-cycle lessons file archived inside the product is never read again; duplicates waste the maintainer's
  triage.
- *Check:* the template header is unchanged; every status is one of the five; no id repeats.
- *Applies when:* always.
- *Provenance:* industry baseline

**ENR-3** — Cut proposals at Harvest: when it archives the cycle, the Manager writes one file,
`proposal-<slug>-YYYY-MM-DD.md`, into the cycle's archive folder, in the format below, covering every `proposed` row;
strips client names, secrets, personal data and stack-only detail; asks the user to deliver it verbatim as
`absd/lessons/inbox/<slug>-YYYY-MM-DD.md` in the ABSD repository; then marks the rows `sent` and adds a "Proposals
sent" row.
- *Why:* with no format, path or sender, lessons stayed in product archives (LL-28).
- *Check:* every `sent` row names a proposal file present in an archive folder; the inbox holds the same file.
- *Applies when:* every Harvest with a `proposed` row.
- *Provenance:* LL-28 (KatenatsioTipster, 2026-10)

**ENR-4** — Never keep a local edit to a kit file (`absd/`, `.claude/agents/`, `.github/agents/`; the ownership hook
refuses agent writes there): a need found while working, a difference `absd_sync.py check` reports, or a row of
`absd-project/upgrade-local-edits.md` becomes a universal lesson (ENR-1), and the file returns to the kit's version;
product-specific adaptations go to `context.md`.
- *Why:* the source project adapted the kit by moving artifacts and writing exceptions into its own guide, so every
  later kit change collided with it (LL-28).
- *Check:* `absd_sync.py check` is green at every cycle start; each local-edit row maps to a `lessons.md` row.
- *Applies when:* product repositories.
- *Provenance:* LL-28 (KatenatsioTipster, 2026-10)

### ABSD side

**ENR-5** — Start every kit change from an inbox file, the maintainer's own ideas and review findings included:
`absd/lessons/inbox/<slug>-YYYY-MM-DD.md`, product proposals verbatim. The maintainer appends an "Outcome" section and
never edits the text above it.
- *Why:* ad hoc edits in a session that took the pipeline rules as its own duplicate or renumber rules and leave no
  record of why the kit changed.
- *Check:* every CHANGELOG entry names the inbox files it answers; no playbook change lands without one.
- *Applies when:* the ABSD repository.
- *Provenance:* industry baseline

**ENR-6** — Dedupe before writing: find the topic's single home in the routing table of `absd/playbook/README.md`,
read that code's rules and the LEDGER entries citing them, and amend an existing rule (a condition, a check, a
provenance) before adding one; a topic never gets a second home — other files link to it.
- *Why:* one lesson fits several topics; filed twice, the copies drift apart.
- *Check:* the Outcome names "amended CODE-n" or "new CODE-n — no existing home" per lesson; each topic appears once in
  the routing table.
- *Applies when:* every accepted lesson.
- *Provenance:* industry baseline

**ENR-7** — Generalize: state the failure class, not the incident; strip stack, vendor, domain, company and product
names (specifics reach the kit only through LL ids); write one imperative, checkable sentence; illustrations name at least
two stacks; key *Applies when* to interface profiles and conditions, and keep the rule true for every profile it names.
- *Why:* rules shaped by one product's stack fail silently for a CLI, a library or a pipeline.
- *Check:* kit_lint's stack-word check; the Outcome records a replay of the lesson against one other profile.
- *Applies when:* every new or amended rule.
- *Provenance:* industry baseline

**ENR-8** — Decide each lesson: new, amend, reject (duplicate, project-specific, unverifiable, unsafe — with the reason)
or conflict. Resolve a conflict by adding a condition ("when X …; otherwise …") under which each lesson holds, both
provenances kept on the rule; never let a newer lesson silently override an older one. A conflict no condition
reconciles goes to the kit owner, and the LL entry records the decision and why.
- *Why:* contradicting lessons from two products are both evidence; overriding one reintroduces its failure.
- *Check:* the Outcome holds one decision per lesson; a conflict-resolved rule cites both LL ids.
- *Applies when:* every proposal.
- *Provenance:* industry baseline

**ENR-9** — Give every accepted lesson an entry in `absd/lessons/LEDGER.md`: next LL = highest + 1, never renumbered;
date, project slug, type (escape, finding, process, practice), what happened, why it slipped, lesson → rule ids. Count
each escape and finding on the scoreboard row for (project, ABSD version) under the gate that should have caught it;
add a column when a gate is added.
- *Why:* the scoreboard measures whether each project shows fewer escapes; a rule without an entry has no provenance.
- *Check:* kit_lint resolves every LL cited by rules and CHANGELOG; scoreboard totals equal the project's entries.
- *Applies when:* every accepted lesson.
- *Provenance:* industry baseline

**ENR-10** — Write the rule in its home file in the kit format (`absd/playbook/README.md` "Rule format") and add or amend
its checklist line. Number it next within its code, unpadded; never reuse or renumber an id; a moved rule keeps its id;
a pinned id (cited by `absd/RULES.md`) keeps its meaning. Retire by tombstone, never delete: the rule line becomes
"Retired in x.y.z: superseded by CODE-m" (or "no successor — reason"), its four bullets stay with *Applies when:*
"never — retired", and its checklist line goes.
- *Why:* archived artifacts and products cite rule ids; a renumbered or reused id silently changes what they mean.
- *Check:* kit_lint: unique, contiguous ids; four bullets; provenance format; no citation of a retired id.
- *Applies when:* every rule change.
- *Provenance:* industry baseline

**ENR-11** — Change agent manuals, `absd/RULES.md`, templates or tooling only where the rule changes what an agent does
or a tool checks: manuals cite `ABSD:CODE-n` and never restate the rule; RULES.md changes only for routes, gates,
immutable rules and Q-laws with their pinned ids; a tooling change ships with its tests in the same commit.
- *Why:* rules copied into several files drift apart and blow the size budgets (`absd/RULES.md` §9).
- *Check:* kit_lint: every cited id and path exists, mirrors match manuals, budgets hold.
- *Applies when:* every accepted lesson.
- *Provenance:* industry baseline

**ENR-12** — Add a CHANGELOG entry, newest first: version, date, every LL added, every inbox file and lesson id with its
outcome (accepted → rule ids, amended, rejected: reason), and for MAJOR the migration notes products apply in Mode U.
Bump `absd/VERSION` by the table below; the highest matching row wins.
- *Why:* products learn outcomes only from the CHANGELOG (ENR-16); a bump without meaning lets an upgrade break a
  product mid-flight.
- *Check:* kit_lint resolves every id the CHANGELOG cites; the VERSION change matches the table.
- *Applies when:* every kit release.
- *Provenance:* industry baseline

| Bump | When | Products then |
|---|---|---|
| MAJOR | Artifact structure, id scheme, gate, route, mode or ownership changes; a pinned rule's meaning changes | apply the migration notes in Mode U |
| MINOR | A rule added, amended or retired; a checklist, template or tool gains a check | baseline against the changed rules in Mode U (gaps → DEBT) |
| PATCH | Wording, examples, typos — nothing anyone does or checks changes | nothing |

**ENR-13** — Before every kit commit, regenerate the manifest and run the kit checks below; all must pass, and the kit
CI (`.github/workflows/kit.yml`) runs the same on every push.
- *Why:* a kit enriched after every project slowly breaks its own cross-references: cited ids, paths, mirrors, hashes.
- *Check:* kit CI green at the release commit; `absd_sync.py check` reports no difference.
- *Applies when:* every kit commit.
- *Provenance:* industry baseline

```bash
python3 absd/tooling/absd_sync.py manifest --root .
python3 absd/tooling/kit_lint.py --root .
python3 -m unittest discover -s absd/tooling -p 'test_*.py'
```

**ENR-14** — Before tagging a MINOR or MAJOR version, run the kit acceptance procedure: install the kit into a tiny
fixture product per interface profile (e.g. a one-screen web app, a todo CLI, a small library, a two-endpoint HTTP API,
a one-stage batch pipeline, a one-screen native app), kept outside `absd/` and never in the MANIFEST; run Bootstrap and
one feature cycle on each. Pass: every Foundation negative control turns RED then GREEN, trace_check and ownership_check
pass at every gate, and no agent halted on a question the kit should have answered.
- *Why:* the golden standard needs a regression test of its own; a manual can contradict a rule with no lint noticing.
- *Check:* the CHANGELOG entry lists each fixture run with profile, commit and result.
- *Applies when:* every MINOR or MAJOR release.
- *Provenance:* industry baseline

**ENR-15** — Keep provenance pseudonymous: a product appears in the kit only as its slug (a pseudonym for client
products) in LEDGER entries and Provenance lines — `LL-n (<slug>, YYYY-MM)`, or `industry baseline` for practice adopted
before any project hit it; no client, person or domain names, secrets, personal data or internal addresses reach rule
text, LEDGER or CHANGELOG.
- *Why:* the kit is shared across products and clients; a lesson must travel without its owner's data.
- *Check:* kit_lint's provenance format; the maintainer redacts before writing the LL entry.
- *Applies when:* always.
- *Provenance:* industry baseline

**ENR-16** — Close the loop: in Mode U the Manager reads every CHANGELOG entry between the installed and the new version,
sets each answered `sent` row to `accepted → LL-n` or `rejected: <reason>` (a rejected lesson may stay as a project
convention), and the Tester baselines the product against the new and changed rules (DOD-9).
- *Why:* a product that never learns its proposal's fate re-sends it or keeps a local workaround.
- *Check:* after Mode U no `sent` row that the CHANGELOG answers is still `sent`.
- *Applies when:* every Mode U.
- *Provenance:* industry baseline

## Proposal file format

```markdown
# ABSD enrichment proposal — <slug> — YYYY-MM-DD

| Product slug | ABSD version | Interface profiles | Lessons |
|---|---|---|---|
| <slug (pseudonym for client products)> | x.y.z | web-ui, … | <slug>-L4, <slug>-L7 |

## <slug>-L4 — <one-line title>
- Type: escape | finding | process | practice
- What happened: <symptom and impact — no client names, secrets or personal data>
- Why it slipped: <the gate or rule that should have caught it, or "no rule">
- Evidence: <C###/F-n, DEF-n, ESCAPED-DEFECTS row, redacted excerpt>
- Proposed change: new rule in <file> | amend ABSD:CODE-n | taxonomy, checklist, template or tool item
- Proposed rule: <imperative sentence> · Why · Check · Applies when
- Conflicts with: <ABSD:CODE-n or "none found"> · reconciling condition: <when …>

## Outcome (ABSD maintainer only; the text above stays verbatim)
| Lesson | Decision | LL | Rules | Version | Reason |
|---|---|---|---|---|---|
```
