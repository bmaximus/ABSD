# Design system

> Living, owned by the Designer, NEVER archived. Created in the Foundation cycle, amended at Gate UX (every `design.md`
> references it instead of re-declaring tokens). Rules: `absd/playbook/design/excellence.md` (DSN) and
> `absd/playbook/design/content-and-locale.md` (LOC). Keep only the sections for the product's interface profiles.

## 1. Character
- Personality in three words: <e.g. calm, precise, warm>
- Signature moments (where delight is worth the effort): <…>
- What the product never does: <e.g. modal interruptions for non-critical news; colour-only meaning>

## 2. Visual foundations (web-ui, native-app)
| Token | Value | Use | Contrast checked against |
|---|---|---|---|
| color.bg / surface / raised | | | |
| color.text.primary / secondary / muted | | | ≥ 4.5:1 (body), ≥ 3:1 (large) |
| color.accent / accent.on | | primary action | |
| color.success / warning / danger / info | | status — always paired with icon or text | |
| space.xs … xl | | 4- or 8-based scale | |
| radius.sm / md / lg | | | |
| elevation.1 … 3 | | | |
| type.display / title / body / caption / mono | size / weight / line height | | |
| motion.fast / normal / slow + easing | ~150 / 250 / 400 ms | state changes; reduced-motion fallback | |
| breakpoints | phone / tablet / desktop | | |
| touch target min | 44 × 44 px (never below 24 × 24) | | |

## 3. Components
| Component | Variants | States (default, hover, focus, active, disabled, loading, error, empty, success, read-only) | Accessible name rule | Notes |
|---|---|---|---|---|

## 4. Content and formatting (all profiles)
- Language(s) and tone: <…>
- Times: <24h/12h>, zone shown as <…>; dates <…>; numbers and currency <…> — one formatter per kind, never raw values.
- Enumerations are always shown through a label map (never raw enum names).
- Empty, loading, error and success copy patterns: <…>

## 5. Command-line output style (cli)
- Grammar: `<tool> <noun> <verb> [flags]` · flags: long `--kebab-case`, short only for the most common.
- Output: human by default; `--json` stable machine output; data → stdout, diagnostics → stderr; exit-code table.
- Colour only when stdout is a TTY and `NO_COLOR` is unset; never colour-only meaning; width-aware wrapping.

## 6. Public API style (library)
- Naming, error types, async conventions, versioning/deprecation policy (semver), examples format.

## 7. Data contract style (data-pipeline, http-api)
- Field naming, units, time zones (always explicit), nullability, keys, pagination, error body, versioning.

## Change log
| Date | Cycle | Change | Reason |
|---|---|---|---|
