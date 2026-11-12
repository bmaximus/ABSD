# Enrichment proposal — KatenatsioTipster, 2026-11-12 (tests that pass vs tests that test; a second contributor's PRs)

Source: KatenatsioTipster (ABSD 1.x adaptation), cycle 007, 11–12 November 2026. Sender: the product's Manager, at
the owner's request. Pseudonymous; no client data.

## What happened

The default branch stayed red for a day while a second contributor (another person's AI coding session) merged PRs
without running the full suites. Restoring it, and then testing that contributor's PRs one at a time before merge, gave
these findings:

1. **Weakened-test pressure.** Fixing 17 failing tests, the quick fix each time was to edit the test to match the new
   output. The owner's rule: «I don't want the tests to pass only — they must actually pass and work; changing a test to
   make it pass is the easy part. A test may change to support new functionality, but that's a thin line.» The kit has
   TCQ-1, TCQ-16 and XCA-4, but they bind the kit's own agents inside a cycle. PRs from a contributor outside the
   pipeline arrived with test edits that no rule reviewed.
2. **Floating CI image.** The CI provider moved its `*-latest` runner label to a new OS overnight. The browser-test
   framework refused to install its browser there, so every browser suite failed before running a test. The change was
   not ours. (Product escape D-121; fixed by pinning the image, with a workflow test that fails on a `*-latest` label.)
3. **Random test data matched domain vocabulary.** A test used a random 8-hex-digit tag to keep its question unique.
   The support chat matched FAQ keywords as substrings, and one keyword is the number «21» (the age limit), so about 1
   run in 35 the tag held «21» and got the gambling-help answer. That was a real product bug: «2021» or «210» got that
   answer too. It surfaced only as a flake. (D-123.)
4. **Unreadable CI failure.** A browser test failed twice in one CI run and passed on re-run. Its screenshot and error
   context were only in a run artifact on storage the investigating session could not reach, so the cause was never
   found. GATE-10 asks for readable failures; the failing step's own output held only "timeout waiting for button X".
5. **Kit rules the product never adopted.** The product's tests are broad (~3,000: unit, integration on a real
   database, access matrix, contracts with recorded provider answers, browser per role on desktop and phone, acceptance
   journeys, deploy-script tests, an 88% coverage gate). It has no mutation testing (GATE-5), no property-based tests
   (VAR-15) and no clock-edge runs, although the kit requires them. A new external feed (an NBA box-score reader) was
   proposed for merge with no recorded real response (EXT).

## Proposed lessons (universal)

| # | Lesson | Proposed target |
|---|---|---|
| P1 | Code from a contributor outside the pipeline (another person, session or bot, through a PR) gets the same test-integrity review as the kit's own agents before merge. Every change to an existing test, fake, fixture, allowlist, threshold or requirement entry is classified (a) follows an intended, owner-approved behaviour change, new expectation still specific → OK, or (b) makes a test pass without the behaviour being right → blocks the merge, with file:line. Red flags to list: assertion removed or loosened (exact → contains/regex, value → truthy, count dropped), expected value edited to the new output, case deleted, skip/only/retry added, timeout raised, try/catch or early return around assertions, fake changed to agree with the code, selector weakened so the check no longer reaches its target | amend TCQ-16 / XCA-4 (scope: any contribution, not only the cycle's agents); merge-queue procedure in process |
| P2 | Merge external contributions one at a time, in order, each with the full suites run on the tree as it will land (default-branch tip + that change); a failure is first classified as the change's or a flake already on the default branch, and the latter is fixed there with its own failing test before re-running | amend GATE-16 (it covers releases, not merges) |
| P3 | Pin every CI runner image and toolchain to an explicit version; a floating label (`*-latest`) is a change outside the change. A workflow test fails on a floating label; moving the pin is a deliberate change made together with the tools that depend on it | amend GATE-11 (it names per-run pulls of images and packages, not runner labels) |
| P4 | Data generated to keep tests unique must not be able to match the product's own vocabulary: no digits or words a matcher, parser or keyword list reads. When a flake depends on random data, look first for a product bug in the matcher (here a numeric keyword matched inside larger numbers) | amend TCQ-5; cross-link VAR-15 (a property test over generated questions would have found it) |
| P5 | A failing browser test prints its own diagnosis to the step log: final URL, visible headings, the role tree near the awaited element, the last console and network errors. An artifact alone is not a readable failure, because whoever investigates may not reach the artifact store | amend GATE-10 |
| P6 | Rules that existed and were not adopted: mutation testing on money/time/access rules (GATE-5), property-based tests on parsers, settlement and ranking (VAR-15), clock-edge and DST runs (test-design), a recorded real response before a new feed merges (EXT). When the product upgrades its kit, its Plan step lists these as adoption work with a target per rule | enforcement: Mode U upgrade checklist names each mandatory gate the product does not yet run |

## Requested by the product

The product's owner asks for a kit release covering P1–P6. The product will upgrade to it (Mode U) when the owner
says so, then plan the adoption work of P6 in its next cycle.
