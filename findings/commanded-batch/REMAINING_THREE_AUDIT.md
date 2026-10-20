# Remaining Commanded tasks — 2026-10-18

Scope: #290, #335, #380 only. No model calls or final sample changes.

## Issue alignment

### #290: idle timeout

Four added tests check inactivity shutdown, infinity keeping a process alive,
and explicit stopping with both finite/infinite settings. A fifth checks event
handling through the new keyword-list start_link/1 API. The issue names the
idle_timeout option; the supplemental interface explicitly documents the API
change. Original base failures reject the option or lack start_link/1, so these
are expected feature/API-transition failures, not environment setup failures.

There is a potential monitor race in two explicit-stop tests: the monitor is
installed after dispatching Stop. No assertion was changed for this theoretical
risk; a failing :noproc outcome would warrant investigation if observed.

The repeated reference runs instead exposed unrelated missing local PubSub
tracker registries. Setup tests only for existence of the main registry, while
an old test supervisor can be shutting down. A separate fixture patch stops the
Commanded application before adapter setup, starts a fresh adapter supervisor,
unlinks it, and synchronously stops it in on_exit. Both Local and Phoenix tests
get explicit ownership/cleanup. Assertions remain unchanged.

### #335: empty-list routing

The added test sends an empty-target start followed by a normal start. In base,
the normal instance is never created: the error is process_manager_not_found,
not merely a PID-versus-tuple mismatch. This directly tests continued routing
after an empty list. Other failing tests demand {:ok, pid} from process_instance;
that ancillary return-contract change is explicitly described in the interface.
Do not treat all 18 transitions as independent empty-list behavioral tests.

The upstream expected subscription-shutdown failure is intermittent: one new
base run fails while another passes. Logs show :noproc instead of :normal. The
mock sends the test a subscribed notification *inside* subscribe_to, before
ProcessRouter installs Process.monitor after subscribe_to returns. Thus the
test can kill the subscription too early. The diagnostic fixture uses
:sys.get_state to wait for the router's callback to complete and checks that its
subscription_ref is installed before triggering shutdown. The existing exit
reason assertion remains intact; there is no arbitrary sleep or timeout increase.

### #380: apply exceptions

The added test raises a RuntimeError in the process manager's apply/2, checks
that error/3 receives it, and monitors the router's resulting shutdown. The
helper itself supplies the exception message and returns {:stop, error}; the
message assertion is not an unspecified library error string. This matches the
reported missing exception handling. No fixture repair proposed.

## Method and limits

Fresh containers from the previously recorded immutable historical images,
original reference patch only in gold and original test patch in both phases.
Original distributed inclusion is retained; max-cases 1 and seeds 42/7 make
module execution serial and vary order. Epmd runs locally; network is disabled.
Each run has a 300-second limit. Qualified identities must reconcile with raw
suite totals. Original evidence and upstream expectations remain untouched.

`check_remaining_three.py` performs the unmodified suite repetitions; its
`--fixtures` option separately repeats #290 and #335 with only the fixture
patches above. Recorded results include image identity, patch hashes, raw-log
hashes, exact commands, exit codes and qualified outcomes. Repeated success is
limited evidence, not proof of freedom from scheduling-dependent failures.

## Results and decisions

Twenty full-suite runs completed: twelve initial repetitions plus eight with
fixture repairs. Counts below are qualified test identities, reconciled to the
raw suite summaries. Both orders were seeds 42 and 7.

| Task / setup | Base failures (42 / 7) | Gold failures (42 / 7) | Suite size |
| --- | --- | --- | --- |
| #290 historical, original fixtures | 5 / 6 | 1 / 1 | 212 |
| #290 isolated PubSub fixtures | 5 / 5 | 0 / 0 | 212 |
| #335 historical, original fixtures | 19 / 18 | 0 / 0 | 340 |
| #335 subscription-monitor barrier | 18 / 19 | 0 / 0 | 340 |
| #380 historical, original fixtures | 1 / 1 | 0 / 0 | 360 |

**#290:** qualified passing and failing inventories agree across repaired seeds.
Record a historical-reviewed variant, retaining the full regression inventory.
The five reviewed failures exactly match upstream FAIL_TO_PASS. The theoretical
monitor-after-stop race did not occur in these runs and remains a limitation.

**#380:** qualified inventories agree across both seeds, with the one intended
apply-exception failure before the fix. Record a historical-reviewed variant;
no test fixture repair was needed. This is the clearest of the three outcomes.

**#335:** the monitor barrier prevents the subscription-shutdown race in both
runs. However, repaired seed 7 fails an additional regression:
Commanded.Event.HandleEventTest / reset event handler should be reset when
starting from :current. It expects ["PREF_ACC1234"] but receives []. Gold passes
both seeds. This is preserved as a reliability hold, not dropped or promoted.
The test sends asynchronous :reset and immediately appends a new event; a
subscription readiness race is a plausible next lead, not a verified cause.
See `335-inclusion-decision.json` and the full raw-log hashes.

`evaluation_variants/record_remaining_commanded.py` verifies hashes, suite
counts, seed agreement and reviewed failure names before writing #290/#380
manifests. #335 deliberately has no new scored variant. Neither recorded variant
is selected automatically; the current patch grader supports #171 only.
No upstream expectations, original validation totals or saved pairs changed.

This is a progress-commit checkpoint: save the scripts, fixture patches,
small result reports, audit and variant manifests. Keep validation_runs ignored.
Suggested message: `Audit remaining Commanded tasks and record fixture repairs`.
