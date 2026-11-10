# Proposal: harvest from ECC (everything-claude-code v2.2.3, MIT, commit d2ef268) — 2026-11-10

Source: a read-only review of ECC (nothing installed or run), in two parts: engineering practice and security
(including a safety review of every hook). Verdict: **do not install ECC next to ABSD** — duplicate agents that
self-activate, contradicting rules, and hooks that send session content to a model, run commands from repo config,
rewrite files and compete with the ownership hook. Take ideas through enrichment only; each NEW item below has a
rule draft (text, Why, Check, target agent/gate). Dedupe each against the playbook before writing it (four
engineering items are marked unverified in their sections).

Shortlist (both reports):
- Auditor: evidenced findings (file:line, trigger, outcome, why guards miss it; zero findings is valid); security
  findings labelled by attacker reachability.
- GATE: piped gate commands keep their exit status (`set -o pipefail`).
- Auditor: planned-vs-actual diff per work package in every cycle.
- Architect: entity states that make invalid combinations unrepresentable.
- RULES §8: a worker's final reply is the deliverable. Builder: per-WP checkpoint; callers/data shapes from search.
- SEC-15 (new): products that call an LLM. SEC-16 (new): agent configuration as supply chain (kit and products).
- SEC-7: concrete SSRF and file-path rules with hostile-input sets. SEC-14: concurrent duplicate request (double spend).
- Settings template: deny secret paths, pipe-to-shell, remote copy. Kit tool idea: block `git commit --no-verify`.
- Structure: long procedures as on-demand skills; model tier per agent; optional second auditor on money/permission paths.
- Auditor security procedure: Gate 2R design review + Gate 3 evidence checklist (security report §4).

---

## ECC v2.2.3 vs ABSD — engineering practice (excl. security, stack reviewers)

Read-only review. ECC root below = `ecc/` (scratchpad/eval/ecc). Nothing in ECC was executed. "UNVERIFIED" marks claims
I did not confirm by reading.

## 1. Map

| ECC component | What it is | ABSD counterpart |
|---|---|---|
| `agents/planner.md` | Free-form phased plan (steps, files, risk, test strategy) | Analyst (`analysis.md`) + Architect work packages (ARCH-24) — ABSD far stricter |
| `agents/architect.md`, `code-architect.md` | System design advice, ADR suggestions | Architect + ARCH-* + Gate 2/2R (XCA-10) |
| `agents/tdd-guide.md`, `skills/tdd-workflow` | Red-green-refactor, 80 % coverage, edge-case list | Tester; ORACLE (red before green), VAR, GATE coverage ratchet |
| `agents/e2e-runner.md`, `skills/e2e-testing` | Playwright journeys | E2E-*, end-to-end-profiles (multi-profile, stronger) |
| `agents/pr-test-analyzer.md` | Do tests cover the changed behaviour? | Auditor L-levels, TRACE, XCA-4 (test changes since T-SHA) |
| `agents/code-reviewer.md` | Diff review with confidence filter, false-positive list | Auditor L4 + CODE-* + XCA-7 severity calibration |
| `agents/code-simplifier.md`, `refactor-cleaner.md` | Behaviour-preserving cleanup, dead-code removal in batches | CODE-3/5 (limits, no dead code); no "cleanup pass" role (by design: YAGNI/WP) |
| `agents/silent-failure-hunter.md` | Swallowed errors, bad fallbacks | CODE-8 |
| `agents/type-design-analyzer.md` | Make illegal states unrepresentable | CODE-11 + ARCH-6 (invariants) — partial |
| `agents/build-error-resolver.md` (+ per-stack) | Minimal-diff build fixing | Builder (halts to `clarification_needed.md`) |
| `agents/doc-updater.md` | Keep docs in sync | DOD rows / OPS fresh-clone (partial) |
| `contexts/dev|research|review.md` | Mode prompts injected per session | ABSD routes/modes (RULES §2), per-agent manuals |
| `rules/common/*.md` | Always-loaded generic rules (workflow, testing 80 %, agents, performance/model choice) | `absd/RULES.md` + playbook |
| `skills/` (314) | On-demand procedures loaded by description match | None — ABSD has manuals + playbook "Read first" lists |
| `hooks/hooks.json` | gateguard fact-force, suggest-compact, pre:compact state save, config-protection, stop:format-typecheck, session-end/evaluate-session (continuous learning) | ABSD has no hooks; enforcement is gates + CI + `kit_lint` |
| `the-longform-guide.md` | Context/memory, sub-agent iterative retrieval, pass@k / pass^k | RULES §9 size budgets, Resume brief, FAKE-13 (k repeats) |
| `skills/continuous-learning*`, `stop:evaluate-session` | Auto-extract "instincts" from sessions | ENR harvest + LEDGER (human-curated, stronger provenance) |

