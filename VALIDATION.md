# Reference-test preparation

Current state: 60 exported tasks; initial two-task container runs completed with
environment failures. See SMOKE_RESULTS.md for the diagnostic rerun.
Finch historical PR/base lineage is verified in repository_audit/finch_lineage.json.

## Reproduce inputs

From the project root:

```sh
.venv/bin/python profile_elixir.py
.venv/bin/python prepare_validation.py
```

The export verifies dataset bytes and pinned evaluator source hashes. Large generated
validation_inputs files are ignored by Git. They contain reference solutions and
test patches: evaluator input only, never agent prompts or agent-mounted files.
validation_manifest.json records input hashes and smoke task IDs.

## Runtime prerequisite

This Mac is arm64 and Docker Desktop is installed. Verify `docker version`
shows both client and server. Inspect image
platform support before running; use a Linux amd64 host or supported emulation
if the published images are amd64-only. Record pulled image digests before tests.

The profiler environment is Python 3.9. The official evaluator requires Python
3.10+; .harness-venv was created locally with Python 3.12. It currently needs only
the standard library for the vendored evaluator/parser. No model SDK is needed.
On another machine, create this environment using its Python 3.10+ interpreter.

## First smoke run, once Docker is ready

```sh
mkdir -p validation_runs/smoke
.harness-venv/bin/python third_party/swe-rebench-v2/scripts/eval.py \
  --json validation_inputs/smoke.json --golden-eval --max-workers 1 \
  --report-json validation_runs/smoke/gold.json
```

This is an initial gold-patch smoke test, not full benchmark validation. The
unmodified upstream runner uses host networking, applies gold then test patch,
runs the supplied test command and compares parsed passing tests exactly with
FAIL_TO_PASS + PASS_TO_PASS. It has no per-task timeout. Review exit codes and
logs as well as passed_match; upstream all_ok alone is insufficient.

The local validate_reference.py wrapper now provides bounded execution,
base-commit checks, digest capture, and a base-only test phase. Confirm FAIL_TO_PASS fails on base and passes with
gold, while PASS_TO_PASS passes in both phases. The upstream runner refuses an
empty patch, so a blank override is not a valid base-only implementation.

Recorded diagnostic command (fresh output directory required):

```sh
.harness-venv/bin/python validate_reference.py \
  --output validation_runs/smoke-single-map --timeout 180 \
  --erl-flags '+JMsingle true'
```

The optional JIT override addresses emulation compatibility; it is not silently
enabled for future runs. The report records it alongside immutable image IDs.
The wrapper uses a Docker server-version preflight because `docker info` hung
on this installation. No global Docker or Erlang settings are changed.

Start with two tasks, inspect results and measure durations, then validate all
60. Separate environment failures from test failures and audit any replacements.
Only then connect the agent runner, decide model/budget limits and do a small
pilot before a full paid run.

Upstream source: https://github.com/SWE-rebench/SWE-rebench-V2/tree/c71902a8cf8d2b725f63d51f199f4d3e56f68d2d
Vendored files are unchanged; revision and hashes are in harness_config.json.

## Continuing while the draft includes a quarantine

Use `prepare_validation.py --diagnostic-ids ID1 ID2` to export a named subset of
non-excluded draft tasks without finalizing or resampling the study. This writes
validation_inputs/diagnostic.json and diagnostic_manifest.json; original smoke
inputs/manifest remain intact. Run validate_reference.py with
`--input validation_inputs/diagnostic.json --manifest diagnostic_manifest.json`
and a fresh `--output` directory. Both exporter and runner reject quarantined
IDs. Diagnostic batches do not establish a final balanced sample.

## Completed first pass

All original 60 tasks have recorded attempts. Run `.harness-venv/bin/python summarize_validation.py` to regenerate VALIDATION_RESULTS.md and validation_summary.json. These distinguish upstream gold passing-list matches from stricter before/after validation; neither is an agent success rate. See findings/validation-triage.md for unresolved log evidence. The runner can fetch missing images with --pull-missing and release only images downloaded by that invocation with --release-pulled-images. No global image pruning is performed.
