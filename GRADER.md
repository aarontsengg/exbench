# Local grader prototype — Commanded #171

This accepts a proposed production patch and grades it against the audited
historical-fixtures-v2 evaluation. It does not run an AI or prepare agent prompts.
No final sample changes or paid model calls are involved.

```sh
.harness-venv/bin/python grade_patch.py --patch /absolute/path/to/proposed.patch --output validation_runs/my-first-grade
```

Use a new output directory per run. The retained historical Docker image,
prepared task export, variant, fixture, parser and evidence files must exist.
The grader checks evidence hashes and uses the immutable image ID. Only lib/
changes are accepted in this initial prototype. It applies the submitted patch,
then upstream evaluation tests and the shared fixture corrections in a fresh
container. No reference patch is supplied unless deliberately used as the
submitted patch for a smoke check. There is no network and a 300-second limit.

All 202 module-qualified identities must be present and passing, with exit code
zero. Failure, missing/extra tests, setup failure, timeout or inconsistent output
cannot produce a passing result. Original upstream grading remains untouched.
This is not hardened execution for adversarial submissions; lib code still runs
inside the container. Agent execution/prompt-policy integration is separate.

## Integration check (2026-10-18)

- Empty patch: rejected. The intended consistency test failed, plus a new timeout
  in CorrelationCasuationTest's event-handler causation-ID test. Raw: 202 tests,
  two failures. That regression timed out awaiting MoneyDeposited after 1000 ms.
- Reference production patch (lib changes extracted from the pinned reference):
  accepted, 202 tests and zero failures.
- Grading unit checks cover qualified-name separation, missing/extra tests,
  regressions, and nonzero test-run exit codes. Historical parser tests pass.

The newly observed timeout was absent in the earlier two-seed runs. Its cause
has not been established; it is a repeatability concern, not justification to
increase a timeout or delete the test. The prototype correctly rejects this
run, but the task is not approved for scored agent evaluation until this is
investigated. See findings/grader/integration-check.json for complete results,
log hashes, patch hashes and the exact failing identities.

## Commit checkpoint

The grader prototype, its tests, evaluation_variants, and small findings/scripts
are suitable for a progress commit. Suggested message:
`Add qualified Commanded grader prototype and record reliability findings`.

The .gitignore excludes train.parquet, validation_inputs, validation_runs and
virtual environments; none of those paths is currently tracked. Keep raw logs,
dataset downloads and Docker artifacts local. No commit or push was performed.
