# Design Excellence

Code **DSN**. The bar every design must reach and how it is proven: beauty through hierarchy, rhythm and restraint;
minimal flows; every device class, volume, state and failure designed; WCAG 2.2 AA as testable checks; per-profile
deliverables; the design-quality rubric; Design QA on the rendered product. The Designer applies it in `design.md`,
`design-system.md` and `design_review.md`; the Checklist is also the Manager's Gate UX checklist (items marked QA are
checked at Design QA); the Tester turns it into tests at Plan & Bind; the Auditor cites it at L2. Copy, formatting and
locale are LOC (`absd/playbook/design/content-and-locale.md`); accessibility and visual-regression test mechanics are
A11Y and VIS (`absd/playbook/testing/nonfunctional.md`).

## Checklist

- [ ] One design section per declared interface profile; none N/A while the interface exists (DSN-1)
- [ ] Designer-authored, every section complete; each UXQ/UXA has a default + impact, none self-resolved (DSN-2)
- [ ] Only design-system tokens and shared components; amendments logged (DSN-3)
- [ ] Type scale, colour roles, spacing scale, grid and alignment set per screen (DSN-4)
- [ ] Steps counted per journey; one primary action per surface; progressive disclosure; nothing beyond analysis.md (DSN-5)
- [ ] Component–state matrix per interactive element with 0 blank cells; every data-view state incl. each failure (DSN-6)
- [ ] Motion table: token, purpose, reduced-motion variant; signature moments specified (DSN-7)
- [ ] Every journey step: screen, element, screen + focus after, confirmation; interruption paths; dirty-dismiss guard (DSN-8)
- [ ] Device × journey table; blueprint per device class, smallest first; phone on unless waived (DSN-9)
- [ ] Zero hover-only controls, information or disabled reasons (DSN-10)
- [ ] Scroll containers annotated; overscroll contained; safe areas, on-screen keyboard, landscape (DSN-11)
- [ ] Every list at 0, 1, a page and the Data Volume Profile max in real order; paging/virtualisation stated (DSN-12)
- [ ] Initial selection, focus and scroll per view; selection visible at the smallest size (DSN-13)
- [ ] Input and dialogs survive background refresh; idle screens request nothing unless polling is specified (DSN-14)
- [ ] Latest input wins; repeat submits ignored; optimistic UI has rollback + copy (DSN-15)
- [ ] Error catalogue: a row per external failure mode with copy, placement, recovery; notification policy (DSN-16)
- [ ] Role × gated control: hidden or disabled-with-reason; gated data withheld by the server (DSN-17)
- [ ] Accessible name, role and state for every interactive element; labels linked; live-region plan (DSN-18)
- [ ] Keyboard path per journey; focus order, visible focus, dialog contract (DSN-19)
- [ ] Computed contrast; targets ≥ 24×24 (44×44 touch); reflow 320 px; zoom 200 %; no colour-only meaning (DSN-20)
- [ ] Every statement observable (copy, name, state, device, literal); trace table complete (DSN-21)
- [ ] cli: grammar, help, `--json`, stdout/stderr, exit codes, `NO_COLOR`/TTY/width, error text (DSN-22)
- [ ] library / http-api / data-pipeline: surface, errors, examples, versioning, data contracts, runbook (DSN-23)
- [ ] Rubric scored with evidence: every dimension ≥ 4, every ★ dimension 5 (DSN-24)
- [ ] QA: every gallery image or golden output opened; rubric re-scored; DQ findings; verdict (DSN-25)
- [ ] QA: protected screens listed; baselines approved by path + hash; never auto-updated (DSN-26)

## Rules

**DSN-1** — Deliver the design of every interface profile declared in `context.md` as the table below requires; a deliverable is never N/A while its interface exists.
- *Why:* web-only assumptions left a CLI's grammar, errors and exit codes to be invented in the architecture, with no oracle for tests (LL-41).
- *Check:* Gate UX: one `design.md` section per declared profile containing every listed element; `absd/tooling/trace_check.py` gate-ux maps every requirement with an interface effect.
- *Applies when:* always.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

