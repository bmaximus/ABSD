# Proposal: owner review of the 2.4.0 benchmark, visual craft and a light route (2026-11-11)

Source: the kit owner, verbatim request:

> Go ahead with the visual-craft work and benchmark
>
> Why: 2.4.0 caught 9 of 9 traps, so the benchmark can't separate models. It recorded tokens for 0 of 162
> invocations, and one agent played every role. Tipster, Virtual, RideRocket and StoickGate still run 1.x with no
> Tester.
> Model map: strongest Fable 5.2, second auditor Opus 5.5, balanced Sonnet 5.5, fast Haiku 5.5.
> Benchmark with one sub-agent per role, token capture, and new traps from the 7/11 payments lesson.
> A light route for small owner requests (your README's open item).

Findings behind it:

- A benchmark every model passes cannot rank models or model maps: scores need depth (raised, planned, tested).
- Telemetry recorded no tokens: the Manager had no instruction to take the count the platform reports per delegation.
- One agent playing every role measured neither role independence nor per-role cost.
- The 2026-11-07 payments escape (LL-59 to LL-62) had no benchmark trap: provider event lifecycle, reachability from
  the member's navigation, idempotent fulfilment, honest status levels, webhook authenticity, provider configuration.
- Small owner requests (a word, a colour) still ran the Mode S route with analysis, design, blueprint and 2R passes.
- Visual craft (art direction, generic looks, type, colour, space, depth, motion, charts, visual lint, a scored visual
  review) had no rules; research of three public design rule sets (an Anthropic frontend-design skill, Impeccable,
  UI UX Pro Max — rules reworded, nothing copied or installed; Impeccable's hooks download binaries and send
  telemetry, so it was read, never run) is the source.
