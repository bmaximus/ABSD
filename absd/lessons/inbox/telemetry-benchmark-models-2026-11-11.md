# Proposal: model levels per role, pipeline telemetry, agent benchmark

Source: the kit owner, after the ECC evaluation (LL-65) and the 2.3.0 release, 2026-11-10/11. Owner's words:
"I like the benchmarks thing for the agents. Also I like that you mentioned something about telemetry from ecc which
we miss, we need that also." and "I was also thinking if we could add model selection for each agent. Like for
architect opus or fable, and for others the equivalent ones."

## Gaps

- **Models.** 2.2.0 set a model in each manual's frontmatter and let only the Builder use a faster tier. A product
  cannot choose per role without editing kit files (read-only there). Model names change faster than the kit.
- **Telemetry.** No record of what a cycle cost, where it failed or which rules caught anything. The Harvest step
  tightens or drops rules on impressions, and the "too heavy" complaint cannot be answered with numbers.
  ECC's metrics hooks are not a model to copy: they send session content to a model and run repository-configured
  commands.
- **Benchmark.** The acceptance run (ENR-14) is a manual pass/fail exercise. It does not measure whether a kit
  change makes the agents catch more or less, and it has no seeded problems to catch.

## Proposed

1. Levels, not models, in the kit (strongest, balanced, fast). A default level per role and step, floors no product
   can lower, a level-to-model map in each product's `context.md`, and the Manager passing the model per invocation.
2. A per-cycle telemetry file written only through a validating tool: numbers, ids and enums only, local only,
   one off switch. A report at Harvest: cost, gate rounds, rules that fire and rules that never do, rework, halts.
3. A benchmark in the kit repo: the acceptance fixtures with seeded traps (ambiguity, contradiction, input
   variation, time, security) and a scorer. A release must not score worse than the last accepted one. Model-map
   experiments use the same comparison.