## 2. Overlap / conflict if installed alongside ABSD

- **Duplicate agent names**: `architect` exists in both (`ecc/agents/architect.md` vs `.claude/agents/architect.md`).
  With a manual install into `~/.claude/agents/`, project-level ABSD wins in Claude Code precedence (UNVERIFIED for every
  harness), but descriptions overlap and the model may pick the wrong one.
- **"Use PROACTIVELY / MUST BE USED" descriptions** (`planner`, `code-reviewer`, `tdd-guide`, `refactor-cleaner`) plus
  `rules/common/agents.md` "Immediate Agent Usage — no user prompt needed" directly contradict RULES "only the Manager
  delegates/speaks", "no code before Gate 2" and "agents never modify artifacts they do not own". code-simplifier and
  refactor-cleaner have Write/Edit and would edit outside a WP — breaks CODE-14 (one WP per commit) and XCA-9.
- **Contradictory rules**: `rules/common/development-workflow.md` step 0 "GitHub code search first … prefer adopting
  open-source" vs CODE-12 (dependency only if `architecture.md` lists it); "80 % coverage" vs ABSD's ratchet floor
  (GATE); "conventional commits" vs CODE-14 subject format `absd(C###): …`; `contexts/dev.md` "Get it working, then
  right" vs ABSD red-before-green / correctness-first.
- **Hooks**: `pre:edit-write:gateguard-fact-force` denies the first Edit/Write — would stall a Builder mid-WP (and Builder
  halts must be atomic). `stop:format-typecheck` and `post` formatters rewrite files outside the WP. `pre:config-protection`
  may block legitimate gate-config edits owned by the Tester (UNVERIFIED what it matches). `stop:evaluate-session`
  writes learned "instincts" into user memory — an un-provenanced rule channel parallel to ENR.
- **Prompt Defense Baseline** block in every agent: harmless but adds tokens per invocation (cost vs RULES §9).
- Verdict: do **not** install ECC alongside ABSD. Harvest ideas through enrichment only.

## 3. Idea-by-idea

