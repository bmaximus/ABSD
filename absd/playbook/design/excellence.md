# Design Excellence

Code **DSN**. The design bar and its proof: beauty through hierarchy, rhythm and restraint; minimal flows; every
device class, volume, state and failure designed; WCAG 2.2 AA as testable checks; per-profile deliverables; the
quality rubric; Design QA on the rendered product. The Designer applies it in `design.md`, `design-system.md` and
`design_review.md`; the Checklist is the Manager's Gate UX checklist (QA items: Design QA); the Tester binds it at
Plan & Bind; the Auditor cites it at L2. Copy and formats: LOC (`absd/playbook/design/content-and-locale.md`); a11y and
visual test mechanics: A11Y, VIS (`absd/playbook/testing/nonfunctional.md`).

## Checklist

- [ ] A design section per declared profile; none N/A while the interface exists (DSN-1)
- [ ] Designer-authored and complete; every UXQ/UXA has a default + impact (DSN-2)
- [ ] Design-system tokens and components only; hierarchy, type, colour roles, spacing, grid set (DSN-3)
- [ ] Steps counted; one primary action per surface; progressive disclosure; nothing beyond analysis.md (DSN-4)
- [ ] State matrix with 0 blank cells; every data-view state; hidden vs disabled per role (DSN-5)
- [ ] Motion: token, purpose, reduced-motion variant; signature moments (DSN-6)
- [ ] Each journey step: screen, focus after, confirmation; interruptions; dirty-dismiss guard (DSN-7)
- [ ] Device × journey table; blueprint per class, smallest first; phone unless waived (DSN-8)
- [ ] Zero hover-only controls, information or disabled reasons (DSN-9)
- [ ] Scroll containers annotated; overscroll contained; safe areas, on-screen keyboard, landscape (DSN-10)
- [ ] Lists at 0, 1, a page and max in real order; initial selection visible (DSN-11)
- [ ] Input and dialogs survive refresh; idle screens make no requests (DSN-12)
- [ ] Latest input wins; repeats ignored; optimistic UI has rollback (DSN-13)
- [ ] Error catalogue row per external failure mode; notification policy (DSN-14)
- [ ] Name, role, state per interactive element; labels linked; keyboard path; dialog contract (DSN-15)
- [ ] Computed contrast; targets ≥ 24×24, 44×44 on touch; reflow 320 px; zoom 200 % (DSN-16)
- [ ] Every statement observable; trace table complete (DSN-17)
- [ ] cli: grammar, help, `--json`, stdout/stderr, exit codes, `NO_COLOR`/TTY/width (DSN-18)
- [ ] library / http-api / data-pipeline: surface, errors, examples, contracts, runbook (DSN-19)
- [ ] Rubric with evidence: every dimension ≥ 4, every ★ dimension 5 (DSN-20)
- [ ] QA: every gallery image or golden output reviewed; DQ findings; verdict (DSN-21)
- [ ] QA: baselines of protected screens approved by path + hash (DSN-22)

## Rules

**DSN-1** — Deliver the design of every interface profile declared in `context.md` per the table below; a deliverable is never N/A while its interface exists.
- *Why:* web-only assumptions left a CLI's grammar, errors and exit codes to the architecture, with no oracle (LL-41).
- *Check:* Gate UX: one `design.md` section per profile with every listed element; `absd/tooling/trace_check.py` gate-ux maps every requirement with an interface effect.
- *Applies when:* always.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

| Profile | `design.md` delivers |
|---|---|
| web-ui, native-app | UJ, SCR, blueprints per device class, state matrix, copy deck, names, formatters, volume, resilience, motion, a11y, protected screens (native: platform conventions) |
| cli | grammar, flags, help, human + `--json` output, stdout/stderr, exit codes, `NO_COLOR`/TTY/width |
| http-api | resource model, error body, pagination, versioning, examples |
| library | public surface, naming, error types, examples, deprecation + semver |
| data-pipeline | data contracts, operator runbook + alerts |

**DSN-2** — Have the Designer author all of `design.md`: every section present (delta: "Unchanged — reason"; N/A with a reason), every UXQ-n/UXA-n with a recommended default and its touch, a11y and testability impact, none resolved by the Designer.
- *Why:* the gatekeeper wrote, then approved, the thinnest spec for the most phone-critical screen (LL-26); an open question's hover-only default passed unchallenged (LL-52).
- *Check:* design.md commits carry `ABSD-Agent: designer`; sections 100 %; UXQs answered in brd.md Decisions; an interrupted Designer is resumed, never replaced.
- *Applies when:* always.
- *Provenance:* LL-26, LL-52 (KatenatsioTipster, 2026-10)

