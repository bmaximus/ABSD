# ABSD Pipeline — Workflow Rules

These rules govern how all agents behave within the Artifact-Based Software Development pipeline. Every agent must follow these rules without exception.

---

## Pipeline Sequence

```
Manager → Analyst → Manager (Gate 1) → Designer → Manager (Gate UX) → Architect → Manager (Gate 2) → Builder → Auditor → Manager (Gate 3)
```

No step may be skipped. No agent may begin work before the prior agent's artifact is approved and handed off.

---

## Artifact Routing Table

| Artifact | Produced By | Reviewed By | Consumed By | Location |
|----------|-------------|-------------|-------------|----------|
| `brd.md` | Manager | (Manager is author) | Analyst | `working/brd.md` |
| `analysis.md` | Analyst | Manager (Gate 1) | Designer, Architect | `working/analysis.md` |
| `design.md` | Designer | Manager (Gate UX) | Architect, Builder | `working/design.md` |
| `architecture.md` | Architect | Manager (Gate 2) | Builder | `working/architecture.md` |
| `build_log.md` | Builder | Auditor | Manager | `working/build_log.md` |
| `clarification_needed.md` | Builder | Manager | Architect | `working/clarification_needed.md` |
| `audit.md` | Auditor | Manager (Gate 3) | Manager | `working/audit.md` |
| `context.md` | Manager | (Manager is author) | All agents | `working/context.md` |

**No agent writes to another agent's artifact.** Agents read artifacts not owned by them but never modify them.

---

## Operating Modes

### Mode 1 — Requirement Elicitation (Manager)

1. Read `working/context.md` to understand existing project state.
2. Engage the user in active dialogue — challenge vague requirements, expose gaps, confirm edge cases.
3. Work through the completeness framework: actors, capabilities, constraints, out of scope.
4. Write `working/brd.md` when requirements are complete and unambiguous.
5. Hand `brd.md` to the Analyst.

---

### Mode 1A — Requirements Analysis (Analyst)

1. Read `working/brd.md` completely.
2. Decompose every business statement into structured, numbered, traceable requirements.
3. Write `working/analysis.md` following the mandatory structure exactly.
4. Return `analysis.md` to the Manager for Gate 1 review.

---

### Mode 2 — Review Gate 1 (Manager)

1. Read both `brd.md` and `analysis.md`.
2. Apply the Gate 1 verification checklist.
3. **If approved:** Pass `analysis.md` to the Designer.
4. **If rejected:** Provide specific, itemized feedback. Route back to Analyst.

#### Gate 1 Checklist
- [ ] Every BRD section has corresponding requirements in `analysis.md`
- [ ] No requirements in `analysis.md` contradict `brd.md`
- [ ] No requirements were fabricated
- [ ] All REQ-F and REQ-NF IDs are unique and sequential
- [ ] Every functional requirement has at least one GIVEN/WHEN/THEN acceptance criterion
- [ ] Analyst's assumptions are reasonable
- [ ] Open questions are valid concerns
- [ ] Business rules (BR-###) are correctly extracted

---

### Mode 2A — UX Design (Designer)

1. Read `working/context.md` and `working/analysis.md`.
2. Produce `working/design.md` with minimalist user flows, states, responsiveness, and accessibility guidance.
3. Return `design.md` to the Manager for Gate UX review.

---

### Mode 2B — Review Gate UX (Manager)

1. Read `working/analysis.md` and `working/design.md`.
2. Verify every UI-affecting requirement is covered, states are complete, responsive/accessibility expectations are defined, and no features were invented.
3. **If approved:** Pass `analysis.md` + `design.md` to the Architect.
4. **If rejected:** Provide specific, itemized feedback. Route back to Designer.

---

### Mode 3 — Technical Architecture (Architect)

1. Read `working/context.md`, `working/analysis.md`, and `working/design.md`.
2. Design the exhaustive technical blueprint.
3. Write `working/architecture.md` with blueprint-level detail — every class, method, endpoint, schema, DI registration, and config value.
4. Self-verify: every REQ ID must appear in the traceability matrix.

---

### Mode 4 — Review Gate 2 (Manager)

1. Read `analysis.md`, `design.md`, and `architecture.md`.
2. Apply the Gate 2 checklist (coverage check only — not quality).
3. **If approved:** Pass `architecture.md` to the Builder.
4. **If gaps found:** Itemize exactly which REQ IDs are unaddressed. Route back to Architect.

#### Gate 2 Checklist
- [ ] Every REQ-F appears in the traceability matrix with a section reference
- [ ] Every REQ-NF is addressed
- [ ] Every BR is enforced in the design
- [ ] Approved `design.md` behavior is reflected for user-facing flows
- [ ] Architecture does not introduce features absent from `analysis.md` (YAGNI)

**This is a COVERAGE check, not a quality review.**

---

### Mode 5 — Code Implementation (Builder)

1. Read `working/context.md`, `working/design.md`, and `working/architecture.md`.
2. Perform the full pre-generation scan (cross-reference Sections 2 vs 3–10).
3. **If ANY ambiguity:** HALT. Atomic discard. Produce `working/clarification_needed.md` only.
4. **If no ambiguity:** Generate all source code exactly as specified. Produce `working/build_log.md`.

#### Atomic Discard Rule
When the Builder halts, no source files are produced. Not partial, not placeholder — nothing.

---

### Mode 5A — Builder Halt Handling (Manager)

1. Read every CLR item and classify: business question → user, UX gap → Designer, technical gap → Architect.
2. Resolve appropriately and pass corrected artifacts to Builder for full restart.
3. **Builder halts do NOT count toward the 3-iteration limit.**

---

### Mode 6 — Audit Verification (Auditor)

1. Read ALL artifacts: `brd.md`, `analysis.md`, `design.md`, `architecture.md`, `build_log.md`.
2. Read ALL source code produced by the Builder.
3. Perform all five verification levels.
4. Produce `working/audit.md`. Always produce it — even on a clean pass.

---

### Mode 7 — Review Gate 3 (Manager)

Read `audit.md` and route per finding type:

| Finding Type | Route To |
|-------------|----------|
| Implementation Drift | Architect (clarify) → Builder (restart) |
| UX Drift | Designer → Architect → Builder (restart) |
| Design Gap | Designer → Architect → Builder (restart) |
| Requirements Gap | Analyst → Gate 1 → Designer → Gate UX → Architect → Builder |
| Code Quality Critical/Major | Architect or Builder (by root cause) |
| Code Quality Minor | Defer at Manager's discretion; log in `context.md` |

**3-iteration maximum.** Escalate to user after 3 failed build-audit cycles.

---

### Mode 8 — Cycle Archiving (Manager)

1. Update `working/context.md`: add cycle row, new endpoints, tables, decisions, debt.
2. Create `archive/NNN_YYYY-MM-DD_short-description/`.
3. Copy all per-cycle artifacts to archive folder.
4. Delete per-cycle artifacts from `working/` — **keep `context.md` and `src/`.**
5. Confirm archival to user.

---

## Immutable Rules

1. **Only the Manager speaks to the user.**
2. **No agent writes code before `architecture.md` is approved at Gate 2.**
3. **No agent writes `architecture.md` before `analysis.md` is approved at Gate 1.**
4. **Builder halts are atomic.** No partial code is ever produced.
5. **Every artifact is Markdown.**
6. **`context.md` is never archived.**
7. **3-iteration maximum.** Escalate after 3 failed build-audit cycles.
8. **YAGNI is enforced.**
9. **Agents do not modify artifacts they do not own.**
10. **Gate 2 is a coverage check, not a quality review.**
