# Design Excellence

Code **DSN**. The design bar and its proof: beauty through hierarchy, rhythm and restraint; minimal flows; every
device class, volume, state and failure designed; WCAG 2.2 AA as testable checks; per-profile deliverables; the
quality rubric; Design QA on the rendered product. Applied by the Designer (`design.md`, `design-system.md`,
`design_review.md`); the Checklist is the Manager's Gate UX checklist (QA items: Design QA); the Tester binds it at
Plan & Bind; the Auditor cites it at L2. Related: LOC (`absd/playbook/design/content-and-locale.md`); A11Y, VIS
(`absd/playbook/testing/nonfunctional.md`).

## Checklist

- [ ] A section per declared profile; never N/A while the interface exists (DSN-1)
- [ ] Designer-authored and complete; every UXQ/UXA has a default + impact (DSN-2)
- [ ] Design-system tokens and components only; hierarchy, type, colour, spacing, grid (DSN-3)
- [ ] Steps counted; one primary action per surface; progressive disclosure; YAGNI (DSN-4)
- [ ] State matrix with 0 blank cells; every data-view state; hidden vs disabled per role (DSN-5)
- [ ] Motion: token, purpose, reduced-motion variant; signature moments (DSN-6)
- [ ] Each journey step: screen, focus after, confirmation; interruptions; dirty-dismiss guard (DSN-7)
- [ ] Device × journey table; blueprint per class, smallest first; phone unless waived (DSN-8)
- [ ] Zero hover-only controls, information or disabled reasons (DSN-9)
- [ ] Scroll containers annotated; overscroll contained; safe areas, on-screen keyboard, landscape (DSN-10)
- [ ] Lists at 0, 1, a page and max in real order; initial selection visible (DSN-11)
- [ ] Input survives refresh; idle screens silent; latest input wins; optimistic UI rolls back (DSN-12)
- [ ] Error catalogue row per external failure mode; notification policy (DSN-13)
- [ ] Name, role, state per interactive element; labels linked; keyboard path; dialog contract (DSN-14)
- [ ] Computed contrast; targets ≥ 24×24, 44×44 on touch; reflow 320 px; zoom 200 % (DSN-15)
- [ ] Every statement observable; trace table complete (DSN-16)
- [ ] cli: grammar, help, `--json`, stdout/stderr, exit codes, `NO_COLOR`/TTY/width (DSN-17)
- [ ] library / http-api / data-pipeline: surface, errors, examples, contracts, runbook (DSN-18)
- [ ] Rubric with evidence: every dimension ≥ 4, every ★ dimension 5 (DSN-19)
- [ ] QA: every gallery image or golden output reviewed; DQ findings; verdict (DSN-20)
- [ ] QA: baselines of protected screens approved by path + hash (DSN-21)

## Rules

**DSN-1** — Deliver the design of every interface profile declared in `context.md` per the table below; a deliverable is never N/A while its interface exists.
- *Why:* web-only assumptions left a CLI's grammar, errors and exit codes to the architecture, with no oracle (LL-41).
- *Check:* one `design.md` section per profile holding every listed element; `absd/tooling/trace_check.py` gate-ux passes.
- *Applies when:* always.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

| Profile | `design.md` delivers |
|---|---|
| web-ui, native-app | UJ, SCR, blueprints per device class, state matrix, copy, names, formatters, volume, resilience, motion, a11y, protected screens (DSN-2–16, 19–21); native adds platform conventions |
| cli | DSN-17 + golden outputs (DSN-20, DSN-21) |
| http-api, library, data-pipeline | DSN-18 |
| every profile | DSN-2, DSN-4, DSN-11, DSN-13, DSN-16, DSN-19, LOC |

**DSN-2** — Have the Designer author all of `design.md`: every section present (delta: "Unchanged — reason"; N/A with a reason), every UXQ-n/UXA-n with a recommended default and its touch, a11y and testability impact, none resolved by the Designer.
- *Why:* the gatekeeper wrote and approved the thinnest spec, for the riskiest phone screen (LL-26); a hover-only default in an open question went unchallenged (LL-52).
- *Check:* design.md commits carry `ABSD-Agent: designer`; sections 100 %; UXQs answered in brd.md Decisions; an interrupted Designer is resumed.
- *Applies when:* always.
- *Provenance:* LL-26, LL-52 (KatenatsioTipster, 2026-10)