**DSN-3** — Compose every screen from `design-system.md` for hierarchy and rhythm: semantic tokens only (colour roles, type and spacing scales, radius, elevation, motion, breakpoints), one shared component per pattern, one focal point, type from the scale (default ≤ 3 sizes, 2 weights per screen), every edge on the grid, accent reserved for the primary action and selection, status colour paired with icon or text; a missing token or component is a logged design-system amendment.
- *Why:* per-screen improvisation drifts (one badge, three colourings) and buries the important thing.
- *Check:* tokens and components named in design.md exist in design-system.md (grep); Design QA: squint test, alignment overlay, sizes, weights and colours counted, one pattern identical everywhere.
- *Applies when:* web-ui, native-app (cli: output style guide; library: naming guide).
- *Provenance:* industry baseline

**DSN-4** — Minimise the user's work: count each journey's steps and fields and justify each by a requirement; one primary action per surface; rare options behind progressive disclosure; defaults prefilled; plain words; nothing beyond `analysis.md`.
- *Why:* every extra step, choice or term costs on every use and is one more way to fail.
- *Check:* each UJ states its step count, each SCR its primary action; every element traces to a requirement id; a cognitive walkthrough per primary journey is recorded.
- *Applies when:* always (cli: fewest flags for the common case).
- *Provenance:* industry baseline

**DSN-5** — Design every state: a matrix row per interactive element (default, hover, focus, active, disabled + visible reason, loading, error, empty, success, read-only; accessible role, name, state attribute, touch equivalent) with no blank cell (N/A + reason); per data view loading, empty, populated, partial, validation error, each failure, permission-denied, offline; per role × gated control hidden or disabled-with-reason, gated data withheld by the server; reserved slots so states never shift layout.
- *Why:* unspecified states shipped broken: "clear all" filled a grid with blank rows (LL-6), a screen did not advance (LL-19), paid data merely not shown still reached free accounts (LL-10).
- *Check:* blank cells = 0; one Tester assertion per non-N/A cell and per role × control; the gallery shows every SCR × state; boxes equal across a state flip.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-6, LL-19, LL-10 (KatenatsioTipster, 2026-10)

**DSN-6** — Give motion a purpose: each transition names trigger, property, duration and easing tokens and its purpose (orientation, feedback, continuity), never blocks input, and has a reduced-motion variant; at most three signature moments, specified as precisely and polished on every device class.
- *Why:* decorative motion slows people; a reduced-motion fallback not specified per transition is never built.
- *Check:* motion table complete; one journey per motion-heavy screen runs with reduced motion emulated and no transform animation; Design QA reviews signature moments on a recording.
- *Applies when:* web-ui, native-app with motion.
- *Provenance:* industry baseline

**DSN-7** — Number each journey step and name the screen (SCR-n), the element (accessible name), the screen and focused element after the action and the visible confirmation; add recovery and interruption paths (background refresh, session expiry, back/refresh, second tab, network loss, re-entry); irreversible actions confirm with consequence copy; every dismissal of unsaved input (close, Escape, backdrop, back) asks first.
- *Why:* a key action left the user on the wrong screen (LL-19); a phone gesture reloaded the app and lost input (LL-4).
- *Check:* no step lacks screen + focus after; the Tester asserts location, focus and confirmation per step on desktop and phone, and each dismissal × {clean, dirty}.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19, LL-4 (KatenatsioTipster, 2026-10)

**DSN-8** — Treat each device class as its own target: a device × journey table (phone portrait and landscape, tablet, desktop; phone on for web-ui unless waived in brd.md Decisions), a blueprint per supported class for every screen drawn smallest first, input modality per class (touch, pointer, keyboard), and a tablet layout per orientation.
- *Why:* designs and tests were desktop-only; three phone defects reached users (LL-4).
- *Check:* every SCR has a blueprint per supported class; every UJ runs on each listed class (VAR-6); the gallery covers every class.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-9** — Make nothing depend on hover: hover only enhances what touch and keyboard already reach; a disabled action shows its reason as visible linked text; a tooltip is never the only carrier; close, sign-out and exit actions are always visible.
- *Why:* a hover-only control was unreachable on touch screens (LL-16) after the gate approved it (LL-52).
- *Check:* Gate UX searches design.md for hover, tooltip and title and finds a touch + keyboard equivalent for each; the Tester asserts each is visible and operable on a touch profile.
- *Applies when:* web-ui, native-app with any touch-capable audience.
- *Provenance:* LL-16, LL-52 (KatenatsioTipster, 2026-10)

