# Commanded #380 historical-runtime experiment

## Result

With Elixir 1.10.2 / OTP 22.3.2 and the original locked dependencies, the original
evaluation suite reports 360 tests: **base has exactly one failure; gold has
zero failures**. The failure is the intended process-manager apply-error
callback test. No test assertions or production compatibility code were edited.
Epmd was started in both containers, as required by the historical CI.

The prior lifecycle, JSON-order, subscription-order, and startup-message
failures did not occur in this single base/gold pair. This does not prove the
lifecycle code is safe under every schedule, or establish a flakiness rate.
The original CI listed OTP 22.0; the image provides 22.3.2. This is a historical
major-version reproduction, not an exact CI environment reconstruction.

## Environment and provenance

- Base image: `elixir@sha256:846a4741100318653895ed1ac8d9fdd102ca7cfce1f6b85d6e1448512a8c613f`.
- Source archive: exact commit `4a6df4a3fc3e318805574ca9cab5cef0a83617e3` from GitHub codeload.
- Original `mix.lock` preserved byte-for-byte through dependency resolution.
- Hex 2.0.6, archive built for Elixir 1.10.0, downloaded from `https://repo.hex.pm/installs/1.10.0/hex-2.0.6.ez`.
- Rebar installed through historical Mix's `mix local.rebar --force`; not independently version-pinned. The resulting image ID pins the tested built artifact; a future rebuild must also pin this tool for stronger reproducibility.
- Tests run in fresh amd64 containers under emulation, with networking disabled
  except container-local loopback. No JIT override was used on OTP 22.
- Original reference patch only in gold; original test patch in both. Test
  command comes from the dataset. No startup-probe or assertion-compatibility
  patches applied.

Runtime, dependencies and image setup differ from the original upstream image.
This experiment identifies a working combination; it does not isolate which
individual change accounts for every recovered test.

The first build used a Hex archive compiled for Elixir 1.8 and failed with a
Logger API mismatch. Retrying the same Hex version's Elixir 1.10 archive resolved
it. That setup failure occurred before testing and is retained in
`validation_runs/commanded-380-historical/build-attempt-1.log`.

## Parser limitation and expectation mismatch

Old ExUnit trace lines lack `[L#...]`. The unchanged upstream parser therefore
recognized the failure but **zero passing IDs**, despite successful completed
tests. `parse_380_historical.py` provides an explicit separate adapter for timed
completion lines, preserving failures and ignoring unfinished starts/doctests.
Small checks cover interrupted tests, carriage-return progress, and failure
precedence. The upstream parser's original output remains in the result.

Adapted unique test-ID counts: base 348 pass / 1 fail; gold 349 pass / 0 fail.
These differ from raw 360-test totals because names are not globally unique.
No upstream expected test IDs are missing. Five extra IDs pass in both phases:

- Unconfigured application startup rejection.
- Aggregate lifespan after snapshot.
- Distributed subscriptions on all nodes.
- Registered subscription membership.
- JSON serialization.

Those IDs were absent from the upstream expected lists. Consequently this is
not unchanged-upstream strict validation. An explicitly versioned historical
variant needs its parser and expected sets recorded before use in evaluation.
No such variant has been added to the final sample automatically.

## Evidence

`380-historical-result.json` records image identity, source/build/lock/archive/log
hashes, both parsers' results and the diagnostic transition check.
`380-historical.Dockerfile` records the build recipe; `run_380_historical.py`
records bounded execution and cleanup. Raw logs and build context live under
ignored `validation_runs/commanded-380-historical/`. The built historical image
is retained for follow-up repeatability checks. No paid model calls.
