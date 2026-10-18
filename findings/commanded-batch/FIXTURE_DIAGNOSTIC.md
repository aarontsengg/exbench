# Commanded test-fixture diagnostics — 2026-10-16

Both #139 and #171 can complete with zero reference-fixed failures after narrow
changes to test setup in the retained historical images. This does not establish
unchanged-upstream validity: both observed failure partitions differ from the
upstream FAIL_TO_PASS lists.

## Controlled comparisons

Each run used a fresh container, the same immutable image as its earlier
historical run, original test patch, reference patch only in gold, local epmd,
no external network, and a 300-second limit. Command:
`mix test --trace --max-cases 1 --seed 42`.
This explicitly serializes test modules and fixes ordering; it differs from the
original `mix test --trace --include distributed`. These source trees start
ExUnit without exclusions and contain no distributed test tags found by source
search. Both versions execute 179 / 202 raw tests respectively. A fixed seed
does not fix scheduler timing. No production code or test assertions changed.

| Task / setup | Base failures | Gold failures | Raw tests per phase |
| --- | ---: | ---: | ---: |
| #139 unchanged | 22 | 15 | 179 |
| #139 explicit application startup | 7 | 0 | 179 |
| #171 unchanged | 16 | 15 | 202 |
| #171 explicit application startup | 2 | 2 | 202 |
| #171 startup + explicit PubSub cleanup | 1 | 0 | 202 |

## What changed and why

**#139:** SubscriptionsTest calls Subscriptions.reset without ensuring its named
process exists. StorageCase stops the application after its tests. Adding
Application.ensure_all_started(:commanded) before reset, and after configuring
local PubSub in LocalPubSubTest, removed all 15 gold failures. The same setup
patch in base leaves seven failures; all seven pass in gold, with no lost
passing IDs. See `139-fixture-startup.patch`.

**#171:** The same subscription setup omission accounts for 15 failures.
Its local PubSub test already starts a supervisor, so it was not changed.
The Phoenix PubSub test starts a named supervisor per test without explicit
synchronous teardown. Logs show `already started` errors; they vary between
runs, and can spill into a subsequent event-store test's application startup.
The additional patch retains the supervisor PID, unlinks it from the test
process, and synchronously stops it in on_exit before removing configuration.
With that cleanup, base has only the process-manager consistency timeout,
while gold passes all 202 tests. See `171-fixture-startup-cleanup.patch`.
The earlier historical report's generic description of #171's remaining failure
as a missing shared process was incomplete: its Phoenix tracker failure was an
already-started collision, not a missing local registry.

## Why these are not final benchmark approvals

- #139: 19 of 22 upstream expected failures already pass on base. Three recorded
  failures reproduce, plus four aggregate-lifespan failures absent from the
  recorded list. Those four are plausibly relevant to the issue (changing
  lifespan callbacks from commands to events), but relevance needs an explicit
  issue/assertion audit before selecting a repaired expectation set.
- #171: 17 of 18 upstream expected failures already pass on base. Only
  `process manager consistency should successfully dispatch command` reproduces
  and becomes passing in gold.
- Gold passes 61 / 40 additional unique parsed IDs for #139 / #171, respectively,
  beyond the upstream expected union. No expected gold IDs are missing.
- Results use the explicit historical ExUnit parser. Names repeated across test
  modules collapse to a single ID, so raw test counts and parsed IDs differ.
- One run per setup and phase is diagnostic evidence, not a stability estimate.
  The #171 collision varied even at seed 42 before cleanup. Multiple seeds and
  repeats remain necessary before adopting a variant.
- Original validation statuses, expected lists, sample membership, and headline
  counts remain unchanged. No model calls were made.

## Reproduction and evidence

`run_fixture_diagnostic.py` runs the original/startup comparison for both tasks.
`run_fixture_diagnostic.py --cleanup-only` runs #171 with both fixture changes.
Both refuse to overwrite an existing report. Retained historical images and
source contexts are required; no downloads are performed.

`summarize_fixture_diagnostic.py` verifies raw-log SHA-256 values and pinned
upstream helper hashes, then writes comparisons to
`fixture-startup-result.json` and `fixture-startup-cleanup-result.json`.
Those reports record image identity, base commit, patch hashes, log hashes,
commands, timeouts, exit codes, full parsed results, and expectation mismatches.
Raw logs remain under `validation_runs/commanded-fixture-diagnostic*`.

Next: audit the seven / one observed transitions against each issue, then test
repeatability of any proposed historical evaluation variant. A clean gold run
alone is insufficient for acceptance.