| # | ECC idea (path) | Status |
|---|---|---|
| 1 | Phased plan with files, dependencies, risk (`agents/planner.md`) | Already: ARCH-24 work packages, ARCH-7 |
| 2 | Red-green-refactor, verify test fails first (`agents/tdd-guide.md`) | Already: ORACLE red-before-green |
| 3 | Edge-case list: null, empty, boundary, unicode, 10k items, races (`tdd-guide.md`) | Already: VAR (boundaries, volume, races, absent inputs) |
| 4 | 80 % coverage fixed threshold | Skip: ABSD ratchet + no-untested-unit gate (GATE) is stronger |
| 5 | Swallowed errors, dangerous fallbacks (`silent-failure-hunter.md`) | Already: CODE-8 |
| 6 | Dead code removal (`refactor-cleaner.md`) | Already: CODE-5. Its batch-safety protocol is for legacy cleanup — skip unless a "ratchet cleanup" WP type is added |
| 7 | Reviewer Pre-Report Gate, proof for HIGH/CRITICAL, "zero findings is valid", false-positive list (`agents/code-reviewer.md`) | Partly: XCA-7 calibration, XCA evidence rule, finding schema RULES §6. **Gap**: no explicit anti-manufacture / false-positive rule found (UNVERIFIED that none exists in RULES §6) → NEW-1 |
| 8 | Read surrounding code / trace one caller before flagging (`code-reviewer.md`) | Covered implicitly by XCA-5 probes; folded into NEW-1 |
| 9 | Type design — illegal states unrepresentable (`type-design-analyzer.md`) | Partial: CODE-11 immutability, ARCH-6 invariants. **Gap**: no rule that a state machine / mutually exclusive fields are encoded so invalid combinations cannot be constructed → NEW-2 |
| 10 | Change-impact before & diff reconciliation after (`skills/change-impact/SKILL.md`) | Partial: Architect §4.4 survey, XCA-11 (Mode S real diff), ARCH-24 file lists. **Gap**: Auditor reconciling *planned files per WP vs actual diff* for full cycles not found (UNVERIFIED — may sit in auditor L-levels) → NEW-3 |
| 11 | GateGuard fact-forcing before first edit (`skills/gateguard`, hook) | Idea worth taking as manual rule, not as hook → NEW-4 |
| 12 | Santa method: two independent reviewers, same rubric (`skills/santa-method`) | Partial: Auditor independence (XCA-1/2). Two-auditor rule is costly — skip except optional for Critical-path cycles; ranked low |
| 13 | Verification loop: build/type/lint/test/diff → PASS/FAIL report (`skills/verification-loop`) | Already: XCA-2 (auditor reruns all), GATE-* "a check that did not run is RED" |
| 14 | `set -o pipefail` so piped output does not hide exit code (`verification-loop`) | **Gap (small, concrete)**: GATE says unrun = RED but piping a test command through `tail` reports success → NEW-5 |
| 15 | Delegation completion contract: final message is the deliverable; no "waiting for background agents"; delegate only what doesn't fit one context (`rules/common/agents.md`) | Partial: ABSD Resume brief (RULES ~l.60). **Gap**: worker reply must not end with pending background work → NEW-6 |
| 16 | Orchestrator evaluates each sub-agent return, asks follow-ups, max 3 (longform guide "Iterative Retrieval") | Already: Manager gate reviews + 3-iteration cap (rule 7) |
| 17 | Strategic compaction at phase boundaries; save state pre-compact (`skills/strategic-compact`, `pre:compact` hook) | Partial: artifacts are on-disk state; RULES §9 budgets. **Gap**: no rule for a long-running agent (Builder across many WPs) to checkpoint progress before context exhaustion → NEW-7 |
| 18 | Context budget: live meter, don't estimate (`skills/context-budget`) | Skip: harness-specific |
| 19 | Skills as on-demand procedures (`skills/*/SKILL.md`, description-triggered) | Structural idea → NEW-8 (kit structure, not a rule) |
| 20 | Mode contexts (`contexts/*.md`) | Already: ABSD routes/modes + per-agent manuals |
| 21 | Model tiering per agent (`rules/common/performance.md`, frontmatter `model:`) | Possibly NEW-9 — RULES §8 frontmatter; UNVERIFIED whether ABSD manuals set `model:` |
| 22 | pass@k vs pass^k (longform guide) | Already: FAKE-13 k repeats; could cite pass^k as threshold wording (PATCH) |
| 23 | Continuous learning from sessions (`skills/continuous-learning-v2`, `stop:evaluate-session`) | Skip: ENR + LEDGER is curated and provenanced; auto-instincts conflict with ENR-1/4 |
| 24 | Research & reuse / GitHub code search before writing (`development-workflow.md` step 0) | Partly conflicts with CODE-12; could become Architect ADR alternative "existing library considered" — ARCH ADR already lists alternatives (UNVERIFIED wording). Skip |
| 25 | Stop hook: no stray `console.log` (`stop:check-console-log`) | Already: CODE-2 banned-API list / CODE-5 |
| 26 | doc-updater | Already: OPS fresh-clone-from-docs, DOD |
| 27 | Build-error-resolver minimal diff | Skip: ABSD Builder halts rather than patches beyond the blueprint (rule 4) |

### Rule drafts (stack-neutral)

**NEW-1 (XCA)** — Raise a finding only when it names file and line, the trigger (input or state) and the bad outcome, and
says why existing guards (types, validation, framework, caller) do not stop it; a Major/Critical finding without all four
is demoted or dropped. A level with zero findings is reported PASS with its evidence, never padded.
- *Why:* manufactured or speculative findings cost fix iterations against the 3-iteration cap and erode trust in real ones.
- *Check:* Gate 3 — Manager rejects any finding row missing location, trigger, outcome or guard analysis.
- *Applies when:* always. Target: Auditor manual, RULES §6 finding schema (add "Trigger" and "Why guards miss" columns). Provenance: industry baseline (ECC `agents/code-reviewer.md`).

**NEW-2 (ARCH/CODE)** — Model each entity state and each mutually exclusive field group so invalid combinations cannot be
constructed: one state field (or tagged variant) per lifecycle, state-specific data owned by that state, transitions only
through methods that check the source state.
- *Why:* two booleans or nullable pairs admit "settled and open" rows that no validator catches.
- *Check:* Gate 2R — every lifecycle in `analysis.md` maps to one state type; L4 grep for parallel status flags on one entity; VAR state-transition tests reject invalid events.
- *Applies when:* the product has stateful entities. Target: Architect (component spec), Auditor L4.

**NEW-3 (XCA)** — Reconcile each WP's planned file list (ARCH-24) with its commit's diff; any unplanned file, endpoint,
config key or dependency is a finding.
- *Why:* scope drift outside the blueprint evades Gate 2 coverage.
- *Check:* auditor table WP → planned vs actual files.
- *Applies when:* always. Target: Auditor (Mode S already does this via XCA-11 — extend to full cycles).

