# Escaped defects — what slipped past the tests, and how the tests got better

> Living, owned by the Tester, NEVER archived. **The main rule (`ABSD:ESC-1`):** when something slips past the tests —
> found by a user, on the live system, in an exploratory session, by CI on another change, or by reasoning — the fix is
> not done until
> 1. **a test fails without the fix** (at the level that should have caught it; plus a UI/end-to-end regression test if
>    it reached a screen or a user-visible output);
> 2. we name **why the existing tests missed it** (taxonomy in `absd/playbook/testing/escaped-defects.md`) and fix
>    **that kind of test**, not only add a case;
> 3. we **look for the same weakness elsewhere** and cover it (the Auditor verifies the sweep);
> 4. the slip is **logged here**, with the ABSD gate or rule that should have caught it, and the Manager closes it in
>    `absd-project/lessons.md` (playbook change, or "rule existed, not followed → enforcement change").
>
> Over time the tests must catch what people used to find. Newest first.

| DEF | Date | What slipped | Found by | Why the tests missed it (taxonomy) | How the tests improved | Same weakness looked for elsewhere | ABSD gate/rule that should have caught it | Lesson / rule changed |
|---|---|---|---|---|---|---|---|---|
| <DEF-n> | <YYYY-MM-DD> | <symptom, impact> | <user / live / exploratory / CI / reasoning> | <e.g. assumption-fed fake; desktop-only; tiny data; test-only override; no test ran the unit; missing requirement; inherited behaviour unspecified; oracle from code; real-time race> | <tests and test kinds added/changed> | <where else, what was found> | <Gate T / ABSD:VAR-8 / …> | <slug-L n → LL-n or "enforcement"> |