**DSN-3** — Compose every screen from `design-system.md` for hierarchy and rhythm: semantic tokens only (colour roles, type and spacing scales, radius, elevation, motion, breakpoints), one shared component per pattern, one focal point, type from the scale (default ≤ 3 sizes, 2 weights per screen), every edge on the grid, accent reserved for the primary action and selection, status colour paired with icon or text; a missing token or component is a logged design-system amendment.
- *Why:* per-screen improvisation drifts (one badge, three colourings) and buries what matters.
- *Check:* named tokens and components exist in design-system.md (grep); Design QA: squint test, alignment overlay, type and colour counts, identical patterns.
- *Applies when:* web-ui, native-app (cli: output style guide; library: naming guide).
- *Provenance:* industry baseline

**DSN-4** — Minimise the user's work: count each journey's steps and fields and justify each by a requirement; one primary action per surface; rare options behind progressive disclosure; defaults prefilled; plain words; nothing beyond `analysis.md`.
- *Why:* every extra step, choice or term costs on every use and adds a way to fail.
- *Check:* UJs state step counts, SCRs their primary action; every element traces to a requirement; a cognitive walkthrough per primary journey is recorded.
- *Applies when:* always (cli: fewest flags for the common case).
- *Provenance:* industry baseline

**DSN-5** — Design every state: a matrix row per interactive element (default, hover, focus, active, disabled + visible reason, loading, error, empty, success, read-only; accessible role, name, state attribute, touch equivalent) with no blank cell (N/A + reason); per data view loading, empty, populated, partial, validation error, each failure, permission-denied, offline; per role × gated control hidden or disabled-with-reason, gated data withheld by the server; reserved slots so states never shift layout.
- *Why:* unspecified states broke: "clear all" made blank rows (LL-6), a screen did not advance (LL-19), merely hidden paid data reached free accounts (LL-10).
- *Check:* blank cells = 0; a Tester assertion per non-N/A cell and role × control; the gallery shows every SCR × state.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-6, LL-19, LL-10 (KatenatsioTipster, 2026-10)

**DSN-6** — Give motion a purpose: each transition names trigger, property, duration and easing tokens and its purpose (orientation, feedback, continuity), never blocks input, and has a reduced-motion variant; at most three signature moments, specified as precisely and polished on every device class.
- *Why:* decorative motion slows people; an unspecified reduced-motion fallback never gets built.
- *Check:* motion table complete; a journey per motion-heavy screen runs with reduced motion emulated, no transform animation; Design QA reviews signature moments.
- *Applies when:* web-ui, native-app with motion.
- *Provenance:* industry baseline

**DSN-7** — Number each journey step and name the screen (SCR-n), the element (accessible name), the screen and focused element after the action and the visible confirmation; add recovery and interruption paths (background refresh, session expiry, back/refresh, second tab, network loss, re-entry); irreversible actions confirm with consequence copy; every dismissal of unsaved input (close, Escape, backdrop, back) asks first.
- *Why:* a key action left the user on the wrong screen (LL-19); a phone gesture reloaded the app and lost input (LL-4).
- *Check:* no step lacks screen + focus after; tests assert location, focus and confirmation per step (desktop and phone) and each dismissal × {clean, dirty}.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19, LL-4 (KatenatsioTipster, 2026-10)

**DSN-8** — Treat each device class as its own target: a device × journey table (phone portrait and landscape, tablet, desktop; phone on for web-ui unless waived in brd.md Decisions), a blueprint per supported class for every screen drawn smallest first, input modality per class (touch, pointer, keyboard), and a tablet layout per orientation.
- *Why:* designs and tests were desktop-only; three phone defects reached users (LL-4).
- *Check:* every SCR has a blueprint per supported class; every UJ runs on each listed class (VAR-6); the gallery covers every class.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-9** — Make nothing depend on hover: hover only enhances what touch and keyboard already reach; a disabled action shows its reason as visible linked text; a tooltip is never the only carrier; close, sign-out and exit actions are always visible.
- *Why:* a hover-only control was unreachable on touch screens (LL-16) after the gate approved it (LL-52).
- *Check:* each hover, tooltip and title in design.md has a touch + keyboard equivalent, asserted visible and operable on a touch profile.
- *Applies when:* web-ui, native-app with touch users.
- *Provenance:* LL-16, LL-52 (KatenatsioTipster, 2026-10)