**NEW-4 (Builder)** — Before the first edit of an existing file in a WP, record in `build_log.md` its importers/callers
and the data shapes it reads or writes, from search results, not memory.
- *Why:* edits based on guessed call relationships break untouched callers (ECC reports A/B gain, unverified).
- *Check:* build_log rows per modified existing file; Auditor samples one.
- *Applies when:* brownfield files. Target: Builder.

**NEW-5 (GATE)** — Every gate or test command whose output is piped or filtered preserves the command's exit status
(e.g. bash `set -o pipefail`, PowerShell `$LASTEXITCODE` check).
- *Why:* `test | tail` returns the filter's status, so a red suite reads green.
- *Check:* `kit_lint`/CI lint greps workflow and script lines with `|` after a test/build command without pipefail; gate proven able to fail (existing GATE rule) catches the rest.
- *Applies when:* always.

**NEW-6 (RULES §8)** — A worker's final reply is its deliverable: it never ends with work pending in background tasks or
sub-delegations; anything it started it collects or cancels first.
- *Why:* "waiting for X" replies leave the Manager with no artifact and an unknown state.
- *Check:* Manager rejects a reply referencing unfinished background work.
- *Applies when:* always.

**NEW-7 (Builder/RULES)** — A long-running agent writes its progress (WP done, next WP, open decisions) to its artifact
after each WP, so a Resume brief can continue after context loss without re-reading the transcript.
- *Why:* compaction mid-WP loses state; Resume briefs (max 2) need a durable checkpoint.
- *Check:* `build_log.md` has a status row per completed WP before the next WP's first commit.
- *Applies when:* multi-WP builds. (UNVERIFIED that build_log already mandates this — check builder manual.)

**NEW-8 (kit structure)** — Consider splitting long per-situation procedures out of manuals into on-demand "procedure"
files loaded only when triggered (ECC skills pattern): e.g. brownfield adoption, migration authoring, flake triage. Keeps
manuals under the 9k budget. Not a rule; a MINOR restructuring proposal.

**NEW-9** — Declare a model tier per agent in frontmatter (reasoning-heavy: Analyst/Architect/Auditor; mechanical: Builder
WP execution). UNVERIFIED current ABSD frontmatter. Low value; cost only.

## 4. Top 10 ranked

1. NEW-1 finding proof / no manufactured findings (Auditor) — high value, cheap.
2. NEW-5 pipefail / exit status preserved in gate commands — concrete escape class.
3. NEW-3 WP planned-vs-actual diff reconciliation for every cycle.
4. NEW-2 illegal states unrepresentable (Architect + L4).
5. NEW-6 worker reply completeness / no dangling background work.
6. NEW-7 per-WP progress checkpoint for resume after context loss.
7. NEW-4 Builder records callers/data shapes before editing existing files.
8. NEW-8 on-demand procedure files (skills pattern) to relieve manual budgets.
9. pass^k wording for FAKE-13 thresholds (PATCH).
10. Optional dual-auditor (santa-method) for money/permission-path cycles — only if escapes show single-auditor blind spots.

Everything else in ECC's engineering surface (planning, TDD, e2e, dead code, silent failures, verification loop, mode
contexts, continuous learning) is already in ABSD, generally in stricter, checkable form.

---

## ECC (v2.2.3) security material vs ABSD — evaluation

Scope: read-only. Nothing from ECC was installed or executed. Paths are relative to the ECC clone
(`.../scratchpad/eval/ecc`). "Unverified" marks claims inferred from grep/partial reads only.

Headline: ABSD's `absd/playbook/security/baseline.md` (SEC-1..14, PRIV-1..8) plus `testing/access-visibility.md`
(ACCESS-1..14) already covers, and is more checkable than, ECC's generic app-security checklists (OWASP list, secrets,
input validation, CSRF/CSP, rate limits, supply chain). ECC's real additions are about **LLM/agent security**
(products that embed a model or tools; and the development pipeline itself) plus three app gaps (SSRF detail,
path containment detail, money-path race). ECC's hooks are mostly productivity/telemetry; several send data off-box
or execute repo-configured commands — none should be adopted as-is.

## 1. Inventory (security-relevant)