| Profile | `design.md` delivers | Rules |
|---|---|---|
| web-ui, native-app | UJ, SCR, blueprints per device class, component–state matrix, copy deck, accessible names, formatters, volume, resilience, motion, a11y, protected screens; native adds platform conventions | DSN-3…21, 24–26, LOC |
| cli | grammar, flags, help, human + `--json` output, stdout/stderr, exit codes, `NO_COLOR`/TTY/width | DSN-21, 22, 24, 25, LOC |
| http-api | resource model, error body, pagination, versioning, examples | DSN-21, 23, 24, LOC |
| library | public surface, naming, error types, examples, deprecation + semver | DSN-21, 23, 24 |
| data-pipeline | data contracts (schema, units, zones, nullability, keys, duplicates, late data), runbook + alerts | DSN-21, 23–25, LOC |

**DSN-2** — Have the Designer author the whole `design.md`: every section present (a delta says "Unchanged — reason"; N/A always carries a reason), open questions UXQ-n and assumptions UXA-n each with a recommended default and its touch, accessibility and testability impact, none resolved by the Designer.
- *Why:* when the designer could not run, the gatekeeper wrote the thinnest spec for the most phone-critical screen and approved it (LL-26); a hover-only recommendation in an open question passed unchallenged (LL-52).
- *Check:* Gate UX: design.md commits carry `ABSD-Agent: designer`; section checklist 100 %; each UXQ answered by the user in brd.md Decisions; an interrupted Designer is resumed, never replaced.
- *Applies when:* always.
- *Provenance:* LL-26, LL-52 (KatenatsioTipster, 2026-10)

**DSN-3** — Build every surface from `design-system.md`: semantic tokens (colour roles, type scale, spacing scale, radius, elevation, motion, breakpoints) and one named shared component per pattern (dialog, sheet, toast, badge, chip, tabs, table, form field, formatter); a missing token or component is a design-system amendment with a change-log row, never a raw value in `design.md`.
- *Why:* patterns re-implemented per screen drift (one badge in three colourings) and a token that does not exist renders wrong silently.
- *Check:* every token and component named in design.md exists in design-system.md (grep); amendments logged; Design QA: one pattern looks and behaves the same on every screen.
- *Applies when:* web-ui, native-app (cli: output style guide; library: naming guide).
- *Provenance:* industry baseline

**DSN-4** — Compose each screen for beauty through hierarchy and rhythm: one focal point; type from the scale only (default ≤ 3 sizes, 2 weights per screen); spacing from the scale, related items closer than unrelated; every edge on the grid; accent colour reserved for the primary action and selection; status colour always paired with icon or text; no decoration that carries no information.
- *Why:* beauty that is not specified is improvised per screen; restraint is what makes the important thing visible first.
- *Check:* blueprints name grid, tokens and focal point; Design QA on the gallery: squint test (primary action seen first), alignment overlay, count of sizes, weights and colours against the design system.
- *Applies when:* web-ui, native-app.
- *Provenance:* industry baseline

**DSN-5** — Minimise the user's work: count the steps and fields of every journey and justify each against a requirement; one primary action per surface; rare or advanced options behind progressive disclosure; sensible defaults prefilled; plain language; no screen, setting or control beyond `analysis.md` (YAGNI).
- *Why:* every extra step, choice or term is a chance to fail and a cost on every use.
- *Check:* each UJ lists its step count; each SCR names its primary action; every element traces to a requirement id; a cognitive walkthrough of each primary journey is recorded with findings.
- *Applies when:* always (cli: fewest flags for the common case).
- *Provenance:* industry baseline

