# Commanded integration repairs — 2026-10-18

Scope: #139, #171, #290, #335, #380. No model calls, final sample changes,
upstream data rewrites, or production compatibility patches.

## Changes

- #139: preserve ArgumentError checks for invalid configuration, but remove
  unspecified literal-message requirements. Keep the corrected valid-handler
  fixture so the obsolete-lifespan test fails for the intended reason.
- #171: preserve application startup/PubSub cleanup repairs. During integrated
  testing a subscription test read state before its broadcast acknowledgement
  arrived. Its v2 fixture waits for the named handler's acknowledgement through
  the existing wait_for API, then runs the original assertions. Timeout settings
  are unchanged. This repairs an observed acknowledgement race, not the separate
  earlier MoneyDeposited timeout whose root cause remains unestablished.
  V3 isolates both PubSub adapter supervisors. It also restarts the application
  before each subscription test: the stale-ack test schedules recurring zero-TTL
  purges, which otherwise leak into the fresh-ack test. Resetting ETS alone does
  not stop that timer. The expiry implementation and assertions are unchanged.
- #290: retain isolated PubSub test supervisors and synchronous cleanup. In v2,
  install process monitors before Stop dispatch, avoiding a race where monitoring
  a process that already stopped yields :noproc instead of its normal exit.
- #335: wait for the process-manager subscription monitor and event-handler
  subscription monitor before triggering shutdown. Wait for :reset to finish
  resubscribing before publishing the next event. This tests post-reset delivery
  rather than racing event publication against reset. Existing assertions remain.
- #380: integrated runs exposed the same reset/publication race as #335, so apply
  the same synchronization. V2 incorrectly copied a flat monitor-state pattern
  from #335; v3 reads the nested Subscription struct used by #380. Both failed
  v2 runs are preserved. No production code or timeouts were changed.

The three relaxed assertions in #139 are the only removed assertion requirements:
exact error prose was unspecified. Exception type and invalid-input scenarios
remain enforced. Other tasks retain behavioral assertions and timeout values.

## Grader

`grade_patch.py --variant <manifest> --patch <candidate.patch> --output <new-dir>`
now supports all five versioned configurations, including variants without a
fixture patch. It verifies the test patch, parser, fixture and expected inventory,
applies the submitted lib/ patch in a fresh immutable-image container, and checks
all module-qualified results plus process exit status. Missing/extra/duplicate
identities and incomplete logs cannot pass. It does not launch an agent.

`prepare_commanded_integration.py` regenerates v1 candidate definitions from
reviewed inventories; `prepare_commanded_followups.py` builds v2 for #171, #290,
and #335, plus #380. The separate `prepare_commanded_171_v3.py` and
`prepare_commanded_380_v3.py` scripts produce the final fixture corrections.
`check_all_commanded.py` runs empty/reference checks at seeds 42 and 7;
`--followups` separately verifies v2, and `--final-171` / `--final-380` verify v3.
Original failures are retained.

The full reference production diff is used as a submitted patch in positive
controls. No reference patch is automatically added by the grader. Empty
submissions are negative controls. Both see the same evaluation/setup patches.

## Interpretation

Final evidence verification completed 2026-10-19. Each row reproduced at seeds
42 and 7 in fresh containers, with complete module-qualified inventories:

| Task | Current variant | Original-code failures | Reference passing tests |
| --- | --- | ---: | ---: |
| #139 | integration-v1 | 7 | 179/179 |
| #171 | integration-v3 | 1 | 202/202 |
| #290 | integration-v2 | 5 | 212/212 |
| #335 | integration-v2 | 18 | 340/340 |
| #380 | integration-v3 | 1 | 360/360 |

All ten empty-patch controls were rejected for exactly their recorded failure
sets, and all ten reference controls passed. The verified summary is
`commanded-integration-summary.json`. Six grader/parser unit tests also pass.

Local check success means the grader distinguishes these empty/reference controls
under the recorded setup. It does not prove arbitrary agents cannot exploit the
harness, certify absence of intermittent failures, or establish final sample
eligibility. Earlier #171 deposit timeout remains a reliability caveat even if
it does not recur. Keep all historical failed runs; never relabel them as passes.
