# Content and Locale

Code **LOC**. What people read and how values look: label maps instead of raw values, one formatter per kind of value
driven by the Locale & Time Profile in `absd-project/context.md`, time-zone and calendar display, number consistency,
truncation, exact copy and wording, localisation readiness. The Designer writes the copy deck, label maps and Format
Policy (shared parts in `design-system.md` §4, cycle additions in `design.md`); the Manager checks presence at Gate UX;
the Tester takes literal oracles from them (ORACLE-1); Design QA checks the rendered result (DSN-20). Applies to every
human-facing output: screens, CLI human output, human-readable messages in API errors, notifications, exports for
people; machine outputs follow LOC-3. Visual and interaction rules are DSN (`absd/playbook/design/excellence.md`;
rubric and Design QA: `absd/playbook/design/rubric-and-qa.md`).

## Checklist

- [ ] No raw enum, id, code or server message shown; a label map per displayed enumeration (LOC-1)
- [ ] Format Policy: one named formatter per kind of value with literal examples; every displayed value names one (LOC-2)
- [ ] Machine outputs: RFC 3339 with offset, plain numbers, stable codes (LOC-3)
- [ ] 24-hour vs 12-hour decided per audience and set explicitly; 00:xx and 12:xx examples (LOC-4)
- [ ] Every time shown in a declared zone passed explicitly; never the browser or device zone silently (LOC-5)
- [ ] Labels are true: a named zone, unit, period, source or freshness shows exactly that (LOC-6)
- [ ] Today/week/month/season buckets in the display zone; boundary examples given (LOC-7)
- [ ] One number style per screen: separator, grouping, decimals, single sign, unit position (LOC-8)
- [ ] No truncation while space exists; ellipsis + full value reachable; compared values never cut (LOC-9)
- [ ] Copy deck: every string verbatim with key, context, max length, variables (LOC-10)
- [ ] One language, tone and register from the design system; page language declared (LOC-11)
- [ ] Empty states say what, why and next action; empty ≠ no results ≠ unavailable ≠ failed (LOC-12)
- [ ] Actions named verb + object; destructive confirmations state the consequence; errors say what to do (LOC-13)
- [ ] Strings externalised; plural categories; no concatenation; expansion tolerated; RTL only if in scope (LOC-14)
- [ ] Verified mechanically: formatter lint, foreign zone/locale run, literal oracles (LOC-15)

## Rules

**LOC-1** — Never show people raw values: every enumerated value (status, role, type, reason) reaches a person only through one label map in `design.md` (value → label → icon/colour → description), unknown values get a defined fallback label, and ids, internal codes, exception or provider text and `null`/`undefined`/`NaN` never render.
- *Why:* one role enumeration rendered several ways on one product, including raw identifiers (LL-19); an external service's failures surfaced as raw "Server error" (LL-11).
- *Check:* Gate UX: every displayed enumeration in analysis.md has a map; the Tester renders each value and asserts its label, and every screen asserts no rendered text matches the raw-value list or `null|undefined|NaN|Exception`; a lint flags enum values interpolated in view code.
- *Applies when:* web-ui, native-app, cli human output, human-readable messages in any profile.
- *Provenance:* LL-19, LL-11 (KatenatsioTipster, 2026-10)

**LOC-2** — Format every displayed value through one formatter per kind, declared in the Format Policy table below and derived from the `context.md` Locale & Time Profile; every displayed value in blueprints, state matrix and copy deck names its formatter, and every editable formatted value has a parser that accepts exactly what the formatter shows.
- *Why:* ad-hoc formatting put three number styles on one screen (LL-19), and a locale default turned a past-midnight time into a midday reading (LL-4).
- *Check:* Gate UX: no displayed value without a formatter name; table-driven formatter tests use the policy's literal examples as oracles (0, ±small, ≥ 1000, rounding edge, empty) plus parser round-trips.
- *Applies when:* any human-facing output with times, dates, numbers, money, percentages or durations.
- *Provenance:* LL-19, LL-4 (KatenatsioTipster, 2026-10)

| Kind | Formatter decides | Literal examples the policy must show |
|---|---|---|
| time | zone (LOC-5), clock (LOC-4), seconds or not | 00:05, 12:30, 23:59 |
| date, date-time | pattern, zone, relative words (LOC-7) | first of month, year change |
| number | decimals per measure, grouping, rounding mode | 0, 0.5, 1485.5, 1000000 |
| currency | symbol or code, position, decimals, rounding | 0, −12, 1485.5 |
| percentage | input scale (0.5 or 50), decimals | 0, 12.5, 100 |
| signed number | sign rule, minus character, zero | −12, 0, +12 |
| duration | units, largest unit, rounding | 59 s, 61 min, 25 h |
| relative time | thresholds, switch to absolute date | 30 s, 2 h, 3 days, last year |

