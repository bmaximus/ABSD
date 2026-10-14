# Exploratory testing — agent and human sessions

Code **EXPL**. Finding what no test thought of: charters, the session protocol, the Tester's agent pass at Verify on
every device class, human sessions and the manual acceptance checklist before a release, real devices, severity, and
how each finding becomes a fix, a defect, a product decision or a "by design" note. Applicability
(`absd/playbook/testing/strategy.md`): **M** web-ui, native-app, cli, data-pipeline (output vs source of truth) ·
**R** http-api, library (API usability). Living record: the Tester's `EXPLORATORY.md` (template in
`absd/templates/project/`); release use: Mode R.

## Checklist

- [ ] Charters for every principal × device class × journey the cycle touches; the standing set kept (EXPL-1)
- [ ] Each charter names its mission, where to wander, its oracles and the ids of the risks it targets (EXPL-1)
- [ ] Sessions: 60–90 min, one charter, one principal, one device class; start state recorded (EXPL-2)
- [ ] Findings noted as they happen: did → happened → expected, with evidence; a debrief closes it (EXPL-2)
- [ ] Verify: the Tester's agent pass drives the built product per charter on every device class (EXPL-3)
- [ ] Human sessions per affected principal before users get a build; offered after visible cycles (EXPL-4)
- [ ] Severity from the unified scale, set by the finder, never downgraded by the Manager (EXPL-5)
- [ ] Every finding → TF, DEF (Mode D), product decision or by-design entry; fixed ones get tests (EXPL-6)
- [ ] "By design" entries cite the requirement or decision behind them; reviewed at Mode R (EXPL-7)
- [ ] Manual acceptance checklist run by a person at Mode R; each item dated, with device and person (EXPL-8)
- [ ] Real devices before release: gestures, on-screen keyboard, safe areas, every E2E-6 item (EXPL-9)
- [ ] cli, http-api, library and data-pipeline get charters of their own kind (EXPL-10)
- [ ] Session log newest first, never archived; agent sessions marked as such (EXPL-11)

## Rules

**EXPL-1** — Write charters at Plan & Bind for every journey, screen, command or flow the cycle touches — one per
principal × device class × goal — and keep the product's standing set in `EXPLORATORY.md`. A charter states its
mission ("explore <target> as <principal> on <device class> with <data> to discover <risk>"), where to wander (tours
below), the oracles to check against (an independent calculation, an official source, `design.md` copy and states,
the data contract) and the ids it targets (requirement, BR, EXT, RISK). The standing set always includes: the
least-privileged principal hunting for leaks and paywall gaps; the admin through every lifecycle; a phone-only sweep of
every screen and form; midnight and month or season start in the display zone; user-visible external facts against the
real world.
- *Why:* one first session found ten issues, four Major, that no test had looked for — wrong prize order after a
  removal, paid content in a free account's response, a dialog wiped every second, a role lacking its core value
  (LL-9, LL-10, LL-12, LL-18).
- *Check:* `test_plan.md` lists the cycle's charters with the ids they target; the standing set is in `EXPLORATORY.md`.
- *Applies when:* the exploratory row is M or triggered R.
- *Provenance:* LL-9, LL-10, LL-12, LL-18 (KatenatsioTipster, 2026-10)

**EXPL-2** — Time-box each session to 60–90 minutes with one charter, one principal and one device class (changing
any of them starts a new session). Record the start state: build SHA, data set, account, device and runtime, zone and
locale. Follow the charter, then wander. Write each finding as it happens: did → happened → expected, with evidence
(screenshot, recording, output, time, account, device). Close with a debrief: what was covered and not, findings,
questions, new charters and test ideas.
- *Why:* unstructured clicking repeats the happy path, and findings written up later lose the steps that reproduce them.
- *Check:* each session entry has start state, duration, findings table and debrief; a finding without steps or
  evidence goes back to its author.
- *Applies when:* every session, agent or human.
- *Provenance:* industry baseline

