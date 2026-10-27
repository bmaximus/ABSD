# Escaped defects — what slipped past the tests, and how the tests got better

> Living, owned by the Tester, NEVER archived. **The main rule (`ABSD:ESC-1`):** when something slips past the tests —
> found by a user, on the live system, in an exploratory session, by CI on another change, or by reasoning — the fix is
> not done until
> 1. **a test fails without the fix** (at the level that should have caught it; plus a UI/end-to-end regression test if
>    it reached a screen or a user-visible output);
> 2. we name **why the existing tests missed it** (taxonomy in `absd/playbook/testing/escaped-defects.md`) and fix
>    **that kind of test**, not only add a case;
> 3. we **look for the same weakness elsewhere** and cover it (the Auditor verifies the sweep; hits outside the cycle
>    become DEF rows in the `absd-project/context.md` defect backlog);
> 4. the slip is **logged here**, with the ABSD gate or rule that should have caught it, and the Manager closes it in
>    `absd-project/lessons.md` (playbook change, or "rule existed, not followed → enforcement change").
>
> **When rows are written (`ABSD:ESC-8`, `ABSD:ESC-9`):** the Tester writes the whole row at Verify of the Mode D cycle,
> every cell filled (an empty sweep says what was searched: "none found: …"), with Lesson = `pending H`. After Harvest
> the Tester's **Log** step fills each Lesson cell with the `<slug>-L<n>` id the Manager's brief passes — one commit
> changing only Lesson cells; the archive is refused while a row of the cycle reads `pending H`. LL ids, once the kit
> accepts a proposal, are recorded in `absd-project/lessons.md`, never here. Over time the tests must catch what people
> used to find. Newest first.
>
> **Columns:** Found by = user / live / exploratory / audit of a later cycle / nightly / CI on another change /
> reasoning · Same weakness = the searches run and what they found ("none found: <patterns, scope>"), with the DEF ids
> raised · Gate/rule = the gate or lane that should have caught it plus `ABSD:CODE-n` ("none — gap" opens a
> proposal) · Lesson = `pending H`, then the `<slug>-L<n>` id of its `lessons.md` row (that row says whether the rule
> changes or, when it existed, which enforcement change closes it).

| DEF | Date | What slipped | Found by | Why the tests missed it (taxonomy #: primary; secondary) | Root-cause class | How the tests improved (TC ids) | Same weakness looked for elsewhere | ABSD gate/rule that should have caught it | Lesson |
|---|---|---|---|---|---|---|---|---|---|
| <DEF-n> | <YYYY-MM-DD> | <symptom, impact> | <user / live / exploratory / CI / reasoning> | <e.g. #1 assumption-fed fake; #3 single device class> | <implementation / architecture / external-fact / UX / requirements / test-only gap> | <tests and test kinds added or changed, TC-nnnn> | <where else, what was found, DEF ids raised> | <Gate T / ABSD:VAR-8 / …> | <pending H → slug-Ln> |