**DSN-10** — Specify touch behaviour: each scroll container's axis, overscroll containment and initial position; overlays and inner lists contain overscroll and lock the page so pull-to-refresh, edge or back swipes never reload, navigate or lose input; fixed bars respect safe areas; the focused field and its primary action stay above the on-screen keyboard, with the matching keyboard type; full-height surfaces use the visible viewport; landscape works (WCAG 1.3.4).
- *Why:* swiping a picker list fired the page's pull-to-refresh, reloading the app and losing input (LL-4).
- *Check:* the Tester swipes past every scroll edge in the phone project and asserts no reload or navigation and input kept (the outcome, not a style property); Mode R real-device session (EXPL).
- *Applies when:* web-ui, native-app on touch devices.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-11** — Specify every list, table, select and tab strip at 0, 1, one page and the Data Volume Profile max in real order (search, filters, grouping, paging, count, truncation) and its initial selection, focus and scroll, saying which wins when "first listed" ≠ "earliest" and keeping the selection visible at the smallest size; when the max cannot render within budget, paging or virtualisation is a stated requirement.
- *Why:* a three-item fake hid that the default group sat off-screen among hundreds, so items showed under another group's name (LL-4).
- *Check:* every list cites the `context.md` volume; the Tester seeds max volume with first ≠ earliest (VAR-7) and asserts the selection in viewport at phone size and the budget.
- *Applies when:* variable-length collections, any profile.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-12** — Protect user state from the system: dialogs, typed input, focus, selection and scroll survive background refresh, polling, timers and re-renders; a screen at rest makes no requests unless `design.md` specifies polling (interval, scope, pause when hidden); tickers re-render only themselves.
- *Why:* a clock re-render refetched every second and wiped a dialog mid-typing (LL-12).
- *Check:* per screen, zero requests at rest for longer than the longest timer, and typed dialog text unchanged after it.
- *Applies when:* web-ui, native-app with timers, polling or live data.
- *Provenance:* LL-12 (KatenatsioTipster, 2026-10)

**DSN-13** — State async rules per interaction: the latest input wins (a late response never overwrites newer input), debounce windows are named, submits show loading and ignore repeats, optimistic UI only for reversible actions with a stated rollback and conflict copy.
- *Why:* a filter clicked right after typing was overwritten by the delayed search reload (LL-20).
- *Check:* act inside the debounce window and assert both inputs hold; inject a conflict and assert rollback + copy; a double activation submits once.
- *Applies when:* interactive profiles with async loads or writes.
- *Provenance:* LL-20 (KatenatsioTipster, 2026-10)

**DSN-14** — Design an error catalogue: per external failure mode (analysis.md) and per error class a message key, exact copy saying what happened and what to do, placement, recovery control and whether input is kept, plus a generic fallback with retry; errors needing action persist or sit by their cause, successes are polite and transient, messages never overlap.
- *Why:* an external service's failures surfaced as "Server error" (LL-11).
- *Check:* every analysis.md failure mode has a row (trace_check); each is injected and its copy and recovery asserted; end-to-end fails on raw server text.
- *Applies when:* any interface that can fail (cli: stderr + exit code; http-api: error body).
- *Provenance:* LL-11 (KatenatsioTipster, 2026-10)

**DSN-15** — Specify for every interactive element an accessible name (containing its visible label, unique per screen), role and state from the matching WAI-ARIA Authoring Practices pattern; link every label to its field; give each journey a keyboard path and focus order with visible, unobscured focus; apply the dialog contract (name, initial focus, focus trapped, Escape closes, focus restored); one polite status region per screen (errors assertive; never a live table); declare the page language.
- *Why:* unnamed buttons, unlinked labels and dialogs without trap or restore shipped despite the spec and forced positional selectors (LL-19).
- *Check:* tests select only by role + name or label (E2E-2), each resolving to one element; every journey completes keyboard-only; an automated scan (e.g. axe-core, Pa11y, Lighthouse) per SCR state and device class: 0 serious/critical.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-16** — Prove perception with numbers: computed contrast per token pair incl. dimmed states (text 4.5:1, large text and UI parts 3:1), a minimum text size, targets ≥ 24×24 CSS px everywhere and 44×44 on touch layouts (smaller only with a reason in design-system.md), reflow at 320 CSS px, 200 % zoom and text spacing without loss, never colour alone.
- *Why:* an estimated ratio hid a failing muted-label pair; 44 px targets were specified and built at about 26 px (LL-19).
- *Check:* contrast script over the token table; target sizes measured in the phone project; reflow and zoom runs; estimated ratios fail Gate UX.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-17** — Write every normative statement as an observable (exact copy, accessible name, state attribute, device class, focus target, format literal, timing), never an unmeasured adjective like "intuitive" or "fast", and end with a trace table requirement → UJ/SCR → matrix row.
- *Why:* measurable criteria were never turned into tests, and tests came after the code (LL-45, LL-29).
- *Check:* Plan & Bind raises 0 blocking "untestable design statement" defects; trace_check gate-ux has no unmapped requirement.
- *Applies when:* always.
- *Provenance:* LL-45, LL-29 (KatenatsioTipster, 2026-10)

