# Commanded batch findings — 2026-10-15

Investigated all five selected tasks. Read their exact base-commit CI and
dependency files and existing runtime logs. Ran an additional two-phase
experiment for #380. No paid model calls or task eligibility changes.

## Historical environments

| Task | CI Elixir | CI Erlang/OTP | Original gold failures (parsed IDs) |
| --- | --- | --- | ---: |
| #139 | 1.5.3 | 20.2 | 92 |
| #171 | 1.5.3 | 20.2 | 22 |
| #290 | 1.8.0 | 21.2 | 28 |
| #335 | 1.9.4 | 22.0 | 9 |
| #380 | 1.10.2 | 22.0 | 5 |

Source files are saved in the task directories; `sources.json` records exact
commit URLs and hashes. Missing distributed-test files at the first four commits
returned 404, not a download failure for their CI/dependency files.

## #139, #171, #290, #335

All four have actual crashes in Phoenix.PubSub.PG2Server.init/1 calling missing
`:pg2.create/1`. Their historical CI runtimes predate its removal in OTP 24;
our recorded runtime is newer. This is a confirmed incompatibility, not merely
a compiler warning. Official removal documentation:
https://www.erlang.org/docs/24/general_info/removed.html

All five original runs also have a JSON string-order assertion failure: the
serialized object contains the same fields and values in a different order.
#335 additionally has application-startup and aggregate-lifespan failures.
Other failures may be cascades; the shared pg2 cause does not explain every
failure conclusively. `failure-evidence.json` stores illustrative failure blocks
and category counts; raw failure blocks need not equal unique parser test IDs.

A repair should first reproduce each task's historical runtime pair and rebuild
its pinned dependencies. Replacing pg2 calls with pg changes messaging semantics
and is not an appropriate unexamined benchmark repair. Historical runtimes have
not been rebuilt in this batch, so no recovery count is claimed for these four.

## #380: tested missing historical startup step

The pinned `.travis.yml` explicitly runs `epmd -daemon` before tests.
Its distributed test calls `LocalCluster.start()` then starts three nodes.
The original run's `:nodistribution` / connection-refused failure was consistent
with that omitted service startup.

Reran both phases in the same immutable task image, with the original reference
and test patches, original test command, and prior `ERL_FLAGS="+JMsingle true"`.
The only added setup was `epmd -daemon` followed by `epmd -names`.

| Phase | Passing parsed IDs | Failing parsed IDs |
| --- | ---: | ---: |
| Original base | 343 | 6 |
| Base with epmd | 344 | 5 |
| Original gold | 344 | 5 |
| Gold with epmd | 345 | 4 |

`distributed subscriptions should be registered on all nodes` now passes in
both phases. The target `process manager event applying error should call
\`error/3\` callback on exception` fails only on base. Both phases still exit 2.

Four remaining gold failures:

1. `should serialize value to JSON`: same object, different key order.
2. `register subscription should be registered`: same two subscriptions, different list order. Whether ordering is contractual needs source review before changing the assertion.
3. `a Commanded application should fail to start unconfigured application`: expected EXIT message absent.
4. `aggregate lifespan should adhere to aggregate lifespan after taking snapshot`: expected normal shutdown, got invalid callback return instead.

These remain visible; no tests were skipped or rewritten. `epmd-result.json`
records the image, setup override, complete parsed results and log hashes.

Reproduce with a new output path:

```sh
.venv/bin/python prepare_validation.py --diagnostic-ids commanded__commanded-380
.harness-venv/bin/python validate_reference.py --input validation_inputs/diagnostic.json --manifest diagnostic_manifest.json --output validation_runs/commanded-380-epmd-rerun --timeout 300 --erl-flags '+JMsingle true' --start-epmd --pull-missing --release-pulled-images
```

## Disposition

All five remain unresolved under strict validation. One concrete environment
repair is demonstrated for #380; four have verified historical-runtime mismatch.
No original reports, expectation lists, or sample entries were changed. The next
substantial step is historical-runtime reproduction, starting with one task to
verify dependency availability before expanding to the remaining tasks.
