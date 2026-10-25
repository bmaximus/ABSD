# Proposal notes: ABSD v2 acceptance fixtures — 2026-10-25

Verbatim issue reports from three fixture products driven through Foundation on the v2.0.0 kit (`shelf` web-ui,
`tally` cli, `meter` native-app with two vendor feeds). The runs reached Design / Architecture / Gate 2R; build, test,
audit and merge were not exercised. **Unverified** — many repeat findings of `acceptance-review-2026-10-25.md`;
verify each against the files before acting on it. Ledger: LL-58.

354 reports: 0 critical, 104 major, 250 minor.

### FX-1 · major · meter · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table, rows QC-6 and QC-15 (condition "products with persistent state")

The kit never defines "persistent state". ABSD:INTEG-2 narrows it to "persistent state with a managed schema", while ABSD:OPS-5 and ABSD:GATE-12 say only "owns persistent state". QC-6 and QC-15 share the same condition text but have different subjects. For a pipeline whose output files are kept forever but never read back or migrated, applying the condition literally gives the same answer for both, which is wrong for one of them. I had to guess.

### FX-2 · major · meter · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table, row QC-14 (Profiles: all)

Two kit files disagree. The foundation brief makes the secret-canary QC mandatory for every product. absd/playbook/testing/ci-and-release-gates.md GATE-13 applies only when "the product or its pipeline handles any secret or credential", and absd/playbook/process/definition-of-done.md DOD-5 row 5 says "when the product has secrets". Meter has no secret anywhere.

### FX-3 · major · meter · C001 Foundation · analyst 3

- Kit file: absd/tooling/trace_check.py — gate1(): with_ac = {requirement_of(ac) for ac in analysis.referenced("ac")}

The check "every functional requirement has an AC" counts any AC id mentioned anywhere in analysis.md, for example only in the Traceability ACs column. A functional requirement with no AC row at all passes. I reproduced this in /tmp/claude-0/-home-user/53868e08-f41b-5231-bc88-7ed1d8326af8/scratchpad/accept/meter-scratch/g1/analysis.md: a requirement heading with no AC table, plus a Traceability row citing OUTF-1.AC1, gives "gate1: PASS". The control fails silently.

### FX-4 · major · meter · C001 Foundation · analyst 3

- Kit file: absd/playbook/process/requirements.md — ELIC-2 Check ("every Yes cites a requirement") vs its rule text ("source: brd section, D-n, catalogue id"); .claude/agents/analyst.md §6.1 ("every Yes cites an id")

The Foundation matrix must cover the whole product, including capabilities that are deliberately not built this cycle (brd §3.1–§3.4) and so have no requirement ids. A Yes cell for them cannot cite a requirement. The Check text and the rule text disagree on what a Yes may cite.

### FX-5 · major · meter · C001 Foundation · analyst 5

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block vs .claude/agents/analyst.md §9

The brief template's reply format (Status COMPLETE-WITH-CONFLICTS/HALTED, 'Findings: Critical/Major/Minor', 'Blockers / questions') differs from the analyst manual's §9 format (Mode, Counts, Facts needed, trace_check, Sign-off needed, Routed items, Proposals). The manual's format has only a count of changed matrix cells, while the Manager needs the list of changed §2/§4/§6 cells for the ELIC-21 sign-off (meter-L8). This Manager added a 'Changed §2/§4/§6 cells' line to the brief that neither template has.

### FX-6 · major · meter · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.2 step 3 and §5.1 Delta row

Delta mode, which the §2 table prescribes for Gate 1 rounds, says untouched sections read 'Unchanged — <reason>'. In an in-cycle G1 round that would blank the cycle's own signed-off sections. The brief overrode it ('do not replace them'). The kit has no in-place revision mode for Gate 1 rounds (known as meter-L9, still unfixed).

### FX-7 · major · meter · C001 Foundation · analyst 5

- Kit file: absd/templates/project/foundation-brief.md — QC table, QC-15 'products with persistent state'; absd/playbook/testing/nonfunctional.md OPS-5 'Applies when: the product owns persistent state'

The kit does not say whether QC-15 and the OPS-5 drill apply when the product is the only writer of kept data but the user puts its backup on the host platform, outside the product, and forbids product-made copies (D-19). One reading keeps the drill with a test-step copy; the other makes it N/A or a waiver. That ambiguity forced a new blocking contradiction (D-16 'in' vs D-19) and likely costs a third Gate 1 round. Related to meter-L5.

### FX-8 · major · meter · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — §4.2 step 3; §5.1 Mode table (Delta row); §5.1 Statuses

Two parts of the Delta rules disagree with in-cycle Gate 1 rounds, and nothing in kit 2.0.0 settles it (same as meter-L9). (a) Delta says unchanged sections read "Unchanged — <reason>". That is written for a delta against an archived analysis; in a G1 round it would blank sections of the same cycle that the user has already signed off. The brief overrides it again. (b) Requirement-heading statuses (new | changed | removed | re-verify) are defined against the archive. The manual does not say what an in-place round does to a same-cycle requirement whose Source or Behaviour text it edits (OUTF-1, QC-15 here).

### FX-9 · major · meter · C001 Foundation · analyst 8

- Kit file: .claude/agents/analyst.md — 4.3 step 1 (and 6.2 first item)

The check that analysis.md is unchanged since the Gate 1 approval SHA is `git diff <sha> -- absd-project/working/analysis.md`. That command leaves out the parts directory `absd-project/working/analysis/`. 5.1 tells the Analyst to split analysis.md into parts above 20k tokens, and trace_check reads those parts. So a change to a part (here §1 to §11 live in analysis/01-requirements.md and analysis/02-lenses.md) after approval passes the manual's check unseen, and the control fails silently for every split analysis.

### FX-10 · major · meter · C001 Foundation · architect 13

- Kit file: .claude/agents/architect.md — §7 Halts (blocking upstream issue) and §4.1 Done; the brief's D-30 constraint

The manual has only two paths: a blocking §0.2 issue (Status BLOCKED, specify nothing that depends on it) or a full spec. It has no path for a missing failure outcome that the user has explicitly carried forward as non-blocking (OQ-19, D-30: keep the fallback message, no Gate 1 round 4). A Builder-ready QC-8 must still state what is in place after deploy.failed_no_rollback, and the brief forbids filling it with a default.

### FX-11 · major · meter · C001 Foundation · architect 13

- Kit file: absd/playbook/testing/ci-and-release-gates.md — GATE-9, GATE-14 ("on every push", workflow files, required checks); also architect.md §5 §12 rule, absd/templates/project/context.md §4 "CI job" column, absd/templates/project/foundation-brief.md step 4 "quality gates & CI"

The job graph, workflow-file ownership split and push triggers assume a CI service and pushes. RULES §6 allows local evidence, but no kit file says how jobs, owners, triggers and the 'CI job' column map onto a product with no CI service and no remote (D-2, D-4).

### FX-12 · major · meter · C001 Foundation · designer 11

- Kit file: absd/tooling/trace_check.py — gate_ux() (lines 424-444) and the usage header's gate-ux line; cited by absd/playbook/design/excellence.md DSN-1, DSN-13 and DSN-16 Check

gate-ux checks only two things: every UJ/SCR appears in Traceability, and every requirement design.md mentions exists in the catalogue. It never checks that the in-scope requirements, or the analysis failure modes, are covered. Yet DSN-13 Check says 'every analysis.md failure mode has a row (trace_check)' and DSN-16 says 'trace_check gate-ux has no unmapped requirement'. Negative control: a design.md with one UJ and no requirement at all gets 'gate-ux: PASS — 3 checks passed'. The coverage control the playbook promises does not exist, and nothing reports that.

### FX-13 · major · meter · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.2 steps 3-4 and Done line vs .claude/agents/manager.md §6.3

Design System mode (Foundation step 3) also writes the skeleton's design.md. Yet 4.2 self-verifies only by §6.4 and asks neither for gate-ux, the §20 rubric, the DSN-18 contract and runbook, nor §6.1/§6.3, all of which Gate UX checks on that design.md. Two kit files disagree; this is already lesson meter-L22, confirmed here.

### FX-14 · major · meter · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 4.4 route table row B; 4.6; 5.2; absd/templates/artifacts/brd.md header (Mode: F/S/C)

Mode B has no artifact for the user's product description. The Analyst (Foundation) must build the actor x capability matrix 'for the whole product as known today' (analyst.md 4.1) and its Done-when says 'every brd sentence traced', yet its listed input in Mode B is only the context.md frame. brd.md is defined for Modes F/S/C only, so nothing says where the owner's notes go in a Foundation cycle.

### FX-15 · major · meter · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 6.2 last item ("a Facts result that changes a requirement → analyst · Delta → G1")

Only one Facts outcome has a route. A Facts result can contradict a statement the gated analysis carries without changing a requirement. Here, EXT-AMPERA-4 (VERIFIED: Athens offsets) contradicts the UNVERIFIED "timestamps in UTC" in analysis §1.4 time row 5 and §7 AMPERA row 4. The kit does not say whether the analysis must be corrected. With G1 at round 3/3, any Delta would be an escalation. So the Designer and Architect will read a gated analysis that holds a contradicted candidate.

### FX-16 · major · meter · C001 Foundation · manager 11

- Kit file: .claude/agents/designer.md — §2 row B, §4.2 steps 3-4 and Done line, §6.4

Foundation step 3 runs in Design System mode, which also writes the skeleton's design.md. That mode self-verifies only by §6.4 and asks neither for `trace_check gate gate-ux` nor for the §20 rubric. Gate UX (manager.md 6.3) checks gate-ux all ✓, the DSN-18 surface and runbook, LOC formatters and the rubric on that same design.md. Two kit files disagree on what the Foundation design.md must meet.

### FX-17 · major · meter · C001 Foundation · manager 12

- Kit file: absd/tooling/trace_check.py — gate gate-ux (usage header and implementation)

