# Invocation brief — the only way the Manager delegates

Workers see none of the Manager's conversation. Every delegation passes this brief, filled in completely, as the
whole prompt. A worker that receives a request without a brief refuses and answers "ABSD brief missing".

```markdown
# ABSD brief — <agent> · <mode>

| Field | Value |
|---|---|
| Cycle | C### — <slug> (branch `absd/C###-<slug>`) |
| Route | Mode F / S / D / B / C / X / R / U — step <n> of `absd-project/working/cycle.md` |
| Agent mode | e.g. Analyze · Design · Design QA · Architect · Architecture Review · Plan & Bind · Reproduce · Verify · Build · Fix · Audit · Baseline |
| Iteration | Builder pass <n>/3 · gate round <n>/3 · halts <n>/3 |
| Revision | HEAD <sha> · T-SHA <sha or "not yet"> |
| Resume | "fresh start" or "resume from <artifact section / WP-n>; artifact status IN-PROGRESS" |

## Read first
- `absd/RULES.md` (always) and your manual's playbook list
- `absd-project/context.md`
- <input artifacts, each with its path>

## Produce
- <artifact path(s)> — full / delta (unchanged sections: "Unchanged — <reason>")
- Commit with trailers `ABSD-Agent: <agent>` and `ABSD-Cycle: C###`; leave the working tree clean

## Address (only when routed back)
| Finding | Severity | Source | What is expected |
|---|---|---|---|
| C###/F-n | Major | audit.md | <one line> |

## Constraints for this run
- <scope limits: Mode S delta, defect ids, profiles in scope, sections to leave untouched>

## Reply format (≤ 15 lines, never artifact contents)
Status: COMPLETE | COMPLETE-WITH-CONFLICTS | HALTED | BLOCKED | IN-PROGRESS (interrupted)
Artifacts: <paths> · Commit: <sha>
Findings: Critical <n> · Major <n> · Minor <n>
Blockers / questions for the Manager: <list or "none">
```

## Manager checklist before sending

- [ ] `cycle.md` updated: invocation logged (agent, mode, brief summary, time).
- [ ] Working tree clean (`git status --porcelain` empty) and on the cycle branch.
- [ ] Every input artifact the worker needs has passed its gate (or the brief says it is a draft input).
- [ ] Findings to address are copied with their ids — never paraphrased into new requirements.
- [ ] No technical decision is made in the brief; questions go to the owner agent, business questions to the user.