**DSN-6** — Design every state: a component–state matrix row per interactive element (default, hover, focus, active, disabled with visible reason, loading, error, empty, success, read-only + accessible role, accessible name, state attribute, touch equivalent of hover) with no blank cell (N/A + reason), and per data view loading, empty, populated, partial, validation error, each failure mode, permission-denied, offline/slow; state changes never shift layout (reserved slots).
- *Why:* unspecified states shipped broken — a "clear all" that filled a grid with blank rows, an unchanged screen after a key action (LL-6, LL-19).
- *Check:* Gate UX: blank cells = 0; the Tester derives one assertion per non-N/A cell; the gallery shows every SCR × state; bounding boxes equal before and after a state flip.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-6, LL-19 (KatenatsioTipster, 2026-10)

**DSN-7** — Give motion a purpose: each transition names trigger, property, duration and easing tokens and its purpose (orientation, feedback, continuity), never blocks input, and has a reduced-motion variant (opacity or instant); `design-system.md` lists at most three signature moments, each specified to the same precision and polished on every device class.
- *Why:* decorative motion slows people down; a mandated reduced-motion fallback that is never specified per transition is never built.
- *Check:* motion table complete; the Tester runs one journey per motion-heavy screen with the reduced-motion preference emulated and asserts no transform animation; Design QA reviews signature moments on a recording.
- *Applies when:* web-ui, native-app with motion.
- *Provenance:* industry baseline

**DSN-8** — Number every journey step and name the screen (SCR-n), the element acted on (accessible name), the screen and focused element after the action, and the visible confirmation; include error-recovery and interruption paths (background refresh, session expiry, back/refresh, second tab, network loss mid-action, re-entry); confirm irreversible actions with consequence copy, and make every dismissal path of unsaved input (close, Escape, backdrop, back) ask first.
- *Why:* the screen did not advance after a key action (LL-19); a phone gesture reloaded the app and lost the input (LL-4).
- *Check:* Gate UX: no step without screen + focus after; the Tester asserts location, focus and confirmation after each action (desktop and phone) and each dismissal × {clean, dirty}.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19, LL-4 (KatenatsioTipster, 2026-10)

**DSN-9** — Treat each device class as its own target: a device × journey table (phone portrait and landscape, tablet, desktop; phone on for web-ui unless the user waived it in brd.md Decisions), a blueprint per supported class for every screen drawn smallest first, the input modality per class (touch, pointer, keyboard), and an explicit tablet layout per orientation.
- *Why:* designs and tests were desktop-only; three phone defects reached users (LL-4).
- *Check:* Gate UX: every SCR has a blueprint for every class it supports; the Tester runs every UJ on each listed class (VAR-6); the gallery covers every class.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-10** — Never let a control, information or a disabled reason depend on hover: hover only enhances what touch and keyboard already reach; a disabled action shows its reason as visible text linked to it; a tooltip is never the only carrier; close, sign-out and exit actions are always visible.
- *Why:* a hover-only control was unreachable on touch screens (LL-16), and the gate approved it (LL-52).
- *Check:* Gate UX searches design.md for hover, tooltip and title and finds a touch + keyboard equivalent in the matrix for each; the Tester asserts on a touch profile that each is visible and operable.
- *Applies when:* web-ui, native-app with a touch-capable audience.
- *Provenance:* LL-16, LL-52 (KatenatsioTipster, 2026-10)

