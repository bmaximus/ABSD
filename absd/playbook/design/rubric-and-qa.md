# Design Rubric and QA

Code **DSN** (DSN-17 to DSN-21): command-line and machine-surface design, the public names the Architect adopts, the
design rubric per interface profile, Design QA on the rendered product and protected baselines. Applied by the
Designer (`design.md`, `design_review.md`); the Manager checks the rubric at Gate UX; the Architect binds the named
surface in `architecture.md` §5.0; the Tester binds examples, golden outputs and baselines at Plan & Bind; the Auditor
cites it at L2. Screens, states, devices and accessibility (DSN-1 to DSN-16): `absd/playbook/design/excellence.md`;
LOC: `absd/playbook/design/content-and-locale.md`; A11Y, VIS: `absd/playbook/testing/nonfunctional.md`.

## Checklist

- [ ] cli: grammar, help, `--json`, stdout/stderr, exit codes, `NO_COLOR`/TTY/width (DSN-17)
- [ ] library / http-api / data-pipeline: surface, errors, examples, contracts, runbook (DSN-18)
- [ ] cli, http-api, library: the public surface named in `design.md`; adopted verbatim, never re-chosen (DSN-18)
- [ ] Data contracts take field meaning from a recorded real sample (Tester Facts mode), never a description (DSN-18)
- [ ] Rubric per declared profile with evidence: every scored dimension ≥ 4, every ★ dimension 5 (DSN-19)
- [ ] N/A only where the profile's rubric column says N/A (DSN-19)
- [ ] QA: every gallery image or human-facing golden output at the product SHA reviewed; DQ findings; verdict (DSN-20)
- [ ] QA: baselines of protected screens approved by path + hash (DSN-21)

## Rules

**DSN-17** — Design the CLI: one grammar (`tool noun verb` or `tool verb`) and flag style (long kebab-case, short only for the commonest); `--help` per command with usage, examples and exit codes; human output by default and a stable documented `--json`; data to stdout, progress, prompts and diagnostics to stderr; an exit-code table (0 ok, 2 usage, others documented); colour only on a TTY with `NO_COLOR` unset; wrap to terminal width; prompts only on a TTY, destructive commands need `--yes` otherwise; every error says what failed and what to do.
- *Why:* nobody designed a CLI's grammar, errors or exit codes, so tests had no oracle (LL-41).
- *Check:* golden output per command × {TTY, pipe, `NO_COLOR`, narrow, `--json`}; subprocess tests assert stdout, stderr and exit code.
- *Applies when:* cli.
- *Provenance:* LL-41 (ABSD v2 design review, 2026-10)