| Path | What it is |
|---|---|
| `the-security-guide.md` | Essay on *agent* security: attack surfaces (chat, email, PR comments, MCP), Claude Code CVEs, sandboxing, deny-lists, hidden-Unicode scans, least agency, logging, kill switches, memory hygiene, minimum-bar checklist |
| `agents/security-reviewer.md` | Reviewer agent (sonnet): OWASP Top-10 walk, pattern table (secrets, shell, SQL concat, innerHTML, fetch(userUrl), balance check without lock, no rate limit), false-positive list; npm-centric |
| `rules/common/security.md` | 8-item pre-commit checklist + "stop, call security-reviewer, rotate secrets" protocol |
| `rules/<lang>/security.md` (≈22 files: web, react, csharp, python, java, go, …) | Stack-specific idioms (e.g. web: nonce CSP, SRI, CSRF on forms) |
| `skills/security-review/SKILL.md` | 10-section checklist (secrets, validation, SQLi, authN/Z, XSS, CSRF, rate-limit, data exposure, Solana, deps) + pre-deploy checklist; vendor-specific (Supabase, Vercel) |
| `skills/security-scan/SKILL.md` | Wrapper for external "AgentShield" scanner of `.claude/` (CLAUDE.md, settings, MCP, hooks, agents); needs npx install |
| `skills/agent-security-hardening/SKILL.md` | Best item: trust-boundary map `source→parser→validator→side effect`; identifier/env/URL validation (SSRF, DNS rebinding, embedded creds); filesystem containment; temp data/creds; bounded tool output |
| `skills/mcp-dependency-review/SKILL.md` | Static classification of MCP/package/image selectors: exact/digest SAFE, tag/bare HIGH, range MEDIUM, path/URL REVIEW |
| `skills/security-bounty-hunter/SKILL.md` | Reachability-first triage: SSRF, auth bypass, deser/upload RCE, SQLi, cmd-inj, traversal, auto-XSS (CWE-mapped); "skip" list of low-signal findings |
| `skills/gateguard/SKILL.md`, `skills/safety-guard/SKILL.md` | Agent behaviour gates: fact-forcing before first edit; confirm destructive commands; freeze writes to a dir |
| `skills/llm-trading-agent-security`, `defi-amm-security`, `hipaa-compliance`, `django-/springboot-/laravel-/quarkus-/perl-security` | Domain/stack-specific; not reviewed in depth |
| `skills/repo-scan/SKILL.md` | Installs an external skill from a pinned commit (download) |
| `hooks/hooks.json`, `hooks.metadata.json`, `codex-hooks.json`, `qoder-hooks.json`, `hermes/*.py`, `memory-persistence/` | Hook graph — see §3 |
| `scripts/hooks/*.js` (61 files), `scripts/lib/llm-summary.js`, `skills/continuous-learning-v2/hooks/observe.sh`, `.../agents/start-observer.sh`, `observer-loop.sh` | Code the hooks run |

## 2. Idea-by-idea verdict

### Already in ABSD (skip, cite)
| ECC idea (path) | ABSD |
|---|---|
| Hardcoded secrets, secrets in history, rotate on leak (`rules/common/security.md`, `skills/security-review` §1) | SEC-8 (scanner over tree+history, GATE-13, XCA-1), SEC-9 |
| Validate all input, allow-list, upload checks, XXE, insecure deserialisation (security-reviewer OWASP 4/8) | SEC-6 |
| SQLi, shell with input, innerHTML, header/CRLF, redirects (pattern table) | SEC-7 (+ CODE-2 banned APIs, VAR-11 hostile payload TC) |
| AuthN, password hashing, JWT/session (OWASP 2) | SEC-1, SEC-2 |
| Auth on every route, broken access, CORS (OWASP 5) | SEC-4, ACCESS-1..14, SEC-10 http-api row |
| Rate limiting, expensive ops (`skills/security-review` §7) | SEC-3 (stronger: trusted key, lockout without victim lockout) |
| Errors without stack traces; no secrets in logs (§8) | SEC-11, SEC-12, PRIV-6 |
| CSP nonces, CSRF, SameSite cookies, HSTS (`rules/web/security.md`) | SEC-10 web-ui row |
| npm audit / deps / lockfiles / Dependabot (§10) | SEC-13 (SCA+SAST every push, Critical/High=0, pinned digests, SBOM) |
| Security event logging (OWASP 10) | SEC-12 |
| Client-supplied prices/balances | SEC-5 |
| "Run security review on new endpoint/auth/payment" (When to Run) | SEC-14 threat model + Auditor L5 |
| PII handling | PRIV-1..8 (far more complete than ECC) |

### NEW — worth taking (drafts, stack-neutral)

