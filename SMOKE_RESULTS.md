# Smoke validation — 12 October 2026

One of two tasks validated under the recorded local emulation configuration.
The remaining 58 selected tasks have not been executed. No agent/model calls.

| Task | Base | Reference fix | Decision |
| --- | --- | --- | --- |
| elixir-protobuf__protobuf-387 | 5 expected failures, 476 parsed passes; 30.65 s | 481 parsed passes, no failures; 29.65 s | Validated for this runtime configuration |
| phoenixframework__phoenix-2974 | EEx.Engine compilation error; 20.33 s | Same compilation error; 16.05 s | Not validated; investigate/reproduce on native amd64 before replacement |

Counts are upstream parser test IDs, not ExUnit's raw case count (which also
reports doctests, properties, skips and exclusions). Protobuf matches all five
FAIL_TO_PASS and 476 PASS_TO_PASS IDs exactly in both phases.

Phoenix's only expected FAIL_TO_PASS ID, `to_param for binaries`, already passes
on base. PASS_TO_PASS is empty. Along with the compilation failure, this makes
the supplied task unsuitable for scoring in the current environment. Do not
interpret it as an agent failure or silently repair its test expectations.

## Configuration and evidence

The first run used default Erlang flags: Phoenix timed out twice at 900 seconds;
Protobuf stopped with a dependency compiler error before tests ran.
The diagnostic rerun used `ERL_FLAGS=+JMsingle true`, identical base/gold flags,
fresh containers, immutable image IDs and a 180-second timeout per phase.
The published images and patches were unchanged. The official parser and test
name normalization were reused without modification.

Erlang documents single JIT mapping as a workaround for emulators unable to
handle dual mapping: https://www.erlang.org/doc/apps/erts/erl_cmd.html
The change resolving the compilation symptoms supports an emulation-related
cause; it does not establish parity with native x86 execution.

Tracked summary and image/log hashes: smoke_results.json.
Full local logs: validation_runs/smoke-first/ and validation_runs/smoke-single-map/.
Large logs are ignored by Git; preserve them separately when publishing evidence.

## Next

Validate more tasks with the same explicitly recorded runtime configuration and
recheck problematic tasks on native Linux amd64 before making exclusions.
Twelve selected tasks have empty PASS_TO_PASS lists, which warrants attention
during execution but is not itself an exclusion rule. Do not alter the 30-pair
sample based solely on this two-task diagnostic. Any replacement must preserve
matching and repository caps, and needs its own label/runtime review.

## Scoring quarantine after issue/patch alignment review

The gold patch does address the issue: priv/templates/phx.gen.json/fallback_controller.ex wraps the Ecto.Changeset clause in `if schema.generate?`. It also includes unrelated Phoenix.Config and socket-supervisor changes, explaining the patch-level OTP classification. The test patch changes context alias expectations, config cleanup assertions and origin logging; it does not directly check the reported no-Ecto scenario. The sole designated FAIL_TO_PASS test already passes on base.

The user agreed to exclude this task from scoring. Recorded it in sample_exclusions.json without rewriting its OTP tag or upstream quality annotation. Preserved the 30-pair draft and marked it blocked; archived its prior state. Recomputed feasibility: cap four = 26 pairs, cap five = 29 pairs. These are label/eligibility capacities, not counts of runtime-validated pairs. No cap change or replacement performed.

## Second diagnostic batch

Absinthe #1336 validates: base 1300 parsed passes and the expected duplicate-subscription failure; gold 1301 passes, no failures. Combined time ~31 seconds. Phoenix HTML #282 target content_tag fails on base and passes with gold, but five other tests fail in both: four date selectors expect 2020, outside the observed generated 2021–2031 range, and one EEx test rejects a nil quote line. Do not count this as an agent failure or silently ignore those tests. Summary: validation_batch_02_results.json. Total: 2 validated, 1 scoring quarantine, 1 environment/test-suite investigation, 56 untested; validation remains specific to the recorded emulation configuration.