**DSN-11** — Specify touch behaviour: annotate every scroll container (axis, overscroll containment, initial position); modals, sheets, drawers and inner lists contain overscroll and lock the page so pull-to-refresh, edge or back swipes never reload, navigate or lose input; fixed bars respect safe-area insets; the focused field and its primary action stay above the on-screen keyboard with the matching keyboard type; full-height surfaces use the visible viewport; landscape works unless essential (WCAG 1.3.4).
- *Why:* swiping a picker list triggered the page's pull-to-refresh and reloaded the app, losing input (LL-4).
- *Check:* the Tester swipes past every scroll edge in the phone project and asserts no reload or navigation and input kept (the outcome, not a style property); Mode R real-device session per `absd/playbook/testing/exploratory.md` (EXPL).
- *Applies when:* web-ui, native-app on touch devices.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-12** — Specify every list, table, select and tab strip at 0, 1, one page and the Data Volume Profile max in its real ordering: search, filters, grouping, paging, count text, pager beyond the visible buttons, truncation; when the max cannot render within the performance budget, paging or virtualisation is a requirement stated with that budget, not an implementation choice.
- *Why:* the fake had three groups where production has hundreds, hiding off-screen selections and slow lists (LL-4).
- *Check:* Gate UX: every list has a volume row citing `context.md`; the Tester seeds max volume with adversarial order (VAR-7) and asserts the behaviour and budget.
- *Applies when:* any variable-length collection on any profile.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-13** — Declare per view the initial selection, focus and scroll position and which order wins when "first listed" ≠ "earliest" or "most relevant"; the selection is inside the viewport at the smallest supported size and content beside it visibly belongs to it.
- *Why:* each day opened on an off-screen group, so its items appeared under another group's name (LL-4).
- *Check:* with max-volume data where first ≠ earliest, the Tester asserts the selected state and in-viewport at phone size.
- *Applies when:* views with a default selection, tabs or more than one screen of content.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**DSN-14** — Protect user state from the system: open dialogs, typed input, focus, selection and scroll survive background refresh, polling, timers and re-renders; a screen at rest makes no requests unless `design.md` specifies polling (interval, scope, pause when hidden); clocks and tickers update only their own element.
- *Why:* a clock re-render refetched every second and wiped a dialog, so a reason could not be typed (LL-12).
- *Check:* the Tester's idle test per screen: zero requests at rest for longer than the longest timer, and typed dialog text unchanged after it.
- *Applies when:* web-ui, native-app with timers, polling or live data.
- *Provenance:* LL-12 (KatenatsioTipster, 2026-10)

**DSN-15** — State async behaviour per interaction: the latest input wins (a late response never overwrites newer input), debounce windows are named, submits show a loading state and ignore repeats, optimistic UI only for reversible actions with a stated rollback and conflict copy, and a conflict updates the item in place with an explanation.
- *Why:* a filter clicked right after typing was overwritten by the delayed search reload (LL-20).
- *Check:* the Tester acts inside the debounce window and asserts both inputs hold; injects a conflict and asserts rollback + copy; a double activation submits once.
- *Applies when:* any interactive profile with async loads or writes.
- *Provenance:* LL-20 (KatenatsioTipster, 2026-10)

**DSN-16** — Design an error catalogue: one row per external failure mode (analysis.md external interfaces) and per error class → message key and exact copy saying what happened and what to do → placement → recovery control → whether input is kept, plus a generic fallback with retry; errors needing action persist or sit inline by their cause, successes are polite and transient, messages never overlap.
- *Why:* failures of an external service surfaced as "Server error" (LL-11).
- *Check:* Gate UX: every failure mode in analysis.md has a row (trace_check); the Tester injects each failure and asserts copy and recovery (Gate T); end-to-end fails on raw server text.
- *Applies when:* any interface that can fail (cli: stderr + exit code; http-api: error body).
- *Provenance:* LL-11 (KatenatsioTipster, 2026-10)

**DSN-17** — For every role × gated control (permission, tier, flag, lifecycle state) state hidden or disabled-with-reason, mark gated data "withheld by the server", and leave no trace (gap, dead link) when a flag is off.
- *Why:* free accounts received paid content in a response the UI merely did not show (LL-10).
- *Check:* the Tester's role × screen assertions per control; visibility cells assert absent fields (ACCESS-3).
- *Applies when:* roles, tiers or flags gate the interface.
- *Provenance:* LL-10 (KatenatsioTipster, 2026-10)