**N1. Model and tool-call boundary for products that embed an LLM or agent** (source: `the-security-guide.md`
"lethal trifecta", "Sanitization", "Approval Boundaries"; `skills/agent-security-hardening` §1, §5). ABSD only names
LLMs as metered dependencies (SEC-3).
- *Rule (SEC-15):* Treat model output as untrusted input: every value a model returns is validated against a declared
  schema (SEC-6) before it reaches a sink, a state change or a user; a model never holds a credential or permission
  beyond the calling principal's; any component where untrusted content, private data and an outbound channel meet
  (the "lethal trifecta") has a server-side approval or allow-list step between model and side effect — never a
  prompt instruction; money, access and destructive actions never depend on model output alone.
- *Why:* prompt injection through documents, mail, web pages, images, tool results turns read access into actions.
- *Check:* `architecture.md` lists each model call with input sources, output schema, allowed side effects;
  TC: an injected-instruction fixture (hidden text, invisible Unicode, in an image/PDF) produces no out-of-schema
  output and no side effect; TC: model output exceeding schema/size is refused.
- *Applies when:* the product calls a model or exposes tools to one. *Agent/gate:* Analyst (threat inputs),
  Architect (model-call table), Gate 2R, tester abuse TCs, Auditor L5.

**N2. SSRF and outbound-destination detail** (source: `skills/agent-security-hardening` §2; `security-bounty-hunter`
CWE-918). SEC-7 says "server-side fetches allow-listed" but no checkable detail.
- *Amend SEC-7 (or add to SEC-6):* a URL from input is parsed, scheme allow-listed, host required, embedded
  credentials refused; resolved addresses checked against private, loopback, link-local and metadata ranges **after
  resolution and on every redirect** (DNS rebinding); redirects not followed by default.
- *Check:* hostile-payload TC set per fetch sink: loopback, 169.254.169.254, IPv6/decimal-encoded IP, `user:pass@`,
  redirect to private address, rebinding host (fake resolver).

**N3. Path containment detail** (`agent-security-hardening` §3). Amend SEC-7 "paths confined to a base directory":
canonicalise then check prefix; refuse absolute paths, `..`, symlinks escaping the base, NUL, and reserved device names
on every OS. *Check:* traversal TC set per file sink (VAR-11).

**N4. Money/state race** (security-reviewer "Balance check without lock — CRITICAL"). ABSD has ELIC-17 and ARCH
concurrency register; make the security angle explicit: *SEC-14 walk list adds "concurrent duplicate request (race,
double-spend, TOCTOU)"*; *Check:* a parallel-request TC per money/entitlement mutation asserts one effect.

**N5. Agent-configuration supply chain (kit and product repos)** (`the-security-guide.md` "Hidden Unicode",
CVE-2025-59536/CVE-2026-21852 discussion; `skills/mcp-dependency-review`; `skills/security-scan` concept).
- *Rule (SEC-16):* Treat agent instructions and configuration (`CLAUDE.md`, agent manuals, skills, hook
  settings, MCP config, prompt templates) as code under SEC-13: no invisible/bidi control characters or hidden
  comment payloads; no hook or MCP command fetching or executing remote content; MCP servers, packages and images
  referenced by exact version or digest (tag/bare = High, range = Medium); no setting that auto-approves project MCP
  servers or overrides the model API endpoint.
- *Check:* a kit_lint-style scanner (stdlib) for U+200B–200D, U+2060, U+FEFF, U+202A–202E, U+2066–2069 in those
  files; grep for `curl|wget|nc |scp|ssh|base64,|enableAllProjectMcpServers|ANTHROPIC_BASE_URL`; selector classifier
  per `mcp-dependency-review` table. *Agent/gate:* CI (GATE-13) + Auditor L5; also run on the kit itself.

**N6. Least agency for pipeline sessions** (`the-security-guide.md` "Restrict tools and paths", "Approval
Boundaries"). The product settings template ships a deny-list for secret-bearing paths (`~/.ssh`, cloud CLI creds,
`.env*`), pipe-to-shell, and remote-copy commands; deploy/workflow dispatch requires a human. *Check:* template
contains the list; kit_lint verifies. Platform mechanics → RULES §8. (Kit-level, not a product rule.)

**N7. Reachability-first triage of findings** (`skills/security-bounty-hunter` "Skip These"). For the Auditor: each
security finding states entry point → sink reachability and principal needed; severity follows reachability
(unreachable/test-only → Low). Reduces noise; fits audit severity rules (`process/audits.md`).

