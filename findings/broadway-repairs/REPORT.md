# Broadway #40 and #95 — 20 October 2026

Test-only diagnostic repairs remove the shared log-format blocker. #95's
reference now passes both orders; #40 still has a reference failure. Neither is
automatically eligible for scoring.

## Repairs and rationale

Both tasks require error logs to contain the literal phrase
`function Unknown.ack/N is undefined`. Modern logs instead contain
`(UndefinedFunctionError) undefined function`. The issue/interface does not
specify that prose. Both repaired tests still require the error log and exception
type, successful acknowledgements and the existing no-exit assertion. Only the
unspecified message suffix is removed, following the documented versioned-repair
policy. This is a test-contract change, not an unchanged upstream evaluation.

#95's no-batcher shutdown test calls `Process.exit` on a linked pipeline without
trapping exits. Its other shutdown tests do trap exits. The repair enables
trapping in this test, retains all four message acknowledgements and adds an
assertion for the expected pipeline `:shutdown` exit. No production code or
timeouts are changed. Both repairs apply identically to base and reference.

## Results

Fresh containers use the original immutable images, linux/amd64 emulation,
`+JMsingle true`, host networking, and explicit seeds. Pinned source files were
retrieved from `dashbitco/broadway` at the original task commits.

| Task | Seed | Original failures | Reference failures | Complete inventory |
| --- | --- | ---: | ---: | --- |
| #40 | 42 | 4 | 0 | 85 tests |
| #40 | 7 | 4 | 1 | 85 tests |
| #95 | 42 | 20 | 0 | 100 tests + 1 doctest |
| #95 | 7 | 19 | 0 | 100 tests + 1 doctest |

## Remaining concerns

