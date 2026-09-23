# Tag audit — 20 September 2026

Reviewed all 40 reference patches in the existing seeded audit sample: 20 automatic OTP and 20 automatic control, all exact upstream quality A. The first two existing OTP labels were preserved and given reasons; the remaining 38 were reviewed by the assistant. This is an **AI-assisted semantic audit**, not independent human ground truth. No external model API calls or task execution were performed.

Decisions and per-patch SHA-256 hashes are in [reviews.json](reviews.json). The original file is preserved as `reviews.before_assistant_audit.txt`; its unquoted `otp` value was repaired in the working JSON. The `manual_tag` field name is retained for compatibility; provenance is recorded on every entry.

## Rubric

- **otp:** substantive changes to process interaction, server request handling, supervision, registration, timers, acknowledgement, failure handling or lifecycle. Mixed patches count if at least one such change is substantive.
- **control:** the patch changes application/data/compiler/template logic without substantive process behavior. Merely mentioning OTP, changing formatting/types, or changing ordinary return data inside a server is insufficient.
- **uncertain:** available patch evidence or the scope definition does not support a confident binary decision. Exclude pending adjudication.

These are semantic patch-based judgments, not proof that solving the issue necessarily requires OTP reasoning. The audit does not validate the tests, issue specification, runtime behavior or upstream quality labels. Process-dictionary-only changes are a scope question. No regex rules were changed.

## Initial results (before adjudication)

| Automatic group | Reviewed OTP | Reviewed control | Uncertain | Total |
|---|---:|---:|---:|---:|
| OTP | 15 | 3 | 2 | 20 |
| Control | 1 | 19 | 0 | 20 |
| Total | 16 | 22 | 2 | 40 |

There are 4 definite disagreements among 40 reviewed tasks (10%), plus 2 unresolved (5%). Among the 38 determinate reviews, disagreement is 4/38 (10.5%). If both unresolved cases are disagreements, the sample disagreement proportion is 6/40 (15%). The project's greater-than-20% trigger is not reached, but these results do not establish that the tagger is reliable across the dataset.

The sample deliberately contains equal numbers from unequal automatic groups and excludes borderline/non-A tasks. These proportions are **not a population-wide error-rate estimate**. Review was unblinded to automatic labels; labels are assistant judgments, with no independent reviewer agreement measurement.

### Definite disagreements

- `fika-lang__fika-18`: OTP → control. Tuple/compiler implementation; the supervision call was reformatted without changing behavior.
- `phoenixframework__phoenix-5582`: OTP → control. Generator/form changes with incidental supervision formatting/type references.
- `newrelic__elixir_agent-464`: OTP → control. Host metadata configuration; “Agent” is a product name in prose.
- `commanded__commanded-380`: control → OTP. Process-manager error recovery changes persistence/acknowledgement and callback failure behavior without matching the regex.

### Unresolved scope cases

- `ash-project__ash-1624`: process-dictionary error bookkeeping alongside validation changes. Decide whether process-local storage alone belongs in the treatment definition.
- `commanded__commanded-105`: correlation/causation data propagation with acknowledgement/retry changes. Confirm whether the latter materially change process failure behavior before assignment.

## Verification and next step

Verified 40 unique IDs, populated labels/reasons, exact-A quality, Elixir language, repository identity, patch byte equality against local `train.parquet`, and all recorded patch hashes. The dataset revision and previously verified file hash remain documented in `dataset_config.json` and `PROFILE.md`.

Keep original automatic counts as provisional. Do not assume the cap-four capacity of 32 represents 32 confirmed OTP tasks. Resolve the two scope cases, apply explicit reviewed overrides or refine the tagger, then recompute eligibility and matching capacity. Semantic control reclassifications here do not automatically satisfy the existing stricter no-marker control sampling rule. No sample was selected and no eligibility rules were changed by this audit.


## Adjudication of the two uncertain cases

Both were re-reviewed against the issue description and reference test changes in the local dataset. These remain assistant judgments, not independent human validation.

- **ash-project__ash-1624 → control.** The reported bug and added test concern validation-condition negation. The process dictionary already stores errors; the patch fixes counting and argument passing, not process interaction or ownership. Clarification: process-local bookkeeping alone does not qualify as OTP.
- **commanded__commanded-105 → otp (mixed patch).** Correlation/causation ID propagation is the main feature. Separately, event-handler and process-router acknowledgement helpers change ignored return values to `:ok = ...` matches. A non-`:ok` first return now raises before the second acknowledgement, changing failure behavior. This qualifies under the existing rule that any substantive process-behavior change counts. The main issue/tests concern metadata; this is not evidence that solving the issue requires OTP reasoning. For a future issue-focused benchmark, reconsider eligibility explicitly rather than treating this tag as proof.

Final audit: **17 OTP, 23 control, 0 uncertain**. Automatic OTP sample: 16 OTP / 4 control. Automatic control sample: 1 OTP / 19 control. Definite disagreements: **5/40 (12.5%)**; the sampling and independence limitations above still apply. No original automatic profile totals or sampling rules were changed. Next: incorporate reviewed decisions into eligibility and recompute capacity before selecting tasks.
