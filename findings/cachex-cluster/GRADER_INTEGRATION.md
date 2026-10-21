# Cachex patch-grader integration — 20 October 2026

The shared `grade_patch.py` entry point now grades both Cachex variants using
their pinned historical images and complete module-qualified test inventories.
No agent was run and no tests or production code were modified by this integration.

| Task | Empty submission | Reference production patch |
| --- | --- | --- |
| #292 | Rejected: intended courier error-handling test fails | Accepted: 194/194 pass, exit 0 |
| #294 | Rejected: missing `async` API prevents compilation | Accepted: 195/195 pass, exit 0 |

These are seed-42 integration checks through the shared grader. They supplement
the earlier two-seed historical-runtime checks; they are not another two-seed
integration run. `grader-results.json` preserves complete results and hashes.

## Changes

- A variant can specify its repository working directory and whether the test
  command includes the distributed tag. Existing Commanded defaults are retained.
- The grader verifies hashes for the Cachex parser adapter and its imported
  qualified parser, plus the historical evidence and original test patch.
- #292 retains its observed FAIL_TO_PASS and PASS_TO_PASS partition.
- #294 uses REQUIRED_PASS for the complete gold inventory, avoiding an invented
  baseline partition. Missing, failing or incomplete tests and nonzero exits
  cannot pass. Its empty result is `invalid_or_incomplete_test_output` because
  compilation prevents a final test summary; `resolved` is false.
- Production submissions remain restricted to `lib/`; no reference code is
  injected unless explicitly supplied as the candidate in a positive control.

Four grader unit tests and three parser-adapter tests pass. The new grading test
checks that an expected-API baseline category cannot make empty, incomplete or
nonzero-exit output pass. Existing Commanded containers were not rerun: their
working-directory and test-command defaults are unchanged.

## Use

```sh
.harness-venv/bin/python grade_patch.py --variant evaluation_variants/whitfin__cachex-292--historical-integration-v1.json --patch /absolute/path/to/candidate.patch --output validation_runs/cachex-candidate-1
```

Use the #294 variant for that task and a fresh output directory each time.
`check_grader.py` reproduces all four controls with retained images, refusing to
overwrite its existing output. `prepare_cachex_integration.py` regenerates the
variant definitions from recorded historical evidence.

Passing these controls is not automatic final-sample inclusion or proof of
adversarial harness safety. #294 remains separately identified as an expected-API
compilation-failure candidate, and future agent prompts must include its supplied
interface consistently with other tasks. Original upstream validation totals
are unchanged. No model calls, commits or pushes.