**EXPL-3** — At Verify, run the agent pass: the Tester drives the built product on the real stack (E2E-3) per cycle
charter on every declared device class — desktop and phone projects through the browser harness, native emulators, a
terminal with TTY and pipe, an HTTP client as a consumer, the pipeline on recorded input — with the error harness on
(E2E-1), and probes in every session: a screen left idle past its longest timer with a dialog open, lists at volume
max, a foreign zone and locale, keyboard only, slow and failing network, back, refresh, a second tab. In-scope
findings become TF-n in `test_report.md`; the session goes to `EXPLORATORY.md` marked "tester agent". The agent pass
never replaces human sessions.
- *Why:* nobody looked at the rendered product before users did, so raw enums, mixed formats and a screen that did not
  advance reached them (LL-19); a dialog wiped every second shows only to someone who stays on the screen (LL-12).
- *Check:* `test_report.md` exploratory notes: a session per charter × device class with evidence paths; Gate 3
  routes the TFs.
- *Applies when:* the exploratory row applies and the cycle changes something users or consumers see.
- *Provenance:* LL-12, LL-19 (KatenatsioTipster, 2026-10)

**EXPL-4** — Have people explore too: before users get a build (Mode R), at least one human session per affected
principal on each device class its users use, by the user or someone they name; after a cycle with a visible change
the Manager offers the user a short session on the increment. The Manager arranges it (only it speaks to the user);
the Tester supplies charters and the checklist and logs results from the person's notes and recordings.
- *Why:* the blocking feed facts and the phone defects were found by the owner on the live site and in a screen
  recording, not by any test (LL-1, LL-3, LL-4).
- *Check:* the Mode R record lists sessions per principal × device class with date and person; a missing one blocks
  the release (DOD release checklist, `absd/playbook/process/definition-of-done.md`).
- *Applies when:* Mode R always; after visible cycles on the user's acceptance.
- *Provenance:* LL-1, LL-3, LL-4 (KatenatsioTipster, 2026-10)

**EXPL-5** — Rate every finding on the unified scale (`absd/RULES.md` §6) as its finder; the Manager never downgrades
it. **Critical** — cannot continue; wrong money, results, deadlines or stored data; data loss; another principal's data
shown; security. **Major** — works wrongly; a principal cannot get its core value; a failure shown as a generic error;
input lost to a refresh or gesture. **Minor** — cosmetic, wording, small annoyance, no wrong information. "Blocker" in
a person's notes means Critical.
- *Why:* the same defect class was graded Major in one cycle and Minor in another (LL-47).
- *Check:* each finding row carries a severity consistent with these examples; the Auditor samples them against the
  severity calibration (XCA, `absd/playbook/process/audits.md`).
- *Applies when:* always.
- *Provenance:* LL-47 (KatenatsioTipster, 2026-10)

**EXPL-6** — Route every finding to exactly one place: in the cycle's scope at Verify → TF-n in `test_report.md` (routed
at Gate 3); outside the scope, or on a merged or released build → a DEF the Manager opens in `defect.md` (Mode D:
failing test first; logged per ESC-1 when it escaped a gate); wrong only if the product wants otherwise → "Open — needs
a product decision", taken to the user by the Manager and recorded as a brd Decision (Manager) or, through a cycle, a
catalogue change (Analyst); specified → "by design" (EXPL-7). Nothing is fixed outside a mode; every fixed finding gets
a test at the level that should have caught it and, if it reached a surface, an e2e regression test (E2E-17).
- *Why:* a dozen exploratory fixes were made outside the pipeline, with no route, audit or recorded decision (LL-27).
- *Check:* each finding row ends in a TF, DEF or decision id, or a by-design entry; the Auditor checks each fixed one
  has its tests.
- *Applies when:* always.
- *Provenance:* LL-27 (KatenatsioTipster, 2026-10)