**DSN-10** — Specify touch behaviour: each scroll container's axis, overscroll containment and initial position; overlays and inner lists contain overscroll and lock the page so pull-to-refresh, edge or back swipes never reload, navigate or lose input; fixed bars respect safe areas; the focused field and its primary action stay above the on-screen keyboard, with the matching keyboard type; full-height surfaces use the visible viewport; landscape works (WCAG 1.3.4).
- *Why:* swiping a picker list fired the page's pull-to-refresh, reloading the app and losing input (LL-4).
- *Check:* a real swipe past every scroll edge in the phone project: no reload or navigation, input kept (the outcome, not a style property); Mode R real-device session (EXPL).
- *Applies when:* web-ui, native-app on touch devices.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-11** — Specify every list, table, select and tab strip at 0, 1, one page and the Data Volume Profile max in real order (search, filters, grouping, paging, count, truncation) and its initial selection, focus and scroll, saying which wins when "first listed" ≠ "earliest" and keeping the selection visible at the smallest size; when the max cannot render within budget, paging or virtualisation is a stated requirement.
- *Why:* a three-item fake hid a default group sitting off-screen among hundreds (LL-4).
- *Check:* each list cites `context.md` volume; max-volume seeds with first ≠ earliest (VAR-7) prove the selection in viewport at phone size, within budget.
- *Applies when:* variable-length collections, any profile.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-12** — Protect user state from the system: dialogs, typed input, focus and scroll survive background refresh, polling, timers and re-renders; a screen at rest makes no requests unless `design.md` specifies polling (interval, scope, pause when hidden); the latest input wins (a late response never overwrites newer input); submits ignore repeats; optimistic UI only for reversible actions, with stated rollback and conflict copy.
- *Why:* a clock re-render refetched every second and wiped a dialog mid-typing (LL-12); a delayed search reload overwrote a filter clicked after typing (LL-20).
- *Check:* zero requests at rest beyond the longest timer, typed dialog text intact; act inside the debounce window, both inputs hold; an injected conflict rolls back with copy.
- *Applies when:* UIs with timers, polling, live data or async calls.
- *Provenance:* LL-12, LL-20 (KatenatsioTipster, 2026-10)

**DSN-13** — Design an error catalogue: per external failure mode (analysis.md) and per error class a message key, exact copy saying what happened and what to do, placement, recovery control and whether input is kept, plus a generic fallback with retry; errors needing action persist or sit by their cause, successes are polite and transient, messages never overlap.
- *Why:* an external service's failures surfaced as "Server error" (LL-11).
- *Check:* every analysis.md failure mode has a row (trace_check); each is injected and its copy and recovery asserted; raw server text fails end-to-end.
- *Applies when:* any interface that can fail (cli: stderr + exit code; http-api: error body).
- *Provenance:* LL-11 (KatenatsioTipster, 2026-10)

**DSN-14** — Specify for every interactive element an accessible name (containing its visible label, unique per screen), role and state from the matching WAI-ARIA Authoring Practices pattern; link every label to its field; give each journey a keyboard path and focus order with visible, unobscured focus; apply the dialog contract (name, initial focus, focus trapped, Escape closes, focus restored); one polite status region per screen (errors assertive; never a live table); declare the page language.
- *Why:* unnamed buttons, unlinked labels and dialogs without trap or restore shipped despite the spec (LL-19).
- *Check:* tests select only by role + name or label (E2E-2), each matching one element; every journey completes keyboard-only; a scan (e.g. axe-core, Pa11y, Lighthouse) per SCR state and device class: 0 serious/critical.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-15** — Prove perception with numbers: computed contrast per token pair incl. dimmed states (text 4.5:1, large text and UI parts 3:1), a minimum text size, targets ≥ 24×24 CSS px everywhere and 44×44 on touch layouts (smaller needs a recorded reason), reflow at 320 CSS px, 200 % zoom and text spacing without loss, never colour alone.
- *Why:* estimated ratios hid a failing label pair; specified 44 px targets shipped at about 26 px (LL-19).
- *Check:* contrast script over the token table; target sizes measured in the phone project; reflow and zoom runs; estimated ratios fail Gate UX.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-16** — Write every normative statement as an observable (exact copy, accessible name, state attribute, device class, focus target, format literal, timing), never an unmeasured adjective like "intuitive" or "fast", and end with a trace table requirement → UJ/SCR → matrix row.
- *Why:* measurable criteria never became tests; tests came after the code (LL-45, LL-29).
- *Check:* Plan & Bind raises 0 blocking "untestable design statement" defects; trace_check gate-ux has no unmapped requirement.
- *Applies when:* always.
- *Provenance:* LL-45, LL-29 (KatenatsioTipster, 2026-10)

