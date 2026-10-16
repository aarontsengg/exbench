# Baseline validation policy v1

Adopted before model evaluation. Apply the same rules to OTP and control tasks.

## Strict transition verified

The recorded base run has exactly the expected failing and passing test IDs;
the reference run exits successfully, passes the full expected set, and has no
failed tests. Keep this existing result unchanged.

## Expected API compilation failure

Record a separate, manually reviewed category when all of these hold:

1. The original base plus evaluation tests stops at compilation because an API is missing.
2. The issue or supplemental interface explicitly requires that API, including names or fields used by the tests.
3. Inspection connects the failure to that missing API, rather than unrelated runtime incompatibility, dependencies, or test-helper setup.
4. The original reference run passes the strict gold checks.
5. Saved review evidence matches the interface, image, and base/gold log hashes.

This category establishes an explained base compilation failure and a successful
reference run. It does not establish individual FAIL_TO_PASS transitions, full
behavioral coverage, or automatic final sample eligibility. Never report it as
strict transition validation or silently rewrite the upstream test lists.

The current reviewed cases are Poolex #59, Cachex #343, and Broadway #31.
CurlReq #53's helper setup failure and Plug #1245's unrelated cookie API changes
do not qualify. Other unresolved tasks require their own evidence review.

## Agent instructions and reporting

Future agent instructions must consistently include `problem_statement` and
`interface` for both groups. Do not supply `patch` or `test_patch`. The runner is
not yet integrated: verify the actual prompt construction before any model run.
Disclose that this is an issue-plus-interface evaluation, not an issue-only one.

Keep this category separate in reported counts and retain task IDs so later
results can be shown with and without these cases. Gold grading remains strict;
this policy does not relax reference-run requirements. Before scoring agents,
implement and verify the prompt policy and finalize an explicitly versioned
sample. No automatic sample replacement or expansion is authorized by this file.

`validation_policy.json` stores the reviewed evidence. `summarize_validation.py`
checks that evidence before annotating the report, preserving original statuses.
