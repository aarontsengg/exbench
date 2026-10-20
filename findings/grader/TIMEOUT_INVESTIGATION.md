# #171 causation-test timeout investigation — 2026-10-18

The first empty-patch grader run failed an additional regression:
`Commanded.Commands.CorrelationCasuationTest` / `event handler dispatch command
should copy causation_id from handled event` (backticks around causation_id in
the exact recorded identity). It waited 1000 ms for MoneyDeposited.

## Source and log evidence

- The test starts OpenAccountBonusHandler, opens an account, waits for the
  welcome-bonus deposit, and verifies propagated event/command causation IDs.
- The assertion subscribes from :origin. The in-memory event store replays
  persisted events and sends new ones to persistent subscribers. Merely
  subscribing after the event was stored should not lose it.
- The failed run logs successful handler subscription, receipt of BankAccountOpened,
  and entry into the DepositMoney command. Thus the logs do not support a simple
  missing-handler-startup explanation. They do not establish where the remaining
  time was spent or why the deposit was not observed before the deadline.
- StorageCase resets storage and stops the application after tests. Scheduler
  delays and cross-test lifecycle effects remain hypotheses, not proven causes.

## Bounded reproduction

`check_timeout.py` ran the whole affected module (10 tests) in six fresh
containers: base/gold at seeds 42, 7 and 123. All 60 test executions passed.
The upstream assertions and 1000 ms event timeout were unchanged. Gold applied
only the reference lib/ change; both used the same v2 fixture and immutable image.

Evidence: `timeout-repeats.json`, including commands, qualified results and
raw-log hashes. Logs are in ignored `validation_runs/171-timeout-repeats`.
These passing runs do not disprove the earlier full-suite failure or establish
that the suite is reliable. No test was removed, no timeout enlarged, and no
production fix was guessed from a failure that could not be reproduced here.

## Full-suite repeat

The unchanged empty-patch grader was repeated at seed 42. It completed all 202 tests with 1 failure(s):

- `Commanded.Commands.DispatchConsistencyTest` / `process manager consistency should successfully dispatch command`

See `full-suite-repeat.json`. This result is preserved alongside the earlier
extra timeout; it does not replace or erase that failure. Reliability remains
unresolved pending targeted instrumentation if the timeout recurs.
