# Elixir dataset profile

## Source and verification

- Dataset: nebius/SWE-rebench-V2
- Revision: 475dd5e8703bb5fb22dd3c60b5d038b019eba1e0
- Split: train
- Exact language label: elixir
- Local file size and SHA-256 verified against upstream metadata.
- Required field types checked, including nested quality and difficulty fields.
- No model calls or task execution performed.

## Counts

| Pool | Tasks | Repositories |
|---|---:|---:|
| Full dataset | 32,079 | 3,617 |
| Elixir | 416 | 61 |
| Provisional OTP candidates | 72 | 21 |
| Exact-A OTP candidates | 45 | 15 |

| Provisional tag | All Elixir tasks | Exact-A only |
|---|---:|---:|
| OTP | 72 | 45 |
| Borderline | 21 | 10 |
| Control | 323 | 244 |
| Total | 416 | 299 |

## Classification policy

Tags are based on regex matches in the reference solution patch.

- OTP: a marker appears on an added or removed line.
- Borderline: a marker appears elsewhere in the patch, but not on changed lines.
- Control: no marker appears anywhere in the patch.

The rules include process operations alongside OTP modules and callbacks.
The exact patterns are saved in elixir_profile.json.

Exact-A filtering accepts only the upstream quality code "A".
It excludes compound labels such as "A|B5" and missing annotations.
This is a screening policy, not independent proof of task quality.

## Repository cap

The per-repository cap was increased from 3 to 4 during profiling,
before agent evaluation.

- Cap 3: at most 28 exact-A OTP candidates.
- Cap 4: at most 32 exact-A OTP candidates.

The eventual cap applies across OTP and control groups combined.
These capacities are upper bounds before manual review, matching,
and gold-patch validation. No final sample has been selected.

## Limitations and review findings

- Regex tags can match documentation or unrelated names and miss relevant code.
- Repository names have not been checked for renames or duplicate projects.
- Upstream quality and difficulty annotations are model-generated estimates.
- The reverse-proxy task tallarium__reverse_proxy_plug-186 has quality code B4,
  but its interface text supplies the exception requirement absent from the
  issue statement. Its suitability depends on what the agent is shown.
  No eligibility override was made.
- An AI-assisted audit of 20 exact-A OTP and 20 exact-A control candidates is recorded in [tag_audit/AUDIT.md](tag_audit/AUDIT.md): 5 definite disagreements after adjudication (17 OTP, 23 control, no uncertain cases). No matched sampling or gold-patch validation yet.

## Next milestone

Incorporate reviewed disagreements and the clarified audit rubric into
the eligibility policy, and recompute capacity before matched sampling.
The counts above remain the original automatic profile, not audited totals.
