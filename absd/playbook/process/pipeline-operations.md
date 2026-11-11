# Pipeline operations — model levels, telemetry, benchmark

Code **PIPE**. How the pipeline itself is run and measured: which model level each role and step runs on and how the
Manager passes it per invocation; the per-cycle telemetry record, its privacy limits and the Harvest report built
from it; and, on the kit side, the agent benchmark every MINOR or MAJOR release must not regress. The Manager applies
PIPE-1 to PIPE-5 in products; the kit maintainer applies PIPE-6 (`absd/playbook/process/enrichment.md`, ENR-14).

## Checklist

- [ ] The kit names levels (`strongest`, `balanced`, `fast`), never models; §14 maps level → model (PIPE-1)
- [ ] Each role and step runs on its default level or a §14 override; no override lowers a floor (PIPE-1)
- [ ] A second audit (XCA-17) runs on a different strongest-level model than the build when the map names two (PIPE-1)
- [ ] Every delegation resolves role/step → level → model and passes the model explicitly; the brief names both (PIPE-2)
- [ ] Assisted mode: the handoff names the level and the model the user picks (PIPE-2)
- [ ] Every invocation, gate verdict, halt, rework loop, negative control, escape and resume recorded with `metrics.py record` (PIPE-3)
- [ ] Tokens recorded only when the platform reports them — never estimated (PIPE-3)
- [ ] Telemetry holds only numbers, timestamps, enums and ids; local, never sent; `Telemetry: off` honoured (PIPE-4)
- [ ] Mode H runs `metrics.py report` over all cycles; lessons cite its numbers (PIPE-5)
- [ ] Kit side: benchmark run, scored, committed and compared before every MINOR or MAJOR tag (PIPE-6)

## Rules

### Model levels

**PIPE-1** — Run every role and step on a named model level — `strongest`, `balanced` or `fast` — taken from the
default table below unless `absd-project/context.md` §14 "Role/step overrides" raises it or lowers a non-floor one;
the §14 "Model levels" table maps each level to a model. No product setting lowers a floor: architecture, the Gate 2R
review, Plan & Bind oracles and RED tests, every audit and security review, and every work package with money,
permission or security content run on `strongest`. When the second audit (XCA-17) runs and the map names two
strongest-level models, it runs on the one that did not build the code.
- *Why:* one tier for every step either wastes the strongest model on bookkeeping or puts a cheaper one on the
  judgement that gates catch least; naming models in the kit dates it with every model release (LL-67).
- *Check:* every invocation event in the cycle's telemetry (PIPE-3) names a level at or above its row's floor and the
  model §14 maps it to; the second audit's model differs from the Builder's when §14 names two strongest models.
- *Applies when:* always.
- *Provenance:* LL-65 (ECC evaluation, 2026-11); LL-67 (owner request after the 2.3.0 release and the ECC evaluation, 2026-11)

| Role · step | Default level | Floor (no product setting lowers it) |
|---|---|---|
| Manager, Analyst, Designer, Architect — every step | strongest | Architect: strongest |
| Auditor — Architecture Review, Audit, Re-audit, second audit, every security review | strongest | strongest |
| Tester — Facts, Plan & Bind, Reproduce | strongest | Plan & Bind (oracles, RED tests): strongest |
| Tester — Baseline, Verify, Log, Harvest bookkeeping | balanced | none |
| Builder — a WP with no money, permission, security, time or data-migration content | balanced | none |
| Builder — any other WP | strongest | money, permission, security WP: strongest |