gate-ux checks only that UJ/SCR ids are in the Traceability section and that the requirements design.md cites exist in the catalogue. A design.md that names no requirement at all still passes (the Designer's negative control in evidence/designer/gate-ux.txt). Yet manager.md 6.3 ('every user-visible requirement covered'), the DSN-1 Check and the DSN-16 Check ('trace_check gate-ux has no unmapped requirement') rely on it. So the coverage control fails silently.

### FX-18 · major · meter · C001 Foundation · manager 12

- Kit file: .claude/agents/manager.md — 6.3 Gate UX, 6.8 Finding routing, 7 Worker questions

There is no step for a non-blocking upstream issue in design.md §0.2 (or architecture §0.2). 6.3 lists only UXQ/UXA, 7 lists OQ/UXQ/CLR, and 6.8's requirements-gap route (analyst Delta → G1) collides with the G1 limit: G1 is at 3/3 after the Foundation's rounds, so any requirement fix from a downstream issue becomes a 4th round. The kit says neither whether a non-blocking upstream issue holds Gate UX, nor whether it may be carried to a later cycle, nor whether a G1 round reopened after G1 PASS counts toward the limit.

### FX-19 · major · meter · C001 Foundation · manager 13

- Kit file: absd/templates/project/foundation-brief.md — step 4 ("quality gates & CI, split into Builder and Tester workflow files"); also absd/playbook/testing/ci-and-release-gates.md GATE-9, GATE-14; QC-13 "in CI"; absd/templates/project/context.md §4 "CI job" column

The Foundation architecture step, the CI job graph rule (GATE-9), the integrity checks "on every push of a cycle branch" in a Tester-owned workflow (GATE-14) and QC-13 all assume a CI service and a push target. The kit gives no guidance for a product with no CI service and no remote (this one, D-4), apart from GATE-1's "local output". So nobody is told what a "workflow file", a "required status" or "on every push" means when everything runs locally, and the §4 "CI job" column has no defined value.

### FX-20 · major · meter · C001 Foundation · manager 14

- Kit file: .claude/agents/manager.md — 6.4 Gate 2 checklist; 7 Worker questions; 4.13 counters

After Gate 2 the Architect's §0.2 leaves non-blocking upstream items owned by the user (#4 file group, #8 overlapping deploys) and by the Designer (#2 no outcome for a log that cannot be written). 6.4 has no item for them. Section 7 says only 'business → user, technical → owning agent'. The kit never says whether they hold step 4R, or how a Designer-owned gap found at Gate 2 is handled without re-opening GUX and G2·2R. G2 and G2R share one round counter, so an answer that changes the blueprint after 2R costs a whole review round. This is the same gap as meter-L25, one gate later.

### FX-21 · major · meter · C001 Foundation · manager 14

- Kit file: absd/RULES.md — §9 context.md ≤ 25 KB vs .claude/agents/manager.md 4.6 'After G2R: ADR-002's table verbatim into §3, ADR-001 into §2, the ADR-003 commands into §4'

The Foundation template makes the Manager fill context.md §1 and §5–§7 with the user's verbatim answers (23 772 bytes before §2–§4). Copying the three ADR tables verbatim, as 4.6 requires, takes the file to about 27.4 KB, over the RULES §9 budget. No step says what to trim or whether the machine-read §3/§4 tables count toward the budget.

### FX-22 · major · meter · C001 Foundation · manager 2

- Kit file: absd/tooling/ownership_check.py — line 99 (from absd_sync import SEEDS); absd/templates/project/ (no .gitignore seed)

ownership_check imports absd_sync, so its first run writes absd/tooling/__pycache__/ into the product tree. The install seeds no .gitignore, so `git status --porcelain`, which manager.md 4.5 and RULES §5 require to be empty at every hand-off, turns dirty after the first ownership check. No owner for .gitignore exists before ADR-002, so nobody may legitimately add the ignore line during step 1.

### FX-23 · major · meter · C001 Foundation · manager 2

- Kit file: absd/templates/project/context.md — §1 Kit sync line; header note; manager.md 4.1 step 3

The Mode B entry test is 'context.md §1 still holds `<…>` placeholders'. The template's own fixed kit-sync sentence contains `<operation> <version>`, so read literally §1 always holds a placeholder and every session re-enters Mode B, even after the Foundation row exists. User-given file patterns such as summaries/<YYYY-MM-DD>.json have the same problem.

### FX-24 · major · meter · C001 Foundation · manager 2

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table ('select per profile'); analyst.md 4.1 Foundation paragraph

Neither the brief nor the manuals say who selects the QCs (the Manager in brd, or the Analyst). Conditional columns ('products with persistent state', 'all deployable') must be settled before any architecture exists, so selecting them needs a guess, and the Manager may make no technical judgement.

### FX-25 · major · meter · C001 Foundation · manager 4

- Kit file: .claude/agents/manager.md — §6 intro ("any ✗ fails the gate and returns to the owner") vs §6.2 last item ("Approved → analyst · catalogue apply → gate1 all ✓")

gate1 includes the check "every requirement in analysis.md is defined in catalogue.md". That check can only pass after the catalogue apply, and §6.2 puts the apply after the user's approval. At the G1 review gate1 is therefore always ✗, and §6 says any ✗ fails the gate. The kit gives no pre-apply mode. The Analyst worked around this with `--catalogue absd-project/working/analysis.md`, which checks the analysis against itself, so the third check always passes.

### FX-26 · major · meter · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — §9 Reply format ("Paths and ids, never contents or paraphrase") vs absd/playbook/process/requirements.md ELIC-21 ("the Manager shows the user the actor × capability matrix, the role value check and the inherited behaviour inventory") and manager.md 6.2 ("The user saw the matrix …")

The two files disagree. Followed literally, §9 makes the G1 sign-off question cite only paths and section numbers. The owner then signs off on content they never saw (the owner reported exactly this from G1 round 1), so the ELIC-21 control can pass without the owner seeing anything. No tool checks the sign-off either (trace_check does not read the brd §9 sign-off line).

### FX-27 · major · meter · C001 Foundation · manager 6

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block (vs .claude/agents/analyst.md §9 and the other manuals' §9)

The brief template fixes a generic 4-line reply format (Status, Artifacts, Findings, Blockers), but every worker manual's §9 defines its own, richer reply format (analyst.md §9 has 11 lines: Counts, Facts needed, Sign-off needed, Routed items, Proposals). A brief filled in literally from the template asks for a different reply than the worker's manual, and the Analyst flagged the conflict.

### FX-28 · major · meter · C001 Foundation · manager 6

- Kit file: .claude/agents/manager.md — §6.2 Gate 1 checklist ("every blocking one answered by the user as a D-n") and §4.13 (3 rounds per gate)

The kit does not say whether a user answer to a blocking OQ that changes no requirement (here OQ-17 option A: QC-15 stays as written) must go back through another analyst · Delta round so analysis.md stops showing the OQ as open, or whether the D-n in brd §9 is enough. The Delta mode itself can raise new blocking questions from the answers it applies (D-19 vs D-16 gave OQ-17), so answer-recording rounds can use up the 3-round G1 limit and force an escalation without any real defect. Catalogue apply writes only catalogue.md, so it cannot close an OQ either.

### FX-29 · major · meter · C001 Foundation · manager 7

- Kit file: absd/RULES.md — §2 Limits (3 revision rounds per gate) with .claude/agents/analyst.md §2 table (a Gate 1 round is Delta mode) and .claude/agents/manager.md 6.2

A user answer to a blocking OQ that changes no requirement (OQ-17 = A, QC-15 kept as written) can only reach analysis.md through an Analyst Delta, and every Delta at Gate 1 counts as a round. The kit has no lighter path, such as Catalogue apply recording answered OQ statuses or a 'record-only' revision outside the round count. Here G1 round 2 had to be closed FAIL on the user's own answers, and the last allowed round (3/3) goes to copying text. A small finding there now forces an escalation. The owner raised this too.

### FX-30 · major · meter · C001 Foundation · manager 7

- Kit file: absd/playbook/process/requirements.md — ELIC-21 (sign-off) with .claude/agents/manager.md 6.2 and §9

ELIC-21 does not say whether the user's sign-off still covers a matrix cell that the next revision rewrites only to record the user's own answer. Here the user signed off 'reading every "QC-15 scope is OQ-17" cell as resolved by (A)'. Read strictly, the round-3 rewrite of those cells is a changed cell that needs another sign-off, and that turns one more round into another question to the user. The owner also reported that the packet is dense with internal ids they cannot resolve without the repository, so the sign-off rests on trust rather than review.

### FX-31 · major · meter · C001 Foundation · manager 8

- Kit file: .claude/agents/manager.md — 6 ("any ✗ fails the gate") vs 6.2 last item (catalogue apply after approval)

At the G1 review, gate1 can never be all ✓: its third check needs the catalogue apply that 6.2 puts after approval. Taken literally, 6 says the gate fails. The Analyst's self-check (`--catalogue analysis.md`) makes that check true by definition. This happened again in round 3: "FAIL — 1 of 3" on an artifact that is ready to approve.

### FX-32 · major · meter · C001 Foundation · manager 9

- Kit file: .claude/agents/analyst.md — 4.3 Catalogue apply, step 1

The check that the analysis is unchanged since approval diffs only absd-project/working/analysis.md. RULES §9 splits artifacts over 20k into an index plus parts (working/analysis/NN-*.md), so a change in a part gets past this control unseen. The Analyst reported it.

### FX-33 · major · meter · C001 Foundation · manager 9

- Kit file: absd/templates/project/foundation-brief.md — Steps table, step 2a (Facts) vs step 4 (ADR-002); also .claude/agents/tester.md 4.5

Facts runs before ADR-002 assigns test paths. EXTERNAL-FACTS.md still requires a VERIFIED fact's recording to be 'committed in the test tree'. At Facts, context.md §3 holds only <tests/**>-style placeholders, which ownership_check skips, so any recording outside docs/testing/** is 'unowned' (a warning, an error with --strict). The recording location gets decided before the architecture that owns the layout, and the kit says nothing about where it goes.

### FX-34 · major · meter · C001 Foundation · tester 9

- Kit file: .claude/agents/tester.md — §4.5 step 4 vs 'Done when' (same paragraph); §7 'Reply BLOCKED' list

Step 4 says 'No access or credential → BLOCKED + proposed RISK'. 'Done when' says the run is done when 'each in-scope fact has a row with status and evidence'. The SERVER system cannot be reached by design (D-4, Meter runs locally). Read literally, the kit blocks the Foundation on an access the user has said is not available, even though no C001 behaviour rests on these facts and RISK-3…6 already cover them. The kit does not separate 'no access, and current behaviour needs the fact' from 'no access, fact recorded UNVERIFIED with a RISK'.

### FX-35 · major · meter · C001 Foundation · tester 9

- Kit file: absd/playbook/testing/external-facts.md — EXT-2 (and the intro of absd/templates/project/EXTERNAL-FACTS.md)

VERIFIED needs a recording plus an independent source such as official documentation. A vendor file drop with no published docs has only one possible independent source, the vendor's spec, and here it reached us only as the user's relay, which EXT-2 counts as a statement. The kit does not say three things: whether a published standard (RFC 4180/3339/3629, the tz database) counts as the independent source for syntax and time facts the recording itself settles; what to do when the recording contradicts the documentation (the note says UTC, the files carry Athens offsets); and whether a self-describing field such as an offset needs a source at all.

### FX-36 · major · meter · C001 Foundation · tester 9

- Kit file: absd/RULES.md — §6 evidence validity; absd/templates/artifacts/test_report.md header 'Facts: its own, earlier SHA; valid while git diff --quiet <sha> HEAD'; .claude/agents/tester.md §4.0 step 6 'Facts, Log: one commit'

The single Facts commit must contain EXTERNAL-FACTS.md and the recordings, which are outside absd-project/. That commit therefore moves the product SHA past the SHA its own Facts evidence cites. By the RULES §6 test, the evidence is invalid at HEAD the moment it is committed. RULES §6 exempts only the Log commit, not Facts.

### FX-37 · major · meter · setup

- Kit file: absd/tooling/ownership_check.py — imports absd_sync.py; together with the install seeds (no .gitignore) and absd_sync.py check

Running ownership_check.py in a product writes absd/tooling/__pycache__/absd_sync.cpython-313.pyc inside the read-only kit path. The installer seeds no .gitignore, and absd_sync.py check ignores the folder ('0 extra'), so nothing warns. I tested it in a throwaway clone: the next commit that used `git add -A` (here a manager commit, ABSD-Agent: manager) was a violation, 'changed absd/tooling/__pycache__/absd_sync.cpython-313.pyc, owned by kit'. The seeded settings allow `git add:*`, and agents run these tools every cycle, so this run will likely hit it.

### FX-38 · major · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table (QC-7, QC-8, QC-15, QC-16) vs absd/playbook/process/requirements.md ELIC-14 and absd/RULES.md rule 8

The same operability defaults (boot on empty infrastructure, deploy/rollback, backup→restore, fresh clone) are both a Foundation QC-n requirement and a default REQ-NF. No kit file says whether a QC-n replaces the REQ-NF, whether both must exist, or how they link. The analyst has to guess, and doubled requirements are the likely result.

### FX-39 · major · shelf · C001 Foundation · analyst 2

- Kit file: absd/playbook/testing/external-facts.md — EXT-1 (with EXT-3) and the §7 note in absd/templates/artifacts/analysis.md

An UNVERIFIED fact driving lifecycle must be 'flag-off and fail-closed' with a §12 row 'blocks flag:<name>'. EXT-3 makes the host platform an external system, so every Foundation of a deployable product rests on UNVERIFIED host facts (runtime, OS, start/stop semantics). Deploy, rollback and backup cannot sit behind a feature flag, so the rule cannot be followed as written.

### FX-40 · major · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/project/foundation-brief.md — QC-10 row, Profiles 'products with external systems'

Contradicts EXT-3 (platforms are external systems 'with fact sheets, fakes and live checks') and FAKE-10 (a live check wherever safe read-only access exists). It is ambiguous whether a product whose only external system is its host platform selects QC-10; the Manager's mechanical selection excluded it.

### FX-41 · major · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/project/EXTERNAL-FACTS.md — system section template, rows EXT-<SYS>-1 to EXT-<SYS>-12

The template numbers the 12 fact-checklist rows by topic (-1 format, -2 time zone, …). .claude/agents/analyst.md 4.1 step 1 and ELIC-10 have the Analyst reserve 'highest + 1' per needed fact. For a new system the two numberings collide (my EXT-HOST-1 = runtime; the template's -1 = format and encoding).

### FX-42 · major · shelf · C001 Foundation · analyst 4

- Kit file: .claude/agents/analyst.md — §4.2 step 3 and §5.1 Delta row; also absd/templates/briefs/invocation-brief.md 'Produce' line

A Delta must write untouched sections as 'Unchanged — <reason>' and §2 as 'one line citing the archived copy'. That assumes an archived full analysis exists. In a Gate 1 round Delta inside the same cycle there is no archive: the round 1 content exists only in this working file. Replacing §3, §5 and §6 with one line would delete content that the catalogue apply, the Designer and the Architect still need.

### FX-43 · major · shelf · C001 Foundation · analyst 4

- Kit file: .claude/agents/analyst.md — §4.2 step 4 and §5.1 Statuses (new | changed | removed | re-verify)

No baseline is defined for Status values in a Gate 1 round Delta before any catalogue apply. Marking round 2 edits 'changed' would contradict §15, where every row is an Add (the catalogue is empty), and the Traceability 'add' column. Leaving them 'new' hides from the Manager what changed since round 1.

### FX-44 · major · shelf · C001 Foundation · analyst 4

- Kit file: absd/playbook/process/requirements.md — ELIC-2 (rows = every principal × entitlement state, jobs, service identities, inbound callers); .claude/agents/analyst.md §6.1 Lenses item 1

The rule requires a row for every principal × state, and for absent jobs and service identities, even when rows are identical or all N/A. It says nothing on whether identical rows may share one row. The owner found 13 rows excessive for a three-role product ('Keep the rows only where they change who may do something', D-11). Reconciling the two needed guessing.

### FX-45 · major · shelf · C001 Foundation · analyst 4

- Kit file: absd/templates/project/claude-settings.json — PreToolUse hook command `python3 "$CLAUDE_PROJECT_DIR/absd/tooling/ownership_hook.py"`; absd/tooling/ownership_hook.py imports ownership_check

The hook runs without -B and does not set sys.dont_write_bytecode. Importing ownership_check from absd/tooling therefore writes absd/tooling/__pycache__/ into the vendored kit on every agent Write or Edit, which dirties the tree. This is the same defect cycle.md Decisions 2026-10-24 found for manual tool runs, but the '-B' workaround in briefs does not cover the hook. absd_sync check does not report the file. Not observed in this session (the hook did not run here); found by reading the code.

### FX-46 · major · shelf · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.3 step 1 and §6.2 item 1 ("git diff <sha> -- absd-project/working/analysis.md empty")

The 'unchanged since Gate 1' control checks only the index file. §5.1 lets analysis.md be split into parts under absd-project/working/analysis/NN-<part>.md, and trace_check reads those parts. In this cycle §1 to §11 (all requirements and ACs) live in analysis/01-requirements.md and 02-lenses.md. A change to a part made after approval would pass this check without any warning. The Manager's resume-point check in cycle.md has the same gap.

### FX-47 · major · shelf · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §9 Reply format vs absd/RULES.md §8 and absd/templates/briefs/invocation-brief.md 'Reply format'

The three kit files disagree on the reply. RULES §8 requires 'finding counts by severity' in every worker reply, but the analyst's single reply format has no Findings line. It also has no line for Catalogue apply results (rows added, changed, retired, placeholders removed). Its Counts, Facts and Sign-off lines are written for Analyze and Delta. The brief template's generic format (COMPLETE-WITH-CONFLICTS, HALTED, Findings) differs again. This Manager's brief used a third, mode-specific format.

### FX-48 · major · shelf · C001 Foundation · designer 8

- Kit file: absd/tooling/trace_check.py — gate_ux() (gate-ux preset, docstring lines 31-33) vs absd/playbook/design/excellence.md DSN-13 Check

DSN-13's Check says 'every analysis.md failure mode has a row (trace_check)', but gate-ux only checks two things: every UJ/SCR appears in the Traceability section, and every referenced requirement id exists in the catalogue. It does not check failure-mode or AC coverage. A design.md with no UJ or SCR (for example an http-api-only design) passes vacuously. As a result, 'gate-ux ✓' in the reply and at the Manager's gate says nothing about DSN-13 or about requirement coverage.

### FX-49 · major · shelf · C001 Foundation · designer 8

- Kit file: .claude/agents/designer.md — §5.1 profile→sections table; ABSD:DSN-1 table (absd/playbook/design/excellence.md)

The laptop operator runs deploy/rollback/backup commands in a terminal. That is a human-facing command surface, but cli is not a declared profile: D-1, and analysis §10 says 'profile extras N/A'. Even so, APP-NF-7.AC1 says 'copy: design.md' and APP-NF-1/2/3/4 quote the operator's messages. The manual gives no section for operator-tooling copy when cli is not declared, and DSN-17 (grammar, help, exit codes, golden outputs) only applies when it is.

### FX-50 · major · shelf · C001 Foundation · designer 8

- Kit file: absd/playbook/design/rubric-and-qa.md — DSN-18 and design-system §7 contract style vs .claude/agents/designer.md §5.1 'Machine outputs' bullet / ABSD:ORACLE-4

No rule says who owns how a machine-output value is written (format, precision) when the AC's literal and the designed contract differ. ORACLE-4 and the manual say values come from the AC. DSN-18 and the design-system make the Designer define the formats. Here the analysis even says 'Exact field names and values: design.md'. APP-2.AC1 writes started '2026-10-24T20:59:41Z', but the strict 'later than' in APP-2.AC5 needs millisecond precision: a restart lands within the deploy's own second (EXT-HOST-3). The kit also does not say whether the Tester compares strings or instants.

### FX-51 · major · shelf · C001 Foundation · designer 8

- Kit file: .claude/agents/designer.md — §8 rule 3 / RULES rule 8 ('no new … screen … without a requirement id') vs ABSD:DSN-13 ('plus a generic fallback with retry')

DSN-13 requires a generic error fallback, which for web-ui means a server-fault page. No AC states what a visitor sees on a page server fault: APP-NF-6 covers only the log entry. Two kit rules therefore pull in opposite directions: design the fallback screen, or add no screen without a requirement.

### FX-52 · major · shelf · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 4.6 Mode B ("Brownfield: … step 5 adds tester · Baseline") vs absd/templates/project/foundation-brief.md step 5 and .claude/agents/tester.md §2/§4.1

These files disagree on whether a greenfield Foundation runs tester · Baseline. The manager manual says only brownfield adds it. The foundation brief and the tester manual put Baseline at step 5 for every Mode B, because it fills the seeded TESTING.md.

### FX-53 · major · shelf · C001 Foundation · manager 1

- Kit file: absd/templates/project/foundation-brief.md — step 1-2; also .claude/agents/analyst.md §2 (Mode B input = "context.md frame") and §4.1 Done when ("every brd sentence traced"); absd/templates/artifacts/brd.md header (Mode: F/S/C)

Mode B defines no brd.md. Yet the Foundation Analyst must build the whole-product actor × capability matrix "as known today", and the walking-skeleton requirement needs a user-stated scope. The kit names no artifact that carries the user's product description (the user's notes) to the Analyst. The analyst's done-when also refers to brd sentences.

### FX-54 · major · shelf · C001 Foundation · manager 2

- Kit file: absd/tooling/ownership_check.py — line 99 `from absd_sync import SEEDS`; absd/templates/project (no .gitignore seed); absd_sync.py check

Running a kit tool with plain `python3` (as the manuals and the settings allow list write it) writes absd/tooling/__pycache__/absd_sync.cpython-313.pyc into the vendored kit. The tree turns dirty, which breaks the clean-tree checks every hand-off needs, and a routine `git add -A` commits a kit-path change under an agent trailer. `absd_sync.py check` still reports '0 extra' with the file present, so only ownership_check notices, and only after the commit.

### FX-55 · major · shelf · C001 Foundation · manager 2

- Kit file: absd/templates/project/foundation-brief.md — step 4 (Builder and Tester CI workflow files), with DOD-5 row 8 in absd/playbook/process/definition-of-done.md, manager.md 4.10 step 4 (merge when CI is green) and ABSD:GATE-14 (CI re-runs the gates)

The kit assumes a CI service exists: workflow files, 'in CI' checks, merging only when CI is green. It has no path for a product with no CI at all, as here (local git, no remote, no CI). DOD-5 row 8 and the merge condition cannot be met as written, so what stands in for them has to be guessed.

### FX-56 · major · shelf · C001 Foundation · manager 3

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table, row QC-10 (Profiles: "products with external systems")

Two kit files disagree on whether QC-10 applies to a product with no outside services. ABSD:EXT-3 (absd/playbook/testing/external-facts.md) and ABSD:DOD-5 rows 3 and 5 (definition-of-done.md: EXTERNAL-FACTS section for deploy and CI platforms; 'when an external system exists: missing live credential' RED) count the host/deploy platform as an external system. The QC table's Profiles cell does not mention platforms, so I selected QC-10 out in brd §3.2. The Analyst then challenged that choice (§13 #1, OQ-7). For a local-laptop product it is also unclear what 'live checks nightly' and 'a missing credential is RED' mean when there is no credential and no nightly runner.

### FX-57 · major · shelf · C001 Foundation · manager 4

- Kit file: .claude/agents/manager.md — 6.2 Gate 1, item 4 ("every blocking one answered by the user as a D-n"); with absd/playbook/process/requirements.md ELIC-19 and .claude/agents/analyst.md §2/§7

Every blocking assumption or open question has to be answered by the user as a D-n, and nothing separates technical from business ones. analyst.md calls technical questions non-blocking and gives them to the Architect, but in a Foundation the QC selection (QC-10) and the skeleton's scope (A-1, an empty store) block Gate 1 before any Architect exists. So they end up with the owner, even though the owner's standing answer gives technical choices to the team. The owner noticed this and reported it. foundation-brief.md also names no owner for selecting the QCs.

### FX-58 · major · shelf · C001 Foundation · manager 5

- Kit file: absd/playbook/process/requirements.md — ELIC-21 (Applies when: every Gate 1); .claude/agents/manager.md 6.2 sign-off item

The user signed off the round 1 matrix and asked in the same answer for rows to be merged. The kit doesn't say whether the Delta round that then restructures the signed-off §2 matrix (13 rows → 7, no value changed) at the user's own request needs a second showing to the user. 'Gate 1 never passes on the Manager's own reading' argues for showing it again. The standing answer and a sign-off that already covers the answers argue against.

### FX-59 · major · shelf · C001 Foundation · manager 6

- Kit file: docs/testing/EXTERNAL-FACTS.md (seed: absd/templates/project/), .claude/agents/tester.md — EXTERNAL-FACTS preamble ('recorded real response committed in the test tree'); tester.md §4.5; foundation-brief step 2a

In a Foundation cycle, Facts (step 2a) runs right after Gate 1, before ADR-002 defines the source layout. At that point context.md §3 has only docs/testing/** as a filled Tester row; the test-tree row is still a placeholder, which the hook and ownership_check skip. VERIFIED requires a recording 'committed in the test tree', and no test tree exists yet. No kit file says where Facts recordings go before ADR-002, or whether they move once it passes.

### FX-60 · major · shelf · C001 Foundation · manager 7

- Kit file: .claude/agents/tester.md — §4.0 step 2 vs §7 Resume; .claude/agents/manager.md 4.5 / 4.13 resume counter

§4.0 step 2 says a dirty tree means BLOCKED, but §7 Resume tells the Tester to continue from the uncommitted changes in its own paths. A resumed run therefore always meets a dirty tree, so as written every resume is BLOCKED. The Manager side has a related gap: manager.md counts resumes only as Resume briefs the Manager sends. A worker interrupted inside one invocation (here the machine restarted) that continues by itself is not covered, and nothing says whether that counts toward '2 resumes per invocation'.

### FX-61 · major · shelf · C001 Foundation · manager 9

- Kit file: absd/playbook/design/excellence.md — DSN-13 Check ("every analysis.md failure mode has a row (trace_check)") vs absd/tooling/trace_check.py gate gate-ux

The gate-ux preset runs only 3 checks: UJ referenced, SCR referenced, requirement ids defined. It never checks that every analysis.md failure mode has an error-catalogue row, even though DSN-13 says trace_check does. A design with no row for a failure mode would still pass gate-ux, so the control fails silently. The Designer reported the same thing.

### FX-62 · major · shelf · C001 Foundation · manager 9

- Kit file: .claude/agents/manager.md — 6.3 Gate UX checklist; 4.4 route table

No step says how or when the Manager routes a Designer's NON-blocking §0.2 upstream issues owned by the Analyst. It does not say whether GUX may pass while they are open, whether they wait for the next Analyst step, or whether they force an analyst Delta now. Routing them now costs a G1 round (here the last one, 3/3, which needs the user's sign-off again) and makes every downstream gate re-pass. Leaving them open has no defined closing point.

### FX-63 · major · shelf · C001 Foundation · manager 9

- Kit file: absd/playbook/design/excellence.md — DSN-1 ("a deliverable is never N/A while its interface exists", Why LL-41) vs RULES §3 rule 8 operability defaults and context.md §1 Interface profiles

The operability defaults (deploy, rollback, restore drill) create terminal commands that an operator uses. No kit file says whether these operability commands are a cli interface that needs DSN-17 design, or Architect-named tooling outside the declared profiles. DSN-1's own rationale (LL-41: a CLI's grammar and exit codes left to the architecture) argues for designing them, while the declared profiles (web-ui, http-api) exclude cli. The Designer had to guess (copy only) and pass the question to the user.

### FX-64 · major · shelf · C001 Foundation · tester 6

- Kit file: .claude/agents/tester.md — §4.0 step 2 vs §7 Resume

§4.0 step 2 says every run needs `git status --porcelain` empty, else BLOCKED. §7 Resume says to read the uncommitted changes in your paths and continue at the first unticked step. A run interrupted before its single Facts commit always leaves a dirty tree, so the two rules contradict each other. The brief also said 'Resume: fresh start' although the interrupted run's untracked output (recordings, a report with no ticks) was present: the Manager cannot see what a worker left behind.

### FX-65 · major · shelf · C001 Foundation · tester 6

- Kit file: absd/templates/project/EXTERNAL-FACTS.md — section skeleton, fact table rows EXT-<SYS>-1 … EXT-<SYS>-12

The skeleton ties each fact id number to an EXT-2 checklist row (1 = format … 12 = version). The Analyst instead reserves ids per fact (analysis §7: EXT-HOST-1 = runtime … 7 = availability), and tester.md §4.5 step 1 says to adopt those and number missed facts highest + 1. The two numbering schemes collide, so the template rows cannot be kept as they are.

### FX-66 · major · shelf · C001 Foundation · tester 6

- Kit file: .claude/agents/tester.md — §4.5 step 2 (with absd/playbook/testing/external-facts.md EXT-2)

A fact's status is all-or-nothing, and the kit does not say what to do when a reserved fact is only partly observable. EXT-HOST-4 (network reach) is fully observable within the machine but not from other devices; marking the whole row UNVERIFIED would deny the Architect the verified part.

### FX-67 · major · tally · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — Steps table step 2 ("+ any walking-skeleton requirement") and the Quality capabilities table; .claude/agents/analyst.md §4.1 "Foundation" and §7 BLOCKED list

The Foundation asks for walking-skeleton requirements as well as one QC-n per capability. But the context area codes are feature areas (here TALLY, PARSE, OUT, BUDG), and QC ids are fixed to the 16 brief capabilities. Nothing says which area the skeleton's trivial slice takes (version answer, usage refusal). Read literally, §7 then requires BLOCKED ("context.md lacks ... the area codes you need") in every Foundation whose product areas are features.

### FX-68 · major · tally · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table, row QC-14 (Profiles: all)

QC-14 secret canaries is listed for 'all' profiles. absd/playbook/testing/ci-and-release-gates.md GATE-13 applies only when 'the product or its pipeline handles any secret or credential'. absd/playbook/process/definition-of-done.md DOD-5 row 5 conditions the canary control on 'when the product has secrets'. The files disagree for a product with no secrets.

### FX-69 · major · tally · C001 Foundation · analyst 3

- Kit file: .claude/agents/analyst.md — §9 Reply format vs absd/templates/briefs/invocation-brief.md 'Reply format' vs absd/RULES.md §8

Three reply contracts disagree. The manual has Status COMPLETE|BLOCKED|IN-PROGRESS and no findings line. The brief template has COMPLETE-WITH-CONFLICTS and HALTED plus 'Findings: Critical/Major/Minor'. RULES §8 requires 'finding counts by severity'. The Manager's brief carried the template's format, so the worker cannot satisfy all three.

### FX-70 · major · tally · C001 Foundation · analyst 3

- Kit file: absd/playbook/testing/external-facts.md — EXT-3 Applies when; with foundation-brief step 2a, QC-10 'products with external systems', analyst.md 4.4-10

No rule says whether build and install platforms of a locally installed cli or library count as external systems (here pip, venv and Python 3.13 per OS, and git tags). If they do, they need fact sheets, contract tests, live checks and a Facts step before Design. EXT-3 applies to 'platform APIs or custom deploy and ops automation'; step 2a only 'if the skeleton or a selected QC touches an external system'. analyst.md 4.4-10 sends any new fact to Facts mode before Design, while brd §6 and the brief name Tester Baseline. The analyst has to guess, and the guess decides the route (step 2a) and whether QC-10 applies.

### FX-71 · major · tally · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.2 step 3 and §5.1 Delta row (also the brief's 'untouched sections "Unchanged — <reason>"')

The Delta rules assume the delta is written over an archived analysis. A Gate 1 round inside the same cycle edits the cycle's only analysis.md. Taken literally, replacing each untouched section with 'Unchanged — <reason>' would delete content that the Designer, Architect, Tester and trace_check still need. The fallback ('one line citing the archived copy') has no archived copy to cite.

### FX-72 · major · tally · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.2 step 4 and §5.1 Statuses

The kit does not say what 'changed' is measured against in a Gate 1 round of the same cycle: the catalogue and archive, or the previous round. Marking a heading 'changed' implies a §15 Change row for a requirement the catalogue does not hold yet, while the brief asks for changed ACs to have Status 'changed'.

### FX-73 · major · tally · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §5.1 '≤ 20k tokens; beyond, an index … plus parts' and §6.1 '≤ 20k tokens or split' (RULES §9)

No measure or tool is defined for an artifact's token size; kit_lint's ~4 chars/token rule covers kit files only. The Analyst may run only git and trace_check, so the check cannot be done mechanically. The round-1 file (64.5 KB, about 27k tokens by a real tokenizer) passed Gate 1 with no size check at all. The control does not exist in practice.

### FX-74 · major · tally · C001 Foundation · analyst 7

- Kit file: absd/tooling/trace_check.py — gate gate1, check "every requirement defined in analysis.md is defined in catalogue.md"; cited as the Catalogue apply check by .claude/agents/analyst.md 4.3 step 4, 6.2 and .claude/agents/manager.md 6.2

gate1 is the only mechanical check of Catalogue apply, and the user's D-15 approval depends on it. It only checks that each analysis id has a row that is not removed or retired. Tested on a scratch copy of the catalogue in which QC-2's Story was changed, every Status read `Active`, QC-3 was duplicated and an invented QC-99 was added: gate1 still said PASS 3/3. So a wrong apply (mistyped story, extra row, duplicate, Status not exactly `active`) passes the gate the Manager writes G1 PASS on, and the check fails without anyone noticing. ABSD:TRACE-2 assigns the duplicate check to traceability_report, which is not run at Gate 1.

### FX-75 · major · tally · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — 4.0 ("Catalogue apply: Gate 1 approved in the ledger") and 4.3 step 1 ("ledger shows Gate 1 approved at a SHA … git diff <sha> -- analysis.md"); vs .claude/agents/manager.md 6.2 checklist ("Approved → analyst · catalogue apply → gate1 all ✓ → ledger PASS") and absd/templates/artifacts/cycle.md Gate ledger

The analyst's precondition reads a ledger state the kit never defines. The Manager writes PASS only after the apply, and the ledger has no APPROVED verdict. The ledger's only SHA column is the Product SHA (1df0aaa, the last commit outside absd-project/), which is older than analysis.md. Read literally, `git diff 1df0aaa -- analysis.md` is not empty and the step BLOCKS. The step works only because the Manager improvised the verdict text "APPROVED by the user (D-15) at analysis.md @5390af5" (lesson tally-L9).

### FX-76 · major · tally · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — 4.3 step 1 and checklist 6.2 ("analysis.md unchanged since")

The unchanged-since-approval check diffs only absd-project/working/analysis.md. Section 5.1 lets the artifact be split into parts under analysis/ (as here), and trace_check reads them. A change to a part after the Gate 1 approval would pass the precondition without anyone noticing.

### FX-77 · major · tally · C001 Foundation · designer 11

- Kit file: absd/tooling/trace_check.py — gate_ux() and the usage header 'gate-ux'; vs absd/playbook/design/excellence.md DSN-13 Check and DSN-16 Check

DSN-13's Check says every analysis.md failure mode has a row, verified by trace_check. DSN-16's Check says gate-ux leaves no requirement unmapped. gate-ux does neither. It checks only two things: that each UJ/SCR appears in Traceability, and that each requirement design.md mentions exists in the catalogue. A design.md that leaves out an in-scope AC or a §7 failure mode still passes. The SCR check also passes with 0 ids checked. The control is weaker than the playbook says and gives no warning.

### FX-78 · major · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §6.3 cli checklist ('human output by default and a stable `--json`'); absd/playbook/design/rubric-and-qa.md DSN-17

DSN-17 and the 6.3 checklist require a stable `--json` for every cli, with no Applies-when condition. RULES rule 8 says nothing beyond analysis.md. The C001 skeleton has no machine-output requirement: JSON is area OUT, built in C002 (D-3). Both rules cannot be met at once.

### FX-79 · major · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.1 step 3, §5.1 (public surface = cli, http-api, library); absd/playbook/design/rubric-and-qa.md DSN-17/DSN-18

The kit does not say who designs the experience of owner-facing operational tooling: the QC-8 build/smoke/publish/withdraw refusals, and the runtime-matrix 'not in force' and 'not yet run' outcomes. The analysis gives the wording to the Designer, but the mechanism belongs to the Architect (OPS), and DSN-17/18 cover only the product's own public surface. The Designer has to guess both the boundary and how much to design.

### FX-80 · major · tally · C001 Foundation · manager 1

- Kit file: absd/templates/project/foundation-brief.md — Steps 1–2; also .claude/agents/manager.md 4.6 and .claude/agents/analyst.md §2 / 4.1 / 4.4

Mode B never says whether the Manager writes brd.md. The Analyst's §2 table says Foundation analysis starts after the 'context.md frame', but Analyze 4.1 reads brd.md section by section and 4.4 makes 'brd.md missing' a BLOCKED condition. The whole-product actor × capability matrix needs the user's intent from somewhere.

### FX-81 · major · tally · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 4.6 Mode B — 'Brownfield: … step 5 adds tester · Baseline'

Disagrees with foundation-brief.md step 5 and tester.md §2 ('step 5 = Baseline (fills the seeded TESTING.md), then Plan & Bind'), which put Baseline in every Foundation, greenfield included. Reading the manager manual alone, greenfield would skip the step that fills TESTING.md.

### FX-82 · major · tally · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 4.13 Counters and escalation; 6.2 last item (Facts result → analyst · Delta → G1)

Gate 1 reached its last round (3/3) on a Facts Delta that had no Analyst ✗ (follows tally-L7 and tally-L14). The Facts result opened user-owned readings (A-8, A-9) that only the user can sign. Any answer other than "as written" adds an AC, so it needs a fourth round, which means escalation. The round limit puts a process cost on a product choice the user is entitled to make freely, and the kit gives no route for a user-owned assumption that arrives in the last round.

### FX-83 · major · tally · C001 Foundation · manager 12

- Kit file: absd/playbook/design/rubric-and-qa.md — DSN-17 rule text; .claude/agents/manager.md 6.3 cli item

DSN-17 requires 'a stable documented --json' for every cli, and manager.md 6.3 lists --json as a Gate UX checklist item. Neither gives an exception for when no requirement asks for machine output, so the rule conflicts with RULES rule 8 (YAGNI). The Designer left --json out ('reserved for C002') and the Manager had to decide whether that counts as present.

### FX-84 · major · tally · C001 Foundation · manager 12

- Kit file: absd/templates/artifacts/design.md — §0.2 Upstream issues, Owner column; .claude/agents/designer.md §9 reply line 'upstream issues <n> → Analyst / user'; .claude/agents/manager.md 6.3 and 7

designer.md §2 sends an unrecorded external answer to 'Tester Facts', but the design skeleton's Owner column and the Designer's reply format allow only Analyst or user. manager.md has no route for a design upstream issue owned by the Tester, and does not say whether a non-blocking one must be settled before Gate UX or the Architect.

### FX-85 · major · tally · C001 Foundation · manager 13

- Kit file: absd/templates/project/foundation-brief.md — step 4 "quality gates & CI, split into Builder and Tester workflow files"; also .claude/agents/architect.md §5 §12, absd/templates/project/context.md §4 "CI job" column, absd/RULES.md §5 and .claude/agents/manager.md 4.10 step 4 "when CI is green at the Gate 3 product SHA"

The kit assumes a CI service throughout: workflow files per owner, a CI job column, a merge condition of "CI green", and GATE-14 "CI re-runs them". This product has none (the owner's notes; RISK-2). RULES §6 allows local evidence, but no kit file says what replaces a workflow file or the "CI green" merge condition for a local-only product. The Architect has to guess at step 4, and the Manager will have to guess at merge.

### FX-86 · major · tally · C001 Foundation · manager 2

- Kit file: absd/playbook/process/definition-of-done.md — DOD-5 row 8; also absd/playbook/testing/ci-and-release-gates.md GATE-14, absd/RULES.md §5 merge rule, .claude/agents/manager.md 4.10 step 4 and §6, foundation-brief QC-13

The kit assumes every product has a CI service. It says 'ownership_check and trace_check in CI', 'CI re-runs them', and that the merge needs 'CI green at the Gate 3 product SHA'. There is no N/A clause or local-equivalent clause for a product whose owner says there is no CI service. RULES §6 accepts local output as evidence, but the merge precondition and DOD-5 row 8 name CI literally, so this product cannot meet them as written.

### FX-87 · major · tally · C001 Foundation · manager 2

- Kit file: .claude/agents/analyst.md — §2 route table row B vs §3 item 3 and §4.7 BLOCKED list; absd/templates/project/foundation-brief.md step 1; absd/templates/artifacts/brd.md header

These files disagree on whether Mode B has a brd.md. Analyst §2 says Analyze (Foundation) starts after the 'context.md frame', and the foundation brief names no brd.md. Yet analyst §3 reads brd.md whole and §4.7 BLOCKs when 'brd.md or defect.md [is] missing'. The brd skeleton header also offers only 'Mode: F/S/C', with no B. Without a brd the Foundation Analyst would block, and with one the header has no valid mode.

### FX-88 · major · tally · C001 Foundation · manager 3

- Kit file: absd/tooling/ownership_check.py — line 99 `from absd_sync import SEEDS`; with .claude/agents/manager.md 4.5 (clean tree before delegation) and absd/templates/project (no .gitignore seed)

Running the mandated ownership_check imports absd_sync and writes absd/tooling/__pycache__/absd_sync.cpython-313.pyc inside the vendored kit. The tree is then dirty (`git status --porcelain` not empty), which the manual requires to be clean at every hand-off. The previous Manager turn ended with this untracked directory. `absd_sync.py check` reports 0 extra, so the kit check does not show it. The install seeds no .gitignore, and the settings allow list (`Bash(python3 absd/tooling/...:*)`) does not cover `python3 -B` or PYTHONDONTWRITEBYTECODE=1.

### FX-89 · major · tally · C001 Foundation · manager 4

- Kit file: absd/tooling/trace_check.py — gate1 preset (catalogue coverage check) vs .claude/agents/manager.md §6 intro ('any ✗ fails the gate') and §6.2 last bullet; absd/playbook/process/requirements.md ELIC-20 Check

gate1 requires every analysis requirement to be in catalogue.md, but Catalogue apply happens only after the user's Gate 1 sign-off (manager.md 6.2), and ELIC-20's Check reads 'gate1 passes; the delta lands … after Gate 1'. That is circular. Read literally, §6 makes round 1 a FAIL that returns to the Analyst, even though nothing is wrong.

### FX-90 · major · tally · C001 Foundation · manager 4

- Kit file: .claude/agents/manager.md — §6.2 Gate 1 checklist (bullets 4–6)

Blocking OQs must be answered as D-n before Gate 1, and the user must sign off the matrix. The manual does not say how the answers get into analysis.md when they change ACs and matrix cells (here QC-8.AC7, QC-16, Table B 'Undecided — OQ-7'). It also does not say whether the sign-off comes before or after that change. Only a Facts result has a stated 'analyst · Delta → G1' route. Folding in the user's own answers then uses up a gate revision round (counted toward the 3-round limit) even though no defect was found.

### FX-91 · major · tally · C001 Foundation · manager 4

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table, row QC-14 (Profiles: all)

QC-14 secret canaries is listed for 'all' profiles, but ABSD:GATE-13 (absd/playbook/testing/ci-and-release-gates.md) applies only when the product or pipeline handles a secret. DOD-5 row 5 has the same condition. Two kit files disagree. The Analyst raised it.

### FX-92 · major · tally · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — §9 Reply format ("Paths and ids, never contents or paraphrase") vs §6.2 item 6 ("The user saw the matrix … and signed off") and absd/playbook/process/requirements.md ELIC-21 ("the Manager shows the user the matrix …")

Two kit rules disagree: following §9, the Manager's round-1 sign-off request gave only section references, so the user approved the matrix, value check and inventory without seeing them (the user said so explicitly). The ELIC-21 control quietly turned into approving a file reference, and 6.2's 'the user saw' tick cannot honestly be made.

### FX-93 · major · tally · C001 Foundation · manager 6

- Kit file: .claude/agents/manager.md — §9 Reply format ("≤ 15 lines … Paths and ids, never contents or paraphrase") vs §6.2 ("The user saw the matrix …") and absd/playbook/process/requirements.md ELIC-21

This happened again in round 2. Gate 1 needs the user to see the cells they sign, but the reply format forbids contents and caps the message at 15 lines. Round 2 had 3 cells, 3 rows and 2 assumptions, each with before and after contents, so it could not fit both rules.

### FX-94 · major · tally · C001 Foundation · manager 6

- Kit file: absd/tooling/trace_check.py — gate gate1, check "every requirement defined in analysis.md is defined in catalogue.md"; manager.md 6.2 last item

This happened again in round 2. gate1 checks the requirements against catalogue.md, but manager.md 6.2 has the catalogue updated (Catalogue apply) only after the user signs off. So gate1 cannot be all ✓ at the moment the Manager asks for sign-off, and every Gate 1 round shows a ✗ that is expected.

### FX-95 · major · tally · C001 Foundation · manager 7

- Kit file: .claude/agents/analyst.md — §2 table (Catalogue apply precondition "Gate 1 approved"), 4.0, 4.3 step 1, checklist 6.2 vs .claude/agents/manager.md 6.2 last item and absd/templates/artifacts/cycle.md Gate ledger

The Analyst refuses Catalogue apply (BLOCKED) unless "the ledger shows Gate 1 approved at a SHA". The Manager's checklist writes "ledger PASS at that SHA" only after Catalogue apply and gate1 all ✓. The cycle.md skeleton defines no Verdict word for the state between the user's sign-off and PASS. Read literally (approved = PASS), this deadlocks: no apply without PASS, and no PASS without the apply.

### FX-96 · major · tally · C001 Foundation · manager 8

- Kit file: absd/templates/artifacts/cycle.md — Gate ledger columns; .claude/agents/analyst.md 4.3 step 1

analyst.md 4.3 step 1 requires the ledger to show 'Gate 1 approved at a SHA', but the Gate ledger's only SHA column is the Product SHA: the last commit outside absd-project/, here a CLAUDE.md commit. That SHA identifies no revision of analysis.md, so the Analyst had to guess which SHA was approved.

### FX-97 · major · tally · C001 Foundation · manager 8

- Kit file: absd/tooling/trace_check.py — gate gate1, check 'every requirement defined in analysis.md is defined in catalogue.md'

After Catalogue apply, gate1 checks only that each requirement id exists in catalogue.md. It never checks that the applied rows (story, role, status) equal the approved analysis §15 delta, so a stale or mistyped story passes the gate silently.

### FX-98 · major · tally · C001 Foundation · manager 8

- Kit file: .claude/agents/tester.md — 4.5 Facts; foundation-brief step 2a; absd/playbook/testing/external-facts.md EXT-2

Facts runs right after Gate 1 and must commit recordings 'in the test tree'. The test tree's paths and owners arrive only with ADR-002 after Gate 2R, and until then context.md §3 holds template placeholders (only docs/testing/** is a real row). Recordings therefore land in paths that ownership_check reports as unowned, and ADR-002 may later move them. The kit does not say where recordings go before ADR-002.

### FX-99 · major · tally · C001 Foundation · manager 9

- Kit file: .claude/agents/manager.md — 6.2 last item vs .claude/agents/analyst.md §2 route table and 4.2 step 2

The two manuals give different triggers for a Delta after Facts. manager.md says "a Facts result that changes a requirement → analyst · Delta → G1". analyst.md says "a Tester Facts result that changes a §7 fact". Every Facts run turns §7 statuses from UNVERIFIED to VERIFIED, so the analyst.md trigger always fires. Each such Delta costs a Gate 1 round. Add tally-L7 (a round spent folding in the user's answers) and C001's Gate 1 reaches round 3/3 without a single Analyst ✗, with no round left for a real defect.

### FX-100 · major · tally · C001 Foundation · manager 9

- Kit file: .claude/agents/manager.md — 4.13 Counters and escalation; RULES §2 Limits

Nothing says whether a Gate 1 round that only folds in a Facts result (or the user's answers to blocking OQs) counts toward the 3-round limit. Mode B/F with blocking OQs plus Facts uses up all three G1 rounds by design. The next real G1 failure would force an escalation that no defect caused.

### FX-101 · major · tally · C001 Foundation · tester 8

- Kit file: absd/templates/project/EXTERNAL-FACTS.md — system section table, rows EXT-<SYS>-1 … EXT-<SYS>-12 (vs absd/playbook/testing/external-facts.md EXT-2 and analysis.md §7 reservation)

The seed numbers EXT ids by checklist row (EXT-<SYS>-2 = time zone, -3 = calendar …), but the Analyst reserves ids per needed fact as highest + 1 (EXT-PIP-2 = the Requires-Python refusal). The two numbering schemes collide, and the template gives no form for a checklist row that is N/A or is already covered by a reserved fact.

### FX-102 · major · tally · C001 Foundation · tester 8

- Kit file: absd/tooling/trace_check.py — verified_facts() (about line 537), and the EXT-2 rules in absd/playbook/testing/external-facts.md

An id counts as VERIFIED when any Status cell of any row whose first cell is that id starts with 'verified'. So a fact verified on one runtime class and unrecordable on another, written 'VERIFIED on Linux; UNVERIFIED on macOS' or given as a second sub-row, would pass as a FACT: source for the macOS tests. No kit rule says how to record a fact that is verifiable for one class and not another. This is a silent-pass risk.

### FX-103 · major · tally · C001 Foundation · tester 8

- Kit file: .claude/agents/tester.md — §4.5 step 4 ('No access or credential → BLOCKED + proposed RISK') vs §4.5 'Done when' and ABSD:EXT-2

The manual does not say whether partial access blocks the run: Linux recordable, macOS not, and the missing Mac is already accepted as RISK-1/D-8. Step 4 reads BLOCKED, while 'Done when each in-scope fact has a row with status and evidence' and EXT-2 (UNVERIFIED is a valid status) read COMPLETE.

### FX-104 · major · tally · setup

- Kit file: absd/tooling/ownership_hook.py — module docstring / sibling import of ownership_check.py (which imports absd_sync.py); absd_sync.py install (seeded files)

The PreToolUse ownership hook runs on every agent Write/Edit. Its sibling imports write absd/tooling/__pycache__/ownership_check.cpython-313.pyc and absd_sync.cpython-313.pyc inside the vendored kit. install seeds no .gitignore, and no kit file mentions one. I tried this in a throwaway clone: after one hook run, a builder commit made with `git add -A` included the two .pyc files, and ownership_check.py reported 2 violations ('changed absd/tooling/__pycache__/..., owned by kit (built-in: absd/)'). So the kit's own tooling plants files that its other control then flags. Meanwhile `absd_sync.py check` still says '0 extra' with those files committed, so the two tools disagree about whether stray files under absd/ matter. The owner's venv (.venv) also has no ignore guidance.

### FX-105 · minor · meter · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table, row QC-11

QC-11 bundles "one foreign time zone/locale project" with device and runtime classes, and limits it to web-ui, native-app, cli and library. ABSD:VAR-8 and RULES Q7 need the foreign-zone run for any product with date rules. A data-pipeline or http-api product with a DST-sensitive day rule (Meter) therefore gets no Foundation QC for it.

### FX-106 · minor · meter · C001 Foundation · analyst 3

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block vs .claude/agents/analyst.md §9

The brief template's reply uses Status values COMPLETE | COMPLETE-WITH-CONFLICTS | HALTED | BLOCKED | IN-PROGRESS and a Findings line. The analyst manual's reply uses COMPLETE | BLOCKED | IN-PROGRESS and different lines (Mode, Counts, Facts needed, …). The Manager asks for both, still within 15 lines.

### FX-107 · minor · meter · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — rows QC-10 ("live checks nightly") and QC-13 ("in CI"); absd/playbook/process/definition-of-done.md DOD-5 row 8 ("checks in CI")

These QCs and DoD rows assume a CI service and a nightly scheduler. They give no wording or fallback for a product that has neither (Meter: RISK-1).

### FX-108 · minor · meter · C001 Foundation · analyst 3

- Kit file: .claude/agents/analyst.md — §4.4 rule 14; absd/templates/artifacts/analysis.md §1.4 Expected output ("rows and fields exactly as produced")

The expected-output table must hold fields "exactly as produced", but for a machine output whose layout the team still designs (D-11, the Designer's data contract at step 3), the field names and order do not exist before Gate UX.

### FX-109 · minor · meter · C001 Foundation · analyst 3

- Kit file: absd/templates/artifacts/analysis.md — §1 structure; .claude/agents/analyst.md §4.1 Foundation

The template has no place for QC-n requirements. They are neither product functional requirements nor NF-shaped, yet trace_check treats them as functional and needs ACs. There is also no area code for operability requirements that are not QCs (version output, log levels, alerting); the Manager's area codes do not cover them.

### FX-110 · minor · meter · C001 Foundation · analyst 3

- Kit file: .claude/agents/analyst.md — §4.1 Done when ("every brd sentence traced") and §6.1 Fidelity vs §4.4 rule 15 / ABSD:TRACE-10

Traceability rows must start with a requirement id, so a brd item that is deliberately not built in this cycle (INGEST, AGG, OUTF content, the speed target) cannot appear there. The kit gives it no other home.

### FX-111 · minor · meter · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §5.1 statuses; §4.2 step 4

The requirement/AC status vocabulary (new | changed | removed | unchanged) defines no baseline for an in-cycle Gate 1 round. A revised AC of a requirement that is not yet in the catalogue is both 'new' (vs the catalogue) and 'changed' (vs round 1). Marking the requirement 'changed' would demand a §15 Change row for an id the catalogue lacks.

### FX-112 · minor · meter · C001 Foundation · analyst 5

- Kit file: absd/RULES.md — §2 Limits (3 revision rounds per gate) with analyst.md §7 (contradiction → blocking §12 question)

Each Gate 1 round that applies user answers can surface a new blocking contradiction, and even a user answer that just confirms the text as written needs a full analyst Delta round to change a status cell. Two rounds of answers can use up the 3-round limit. The kit has no lighter path for the Manager to record a confirming answer.

### FX-113 · minor · meter · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.0 'Commands only for git … and trace_check' vs §6.1 'counts recounted … ≤ 20k tokens or split'

The self-verification asks for recounted §16 counts and a size check, but the manual permits no command that counts AC rows or measures file size. Bulk edits to large tables also fit badly with Edit-only.

### FX-114 · minor · meter · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.0 'Commit after each Progress group'; skeleton Progress line

The Progress groups are designed for Analyze. For a Delta the manual does not say whether to reset the Progress line or how many intermediate commits to make (9 groups would mean 9 commits for a small revision).

### FX-115 · minor · meter · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §2 needs table (EXT row) and §4.4 rule 10; absd/playbook/testing/external-facts.md EXT-4

A person's statement about a platform that is unreachable from the repository (the production server) must get an EXT id and a verification owner (the Tester's Facts mode). Facts mode cannot record a real response from that platform, though, and the kit does not name who can actually verify it (the user with server access) or what Facts records then.

### FX-116 · minor · meter · C001 Foundation · analyst 7

- Kit file: absd/templates/artifacts/analysis.md — §0 Routed items answered

§0 has no structure for two things a repeat Gate 1 round needs. (1) The list of §2/§4/§6 cells changed since the last sign-off (Was → now), which ELIC-21 re-sign-off and the Manager's diff check rely on. (2) Grouping rows by round. Each round invents its own ad-hoc table, and earlier rounds' rows (e.g. the D-19 row's "§14 #2 with OQ-17, blocking Gate 1") read as current unless annotated.

### FX-117 · minor · meter · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — §4.0 (Commit after each Progress group; Resume rule) and the header Progress line

For a Delta on an artifact that is already COMPLETE, the manual does not say whether the Progress line is reset. The Resume rule covers only interrupted runs. For a citations-only delta, nine Progress groups would mean up to nine near-empty commits: pointless work and noise in history.

### FX-118 · minor · meter · C001 Foundation · analyst 7

- Kit file: absd/RULES.md — §2 Limits; with .claude/agents/analyst.md §2 table (a Gate 1 round is Delta)

This whole run only recorded two user answers (D-20 = keep as written; D-21 = a rule for a later cycle). It changed no requirement, AC, id or catalogue row, yet it uses G1 round 3/3, the last round, so any small slip escalates to the user (same as meter-L11, now seen from the Analyst side). The work was rewriting status cells and citations across about 30 places in three files.

### FX-119 · minor · meter · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — §9 Reply format, Counts and Sign-off needed lines

Counts ("functional n (new n · changed n …)") does not say whether it counts the whole artifact or the current round for an in-place revision. "Sign-off needed: §2 matrix (changed cells n)" cannot say that the changed cells are already covered by an earlier sign-off's stated reading. Without that, the Manager cannot tell from the reply whether a new user question is needed.

### FX-120 · minor · meter · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — §4.0 "Commands only for git … and trace_check"; with absd/tooling/ownership_hook.py docstring

Editing very long Markdown table rows (≈30 exact replacements) with single Edit calls is fragile, and the manual allows no other command. The ownership hook guards only Write/Edit; Bash writes rely on ownership_check in history (documented). So the command restriction has no write-time enforcement, and the manual offers no allowed way to do bulk edits safely.

### FX-121 · minor · meter · C001 Foundation · analyst 8

- Kit file: .claude/agents/analyst.md — 4.0 last bullet vs 4.3 step 3 / 6.2

Catalogue apply requires checking that the catalogue diff equals the §15 rows exactly and that no id is duplicated, but 4.0 allows only git and trace_check.py commands, and trace_check gate1 checks neither (it only checks that every analysis requirement is defined in the catalogue). The kit tool that detects duplicates, traceability_report.py (ABSD:TRACE-2 Check: 'exits 2 on a duplicate id'), is outside the analyst's allowed commands, and `git grep` has no -x whole-line match. The verification method had to be improvised. The previous analyst invocation deviated in the same area (python3 through Bash, lesson meter-L13).

### FX-122 · minor · meter · C001 Foundation · analyst 8

- Kit file: .claude/agents/analyst.md — 4.3 step 2 'append in id order within the area'

'Id order' is not defined. It could be numeric (QC-2 before QC-10) or lexical (QC-10 before QC-2). The manual also doesn't say how the series of one area interleave (AREA-n, AREA-NF-n, AREA-BR-n) or how areas are ordered against each other on a first apply. It also doesn't say whether the order of the §15 rows (which ELIC-20 calls 'exactly as they will read') governs instead.

### FX-123 · minor · meter · C001 Foundation · analyst 8

- Kit file: .claude/agents/analyst.md — 4.0 commit bullet vs absd/playbook/engineering/code-quality.md CODE-14

analyst.md 4.0 (and the brief) say the trailers ABSD-Agent and ABSD-Cycle are 'the single final paragraph'. CODE-14 says that paragraph also holds 'any co-author or session lines together'. The session's attribution rule asks for Co-Authored-By and Claude-Session lines. Read literally, the manual leaves no place for them without breaking either 'single final paragraph' or the attribution rule.

### FX-124 · minor · meter · C001 Foundation · analyst 8

- Kit file: .claude/agents/analyst.md — §9 reply format vs absd/RULES.md §8

RULES §8 says workers reply with 'finding counts by severity', but analyst.md §9 has no Findings line. The §9 template is also written for Analyze and Delta: the Counts, Facts needed and Sign-off needed lines have no stated meaning in Catalogue apply mode.

### FX-125 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/tooling/traceability_report.py — line 59, TC_TOKEN = \bTC-\d{4,}\b

Go rewrites spaces in subtest names to '_'. So 'TC-0042 [OUTF-1] …' becomes 'TC-0042_[OUTF-1]_…', which the word-boundary match does not find (verified: TestRun/TC-0042_[OUTF-1]_x → no TC). Yet the tool's header lists go-junit-report and gotestsum as supported writers. A Go suite would silently report planned TCs as missing.

### FX-126 · minor · meter · C001 Foundation · architect 13

- Kit file: .claude/agents/architect.md — §4.0 Every run, the 'Commands only to …' list

The list allows reading history, probing outside the repo, trace_check.py and commit. It omits writing the absd-project/working/evidence/architect/ files the brief asks for, and running ownership_check.py and absd_sync.py check to confirm the hand-off.

### FX-127 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/playbook/engineering/architecture.md — ARCH-15 and skeleton §4 (absd/templates/artifacts/architecture.md)

ARCH-15 applies when 'the product owns persistent state', but its required content (column types, indexes, migrations generated by a tool) is database-shaped. For write-once files kept forever, the rule needed interpretation; this is the same undefined term as lesson meter-L5.

### FX-128 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/playbook/testing/nonfunctional.md — OPS-3 (exit 2 'could not run' keeps the deploy, unverified) vs absd/playbook/testing/end-to-end.md E2E-16

OPS-3's three-way outcome, where 'could not run' keeps the deploy marked unverified, conflicts with the gated QC-8 ('on any failed check, rolls back') and the design's three deploy messages. The kit gives no precedence.

### FX-129 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/playbook/testing/load-and-compatibility.md — PERF-1 Applies when ('always for lists, search, reports and batches') and threshold ('none = a spec defect at Plan & Bind')

A Foundation batch that does no per-item work (OUTF-1 reads no content; the analysis states no C001 speed target) is forced to choose between a spec defect and an argued N/A.

### FX-130 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/tooling/trace_check.py — gate gate2, the 'every EXT referenced in analysis.md' check

gate2 checks only the EXT ids the analysis references. Ids added later by tester · Facts (EXT-AMPERA-14…16, EXT-SERVER-7, -8) are not checked mechanically, so the control is partial for a Foundation where Facts runs after Gate 1.

### FX-131 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/templates/artifacts/architecture.md — §0.1 'Statement (verbatim)' and the §5.0 'Public names (cli, http-api, library …)' table

Quoting every D-n verbatim costs about 3k tokens in a Foundation with 30 decisions. The §5.0 public-names table (and ARCH-25's naming clause) covers only cli, http-api and library, yet design §17 asks Gate 2 to bind data-pipeline names: binary, cron entry, deploy command, settings, log destination, version form, check names, install location (meter-L24).

### FX-132 · minor · meter · C001 Foundation · architect 13

- Kit file: .claude/agents/architect.md — §4.3 ADR-002 owner table (builder / tester / shared / never listed)

Repository-hygiene files such as .gitignore fit none of the listed owner categories, though they affect the build. A build from a tree with untracked run or test outputs reports vcs.modified=true (meter-L1).

### FX-133 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/templates/project/context.md — §2–§4 placeholders and the 25 KB budget (RULES §9); foundation brief step 1 'copies ADR-001/002/003 into context.md §2–§4'

context.md was at 23.8 KB before Gate 2R. Copying even compact ADR-001/002/003 blocks verbatim takes it to about 27.4 KB, so a Foundation with many decisions cannot hold the mandated copies within budget without trimming other living content.

### FX-134 · minor · meter · C001 Foundation · architect 13

- Kit file: absd/playbook/testing/access-visibility.md — ACCESS-2 principal list vs D-13 operator actions

D-13 makes deploying and rolling back 'operator actions' of a team member who is not a third principal. The kit's principal dimension has no slot for an operator action performed by a non-principal, so who runs the deploy's operations in the matrix had to be decided.

### FX-135 · minor · meter · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §8 rule 2 (naming exception: cli, http-api, library only); absd/playbook/design/rubric-and-qa.md DSN-18 naming clause

For data-pipeline the manual lets the Designer name machine outputs ('shape and names', §5.1). It is silent on who names the operator-facing surface that the human copy must quote verbatim: the settings (OUTF-1.AC7 'naming the missing drop-location setting'), the binary and cron entry the runbook needs, the deploy command and the QC-8 check names. It also does not say whether the Designer designs the human-facing output of operator tooling (the QC-8 deploy report), which LOC-10 requires to come from the copy deck.

### FX-136 · minor · meter · C001 Foundation · designer 11

- Kit file: absd/templates/artifacts/design.md — Progress line; §3 journey table columns; with .claude/agents/designer.md §4.0 'Commit after each Progress group'

The Progress line has no item for §22 Traceability. Committing after each group forces separate commits for groups that are entirely N/A for a machine-only profile (4–6, 7–10, contrast), which is pointless work. The journey table's 'After: screen + focused element', interruptions and keyboard-path parts fit only screens.

### FX-137 · minor · meter · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.0 'Commands only to: read history; run trace_check.py; view, crop, scale or hash images and golden files; compute contrast, sizes and counts; commit'

LOC-2, LOC-4 and LOC-5 literal examples for a product that depends on a time zone have to be computed from the tz database. The manual forbids estimated contrast but says nothing equivalent for time literals. Verifying the contract's byte form, SHA-256 and JSON parsing also needs a script. Neither is on the allowed command list.

### FX-138 · minor · meter · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.2 step 1 and Done line ('filled with measured values'), §6.4

Design System mode is written for visual profiles (colour ratios, type scale, spacing, motion, breakpoints, components). For a product that is data-pipeline only, it does not say what a 'measured value' is or which §6.4 items apply.

### FX-139 · minor · meter · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §5.2

'Keep only the declared profiles' sections' and 'add ## 8. Protected screens register' disagree for a product without screens.

### FX-140 · minor · meter · C001 Foundation · designer 11

- Kit file: absd/playbook/testing/nonfunctional.md — VIS-3; with .claude/agents/designer.md §4.3 and design.md §18 ('where TESTING.md marks them')

Golden human-facing outputs are protected 'where TESTING.md marks them', but TESTING.md is filled at Plan & Bind (Foundation step 5), after Design (step 3). At Design time nothing is marked yet.

### FX-141 · minor · meter · C001 Foundation · designer 11

- Kit file: absd/RULES.md — §9 size budgets

Budgets are given in tokens, with no counting method. design.md measures about 17.8k by characters/4 and about 19.3k by a word-based estimate, so whether to split it into parts is a guess near the 20k limit.

### FX-142 · minor · meter · C001 Foundation · designer 11

- Kit file: absd/templates/project/context.md — §5 line 68 ('languages: <…>')

The languages field is framed for UIs. For this machine-only product it was filled 'languages: none — machine-read output', although the failure mail and the deploy report are read by people (D-10). The template does not prompt for the language of human-facing outputs of machine profiles.

### FX-143 · minor · meter · C001 Foundation · manager 1

- Kit file: absd/templates/project/foundation-brief.md — Steps table, step 5 ('Baseline, then Plan & Bind')

The foundation brief lists a Tester Baseline unconditionally in step 5. manager.md 4.6 adds Baseline for brownfield only. On greenfield there is nothing to baseline, so the two files disagree.

### FX-144 · minor · meter · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 6.1 Cycle start, item 2 (last nightly and live contract runs green)

No N/A case for a Foundation cycle, where no suite or nightly job exists yet. Read literally, 'not run yet → trigger it and wait' cannot be done.

### FX-145 · minor · meter · C001 Foundation · manager 1

- Kit file: absd/templates/artifacts/cycle.md — Mode S eligibility table; Close section heading

The skeleton requires the eleven Mode S answers and a Close keyed to DOD-2/DOD-4 rows, but Mode B uses neither. Its DoD is DOD-5, and manager.md 4.10 archive steps still cite DOD-2 row numbers. The skeleton gives no Mode B variant.

### FX-146 · minor · meter · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 4.1 Starting / 4.6 Mode B step 1

No guidance on what to do when the user refers to material ("my notes") that is not in the repository. Intake assumes the request content arrives in conversation.

### FX-147 · minor · meter · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 5.4 ("copying facts verbatim from gated artifacts")

Facts mode passes no gate (the route goes Facts → Design), yet the Tester's reply proposes changes to context §5, §6, §7 and §11. The only rule for copying into context.md requires a gated source, so these proposals have no defined path in.

### FX-148 · minor · meter · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 7 "Worker questions" bullet

Questions go "to the user verbatim → D-n → the owner re-invoked". That does not fit Facts questions meant for a third party (the vendor) or a server only the user can reach: the user's answer is a statement, not evidence (Q6, ABSD:EXT-2). The kit says neither whether such questions hold the route nor how a written spec or capture comes back to the Tester.

### FX-149 · minor · meter · C001 Foundation · manager 10

- Kit file: absd/tooling/trace_check.py — check --ids ext --referenced-in analysis.md,context.md

Ids the Tester adds at Facts (highest + 1) are by design not yet in analysis.md or context.md, so the Tester's own check at Facts exits 1 'expected'. It passes only after the Manager copies the ids into context §7, a later step the manuals do not name. This is the same order-dependence as gate1's catalogue check (meter-L7).

### FX-150 · minor · meter · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 6 ("Every gate, every route: trace_check gate <preset> and ownership_check …; record both in the gate ledger")

Facts (step 2a) is a route step without a gate. Whether its checks belong in the gate ledger is not stated, and there is no trace_check preset for Facts.

### FX-151 · minor · meter · C001 Foundation · manager 11

- Kit file: absd/templates/project/foundation-brief.md — Steps table, step 3 (Owner: Designer); manager.md 4.4 route table row B

Neither the foundation brief nor the Mode B route row names the Designer's mode. The cycle route row written from it said 'designer · Design', while designer.md §2 puts Foundation step 3 in the Design System mode.

### FX-152 · minor · meter · C001 Foundation · manager 11

- Kit file: .claude/agents/manager.md — §7 Worker questions; §4.2 step 5; brd skeleton §9 'Decisions (answered by the user only)'

The answers to external-fact questions for a third party are mostly 'I'll ask Ampera / can't capture now, no answer yet', plus one 'working assumption' about a field's meaning. The kit routes them as business answers → D-n, so brd §9 'Decisions' fills with six rows that decide nothing. The kit has no place for a user's working assumption about an external fact, other than an UNVERIFIED statement. It also does not say whether such answers close the pending question or keep it open.

### FX-153 · minor · meter · C001 Foundation · manager 12

- Kit file: .claude/agents/manager.md — 6.3 'Every UXQ/UXA has a default and impact; product questions answered by the user as D-n'

A UXA resting on an UNVERIFIED external fact (UXA-1: cron mails stderr, EXT-SERVER-3) is not a product question, and the user's statement cannot settle it (Q6). The checklist gives it no home: no RISK, no Facts route.

### FX-154 · minor · meter · C001 Foundation · manager 12

- Kit file: absd/playbook/design/rubric-and-qa.md — DSN-18 naming clause; .claude/agents/designer.md §8 rule 2

The Designer may name the public surface of cli, http-api and library only. For a data-pipeline nobody is told to name the settings, the entry point (binary and cron entry), the deploy command or the log destination, yet the copy deck quotes them in every failure message. Who binds those names, and when the copy gets them, is left implicit.

### FX-155 · minor · meter · C001 Foundation · manager 12

- Kit file: .claude/agents/manager.md — 6.3 vs designer.md 7 (UXQ answered at Gate UX)

Gate UX cannot pass on mechanical checks while any UXQ is unanswered, even a non-blocking one designed as its default. The kit implies, but never states, that an answer equal to the default needs no Designer delta (designer.md 7: 'a different answer arrives as a delta') and that design.md §21's Answer cell can then stay unfilled.

### FX-156 · minor · meter · C001 Foundation · manager 13

- Kit file: .claude/agents/designer.md — §7 UXQ bullet ("a different answer arrives as a delta"); manager.md 6.3

When the user picks a UXQ's designed default, the gated design.md keeps saying "pending UXQ-1" for good (header line and the §21 Answer cell "— pending; the user answers at Gate UX"). Only a different answer triggers a Designer delta, and the Manager may not write design.md (RULES rule 9). So the gated artifact never records the answer, and every later brief has to say to read the marks as answered.

### FX-157 · minor · meter · C001 Foundation · manager 13

- Kit file: .claude/agents/manager.md — 6.3 Gate UX; gate ledger convention in absd/templates/artifacts/cycle.md

The kit doesn't say how to record a Gate UX that was pending only on user answers, when those answers need no artifact change. Is closing it a new round or round 1's close at the same design SHA? (manager.md 6.2 has the same gap for G1, see meter-L7 and meter-L11.)

### FX-158 · minor · meter · C001 Foundation · manager 13

- Kit file: .claude/agents/manager.md — 5.4 ("≤ 25 KB (wc -c)"); 4.6 (ADR-002 table verbatim into §3, ADR-003 commands into §4); absd/RULES.md §9

The context.md budget doesn't say whether KB is 1000 or 1024 bytes, and no kit tool checks it. A greenfield Foundation's own frame (§1, §5–§7, §11 with nine RISKs, §14, §17) already reaches 23 772 bytes before §2–§4 get ADR-001, the ADR-002 table and the ADR-003 command table verbatim. So the verbatim-copy rule and the budget are likely to collide at step 4c.

### FX-159 · minor · meter · C001 Foundation · manager 14

- Kit file: absd/tooling/trace_check.py — gate2 → blocking_spec_defects; check 'no blocking upstream issue in architecture.md is open'

The check reports '(0 checked)' when §0.2 has 9 rows, 5 of them open, because it counts only rows whose Blocking cell says yes. The output reads as if the table was never parsed, so the Manager cannot tell 'no blocking row' from 'table not found' without reading the code.

### FX-160 · minor · meter · C001 Foundation · manager 14

- Kit file: absd/templates/artifacts/cycle.md — whole skeleton (Decisions, Pending routes, Gate ledger)

Midway through the Foundation (step 4 of 9), cycle.md is already about 65 KB (≈16k tokens), close to the RULES §9 artifact budget of 20k tokens. The skeleton has no index-plus-parts rule and no place to move closed Pending routes or old Decisions, yet manager.md 5.1 requires a row before every step takes effect.

### FX-161 · minor · meter · C001 Foundation · manager 14

- Kit file: .claude/agents/manager.md — 6.4 'an ADR with ≥ 2 options for each decision (ABSD:ARCH-22)'

The checklist does not exempt a choice the user has already fixed. ADR-001 records the language as 'Go — fixed by D-4; no alternative is open', which taken literally fails the 6.4 item.

### FX-162 · minor · meter · C001 Foundation · manager 2

- Kit file: absd/templates/artifacts/brd.md — Mode line 'F/S/C'; manager.md 4.2, 4.6 and 5.2

The kit never says whether Mode B writes a brd.md. Manager 4.2 and 5.2 and the skeleton scope brd to Modes F, S and C, and foundation-brief step 1 mentions only the context.md frame. Yet the Gate 1 sign-off line (ELIC-21, manager 6.2) lives in brd §9 and the Analyst reads brd.md whole, so the Foundation needs one.

### FX-163 · minor · meter · C001 Foundation · manager 2

- Kit file: absd/playbook/process/definition-of-done.md — DOD-5 row 1 (Data Volume Profile) vs ELIC-12 'max observed in the real source (not guessed)'

The frame the Manager writes in step 1 must include a Data Volume Profile with the maximum observed, but nothing is measured until tester · Facts (step 2a). Row 1 can only be completed after Facts, and the brief does not say the frame is revisited then.

### FX-164 · minor · meter · C001 Foundation · manager 2

- Kit file: absd/templates/project/context.md — §5 Clock/languages, §1 Audiences and devices, §7 'Facts (EXT ids)' column

These fields assume a human-facing UI and offer no n/a for machine-only profiles such as data-pipeline. §7 asks for EXT ids at frame time, but ELIC-10 has the Analyst reserve them only at Analyze.

### FX-165 · minor · meter · C001 Foundation · manager 2

- Kit file: absd/templates/artifacts/cycle.md — Invocation log / Resume point

There is no row type for intake question batches put to the user. The only durable memory of which batch is outstanding is the free-text Resume point, plus the OQ statuses in brd §10.

### FX-166 · minor · meter · C001 Foundation · manager 3

- Kit file: absd/templates/artifacts/brd.md — §9 Decisions column "Options shown" vs §10 Open questions; .claude/agents/manager.md 4.2 step 4 and §9

The Decisions table needs the options shown to the user, but nothing tells the Manager to save the options it sent in a question batch. §10 keeps only the question text, and the §9 reply format is never stored. So the turn that records the answers has to work the options back out from the letter the user picked ("B", "A, yes").

### FX-167 · minor · meter · C001 Foundation · manager 3

- Kit file: absd/templates/artifacts/brd.md — whole skeleton (no Assumptions section); absd/playbook/process/requirements.md ELIC-19

The brd has nowhere to put the Manager's restatements or inferences that still need the user's confirmation. Examples: the run-day worked examples built from D-6, and whether "the same 3 decimals" for the peak means half-up. A-n assumptions exist only in analysis.md.

### FX-168 · minor · meter · C001 Foundation · manager 3

- Kit file: absd/playbook/testing/external-facts.md — EXT-3 / EXT-4; absd/playbook/process/requirements.md ELIC-10

Facts about the deploy platform (server clock UTC, cron at 01:30 UTC, cron MAILTO, 90-day log rotation) are statements about a server this repository cannot reach: for now Meter runs only locally. The kit asks for a recording plus an independent source in Facts mode, or flag-off and fail-closed. It does not say who verifies a platform that is not reachable during the cycle, or how. Flag-off also makes no sense for alerting that works through the exit status.

### FX-169 · minor · meter · C001 Foundation · manager 3

- Kit file: absd/templates/artifacts/cycle.md — Invocation log, column "Commit"; .claude/agents/manager.md 4.5

The invocation row has to be committed before the delegation, so it cannot hold its own commit SHA. The kit does not say whether "Commit" means the logging commit or the worker's reply commit.

### FX-170 · minor · meter · C001 Foundation · manager 3

- Kit file: absd/templates/briefs/invocation-brief.md — Iteration field "gate round <n>/3" vs cycle.md Counters

It is unclear whether the gate-round number in the brief is the round the artifact will face (1/3) or the counter's current value (G1 0/3 in cycle.md). The two records read differently for the same moment.

### FX-171 · minor · meter · C001 Foundation · manager 4

- Kit file: absd/templates/artifacts/cycle.md — Gate ledger Verdict column; manager.md §9 reply line "Gate <name>: PASS | FAIL | BLOCKED"

There is no verdict for a G1 round that is waiting on the user's sign-off or on blocking OQs, which is the normal state of every Gate 1 under ABSD:ELIC-21. FAIL would send the analysis back to its owner, and BLOCKED is defined in §7 for worker blockers.

### FX-172 · minor · meter · C001 Foundation · manager 4

- Kit file: absd/playbook/process/requirements.md — ELIC-21 ("the Manager shows the user the matrix …") vs manager.md §9 ("Paths and ids, never contents or paraphrase") and §7 ("business ones go to the user verbatim with context")

ELIC-21 says the Manager shows the user the matrix. The reply format forbids contents, but worker questions must go to the user verbatim. The kit does not say whether "show" means a path or the content.

### FX-173 · minor · meter · C001 Foundation · manager 4

- Kit file: .claude/agents/manager.md — §6.2 sign-off item vs the analyst revision that blocking OQ answers require

Answers to blocking OQs (here OQ-11, OQ-12) change analysis.md, which means another analyst round and G1 round 2. The kit does not say whether a sign-off on the round-1 matrix still holds for the revised one or has to be asked again.

### FX-174 · minor · meter · C001 Foundation · manager 4

- Kit file: absd/templates/project/foundation-brief.md — intake standing answers (brd D-5: "approve what the Manager recommends when its checks pass") vs ABSD:ELIC-21 "Gate 1 never passes on the Manager's own reading"

The kit lets intake record standing owner answers. It does not say whether a standing approval can cover a Gate 1 sign-off or a product question. If it could, the Manager's recommendation would become the user's decision.

### FX-175 · minor · meter · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — G1 sign-off request (ABSD:ELIC-21), as reported by the owner from the user's seat

Owner's report, verbatim in substance: the request pointed to repository files and section numbers ("02-lenses.md §2, tables A–C, 9 new cells") without putting the 9 cells or the §4 role summary into the question. An owner who does not read the repository is asked to sign off on content they cannot see. The owner signed off on the strength of their standing answer instead.

### FX-176 · minor · meter · C001 Foundation · manager 5

- Kit file: .claude/agents/analyst.md — §4.2 Delta step 3 and §5.1 Fills table ("Unchanged sections read 'Unchanged — <reason>'"), with §2 routing "Gate 1 round" to Delta

Delta mode serves both deltas against an archived analysis (Mode S, C, D) and in-cycle Gate 1 revision rounds. Its rule that unchanged sections read "Unchanged — <reason>" fits only the first case. Applied in a G1 round, it would blank the cycle's own sections, including ones the user has already signed off. The invocation-brief template's Produce line ("full / delta (unchanged sections: 'Unchanged — <reason>')") has the same problem.

### FX-177 · minor · meter · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — §6.2 Gate 1 and §4.13 counters

Nothing says how to record a G1 round that cannot pass because blocking user questions were legitimately open (FAIL, PENDING or not counted). It also does not say whether the user's answers start a new round of the 3-round limit. Here a round is spent purely on routing the user's answers, which leaves 1 spare round for real defects.

### FX-178 · minor · meter · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — §5.4 context.md maintenance table and §4.10 archive step 2

Unresolved open questions go to the Risk register at archive (ELIC-19), and §5.4 lists only containment, waivers and environment limitations as §11 triggers. Neither says what to do when the user explicitly asks now for a question to go into the Risk register (OQ-14, the OQ-15 copy count).

### FX-179 · minor · meter · C001 Foundation · manager 6

- Kit file: absd/playbook/process/requirements.md — ELIC-21

ELIC-21 does not say whether a later G1 round re-signs the whole matrix, value check and inventory or only the cells changed since the last sign-off. It also conflicts with manager.md §9 ("Paths and ids, never contents", ≤ 15 lines): the ELIC-21 question cannot fit that reply format. This keeps recurring (lesson meter-L8).

### FX-180 · minor · meter · C001 Foundation · manager 7

- Kit file: absd/tooling/trace_check.py — gate gate1, check 'every requirement defined in analysis.md is defined in catalogue.md'

Before Catalogue apply, which manager.md 6.2 orders after approval, the check can only be ✗. The tool then prints 'gate1: FAIL — 1 of 3 checks failed' and exits 1, while the gate is in its expected state. It has no pending or pre-apply mode, so a real failure and an expected-by-order one look the same. Already lesson meter-L7; the owner raised it again.

### FX-181 · minor · meter · C001 Foundation · manager 7

- Kit file: .claude/agents/manager.md — 5.4 context.md maintenance ('copying facts verbatim from gated artifacts') vs the table row 'A user decision with lasting effect → §14'

A user decision (D-20, D-21) can go into context.md §14 at once, but the facts it names (RISK-3 Source gaining EXT-SERVER-5/6) are supposed to come from the gated analysis. That splits one answer across two times and two sources.

### FX-182 · minor · meter · C001 Foundation · manager 8

- Kit file: .claude/agents/manager.md — 4.13 Counters / 6.2 (Catalogue apply after an approved round 3/3)

The kit does not say whether a gate1 ✗ after Catalogue apply, when the round is already 3/3, means a fourth round (so an escalation) or a repair of the apply inside the approved round. The Analyst's 4.3 has no failure branch other than BLOCKED.

### FX-183 · minor · meter · C001 Foundation · manager 8

- Kit file: .claude/agents/analyst.md — 4.0 "Commands only for git … and trace_check.py"

Nothing enforces the command list: ownership_hook.py itself says Bash writes are not covered, and ownership_check reads commits by path. The Analyst edited its own files with python3 through Bash and reported it. manager.md has no step for a self-reported deviation that stayed inside the worker's own paths.

### FX-184 · minor · meter · C001 Foundation · manager 8

- Kit file: .claude/agents/analyst.md — 4.2 step 3 "Unchanged sections read 'Unchanged — <reason>'"

Repeat of meter-L9. For an in-cycle Gate 1 round, the Delta mode says to blank the signed-off sections. The brief had to override this so the sections kept their text, and the Analyst flagged the conflict again in round 3.

### FX-185 · minor · meter · C001 Foundation · manager 8

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block / Address table

The template's fixed 4-line reply has a Findings line that analyst.md §9 does not have, so the Manager logs "Critical 0 · Major 0 · Minor 0" for an Analyst reply that never states it. The Address table has no "none" convention for a fresh run.

### FX-186 · minor · meter · C001 Foundation · manager 9

- Kit file: .claude/agents/analyst.md — 4.0 Every run, commit trailers line

'trailers ABSD-Agent and ABSD-Cycle as the single final paragraph' reads as if only those two lines belong there. ABSD:CODE-14 (absd/playbook/engineering/code-quality.md) puts co-author and session lines in the same paragraph.

### FX-187 · minor · meter · C001 Foundation · manager 9

- Kit file: absd/templates/project/EXTERNAL-FACTS.md — seeded fact table (EXT-<SYS>-1…12 rows)

The seed uses fixed-meaning checklist rows as ids (-1 format, -2 time zone, … -12 version signalling). The Analyst reserves EXT-<SYS>-n ids in its own order (analysis §7), and tester.md 4.5 step 1 says to adopt the reserved ids, so one id can name two different facts. Checklist rows with no reserved id need new ids.

### FX-188 · minor · meter · C001 Foundation · manager 9

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block

Still the generic 4-line block, which differs from every worker manual's §9 format (already logged as meter-L10). Each brief has to override it by hand.

### FX-189 · minor · meter · C001 Foundation · tester 9

- Kit file: absd/playbook/testing/contracts-and-fakes.md — FAKE-6 vs absd/playbook/security/baseline.md PRIV-7; absd/playbook/testing/test-code.md TCQ-13; absd/playbook/testing/traceability.md TRACE-3

Facts needs a scrub and re-record tool, because FAKE-6 asks for a documented re-record procedure and PRIV-7 for scrubbed data. Before ADR-002/003 there is no test stack. TCQ-13 requires scripts with logic to have their own tests, and TRACE-3 requires a TC id on every test, while Facts mode adds no TCs. So the tool has no clean home. The kit also never says how to scrub numeric personal values (readings) and still keep a 'real response', or which facts a scrubbed recording still evidences.

### FX-190 · minor · meter · C001 Foundation · tester 9

- Kit file: absd/playbook/testing/external-facts.md — EXT-1 Check ('each UNVERIFIED fact has a Risk register row blocks: flag:<name>'); .claude/agents/tester.md §4.5 step 2

Facts runs before Design and Architecture, so no flag has a name yet (context §8 is empty) and the proposed RISK cannot name its flag. EXT-1 wants a RISK for every UNVERIFIED fact, while step 2 asks only for those 'behind a feature'.

### FX-191 · minor · meter · C001 Foundation · tester 9

- Kit file: absd/templates/artifacts/test_report.md — Facts section; §1 Evidence index; §15 Proposed register rows; Progress line

The Facts section has a single table with no place for the RISK statements, the context.md proposals, the questions for the user or an evidence index. §1 and §15 are Verify's (tester.md 5.2), so proposed RISKs have two possible homes: §15 and the Facts 'Proposed RISK' column. The skeleton's Progress line lists Verify steps, while tester.md 4.0 step 3 asks for this mode's steps.

### FX-192 · minor · meter · C001 Foundation · tester 9

- Kit file: absd/templates/project/EXTERNAL-FACTS.md — seeded section table (EXT-<SYS>-1…12) — see also lesson meter-L17

The template rows use the checklist numbers as ids, which collide with the Analyst's reserved ids (already lesson meter-L17). The template also gives no way to list a checklist row that is N/A and has no reserved id, so it is unclear whether it gets a new id or a row without one. The rows are HTTP-centric (401/429/pagination) and map awkwardly onto a file drop and a cron host.

### FX-193 · minor · meter · C001 Foundation · tester 9

- Kit file: .claude/agents/tester.md — §3 step 5 (playbook reading list)

For every mode, including Facts, the manual requires the Checklists of all 18 files in absd/playbook/testing/ (about 280 KB), most of them irrelevant to Facts. Yet it omits absd/playbook/security/baseline.md, which holds the PRIV-7 rule that §4.2, §4.5 and the brief rely on.

### FX-194 · minor · meter · C001 Foundation · tester 9

- Kit file: absd/playbook/security/baseline.md — PRIV-1/PRIV-7 (with context.md RISK-2)

Facts mode must read and record real responses (FAKE-2, EXT-2) even when they contain personal data whose legal basis is still open (RISK-2 says 'no meter data handled' in C001). PRIV-7 covers only what gets stored. The kit has no check or note for reading real personal data before the basis is settled.

### FX-195 · minor · meter · C001 Foundation · tester 9

- Kit file: absd/templates/project/foundation-brief.md — step 2a (Facts) before step 4 (ADR-002) — see also lesson meter-L16

The recording location must be chosen before ADR-002 assigns test paths. context.md §3 holds only placeholders, so any recording outside docs/testing/** is reported 'unowned' (as a warning; an error under --strict).

### FX-196 · minor · meter · C001 Foundation · tester 9

- Kit file: .claude/agents/tester.md — §9 reply format 'Facts / Log' line

The manual's line reads 'VERIFIED · UNVERIFIED · N/A · lessons'. The brief, which says to use 'your manual's §9 format', gives a different line ('— new ids …; facts that change a requirement …') and drops 'lessons'. §4.5 step 1 also requires new ids to be named in the reply, which the manual's line has no slot for.

### FX-197 · minor · meter · setup

- Kit file: absd/tooling/absd_sync.py — install, printed 'Next steps' step 1; README.md 'Start a new product' / 'Existing codebase: same install'

The printed command uses `git add -A` and promises '(ownership_check accepts it)'. Install does not check for a clean working tree first, and the README says an existing codebase uses the same install. I tested it on a repo with an uncommitted product edit plus an untracked .env: both went into the sync commit, which ownership_check then failed ('a kit-sync commit may only change kit paths, add seeds…'). That leaves a permanent violation on the default branch and can commit a secret. No effect on this greenfield run.

### FX-198 · minor · meter · setup

- Kit file: README.md — 'Start a new product' code block

The README says `git init` without `-b main`. Plain git 2.43 with no init.defaultBranch makes `master`, but ownership_check.py defaults to --base main and the context.md template shows `default branch: <main>`.

### FX-199 · minor · meter · setup

- Kit file: absd/tooling/absd_sync.py — install 'Next steps' step 3 vs README.md 'Start a new product' and .claude/agents/manager.md mode detection

The tool says to ask the Manager to run Bootstrap (Mode B). The README says to just tell it what to build, and the Manager detects the unfilled frame and starts the Foundation cycle itself. A first-time owner cannot tell whether an explicit Bootstrap request is needed.

### FX-200 · minor · meter · setup

- Kit file: absd/tooling/ownership_check.py — default range (merge-base of HEAD and --base main)

With no arguments on main right after install, it exits 2 with '::error::no commits in range …'. An owner checking the claim '(ownership_check accepts it)' gets an error unless they guess `--range HEAD`.

### FX-201 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/artifacts/analysis.md — §7 fact table columns

There is no verification-owner column, although .claude/agents/analyst.md §2 and checklist 6.1 ('every fact with … Status and an owner') and the brd §6 template all require an owner.

### FX-202 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/project/context.md — §1 Principals (and ELIC-2 row list)

There is no slot for the person who operates a locally deployed product (deploy, rollback, backup, restore) when no CI or deploy service identity exists. The operability capabilities had no principal row, and QC rows have no natural Role.

### FX-203 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/artifacts/analysis.md — §2 cell vocabulary ('Yes <id> | No <id or D-n> | N/A')

A Foundation matrix covers the whole product as known today, but requirement ids exist only for C001. The vocabulary has no value for 'capability known, specified in a later cycle', so 'every Yes cites an id' (checklist 6.1) cannot hold for C002/C003 cells.

### FX-204 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/artifacts/analysis.md — §1.2 Non-functional block

There is no AC table for NFs, yet operability NFs need example cases (rollback target ordering, retention at N−1/N/N+1, health exactly at the budget) that the Tester consumes verbatim (ORACLE-6). Decomposition rule 4.4-2 mentions ACs only for functional requirements.

### FX-205 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/playbook/testing/gates.md — Gate register rows Static, Mutation, Flake, Visual vs foundation-brief QC table and DOD-5 row 5

These gates have no QC capability, so they never become catalogue entries the acceptance report could show as verified, although the Foundation must show every gate RED once.

### FX-206 · minor · shelf · C001 Foundation · analyst 2

- Kit file: .claude/agents/analyst.md — §9 reply format vs absd/templates/briefs/invocation-brief.md reply block

The two formats differ. The brief's status values (COMPLETE-WITH-CONFLICTS, HALTED) are missing from the analyst manual, and the brief's 'Findings: Critical/Major/Minor' line has no meaning for an analyst.

### FX-207 · minor · shelf · C001 Foundation · analyst 2

- Kit file: .claude/agents/analyst.md — §4.0 'Commands only for … python3 absd/tooling/trace_check.py'; allow list in absd/templates/project/claude-settings.json

The manual and the installed allow list use plain 'python3 absd/tooling/…'. Kit tools that import kit modules (ownership_check → absd_sync) write __pycache__ into the vendored kit and dirty the tree, so the Manager briefs 'python3 -B'. That form is not on the allow list and triggers permission prompts.

### FX-208 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/tooling/trace_check.py — gate1 preset

gate1 passes while analysis.md §12 holds open questions flagged as blocking Gate 1 (here OQ-3, OQ-5, OQ-7). Manager checklist 6.2 'every blocking one answered' rests on reading alone; there is no mechanical check.

### FX-209 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/templates/project/foundation-brief.md — QC-13 'in CI'; absd/playbook/process/definition-of-done.md DOD-5 row 8

The kit assumes a CI service exists and gives no wording or route for products with none (local only); this produced a contradiction with the user's D-3.

### FX-210 · minor · shelf · C001 Foundation · analyst 2

- Kit file: absd/playbook/process/requirements.md — ELIC-6 ('not offered' with the user's reason)

It does not say whether a standing owner answer (here D-7, 'keep everything as small as the requirements allow') counts as the user's reason for a 'not offered' CRUD verb on operational entities (release, store, backup).

### FX-211 · minor · shelf · C001 Foundation · analyst 4

- Kit file: .claude/agents/analyst.md — §4.0 'Commands only for … python3 absd/tooling/trace_check.py'; §4.1 step 7; §4.3 step 4

The manual prints the trace_check commands without -B, while the brief (and cycle.md) require `python3 -B` to keep the vendored kit clean. The manual and the brief disagree on the exact command.

### FX-212 · minor · shelf · C001 Foundation · analyst 4

- Kit file: .claude/agents/analyst.md — §9 Reply format vs absd/templates/briefs/invocation-brief.md 'Reply format'

The brief's reply format has Status values COMPLETE-WITH-CONFLICTS and HALTED and a 'Findings: Critical/Major/Minor' line. The analyst manual's format has neither. Both have Status, Artifacts and Blockers lines, so the merged order had to be guessed.

### FX-213 · minor · shelf · C001 Foundation · analyst 4

- Kit file: .claude/agents/analyst.md — §4.0 'Commit after each Progress group'

A Delta has the same nine Progress groups as a full Analyze, so the rule asks for nine commits for a small answer-applying Delta. The manual also does not say whether a second invocation resets the round 1 Progress line or keeps it.

### FX-214 · minor · shelf · C001 Foundation · analyst 4

- Kit file: absd/templates/project/foundation-brief.md — QC-10 row ('live checks nightly; a missing credential is RED')

The QC-10 wording assumes a scheduler (nightly) and a credentialed outside service. With the host platform as the only external system and no CI service, the host needs no credential and nothing can run 'nightly'. The kit gives no guidance for local-only products.

### FX-215 · minor · shelf · C001 Foundation · analyst 4

- Kit file: .claude/agents/analyst.md — §4.4 rule 15 (every other table starts with a non-id column) vs absd/templates/artifacts/analysis.md §16 lens table

The skeleton's §16 lens table starts each row with an ELIC-n id, which rule 15 forbids as written. trace_check ignores it only because ELIC is a reserved code.

### FX-216 · minor · shelf · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.0 last bullet (commands only git status/diff/log/show/add/commit and trace_check) vs §4.3 step 3

The step 3 checks (diff equals the §15 rows, no duplicate id, Status cells exact) have no tool among the allowed commands. trace_check gate1 only checks that each id is present in the catalogue. It does not compare row text or Status values, and it ignores duplicates and extra rows. traceability_report.py does detect duplicate ids but is not an allowed command. So the ABSD:TRACE-2 checks rely on eyeballing.

### FX-217 · minor · shelf · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §3 Read first item 4 (every playbook Checklist in full, every run) vs §4.3

The manual has no reading list per mode, so a purely mechanical Catalogue apply also has to read the full ELIC, TRACE, ORACLE, ACCESS, EXT, FAKE, PRIV, VAR, STRAT and DOD material. That is pointless work for copying 27 approved rows. The brief referred to 'your manual's playbook list (§4.3 Catalogue apply)', but no such list exists.

### FX-218 · minor · shelf · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.3 step 2 ("Add → append in id order within the area"; "Keep the header line exactly") and §6.2 ("header byte-identical")

'Id order' is undefined across series (APP-2 vs APP-NF-1 vs APP-BR-1) and between lexical and numeric order (QC-10 after QC-9 or after QC-1). Area order on a first apply is also undefined. 'Header line' could mean the table header row (§5.2) or the title and preamble of the catalogue template.

### FX-219 · minor · shelf · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §3 item 5, §4.0 last bullet, §4.1 step 7, §4.3 step 4 (python3 absd/tooling/trace_check.py …)

The kit's commands run vendored tools without -B. Any kit tool that imports a sibling module writes absd/tooling/__pycache__ into the read-only kit and dirties the tree, as already happened with ownership_check in this cycle. The Manager had to add the -B rule to every brief by hand.

### FX-220 · minor · shelf · C001 Foundation · designer 8

- Kit file: .claude/agents/designer.md — §9 Reply format vs absd/templates/briefs/invocation-brief.md 'Reply format' vs the brief's own reply block

There are three different reply formats. The manual has Mode, Coverage, Rubric, Design QA, Findings with routes, Questions, Proposed rows, Blockers and Lessons. The brief drops the Design QA line and the Findings routing. The brief template has only Status, Artifacts·Commit, Findings and Blockers.

### FX-221 · minor · shelf · C001 Foundation · designer 8

- Kit file: absd/templates/project/design-system.md — header + §2 'Contrast checked against'; designer.md 4.2 step 1 / 6.4

The living design-system.md, which is never archived, must carry computed ratios backed by command evidence. But the Designer's evidence folder is absd-project/working/evidence/designer/, which is archived with the cycle. So the living document's evidence citation points to a path that moves at the archive.

### FX-222 · minor · shelf · C001 Foundation · designer 8

- Kit file: .claude/agents/designer.md — §4.0 'Commit after each Progress group (Status IN-PROGRESS)'; absd/templates/artifacts/design.md Progress line

The design.md Progress line has 10 groups (0, 1–3, 4–6, …, contrast, gate-ux, commit). Read literally, an uninterrupted Foundation run makes about 10 commits. Design System mode also has no Progress list of its own for design-system.md.

### FX-223 · minor · shelf · C001 Foundation · designer 8

- Kit file: absd/playbook/design/rubric-and-qa.md — DSN-19 table, row D5 Motion, web-ui column

The web-ui column has no N/A for a design that deliberately has no motion, even though DSN-6 applies only 'with motion'. A 5 ('signature moments delight') cannot be earned when there is nothing to animate, so the rubric minimum is forced down by a choice the owner's character asks for.

### FX-224 · minor · shelf · C001 Foundation · designer 8

- Kit file: absd/templates/project/design-system.md — §2 token rows (surface/raised, text.muted, success/warning/danger/info, radius sm/md/lg, elevation 1–3, type.mono)

The template invites filling every token row. The kit does not say whether a Foundation design system defines a full palette or only what the skeleton uses, and that clashes with YAGNI and the owner's 'as small as the requirements allow'.

### FX-225 · minor · shelf · C001 Foundation · designer 8

- Kit file: absd/templates/artifacts/design.md — §6 matrix ('a row per interactive element') and §12 'one polite status region per screen'

SCR-1 has no interactive element, so a strict per-interactive-element matrix would give it no row and no gallery cell. The rules also demand a polite status region on static pages that announce nothing, which is pointless.

### FX-226 · minor · shelf · C001 Foundation · designer 8

- Kit file: absd/playbook/testing/nonfunctional.md — VIS-1 (gallery file names SCR-n_<state>_<device>_<theme>.png) vs absd/templates/artifacts/design.md §6

VIS-1 names gallery files by state, device and theme slugs, but the design.md template has no place where the Designer fixes those slugs or the list of gallery cells. The Tester and Design QA could each spell them differently.

### FX-227 · minor · shelf · C001 Foundation · designer 8

- Kit file: absd/templates/artifacts/design.md — header 'Inputs: … design-system.md @<sha>'

In Design System (Foundation) mode, design-system.md is created in the same commit as design.md, so there is no SHA to cite.

### FX-228 · minor · shelf · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 6.1 Cycle start, item 2 (nightly and live contract runs green)

Gives no case for a greenfield Foundation where no suite, CI or external system exists yet. It only says red → Mode D, or not run → trigger and wait.

### FX-229 · minor · shelf · C001 Foundation · manager 1

- Kit file: absd/templates/artifacts/cycle.md — Mode S eligibility table; Close table heading

The skeleton makes the eleven-question table mandatory, though ELIC-1 applies only to F/S/D/C intakes. It does not say what Mode B writes there. The Close heading names only DOD-2 and DOD-4 row order: no DOD-5 rows for the Foundation and no harvest/archive/merge rows (DOD-5 has none, foundation-brief step 9 does).

### FX-230 · minor · shelf · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 6.3 Gate UX; 5.4 context maintenance; 4.4 route table

In some UXQs the Designer has already designed the recommended default, and the user can accept it. The kit has no step for writing that answer back into the Designer's artifacts without a Designer round. design.md is archived with the cycle, so its stale '§21 Answer —' cells only matter for history. design-system.md is a living document that is never archived, and its 'pending C001 UXQ-1 / UXQ-2' notes now outlive the cycle. The Manager may not edit them (RULES rule 9).

### FX-231 · minor · shelf · C001 Foundation · manager 10

- Kit file: absd/playbook/testing/access-visibility.md — ACCESS-1, ACCESS-6; also absd/templates/artifacts/architecture.md §5.3, §7

With cli not declared (D-26 = A), the operator's release commands sit outside every interface profile. Yet analysis §2 lists the laptop operator as a principal, and Q3 says 'no operation without an access-and-visibility rule'. The kit ties the operation inventory, the cli operation keys (`cmd sub --flag`), the exit-code taxonomy and the architecture §5.3 command tree to a declared cli profile. It does not say whether operator tooling outside a declared profile needs operation-inventory and matrix rows, or where its exit codes are specified.

### FX-232 · minor · shelf · C001 Foundation · manager 10

- Kit file: .claude/agents/architect.md — §9 Reply format

The architect reply format has no 'Findings:' line, but RULES §8 requires finding counts by severity in every worker reply. analysis.md §9 has the same gap (reported at invocation 3). The invocation-brief template's reply format includes the line, so the manual and the template disagree.

### FX-233 · minor · shelf · C001 Foundation · manager 10

- Kit file: absd/templates/artifacts/cycle.md — whole file vs absd/RULES.md §9 budgets

cycle.md only ever grows: every Decision, invocation, gate round and pending route stays in it. After 6 of about 15 C001 invocations it holds about 54.7 KB (8,400 words, roughly 16k tokens), close to the 20k-token artifact budget. RULES §9 says to split larger artifacts into an index plus parts. Neither the cycle.md skeleton nor the tools that read it (gate3 reads `Mode:`, the manual's 'read FIRST' resume rule) say whether cycle.md may be split, or which sections must stay in the index.

### FX-234 · minor · shelf · C001 Foundation · manager 2

- Kit file: .claude/agents/manager.md — 4.2 intake / 4.6 Mode B step 1 (and absd/playbook/process/requirements.md intake lenses)

Reported by the owner: the Foundation takes the first cycle number (C001), so an owner who writes 'first cycle' or 'second cycle' in their notes can mean two different cycle numbers. No intake question asks how the owner counts cycles.

### FX-235 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/templates/project/context.md — §1 Product frame

foundation-brief step 1 and ABSD:DOD-5 row 1 require a 'deploy target' in the frame, but the context template has no field for it. Who can reach the product (laptop plus local network, never the public internet) has no field either.

### FX-236 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/templates/project/foundation-brief.md — 'Quality capabilities (select per profile …)'

No kit file says who selects the QCs. Analyst and Architect manuals refer to 'the selected QC-n', but neither the Manager's 4.6 nor the Analyst's 4.1 says it is their job.

### FX-237 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/templates/project/foundation-brief.md — step 1 'area codes' / step 2 'walking-skeleton requirement'

The frame asks the owner for feature area codes only. The walking skeleton and the operability defaults that no QC covers (log levels, alerting, health and version) need an area code that is not QC. The kit gives no default and does not tell the Manager to ask for one.

### FX-238 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/templates/artifacts/brd.md — header 'Mode: F/S/C'; §1–§12

The brd skeleton has no Mode B variant. It also has no home for the owner's source document, which brd keeps per cycle and archives while context.md holds current state only, and none for technical constraints the owner imposes (stack, preinstalled browsers) before ADR-001 exists.

### FX-239 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/playbook/process/requirements.md — ELIC-2 Check ('every Yes cites a requirement') vs rule text ('source (brd section, D-n, catalogue id)'); analyst.md 6.1

In a Foundation the whole-product matrix covers capabilities that have no requirement yet (SHELF and ACC come in C002, LOAN in C003). The Check and the Analyst's self-check demand a requirement id for every Yes, while the rule text accepts a brd section or a D-n.

### FX-240 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/playbook/process/requirements.md — ELIC-21 (sign-off never on the Manager's own reading)

The kit does not say whether an owner's standing answer ('approve what the Manager recommends when its checks pass') can stand in for the Gate 1 sign-off of the matrix, value check and inventory.

### FX-241 · minor · shelf · C001 Foundation · manager 2

- Kit file: absd/playbook/process/requirements.md — ELIC-12 ('maximum observed in the real source (not guessed)'); context template §6 'Max observed'

A greenfield product has no real source to observe. Only the owner's stated limits exist (60 members, 500 books per shelf), and the kit does not say how to record that.

### FX-242 · minor · shelf · C001 Foundation · manager 3

- Kit file: .claude/agents/manager.md — §6 (trace_check gate <preset> at every gate) and §6.2 Gate 1

§6 says to run `trace_check.py gate <preset>` at every gate. Before catalogue apply, plain `gate gate1` is always red: every requirement shows as missing from catalogue.md. The pre-sign-off form (`--catalogue absd-project/working/analysis.md`) is documented only in analyst.md 4.1 step 7. manager.md §6.2 does not say which form the Manager runs in round 1, or that the red catalogue check is expected there.

### FX-243 · minor · shelf · C001 Foundation · manager 3

- Kit file: .claude/agents/manager.md — §4.13 counters and §6.2 (Gate 1 rounds); §9 gate verdicts

The kit does not say whether an analyst · Delta that only writes the user's answers to Gate 1-blocking questions counts as a new G1 round. A Foundation's Analyze almost always ends with blocking questions (thresholds such as S and N), so every Foundation would spend 2 of its 3 G1 rounds by design. Also, the gate ledger and the §9 reply format offer only PASS, FAIL or BLOCKED, with no state for 'waiting for the user's sign-off'.

### FX-244 · minor · shelf · C001 Foundation · manager 3

- Kit file: .claude/agents/manager.md — §9 reply format (≤ 15 lines; 'paths and ids, never contents or paraphrase'; 'each question answerable alone') vs §6.2 / ABSD:ELIC-21

ELIC-21 requires the user to see the matrix, the role value check and the inventory before signing off. The reply format allows only paths and ids, no content or paraphrase, and at most 15 lines, yet each of up to 7 questions must be answerable alone. A Foundation sign-off batch (sign-off plus 3 Gate 1 questions plus 3–4 Gate 2 items) cannot satisfy both rules.

### FX-245 · minor · shelf · C001 Foundation · manager 4

- Kit file: absd/playbook/process/requirements.md — ELIC-21 (and manager.md 6.2 item 6)

Nothing says whether a Gate 1 sign-off covers the Delta that applies answers the user gave with it. Here the owner signed off on the round 1 artifact together with the answers to blocking OQs that a Delta still has to apply, and one remark will change §2 rows.

### FX-246 · minor · shelf · C001 Foundation · manager 4

- Kit file: absd/playbook/process/requirements.md — ELIC-2 Check ("rows = context.md Principals"), and analyst.md 6.1 Lenses item 1

The matrix must have one row per principal × entitlement state, plus jobs, service identities and inbound callers, even when rows are identical or all N/A. Here that gave 13 rows for three roles. The owner found it heavy and asked to keep only the rows that change who may do something. The kit says nothing about collapsing identical rows.

### FX-247 · minor · shelf · C001 Foundation · manager 4

- Kit file: .claude/agents/manager.md — 4.2 step 4 / §9 reply format; absd/templates/artifacts/brd.md §9 'Options shown' column

The Manager has no instruction to record the outgoing question batch and its options in the repository before asking. Yet the brd §9 'Options shown' column has to be filled once the answer arrives, and the Manager's memory between turns lives only in the repo. The user answered 'option A', and the options had to be rebuilt from analysis §12/§13.

### FX-248 · minor · shelf · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — 6.2 last item vs .claude/agents/analyst.md 4.3 step 1; absd/templates/artifacts/cycle.md Gate ledger

Gate 1 has two SHAs: 'approved' at the analysis SHA, which Catalogue apply step 1 needs in the ledger, and 'PASS at that SHA' after catalogue apply. The ledger has one Verdict and one Product SHA column, and no column for the artifact SHA. So it isn't clear which row or SHA records the G1 PASS, or where the approval SHA goes.

### FX-249 · minor · shelf · C001 Foundation · manager 5

- Kit file: absd/playbook/process/requirements.md — ELIC-19 / manager.md 6.2 'every blocking one answered'

A non-blocking assumption owned by the user (A-4: is the 90-day retention boundary inclusive, and is it counted in UTC) can pass Gate 1 and go into the catalogue story and the ACs. Yet changing it after Gate T needs an amendment through a new G1. The kit doesn't say when an open, non-blocking user-owned A-n must be put to the user: at G1, before Plan & Bind, or only at archive as a RISK.

### FX-250 · minor · shelf · C001 Foundation · manager 5

- Kit file: absd/templates/project/settings.json — permissions.allow

The allow list holds 'python3 absd/tooling/<tool>.py:*'. The kit tools have to run as 'python3 -B absd/tooling/…' so they don't write __pycache__ into the vendored kit (found in round 1). The -B form doesn't match the allow list.

### FX-251 · minor · shelf · C001 Foundation · manager 6

- Kit file: .claude/agents/analyst.md — §9 Reply format

The analyst reply format has no Findings line (counts by severity), but RULES §8 requires every worker reply to carry finding counts by severity. The analyst had to add the line itself.

### FX-252 · minor · shelf · C001 Foundation · manager 6

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block

The brief template's generic 4-line reply format differs from each worker manual's own §9 reply format (the tester's has many more lines, including a Facts/Log line). The kit does not say which one the brief should carry or which wins.

### FX-253 · minor · shelf · C001 Foundation · manager 6

- Kit file: .claude/agents/manager.md — §5.4 table / §4.10 step 2; context template §11

The Analyst proposes RISK rows when its question is marked non-blocking (OQ-9: 'Blocking? none'). The kit does not say what 'Blocks' value such a RISK takes, or when a Manager records analysis proposals: §5.4 has no row for 'G1 passed → apply analyst proposals'. Only the 6.2 checklist implies it, through the analyst's Proposals reply line.

### FX-254 · minor · shelf · C001 Foundation · manager 7

- Kit file: absd/tooling/trace_check.py — `check` subcommand; definition rule (first token of a row's first cell) vs absd/templates/artifacts/analysis.md §7 table (EXT id in column 4)

`check --ids ext --defined-in analysis.md,analysis --referenced-in EXTERNAL-FACTS.md` printed PASS with '0 checked' and no warning. The analysis skeleton puts reserved EXT ids in column 4, so the tool never counts them as defined. The Manager therefore has no mechanical way to confirm that Facts adopted every reserved EXT id. gate2 and gateT read EXT ids as referenced, so they are not affected.

### FX-255 · minor · shelf · C001 Foundation · manager 7

- Kit file: absd/RULES.md — §6 product SHA definition

A Facts commit that only touches the Tester's living docs (docs/testing/EXTERNAL-FACTS.md and recordings) becomes the new product SHA even though no product path changed; only the Log commit's Lesson cells are exempt. Facts evidence 'taken at 083e29b' is therefore formally out of date the moment it is committed, and the Tester had to explain this in the test_report header.

### FX-256 · minor · shelf · C001 Foundation · manager 7

- Kit file: .claude/agents/manager.md — 6.2 last bullet ('a Facts result that changes a requirement → analyst · Delta → G1') and 4.4 route F/B

There is no rule for a Facts result that contradicts no AC but leaves a fact UNVERIFIED in a way that casts doubt on user decisions (here D-3 vs D-15). It is also unclear whether the route may go on to Design while the user's answer is pending, and whether a Delta after Facts is a new G1 round. If it is, a Facts discovery after two G1 rounds leaves only round 3/3.

### FX-257 · minor · shelf · C001 Foundation · manager 7

- Kit file: .claude/agents/manager.md — §6 opening ('Every gate, every route: trace_check … and ownership_check …; record both invocations and results in the gate ledger')

A route step with no gate (tester · Facts) has to be checked too, but the gate ledger has no row type for a step without a gate, and it is unclear whether 'every route' means every route step.

### FX-258 · minor · shelf · C001 Foundation · manager 8

- Kit file: .claude/agents/manager.md — §6.2 Gate 1 last item; §5.4; §7 Worker questions

No kit step brings a user's confirmation of a non-blocking assumption, given after Gate 1 passed (A-4 → D-23), back into analysis.md. Only the Analyst may write analysis §12, and in Mode B no analyst step is left on the route, so the artifact keeps showing A-4 as 'open'. The only way to update that cell is an analyst Delta, which would cost a G1 round (here round 3/3, the limit) for a status cell.

### FX-259 · minor · shelf · C001 Foundation · manager 8

- Kit file: .claude/agents/manager.md — §4.2 step 4 / §6.2 'a Facts result that changes a requirement → analyst · Delta'

The user picked option A (keep the requirements) but added a constraint in the same answer: 'no tunnel and no VPN'. The kit does not say whether a constraint the user adds inside an answer needs the Analyst (a Delta and a G1 round) when it only narrows scope the requirements already cover (D-3: 'not exposed to the public internet'), or whether brd §8 Out of scope is enough. The Manager must not make that call on technical grounds, and no rule tells it which.

### FX-260 · minor · shelf · C001 Foundation · manager 8

- Kit file: absd/templates/project/context.md — §11 Risk & Assumption register, Owner and Status columns

RISK-5 needs two owners (the user does the phone check, the Tester records it), and its status is 'open' but already accepted by the user as release-blocking. The template defines only one owner and has no status between open and accepted for a risk the user accepted as blocking. RISK-9 has the opposite shape: accepted, blocks nothing.

### FX-261 · minor · shelf · C001 Foundation · manager 8

- Kit file: absd/playbook/process/definition-of-done.md — ABSD:DOD-5 (Foundation) vs DOD-7/DOD-8 (release); manager.md 4.9

A release-blocking RISK whose unblocker is a person's real-device check (RISK-5: phone on the club network) belongs in Mode R. The kit does not say whether the Foundation's Gate 3 and merge, which deploy the walking skeleton to the serving machine, count as a 'first release' (DOD-7 'users get a build') that would pull Mode R into C001.

### FX-262 · minor · shelf · C001 Foundation · manager 9

- Kit file: .claude/agents/manager.md — 6.3 item "library, http-api, data-pipeline: the public surface named (…), contracts, runbook (ABSD:DSN-18)"

The checklist line reads as if every machine profile, http-api included, needs contracts and a runbook. DSN-18 asks for a dataset contract and a runbook only for data-pipeline. For http-api it asks for the resource model, fields, one error body, pagination, versioning and named examples.

### FX-263 · minor · shelf · C001 Foundation · manager 9

- Kit file: absd/templates/artifacts/design.md — §21 column "Answer (D-n)" and the header's "pending UXQ-n" notes

The user answers UXQs after the Designer's reply, at GUX. When the answer is the designed default, the Designer's artifact can only record it through another Designer round, which costs a GUX round for status cells. Without that round the artifact stays 'pending' after the gate. The analysis template has the same problem for confirmed assumptions (A-4 / D-23).

### FX-264 · minor · shelf · C001 Foundation · manager 9

- Kit file: .claude/agents/manager.md — 6.3 "product questions answered by the user as D-n"; 8 rule 1

The kit does not say whether a user's standing answer ('I approve what you recommend when your checks pass', context §14) settles a non-blocking UXQ that has a default. So every UXQ forces a user round trip before GUX can pass, even when the design already follows the recommended default.

### FX-265 · minor · shelf · C001 Foundation · manager 9

- Kit file: absd/RULES.md — §7 IDs table

The ID table lists neither the question and decision ids the manuals and templates use everywhere (OQ-n, A-n, UXQ-n, UXA-n, D-n) nor their scope (product or cycle, and whether they are reused across cycles).

### FX-266 · minor · shelf · C001 Foundation · tester 6

- Kit file: .claude/agents/tester.md — §9 reply format vs absd/templates/briefs/invocation-brief.md 'Reply format'

The brief template lists Status COMPLETE-WITH-CONFLICTS | HALTED and a 'Facts: … new EXT ids …; facts that change a requirement …' line. Manual §9 has only COMPLETE | BLOCKED | IN-PROGRESS and a 'Facts / Log' line with no slot for new ids, although §4.5 step 1 says new ids are 'named in your reply'. The manual also does not say where a Facts result that bears on a requirement goes.

### FX-267 · minor · shelf · C001 Foundation · tester 6

- Kit file: absd/templates/artifacts/test_report.md — header 'Product SHA … valid while git diff --quiet <sha> HEAD'

The Facts commit itself changes docs/testing/** (outside absd-project/), so the Facts SHA stops being 'valid' the moment the Facts work is committed. The header also has no defined value for a report that holds only Facts. RULES §6 evidence validity does not fit host facts, which do not depend on the product tree at all.

### FX-268 · minor · shelf · C001 Foundation · tester 6

- Kit file: absd/playbook/testing/contracts-and-fakes.md — FAKE-2 'committed in the test tree' (also absd/templates/project/EXTERNAL-FACTS.md intro)

Facts runs before ADR-002, so no test tree exists yet; context.md §3 has only docs/testing/** as a filled Tester row. The Manager already logged this, and the brief left the location to me.

### FX-269 · minor · shelf · C001 Foundation · tester 6

- Kit file: absd/playbook/testing/contracts-and-fakes.md — FAKE-6 Check 'secret and personal-data scan over the recordings directory'

Facts mode demands a scan before any test stack exists, and absd/tooling ships no scanner, so every product must write its own. This is repeated work across products and an unproven control until each one is written.

### FX-270 · minor · shelf · C001 Foundation · tester 6

- Kit file: absd/tooling/trace_check.py — `check --ids ext` (defined → referenced only)

The analysis §7 fact table's first column is a row number, so reserved EXT ids are never 'defined' in the tool's sense. No mechanical check can confirm that Facts adopted every id the Analyst reserved; the tool checks only defined → referenced.

### FX-271 · minor · shelf · C001 Foundation · tester 6

- Kit file: absd/playbook/testing/external-facts.md — EXT-2 checklist / EXT-3

There is no checklist for a host platform. EXT-2 #5 (volume & pagination) and #11 (late corrections & duplicates) do not fit a host. EXT-3's platform list misses facts that drove real traps here: the account's privileges (as root a chmod-0555 folder is writable, so 'not writable' tests are vacuous), clock synchronisation, persistence across a restart and autostart, and the test browser build pinning the runner version.

### FX-272 · minor · shelf · C001 Foundation · tester 6

- Kit file: .claude/agents/tester.md — §4.5 step 2 'an independent source' / §4.0 step 4 'Run commands exactly as context.md §4 lists them'

The kit does not say what to do when the official documentation hosts are unreachable from the environment (man7.org, rfc-editor.org, gnu.org, sqlite.org, freedesktop.org, git-scm.com were blocked by the proxy). It also does not say how to preserve third-party sources. Separately, context.md §4 is all placeholders at Facts time and lists no capture command to run 'exactly'.

### FX-273 · minor · shelf · setup

- Kit file: absd/templates/project/claude-settings.json — hooks.PreToolUse[0].hooks[0].command ("python3 \"$CLAUDE_PROJECT_DIR/absd/tooling/ownership_hook.py\""); also absd_sync.py install (no .gitignore created)

The ownership hook imports ownership_check.py, so every agent write leaves untracked bytecode in absd/tooling/__pycache__/ (absd_sync.cpython-313.pyc and ownership_check.cpython-313.pyc). I reproduced this by piping a single hook event in. The install creates no .gitignore and nothing ignores __pycache__. From the Manager's first write the tree is dirty inside the read-only kit folder, and `git add -A` (the command the kit itself prints) would commit .pyc files into absd/. Nothing would flag it: `absd_sync check` skips bytecode and still says 0 extra, and in a scratch clone ownership_check passed a non-sync commit that added absd/tooling/__pycache__/*.pyc.

### FX-274 · minor · shelf · setup

- Kit file: absd/tooling/ownership_hook.py — main() / decide(); settings key "onFailure": "block"

The hook returns 2 only for bad JSON and for refusals. Any other crash ends with exit 1 and a Python traceback. I fed it tool_input as a string and got AttributeError and exit 1. A context.md that is not valid UTF-8 would likely do the same, because UnicodeDecodeError is not an OSError. In Claude Code's PreToolUse contract exit 1 does not block, so in those cases the write goes through. The seeded settings rely on "onFailure": "block" to cover this. As far as I know that is not a documented Claude Code hook field, so the protection may be silently ignored.

### FX-275 · minor · shelf · setup

- Kit file: README.md — Start a new product (code block: `git init`)

The README runs a plain `git init` and then says to commit "on the default branch". On a machine where git's default branch is still master, the product's default branch becomes master. The rest of the kit assumes main: context.md shows `default branch: <main>` and ownership_check's --base defaults to main. Nothing tells the owner about this.

### FX-276 · minor · shelf · setup

- Kit file: absd/tooling/absd_sync.py — install 'Next steps' item 3 vs README 'Start a new product' and absd/templates/project/context.md header (ABSD:DOD-5)

The install's step 3 tells the owner to "Ask it to run Bootstrap (Mode B...)". The README says the owner just says what to build and the Manager sees the empty project file and starts Foundation by itself. The context.md template says the same: the Manager starts Mode B automatically. A first-time owner cannot tell whether they must name Bootstrap or Mode B. Also, neither the README nor the install output says how to hand over existing written requirements, such as a notes file.

### FX-277 · minor · shelf · setup

- Kit file: README.md — Start a new product (`git clone https://github.com/bmaximus/ABSD /path/to/ABSD  # the kit (a release tag)`)

The comment says to use a release tag, but the command clones the default branch and never checks out a tag. A first-time owner would install whatever is on the default branch.

### FX-278 · minor · tally · C001 Foundation · analyst 3

- Kit file: absd/RULES.md — §4 Q6 vs .claude/agents/analyst.md §6.1 (§7 item) and absd/templates/artifacts/analysis.md §7

Q6 says any behaviour that depends on an UNVERIFIED external fact ships disabled. The manual and the template require a flag only for facts driving time, money, security or lifecycle. For platform facts behind release and install procedures, 'ships disabled' means nothing.

### FX-279 · minor · tally · C001 Foundation · analyst 3

- Kit file: .claude/agents/analyst.md — §6.1 Lenses '§2 ... every Yes cites an id'; absd/playbook/process/requirements.md ELIC-2 Check 'every Yes cites a requirement'

In a Mode B whole-product matrix, capabilities deferred to later cycles (D-3) have no requirement ids yet, so the rule cannot hold for them. Library cells that depend on an unanswered question fit none of Yes, No or N/A.

### FX-280 · minor · tally · C001 Foundation · analyst 3

- Kit file: .claude/agents/analyst.md — §4.0 'Commit after each Progress group (Status IN-PROGRESS)'

The skeleton has 9 Progress groups, so an uninterrupted run would make 9 commits for one artifact. That is churn the resume purpose does not need.

### FX-281 · minor · tally · C001 Foundation · analyst 3

- Kit file: absd/templates/artifacts/analysis.md — §12 'Id (A-n · OQ-n)'

Within one cycle, the brd §10 OQ-n (Manager) and the analysis §12 OQ-n (Analyst) share the same prefix, and nothing says whether the analysis continues the brd's numbering. Here brd OQ-1–OQ-4 already exist.

### FX-282 · minor · tally · C001 Foundation · analyst 3

- Kit file: absd/templates/project/foundation-brief.md — QC-13 'in CI'; absd/playbook/process/definition-of-done.md DOD-5 row 8 'ownership_check and trace_check in CI'

There is no variant for products without a CI service; it is covered here only through the product-specific RISK-2.

### FX-283 · minor · tally · C001 Foundation · analyst 3

- Kit file: absd/playbook/process/definition-of-done.md — DOD-5 row 7 (cli, library 'built once, published and installed ... withdraw or yank')

The Foundation must publish the skeleton, but the kit does not say whether that publication is a release in the Mode R / DOD-8 sense. Here that collides with the user's D-8: every release waits for the owner's Mac run, and RISK-1 blocks it.

### FX-284 · minor · tally · C001 Foundation · analyst 3

- Kit file: absd/playbook/process/requirements.md — ELIC-6 ('not offered' with the user's reason) and analysis template §11 'not offered — <reason> (D-n)'

Every not-offered CRUD verb needs a user decision, even when a stated rule already implies it (a published version never changes). This invites pointless questions.

### FX-285 · minor · tally · C001 Foundation · analyst 3

- Kit file: .claude/agents/analyst.md — §2 table row B ('Produces analysis.md ...; first catalogue.md') vs §4.3 Catalogue apply after Gate 1; foundation-brief step 2 'first catalogue.md'

Step 2 reads as if the Foundation analyst run also writes the first catalogue.md, while §4.3 and the cycle route make that a separate invocation after Gate 1.

### FX-286 · minor · tally · C001 Foundation · analyst 3

- Kit file: absd/templates/artifacts/analysis.md — §1.1 Functional / §1.2 Non-functional

Nothing says where QC-n requirements go. They have no NF form, and trace_check treats them as functional (an AC is required), but they are quality capabilities.

### FX-287 · minor · tally · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.0 'Commands only for git … and trace_check' together with §5.1 split rule

Splitting means moving whole sections exactly. With no file commands allowed, the Analyst has to retype about 60 KB of unchanged text through Write and Edit, which is costly and error-prone. The kit gives no mechanical way to split.

### FX-288 · minor · tally · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.0 Progress / Resume

The kit does not define the Progress line across Gate 1 rounds. After round 1 every item is ticked, so a Resume of an interrupted round-2 delta would find nothing to continue from.

### FX-289 · minor · tally · C001 Foundation · analyst 5

- Kit file: absd/playbook/process/requirements.md — ELIC-21 (and analyst.md §9 'Sign-off needed' line)

Sign-off covers only the matrix, the value check and the inventory. Assumptions owned by the user (A-n) have no defined sign-off point, yet D-14 signed A-1, A-3, A-4 and A-5, and this delta needed new user-owned readings (A-6 for D-12 d 'only release', A-7 for D-8 with D-9 and D-11). The reply format has no slot for them.

### FX-290 · minor · tally · C001 Foundation · analyst 5

- Kit file: absd/playbook/process/definition-of-done.md — DOD-5 row 4, with traceability TRACE-12

Every QC must be verified by its tests in the Foundation cycle. QC-11.AC4's success path (the owner's Mac output recorded with a release) can only happen at C002's first release under D-13. The kit has no status for an AC whose success path is tied to a later release.

### FX-291 · minor · tally · C001 Foundation · analyst 5

- Kit file: .claude/agents/analyst.md — §4.4 rule 10 / RULES Q6 ('dependent behaviour specified flag-off and fail-closed')

For build and install-platform facts (EXT-3), the behaviour that rests on an UNVERIFIED fact is an install procedure, here the refusal on 3.12 and 3.14 resting on EXT-PIP-2. No feature flag can guard it, and the kit offers no other fail-closed form.

### FX-292 · minor · tally · C001 Foundation · analyst 5

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format (Status / Artifacts / Findings / Blockers)

This format still differs from analyst.md §9, which has Mode, Counts, Facts needed, trace_check, Sign-off and Routed items. The two kit files disagree. This brief resolved it by pointing to §9, and cycle.md already has the lesson.

### FX-293 · minor · tally · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — 4.0 "Commands only for git (status, diff, log, show, add, commit) and python3 absd/tooling/trace_check.py" vs 4.3 step 3

Step 3 asks for verification (diff equals the §15 rows, no duplicate id, exact Status cells) that the allowed commands cannot do well, and no kit tool does it (see the gate1 issue). git diff --no-index is not on the list, and extracting the §15 rows needs grep/sed/awk.

### FX-294 · minor · tally · C001 Foundation · analyst 7

- Kit file: absd/templates/project/claude-settings.json — permissions.allow "Bash(python3 absd/tooling/trace_check.py:*)" etc.; hooks.PreToolUse command "python3 …/ownership_hook.py"

The allow-list entries do not match the `python3 -B …` form the Manager adopted (and this brief requires) so kit tools leave no absd/tooling/__pycache__/. Every -B run therefore needs a permission prompt. The hook itself runs without -B and imports ownership_check.py, so wherever it fires it writes absd/tooling/__pycache__/. No .gitignore seed covers that, and a worker cannot clean it (rm is outside its command list; .gitignore belongs to the Manager). The hook did not fire in this run because the session was not rooted in the product, so this comes from reading the code, not from seeing it happen.

### FX-295 · minor · tally · C001 Foundation · analyst 7

- Kit file: .claude/agents/analyst.md — §9 Reply format; §3 Read first item 4

The reply format is the same for every mode. Its Counts, Facts needed, money movements, expected-output and Sign-off lines mean nothing for Catalogue apply, and it has no Findings line, which the brief requires. §3 lists one playbook reading set for all modes, while the brief points to "the playbook files your manual lists for Catalogue apply", a list that does not exist.

### FX-296 · minor · tally · C001 Foundation · analyst 9

- Kit file: absd/templates/artifacts/analysis.md — §12 header, Status column (open · answered D-n · verified EXT-…); with absd/playbook/process/requirements.md ELIC-19

The kit doesn't say what Status an assumption takes once the user has signed it at the Gate 1 sign-off (ELIC-21). Rounds 1 and 2 left A-1 and A-3–A-7 'open' even though D-14 and D-15 signed them. Under ELIC-19, every unresolved A/OQ is copied to the Risk register at archive, so signed assumptions would become RISKs by mistake. The Manager only routed A-6 and A-7.

### FX-297 · minor · tally · C001 Foundation · analyst 9

- Kit file: .claude/agents/analyst.md — §2 row 'a Tester Facts result that changes a §7 fact' (Delta → Gate 1) with absd/RULES.md §2 Limits (3 rounds per gate)

The Facts Delta takes a Gate 1 round, here round 3 of 3. Any new user-owned assumption or question it raises (ELIC-19 requires them) can only lead to escalation: if the user's answer changes the analysis, folding it in is round 4. The kit has no path for a Facts result that needs one user reading after round 3. The analyst has to choose between raising the reading (risking escalation) and staying silent (against ELIC-19).

### FX-298 · minor · tally · C001 Foundation · analyst 9

- Kit file: .claude/agents/analyst.md — 5.1 Statuses (AC rows new | changed | removed | unchanged; headings new | changed | …) and 4.2 step 4

Over several Gate 1 rounds in one cycle, it is unclear what 'changed' is measured against: the catalogue, the archive, or the previous round's approved revision. A requirement already in the catalogue (applied mid-cycle at dacb1b0) keeps the heading 'new'. An AC new in this cycle but changed in round 3 has no defined status. §16 counts depend on the choice.

### FX-299 · minor · tally · C001 Foundation · analyst 9

- Kit file: absd/templates/artifacts/analysis.md — §7 fact table columns 'EXT id (existing, or reserved new …)' and 'Statement source (who · document)'

The §7 table is built for reserving UNVERIFIED facts. analyst.md 4.2 step 2 says a Facts result 'replaces the §7 row', but there is no column for a VERIFIED fact's evidence (recording + independent source). Nothing says how much of EXTERNAL-FACTS.md the analysis should copy rather than cite, so the two registers can drift.

### FX-300 · minor · tally · C001 Foundation · analyst 9

- Kit file: .claude/agents/analyst.md — 4.0 'Commands only for git (status, diff, log, show, add, commit) and python3 absd/tooling/trace_check.py'

The Delta needed read-only shell work the allow-list doesn't cover: listing and grepping the recordings, counting AC statuses for the §16 recount, checking table columns. The manual gives the analyst Bash but limits it to git and trace_check, which conflicts with checks 6.1 itself requires ('§16 counts recounted'). The round-2 analyst also had to write through the shell.

### FX-301 · minor · tally · C001 Foundation · analyst 9

- Kit file: .claude/agents/analyst.md — 4.0 'Commit after each Progress group (Status IN-PROGRESS)'

In a Delta most Progress groups are one-line 'Unchanged — <reason>' edits. A commit per group (10 groups) adds history noise and no resumability, since each group is minutes of work.

### FX-302 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §5.1 table and §6.3 ('golden outputs … that the applicability matrix marks'); §4.3

§18 golden outputs are supposed to follow the TESTING.md applicability matrix. That matrix is filled at Baseline, foundation-brief step 5 after Gate 2R, which comes after Design at step 3. It is still the empty seed when the Designer has to list goldens.

### FX-303 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.1 step 5, §6.4, §9 reply line 'contrast evidence <path>'; absd/templates/project/design-system.md §2

The manual asks for computed contrast for every token pair, and the reply asks for a contrast evidence path, even for cli/library products. Those have no colour tokens, and DSN-15 applies only to web-ui and native-app. This is pointless work, and it is unclear what evidence would satisfy it.

### FX-304 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §5.2 ('add `## 8. Protected screens register`'); absd/templates/project/design-system.md §3, §8

The template already has §8, so 'add' is redundant. The template's §3 Components columns (accessible name, states such as hover and focus) are screen-oriented and carry no profile label, so it is unclear whether a cli keeps §3. The template does not say how §8 applies to a cli with no screens.

### FX-305 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.0 ('Commit after each Progress group (Status IN-PROGRESS)'); absd/templates/artifacts/design.md Progress line

The design.md skeleton has about 10 Progress groups, so an uninterrupted run would need about 10 checkpoint commits, which is pointless work. The '[ ] commit' item also cannot truthfully be ticked inside the commit it records.

### FX-306 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.0 command list

The list of allowed commands (read history, trace_check, images, contrast/sizes/counts, commit) does not cover reading files with shell tools, writing a small measuring script, or self-checking ownership before hand-off. It also does not say where a measuring script should live so that its evidence can be reproduced.

### FX-307 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §5.1 profile table (cli sections exclude §12) and §4.2 step 3

For a cli, the table leaves out §12 Accessibility, so it reads 'N/A — profile not declared'. Yet DSN-19 cli D8 and A11Y-4 still apply, so the N/A is misleading. Separately, 4.2 step 3 ('Foundation also writes design.md … minimal but complete') does not point to the 4.1 self-checks and rubric that Gate UX applies; the brief had to fill that in.

### FX-308 · minor · tally · C001 Foundation · designer 11

- Kit file: absd/playbook/design/rubric-and-qa.md — DSN-19 table, column 'http-api, library, data-pipeline', D8 and D4

There is no guidance on scoring D8 'typed errors' (★, so it must be 5) or D4 when the library surface has no failure outcome at all, as with C001's single attribute `__version__`.

### FX-309 · minor · tally · C001 Foundation · designer 11

- Kit file: absd/tooling/trace_check.py — gate-ux check 'every requirement referenced in design.md is defined in catalogue.md'

Because QC is the catalogue's own area code, citing a foundation capability that is N/A by condition (one not in the catalogue) anywhere in design.md fails gate-ux. The Designer therefore cannot name those ids when explaining why something is out of scope, though analysis.md does ("brief QC-n").

### FX-310 · minor · tally · C001 Foundation · designer 11

- Kit file: .claude/agents/designer.md — §4.2 step 1 ('the brief's character'); absd/templates/briefs/invocation-brief.md

No field in the brief template defines 'the brief's character' (already logged by the Manager as tally-L19). The only character statement available was the owner's notes 'Design' line.

### FX-311 · minor · tally · C001 Foundation · manager 1

- Kit file: absd/templates/artifacts/cycle.md — Header 'Scale: <F | S>', 'Mode S eligibility' table, 'Close' heading

The skeleton has no Mode B variant. Scale only allows F or S, the eligibility table has no N/A guidance for Foundation (manager.md 4.3 covers F, S and C only), and the Close heading gives a tick order for DOD-2 and DOD-4 only, while DOD-5 (Foundation) has none.

### FX-312 · minor · tally · C001 Foundation · manager 1

- Kit file: .claude/agents/manager.md — 6.1 Cycle start, item 2 (nightly/live runs)

'not run yet → trigger it and wait' has no greenfield case: before the Foundation no suite, nightly or contract exists to run.

### FX-313 · minor · tally · C001 Foundation · manager 10

- Kit file: .claude/agents/analyst.md — 4.0 Every run, last bullet ("Commands only for git … and trace_check")

The command list names no read-only commands and no fallback for when the file-writing tool refuses the artifact (tally-L1). A Delta over an index-plus-parts analysis needed read-only shell commands and scripted edits of the Analyst's own files, so the run broke the rule. The Manager can only note it.

### FX-314 · minor · tally · C001 Foundation · manager 10

- Kit file: .claude/agents/manager.md — 4.10 step 2 (Risk register gets every unresolved assumption) with 6.2 sign-off and 5.4 (Manager never writes analysis.md)

After the last Gate 1 sign-off, the user's answer (D-16) must reach analysis.md §12. Otherwise A-8 and A-9 stay "open", and at archive they count as unresolved assumptions for the Risk register. The only Analyst route that edits §12 is a Delta, which costs another G1 round. The kit has no status-only Analyst touch, and does not say that a brd D-n settles an analysis assumption.

### FX-315 · minor · tally · C001 Foundation · manager 11

- Kit file: .claude/agents/manager.md — 6.2 last item; .claude/agents/analyst.md 4.3; absd/playbook/process/requirements.md ELIC-19

When the user signs off user-owned assumptions and no Catalogue apply follows (§15 unchanged), the kit has no step that updates their Status in the gated analysis.md. A-6 and A-7 (signed D-15) and A-8 and A-9 (signed D-16) still read "open" in §12. Any Analyst touch to fix them would be another G1 round, a fourth one here, which means an escalation. Downstream workers therefore read "open" while brd §9 says the assumptions are answered, and the archive step (ELIC-19: unresolved assumptions become RISK rows) would read them as unresolved.

### FX-316 · minor · tally · C001 Foundation · manager 11

- Kit file: .claude/agents/designer.md — 4.2 step 1 ("from context.md … and the brief's character")

Neither absd/templates/briefs/invocation-brief.md nor absd/templates/project/foundation-brief.md step 3 has a field for the product's character, and the Manager may not invent it because it would be a product decision. Nothing says who supplies the character or where it comes from.

### FX-317 · minor · tally · C001 Foundation · manager 11

- Kit file: .claude/agents/manager.md — 6 intro ("record both invocations and results in the gate ledger")

The gate checks run at HEAD before the Manager's commit that records the PASS. The commit that holds the PASS is therefore never itself checked, and the kit does not say which SHA a ledger PASS names: the artifact SHA, the HEAD the checks ran at, or the recording commit.

### FX-318 · minor · tally · C001 Foundation · manager 11

- Kit file: absd/templates/briefs/invocation-brief.md — Reply format block

The template's reply format (Status/Artifacts/Findings/Blockers) still differs from the worker manual's §9 format (designer.md §9 has Mode, Coverage, Rubric, Questions, Proposed rows, Lessons). This is the same conflict as tally-L3, now hit for a second worker.

### FX-319 · minor · tally · C001 Foundation · manager 12

- Kit file: absd/tooling/trace_check.py — gate gate-ux (and the requirement-id pattern)

gate-ux checks only three things: UJ and SCR ids appear in Traceability, and referenced requirement ids exist in the catalogue. It does not check that every user-visible AC is covered or that every analysis §7 failure mode has a designed message, which the Designer assumed it does. It also reports 'de_DE.UTF-8' in prose as an id with an unknown area code 'UTF-8'.

### FX-320 · minor · tally · C001 Foundation · manager 12

- Kit file: .claude/agents/designer.md — 4.1 step 5 'Measure' and §9 reply line 'contrast evidence <path>'; absd/templates/artifacts/design.md §4–§13

A cli/library-only product is still asked for contrast evidence for every token pair and for screen-only sections, including a component–state matrix with '0 blank cells'. The Designer produced an evidence file proving there are 0 colour tokens and filled ten sections with 'N/A — profile not declared'. This is pointless work.

### FX-321 · minor · tally · C001 Foundation · manager 12

- Kit file: .claude/agents/manager.md — 6.3 item 'library, http-api, data-pipeline: … contracts, runbook (ABSD:DSN-18)'; absd/playbook/design/rubric-and-qa.md checklist line 2

Both checklists ask library and http-api for a runbook, while the DSN-18 rule text requires a runbook only for data-pipeline.

### FX-322 · minor · tally · C001 Foundation · manager 12

- Kit file: .claude/agents/manager.md — 6.3 'Every UXQ/UXA has a default and impact; product questions answered by the user as D-n' and §9 reply format (≤ 15 lines, 'never contents')

The kit does not say whether a non-blocking UXQ or UXA with a designed default holds the Gate UX PASS. The ≤ 15-line, no-contents reply format also conflicts with showing the user what they sign (the context §14 convention, tally-L5).

### FX-323 · minor · tally · C001 Foundation · manager 13

- Kit file: absd/templates/artifacts/design.md — §21 "Answer (D-n)" column; also absd/templates/artifacts/design-system.md §1 (pending UXA note); .claude/agents/manager.md 6.3

Gate UX passes on the user's answers to UXQ/UXA approved as designed, but the Answer column and the design system's "pending" note are Designer-owned. No route step writes them back: GUX needs no Designer touch, and a touch would count as GUX round 2. So the gated design keeps reading "—" / "pending" while brd D-17 says answered. This is the same gap as analysis §12 Status cells after a G1 sign-off (tally-L18), now at a second gate.

### FX-324 · minor · tally · C001 Foundation · manager 2

- Kit file: absd/templates/project/context.md — §1 Product frame

foundation-brief step 1 and DOD-5 row 1 require a 'deploy target' in the context.md frame, but the context template has no slot for it.

### FX-325 · minor · tally · C001 Foundation · manager 2

- Kit file: absd/templates/project/context.md — §1 'Audiences and devices'

ELIC-11 asks for runtime classes for cli and library (terminal, shell, width, runtime versions), and QC-11 needs a runtime matrix. The context template has a field only for devices and the phone waiver, with no field for runtime classes.

### FX-326 · minor · tally · C001 Foundation · manager 3

- Kit file: absd/templates/project/context.md — §6 Data Volume Profile columns; absd/playbook/process/requirements.md ELIC-12

ELIC-12 asks for a 'maximum observed in the real source (not guessed)'. A greenfield owner has no real source and gives a ceiling to guarantee plus judgment numbers. The table has no slot for a guaranteed ceiling or for where a number comes from (observed or judgment), and ELIC-12 does not say what to record when nothing has been observed.

### FX-327 · minor · tally · C001 Foundation · manager 3

- Kit file: absd/templates/project/foundation-brief.md — Quality capabilities table heading 'select per profile'; .claude/agents/analyst.md 4.1 'selected quality capability'

Neither file says who selects the QCs or how conditional rows ('products with persistent state', 'cli (if credentials)', 'all deployable') are decided. The Manager must not make technical decisions, but the analyst manual assumes the selection already exists.

### FX-328 · minor · tally · C001 Foundation · manager 3

- Kit file: absd/templates/project/CLAUDE.md — line 4 `# <Product name>`

The seeded CLAUDE.md has a placeholder that no step fills: not foundation-brief step 1, and not manager.md 4.1 step 3 or 4.6, which only check context.md §1. Because CLAUDE.md is outside absd-project/, filling it late moves the product SHA.

### FX-329 · minor · tally · C001 Foundation · manager 3

- Kit file: absd/templates/artifacts/cycle.md — ## Counters; .claude/agents/manager.md 4.13

The kit does not say when a gate round is counted: when the producing worker is delegated, or when the gate is run. The brief template's Iteration field asks for 'gate round <n>/3' at delegation.

### FX-330 · minor · tally · C001 Foundation · manager 4

- Kit file: absd/templates/briefs/invocation-brief.md — 'Reply format' block

The brief template's reply format (Status/Artifacts/Findings/Blockers) differs from the worker manual's §9 reply format (analyst.md §9: Mode, Counts, Facts needed, Sign-off needed, Proposals). The Analyst had to choose and named it as a conflict.

### FX-331 · minor · tally · C001 Foundation · manager 4

- Kit file: absd/tooling/ownership_hook.py — settings template matcher 'Write|Edit|MultiEdit|NotebookEdit'

The write-time ownership control covers only the file-writing tools. A worker that writes through Bash, as the Analyst did here after its session refused a Write, gets no write-time check. The docstring admits this, but the Manager's after-reply checklist (manager.md 4.5) does not require an ownership_check run after each reply to cover the gap.

### FX-332 · minor · tally · C001 Foundation · manager 5

- Kit file: .claude/agents/manager.md — 4.13 Counters and escalation; 6.2 (blocking OQs answered as D-n); RULES §2 Limits

An analysis that correctly carries blocking OQs can never pass Gate 1 round 1, because the user's answers have to be folded in by an Analyst Delta, and that Delta is round 2. So every Gate 1 with a blocking question uses 2 of its 3 rounds even when the Analyst has no ✗. The kit does not say whether such a round counts or what verdict it gets.

### FX-333 · minor · tally · C001 Foundation · manager 5

- Kit file: absd/templates/artifacts/cycle.md — no section for questions asked to the user (cf. manager.md 4.2 step 4, §7 'Worker questions', brd skeleton §9 'Options shown' column)

The kit has no place to commit the question batch (questions, options, recommendation) the Manager sends to the user. Memory lives only in the repository, so after the turn boundary the brd D-n 'Options shown' column cannot be filled verbatim.

### FX-334 · minor · tally · C001 Foundation · manager 6

- Kit file: .claude/agents/analyst.md — §9 reply line "Sign-off needed (ELIC-21): §2 matrix (changed cells n) …"; absd/templates/artifacts/analysis.md §0

The Analyst's reply gives only counts of what needs sign-off, and the analysis skeleton has no table listing the changed cells with their old and new contents. To show the user what they sign, the Manager has to open the artifact, which goes against manager.md §2 ("never by rereading them whole"). This Analyst made such a table on its own initiative in §0; the kit does not ask for one.

### FX-335 · minor · tally · C001 Foundation · manager 6

- Kit file: absd/templates/artifacts/cycle.md — Route table / Gate ledger

The skeleton has no Route row for a Gate 1 revision round (an analyst Delta at G1) and no wording for a gate verdict of "open, waiting for the user's sign-off". Every revision round needs an improvised row and verdict.

### FX-336 · minor · tally · C001 Foundation · manager 7

- Kit file: .claude/agents/manager.md — 6.2 (sign-off before Catalogue apply, gate1 after) with absd/playbook ABSD:ELIC-21

This is the second round in which the gate1 catalogue check can only run after the user's ELIC-21 sign-off (same root as tally-L4, reported in round 1). This time the user noticed it and made the sign-off conditional on the check ("count this approval as conditional on that check passing ... If it fails, come back to me"). The kit has no notion of a conditional sign-off and no route for "gate1 fails after the user already signed".

### FX-337 · minor · tally · C001 Foundation · manager 8

- Kit file: .claude/agents/manager.md — 6.2 first item; absd/templates/artifacts/brd.md Traceability

6.2 checks fidelity against the 'brd Traceability' table, but no step says who fills it or when. Its content also duplicates the Analyst's analysis §16 'brd coverage' table, so the Manager copies a gated table by hand, which is pointless work.

### FX-338 · minor · tally · C001 Foundation · manager 8

- Kit file: absd/templates/briefs/invocation-brief.md — Iteration field

The field offers only 'Builder pass n/3 · gate round n/3 · halts n/3'. Gate-less modes (Facts, Baseline, Catalogue apply, Log) have no gate round to put in it.

### FX-339 · minor · tally · C001 Foundation · manager 8

- Kit file: absd/playbook/testing/external-facts.md — EXT-1 Check; manager.md 4.10 step 2

The EXT-1 Check wants a Risk register row 'blocks: flag:<name>' for each UNVERIFIED fact. Platform facts that drive no product behaviour (install procedures here) have no flag, and manager.md 4.10 adds UNVERIFIED facts to the RISK register only at archive. The kit does not say whether a RISK row is due now, or what it blocks.

### FX-340 · minor · tally · C001 Foundation · manager 9

- Kit file: .claude/agents/manager.md — 6.2 / 6.3 (no step for the user after Facts); 4.2 step 5

The kit gives no point at which the Manager tells the user a Facts result. This matters when the user tied a condition to it (D-10: 'come back to me if pip cannot refuse'). The harness lets the Manager reach the user only with a question, so a result that needs no decision has nowhere to go until the next sign-off.

### FX-341 · minor · tally · C001 Foundation · manager 9

- Kit file: absd/templates/artifacts/test_report.md — header 'Product SHA' line

Facts commits recordings and docs/testing/EXTERNAL-FACTS.md outside absd-project/, so the Facts commit itself becomes the product SHA (1df0aaa → 9f0cb70). The report header still names the SHA the facts were taken at as 'the last commit outside absd-project/ this report verified'. A report cannot name its own commit, and the skeleton does not say which SHA a Facts run should record.

### FX-342 · minor · tally · C001 Foundation · manager 9

- Kit file: absd/templates/project/foundation-brief.md — step 2a vs context.md §3 placeholders (ADR-002 after G2R)

Facts must commit recordings into the test tree, but the test tree's owner rows only arrive with ADR-002 after Gate 2R. ownership_check therefore reported 31 'unowned' warnings for tests/recordings/**. The control passes while it cannot check ownership of those paths.

### FX-343 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/playbook/testing/contracts-and-fakes.md — FAKE-2 'committed in the test tree' with .claude/agents/tester.md §4.5 and absd/templates/project/context.md §3

Facts runs before the Architect, so context.md §3 still holds the placeholder <tests/**> and no test tree exists. Recordings must still go 'in the test tree', so ownership_check reports every one as unowned (31 warnings).

### FX-344 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/playbook/testing/contracts-and-fakes.md — FAKE-6 'a re-record procedure is documented' vs ABSD:TCQ-13 and tester.md §4.5 'no TCs yet'

Facts-mode capture tooling has no home. A capture script in the test tree is a script with logic, which TCQ-13 says needs its own tests, yet Facts mode allows no TCs, and the re-record procedure must outlive the cycle.

### FX-345 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/playbook/testing/external-facts.md — EXT-2 evidence rule and FAKE-6 naming

The rules assume API responses. For a platform or CLI system (pip, the interpreter) the 'real response' depends on an input the product does not have yet at Facts (no wheel exists), and the kit gives no guidance on probe inputs or on what a CLI recording should contain (command, environment, exit code, both streams, network state).

### FX-346 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/templates/artifacts/test_report.md — §15 column 'Kind: RISK / DEBT / DEF'

The Facts brief (and the Manager's cycle.md resume point) expects proposed context.md §7 status changes in §15, but the Kind column offers only RISK, DEBT and DEF.

### FX-347 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/templates/artifacts/test_report.md — header 'Facts: its own, earlier SHA'; with .claude/agents/tester.md §4.0 step 6 and absd/RULES.md §6

The single Facts commit itself changes paths outside absd-project/ (docs/testing/EXTERNAL-FACTS.md and the recordings), so it moves the product SHA. The kit does not say whether the header and the reply name the SHA the facts were taken at or the new product SHA.

### FX-348 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/templates/artifacts/test_report.md — Progress line and headings §3–§6

The skeleton's Progress line lists only Verify steps, while tester.md 4.0 step 3 asks for this mode's steps. Headings §3–§6 carry <n> placeholders as part of the heading text that 'keep every heading' protects, so a Facts report must keep unfillable placeholder headings.

### FX-349 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/templates/artifacts/analysis.md — §7 failure table (no EXT column) vs the EXTERNAL-FACTS.md failure-mode table keyed by EXT

The Analyst's failure rows (e.g. a truncated wheel, a missing wheel) cite no fact id, but the register's failure table needs an EXT id per row. So the Tester has to create a fact for pip's error answers that the analysis never reserved.

### FX-350 · minor · tally · C001 Foundation · tester 8

- Kit file: absd/templates/artifacts/test_report.md — Facts section column 'Proposed RISK `blocks: flag:<name>`' (and tester.md §4.5 step 2)

The column and step 2 assume every UNVERIFIED fact sits behind a feature flag. For facts that only install procedures and release records rest on, the kit gives no Blocks form; only EXT-4 says such a fact stays in the Risk register.

### FX-351 · minor · tally · C001 Foundation · tester 8

- Kit file: .claude/agents/tester.md — §3 Read first, item 5

Every mode, Facts included, must read the full checklist of every file in absd/playbook/testing/ plus requirements.md and definition-of-done.md. A Facts run applies only EXT, FAKE and PRIV-7, so most of that reading is pointless for it.

### FX-352 · minor · tally · setup

- Kit file: absd/tooling/absd_sync.py — install 'Next steps' item 3 vs README.md 'Start a new product' and absd/templates/project/foundation-brief.md step 0/1

The tool says 'Ask it to run Bootstrap (Mode B ...)'. The README says to tell the Manager what you want to build, and the Manager will notice the empty project frame and start the Foundation cycle itself. A first-time owner cannot tell whether to say 'run Bootstrap' or describe the product. Neither text says to bring product notes like the OWNER.md to the first session; foundation-brief step 1 only says the Manager writes the frame 'with the user'.

### FX-353 · minor · tally · setup

- Kit file: absd/tooling/absd_sync.py — install 'Next steps' item 1 (git add -A)

The printed commit command stages everything with `git add -A`. In an existing codebase, which the README sends through the same install, it would sweep unrelated product changes, untracked files and build junk into the commit marked 'ABSD-Sync: install', which ownership_check then accepts as a kit sync. A fresh repository is safe.

### FX-354 · minor · tally · setup

- Kit file: absd/templates/project/claude-settings.json — hooks.PreToolUse[0].hooks[0].onFailure

The seeded hook entry uses "onFailure": "block" (repeated in the ownership_hook.py docstring). As far as I know this is not a documented Claude Code hook field; I did not verify it. If Claude Code ignores it, a hook crash (exit code other than 2, e.g. an import error) does not block the write, so the guard fails open while the config suggests it fails closed. The hook itself does return 2 on bad JSON input.
