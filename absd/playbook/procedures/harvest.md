# Procedure — Harvest, then archive (Mode H)

Loaded on demand: the Manager opens this file at every archive, at project end and after Mode U (ENR-1), not before.
It defines steps, never rules.

| # | Step | Evidence | Rules |
|---|---|---|---|
| 1 | `metrics.py report` over `absd-project/metrics/*.json`; cite its numbers in the harvest | the report | PIPE-5 |
| 2 | A `lessons.md` row per finding class (AR, TF, DQ, F), escape, exploratory finding, halt, TC-CONFLICT, extra round, resume, user correction and good practice — project (→ `context.md` §14) or universal (→ proposal) | the rows | ENR-1 |
| 3 | Each new `ESCAPED-DEFECTS.md` row gets a lessons row closed with a proposed playbook change or "rule existed, not followed → enforcement change"; tester · Log then fills the Lesson cells from your brief (documentation only, no re-audit) | rows, the Log commit | ESC-9 |
| 4 | LL ids go only into `lessons.md` (`accepted → LL-n`). Proposals: `proposal-<slug>-YYYY-MM-DD.md` in the archive folder, without client names, secrets or personal data; the user delivers it verbatim to the kit's `absd/lessons/inbox/<slug>-YYYY-MM-DD.md`; mark rows `sent` | the proposal file | ENR-3 |
| 5 | Archive is refused while a finding, escape or halt lacks a lessons row, or a row of this cycle in `ESCAPED-DEFECTS.md` reads `pending H` | the check | ENR-1 |
| 6 | The rest of the `cycle.md` Close table ticked with evidence: DOD-2 row 11 (Harvest) and 14 (Log), DOD-4 rows 7–8; DOD-2 rows 9–10 follow step 7, row 13 step 9 | the ticked table | DOD-1 |
| 7 | `context.md` per the Manager's maintenance list: active cycle none; Risk register gets every unresolved assumption, open question, UNVERIFIED fact and environment limitation; DEBT; accepted findings with expiry; ADR index; interfaces, flags, external systems, volumes; §16 (taken rows closed); a §15 row; stale entries removed. Tick DOD-2 rows 9–10 | the diff | ELIC-19 |
| 8 | One commit `absd(C###): archive — manager`: `git mv absd-project/working/* absd-project/archive/NNN_YYYY-MM-DD_slug/` (NNN = cycle number, date = G3 date, evidence included); living documents and `metrics/` stay | the commit | DOD-1 |
| 9 | Merge per the `context.md` merge policy when CI is green at the G3 product SHA and `git diff --stat <G3 product SHA> HEAD -- . ':!absd-project'` shows only the Tester's Log commit (Lesson cells); plan gates then note "no active cycle". A merge commit, never squash or rebase. A release trigger in the change → Mode R before that action; a Mode D merge never waits for Mode R. DOD-2 row 13: the archive folder goes into the §15 row now, the merge commit in your next cycle's start commit | the merge commit | STRAT-7, GATE-14, DOD-7 |