**DSN-18** — Give every interactive element an accessible name, role and state attribute in `design.md` (name contains the visible label, unique per screen, role from the matching WAI-ARIA Authoring Practices pattern), link every visible label to its field, plan one polite status region per screen for async outcomes (errors assertive; never a live table), and declare the page language.
- *Why:* unnamed icon buttons and unlinked labels failed screen-reader users and forced positional test selectors (LL-19).
- *Check:* the Tester selects only by role + name or label (E2E-2), each resolving to one element; an automated scan (e.g. axe-core, Pa11y, Lighthouse) per SCR state on every device class: 0 serious/critical.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-19** — Specify a keyboard path per journey: focus order per screen, a visible focus indicator (≥ 3:1, never hidden by sticky content), no trap outside modal dialogs, and the dialog contract — name, initial focus, Tab cycles inside, Escape closes (dirty guard per DSN-8), focus returns to the trigger; drag actions have a single-pointer alternative.
- *Why:* dialogs specified with focus trap and restore were built without them, and no test noticed (LL-19).
- *Check:* the Tester completes every journey keyboard-only and runs the contract per dialog; the scan runs with each dialog open.
- *Applies when:* web-ui, native-app with keyboard input.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-20** — Prove perception with numbers: computed contrast for every token pair incl. dimmed states (text ≥ 4.5:1, large text ≥ 3:1, UI parts ≥ 3:1), a minimum text size, targets ≥ 24×24 CSS px everywhere and ≥ 44×44 on touch layouts (a smaller one needs a reason in design-system.md), reflow at 320 CSS px, 200 % text zoom and text spacing without loss, colour never the only carrier.
- *Why:* estimated ratios hid a failing muted-label pair, and 44 px targets were specified but built at about 26 px (LL-19).
- *Check:* a contrast script over the token table; target sizes measured in the phone project; reflow and zoom runs; estimated ratios fail Gate UX.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-21** — Write every normative statement as an observable — exact copy, accessible name, state attribute, device class, focus target, format literal, timing — never an unmeasured adjective ("intuitive", "clean", "fast"); end with a trace table requirement → UJ/SCR → matrix row.
- *Why:* measurable criteria were never turned into tests and tests came after code (LL-45, LL-29).
- *Check:* Plan & Bind finds 0 blocking "untestable design statement" spec defects; trace_check gate-ux shows every requirement with an interface effect mapped.
- *Applies when:* always.
- *Provenance:* LL-45, LL-29 (KatenatsioTipster, 2026-10)

**DSN-22** — Design the CLI: one grammar (`tool noun verb` or `tool verb`) and flag style (long kebab-case, short only for the most common); `--help` on every command with usage, examples and exit codes; human output by default and stable documented `--json`; data to stdout, progress, prompts and diagnostics to stderr; an exit-code table (0 ok, 2 usage, documented others); colour only on a TTY with `NO_COLOR` unset; wrap to terminal width; prompts only on a TTY, destructive commands need `--yes` when non-interactive; every error says what failed and what to do.
- *Why:* nobody designed a CLI's grammar, errors and exit codes, so tests had no oracle (LL-41).
- *Check:* golden outputs per command × {TTY, pipe, `NO_COLOR`, narrow width, `--json`}; subprocess tests assert stdout, stderr and exit code; Design QA reviews the golden outputs.
- *Applies when:* cli.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

**DSN-23** — Design machine-facing surfaces for their consumers: library — the smallest public surface the requirements need, names per the naming guide, typed documented errors, a runnable example per public symbol, deprecation and semver policy; http-api — resource model, one error body (code, message key, field errors, correlation id), pagination with stable order and a max page size, versioning, an example per operation and per error; data-pipeline — a contract per dataset (schema, units, explicit zones, nullability, keys, duplicate and late-data semantics, each field's meaning from a recorded real sample) plus an operator runbook (rerun, backfill, each alert → first action).
- *Why:* a field's meaning and a source's date zone were taken from a description, and the wrong reading reached stored results (LL-2).
- *Check:* examples run as consumer tests against the installed package or the running service; contract fields match recorded payloads (FAKE-2); Design QA reviews golden datasets.
- *Applies when:* library, http-api, data-pipeline.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10)