**DSN-18** — Design the CLI: one grammar (`tool noun verb` or `tool verb`) and flag style (long kebab-case, short only for the commonest); `--help` per command with usage, examples and exit codes; human output by default and a stable documented `--json`; data to stdout, progress, prompts and diagnostics to stderr; an exit-code table (0 ok, 2 usage, others documented); colour only on a TTY with `NO_COLOR` unset; wrap to terminal width; prompts only on a TTY, destructive commands need `--yes` otherwise; every error says what failed and what to do.
- *Why:* nobody designed a CLI's grammar, errors or exit codes, so tests had no oracle (LL-41).
- *Check:* golden output per command × {TTY, pipe, `NO_COLOR`, narrow, `--json`}; subprocess tests assert stdout, stderr and exit code.
- *Applies when:* cli.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

**DSN-19** — Design machine surfaces for their consumer: library — smallest public surface, names per the naming guide, typed documented errors, a runnable example per public symbol, deprecation + semver; http-api — resource model, one error body (code, message key, field errors, correlation id), stable-order pagination with a max page size, versioning, an example per operation and error; data-pipeline — a contract per dataset (schema, units, explicit zones, nullability, keys, duplicate and late-data semantics, field meaning from a recorded real sample) and a runbook (rerun, backfill, alert → first action).
- *Why:* a field's meaning and a source's date zone were taken from a description, and stored results were wrong (LL-2).
- *Check:* examples run as consumer tests on the installed package or running service; contract fields match recorded payloads (FAKE-2).
- *Applies when:* library, http-api, data-pipeline.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**DSN-20** — Score `design.md` against the rubric with evidence per dimension; submit only when every dimension is ≥ 4 and every ★ dimension 5; a score without evidence counts as 1; non-visual profiles mark D1–D6 and D8 N/A with a reason.
- *Why:* a gate that accepted assessment without evidence approved a hover-only design (LL-52).
- *Check:* Gate UX: each score cites a section, computed value or blueprint; any score below the bar returns the design.
- *Applies when:* always.
- *Provenance:* LL-52 (KatenatsioTipster, 2026-10)

Scale: 1 missing or broken · 2 breaks a DSN/LOC rule · 3 meets every rule of the dimension · 4 meets them on every
screen, class and state with no Minor finding · 5 is 4 plus craft: a peer cannot name an in-scope improvement.

| Dimension | 5 looks like | Evidence (spec → rendered) |
|---|---|---|
| D1 Hierarchy | one focal point and primary action | blueprints → squint test |
| D2 Type & rhythm | scale-only type, steady rhythm | tokens → measured screenshots |
| D3 Colour ★ | roles only, computed ratios pass | ratio table → scan |
| D4 Grid | aligned at every class, stable across states | blueprints → overlay |
| D5 States ★ | empty, loading, error as crafted as populated | 0 blank cells → SCR × state gallery |
| D6 Motion | purposeful, reduced variant, signature moments delight | motion table → recording |
| D7 Flow | fewest steps, plain words | step counts → journey run |
| D8 Devices ★ | each class designed, touch-first | device table → phone/tablet gallery |
| D9 Accessibility ★ | DSN-15 and DSN-16 fully specified | names, keyboard → scan + keyboard TCs |
| D10 Content ★ | copy deck, label maps, formatters | LOC tables → literal oracles |
| D11 Resilience | volume, idle, races, failures designed | rows → TCs |
| D12 Consistency | design-system only | amendment log → cross-screen gallery |
| D13 Testability ★ | every statement observable | trace table → 0 untestable |

**DSN-21** — Run Design QA on the rendered product: open every image of the Tester's gallery (`absd-project/working/evidence/tester/screens/`, SCR × state × device class × theme) or golden output, compare with `design.md`, `design-system.md` and the rubric, re-score from what is visible, write DQ-n findings (unified schema, image path as evidence; drift → Builder, design gap → Designer), and pass only at the DSN-20 bar with 0 Critical/Major.
- *Why:* design-fidelity audits passed by reading code while raw enums, mixed formats and truncation were visible on screen (LL-19).
- *Check:* design_review.md marks every gallery cell reviewed; a missing cell makes the verdict BLOCKED (GATE-1); a wrong value users act on is Critical, a rule breach with user impact Major, polish Minor.
- *Applies when:* web-ui, native-app; cli and data-pipeline via golden output.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-22** — List the protected screens (SCR × state × device class × theme), approve each baseline by path and content hash in `design_review.md`, and change a baseline only when a `design.md` change intends it and the Designer re-approves, never auto-updated to turn a run green.
- *Why:* a "no visual regression" requirement written every cycle was never automated (LL-53).
- *Check:* the visual suite (VIS) compares against approved baselines; the Auditor finds an approval row for every baseline change (GATE-6).
- *Applies when:* web-ui, native-app; golden output for cli and data-pipeline.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10)
