# Proposal: owner's design rules for UI work (verbatim, 2026-11-16)

Source: the kit owner, from a design conversation; to be included in ABSD and tried on StoickGate.

---

# Design rules — UI & front-end work

Apply to every UI task: pages, components, styling, dashboards, emails, mockups.

## Standard
- Target: work a senior product designer at Linear, Stripe or Apple would ship. "Clean and functional" is the floor, not the goal.
- Every visual choice needs a reason tied to this product's users, content and tone. If a choice could appear unchanged on any AI-generated site, replace it.
- Quality comes from typography, spacing, hierarchy and finished states first. Decoration comes last, and only if it serves the concept.

## Workflow — IMPORTANT, follow in order
1. **Read `DESIGN.md`** (repo root). If it exists, follow it exactly. To deviate, say why and update it.
2. **No DESIGN.md → design before code.** In ONE message propose 2–3 clearly different directions, each with: name, mood in 3 words, 2–3 real references (products, print, signage, architecture — never "modern SaaS"), type pairing, palette (hex), one signature detail. Recommend one, then stop and wait for my pick. This is the only stop; don't ask other design questions. (Small tweak to an existing UI → infer its current system and stay consistent instead.)
3. **Write DESIGN.md** for the chosen direction: concept, references, tokens (type scale, colors, spacing, radius, shadows, motion), component rules, do/don't. Implement tokens once (CSS variables / Tailwind theme / theme object). Components use tokens only — no hard-coded hex, px or one-off values.
4. **Build with real content**: realistic copy and data, every state (see Components).
5. **Look at it.** Run the app and screenshot at 390px and 1440px (plus dark mode if it exists). Use a browser/Playwright MCP if available, otherwise:
   `npx playwright screenshot --viewport-size "390, 844" --full-page <url> .shots/mobile.png`
   (`--viewport-size "1440, 900"` for desktop, `--color-scheme dark` for dark; first run `npx playwright install chromium`; keep `.shots/` gitignored). Open the PNGs with the Read tool and inspect them. Never call UI done without having seen it.
6. **Critique, fix, repeat.** As a demanding design director, list the 5 weakest things in the screenshots, fix them, re-shoot. At least 2 rounds for new screens. End with a short list of what changed.
7. **References I give** (images/URLs): extract their principles (type, spacing rhythm, color ratios, density) into DESIGN.md. Match the craft, not the content; never copy a brand.

## Direction
- One clear concept per product, executed with precision (e.g. "Swiss transit signage", "quiet editorial", "precision instrument", "warm paper notebook", "broadcast sports graphics"). Half-committed styles look generic.
- Derive it from the domain and audience: a bank, a kids' app and a music tool must not look alike.
- Marketing pages may be expressive. Product UI (apps, dashboards, admin, forms) must be calm, consistent and appropriately dense; personality there comes from type, color restraint and detail, not effects.
- Don't converge: never reuse the fonts, palette or layout of the last project by default.

## Typography — the biggest lever
- Max 2 families (display + text; add a mono only for code/data). Max 3 weights in use.
- Choose fonts for the concept. Overused AI defaults — avoid unless you state a reason: Inter, Roboto, Open Sans, Lato, Poppins, Montserrat, Space Grotesk, Plus Jakarta Sans, DM Sans, Outfit, Sora, Playfair Display. (A neutral grotesk is fine for dense product UI, but tuned: tracking, OpenType features, weights.)
- Starting ideas, not a whitelist: technical — Geist, IBM Plex Sans, JetBrains Mono; editorial — Fraunces, Newsreader, Instrument Serif + Instrument Sans; expressive — Bricolage Grotesque, Archivo; literary — EB Garamond, Literata.
- **Greek (or any non-Latin) text: the font MUST include those glyphs** — check the Google Fonts `greek` subset.
  - Has Greek: Commissioner, Manrope, IBM Plex Sans, Fira Sans, Source Sans 3, Source Serif 4, Literata, Piazzolla, Geologica, Brygada 1918, GFS Didot, EB Garamond, Alegreya Sans, Inter Tight, Noto Sans/Serif, JetBrains Mono.
  - No Greek: Geist, Instrument Sans/Serif, Fraunces, Newsreader, Bricolage Grotesque, Archivo, Figtree, Schibsted Grotesk, IBM Plex Serif.
