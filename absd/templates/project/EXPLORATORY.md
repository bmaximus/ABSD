# Exploratory testing — charters, sessions, findings

> Living, owned by the Tester, NEVER archived (`ABSD:EXPL-*`). Automated tests check what someone thought of;
> exploratory testing is a person — or the Tester agent driving the real product — using it with a goal and curiosity,
> noting anything wrong, confusing or slow. One session = **60–90 minutes, one charter, one principal**, on every
> device class the product supports (phone and desktop for a web UI; real devices before a release).

## How to run a session
1. Pick a charter and an account of that principal.
2. Do what the charter says — then wander: other screens/commands, odd inputs, back/refresh, two tabs or two
   terminals, slow or failing network, midnight and month boundaries, long lists, a foreign time zone.
3. Write each finding as you go: **what you did → what happened → what you expected**, with evidence (screenshot,
   output, time, account, device/runtime).
4. Rate it: **Critical/blocker** (cannot continue, wrong money or results, data loss, security) · **Major** (works
   wrongly) · **Minor** (cosmetic, wording, small annoyance). Every finding becomes a DEF row in the
   `absd-project/context.md` defect backlog (the Manager reserves the id; a finding in the cycle's own scope is a TF of
   that cycle) or a recorded product decision.

## Charters (one per principal × goal; add one for every new journey)
| # | Principal | Device | Charter (goal + where to wander) |
|---|---|---|---|
| 1 | <role> | <phone/desktop/terminal> | <e.g. Complete the core job end to end with real-looking data; check every number against an independent calculation; try after the deadline.> |
| 2 | <role> | | <e.g. Look around as the least-privileged account: is it clear what is locked and how to upgrade? Is anything shown that should be paid or private?> |
| 3 | <admin> | | <e.g. Onboard, change roles, suspend/restore, impersonate: is every action in the audit log with the real actor?> |
| 4 | any | phone only | <Every menu item, every form, portrait and landscape: anything cut off, unreachable, hover-only or too small to tap?> |
| 5 | any | any | <Around midnight in the display zone and at a month/season start: do "today", "this month" and periods make sense?> |

## Manual acceptance checklist (before a release — Mode R)
The automated acceptance tests cover these on every push; a person confirms the feel on real devices.
- [ ] <sign in / wrong password / forced change / sign out — on a phone too>
- [ ] <each principal sees exactly its own menu; nothing else is reachable>
- [ ] <the core journey per principal, with an independent check of the numbers>
- [ ] <external facts visible to users match the real world (e.g. times against an official source)>

## Session log (newest first)
### <YYYY-MM-DD> — charter <#>, <principal>, <device>, by <person | tester agent>
| Severity | Finding (did → happened → expected) | Evidence | DEF / decision |
|---|---|---|---|

**Open — need a product decision**
| Severity | Finding |
|---|---|

**By design (noted so testers don't report it)**
- <…>
