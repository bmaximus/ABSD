# Procedure — park or abandon a cycle (Mode P)

Loaded on demand: the Manager opens this file when the user decides to park or abandon a cycle (DOD-10), not before.
It defines steps, never rules. The cycle branch is kept and never merged; nothing of it reaches the default branch
except the archive folder and the Manager's living-document updates.

| # | Step | Evidence | Rules |
|---|---|---|---|
| 1 | On the cycle branch: record in `cycle.md` the user's decision (D-n, date), the last gate passed, the resume point and the branch; commit | the commit | DOD-10 |
| 2 | On the cycle branch: `git mv absd-project/working/* absd-project/archive/NNN_YYYY-MM-DD_slug_abandoned/` in one Manager commit | the commit | DOD-10 |
| 3 | Switch to the default branch with a clean tree (`git status --porcelain` empty) | output | GATE-18 |
| 4 | Bring only the archive folder: `git restore --source=<cycle branch> -- absd-project/archive/NNN_…_abandoned/` | the restored folder | DOD-10 |
| 5 | Update the living docs on the default branch: `context.md` (active cycle none; RISK and DEBT rows for unresolved questions, UNVERIFIED facts and partial work), `lessons.md` (why it stopped) | the diffs | DOD-10, ENR-1 |
| 6 | Before committing: `git status --porcelain` lists only `absd-project/` paths; any build output, dependency folder or test report means the ignore rules exist only on the cycle branch — leave those files unstaged and record the missing ignore lines as a lesson for their owner | output | GATE-18 |
| 7 | Stage `absd-project/` by name; one Manager commit with `ABSD-Agent: manager` and `ABSD-Cycle: C###`; run ownership_check on it | the commit, output | GATE-14 |
| 8 | Ids: everything the cycle used stays consumed, except the `QC-n` and ADR numbers a Foundation brief fixes, which a restarted Foundation reuses; the next cycle number follows the parked one | `cycle.md` of the next cycle | DOD-10 |

Resume later: open the kept branch, move the archive folder back to `working/` in a Manager commit, and continue from
the recorded resume point with the counters as recorded.