- Modular scale (ratio 1.2–1.333), 6–8 steps, as tokens; fluid display sizes with `clamp()`.
- Body ≥16px (14–15px only in dense product UI); line-height 1.5–1.65; line length 55–75ch.
- Headings: line-height 1.05–1.2, tighter tracking as size grows (−0.01 to −0.03em), `text-wrap: balance`; paragraphs `text-wrap: pretty`.
- Hierarchy through size + weight + color (text / text-muted / text-subtle tokens), not size alone. Labels quieter than values.
- `font-variant-numeric: tabular-nums` for tables, prices, times, stats.
- Sentence case everywhere. Uppercase only for tiny labels, +0.04–0.08em tracking, rarely.
- Self-host or preload fonts, `font-display: swap`, subset; no layout shift.

## Color
- Start with neutrals: a 10–12-step gray ramp tinted toward the brand hue. No flat #808080 grays; no pure #000 on #fff for large areas.
- One accent, reserved for primary actions, focus and key states (~5–10% of the screen). A second accent needs a reason.
- Semantic colors (success/warning/danger/info), muted and consistent, each with bg/border/text variants.
- Build ramps in OKLCH. Expose semantic tokens (`--bg`, `--surface`, `--surface-raised`, `--border`, `--text`, `--text-muted`, `--accent`, `--on-accent`, …); components never use raw palette values.
- Contrast: body ≥4.5:1, large text and UI boundaries ≥3:1 — compute it, don't eyeball. No gray text on colored backgrounds.
- Dark mode is designed, not inverted: tinted near-black bases, elevation = lighter surface, desaturated accents, off-white text.

## Space & layout
- Spacing only from the scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128.
- Proximity shows grouping: space inside a group < space between groups. This is where most messy UIs fail.
- Align everything to a grid and shared edges; consistent max-widths. Left-align text; center only short, isolated statements.
- Marketing: generous whitespace, varied section rhythm, scale contrast (very big vs small), asymmetry, full-bleed moments. Not every section is heading + subtitle + card grid.
- Tools: purposeful density. Dashboards and tables shouldn't feel airy and empty.

## Shape & depth
- Pick one shape personality (sharp 0–4px / soft 6–10px / round 12–16px) and apply it from a radius scale. Nested radius: inner = outer − padding.
- Prefer hairline borders (1px, low contrast) and subtle surface steps over heavy shadows. Shadows: soft, layered, low-opacity, tinted — never default `shadow-lg` everywhere.
- Not everything is a card. Group with spacing, dividers and type. Never nest cards.

## Motion
- Motion explains change (enter, exit, state, reorder). 120–200ms for feedback, 200–350ms for larger transitions; ease-out in, ease-in out; no bounce unless the concept is playful.
- Animate only transform and opacity. Respect `prefers-reduced-motion`.
- No fade-up on every section; at most one orchestrated entrance per page.

## Icons & imagery
- One icon set (Lucide, Phosphor or Tabler), one stroke width, sizes from the scale, optically aligned with text. Never emoji as UI icons.
- Purposeful imagery: real product shots, photography with one consistent treatment, or custom illustration. No 3D blobs, abstract orbs or generic stock. Placeholders must look intentional.