**LOC-3** — Keep machine outputs stable: `--json`, API bodies, files meant for programs and logs use RFC 3339 timestamps with an explicit offset, plain numbers (dot decimal, no grouping, unit in the field name or contract) and the documented codes, never display labels; human formatting never leaks into them.
- *Why:* a source's zone-less local timestamps were read as UTC and every deadline shifted by hours (LL-1).
- *Check:* contract and golden-output tests assert the format per field; a schema check rejects zone-less timestamps.
- *Applies when:* cli `--json`, http-api, library return values, data-pipeline outputs.
- *Provenance:* LL-1 (KatenatsioTipster, 2026-10)

**LOC-4** — Decide the clock (24-hour or 12-hour) per audience in the Locale & Time Profile and set it explicitly in the time formatter, never inherited from a locale or platform default; the Format Policy shows 00:xx and 12:xx examples.
- *Why:* a locale default printed 00:30 as a 12-hour time that people read as midday (LL-4).
- *Check:* fixtures at 00:xx and 12:xx assert the literal strings and, for 24-hour, no day-period marker; a lint flags time formatting without an explicit hour cycle.
- *Applies when:* any time is shown.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**LOC-5** — Show every time in a declared zone: the display zone(s) from the Locale & Time Profile by default, the viewer's zone only where `design.md` says so, provider times converted at the boundary from their recorded zone; formatters receive the zone explicitly and never fall back to the browser or device zone; when viewers may be outside the display zone, the zone is labelled.
- *Why:* a clock showed the browser's zone (LL-13); provider-local times read as UTC made every deadline hours late (LL-1).
- *Check:* the foreign zone and locale end-to-end project (VAR-8) asserts literal display-zone times; formatter tests pass the zone; a lint flags zone-less date construction or formatting in view code.
- *Applies when:* any time or date is shown.
- *Provenance:* LL-13, LL-1 (KatenatsioTipster, 2026-10)

