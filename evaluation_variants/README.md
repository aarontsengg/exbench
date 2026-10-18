# Repaired evaluation variants

These are separate from original upstream validation and the selected sample.
Each variant records exact adjustments, original and revised expectations, and
evidence. A successful variant is not automatically included in agent evaluation.

## Phoenix HTML #282 compatibility v1

`phoenixframework__phoenix_html-282--compatibility-v1.json` records a verified
transition in the existing repaired runs: base has 149 passing parsed IDs and
one failing ID (`content_tag`); gold passes all 150.

The variant adds only the five individually investigated date/template tests to
PASS_TO_PASS. FAIL_TO_PASS remains `content_tag`. It does not infer expectations
automatically from arbitrary passing output or discard failures. The original
dataset and strict validation summary are unchanged.

The shared compatibility patch changes library code: a fixed year anchor and a
fallback template line number. These changes must be disclosed if this variant
is ever evaluated. This is a diagnostic artifact, not a production library fix.

Run `.harness-venv/bin/python evaluation_variants/record_phoenix_html_282.py`
from the project root to verify existing log hashes and exact outcomes, then
regenerate the manifest. This command does not rerun containers. The raw logs
and original task export must be available locally.

Before final inclusion, the agent harness must apply the variant consistently
and use its explicitly versioned expectations. Repeated-run reliability and
native amd64 validation remain untested.

## Commanded #171 historical fixtures v1

`commanded__commanded-171--historical-fixtures-v1.json` records the audited
historical-runtime variant. Both seeds (42 and 7) have 202 raw tests: base has
one process-manager consistency failure and gold has none. The historical
parser produces 199 unique names because some test names repeat across modules.

The failure expectation is the individually reviewed dispatch-consistency test.
The complete remaining observed passing inventory is retained for regression
checking, with 17 former upstream failing IDs now listed as regressions and
40 additional IDs. This inventory was not individually audited for fairness;
it is not authorization to score agents against it yet.

Run `.harness-venv/bin/python evaluation_variants/record_commanded_171.py` to
verify both raw-log hashes, reparse results, check patch/image identities and
regenerate the manifest. No containers or model calls are started by this step.

Before agent scoring: integrate the variant and replace name-only test identity
with module-qualified identity so duplicate names cannot mask outcomes. Final
sample selection remains unchanged.

## Commanded #139 — hold for specification mismatch

The repaired historical suite passes gold under both tested seeds, but final
inclusion is on hold. Two router-validation assertions demand literal error
messages absent from the supplied issue/interface. The interface mentions error
types and conditions, which does not specify their exact wording. The deprecated
callback assertion also matches a literal message; the handler fixture repair
fixes its causal isolation but does not resolve wording fairness.

Do not classify a wording-only failure as inability to fix the OTP issue. No
assertion has been deleted or relaxed, and no task has been removed from the
saved draft. A future separately versioned repair must either explicitly specify
the public error contract or justify assertions on documented behavior. This
requires a consistent policy, not silently changing expectations to favor a run.
See `findings/commanded-batch/139-inclusion-decision.json`.

## Commanded #171 v2: distinct test identities

`commanded__commanded-171--historical-fixtures-v2.json` supersedes v1's name-only
inventory. It identifies tests by both module and name: 201 PASS_TO_PASS and one
FAIL_TO_PASS, totaling all 202 raw tests. Both saved seeds reproduce that exact
inventory and status transition. The original v1 remains available as evidence.

Three names collided: the local and Phoenix pubsub broadcast tests, their tracker
tests, and the event-handler/process-manager `__name__/0` tests. #139 similarly
has two PubSub collisions; all 179 identities are recovered with seven base
failures. No additional failures appeared in the audited runs.

Run `findings/commanded-batch/test_qualified_historical.py` for parser checks,
then `findings/commanded-batch/check_qualified_results.py` with the harness Python
environment to verify all eight saved logs and regenerate qualified evidence/v2.
The new parser requires serial trace output and rejects missing summaries,
inconsistent counts, orphan completions, and repeated completed identities.
It is a diagnostic adapter, not yet integrated into the agent grader. Sample
membership and original upstream validation results remain unchanged.
