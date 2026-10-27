<!-- ABSD skeleton: copy to absd-project/working/design.md; keep every heading (tools read them).
Owner: designer. -->

# Design — C### <slug>
Cycle: C### | Mode: F | S | D | C | B | Status: IN-PROGRESS | COMPLETE | BLOCKED | Date: YYYY-MM-DD
Kind: full | delta · Gate UX round <n>/3 · Inputs: analysis.md @<sha> (G1) · catalogue.md @<sha> · design-system.md @<sha> · context.md @<sha> · EXTERNAL-FACTS.md @<sha> · brd Decisions D-1…D-n
Profiles: <context.md §1> · Device classes: <…> · phone waived (web-ui, native-app): no | D-n · Themes: <design-system.md> · Display zone, clock, language: <context.md §5>
Recorded samples used (Tester Facts mode): <EXT ids · recording paths> | none
Progress: [ ] 0 [ ] 1–3 [ ] 4–6 [ ] 7–10 [ ] 11–13 [ ] 14–17 [ ] 18–21 [ ] contrast [ ] gate-ux [ ] commit

## 0. Inputs honoured and open items
### 0.1 Decisions and inputs honoured
| Source (D-n · requirement · INH-n · EXT failure mode · NF · invariant) | Design consequence | Sections |
|---|---|---|
### 0.2 Upstream issues
| # | Source (quote + path) | Problem: missing / contradiction / untestable | Owner: Analyst / user | Blocking |
|---|---|---|---|---|
### 0.3 Routed items answered (delta)
| Item (C###/DQ-n · spec defect · architecture §0.2 · GUX note · CR-n) | Resolution | Sections |
|---|---|---|

## 1. UX goals
| Role | Goal (role value check) | Observable measure (steps, fields, time to done) | Requirements |
|---|---|---|---|

## 2. Principles applied
Character (design-system §1) · minimal-effort decisions · progressive disclosure · deliberately left out (YAGNI)

## 3. Journeys
### UJ-n — <goal> · Status: new | changed | removed · Roles · Requirements · Device classes · Steps <n> · Fields <n>
| # | Screen / command / call | Action on (accessible name · flag · symbol) | System response | After: screen + focused element | Confirmation (copy key) |
|---|---|---|---|---|---|
- Happy path = the table · Error recovery: <failure mode → message key → recovery step, input kept?>
- Edge: empty · max volume · permission lost mid-journey · <…>
- Interruptions (web-ui, native-app): background refresh · session expiry · back / refresh · second tab · network loss · re-entry → outcome
- Keyboard path: <Tab sequence, shortcuts> · Cognitive walkthrough: <result>

## 4. Screen inventory
| SCR | Name | Primary action | Roles: shown / hidden / disabled + reason | Entry (route name, deep link, back target) | Requirements | Status |
|---|---|---|---|---|---|---|

## 5. Layout blueprints (per SCR, per device class, smallest first)
### SCR-n — <name>
<ASCII grid per class: phone portrait, phone landscape, tablet, desktop> · regions and grid columns · focal point ·
scroll containers (axis, overscroll contained, initial position) · fixed bars + safe areas · on-screen keyboard (focused
field and primary action visible, keyboard type) · reserved slots so states never shift layout

## 6. Component–state matrix (0 blank cells; "N/A — <reason>")
| SCR | Element | Accessible name | Role / pattern | Default | Hover | Focus | Active | Disabled + visible reason | Loading | Error | Empty | Success | Read-only | Touch equivalent | State attribute |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
### 6.1 Data-view states
| SCR · view | Loading | Empty (LOC-12 case) | Populated | Partial | Validation error | Failure per mode (message key) | Permission-denied | Offline / slow |
|---|---|---|---|---|---|---|---|---|
### 6.2 Role × gated control and data
| SCR · control or field | Principal / entitlement state | Shown · hidden · disabled + reason key | Withheld by the server | Act-as marker |
|---|---|---|---|---|

## 7. Interaction rules
Per dialog: name · initial focus · focus trapped · Escape closes · focus restored · dirty-dismiss guard (close, Escape,
backdrop, back) · destructive confirmations (consequence copy, safe choice focused) · repeat submits ignored ·
optimistic UI only when reversible (rollback + conflict copy) · state transitions (trigger → state)

## 8. Devices and input
| UJ | Phone portrait | Phone landscape | Tablet | Desktop | Input modes | Waived (D-n) |
|---|---|---|---|---|---|---|

| Hover / tooltip / title | Touch equivalent | Keyboard equivalent |
|---|---|---|

| Scroll container or overlay | Pull-to-refresh · edge / back swipe · overscroll → outcome |
|---|---|

Beyond automation (real-device list): <…>

## 9. Volume and default position
| SCR · list / output / dataset | Collection (context.md §6) | 0 | 1 | One page | Max, real order | Search · filter · group · paging · count | Initial selection, focus, scroll (first listed vs earliest) | Budget / paging requirement |
|---|---|---|---|---|---|---|---|---|

## 10. Resilience
| SCR | At rest: none / polling (interval, scope, paused when hidden) | Survives refresh and timers (dialog, typed input, focus, scroll) | Latest input wins | Session expiry mid-input |
|---|---|---|---|---|

## 11. Content and formatting
### 11.1 Copy deck
| Key | Context (SCR · command · notification) | Text, verbatim | Max length | Variables | Plural forms (0, 1, 2, 5) |
|---|---|---|---|---|---|
### 11.2 Label maps
| Enumeration | Value | Label | Icon / colour role | Description | Unknown value → |
|---|---|---|---|---|---|
### 11.3 Formatters
| Displayed value (SCR · element · output field) | Kind | Formatter (design-system §4 or new) | Literal examples |
|---|---|---|---|
### 11.4 Time buckets and labels
| Bucket / label | 23:59 · 00:00 · 00:01 display zone | UTC midnight | Provider midnight | Month / season start | DST changes | Period never served → |
|---|---|---|---|---|---|---|
### 11.5 Truncation
| Field | Max length | Phone | Desktop | Full value reachable by |
|---|---|---|---|---|
### 11.6 Error catalogue (message keys)
| Message key | Failure mode / error class (source) | Copy: what happened + what to do | Placement | Recovery control | Input kept | Persists / transient |
|---|---|---|---|---|---|---|
### 11.7 Label truthfulness
| Label naming a zone, unit, period, source or freshness | Must show | Measured from |
|---|---|---|

## 12. Accessibility (WCAG 2.2 AA)
Page language · named landmarks · one polite status region per screen (errors assertive) · focus visible, unobscured ·
reflow 320 CSS px · zoom 200 % · text spacing · reduced motion

| Token pair · state · theme | Computed ratio | Required | Evidence path |
|---|---|---|---|

| Element | Target size (CSS px) | Touch ≥ 44 × 44 | Reason if smaller |
|---|---|---|---|

## 13. Motion
| Trigger | Element | Property | Duration token | Easing token | Purpose | Reduced-motion variant |
|---|---|---|---|---|---|---|
Signature moments (≤ 3): <…>

## 14. cli — public surface (the Architect adopts these names verbatim; DSN-17)
| Command | Synopsis | Flags (long · short · default) | stdin | stdout (human) | `--json` schema | stderr | Exit codes | TTY · pipe · NO_COLOR · narrow | Requirements |
|---|---|---|---|---|---|---|---|---|---|
Help text per command, verbatim · exit-code table (0 ok · 2 usage · …) · errors: what failed + what to do · prompts only
on a TTY, destructive needs `--yes` otherwise · golden outputs: command × {TTY, pipe, NO_COLOR, narrow, --json}

## 15. http-api — public surface by name (routes and operation keys: the Architect, architecture §5.0; DSN-18)
| Resource | Field | Type, unit, zone | Required · nullable | Meaning (requirement · recorded sample · EXT id) |
|---|---|---|---|---|

| Error code | Meaning | Field errors | Message key (§11.6) | Retry? |
|---|---|---|---|---|

| Example name | Resource · action (create · read · list · change · delete · other) | Request (fields, values) | Response (outcome class, fields, values) or error code | Requirements |
|---|---|---|---|---|

Error body (code, message key, field errors, correlation id) · pagination (stable order, max page size) · versioning ·
one named example per resource action and per error code

## 16. library — public surface (DSN-18)
| Public symbol | Kind | Contract in words (inputs, result, side effect) | Error types | Runnable example (name) | Requirements |
|---|---|---|---|---|---|
Smallest public surface · names per the naming guide (design-system §6) · typed, documented errors · deprecation and
semver policy

## 17. data-pipeline
| Dataset | Field | Type | Unit | Zone | Nullable | Key | Meaning (recorded sample · EXT id) |
|---|---|---|---|---|---|---|---|
Duplicate and late-data semantics · expected datasets: the analysis.md example tables (never designed here) · runbook:
rerun · backfill · alert → first action

## 18. Protected screens and golden outputs (human-facing only: screens, cli human output, reports, rendered documents)
| SCR / command / output | State / variant | Device class | Theme | Why protected | Dynamic regions to mask |
|---|---|---|---|---|---|

## 19. Design-system amendments (applied in this run)
| Token / component / pattern | Change | Reason (requirement · DSN rule) | design-system.md Change log row |
|---|---|---|---|

## 20. Rubric (DSN-19) — submit only when every scored dimension ≥ 4 and every scored ★ = 5
One column per declared profile; what each dimension means per profile, its evidence and its N/A cells: the DSN-19
table in `absd/playbook/design/rubric-and-qa.md` (N/A only where that table says N/A).

| Dimension | <profile>: score — evidence (section · computed value · blueprint · golden) | <profile>: score — evidence |
|---|---|---|
| D1 Hierarchy | | |
| D2 Type, rhythm & grid | | |
| D3 Colour ★ | | |
| D4 States ★ | | |
| D5 Motion | | |
| D6 Flow | | |
| D7 Devices ★ | | |
| D8 Accessibility ★ | | |
| D9 Content ★ | | |
| D10 Resilience | | |
| D11 Consistency | | |
| D12 Testability ★ | | |

## 21. Open UX questions and assumptions
| UXQ-n / UXA-n | Question or assumption | Recommended default (designed as) | Touch impact | A11y impact | Testability impact | Blocking | Answer (D-n) |
|---|---|---|---|---|---|---|---|

## 22. Traceability
| Requirement / AC | Sections | UJ | SCR | Matrix rows · message keys · commands · surface names | Status |
|---|---|---|---|---|---|
