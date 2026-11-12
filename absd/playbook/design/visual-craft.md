# Visual Craft

Code **DSN** (DSN-23 to DSN-34). How a screen looks, not only how it works: a written art direction, one signature
and restraint elsewhere, a refusal list of generic looks, measurable floors for type, colour, space, depth, icons,
motion and charts, a visual lint over every rendered screen, and a scored visual review at Design QA. Applied by the
Designer (`design-system.md` §1–§2, `design.md`, `design_review.md`); the Tester runs the visual lint (DSN-33) over
the gallery (VIS-1); the Manager checks this Checklist at Gate UX and the rubric at Gate 3; the Auditor cites it at L2.
Related: DSN-3, DSN-6, DSN-15 and DSN-22 (`absd/playbook/design/excellence.md`), DSN-19 to DSN-21
(`absd/playbook/design/rubric-and-qa.md`), LOC (`absd/playbook/design/content-and-locale.md`).

Clean lint and full scores are a floor, never proof of taste: a dull screen can pass every check. The visual rubric
judges from images; numbers keep the judgement honest.

## Checklist

- [ ] Art direction in `design-system.md` §1 before any screen: subject world, use scene, surface mode per SCR, the category default considered and what replaces it (DSN-23)
- [ ] One signature element; a subtraction pass logged; grouping by space before containers (DSN-24)
- [ ] No generic look from the catalogue unless the brief asks for it, with the reason recorded (DSN-25)
- [ ] Type scale with a ratio, ≤ 2 families with roles, reading floor, tabular numerals for compared numbers (DSN-26)
- [ ] Colour strategy named; roles, not swatches; perceptual ramps; contrast on final colours; each theme designed (DSN-27)
- [ ] Spacing from the scale, rhythm per density; padding ≥ the gap it contains (DSN-28)
- [ ] One depth language and light direction; radius by hierarchy; platform surfaces styled from tokens (DSN-29)
- [ ] One icon family, size and stroke; optical alignment; real imagery or none (DSN-30)
- [ ] Motion durations and easing from the timing table; no page-load choreography on operate screens (DSN-31)
- [ ] Charts: the question first, direct labels, faint grid, a second cue beyond colour, text summary (DSN-32)
- [ ] Visual lint run over every gallery image and page; findings in `test_report.md` (DSN-33)
- [ ] Design QA scores V1–V10 from images before reading the lint; bar ≥ 4, V1 and V3 at 5 on primary screens (DSN-34)

## Rules

**DSN-23** — Write the art direction in `design-system.md` §1 before the first screen: the product's subject world
(the materials, objects and places of its domain), the use scene (who, where, what light, what device, how hurried),
a surface mode per SCR (operate — repeated work; read — long text; persuade — first visits, sign-up; showcase — the
product itself is on display), the colour strategy (DSN-27), type roles (DSN-26), a layout concept, three principles
and one signature (DSN-24). Before building, record the category default — what a generic design for this kind of
product would look like — in a "default considered → our choice" row per foundation (palette, type, layout, motion);
a choice may equal the default only with a reason from the brief. The brief's own look, a brand guide or an inherited
design system wins over a fresh direction. Operate and read screens keep the platform's standard controls and
patterns; their direction shows in type, palette, density and the signature, never in unfamiliar controls.
- *Why:* without a written direction every screen falls back to the average of what models and templates have seen;
  products look interchangeable and nobody can say why a screen is off.
- *Check:* §1 has every field and the default-considered rows; every SCR in `design.md` names its surface mode; Gate UX
  rejects an empty or generic direction ("modern, clean, intuitive").
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71 (visual-craft research of three public design rule sets, 2026-11-11)

**DSN-24** — Spend boldness in one place: one signature element per product (a type treatment, a colour field, a
data presentation, a motion moment) recorded in §1 and used where it serves the primary journey; everything else is
quiet. Before Gate UX, run a subtraction pass over each primary screen — remove each container, border, divider,
colour and decoration that carries no information — and log what went. Group by space and alignment before adding a
card, border or background; a container must say something space cannot.
- *Why:* designs read as busy or generic when every element competes; a single deliberate signature reads as
  intent.
- *Check:* §1 names one signature; `design.md` has the subtraction log per primary SCR; Design QA (V2) finds no
  container that only groups.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-25** — Refuse the generic looks in the catalogue below unless the brief asks for one; a use needs a recorded