**LOC-6** — Make every label true: a label naming a zone, unit, currency, period, source, provider or freshness shows exactly that ("UTC" shows UTC; "updated 5 min ago" counts from the data's own timestamp, not the page load), and replacing an integration, unit or source sweeps every label, status card, help text and doc naming the old one.
- *Why:* a clock labelled UTC showed local time (LL-13); after an integration was replaced, a status card still named the old provider (LL-17).
- *Check:* tests assert the labelled property under a foreign browser zone and seeded timestamps; the replacing cycle's test plan lists the sweep (grep) and its result.
- *Applies when:* a label names a zone, unit, period, source, provider or freshness.
- *Provenance:* LL-13, LL-17 (KatenatsioTipster, 2026-10)

**LOC-7** — Bucket and label dates ("today", "tomorrow", "this week", month, season) in the display zone, mapping the provider's calendar and served periods explicitly; `design.md` gives the expected label at 23:59, 00:00 and 00:01 display zone, UTC midnight, provider midnight, month and season start and both DST changes; a period the source never serves is shown as unavailable or not offered, never as an empty list.
- *Why:* the source never served the current day, giving an always-empty "Today" tab and tonight's events under "Tomorrow" (LL-3); provider-dated results were read as UTC dates (LL-2).
- *Check:* time-instant tests at each boundary with a movable clock (VAR-8) assert the design's literal labels; an exploratory charter runs around midnight and month start.
- *Applies when:* dates are grouped, labelled relatively or bounded by periods.
- *Provenance:* LL-3, LL-2 (KatenatsioTipster, 2026-10)

**LOC-8** — Keep one number style per screen and across screens: one decimal separator and grouping, fixed decimals per measure, exactly one sign character (a true minus unless the design system says otherwise; "+" only where gain or loss matters), one unit and currency position, sign colour always paired with the sign; numeric columns use tabular figures and right or decimal alignment.
- *Why:* `285.0`, `1.485` and `+585,0` appeared together on one screen, so a grouping separator read as a decimal point (LL-19).
- *Check:* fixtures with ≥ 1000, negatives, zero and rounding edges assert literals; a test asserts no doubled sign; Design QA scans the gallery for mixed separators.
- *Applies when:* numbers are shown.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**LOC-9** — Never truncate while space exists: per text field declare the max length and wrap or truncate per device class; truncate only at the declared width, with an ellipsis and the full value reachable by touch, keyboard and screen reader (expand, tap, accessible name; never hover-only); never truncate values people compare or act on (money, numbers, dates, ids, codes).
- *Why:* names were cut off although the screen had free space (LL-19).
- *Check:* text-length variants per field (1, typical, max, max+1, one unbroken string) on phone and desktop: fully visible where space allows, full value reachable otherwise; Design QA reviews the gallery.
- *Applies when:* variable-length text is shown.
- *Provenance:* LL-19 (KatenatsioTipster, 2026-10)

**LOC-10** — Write every user-facing string verbatim in the `design.md` copy deck with a stable key (e.g. `SCR-3.empty.title`), context, max length and named variables: labels, button and loading labels, placeholders, help, accessible names, empty, error, confirmation, success and notification texts; no string reaches a person unless the deck or the design system's shared strings hold it.
- *Why:* where copy was exact, wrong labels were caught by string comparison; where it was not, generic or raw text leaked (LL-19, LL-11).
- *Check:* the Tester asserts exact text and accessible names from the deck; Design QA diffs rendered text against it; a lint flags user-visible literals outside the string catalogue.
- *Applies when:* any human-facing output.
- *Provenance:* LL-19, LL-11 (KatenatsioTipster, 2026-10)

**LOC-11** — Apply the design system's language, tone and register to every string: one UI language unless the profile lists more, untranslated terms only from an allowed list, one form of address, plain words over internal terms, and the document or page language set to the UI language.
- *Why:* mixed-language screens and drifting register read as unfinished, and a wrong page language breaks screen-reader pronunciation.
- *Check:* Design QA copy review against `design-system.md`; the accessibility scan's page-language rule; an allowed-terms lint over rendered text.
- *Applies when:* any human-facing output.
- *Provenance:* industry baseline

**LOC-12** — Write each empty state as what is missing, why, and the one next action, and keep four cases distinct: nothing yet; no results for this search or filter (echo it, offer to clear); not available for this period or source; failed to load (an error with retry, never empty copy).
- *Why:* an always-empty tab looked like "no events" when the source never served that day (LL-3); a status reported "no data" while the feed worked (LL-17).
- *Check:* tests reach each case and assert its exact copy and action; injected load failures never show empty copy.
- *Applies when:* any collection or query result is shown.
- *Provenance:* LL-3, LL-17 (KatenatsioTipster, 2026-10)

**LOC-13** — Name actions by verb and object ("Delete 3 entries", never "OK"); destructive confirmations state what is lost and whether it can be undone, with the safe choice focused by default; error copy says what happened and what to do next in the user's terms, without blame, codes or stack traces (a support reference only as secondary text); success copy says what happened and where to find it.
- *Why:* an external service's failures read "Server error", which told users nothing they could act on (LL-11).
- *Check:* Gate UX copy review against this rule; the Tester asserts exact copy and the confirm, cancel and dismiss paths; each external failure mode has its message test (Gate T).
- *Applies when:* human-facing output with actions or errors (cli: prompts and stderr).
- *Provenance:* LL-11 (KatenatsioTipster, 2026-10)

**LOC-14** — Keep content localisation-ready: strings in one catalogue keyed like the copy deck; whole-sentence templates with named placeholders, never concatenation; plurals through the locale's plural categories (CLDR), never "item(s)"; layouts survive about +40 % on sentences and +100 % on short labels; right-to-left mirroring, extra scripts and locale switching only when `context.md` lists such a locale (YAGNI).
- *Why:* concatenated or singular-only strings cannot be translated without code changes, and layouts sized to one language clip in the next.
- *Check:* a lint flags concatenated user strings; plural copy has examples for 0, 1, 2 and 5; one gallery pass with expanded pseudo-localised strings when a second locale is in scope.
- *Applies when:* human-facing text; expansion and right-to-left checks only when a second locale is in scope.
- *Provenance:* industry baseline

**LOC-15** — Verify formats mechanically, never by memory: formatting and label lookup each live in one module, a lint or grep fails the build on formatting, zone-less date handling or enum display outside them, one end-to-end project runs with the browser, device or process zone and locale deliberately different from the profile, and expected display strings are literals from `design.md`, never produced by the production formatter.
- *Why:* tests pinned to the audience's own zone and locale hid reliance on the browser zone (LL-13); 12-hour times reached users because nothing checked rendered formats (LL-4).
- *Check:* lint output in test_report.md; the foreign zone and locale project green (VAR-8); the Auditor flags mirrored oracles (ORACLE-1).
- *Applies when:* any human-facing time, date, number or enumeration.
- *Provenance:* LL-13, LL-4 (KatenatsioTipster, 2026-10)