### Skip
| ECC idea | Why |
|---|---|
| Stack/vendor rules (`rules/<lang>/security.md`, Supabase/Vercel/Solana sections) | Stack-specific; ABSD is stack-neutral; SEC-7/10 already state the outcome |
| "Rate limiting on all endpoints" | Weaker than SEC-3 (keyed, targeted) |
| AgentShield / repo-scan | Third-party npx/remote install; replace with N5 stdlib scanner |
| Prompt Defense Baseline header in `agents/security-reviewer.md` | Prompt-only control; ABSD relies on tool/ownership enforcement |
| Kill switches, heartbeats, process-group kill, sandbox compose files, separate agent identities, memory rotation | Operator/harness hygiene, not product rules; could be a one-line note in RULES §8 at most |
| Guardrail paragraph next to external links | Not checkable; N1/N5 cover the risk |
| gateguard / safety-guard | Workflow behaviour, not security; ABSD's ownership hook + gates already constrain |
| security-reviewer "Emergency Response" | Covered by SEC-8 rotation + escaped-defect process |

## 3. Hooks safety review

All Claude hooks are `node -e` one-liners that locate the plugin root (env `CLAUDE_PLUGIN_ROOT` or
`~/.claude/plugins/cache/...`) and `require()` `scripts/hooks/plugin-hook-bootstrap.js` /
`lifecycle-hook-bootstrap.js`, which run the named script via `run-with-flags.js` under profile flags
(`minimal|standard|strict`). Implication: the code actually run lives in a plugin cache outside the repo and changes
with plugin updates.

| Hook (event/matcher) | Runs | Reads/writes/network | Risk | ABSD conflict | Verdict |
|---|---|---|---|---|---|
| PreToolUse Bash → `pre-bash-dispatcher.js` (block-no-verify, auto-tmux-dev, tmux/push reminders, commit-quality, gateguard, command log) | lints staged files before commit, blocks `--no-verify`, may start dev server in tmux | reads git index, spawns linters/tmux; logs commands (`post-bash-command-log`) | command log may capture secrets typed in commands; auto-tmux spawns processes | none (Bash) | block-no-verify idea: rewrite-as-kit-tool (small); rest skip |
| PreToolUse PowerShell / Write / Edit\|Write → gateguard-fact-force, doc-file-warning, suggest-compact | denies first edit until "facts" given; warns on .md | local state files | friction; denies writes ABSD agents legitimately make (artifacts are .md) | **yes**: second PreToolUse gate on Write/Edit; doc-file-warning fights ABSD Markdown artifacts | skip |
| PreToolUse `.*` → `observe-runner.js` (async) → `continuous-learning-v2/hooks/observe.sh` | records every tool call; lazily starts `start-observer.sh` → `observer-loop.sh` which runs `claude -p` in the background, told to "use the Write tool… do NOT ask for permission" | writes observations under project/home dirs; **sends tool-call content to the model API** (egress, cost); background process outlives session; writes "instincts" that later load into context | data exfiltration to API (redaction regexes exist, unverified completeness), memory poisoning, unattended writes | its Writes bypass agent_type → allowed by ownership hook as plain session (unverified) | skip |
| PreToolUse Bash\|…\|Edit → `governance-capture.js` | logs "governance events" to a state store | local writes | telemetry of commands | none | skip |
| PreToolUse Write\|Edit\|MultiEdit → `config-protection.js` | exit 2 on editing linter/formatter configs | none | — | overlaps/compatible: ownership hook already locks agent config; both block independently (both must pass) | concept only; ABSD could add lint-config paths to ownership table — skip the script |
| PreToolUse `^mcp__` / PostToolUseFailure `^mcp__` → `mcp-health-check.js` | probes MCP server health; on failure may run a reconnect | **HTTP request to configured MCP URL with configured headers; spawns the configured MCP `command`/`args`** | executes commands from (possibly repo-controlled) MCP config — exactly the CVE pattern the guide warns about | none | skip |
| PreToolUse Edit\|Write\|MultiEdit\|NotebookEdit → gateguard; PreToolUse `.*` → `hookify-runtime.js` (+UserPromptSubmit, Stop) | evaluates project-local `.claude/` Hookify markdown rules (regex with timeout) | reads repo `.claude/`; can block/ask for another turn | repo-controlled policy can block or steer the agent; no code exec found (regex only) | conflicts: competes with ownership hook on the same tools; `.claude/` is Manager-owned in ABSD | skip |
| UserPromptSubmit → hookify | as above on prompts | — | — | — | skip |
| PreCompact → `pre-compact.js` | appends compaction notes; may embed LLM summary | writes session files under `~/.claude/sessions` | stores transcript fragments on disk | none | skip |
| SessionStart → `session-start-bootstrap.js` → `session-start.js`; `plan-canvas-sessions.js` | injects previous session summary into context; lists Plan Canvas reviews | reads `~/.claude/sessions`; plan-canvas: **loopback HTTP only** | cross-session memory injection (poisoning vector the guide itself names) | conflicts with ABSD's `context.md` as the single memory | skip |
| PostToolUse `.*` → `posttooluse-dispatcher.js` (quality-gate, design-quality-check, post-edit accumulator/format/typecheck, console warn, governance, session-activity-tracker, observe, ecc-metrics-bridge, context-monitor, skill-run-tracker, hookify) | formatters/typecheck on edited files; metrics | spawns local bins or **`npx`** (may download packages); writes `~/.claude/metrics/tool-usage.jsonl`, costs.jsonl, state | auto-format **modifies files after the agent wrote them** (edits not in the agent's diff; can touch other owners' files); npx download; local telemetry | yes: post-write mutation sidesteps ownership attribution | skip |
| PostToolUseFailure Skill → skill-run-tracker | logs | local | telemetry | none | skip |
| Stop ×9: check-console-log, cost-tracker, desktop-notify, evaluate-session, format-typecheck, hookify, plan-canvas-pending, session-end, (async) | cost/metrics, OS notification (osascript/PowerShell), session summary via **`claude -p` (`lib/llm-summary.js`, haiku default)**, learned-skill extraction, format+typecheck | writes `~/.claude/sessions`, metrics, learned skills path; **transcript summary sent to model API**; plan-canvas loopback | egress of session content; unattended file formatting at end of turn; learned skills = persistent instructions | format at Stop mutates tree outside ownership | skip |
| SessionEnd → session:end:marker | marker file | local | — | none | skip |
| `codex-hooks.json`, `qoder-hooks.json` | same SessionStart bootstrap for other harnesses | as SessionStart | as above | — | skip |
| `hermes/config-protection.py`, `check-console-log.py` | Python ports for "Hermes" harness | local | — | — | skip |