**DSN-18** — Design machine surfaces for consumers: library — smallest public surface, public symbols and error types named per the naming guide, typed documented errors, a runnable example per public symbol, deprecation + semver; http-api — resource model, resources and fields by name, one error body (code, message key, field errors, correlation id), stable-order pagination with a max page size, versioning, named example requests and responses per resource action and per error; data-pipeline — a contract per dataset (schema, units, explicit zones, nullability, keys, duplicate and late-data semantics, field meaning from a recorded real sample the Tester's Facts mode produced, EXT-2) and a runbook (rerun, backfill, alert → first action). For cli (commands and flags, DSN-17), http-api and library these names are the public surface: the Architect adopts them verbatim and binds them to routes, operation keys or handlers in `architecture.md` §5.0, the Tester binds the examples (E2E-4); the Designer never chooses internal structure (routes, modules, classes).
- *Why:* a field's meaning and a source's date zone were taken from a description; stored results were wrong (LL-2). Examples were demanded "per operation" before any operation existed, and the Designer was forbidden to name what it had to specify (LL-55, LL-56).
- *Check:* every named command, flag, resource, field, public symbol and error type appears verbatim in `architecture.md` §5.0 with its binding; examples run as consumer tests on the installed package or running service; contract fields match recorded payloads (FAKE-2).
- *Applies when:* library, http-api, data-pipeline; the naming clause also cli.
- *Provenance:* LL-2 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

**DSN-19** — Score `design.md` against the rubric with evidence per dimension, once per declared profile in its own column; submit only when every scored dimension is ≥ 4 and every ★ dimension 5; a score without evidence counts as 1; a dimension is N/A only where its profile column says N/A.
- *Why:* a gate taking assessment without evidence approved a hover-only design (LL-52); visual definitions made a library or a pipeline score colour ratios and screen galleries it does not have, so no honest score could pass (LL-56).
- *Check:* Gate UX: one rubric per declared profile; each score cites a section, computed value, blueprint or golden output; any score below the bar returns the design.
- *Applies when:* always.
- *Provenance:* LL-52 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

Scale: 1 missing or broken · 2 breaks a DSN/LOC rule · 3 meets every rule of the dimension · 4 meets them on every
screen, class and state with no Minor finding · 5 is 4 plus craft: a peer cannot name an in-scope improvement.
Evidence is written spec → rendered; "same" repeats the web-ui, native-app cell.

| Dimension (5 looks like) | web-ui, native-app | cli | http-api, library, data-pipeline |
|---|---|---|---|
| D1 Hierarchy (one focal point and primary action) | blueprints → squint test | result first → golden output | N/A |
| D2 Type, rhythm & grid (scale only, aligned) | tokens, blueprints → overlay | output style guide (columns, wrapping) → narrow golden | N/A |
| D3 Colour ★ (roles only, never colour alone) | computed ratio table → scan | TTY only, `NO_COLOR` honoured (DSN-17) → golden per TTY, pipe, `NO_COLOR` | N/A |
| D4 States ★ (empty, loading, error as crafted as populated) | 0 blank cells → SCR × state gallery | every error, empty and late outcome designed → golden per outcome | every error, empty and late outcome designed → example per outcome |
| D5 Motion (purposeful; signature moments delight) | motion table → recording | progress on a TTY only → golden, or N/A | N/A |
| D6 Flow (fewest steps, plain words) | step counts → journey run | fewest flags for the common case → golden | fewest calls for the common case → consumer example |
| D7 Devices ★ (every class designed, touch-first) | device table → phone/tablet gallery | runtime classes (OS, shell, width) → golden per class | N/A |
| D8 Accessibility ★ | DSN-14, DSN-15: names, keyboard paths → scan, keyboard TCs | typed errors (stderr, exit codes) + A11Y-4 → subprocess TCs | typed errors (codes, error types, error body) → contract TCs |
| D9 Content ★ (copy deck, label maps, formatters) | LOC tables → literal oracles | same | names per naming guide, machine formats (LOC-3) → contract TCs |
| D10 Resilience (volume, idle, races, failures) | volume and error rows → TCs | same | same |
| D11 Consistency (one system) | amendment log → cross-screen gallery | output style guide → goldens side by side | naming and contract style → public-surface snapshot |
| D12 Testability ★ (every statement observable) | trace table → 0 untestable | same | same |

**DSN-20** — Run Design QA on the rendered product at one product SHA (the last commit outside `absd-project/`, `absd/RULES.md` §6): open every image of the Tester's gallery (`absd-project/working/evidence/tester/screens/`, SCR × state × device class × theme) or human-facing golden output (cli output, reports, rendered documents), compare with `design.md`, `design-system.md` and the rubric, re-score from what is visible, write DQ-n findings (unified schema, image path as evidence; drift → Builder, design gap → Designer), and pass only at the DSN-19 bar with 0 Critical/Major. Design QA runs in parallel with the audit and commits only `design_review.md` and `evidence/designer/`; the review stays valid while `git diff --quiet <product SHA> HEAD -- . ':!absd-project'` holds, so a pipeline commit is never a reason to restart. Golden datasets for machines are the Analyst's example tables (ORACLE-4), never Designer-approved.
- *Why:* fidelity audits passed by reading code while raw enums, mixed formats and truncation were on screen (LL-19); a gallery demanded "at HEAD" was stale after the next hand-off commit, so Design QA could never finish beside the audit (LL-55).
- *Check:* `design_review.md` names the product SHA, marks every gallery cell reviewed and states `Verdict: PASS | FAIL | BLOCKED | N/A` on a line outside any table (trace_check gate3 accepts PASS or N/A); a missing cell makes the verdict BLOCKED (GATE-1); a wrong value users act on is Critical, a rule breach with user impact Major, polish Minor.
- *Applies when:* web-ui, native-app; cli and other human-facing outputs via golden output; Mode D when the fix changes a visual or output surface, always for a UX gap.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10); LL-55, LL-56 (ABSD v2 kit review, 2026-10)

**DSN-21** — List the protected screens (SCR × state × device class × theme), approve each baseline by path and content hash in `design_review.md`, and change a baseline only when a `design.md` change intends it and the Designer re-approves, never auto-updated to turn a run green; regenerating a baseline without a Designer row is a user-approved Gate T amendment.
- *Why:* a "no visual regression" requirement written every cycle was never automated (LL-53).
- *Check:* the visual suite (VIS) compares against approved baselines; every baseline change has a Designer approval row or a user-approved amendment (Auditor; GATE-6).
- *Applies when:* web-ui, native-app; golden output for cli and other human-facing outputs.
- *Provenance:* LL-53 (KatenatsioTipster, 2026-10); LL-57 (ABSD v2 kit review, 2026-10)
