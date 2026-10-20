# Local grader prototype — Commanded

This accepts a proposed production patch and grades it against a versioned
evaluation for Commanded #139, #171, #290, #335, or #380. It does not run an AI or prepare agent prompts.
No final sample changes or paid model calls are involved.

```sh
.harness-venv/bin/python grade_patch.py --variant evaluation_variants/commanded__commanded-171--integration-v3.json --patch /absolute/path/to/proposed.patch --output validation_runs/my-first-grade
```

Use a new output directory per run. The retained historical Docker image,
prepared task export, variant, fixture, parser and evidence files must exist.
The grader checks evidence hashes and uses the immutable image ID. Only lib/
changes are accepted in this initial prototype. It applies the submitted patch,
then upstream evaluation tests and the shared fixture corrections in a fresh
container. No reference patch is supplied unless deliberately used as the
submitted patch for a smoke check. There is no network and a 300-second limit.

All module-qualified identities in the chosen variant must be present and passing, with exit code
zero. Failure, missing/extra tests, setup failure, timeout or inconsistent output
cannot produce a passing result. Original upstream grading remains untouched.
This is not hardened execution for adversarial submissions; lib code still runs
inside the container. Agent execution/prompt-policy integration is separate.

## Earlier integration check (preserved evidence)

- Empty patch: rejected. The intended consistency test failed, plus a new timeout
  in CorrelationCasuationTest's event-handler causation-ID test. Raw: 202 tests,
  two failures. That regression timed out awaiting MoneyDeposited after 1000 ms.
- Reference production patch (lib changes extracted from the pinned reference):
  accepted, 202 tests and zero failures.
- Grading unit checks cover qualified-name separation, missing/extra tests,
  regressions, and nonzero test-run exit codes. Historical parser tests pass.

That timeout was absent in the earlier two-seed runs. Its cause
has not been established; it is a repeatability concern, not justification to
increase a timeout or delete the test. The prototype correctly rejects this
run, but the task is not approved for scored agent evaluation until this is
investigated. See findings/grader/integration-check.json for complete results,
log hashes, patch hashes and the exact failing identities.

## Current integration variants (2026-10-18)

Use #139 integration-v1, #171 integration-v3, #290 integration-v2,
#335 integration-v2, and #380 integration-v3. Without --variant the default is
#171 integration-v3. Use --seed to control test order (default 42).

The repairs isolate test supervisors/timers, synchronize asynchronous test
setup, and remove three unspecified exact-message requirements from #139 while
retaining exception-type assertions. They do not change production code. See
findings/grader/COMMANDED_REPAIRS.md for the rationale and retained failures.

findings/grader/commanded-integration-summary.json records verified controls
and hashes for the current variants. The accompanying summarizer verifies
both seeds, exact failure sets, complete inventories, submitted patch hashes,
variant hashes, and raw log hashes. It requires local validation_runs artifacts.

These checks establish local empty/reference behavior, not final sample
eligibility or readiness for adversarial agents. The earlier #171 deposit
timeout remains unresolved even though later checks do not reproduce it.
No original upstream validation counts are changed.

## Commit checkpoint

The grader prototype, its tests, evaluation_variants, and small findings/scripts
are suitable for a progress commit. Suggested message:
`Integrate Commanded graders and repair test synchronization`.

The .gitignore excludes train.parquet, validation_inputs, validation_runs and
virtual environments; none of those paths is currently tracked. Keep raw logs,
dataset downloads and Docker artifacts local. No commit or push was performed.
