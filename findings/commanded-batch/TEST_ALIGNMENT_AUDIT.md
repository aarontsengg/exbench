# Commanded #139 and #171: what the failing tests measure

Audit date: 2026-10-16. Sources: pinned task export, original reference/test
patches, historical source contexts, and diagnostic logs. This audit concerns
repaired historical evaluations, not the original upstream grading results.

## #139 — change lifespan decisions from commands to events

The issue requests `after_event/1` instead of `after_command/1`. The supplied
interface additionally documents timeout, infinity, hibernate, stop, and router
validation. Four runtime tests use a lifespan helper implementing only the new
callback. Base still calls the old callback and raises UndefinedFunctionError;
this is an expected API-transition failure, not missing application startup.
Gold invokes the new callback and reaches the actual lifecycle assertions.

| Test (AggregateLifespanTest) | Assertion / interpretation |
| --- | --- |
| aggregate started should shutdown after timeout | Monitors aggregate shutdown after the opening event's timeout. Relevant. |
| aggregate started should not shutdown if another command executed | Opening then deposit events must update the timeout; no immediate shutdown, then normal shutdown. Relevant, but short timing windows warrant repeated runs. |
| aggregate started should use default lifespan when it's not specified' | An operation routed without an explicit lifespan must leave the aggregate alive over the observation window. Relevant regression protection. |
| aggregate started should stop process when requested | Closing event returns `:stop`; monitor must receive normal shutdown. Explicitly documented in the supplemental interface. |
| deprecated after_command/1 callback should fail to compile when missing after_event/1 function | Intended to reject old callback-only configuration. Original fixture also supplies BankAccount as a handler even though it lacks execute/2. Base therefore raises an unrelated handler error. Corrected as described below. |

Two other base failures are in RoutingCommandsTest: duplicate registration and
missing handle/2. Both already reject invalid configurations in base, but with
RuntimeError and different text. Gold changes them to ArgumentError and exact
new messages. These are ancillary router-contract changes, not evidence of
OTP lifecycle reasoning. The supplemental interface mentions the error type
and conditions, but does not give the literal messages asserted by the tests.
Keep them visible in full-suite results; do not describe all seven transitions
as seven direct tests of the lifespan issue. No assertion was weakened or
removed to hide them. Exact-message fairness remains an inclusion concern.

### Correction to the deprecated-callback fixture

Use `Commanded.ExampleDomain.OpenAccountHandler` with `aggregate: BankAccount`
in the dynamically compiled test router. This is the valid handler/aggregate
combination already used by the test bank router. Leave the intentionally old
`after_command/1` lifespan and expected `after_event/1` validation error intact.

This makes the test isolate its stated condition: handler configuration is
valid, while lifespan configuration is intentionally obsolete. The same patch
is applied in base and gold, after the upstream test patch. No production code
changes. Startup fixes from the previous diagnostic are also retained.

## #171 — process-manager command dispatch times out

The sole remaining base failure is DispatchConsistencyTest's
`process manager consistency should successfully dispatch command`.

The test starts a strongly consistent process manager, dispatches a command,
and requires `:ok`. The helper reacts to the resulting event by dispatching
another command, then handles the subsequent event. Base returns
`{:error, :consistency_timeout}`. The reference patch changes acknowledgement
tracking from one shared list to a map keyed by event number. This is directly
aligned with the reported process-manager dispatch timeout, though the test
uses a smaller reproduction than the issue's four-stage application example.

Retain the assertion unchanged. Retain explicit subscription startup and
synchronous Phoenix PubSub supervisor cleanup. The other 17 upstream expected
failures that pass before the fix are regression checks in this environment,
not demonstrated bug-detection tests.

## Evaluation boundary

Do not silently replace upstream expectations with whatever a run prints.
Any future variant must declare its runtime, fixture corrections, parser,
reviewed failure partition, full regression inventory, and prompt policy.
These runs still use name-only parsed IDs, which collapse duplicate names
across modules. Raw suite counts and process exit codes remain essential.
Original sample membership and strict validation counts remain unchanged.

## Reproduce the audited correction

Run `run_fixture_diagnostic.py --audited --seed 42`, then repeat with `--seed 7`.
Each command runs both tasks, base and gold, in four fresh containers. It keeps
all upstream assertions and applies the corrected fixture identically to both
phases. The script refuses to overwrite existing output. Reports and patches
include the seed in their filenames. Use
`summarize_fixture_diagnostic.py --audit` to verify saved log hashes and compare
expectations after both commands finish.

## Observed outcomes after correction

Both seeds (42 and 7) completed with identical parsed passing/failing sets:

| Task | Base | Gold | Assessment |
| --- | --- | --- | --- |
| #139 | 179 tests, 7 failures | 179 tests, 0 failures | Five lifespan/interface checks plus two ancillary router-error checks transition. |
| #171 | 202 tests, 1 failure | 202 tests, 0 failures | Direct process-manager consistency check transitions. |

For #139's corrected deprecated-callback test, base now reports “Expected
exception ArgumentError but nothing was raised,” replacing the unrelated
missing execute/2 error. Gold raises the intended missing-after_event/1 error
and passes. This verifies that the correction isolates the intended condition.

All observed base failures become gold passes; no parsed passing IDs disappear.
Both seeds have the same fixture patch hashes and use the same immutable images.
No new timing thresholds, skipped tests, or weaker assertions were introduced.
Two seeds provide limited repeatability evidence, not a flakiness-rate estimate.
The two router-error requirements and exact-message assertions still require a
fairness decision before #139 can enter a final benchmark. Neither task has
been promoted automatically or substituted into the original validation totals.
