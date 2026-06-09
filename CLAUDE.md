# ABSD Pipeline — Claude Code Instructions

This directory contains the **Artifact-Based Software Development (ABSD)** pipeline for Claude Code.

## Sub-Agents

The pipeline is implemented as Claude Code sub-agents in `.claude/agents/`. Invoke the **Manager** agent to start a new development cycle. The Manager orchestrates the full pipeline.

```
Manager → Analyst → Manager (Gate 1) → Designer → Manager (Gate UX) → Architect → Manager (Gate 2) → Builder → Auditor → Manager (Gate 3)
```

## How to Start

Tell the Manager what you want to build. The Manager will gather requirements, challenge assumptions, and coordinate all downstream agents.

---

## Pipeline Rules (All Agents Must Follow)

### Artifact Routing Table

| Artifact | Owner | Path |
|----------|-------|------|
| `brd.md` | Manager | `working/brd.md` |
| `analysis.md` | Analyst | `working/analysis.md` |
| `design.md` | Designer | `working/design.md` |
| `architecture.md` | Architect | `working/architecture.md` |
| `build_log.md` | Builder | `working/build_log.md` |
| `clarification_needed.md` | Builder | `working/clarification_needed.md` |
| `audit.md` | Auditor | `working/audit.md` |
| `context.md` | Manager | `working/context.md` |

**No agent writes to another agent's artifact.**

### Immutable Rules

1. **Only the Manager speaks to the user.**
2. **No agent writes code before `architecture.md` is approved at Gate 2.**
3. **No agent writes `architecture.md` before `analysis.md` is approved at Gate 1.**
4. **Builder halts are atomic.** No partial code — ever.
5. **Every artifact is Markdown.**
6. **`context.md` is never archived.** It is the living project memory.
7. **3-iteration maximum.** After 3 failed build-audit cycles, escalate to user.
8. **YAGNI is enforced.** No agent adds features beyond what `analysis.md` requires.
9. **Agents do not modify artifacts they do not own.**
10. **Gate 2 is a coverage check only.** The Manager approves architecture for completeness, not quality.

### Directory Conventions

- `working/` — active cycle artifacts (ephemeral; cleared after archiving)
- `working/src/` — generated source code (kept across cycles)
- `archive/NNN_YYYY-MM-DD_description/` — archived cycle artifacts

### Technology Stack

Defined per project in `working/context.md`. The Manager writes this at cycle start. All agents read it.
