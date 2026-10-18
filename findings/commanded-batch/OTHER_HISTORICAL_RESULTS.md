# Four Commanded historical-runtime checks — 2026-10-15

All four builds and both phases completed. No production or test compatibility
patches applied: original reference patch in gold, original test patch in both,
original test command, and epmd started in fresh containers.

| Task | Elixir / actual OTP | CI OTP | Raw base failures | Raw gold failures | Interpretation |
| --- | --- | --- | ---: | ---: | --- |
| #139 | 1.5.3 / 20.3.8.26 | 20.2 | 22 / 179 tests | 15 / 179 tests | Shared application processes absent |
| #171 | 1.5.3 / 20.3.8.26 | 20.2 | 17 / 202 tests | 16 / 202 tests | Shared application processes absent |
| #290 | 1.8.0 / 21.2.4 | 21.2 | 5 / 212 tests | 0 / 212 tests | Expected failing IDs reproduce and pass with gold |
| #335 | 1.9.4 / 22.3.4.26 | 22.0 | 18 / 340 tests | 0 / 340 tests | Gold clean; one upstream expected failure already passes on base |

## Findings

The missing-pg2 failure is absent in these historical runs. This is a working
runtime/dependency change for that incompatibility, not proof that every task
now has a reliable evaluation.

**#139 and #171:** residual gold failures involve calls to absent
`Commanded.Subscriptions` or missing local pubsub registries. Inspection shows
`Commanded.StorageCase` starts the app in setup but stops it in on_exit.
`Commanded.SubscriptionsTest` uses plain ExUnit.Case and calls reset without
ensuring the app is started. This provides a concrete potential cross-test
lifecycle interaction. A targeted fixture-isolation experiment or repeat with
fixed seeds is needed to establish causality; no fixture was changed here.

**#290:** base's five failed normalized IDs exactly equal upstream FAIL_TO_PASS;
all become passing in gold. The observed pass-set transition is complete.
Gold additionally passes 49 IDs absent from the upstream expected union, so it
does not satisfy unchanged-upstream exact-list grading. A separate variant
would need explicit expectations and the historical parser.

**#335:** all 340 raw tests pass in gold. Of the upstream expected failure IDs,
`process manager subscription should monitor subscription and terminate process
manager on shutdown` already passes on base. There are no unexpected base failed
IDs, but that missing transition prevents claiming the entire upstream failure
partition was reproduced. Gold also has 9 passing IDs absent from the upstream
expected union. Repeatability and that individual test need review.

## Build details and limitations

- Official Elixir image tags were pulled, resolved to immutable digests, and
  used by digest in saved Dockerfiles. Actual OTP patch releases differ from CI.
- Sources came from each exact pinned base commit; source and Hex archive hashes
  are saved in each `<number>-historical-result.json`.
- First builds stopped because Hex rewrote old lockfile syntax/metadata. The
  successful retry evaluated the before/after locks and rejected any changed
  package-key set, source kind, package name, version, or checksum. Then it
  restored the original lockfile byte-for-byte before compiling dependencies.
  `verify_historical_lock.exs` records that check. No dependency versions were
  upgraded. Resolved metadata remains at `/tmp/resolved.mix.lock` in each image.
- Rebar is installed by historical Mix's bootstrap and is not independently
  pinned; the built image IDs identify the tested artifacts. Stronger rebuild
  reproducibility still requires pinning bootstrap tools.
- Tests use amd64 emulation, container-local networking, no JIT override, and a
  five-minute phase limit. This differs from the upstream runtime environment.
- The explicit old-ExUnit parser from `parse_380_historical.py` is used; raw
  counts may exceed unique parsed IDs. All upstream expected IDs were found in
  the gold logs. These are one run per phase, not a stability estimate.

Raw first-attempt build logs: `validation_runs/commanded-other-historical/`.
Successful runs and contexts: `validation_runs/commanded-other-historical-v2/`.
Tracked per-task results include full parsed lists, runtime, image identity,
source/lock/package hashes, and build/log hashes. Built images are retained.

No tasks were added to the final sample, no original statuses or expected lists
were modified, and no paid model calls were made.