**DSN-24** — Score `design.md` against the rubric below with evidence per dimension and submit only when every dimension is ≥ 4 and every ★ dimension is 5; a score without evidence counts as 1; non-visual profiles mark D1–D6 and D8 N/A with a reason.
- *Why:* gates that accept self-assessment without evidence approved hover-only and raw-value designs (LL-52).
- *Check:* Gate UX: rubric table present, each score cites a section, computed value or blueprint; any score below the bar returns the design.
- *Applies when:* always.
- *Provenance:* LL-52 (KatenatsioTipster, 2026-10)

Scale: **1** missing or broken · **2** present, breaks a DSN/LOC rule · **3** meets every rule for the dimension · **4** meets them on every screen, class and state with no Minor finding · **5** 4 plus craft: a peer cannot name an in-scope improvement.

| Dimension | 5 looks like | Evidence (spec → rendered) |
|---|---|---|
| D1 Hierarchy & restraint | one focal point, one primary action, nothing idle | blueprints → squint test on gallery |
| D2 Typography & rhythm | scale-only type, steady vertical rhythm | token refs → measured screenshots |
| D3 Colour & contrast ★ | roles only, computed ratios pass, never colour-only | ratio table → scan report |
| D4 Grid & alignment | every edge on the grid at every class; stable across states | blueprints → gallery overlay |
| D5 State polish ★ | empty, loading, error, success as crafted as populated | 0 blank cells → every SCR × state |
| D6 Motion & signature | purposeful, tokenised, reduced variant, signature moments delight | motion table → recording |
| D7 Minimal flow | fewest steps, progressive disclosure, plain words | step counts, walkthrough → journey run |
| D8 Device fit ★ | each class designed, touch-first, gestures safe | device table → phone/tablet gallery, swipe TC |
| D9 Accessibility ★ | every DSN-18–20 check specified | names, keyboard paths → scan + keyboard TCs |
| D10 Content & formatting ★ | copy deck, label maps, a formatter per value | LOC tables → literal-oracle TCs |
| D11 Resilience & volume | max volume, idle, races, failures designed | volume rows, error catalogue → TCs |
| D12 Consistency | design-system tokens and components only | amendment log → cross-screen gallery |
| D13 Testability ★ | every statement observable | trace table → 0 untestable at Plan & Bind |

**DSN-25** — Run Design QA on the rendered product: open every image of the Tester's gallery (`absd-project/working/evidence/tester/screens/`, every SCR × state × device class × theme) or every golden output (cli, data-pipeline), compare with `design.md`, `design-system.md` and the rubric, re-score the rubric from what is visible, and write DQ-n findings (unified schema, image path as evidence; route Builder for drift, Designer for a design gap) with verdict PASS only at the DSN-24 bar and 0 Critical/Major.
- *Why:* every design-fidelity audit passed by reading code while raw enums, mixed formats, truncation and unlinked labels were visible on screen (LL-19).
- *Check:* design_review.md lists every gallery cell as reviewed; a missing cell makes the verdict BLOCKED, never PASS (GATE-1); severity: a wrong value users act on (time, money) Critical, a rule breach with user impact Major, polish Minor.
- *Applies when:* web-ui, native-app; cli and data-pipeline via golden output.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**DSN-26** — List the protected screens (SCR × state × device class × theme) whose appearance must not drift, approve each baseline image by path and content hash in `design_review.md`, and allow a baseline change only when a `design.md` change makes it intended and the Designer re-approves — never auto-updated to turn a run green.
- *Why:* a "no visual regression" requirement written every cycle was never automated (LL-53).
- *Check:* the visual-regression suite (VIS) compares against approved baselines; the Auditor finds an approval row for every baseline change (GATE-6).
- *Applies when:* web-ui, native-app; golden outputs for cli and data-pipeline.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10)