brief reason in §1. Catalogue: identical card grids for unlike content; cards nested in cards; a giant hero metric with
a small label; eyebrow labels over every heading; fake step numbers (01/02/03) on unordered content; gradient text;
decorative translucent panels; coloured side stripes on cards; glows and neon edges; a border plus a wide soft shadow
on the same element; one radius on everything; emoji as icons; tracked-out capitals for body labels; the same
fade-and-rise entrance on every element; bounce or elastic easing; cream background + serif + terracotta accent for
anything "warm"; near-black + one neon accent for anything "technical"; purple-to-blue gradients. The kit maintainer
reviews the catalogue at every MINOR release (looks date).
- *Why:* these patterns are what generated interfaces converge on; each is fine once, and together they make a
  product look machine-made.
- *Check:* Design QA (V1, V10) and the visual lint (DSN-33: stripes, gradient text, glows) find no catalogue look
  without its §1 reason; on a primary screen an unrecorded one is Major.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-26** — Set type as a system: a scale from a ratio (operate and read surfaces ≈ 1.125–1.25 per step; persuade
and showcase ≥ 1.25), at most two families with named roles, only the weights used loaded. Reading floor on the web:
body ≥ 16 px, nothing below 12 px (11 px only inside dense controls), 45–75 characters per line for running text,
line height 1.4–1.7 for body, tighter for large headings, letter spacing only on capitals and never below the face's
default for body. Headings balance their lines, no single-word last line in a heading or short paragraph, and more
space above a heading than below it. Numbers that are compared (tables, totals, timers) use tabular numerals and
right-align in columns. Light text on dark gets slightly more weight compensation and spacing; fallbacks are
metric-matched so text never shifts or disappears while fonts load.
- *Why:* most "something is off" reactions trace to type: lines too long, sizes too close, numbers that jitter.
- *Check:* the type table in §2 lists scale, ratio, families and roles; the visual lint measures size, line length,
  line height and tracking (DSN-33); Design QA V3.
- *Applies when:* web-ui, native-app (cli: DSN-17 output style).
- *Provenance:* LL-71

**DSN-27** — Choose a colour strategy before any swatch — restrained (neutrals plus one accent), committed (one hue
carries the brand across surfaces), full (several hues with roles) or drenched (colour as the surface itself) — then
define roles, never raw swatches, in §2. Build ramps in a perceptual colour space (OKLCH, CIELAB or HCT) so steps look
even; prefer solid colours to translucent ones; check contrast on the final blended colours (DSN-15). Text on a
coloured surface takes a shade of that surface's hue, never plain grey. Light or dark default follows the use scene;
each theme is designed and checked on its own — dark is not an inversion — with every state in both.
- *Why:* palettes picked swatch by swatch drift, translucent layers fail contrast where they overlap, and inverted
  dark themes glare.
- *Check:* §1 names the strategy; §2 role table per theme with ratios; `absd/tooling/palette.py report` output in
  the Designer's evidence; Design QA V4 per theme.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-28** — Space from the scale only (4-based), with a rhythm: related items closer than unrelated ones, padding at
least the gap between the items it contains, density set per SCR from its surface mode (operate: compact; read and
persuade: generous). No single gap value should cover more than about half of all gaps on a screen — one value
everywhere flattens hierarchy.
- *Why:* uniform spacing makes everything look equally related; ad-hoc values break alignment.
- *Check:* the visual lint reports off-scale values and the gap histogram (DSN-33); Design QA V5.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-29** — Use one depth language: per elevation level either a border or a shadow (not both), one light
direction, radius by hierarchy (outer containers larger, nested radius = outer radius − padding). Style the platform
surfaces from tokens: focus ring, text selection, caret, scrollbars, link underline offset, form accent colour and
autofill — never browser or OS defaults next to a designed palette.
- *Why:* mixed shadows and borders read as several products glued together; default focus rings and selections
  break an otherwise consistent surface and are often invisible on a custom background.
- *Check:* §2 elevation and radius tables; the visual lint finds no element with both border and wide shadow; Design
  QA V6 includes a focus and selection screenshot per theme.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-30** — Use one icon family with one stroke weight and a size token per context, optically aligned with text,
each icon at ≥ 3:1 against its background and paired with a label unless universally known. Use real imagery of the
product's world or none; never stock filler or emoji in its place.
- *Why:* mixed icon sets and filler imagery are the quickest tells of an unfinished product.
- *Check:* §3 names the family and sizes; Design QA V7.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-31** — Time motion from one table: 100–150 ms for feedback (press, toggle), 150–300 ms for state changes,
300–500 ms for overlays and panels, 500–800 ms only for one entrance moment; exits ≈ 60–75 % of their entrance;
ease-out curves, no bounce or elastic. Operate screens have no page-load choreography; content is visible and usable
without the animation (and without scripts where the platform allows). Every animation has the reduced-motion variant
DSN-6 requires.
- *Why:* slow or showy motion on repeated work costs seconds per use; motion with no rule feels arbitrary.
- *Check:* §2 motion tokens fall inside the table; Design QA V8 reviews the recorded transitions or their token list.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