## Components & states — "done" means all of these
- Interactive elements: default, hover, active, `:focus-visible` (custom, clearly visible ring), disabled, loading.
- Data views: loading (skeleton matching the final layout), empty (what it is + next action), error (what happened + how to fix), extremes (1 item vs 1,000; very long names; missing values).
- Forms: visible labels (never placeholder-as-label), hints, validation on blur, errors beside the field in plain language, correct `type`/`autocomplete`/`inputmode`.
- One primary button per view; secondary/tertiary clearly lower. Destructive = danger color + confirmation.
- Touch targets ≥44×44px; consistent control heights (e.g. 32/36/40/44).
- Tables: right-align numbers, tabular figures, quiet borders, row hover, sticky header on long lists.
- Never ship a component library's default theme (shadcn, MUI, Bootstrap, MudBlazor, Ant): re-theme it from the tokens until it no longer looks like the library.

## Responsive & accessible
- Mobile-first; check 390, 768, 1024, 1440. No horizontal scroll, overlap or clipped text. Mobile layouts are recomposed, not just stacked and shrunk.
- Semantic HTML first (`button`, `a`, `nav`, `main`, `label`, `table`); ARIA only where semantics can't do it. Full keyboard support, logical focus order, alt text, `lang` set.

## Copy & content
- Write specific, real copy for this product. Banned filler: unlock, unleash, elevate, seamless, revolutionize, supercharge, empower, "all-in-one", "built for the future", lorem ipsum.
- Buttons say what happens: "Book ride", "Save changes" — not "Submit", "Click here", or "Get started" everywhere.
- Realistic data: varied real-looking names and lengths, plausible numbers, local date/currency formats. No "John Doe", "$1,234", "Item 1".

## Banned AI tells — never, unless DESIGN.md explicitly chooses one
- Purple/indigo/violet → blue/pink gradients; gradient text; animated gradient borders; neon glows; glassmorphism by default.
- The template stack: centered hero + subtitle + 2 buttons → logo strip → 3 equal icon cards → stats row → testimonials → 3-tier pricing → FAQ.
- Uppercase tracked "eyebrow" labels above every heading; "01 / 02 / 03" section numbers; "✨ New" pills; emoji bullets.
- Floating blurred orbs/blobs; dot-grid, noise or grain overlays as filler; shimmer buttons.
- Icon-in-a-rounded-square above every card title; colored left-border cards; `rounded-2xl shadow-lg` on everything.
- Vanity stats ("10k+ users", "99.9% uptime") and invented testimonials.
- Raw Tailwind palette (indigo-500, slate/gray-*) used as the design.
- Cream background + serif headline + terracotta/olive accent as a default — swapping one cliché for another is still slop.

## Before saying "done" — check against the screenshots
- [ ] Squint test: the most important thing reads first; exactly one primary action.
- [ ] Could this pass for a generic AI template? If yes, strengthen the signature detail.
- [ ] Every value comes from a token; nothing off the spacing scale; edges align.
- [ ] Headings wrap well (no orphans); line lengths comfortable.
- [ ] Contrast passes; focus visible; keyboard works.
- [ ] All states exist; short and long content both hold.
- [ ] Mobile looks designed, not squeezed.
- [ ] Nothing from the banned list.

---

## Outcome (ABSD 2.7.0, 2026-11-16)

Already in the kit (2.6.0, DSN-22 to DSN-34 and DSN-1 to DSN-16, LOC): one concept, generic-look refusal, type scale
and reading measures, OKLCH ramps and semantic roles, designed dark theme, space scale and proximity, one depth and
radius language, motion timing and reduced motion, one icon family, every state, touch targets 44 px (DSN-15), copy
deck, rendered-screen review (Design QA, visual lint). Kept the kit's own numbers where they differ slightly (motion,
line height). Tool commands (screenshot CLI) stay with the Tester's gallery, stack-neutral.

Accepted → LL-74: DSN-23 amended (two or three directions with references, the owner picks at Gate UX, recorded in
§1); DSN-25 catalogue amended (library or framework default theme or raw palette, template page stack, icon-in-square
cards, vanity stats and invented testimonials, filler copy, generic button labels, placeholder data); DSN-26 amended
(fonts must cover the product's scripts, checked; default faces need a reason; ≤ 3 weights); DSN-34 amended (five
weakest things listed every Design QA; a second round for new primary screens).
