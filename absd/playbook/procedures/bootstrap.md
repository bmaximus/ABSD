# Procedure — Bootstrap and adoption (Mode B)

Loaded on demand: the Manager opens this file when it enters Mode B (the Foundation cycle, a brownfield adoption or a
v1 Foundation-delta; DOD-5), not before. It defines steps, never rules. The cycle's own steps are
`absd/templates/project/foundation-brief.md` steps 1–9; this file holds the Manager's part of them.

| # | Step | Evidence | Rules |
|---|---|---|---|
| 0 | Entry is the user's, before the Manager exists: `absd_sync.py install` from a kit checkout (a v1 project: `migrate-v1` first), each committed on the default branch with the trailer it prints. The Manager never runs them | the kit-sync commits | DOD-5 |
| 1 | Run the Foundation brief as the cycle (C001, or the next number); DoD is DOD-5 | `cycle.md` | DOD-5 |
| 2 | Brief step 1: `absd_sync.py check` green and the kit-sync commits on the default branch; open `cycle.md` and the branch; frame `context.md` §1, §5–§7 with the user as the brief lists (phone tests for web-ui and native-app on unless waived; a palette source if the user wants one, DSN-22) | check output, the frame commit | DOD-5 |
| 3 | After G2R: ADR-002's table verbatim into §3, ADR-001 into §2, the ADR-003 commands into §4 and the `.claude/settings.json` allow list, with the commands the manuals run (`git mv`, `git merge`, `git push`, `git worktree`, `python3 absd/tooling/…`); keep the ownership hook | the commit | DOD-5, GATE-14 |
| 4 | After GT (brief step 5): §4 and the allow list again from `TESTING.md` | the commit | DOD-5 |
| 5 | Brownfield: survey read-only and draft the frame for the user to confirm; the inherited behaviour inventory covers the WHOLE product; brief step 5 adds tester · Baseline | the inventory, the Baseline brief | DOD-6, STRAT-12 |
| 6 | v1 Foundation-delta: missing steps only, each gated; the archive keeps its numbers; the delta's number follows the highest v1 cycle, the parked one counted | `cycle.md` | DOD-5 |
| 7 | v1, in step 1 before any delegation or gate, your own commits: `context.md` restructured into the `absd/templates/project/context.md` sections (the hook and ownership_check read §3), ≤ 25 KB | the commit | DOD-5 |
| 8 | v1: `CLAUDE.md` keeps the product text; v1 rules replaced by the template imports (`@absd/RULES.md`, `@absd-project/context.md`); text conflicting with RULES (merge, branch, direct-fix authorizations) → §1 merge policy with the user's confirmation, or deleted | the commit | DOD-5 |
| 9 | v1: in-flight working files `migrate-v1` left are parked by `git mv` into `absd-project/archive/NNN_<date>_<slug>_parked/` — a delta step, not Mode P (no `cycle.md`; DOD-10 N/A); a §17 row; its intake is redone after the delta | the commit, §17 row | DOD-5 |
| 10 | v1, later: lasting v1 gate decisions become catalogue BRs through the Analyst (history stays in the archive) | catalogue entries | ELIC-20 |
