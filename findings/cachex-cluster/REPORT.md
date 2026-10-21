# Cachex cluster diagnostic — 19 October 2026

**Historical comparison completed:** see [HISTORICAL.md](HISTORICAL.md). Both
reference suites now pass at two seeds under the documented older environment.
The findings below preserve the earlier diagnostic and remaining concerns at
that point in the investigation.

## Follow-up — 20 October 2026

The parser discrepancy is explained: three names collide across modules.
`checking if a cache cluster is empty` occurs twice, `adding new entries to a
cache cluster` four times, and `multiple slots will return a :cross_slot error`
three times. Collapsing these loses 1 + 3 + 2 = 6 identities.

`audit_identities.py` adapts modern serial trace decorations to the strict
module-qualified parser. It recovers all 194 tests in both #292 phases and all
195 in #294 gold, with failure counts matching raw summaries. Results and log
hashes are in `qualified-results.json`. Three adapter tests pass, including
rejection of incomplete traces. This is a diagnostic adapter, not a change to
upstream grading or the shared grader. #294 baseline still has no test inventory
because compilation fails.

The pinned `.github/workflows/ci.yml` files explicitly start epmd. Both use
Elixir 1.13 / OTP 24.3 as the primary test combination, with older combinations
also listed. The failing modern runs use Elixir 1.16.3 / OTP 26. The source
`mix.exs` requirement `~> 1.5` is broad and does not itself pin a runtime.
Neither base commit has a root mix.lock (HTTP 404); dependency versions need
explicit preservation when building a comparison environment.

The saved assertion source confirms a fixed memory expectation of 10,624 bytes
and a separate human-readable expectation around 10 KiB. The TTL failure occurs
after a 25 ms sleep and before the test calls refresh, so it does not demonstrate
that refresh itself is broken. It demonstrates that the timing precondition did
not hold in that run.

Next experiment: compare with the CI-supported Elixir 1.13 / OTP 24.3 runtime,
retaining epmd, source commits, and recorded dependencies. No historical-runtime
container has been built or run by this follow-up. Runtime causality remains
unproven; no expectations were relaxed. Source URLs and hashes are in
`sources.json`.

## Original diagnostic

Starting `epmd` before tests removes the previously observed `econnrefused` /
`:not_alive` cluster-startup failures for #292 and #294. Neither task is yet
validated for scoring.

The rerun used the same immutable image IDs as the original runs, the same
upstream patches/test commands and the same `+JMsingle true` override. The only
intentional setup change was starting epmd in both phases. Test order was not
pinned; timing failures cannot be causally attributed to this change. Downloaded
images were released by the runner afterward. No production/test patches were
modified and no model calls were made.

| Task | Phase | Raw suite | Remaining failures |
| --- | --- | --- | --- |
| #292 | Original | 194 tests, 2 failures | Expected courier error handling; memory-size assertion |
| #292 | Reference | 194 tests, 2 failures | Memory-size assertion; TTL timing assertion |
| #294 | Original | Does not compile | Missing `async` field in warmer record |
| #294 | Reference | 195 tests, 1 failure | Memory-size assertion |

Original gold logs had 31 parsed failures each. New logs contain no occurrences
of `:not_alive` or `econnrefused`. This supports the missing port-mapper explanation
for the cluster-startup failures, not a claim that all distributed behavior is
correct or stable.

## Remaining blockers

- Both reference runs report memory usage 60,552 against an expected 10,624,
  tolerance 1,000. This is consistent with a runtime-sensitive assertion, but a
  compatible-runtime comparison is needed before assigning a root cause. Do not
  replace the expected number with the observed value just to pass.
- #292's reference TTL refresh test observed 929 ms against 970 ms, tolerance
  6 ms. Scheduling/emulation sensitivity is plausible, not established. Preserve
  the failure; do not silently widen the tolerance.
- #294's interface explicitly specifies `warmer(... async: boolean \\ false)`.
  That explains the baseline compilation failure, but gold still fails. It does
  not yet satisfy our expected-missing-API eligibility policy.
- The upstream name-only parser returns 188 identities for #292's 194 raw tests
  and 189 for #294's 195 raw tests. The six-test shortfall must be investigated
  before complete test coverage can be claimed; do not equate parsed-name counts
  with raw test counts.

#341 was not rerun: its observed blocker is a hook-duration assertion, not the
cluster-startup failure. #343 remains in the separate reviewed compilation-failure
category; #348's existing strict result is unchanged.

## Evidence and next step

`epmd-results.json` preserves original/new results, image identities, source and
log hashes, raw summaries, and startup-error counts. `summarize.py` checks image
identity equality and regenerates this evidence from local reports. Raw logs are
under ignored `validation_runs/cachex-epmd/`.

Next: inspect the parser discrepancy and the repository's historical runtime
requirements, then test a justified compatible environment with epmd retained.
Original validation totals and sample membership remain unchanged.

Reproduction (use a new output directory):

```sh
.venv/bin/python prepare_validation.py --diagnostic-ids whitfin__cachex-292 whitfin__cachex-294
.harness-venv/bin/python validate_reference.py --input validation_inputs/diagnostic.json --manifest diagnostic_manifest.json --output validation_runs/cachex-epmd-rerun --timeout 300 --erl-flags '+JMsingle true' --start-epmd --pull-missing --release-pulled-images
```