**EXPL-7** — Keep a "by design" list in `EXPLORATORY.md`: behaviour that looks wrong but is specified, each entry citing
the requirement, BR or brd Decision behind it, so testers stop re-reporting it; review it at every Mode R (still
specified? still wanted?). An entry without an existing source id is a finding.
- *Why:* behaviour that only looks wrong (a stake counted as a loss until settled, by the user's chosen bookkeeping) is
  re-reported every session — or hides a real defect behind "known".
- *Check:* every entry's id resolves in the catalogue or the brd Decisions.
- *Applies when:* always.
- *Provenance:* industry baseline

**EXPL-8** — Keep a manual acceptance checklist in `EXPLORATORY.md`, derived from the catalogue and UJs: each
principal's core journeys; sign-in variants, on a phone too; each principal reaching exactly its own screens; each
user-visible external fact against the real world (e.g. three times against an official source). A person runs it at
Mode R on real devices and ticks each item with date, device and name; a failed item is a DEF. It confirms the feel of
what automated journeys already prove; it never replaces a test.
- *Why:* feed times were 8 h off until a person compared them with the official times (LL-1); the phone defects
  surfaced only when the owner used a phone (LL-4).
- *Check:* the Mode R record holds the ticked checklist; each item maps to a catalogue or UJ id.
- *Applies when:* Mode R; every profile with a human-facing surface.
- *Provenance:* LL-1, LL-4 (KatenatsioTipster, 2026-10)

**EXPL-9** — Before a release, check on real devices — at least one real phone per mobile engine and OS the audience
uses (e.g. Safari on iOS, Chrome on Android) and each declared tablet — what emulation cannot: pull-to-refresh, edge and
back swipes, overscroll in every scroll container and dialog; the on-screen keyboard (focused field and primary action
stay visible, right keyboard type, no layout jump); safe areas (notch, home indicator, rounded corners); orientation,
system text size and zoom; a slow real network; and every trigger E2E-6 listed as beyond automation.
- *Why:* a swipe in a picker reloaded the app and lost input on a real phone while desktop runs passed (LL-4); a
  hover-only control was unreachable on touch screens (LL-16).
- *Check:* the Mode R record lists devices, OS and browser versions and each item's result; no E2E-6 item open.
- *Applies when:* web-ui, native-app with touch users.
- *Provenance:* LL-4, LL-16 (KatenatsioTipster, 2026-10)

**EXPL-10** — Give the other profiles charters of their own kind: cli — real terminals and shells, piping into other
tools, interrupts and broken pipes, help discoverability, error text that says what to do; http-api (when triggered)
— a consumer builds a client from the docs alone; library (API usability) — a developer completes the README's task
from the docs, every friction a finding; data-pipeline — output compared with the source of truth for a sample
spanning boundary dates and zones, and an operator following the runbook through a rerun and an alert.
- *Why:* a field's meaning taken from a description stayed wrong until someone compared output with the real world
  (LL-2); consumers' confusion is encoded in no assertion.
- *Check:* `TESTING.md`'s exploratory row names the charter kinds per profile; sessions exist for each.
- *Applies when:* cli, data-pipeline (M); http-api, library (R).
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**EXPL-11** — Keep the session log in `EXPLORATORY.md`, newest first, never archived: per session a header (date,
charter, principal, device and runtime, build SHA, by person or "tester agent", duration), the findings table, the
debrief; then the "Open — needs a product decision" and "By design" lists.
- *Why:* findings, decisions and the tests they triggered are lost when a session's record lives only in chat or in an
  archived cycle.
- *Check:* the file's history shows a session per Verify of a visible cycle and per Mode R; every finding id resolves.
- *Applies when:* always.
- *Provenance:* industry baseline

## Tours (where to wander)

| Tour | Do |
|---|---|
| Interruption | back, forward, refresh mid-flow; a second tab or terminal; sign out in one of them |
| Network | slow, offline, a failing dependency; retry after recovery |
| Time | midnight and month or season start in the display zone; a deadline ± 1 min; a foreign zone and locale |
| Volume | the longest lists, max entries, long names, every empty state |
| Inputs | empty, max length + 1, Unicode and diacritics, pasted text, leading spaces, emoji |
| Principals | the least-privileged; switch principal; impersonate and return; an expired entitlement |
| Idle | a screen with an open dialog left longer than its longest timer |
| Access | keyboard only, 200 % zoom, screen-reader names, both themes |
| World | three user-visible values against an official source |

## Charter row (in `EXPLORATORY.md` and `test_plan.md`)

```markdown
| # | Principal | Device class | Mission: explore <target> with <data> to discover <risk> | Wander (tours) | Oracles | Targets |
|---|---|---|---|---|---|---|
```

## Session entry (in `EXPLORATORY.md`)

```markdown
### <YYYY-MM-DD> — charter #<n>, <principal>, <device + runtime>, build <sha>, by <person | tester agent>, <min> min
Start: data <seed/volume>, zone <…>, locale <…>
| Severity | Finding (did → happened → expected) | Evidence | TF / DEF / decision |
|---|---|---|---|
Debrief: covered <…> · not covered <…> · questions <…> · new charters / tests <…>
```
