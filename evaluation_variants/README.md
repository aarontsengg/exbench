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
