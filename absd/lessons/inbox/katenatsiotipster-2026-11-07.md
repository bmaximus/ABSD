# Enrichment proposal — KatenatsioTipster, 2026-11-07 (payments "implemented" but not working end to end)

Source: KatenatsioTipster (ABSD 1.x adaptation), cycles 006–007, 3–7 November 2026. Sender: the product's Manager,
at the owner's request after the owner's correction below. Pseudonymous; no client data.

## What happened

Over several days the owner asked, more than once, whether the card-payment integration was implemented. The Manager
answered yes: checkout sessions, a webhook endpoint, price ids in the admin and fulfilment code existed, with green unit,
integration and browser tests. On launch night the owner found that members could not pay, and a payment-flow review
(owner's request, 6/11) found the integration was incomplete in ways no gate had flagged:

1. **Unreachable screen.** The card-purchase component existed and its tests passed, but nothing in the member
   navigation mounted it: no member could open it. The tests reached it by a path no member had. (Product escapes D-70
   and D-73.)
2. **Incomplete provider lifecycle.** Only "checkout completed" was handled. An abandoned or expired checkout left the
   order pending forever and blocked the next attempt; refunds and chargebacks reached nobody; online orders could be
   "approved" by hand by an admin (double fulfilment possible); subscription renewals were ignored while a feature flag
   was off; the admin had no view of provider subscriptions, refunds or amount mismatches.
3. **Provider-side configuration was never part of the plan.** The webhook endpoint's API version, payload style,
   account scope, the set of subscribed events, the live key's permissions and a second endpoint on the same shared
   account were all owner tasks no artifact listed; the version mismatch alone would have broken parsing. (D-65.)
4. **Status reporting.** "Is Stripe implemented?" was answered from code presence and green tests. Nobody stated the
   level reached (built behind a flag vs reachable by a member vs verified against the real provider vs live), so the
   owner believed payments were ready for launch.
5. **Integration and release slips found while fixing it.**
   - A merge-conflict resolution on the shared branch silently dropped one guard (members cancelling an online order);
     only the full integration and payment browser suites caught it.
   - A Builder reported done after running only one of two backend test projects.
   - New tests skipped themselves when their setup failed, and one stubbed the product's own API.
   - A release built from a stale shared branch removed a feature another contributor had merged to the default branch
     minutes earlier; it was restored by a corrective release.

## Proposed lessons (universal)

| # | Lesson | Proposed target |
|---|---|---|
| P1 | Answer "is X implemented / working?" with the level reached (specified, built, reachable, verified against the real system, live) and its evidence, never a bare yes; list the known gaps | new rule, definition of done |
| P2 | A user-facing capability is not built until a journey starts at the role's real navigation and reaches it; a component only a test can open is unreachable | new rule, end-to-end |
| P3 | For each external provider that moves money, identity or messages, enumerate its whole event lifecycle (success, async success, failure, abandonment/expiry, cancellation, renewal, refund, dispute, duplicate/late events, events for other products on a shared account) and map each to a requirement + test or to explicit out-of-scope | new rule, external facts |
| P4 | Provider-side configuration (endpoint registration, subscribed events, API version, payload format, account scope, credential type and permissions) is a fact verified read-only against the real account before release readiness, with written operator steps for what the team cannot do itself | same rule as P3 |
| P5 | Before pushing a release to a shared default branch, diff the branch's current tip against the release tree; any removal not intended means rebuild on the new tip and re-run the affected suites | new rule, release gates |
| P6 | Rules that existed and were not followed: re-verification after a merge-conflict resolution (audits), every mandated check run (GATE-1), no skipped tests (TCQ-1), no stub of the product's own API (FAKE) | enforcement: Manager re-runs the full suites after every integration merge and before every release; the audit counts skips |

## Outcome (maintainer, 2026-11-07)

Accepted in ABSD 2.1.0. P1 → DOD-11 (LL-59); P2 → E2E-18 (LL-60); P3, P4 → EXT-6 (LL-61, LL-62); P5 → GATE-16 (LL-63);
P6 → enforcement in GATE-16 and the Manager's Mode R (LL-64; TCQ-1, GATE-1 and the audits' re-verification rule already
existed and were not followed). Manuals: Analyst (EXT-6), Manager (GATE-16, DOD-11), Auditor (EXT-6, E2E-18).
