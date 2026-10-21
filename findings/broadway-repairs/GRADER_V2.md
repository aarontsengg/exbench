# Broadway #95 grader integration v2

Local empty/reference integration checks pass at seeds 42 and 7. Both empty
submissions have exactly the 19 recorded failures; both reference submissions
pass all 101 checks with exit code zero. Inventories contain no missing or
unexpected identities. Four grader and four Broadway parser unit tests pass.

The variant is `evaluation_variants/plataformatec__broadway-95--integration-v2.json`.
It pins the existing image, parser/dependencies, test patch, production repair,
compatibility test repair and diagnostic evidence by hash. It uses network
isolation, linux/amd64 and explicit `+JMsingle true`.

Application order:

1. Verify the image checkout's base commit and apply `95-handshake-v2.patch`.
2. Apply the submitted production patch.
3. Apply the upstream test patch and `95-repair-v1.patch`.
4. Run and grade the complete serial test inventory.

The compatibility test repair retains exception type checks and adds test exit
trapping; it does not add warm-up batches. No tracing or readiness workarounds
are present. The handshake is a disclosed production change, not an unchanged
upstream benchmark. Original upstream lists and results remain preserved.

Any future agent must receive this same repaired checkout, plus issue/interface.
This is a requirement for agent integration, not a claim that an agent harness
has already been configured. Candidate conflicts with the repair are setup
failures requiring investigation, not automatically counted as agent failures.

`prepare_broadway_v2.py` regenerates the manifest from verified diagnostic
results. The manifest retains its pre-check candidate status so its hash still
matches the runs; `grader-results-v2.json` records `integration_passed: true`.
No final sample eligibility is implied. The held v1 variant is preserved.

Reproduce (fresh output directory required):

```sh
.harness-venv/bin/python evaluation_variants/prepare_broadway_v2.py
.harness-venv/bin/python findings/broadway-repairs/check_grader_v2.py
```

Raw logs: `validation_runs/broadway-grader-v2/` (ignored). Compact results and
log/result hashes: `findings/broadway-repairs/grader-results-v2.json`.
No paid model calls, commits or pushes.
