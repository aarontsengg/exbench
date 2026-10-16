# Phoenix HTML #282 runtime audit

Reviewed 2026-10-14. No new tests were run; inspected existing base/gold logs,
pinned dataset patches, and source in the existing image
`sha256:f08cf4f893f821e4b617b81f57dae080e4f2aa5421511375ed5b55ae0c38ff29`.
Source inspections used disposable containers with networking disabled.

## Task and observed transition

The issue asks `content_tag` to accept string tag names. The reference patch
only changes guards in `lib/phoenix_html/tag.ex`. The test patch only adds
`content_tag("custom-tag", "Hi")` with the expected HTML output.
The existing base run fails `content_tag`; the gold run passes it.

Five other tests fail in both phases. Base: 144 parsed passes and 6 failures.
Gold: 145 parsed passes and 5 failures. Both exit 2. This task therefore still
fails the strict whole-suite gold rule despite the observed target transition.

## Four date tests: fixed fixture falls outside a moving range

`lib/phoenix_html/form.ex:1500` obtains the current year with `:erlang.date()`.
Line 1503 supplies `(year - 5)..(year + 5)` as the default selector range.
The tests use fixed dates in 2020; for example,
`test/phoenix_html/form_test.exs:1049` expects a selected 2020 option.
Recorded output offers 2021 through 2031, consistent with execution in 2026.
2020 is absent, so the assertions fail. Affected tests:

- `date_select/4`
- `date_select/4 with form`
- `datetime_select/4`
- `datetime_select/4 with form`

This explains the recorded mismatch without attributing it to the tag fix.
No system-clock changes or fixture edits were made.

## One template test: missing line metadata

`does not escape safe expressions` evaluates `Safe <%= {:safe, "<value>"} %>`.
`lib/phoenix_html/engine.ex` derives a source line via `line_from_expr/1`,
whose fallback is `nil`, then passes it to `quote line: line` in `to_safe/2`.
The recorded Elixir 1.16.3 stack trace rejects this value at engine.ex:98:
`invalid runtime value for option :line in quote, got: nil`.
This identifies the immediate runtime failure. It does not establish which
historical Elixir release would pass, since none was tested here.

## Disposition and next diagnostic

Keep the original strict result unresolved. Do not silently drop the five tests
or mark the whole task validated. A future repair experiment should apply the
same documented compatibility adjustments to base and gold, preserve the
string-tag assertion, and verify the full suite in both phases. Any repaired
evaluation is a separate version from the unchanged upstream environment.

Evidence: `validation_batch_02_results.json` contains log hashes and counts;
raw logs are under `validation_runs/batch-02/`. No model calls, scoring-policy
changes, or sample edits were made.

## Controlled repair experiment — completed 2026-10-14

Applied `findings/phoenix-html-282-compatibility.patch` identically in fresh base
and gold containers, using the same immutable image as the original run. The
patch fixes the selector's anchor year to 2020 (range 2015..2025) and substitutes
line 0 when template source line metadata is missing. These are production-code
adjustments for this diagnostic, not a proposed general library fix. Neither the
system clock nor the evaluation assertions were changed. The original reference
patch and test patch were applied as before, with `ERL_FLAGS="+JMsingle true"`.

| Phase | Parsed passing IDs | Parsed failures | Exit |
| --- | --- | --- | --- |
| Base + compatibility | 149 | `content_tag` only | 2 |
| Gold + compatibility | 150 | none | 0 |

The same 149 parsed tests pass in both phases; only `content_tag` changes from
fail to pass. Raw gold ExUnit output reports 19 doctests, 151 tests, 0 failures.
Parsed counts differ because the upstream parser does not retain every raw
ExUnit case as a distinct test ID.

The existing strict checker still reports `ok=false` for both phases: the five
previously failing tests now pass but are absent from the upstream expected lists
(1 FAIL_TO_PASS and 144 PASS_TO_PASS). This is an exact-list mismatch, not a
remaining gold test failure. No expectation lists, original validation statuses,
or sample entries were rewritten. The repaired setup demonstrates the intended
transition, but is a separate evaluation variant, not unchanged-upstream validation.

Tracked evidence: `findings/phoenix-html-282-compatibility-result.json` records the
patch hash, image, log hashes, complete parsed results and diagnostic conclusion.
Raw logs: `validation_runs/phoenix-html-282-compatibility/`.

Reproduce with a new output directory:

```sh
.venv/bin/python prepare_validation.py --diagnostic-ids phoenixframework__phoenix_html-282
.harness-venv/bin/python validate_reference.py --input validation_inputs/diagnostic.json --manifest diagnostic_manifest.json --output validation_runs/phoenix-html-282-compatibility-rerun --timeout 300 --erl-flags '+JMsingle true' --shared-setup-patch findings/phoenix-html-282-compatibility.patch
```

No paid model calls. Runner syntax and whitespace checks passed.
