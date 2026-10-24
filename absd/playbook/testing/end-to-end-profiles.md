# End-to-end harnesses per profile

Code **E2E** (E2E-11 to E2E-15). How each interface profile's end-to-end form (STRAT-5) drives the shipped artifact:
native app on devices, HTTP black box, cli subprocess, installed library, pipeline run. The rules for every profile —
error tripwire (E2E-1), the user's entry point (E2E-2), real stack (E2E-3), binding before the interface (E2E-4),
devices, time, principals, seeding, smoke and regression — are in `absd/playbook/testing/end-to-end.md` and apply here
too. Related: VIS-3 (golden output), COMPAT (previous versions), FAKE-6 (recordings).

## Checklist

- [ ] native-app: release build per platform × device class; interruptions covered (E2E-11)
- [ ] http-api: built artifact driven from another process; contract-checked bodies; `design.md` examples replayed; log watched (E2E-12)
- [ ] cli: subprocess; TTY and pipe, `NO_COLOR`, width; exact stdout, stderr, exit code (E2E-13)
- [ ] library: built package in a clean environment per runtime; public surface only; API diffed (E2E-14, COMPAT-1)
- [ ] data-pipeline: recorded real-volume run + replay, duplicate, late, malformed, empty; counts reconcile; golden rows from the analysis example table (E2E-15)

## Rules

**E2E-11** — native-app: install the release-configuration build, signed as shipped, on emulators and devices per
platform × device class × supported OS (e.g. XCUITest, Espresso, Appium, Maestro), locating elements by the
accessibility identifiers and labels `design.md` names; cover background and resume, process death and restore,
rotation, permissions granted and denied, offline and flaky network, deep links, notification taps, on-screen
keyboard, safe areas, both themes, large text.
- *Why:* phone-only defects reached users while one device class ran (LL-4); debug builds hide shipped behaviour.
- *Check:* CI device matrix = `context.md`; release configuration under test; interruption cases per journey.
- *Applies when:* native-app.
- *Provenance:* LL-4 (KatenatsioTipster, 2026-10)

**E2E-12** — http-api: start the built image or binary with shipped configuration and drive it from another process
over the network as a consumer: documented versioned routes only; the real sign-in flow, never minted tokens; each
status, header and body checked against the HTTP contract, each error body against the error catalogue; pagination
walked to the end at Data Volume Profile max in stable order; each example request and response `design.md` names
replayed literally (E2E-4); journeys across principals; service log watched (E2E-1).
- *Why:* free accounts got paid data in an API response no screen showed (LL-10); refusals were logged as errors
  (LL-15); the designed examples were bound by no test (LL-56).
- *Check:* the job targets the started artifact, not a test host; contract checks on every call; a TC per `design.md`
  example; log capture on.
- *Applies when:* http-api, and the service behind a web-ui or native-app.
- *Provenance:* LL-10, LL-15 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)

**E2E-13** — cli: run the built or installed executable as a subprocess with explicit args, stdin, environment and a
clean home and config directory per test; assert stdout, stderr, exit code (DSN-17 table; stderr empty unless
expected; never a stack trace) and files written. Run each command under a pseudo-terminal and through a pipe
(colour, prompts, progress only on a TTY; destructive commands need `--yes` without one), with `NO_COLOR` set and
unset, at narrow and wide widths; `--json` matches its schema; an interrupt exits with the documented code and cleans
up; one run per supported OS and shell (VAR-6); golden human output per VIS-3.
- *Why:* in-process calls skip argument parsing, terminal detection and exit-code mapping — the cli's real interface.
- *Check:* pty and pipe modes in the harness; three streams asserted per case; OS/shell matrix = `context.md`.
- *Applies when:* cli.
- *Provenance:* industry baseline

**E2E-14** — library: build the distributable exactly as the release does, install it into a fresh isolated
environment per supported runtime (lowest and highest allowed dependency versions too) and run consumer tests using
only the public surface: documented examples run as tests (DSN-18), errors arrive as documented types, no unexpected
warning. Check package contents (licence, types; no tests, secrets, build leftovers) and diff the public API with
the previous release (COMPAT-1): a break without a MAJOR version is a finding.
- *Why:* source-tree suites pass while the package lacks files, leaks private names or breaks on a runtime.
- *Check:* no source path importable in the test environment; runtime matrix = `context.md`; API diff reported.
- *Applies when:* library.
- *Provenance:* industry baseline

**E2E-15** — data-pipeline: run the real entry point over a recorded real-volume dataset (dated, scrubbed, Data Volume
Profile max; FAKE-6) against real stores and brokers, then: the input replayed (identical output, no duplicates),
duplicated and out-of-order records, records past the contract's lateness window, malformed records (quarantined with
a reason), an empty input. Reconcile counts and sums (input = output + rejected); compare output record by record,
zones and units included, with the golden dataset whose expected rows are the Analyst's example table for that recorded
input in `analysis.md` (a `SPEC:` source; ORACLE-4, VIS-3) or with the source of truth.
- *Why:* a provider-zone time read as UTC and a half-time field read as the final result were data-contract defects
  only real recorded input exposes (LL-1, LL-2); three approvers were named for the golden dataset (LL-56).
- *Check:* dataset capture metadata; a reconciliation assertion per run; all six input cases present; the golden file
  cites its analysis example table.
- *Applies when:* data-pipeline, and batch imports or event consumers in any profile.
- *Provenance:* LL-1, LL-2 (KatenatsioTipster, 2026-10); LL-56 (ABSD v2 kit review, 2026-10)