**#40:** The seed-7 reference fails `handle batcher crash only the messages in
the crashing batcher are lost`: expected `[6, 7]`, observed `[4, 5]`. This is a
behavioral mismatch, not just log formatting, and remains unexplained.

Both original-code runs also fail the bad-acknowledger consumer test, outside the
three upstream FAIL_TO_PASS names. The reference separately adds a try/catch
around acknowledgement handling in `lib/broadway/consumer.ex`. That requirement
is not described in the `push_messages/2` issue/interface. Keep this as a scope
concern; do not silently redefine four failures as the intended task.

**#95:** Both base runs fail the 18 upstream FAIL_TO_PASS names plus the consumer
bad-acknowledger test, because it calls the missing `Broadway.test_messages/3`.
The interface explicitly requires that API, so this additional failure is
explained, but needs an explicit versioned expectation decision. Seed 42 also
fails the cancellation test waiting for `:message_during_cancel`; the mailbox
contains producer initialization and shutdown messages. Seed 7 does not fail
that test. Initialization/cancellation ordering is a hypothesis, not an
established cause. Preserve this baseline variability.

## Parser and evidence

The initial runner reused a parser that rejected #95's doctest summary. Those
parse errors are retained in `results-v1.json`; they are not empty passing
inventories. `summarize.py` reparses the same hashed logs with `parse_trace.py`,
which retains doctests as distinct identities and requires raw totals to match.
`qualified-results-v1.json` contains the corrected complete inventories. Four
parser tests pass, including failed/missing doctests and carriage-return traces.
Future `check.py` runs use this adapter directly.

Repair patches, original pinned test sources, image IDs and source/patch/log
hashes are saved here. Raw logs remain under ignored
`validation_runs/broadway-repairs-v1/`. Both images are retained for follow-up.

No model calls, sample changes, upstream expectation rewrites, commits or pushes.
Next: investigate #95's cancellation fixture before grader integration; keep
#40 on hold for both reliability and task-scope review.

## #95 readiness experiment (v2)

The pinned `Broadway.Subscriber` uses `GenStage.async_subscribe`; producer
initialization alone does not establish end-to-end readiness. The cancellation
test shuts down immediately after `Broadway.start_link`. The terminator sends
draining/cancellation signals through the stages. These observations suggest an
ordering issue but do not establish the precise failing interleaving.

`95-readiness-v2.patch` adds a full four-message batch and waits for its
acknowledgement before shutdown. It uses the existing test helper rather than
the new `test_messages/3` API being evaluated. All original cancellation
assertions, including rejection of the late message, remain unchanged. No
production changes, sleeps or timeout increases were added. This patch is
applied after the v1 test repairs, identically to base and reference.

| Seed | Base failures | Reference failures | Cancellation check |
| --- | ---: | ---: | --- |
| 42 | 19 | 0 | passes in both phases |
| 7 | 19 | 0 | passes in both phases |

All four inventories contain 100 tests plus one doctest. The two baseline
failure sets are identical: the 18 upstream expected failures and the additional
bad-acknowledger test invoking the missing, specified `test_messages/3` API.
Four parser unit tests also pass.

This is evidence that establishing readiness removes the observed variability
in these runs, not proof that the original immediate-shutdown behavior is
correct. The revised test exercises shutdown of an established pipeline and
does not retain coverage of immediate startup/shutdown. It remains a diagnostic
candidate, not an automatically adopted evaluation repair. Any integration must
explicitly record this scenario change and the additional expected failure.

Reproduce with `check_cancellation.py` using the retained immutable image. The
runner refuses to overwrite the evidence directory. Results, patch hashes and
log hashes are in `cancellation-results-v2.json`; raw logs are under
`validation_runs/broadway-cancellation-v2/`. The three `95-*.ex` source snapshots
were fetched from `dashbitco/broadway` at base commit
`ec377ca3ed62fd805907b117f4c6c13c3bd31cdf`.
No sample, grader or expectation manifest was changed; no model calls occurred.

## Grader integration attempt: hold

The readiness repair is acceptable for a separately disclosed established-pipeline
scenario under the fixture-synchronization policy. It uses existing message
delivery, retains cancellation assertions and does not implement the target fix.
It does not establish immediate-startup shutdown correctness.

Created `plataformatec__broadway-95--integration-v1` with 19 observed FAIL_TO_PASS
and 82 PASS_TO_PASS identities, preserving upstream lists separately. Actual
grader checks used network isolation and explicit `+JMsingle true`:

| Seed | Empty patch | Reference patch |
| --- | --- | --- |
| 42 | rejected, 19 failures | rejected, 1 failure |
| 7 | rejected, 19 failures | accepted, 101 passing |

The new failure is **pipeline without batchers shutting down broadway waits
until all events are processed**. The seed-42 reference receives shutdown but
not the expected acknowledgement for data `3` within 100ms. This is distinct
from the cancellation test repaired above. The log does not prove whether
this is lost work or delayed delivery, nor whether networking changes
contributed. Do not weaken the assertion or call integration successful.

Manifest status is `hold_reference_shutdown_variability`; final selection is
false. `grader-results-v1.json` retains all four results and log hashes; raw
output is in `validation_runs/broadway-grader-v1/`. Result manifest hashes
record its pre-hold state. The shared grader supports an explicit ERL_FLAGS
override; existing variants retain image defaults. Four grader unit tests pass.
Next: investigate the separate no-batcher shutdown ordering before promotion.

## No-batcher readiness experiment: broader shutdown variability

Added one ordinary warm-up message and acknowledgement before suspending the
producer in the no-batcher test. The original four messages are still queued
while suspended; shutdown precedes resume; all four acknowledgement assertions
and the shutdown exit assertion are unchanged. This is a diagnostic patch only.

The no-batcher shutdown test passes in all four new runs. Empty patches retain
19 failures at seeds 42 and 7. Reference seed 7 passes 101 checks, but reference
seed 42 fails **shutdown shutting down broadway waits until all events are
processed even on incomplete batches**: expected acknowledgement for `[1, 2]`
is absent after 100ms; the mailbox contains producer initialization and pipeline
shutdown. All inventories contain 100 tests plus one doctest.

GenStage's pinned source documents `async_info` as queued behind buffered
messages; `:accumulate` suppresses forwarding new demand to the callback, not
necessarily draining buffered events. The observed missing acknowledgement
cannot safely be explained just by the producer's maximum demand of two.
Neither message loss nor the precise failing interleaving has been proven.

This weakens the claim that a single fixture repair resolves #95. Keep the
integration manifest on hold; do not adopt this additional repair or rewrite
expectations. A useful next diagnostic is a focused event trace of subscription,
message dispatch and cancellation during the incomplete-batch failure, or a
comparison on native amd64. Do not increase timeouts or add warm-ups to every
test simply to obtain passing runs.

Evidence: `check_no_batcher.py`, `95-no-batcher-readiness-v2.patch`,
`no-batcher-diagnostic-v2.json`, `no-batcher-results-v2.json`; raw logs under
`validation_runs/broadway-no-batcher-v2/`. No models or final sample changes.

## Shutdown trace: terminator exits without draining

Tracing before pipeline creation captured the target failure in v3 run 2.
The other startup-traced runs passed the target; run 1 failed the distinct
no-batcher shutdown test, and run 3 passed the whole suite. Each run has 101
parsed checks. Earlier v2 traces started after startup and all passed. v1
tracing had a recorder file-ownership bug and is invalid as test evidence;
its logs are preserved, not counted as benchmark failures.

In the failing trace (`validation_runs/broadway-shutdown-trace-v3/2/events.log`):

- Line 99 identifies PID 0.1566.0 as the terminator.
- Line 121: server sends the asynchronous `:trap_exit` cast.
- Line 122: the supervisor receives shutdown.
- Line 123: the terminator has a receive trace for the cast.
- Line 124: the terminator exits with `:shutdown`.
- No `:never_resubscribe`, `:prepare_for_draining`, or `:cancel_consumers`
  signals appear. No target acknowledgement is sent. The pipeline exits and
  the test then times out waiting for the acknowledgement.

A receive trace is not proof the callback completed. Pinned `95-server.ex`
lines 43–46 invokes `Terminator.trap_exit` then immediately signals the
supervisor. `95-terminator.ex` implements that request with `GenServer.cast`;
`Process.flag(:trap_exit, true)` runs later inside its callback. There is no
synchronous confirmation before the supervisor begins shutdown. This is a
concrete ordering vulnerability, strongly supported by the captured failure:
the terminator can exit before enabling exit trapping and executing its drain
callback. The passing trace instead shows drain propagation, acknowledgements,
consumer `:done`, then termination.

This evidence supersedes the earlier assumption that startup readiness alone
would resolve shutdown variability. It does not prove that every previous
shutdown failure has this same cause. Longer receive timeouts would not make
the captured exited pipeline drain its remaining messages.

**Decision:** keep #95 on hold. A synchronous trap-exit handshake is a plausible
production-code diagnostic, but has NOT been applied. Such a fix would be an
additional environment/production repair outside the batching issue, not a
mere fixture synchronization change. Evaluate and disclose that separately
before any grading use. Do not promote the warm-up patches as a root-cause fix.

`trace_shutdown.py` reproduces the startup trace; earlier recorder versions are
retained. `trace-analysis-v3.json` stores parsed outcomes, compact event excerpts
and source/log hashes; `summarize_trace.py` regenerates it. No paid calls,
production fixes, final sample changes, commits or pushes.

## Synchronous handshake repair (user-authorized production diagnostic)

`95-handshake-v2.patch` changes `Terminator.trap_exit/1` from a cast to a call.
Its callback enables exit trapping before replying `:ok`. The server therefore
cannot initiate supervisor shutdown until the coordinator is ready.

The initial call-only repair exposed a regression in the existing killed-
supervisor test: calling an already-dead terminator replaced `:killed` with a
`:noproc` error. V2 marks the supervisor absent when receiving its EXIT and
skips redundant shutdown coordination in that case, preserving the original
exit reason. This is a production repair, applied equally to base and reference
in a separate diagnostic. No upstream dataset contents were modified.

Validation removes both readiness/warm-up workarounds and all tracing. Only
v1 test compatibility repairs remain (unspecified exception wording and the
no-batcher test's exit trapping). No timeouts or behavioral assertions changed.

| Check | Outcome |
| --- | --- |
| Focused handshake regression, original code | fails: call returns while coordinator is suspended |
| Focused handshake regression, repaired code | passes: blocks until resume, then confirms exit trapping |
| Base + handshake, seeds 42 / 7 / 123 | identical 19 failures, 101 checks each |
| Reference + handshake, seeds 42 / 7 / 123 | 101 passing, zero failures each |

These runs support the repair; three orders are not proof of universal timing
stability. The focused regression in the first attempt called the wrong
start_link arity and is invalid evidence. The corrected regression is
`handshake_test_v2.exs`. Its single-test summary required singular-to-plural
normalization in `summarize_handshake.py`; original parser errors remain in the
raw result file, with corrected verification in `handshake-summary-v2.json`.

Reproduce with `check_handshake_v2.py`, then `summarize_handshake.py`. Results
and hashes are in `handshake-results-v2.json`, raw logs in
`validation_runs/broadway-handshake-v2/`. Earlier failed experiments remain.

The fix is saved and tested, but the old integration-v1 manifest remains on
hold because it does not include this production repair. Next integration must
use a new version, explicitly disclose the production change, and omit the
superseded readiness workarounds. No final sample inclusion, paid calls, commit
or push occurred.

## Grader v2 verified

Integrated the production handshake as a separately hashed `production_patch`,
applied before candidate patches. V2 uses only the earlier test compatibility
repair; no warm-ups or tracing. Both empty submissions fail with exactly 19
expected failures, and both reference submissions pass all 101 checks at seeds
42 and 7. All inventories are complete. See `GRADER_V2.md` and
`grader-results-v2.json`. Final sample selection remains false; v1 stays held.