Not found (grep over `scripts/hooks`): auto-commit or auto-push (hooks only *block* `--no-verify` and remind before
push); remote third-party telemetry endpoints (network = MCP probes, `claude -p`, loopback). `insaits-security-wrapper.js`
spawns a Python monitor only when an env flag is on; not wired in `hooks.json` (unverified beyond grep). Full
redaction coverage of `observe.sh` and whether the observer is on by default: **unverified**.

## 4. Proposed Auditor security review procedure

Early (not Auditor-only):
- **Analyst (Gate 1):** abuse cases per actor×capability with each NFR; mark trust boundaries, model calls (N1),
  personal data (PRIV-1).
- **Architect:** SEC-14 threat table (STRIDE walk + N4 race + N1 injection + N2 SSRF), model-call table, error
  catalogue, baseline profile rows (SEC-10).

Auditor, **Gate 2R** (architecture review, add to `architecture-review.md` rows):
1. Every new trust boundary / entry point / principal / secret / personal flow has a threat row (SEC-14); every row →
   mitigation → named TC or user-accepted RISK-n with expiry.
2. Walk list complete per new operation, incl. concurrency/race (N4), SSRF/fetch (N2), file paths (N3), model
   output and injected content (N1), compromised dependency.
3. Matrix rows exist for every operation incl. exports/aggregates (ACCESS-1, -5); deny by default stated (SEC-4).
4. Server-owned values listed (SEC-5); sinks list their encoding/parameterisation (SEC-7); secrets list their store,
   required-at-start, print-by-name (SEC-8/9).
5. CI declares SCA, SAST, secret scan, image scan, baseline DAST and agent-config scan (SEC-13, N5) with fail levels.

Auditor, **final (Gate 3, L5)** — thin checklist, evidence over opinion:
6. Read CI evidence: secret scan over tree+history, SCA/SAST/image 0 open Critical/High (or RISK), DAST baseline 0 high,
   agent-config scan clean (N5).
7. Every threat row's TC exists and passed (traceability); every abuse case has a TC.
8. Access completeness test enumerates the running system's operations; cells assert status AND visible fields;
   suspended principal's live token refused (ACCESS-3/6/11).
9. Diff-scoped manual pass over high-risk sinks (auth, money, uploads, fetches, files, model calls, webhooks): for
   each finding record entry point → sink reachability and required principal; severity by reachability (N7).
10. Canary checks: secret and personal-data canaries absent from logs, errors, CI output (SEC-9, PRIV-6).
11. Report in `audit.md` with rule ids; never fix (Auditor contract).