`fast` is never a default; a product may assign it only to a step without a floor. Illustration of a §14 "Model
levels" map (two vendor families): strongest → a vendor's top model (e.g. `opus`, or another vendor's flagship);
balanced → its mid model (e.g. `sonnet`, or that vendor's mid model); fast → its small model.

**PIPE-2** — At every delegation the Manager resolves role and step → level (PIPE-1) → model (§14 map), passes that
model explicitly with the invocation (`absd/RULES.md` §8 "Model level" row), fills the brief's `Model` field
(`<level> → <model>`) and records both in the invocation's telemetry event (PIPE-3). Frontmatter `model:` is only the fallback when
the platform cannot set a model per invocation. In assisted mode the handoff names the level and the model the user
selects before confirming.
- *Why:* a frontmatter default silently runs every step of a role on one model, so a floor or an override set in §14
  never takes effect and telemetry reports a model that did not run.
- *Check:* each brief's `Model` field matches PIPE-1 and §14; the invocation event names the same level and model.
- *Applies when:* every delegation.
- *Provenance:* LL-67 (owner request after the 2.3.0 release and the ECC evaluation, 2026-11)

### Telemetry

**PIPE-3** — Record each cycle in `absd-project/metrics/C###.json`, written only through `absd/tooling/metrics.py
record` and committed with the Manager's hand-off commits: one event per invocation, gate verdict, halt, rework loop,
negative control, escape and resume, with the fields below. Tokens are recorded only when the platform reports them,
never estimated — otherwise the field is omitted. The file stays in `absd-project/metrics/` at archive (one file per
cycle, never moved); `metrics.py validate` checks every file.
- *Why:* without numbers, Harvest guesses which steps cost most, which gates fail and which rules earn their place;
  estimates and hand edits make the numbers lie (LL-67).
- *Check:* `metrics.py validate 'absd-project/metrics/*.json'` passes; every logged invocation and gate round in
  `cycle.md` has its event; no event carries an estimated token count.
- *Applies when:* every cycle while telemetry is on (PIPE-4).
- *Provenance:* LL-67 (owner request after the 2.3.0 release and the ECC evaluation, 2026-11)

| Event (`--kind`) | Fields |
|---|---|
| `invocation` | agent, step, level, model, duration (s), tokens (only when reported), result (done, halt, interrupted, rejected) |
| `gate` | gate (G1, GUX, G2, G2R, GT, G3, XCA, REL), round, verdict (PASS, FAIL), finding counts by RULES §6 severity, rule ids the findings cite |
| `halt` | agent, cause (blueprint-gap, spec-gap, kit-gap, external, user) |
| `rework` | from, to, cause (review-fail, upstream-gap, spec-defect, halt, clr, change-request) |
| `control` | negative-control id, turned red, turned green |
| `escape` | DEF id, why-missed class (ESC taxonomy) |
| `resume` | agent |

**PIPE-4** — Keep telemetry private and inert: a local file in the product repository, never sent anywhere — no hook,
tool or workflow transmits it; it holds only numbers, timestamps, enums and ids (the tool refuses free text, unknown
keys and any value outside its pattern); never prompts, code, artifact text, names, paths or personal data. A line
`Telemetry: off` in `context.md` §14 makes `record` a no-op (exit 0 with a notice); the default is on.
- *Why:* a usage log that carries prompts or code is a data leak, and one that phones home is agent configuration
  acting as a supply-chain channel (SEC-16).
- *Check:* `metrics.py validate` passes on every file; the agent configuration holds no hook or server that reads
  `absd-project/metrics/`; with `Telemetry: off`, no metrics file changes during the cycle.
- *Applies when:* always.
- *Provenance:* LL-67 (owner request after the 2.3.0 release and the ECC evaluation, 2026-11)

**PIPE-5** — At every Mode H the Manager runs `metrics.py report` over all cycles' files and cites its numbers in the
lessons it records: most expensive steps, gates with the most FAIL rounds, rules whose findings catch most, kit rules
never cited after the report's cycle threshold (candidates to drop or merge — proposed upstream, never deleted
locally), rework hot spots, halts by cause and cost per level and model. A pattern another product would repeat goes
upstream with its numbers in the proposal (ENR-1, ENR-3).
- *Why:* lessons argued from impressions do not move the kit; numbers show which rules work and which only cost.
- *Check:* the Harvest's lessons rows cite report figures; a "never cited" or cost lesson names the cycles counted.
- *Applies when:* every Mode H while telemetry is on.
- *Provenance:* LL-67 (owner request after the 2.3.0 release and the ECC evaluation, 2026-11)

### Benchmark (kit side)

**PIPE-6** — Before tagging a MINOR or MAJOR kit version, run the agent benchmark (`benchmark/README.md` at the kit
repository root): every fixture product with its seeded traps, scored by `benchmark/score.py`; commit the combined
result as `benchmark/results/<version>.json` and compare it with the last accepted result (`score.py compare`). The
release fails on fewer traps caught, more kit-gap halts, any ENR-14 criterion failing, or a first-pass gate rate more
than 10 points lower; token or time growth above 25 % is a warning recorded in the CHANGELOG. A model-map experiment
is a benchmark run with another level → model map, compared the same way; a role or step moves to a cheaper level
only on a non-regressing result.
- *Why:* a kit change can make agents miss traps they used to catch, and a cheaper model can look fine on one cycle;
  only a repeatable scored run shows it (LL-67).
- *Check:* the release commit holds `benchmark/results/<version>.json`; `score.py compare` exits 0 against the last
  accepted result; the CHANGELOG lists the score and every cost warning.
- *Applies when:* the ABSD repository, every MINOR or MAJOR release and every proposed default-level change.
- *Provenance:* LL-67 (owner request after the 2.3.0 release and the ECC evaluation, 2026-11)
