# ABSD agent benchmark

The kit's regression test for agent behaviour (ABSD playbook PIPE-6, ENR-14). Each fixture is a tiny product brief
with seeded traps: things a careful team must notice (an ambiguity, an input variation, a contradiction, a security
or time trap). A run builds the fixture with the kit and is scored on the evidence it leaves: did the artifacts raise
the traps, how many gate rounds failed, did an agent halt on a question the kit should have answered, what did it cost.
Before tagging a MINOR or MAJOR kit version the benchmark runs and its result is compared with the last accepted one.

This directory is kit-repository tooling: it is not under `absd/`, not in `absd/MANIFEST` and never vendored into a
product.

## Layout

| Path | What it is |
|---|---|
| `fixtures/<name>/brief.md` | The owner brief plus the "Feature for the first feature cycle" — the only input the runner gets |
| `fixtures/<name>/traps.json` | The seeded traps and their detectors — never shown to the runner |
| `score.py` | `score` one run, `combine` a version's runs, `compare` with the baseline (standard library) |
| `test_score.py` | The scorer's tests, including both directions of every shipped detector |
| `results/<version>.json` | One committed result per accepted kit version (from `combine`) |

| Fixture | Interface profile | Feature | Traps |
|---|---|---|---|
| `tally` | CLI + library | Totals by category and month, table or `--json` | variation, ambiguity, contradiction |
| `shelf` | Web UI + HTTP API, phones | Mark a book read with its date; admins see every shelf | security, time, ambiguity |
| `ledger` | Batch data pipeline | Daily summary per local calendar day | time, ambiguity, ambiguity |

## Running it

One run per fixture, each in a fresh, empty repository outside this one:

1. Create the repository (`git init`, default branch `main`) and install the kit at the version under test, as a
   product would (`absd/tooling/absd_sync.py`, see `absd/RULES.md`).
2. Give the runner (the Manager session) the fixture's `brief.md` as the owner's words — the whole file, nothing else.
   Never give it `traps.json`, this README or the scorer. Telemetry stays on (`Telemetry: on` in `context.md` §14,
   the default).
3. Run Bootstrap, then the first feature cycle to its Gate 3 and archive. Answer questions with the brief's standing
   answers only; record each answer you had to give that the brief does not cover — that is a kit-gap signal.
4. Note the ENR-14 results: `c1` every Foundation negative control turned RED then GREEN; `c2` trace_check and
   ownership_check passed at every gate; `c3` no agent halted on a question the kit should have answered.
5. Score the final repository:

```bash
python3 benchmark/score.py score --fixture benchmark/fixtures/tally --repo /path/to/tally-run \
  --kit-version 2.4.0 --criteria c1=pass,c2=pass,c3=pass --out /tmp/tally.json
```

A trap is caught when its detectors' regexes match in the run's artifacts (`absd-project/**/analysis.md`,
`test_plan*.md` and `test_plan/*.md`, `design.md`, `architecture.md`, their split parts, `catalogue.md`,
`clarification_needed.md` — each trap names its own). A repository with no `absd-project/metrics/*.json`, or with an
invalid one, scores RED (exit 1): telemetry is part of the benchmark.

## Comparing

```bash
python3 benchmark/score.py combine /tmp/tally.json /tmp/shelf.json /tmp/ledger.json --out benchmark/results/2.4.0.json
python3 benchmark/score.py compare --baseline benchmark/results/2.3.0.json --candidate benchmark/results/2.4.0.json
```

`compare` fails (exit 1) on a regression: a baseline fixture without a result, a trap the baseline caught now missed
(or fewer traps caught in total), more kit-gap halts, any ENR-14 criterion not `pass`, or a first-pass gate rate more
than 10 points lower. Token or time growth above 25 % is a warning: record it in the CHANGELOG entry. With no
baseline yet, the candidate becomes the first one. Commit the accepted result with the release.

## Model-map experiment

To test whether a role or step can run on a cheaper level or another model, run the same fixtures with the changed
level → model map (`context.md` §14 "Model levels" and "Role/step overrides") and compare its combined result with
the current baseline the same way. A role moves to a cheaper level only on a non-regressing result; the cost lines
show what it saved.

## Adding a fixture or a trap

- A trap is phrased in the brief the way an owner would say it, never flagged as a trap.
- Its detector matches the concept in several phrasings and does not match a run that never discussed it. Add both
  directions to `SAMPLES` in `test_score.py`; the tests also check that the brief copied verbatim into every artifact
  catches nothing (restating the owner is not dealing with the trap).
- Trap ids are `TRAP-<FIXTURE>-n`, never renumbered: `compare` matches traps by id across versions.

## Honest limits

- Detectors read artifact evidence: a trap counts as caught when an artifact raises it, not when the code handles it.
  The Auditor's and the tests' verdicts are what prove the handling; the score only shows the issue was noticed.
- A regex can miss an unusual phrasing (a false miss) or match an unrelated line (a false catch); read the matched
  lines in the result before accepting a changed score.
- One agent playing all roles does not test independence (XCA-17, the second audit): run the roles as separate
  sessions or agents when that is what is being measured.
- Three fixtures and nine traps are a smoke test, not a statistic; a run is not deterministic, so a single missed trap
  is a reason to look, then rerun, before rejecting a release.
