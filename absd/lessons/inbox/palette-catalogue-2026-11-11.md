# Proposal: palette seeded from a colour-combination catalogue (owner request, 2026-11-11)

Source: the kit owner, after seeing Sanzo Wada's *A Dictionary of Color Combinations* (Seigensha reissue of the
1930s *Haishoku Soukan*), asked whether every new website could use the book's colour codes.

Decision with the owner: a guideline, not a mandatory rule. Reasons recorded at the time:

- The book's values are print (ink) values; screen hex values are approximate conversions.
- Combinations were chosen for areas and mood; many same-lightness pairs fail text contrast (DSN-15).
- A combination is not a UI colour system: neutrals, status, focus, hover, disabled and dark theme must be derived.
- One catalogue imposed on every product makes products look alike (a recognisable trend look).
- A brand palette or the brief's colour requirements must win.

Asked for: a palette-source option the Designer may use (product default in `design-system.md` §1, or a brief
Decision), a conversion procedure that keeps hue and adjusts lightness only, and a tool reporting which pairs can carry
text. The kit bundles no catalogue data; the product records its source of screen values.