**DSN-17** — Design the CLI: one grammar (`tool noun verb` or `tool verb`) and flag style (long kebab-case, short only for the commonest); `--help` per command with usage, examples and exit codes; human output by default and a stable documented `--json`; data to stdout, progress, prompts and diagnostics to stderr; an exit-code table (0 ok, 2 usage, others documented); colour only on a TTY with `NO_COLOR` unset; wrap to terminal width; prompts only on a TTY, destructive commands need `--yes` otherwise; every error says what failed and what to do.
- *Why:* nobody designed a CLI's grammar, errors or exit codes, so tests had no oracle (LL-41).
- *Check:* golden output per command × {TTY, pipe, `NO_COLOR`, narrow, `--json`}; subprocess tests assert stdout, stderr and exit code.
- *Applies when:* cli.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

**DSN-18** — Design machine surfaces for consumers: library — smallest public surface, names per the naming guide, typed documented errors, a runnable example per public symbol, deprecation + semver; http-api — resource model, one error body (code, message key, field errors, correlation id), stable-order pagination with a max page size, versioning, an example per operation and error; data-pipeline — a contract per dataset (schema, units, explicit zones, nullability, keys, duplicate and late-data semantics, field meaning from a recorded real sample) and a runbook (rerun, backfill, alert → first action).
- *Why:* a field's meaning and a source's date zone were taken from a description; stored results were wrong (LL-2).
- *Check:* examples run as consumer tests on the installed package or running service; contract fields match recorded payloads (FAKE-2).
- *Applies when:* library, http-api, data-pipeline.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**DSN-19** — Score `design.md` against the rubric with evidence per dimension; submit only when every dimension is ≥ 4 and every ★ dimension 5; a score without evidence counts as 1; non-visual profiles mark D2, D5 and D7 N/A with a reason.
- *Why:* a gate taking assessment without evidence approved a hover-only design (LL-52).
- *Check:* Gate UX: each score cites a section, computed value or blueprint; any score below the bar returns the design.
- *Applies when:* always.
- *Provenance:* LL-52 (KatenatsioTipster, 2026-10)

Scale: 1 missing or broken · 2 breaks a DSN/LOC rule · 3 meets every rule of the dimension · 4 meets them on every
screen, class and state with no Minor finding · 5 is 4 plus craft: a peer cannot name an in-scope improvement.

| Dimension (5 looks like) | Evidence: spec → rendered |
|---|---|
| D1 Hierarchy (one focal point and primary action) | blueprints → squint test |
| D2 Type, rhythm & grid (scale only, aligned at every class) | tokens, blueprints → overlay |
| D3 Colour ★ (roles only, computed ratios pass) | ratio table → scan |
| D4 States ★ (empty, loading, error as crafted as populated) | 0 blank cells → SCR × state gallery |
| D5 Motion (purposeful; signature moments delight) | motion table → recording |
| D6 Flow (fewest steps, plain words) | step counts → journey run |
| D7 Devices ★ (every class designed, touch-first) | device table → phone/tablet gallery |
| D8 Accessibility ★ (DSN-14, DSN-15 met) | names, keyboard paths → scan, keyboard TCs |
| D9 Content ★ (copy deck, label maps, formatters) | LOC tables → literal oracles |
| D10 Resilience (volume, idle, races, failures) | volume and error rows → TCs |
| D11 Consistency (design system only) | amendment log → cross-screen gallery |
| D12 Testability ★ (every statement observable) | trace table → 0 untestable |

**DSN-20** — Run Design QA on the rendered product: open every image of the Tester's gallery (`absd-project/working/evidence/tester/screens/`, SCR × state × device class × theme) or golden output, compare with `design.md`, `design-system.md` and the rubric, re-score from what is visible, write DQ-n findings (unified schema, image path as evidence; drift → Builder, design gap → Designer), and pass only at the DSN-19 bar with 0 Critical/Major.
- *Why:* fidelity audits passed by reading code while raw enums, mixed formats and truncation were on screen (LL-19).
- *Check:* every gallery cell marked reviewed; a missing cell makes the verdict BLOCKED (GATE-1); a wrong value users act on is Critical, a rule breach with user impact Major, polish Minor.
- *Applies when:* web-ui, native-app; cli and data-pipeline via golden output.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-21** — List the protected screens (SCR × state × device class × theme), approve each baseline by path and content hash in `design_review.md`, and change a baseline only when a `design.md` change intends it and the Designer re-approves, never auto-updated to turn a run green.
- *Why:* a "no visual regression" requirement written every cycle was never automated (LL-53).
- *Check:* the visual suite (VIS) compares against approved baselines; every baseline change has an approval row (Auditor; GATE-6).
- *Applies when:* web-ui, native-app; golden output for cli and data-pipeline.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10)