**DSN-32** — Style data from the question it answers: choose the chart for the comparison (trend, part of whole,
ranking, distribution), label series directly when ≤ 5 instead of a legend, keep the grid faint, marks ≥ 3:1 against
the background, colours safe for colour-vision deficiencies plus a second cue (shape, pattern, label), units on axes,
tabular numerals, no 3-D, gradients or decorative fills; on phones simplify (fewer ticks, a summary value); give
every chart a one-line text summary and a table equivalent.
- *Why:* charts styled for decoration hide the answer and exclude readers who cannot rely on colour.
- *Check:* each chart in `design.md` names its question, encoding and summary; Design QA V9; a11y scan of the table
  equivalent.
- *Applies when:* any screen or document with charts.
- *Provenance:* LL-71

**DSN-33** — Lint every rendered screen: the Tester runs a visual lint over each gallery page and state (VIS-1) at
Verify and writes `evidence/tester/visual-lint.json` — one entry per screen with `screen`, `state`, `device`, `theme`
and `findings[]`, each finding `{rule, selector, measured, limit, severity}`. It reports at least: values off the
token scale (colour, space, radius, type size); text below the size floor; line length outside 45–75 characters on
running text; line height and tracking outside DSN-26; rendered contrast below DSN-15 on the final colours; text that
overflows or is clipped; content hidden at rest that needs hover; heading levels skipped; the gap histogram (DSN-28);
broken images; side stripes, gradient text and glows (DSN-25). The implementation is per product (a test-harness
script in the Tester's paths); the kit fixes the report shape. A Major-level lint finding on a primary screen is a TF.
- *Why:* craft rules that nobody measures decay; most visual defects are measurable on the rendered page even though
  taste is not.
- *Check:* the lint JSON exists for every gallery cell at the product SHA; its findings are triaged in
  `test_report.md`; a negative control (a planted off-token colour) turns it RED (GATE-8).
- *Applies when:* web-ui (native-app: the checks the platform's tooling can measure, the rest by Design QA).
- *Provenance:* LL-71

**DSN-34** — At Design QA score the visual rubric below from the gallery images (and recordings for motion), each
dimension 1, 3 or 5 like DSN-19 with an image path or measurement as evidence. Write the scores before opening the
visual lint JSON, so the measurements cannot anchor the judgement; then reconcile — a lint finding the score missed
lowers that score with a note. A fresh reviewer is preferred: the Designer who designed the screen scores it only
when no other Designer invocation is available, and says so. Bar: every dimension ≥ 4 on average across screens; V1 and
V3 at 5 on primary screens. V1 or V3 ≤ 2 on a primary screen is Major; an unrecorded generic look (DSN-25) is Minor,
Major on a primary screen.
- *Why:* a rubric scored after reading the numbers repeats the numbers; scoring blind first keeps the visual
  judgement independent.
- *Check:* `design_review.md` holds the V table with evidence per score, written in a commit before the lint JSON is
  cited; the reconciliation notes follow.
- *Applies when:* web-ui, native-app.
- *Provenance:* LL-71

| V | Dimension (★ = primary-screen bar 5) | 5 means | Evidence |
|---|---|---|---|
| V1 ★ | Direction and specificity | with the product name masked, a reader can tell what the product is for and that it is this one, not a template | images, §1 |
| V2 | Composition and hierarchy | one focal point per screen; the eye path matches the primary action; nothing only decorates | images, squint test |
| V3 ★ | Typography | scale, measure, rhythm and numerals per DSN-26; headings break well | images, lint sizes |
| V4 | Colour | strategy visible; roles consistent; both themes designed | images per theme, ratios |
| V5 | Space and density | rhythm per DSN-28; density fits the surface mode | gap histogram |
| V6 | Depth, shape and surfaces | one depth language; styled focus and selection | focus/selection images |
| V7 | Icons and imagery | one family, aligned, labelled; real imagery or none | images |
| V8 | Motion | timings and easing per DSN-31; reduced motion works | token list, recordings |
| V9 | Data visualisation | DSN-32 met on every chart | images, table equivalents |
| V10 | Finish | lint clean or triaged; long content, empty and max-volume states hold | lint JSON, volume images |
