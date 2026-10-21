# Cachex #341 timing investigation — 20 October 2026

The unchanged reference suite passed all 200 module-qualified tests at seeds 42
and 7 using the original immutable benchmark image and existing JIT override.
No assertion, timeout, dependency, production patch, or runtime version was
changed. The earlier reference failure is preserved as an intermittent failure.

## What failed originally

`Cachex.Services.InformantTest / notifying a list of Hooks` measures a synchronous
hook that sleeps for 25 ms. `:timer.tc` reports microseconds; the assertion expects
25,000 ± 10,000. The original measured value was 35,746 microseconds: 746
microseconds above the allowed upper bound. The preceding expected-message
assertion succeeded. This is a wall-clock duration failure, not evidence that
the hook failed to deliver its message.

The target issue is warmer naming, a separate behavior. Baseline compilation
fails because the evaluation tests construct a warmer with a `name` field that
the original API lacks. The supplemental interface explicitly specifies that
field, supporting an expected-missing-API interpretation. This does not establish
individual baseline test outcomes.

## Results

| Seed | Original code | Reference fix |
| --- | --- | --- |
| 42 | Compile error: missing warmer `name` field | 200 tests, zero failures, exit 0 |
| 7 | Compile error: missing warmer `name` field | 200 tests, zero failures, exit 0 |

Image ID: `sha256:71b3ef14457ae2711eed2df7cb6c47e7a48fb6a7e26560902e1a6369f876d84f`.
Runs use linux/amd64 emulation, `ERL_FLAGS=+JMsingle true`, host networking as in
the original runner, and unchanged upstream patches. Only explicit test ordering
was added. No epmd startup adjustment was added for this task.

The qualified parser recovers 200 tests; the earlier upstream name-only summary
contained 193 identities. Passing inventories agree across both new gold runs.

## Decision and limitations

Keep this as a separately documented expected-API candidate with a timing
reliability caveat. Do not erase the original failure, claim the test can never
flake, or automatically include the task in scored evaluation. Scheduling and
emulation are plausible contributors; these reruns do not isolate a root cause.
No repair was needed to obtain the passing repeats, and no repair was invented.

Before scoring, choose a consistent policy for intermittent timing failures and
check behavior on the intended evaluation hardware. Do not rerun failed agent
submissions until they pass while reporting them as pass@1.

`repeat-results.json` stores full qualified results, image identity, patches'
hashes, source issue/interface and log hashes. `review.json` links the original
failure and pinned test source. `check.py` reproduces the four checks using a new
output directory (its default refuses overwrites). Raw logs remain ignored under
`validation_runs/cachex-341-repeat/`. The downloaded image is retained for follow-up.

No model calls, sample changes, policy changes, commits, or pushes.
