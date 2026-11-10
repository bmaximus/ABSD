# Procedure — repair a commit that touched another owner's path

Loaded on demand: the Manager opens this file when `ownership_check.py` reports a foreign-path or unattributed commit
on a cycle branch (GATE-18), not before. It defines steps, never rules. History is never rewritten (no amend, rebase,
reset of pushed or recorded commits, force push); the repair is a new commit.

| # | Step | Evidence | Rules |
|---|---|---|---|
| 1 | Stop the route at the current step; note the violating commit's sha, agent and the foreign paths from the ownership_check output | the output in `cycle.md` | GATE-14 |
| 2 | Tell the user what happened in product terms and ask for the decision: repair (default) or park the cycle | `D-n` in `cycle.md` with date | GATE-18, DOD-10 |
| 3 | Repair commit by the Manager: restore exactly the foreign paths of the violating commit to their state before it (e.g. `git restore --source=<sha>~1 -- <paths>`, removing paths it added); stage those paths by name; trailers `ABSD-Agent: manager`, `ABSD-Cycle: C###`, `ABSD-Repair: <violating sha> D-<n>` | the repair commit | GATE-18 |
| 4 | Run ownership_check over the cycle range: the violating commit's errors now read as notices naming the repair; any other error is a new finding | output | GATE-14 |
| 5 | If the owner wants the content, re-invoke the owner to commit it from its own role (its brief names the files); the Manager never re-commits it | the owner's commit | RULES §5 |
| 6 | Evidence taken at a product SHA the repair or re-commit moved is re-run (RULES §6); the Resume point and counters are unchanged | `cycle.md` | GATE-1 |
| 7 | Lessons row: the command that staged the files and why GATE-18's check did not stop it | `lessons.md` | ENR-1 |

A violation in a commit already merged to the default branch goes through Mode D, not this procedure.
