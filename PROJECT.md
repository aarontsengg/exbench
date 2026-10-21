# ExBench: goals, log, results, open questions

Working name: **ExBench** (placeholder) Started: 15 Sep 2026

## Goal

Latest diagnostic (20 Oct 2026): Broadway #95's cancellation test passes in
both base/reference phases at seeds 42 and 7 after a test-only readiness batch.
Base failures are consistently 19; reference passes all 101 checks. This
changes the scenario from immediate shutdown to shutdown after successful
processing, so it remains a diagnostic candidate pending explicit evaluation
contract review. No sample/grader promotion or model calls. See
`findings/broadway-repairs/REPORT.md` for evidence and limitations.

Find out *which parts of Elixir* coding agents struggle with in real codebases, starting with OTP, and publish it as an open evaluation plus write-up. Build in public on Twitter and Substack.

Success bar: a credible, reproducible finding the Elixir community shares and argues about, e.g. "agents handle functional Elixir but break on OTP" (or a clean null result).

## Research questions

**Primary (Part 2): do coding agents fail more often on real Elixir tasks that touch OTP?**

- Why OTP:  
  - Puzzle benchmarks mostly test the functional core (pattern matching, pipes, recursion), where Elixir scores very well.  
  - OTP work (GenServers, supervisors, process lifecycles, message passing) is timing- and lifecycle-dependent, spans files, and is what makes Elixir distinctive in production.  
- **Design:** 30 OTP tasks (treatment) vs 30 non-OTP Elixir tasks (control), matched one-to-one on difficulty and patch-size bucket.  
- Report pass@1 per group and the paired difference with a 95% CI.

**Byproduct (Part 1): how good are agents at repo-level Elixir overall?**

- The control group's pass@1 is the plain-Elixir number.  
- Compare it with SWE-rebench V2's Python/JS/Go/Rust/Scala table.  
- Not a representative "Elixir score", because the sample over-weights OTP by design.  
- Context: AutoCodeBench (function level) puts Elixir on top, with a CyberAgent follow-up reporting 87.4% vs 53.1% Python. Nobody has published repo-level Elixir agent results.

**Later:**

- Other constructs (macros, Ecto, Phoenix/LiveView) using the same matched design.  
- A/B test of runtime tooling (Tidewave-style MCP).

**Statistical power:** 30 vs 30 reliably detects only large gaps (on the order of 40% vs 10%). Detecting a modest gap (25% vs 15%) needs roughly 100+ tasks per group, which is a v1 job.

## Foundation: nebius/SWE-rebench-V2 (Hugging Face)

- 32,079 executable tasks from 3,617 repos across 20 languages, **including Elixir**.  
- Pre-built Docker images (`docker.io/swerebenchv2/*`), CC-BY-4.0; each task carries its repo's licence.  
- **Fields:**  
  - `repo`, `base_commit`, `patch`, `test_patch`, `problem_statement`  
  - `FAIL_TO_PASS`, `PASS_TO_PASS`  
  - `language`, `install_config`  
  - `meta.llm_metadata` (quality code A/B1–B7, difficulty, PR categories)  
- **Elixir support in the paper:**  
  - an Elixir base Dockerfile (elixir:1.16)  
  - an ExUnit log parser (Appendix A.3.5)  
- **Elixir candidates:** 6,621 tasks from 563 repos before environment setup. About 20% of repos survive setup, so the final count is unknown until profiled.  
- **The paper's model study skipped Elixir.** It covered Python, JS, Go, Rust and Scala (60 tasks each, 7 models, mini-SWE-agent, 3 runs).  
  - Opus 4.5 pass@1: Py 36.1, JS 26.7, Rust 28.9, Go 15.0, Scala 19.4.  
- **Limitations:**  
  - Single-container only, which likely under-represents Phoenix/Ecto apps needing Postgres.  
  - Tasks span 2014–2025, so contamination risk is real.  
- **Companion dataset:** nebius/SWE-rebench-V2-PRs has 120k+ lower-confidence tasks with LLM-written problem statements (23% show some leakage). It is a fallback pool if OTP tasks are scarce.

## Prior-work audit

| Work | Elixir? | Level | Status for us |
| :---- | :---- | :---- | :---- |
| SWE-bench / Verified | No | Repo | Python only |
| SWE-bench Multilingual (9 languages) | No | Repo | No BEAM |
| Multi-SWE-bench (7 languages) | No | Repo | No BEAM |
| SWE-PolyBench | No | Repo | No BEAM |
| **SWE-rebench V2 (Nebius)** | **Yes (tasks)** | Repo | Tasks and images exist; no Elixir results; no construct breakdown → build on this |
| Senior SWE-Bench (Snorkel) | Partial | Repo | No Elixir breakdown |
| AutoCodeBench (Tencent) | Yes | Function | The claim to contrast with |
| ash-project/evals | Yes | Snippet | Tiny |
| rizafahmi/evalcode | Yes | Greenfield app | One app, 3 runs |

No one has published construct-level (OTP / macros / Ecto / Phoenix) agent results for Elixir.

## Results so far

- **Senior SWE-Bench re-read (weak evidence, do not publish):** 11 public tasks from Elixir-containing repos average 9.0% solved, vs 11.5% across all 50\.  
- **Scaffold tested with fake data:**  
  - The matched sampler balanced difficulty and size exactly and respected the per-repo cap.  
  - The analysis produces group rates and a paired difference with CI.  
  - The budget guard blocks runs with no cap.

## Build sequence

1. ✅ Prior-work and Hugging Face audit.  
2. ✅ **Profile** (`profile_elixir.py`): verify pinned source, schema and Elixir/quality counts.
3. ✅ **Review tags:** AI-assisted patch audit, with recorded reasons and user-assisted examples.
4. ✅ **Sample** (`profile_elixir.py` → `candidate_pairs.json`): 30 reviewed matched pairs, shared cap five; runtime validation pending.
5. ⬜ **Harness:** wire `exbench/harness.py` to the SWE-rebench V2 harness and mini-swe-agent.  
6. ⬜ **Validate gold patches** (`scripts/validate_gold.py`). Free, no model calls. Replace any task whose gold patch fails by re-sampling.  
7. ⬜ **Run** (`scripts/run_eval.py`). Needs Aaron's model list and budget.  
8. ⬜ **Analyze** (`scripts/analyze.py`), then tag every failure in `analysis/failure_taxonomy.md`.  
9. ⬜ **Write up and publish:** HF subset, results, Substack post, Twitter thread, Elixir Forum. Credit Nebius.  
10. ⬜ **v1:**  
    - more pairs for power  
    - other constructs  
    - fresh post-cutoff tasks via the open pipeline  
    - Postgres support for Phoenix/Ecto apps  
    - tooling A/B

## Decisions made

- Build on SWE-rebench V2 instead of mining from scratch.  
- **Part 2 (OTP) is the main question.** Part 1 comes free from the control group.  
- Use a matched design (difficulty × patch size), with at most 3 tasks per repo across both groups.  
- **Construct tags come from regex heuristics on the patch.**  
  - Treatment \= OTP marker on a changed line.  
  - Control \= no OTP marker anywhere in the patch.  
  - Borderline tasks are excluded from both groups.  
- Match the paper's protocol (mini-swe-agent, 3 runs) so numbers are comparable.  
- Use public repos only. Nothing from Whatnot.

## Kill criteria

- **Too few OTP tasks:** fewer than 30 matched pairs. Then either widen to the V2-PRs pool or collect fresh tasks from OTP-heavy repos with the open pipeline (a fork, ask Aaron).  
- **Tags unreliable:** if more than 20% of hand-checked tags are wrong, fix the tagger before sampling.  
- **Scooped:** if construct-level Elixir results appear, pivot to other constructs, fresh tasks, or the tooling A/B.  
- **Cost:** a hard cap per run in `configs/v0.yaml` (decision pending with Aaron).

## Open questions

- How many clean OTP tasks exist? (Step 2 answers this.)  
- **Exact Elixir label and dataset revision.** The sandbox can't reach huggingface.co; run locally or allow the domain.  
- Should `send(` and `Task.async` count as OTP? Currently `send(` does and `Task.*` doesn't, except `Task.Supervisor`. Revisit after the hand check.  
- Budget per run? Which models?  
- Contamination cutoff for v1.  
- Does the elixir:1.16 base image break newer repos?  
- Name.

## Log

- **20 Oct 2026 — Broadway #40/#95 diagnostic repairs:** Replaced unspecified error-message suffix checks with exception-type checks and repaired #95 shutdown test exit handling, retaining message assertions. #95 reference passes 100 tests plus one doctest at seeds 42/7; its baseline has a specified missing API outside the upstream failure list and a variable cancellation failure. #40 reference passes seed 42 but has a batch-message mismatch at seed 7, plus a task-scope concern. Neither promoted to scoring. See [report](findings/broadway-repairs/REPORT.md). No model calls.

- **20 Oct 2026 — Cachex #341 timing review:** Original hook-duration assertion exceeded its 35 ms upper bound by 0.746 ms. Two unchanged reference reruns on the same image pass all 200 qualified tests (seeds 42/7); both baseline runs cannot compile the explicitly requested warmer `name` field. Retain the original intermittent failure and a reliability caveat; no timeout relaxation, automatic inclusion, or status rewrite. See [report](findings/cachex-341/REPORT.md). No model calls.

- **20 Oct 2026 — Cachex grader integration:** Added separately versioned #292/#294 manifests and repository-directory/parser-dependency support to the shared grader. At seed 42, empty submissions are rejected and reference submissions pass all 194/195 tests. #294 uses a required passing inventory without claiming observed individual baseline failures. Seven grader/adapter unit tests pass. See [integration report](findings/cachex-cluster/GRADER_INTEGRATION.md). No model calls or sample changes. Commit checkpoint before remaining task eligibility work.

- **20 Oct 2026 — Cachex historical comparison:** Elixir 1.13.4 / OTP 24 with recorded emulation workaround and unchanged copied dependencies yields #292 base one intended failure / gold 194 passes, and #294 base missing-API compilation failure / gold 195 passes, each at seeds 42 and 7. Qualified parser recovers six identities merged by the upstream name-only parser. See [historical report](findings/cachex-cluster/HISTORICAL.md). No assertion changes, model calls, automatic sample inclusion, or original-status rewrites. Next: versioned Cachex grader integration. Suitable commit checkpoint.

- **19 Oct 2026 — Cachex cluster diagnostic:** Reran #292/#294 with epmd started in both phases and verified unchanged image IDs. Cluster-startup errors disappeared. Reference #292 still fails memory-size and TTL assertions; #294 fails the memory-size assertion and its base cannot compile the requested `async` warmer API. Raw totals exceed upstream parsed-name counts by six in both suites. See [report](findings/cachex-cluster/REPORT.md). No sample/policy changes or model calls.

- **19 Oct 2026 — Commanded grader repairs verified:** All five selected Commanded tasks (#139, #171, #290, #335, #380) now reproduce their recorded base failures and pass every reference test at seeds 42 and 7 in the versioned local grader. Repairs address test isolation, asynchronous setup/reset races, module-qualified test identity, and three unspecified literal-message assertions in #139. No production fixes were injected into the base controls. See [repair report](findings/grader/COMMANDED_REPAIRS.md) and [verified summary](findings/grader/commanded-integration-summary.json). The earlier one-off #171 deposit timeout remains causally unresolved. Original validation totals and final sample membership are unchanged; no model calls, commits, or pushes. This is a commit checkpoint before broader harness/eligibility work.

- **20 Sep 2026:** Completed an AI-assisted patch audit of the existing 40-task sample (20 exact-A automatic OTP, 20 control). Preserved the first two user labels and reviewed the remaining 38. Results: 16 OTP, 22 control, 2 uncertain; 4 definite disagreements with the automatic tags. See [tag_audit/AUDIT.md](tag_audit/AUDIT.md). This is not independent human validation. Resolve uncertainty and recompute eligibility before sampling; automatic capacity 32 remains provisional. No paid model calls or task execution.

- **15 Sep 2026 (a):** Dropped Kalshi. Chose an Elixir coding-agent benchmark. Web audit found no repo-level Elixir benchmark.

- **15 Sep 2026 (b):** Hugging Face audit found SWE-rebench V2, which has Elixir tasks but no Elixir results. Plan: build on it.

- **15 Sep 2026 (c):** Scaffolded the repo (configs, split, step scripts, budget-capped runner, harness stubs).

- **16 Sep 2026:** Made Part 2 (OTP) the primary question. Added:

  - construct tagging (`exbench/constructs.py`: OTP, macros, Ecto, Phoenix; strict and loose levels)  
  - a matched OTP-vs-control sampler that reserves treatment slots under the repo cap  
  - group and paired-difference analysis  
  - construct counts in the profile report

  Tested all of it with fake data. **Next: run step 2\.**

## Development Notes
- Raised the per-repository cap from 3 to 4 during dataset profiling, before agent evaluation. Under the current tagging rules, this increases exact-A OTP capacity from 28 to 32. The cap applies across treatment and control groups combined.

Before model evaluation, raised the shared repository cap from four to five. Reviewed-label matching permits 29 pairs under cap four and 32 under cap five. We chose five to support the planned 30-pair study, accepting greater repository concentration. Feasibility remains provisional pending control review and reference-patch validation.

---

## Claude Code kickoff brief (paste into a long-running session)

> Read `CLAUDE.md` and this file. Continue the build sequence from the first unchecked step, updating Log, Results and Open questions as you go.

> - For step 3, print 20 OTP-tagged and 20 control patches (changed lines only), judge each tag, and record the error rate in Results.  
> - For step 5, read `third_party/swe-rebench-v2` docs before writing any code, and reuse their grader.  
> - Do not run paid model calls. Stop at any fork listed in `CLAUDE.md`.


&nbsp;

- **Audit follow-up:** Resolved the two uncertain entries: ash-project__ash-1624 is control (process-local error bookkeeping); commanded__commanded-105 is OTP under the mixed-patch rule (stricter acknowledgement failure handling), though its main feature is ID propagation. Final audit: 17 OTP / 23 control, 5/40 disagreements. See tag_audit/AUDIT.md for scope and limitations.

- **2 Oct 2026:** Merged verified alias slashdotdash/commanded into commanded/commanded for repository caps, preserving source names and IDs. Corrected feasibility: cap four = 27 pairs; cap five = 30. Archived the invalid earlier sample in sample_history/ and regenerated 30 draft pairs. Checked 60 unique tasks, within-bucket matches and shared cap; Commanded contributes five. Other repository transfers/forks still need verification. Selected controls needing review: 28. No paid model calls or runtime evaluation.

- **5 Oct 2026:** Completed current GitHub identity checks for all 61 Elixir repository names: 60 IDs, with Commanded the sole duplicated ID. Saved sample respects cap five by current ID. Finch is now a fork and needs historical base-commit/PR lineage verification. See repository_audit/REPORT.md. No new cap collision or resampling required; control review remains next.

- **5 Oct 2026 — sample review completed:** Saved 28 selected-control decisions (7 user-assisted, 21 assistant static reviews). All 60 selected tasks now have reviewed labels. Replaced JavaScript-focused phoenixframework__phoenix-4309 with already-reviewed ash-project__ash-1853 in the same medium/large bucket; other 29 pairs preserved. Exclusion is separate from its control label. Validated pinned dataset, unique IDs, exact-A eligibility, group labels, review hashes where recorded, matching buckets and shared canonical-repository cap five. See tag_audit/selected_controls/REPORT.md and candidate_pairs.json. No runtime tests or paid model calls. Next: resolve Finch historical lineage and integrate the upstream harness to validate base/reference patches before any agent evaluation.

- **5 Oct 2026 — runtime preparation:** Verified Finch PR/base lineage (original repository ID 217153245). Pinned official V2 evaluator/parser at c71902a8cf8d2b725f63d51f199f4d3e56f68d2d with file hashes and MIT license. Added prepare_validation.py for pinned local 60-task export and two-task smoke inputs. Existing Python 3.9 cannot import upstream evaluator; created separate Python 3.12 .harness-venv and verified evaluator help. Docker absent, so no container tests run. Base-vs-gold validation, image architecture/digest checks and agent integration still pending.

- **12 Oct 2026 — first runtime results:** Initial unmodified amd64-on-arm64 smoke run had Phoenix compile timeouts and Protobuf dependency compiler errors. Recorded diagnostic override ERL_FLAGS="+JMsingle true" removed those symptoms. Protobuf #387 validated: base 5 failures/476 passing parsed tests, gold 481 passing/0 failures, about 60 seconds combined. Phoenix #2974 remains invalid in this environment: EEx.Engine incompatibility in both phases and its sole FAIL_TO_PASS test already passes on base. No task excluded or replaced yet; 58 tasks remain untested. See SMOKE_RESULTS.md and smoke_results.json. No paid model calls.

- **Phoenix scoring quarantine:** Reference patch includes the actual no-schema fallback fix plus unrelated OTP changes, but the designated failing test passes on base and does not establish issue resolution. User agreed to remove from scoring. Added exclusion, marked saved draft blocked and guarded exports. Recomputed capacity: 29 matched pairs at shared cap five (26 at cap four). Preserve study rules pending a design decision; continue runtime review before choosing final sample size.

- **12 Oct 2026 — second diagnostic batch:** Absinthe #1336 validated; Phoenix HTML #282 has the expected target transition but five persistent suite failures (date selection and EEx compatibility). Saved validation_batch_02_results.json. Added explicit subset exports to continue validation without finalizing the blocked draft. Drafted an X post and upstream issue report under findings/; neither published.

- **14 Oct 2026 — full first validation pass completed:** All 60 draft tasks attempted across three batches. 23 pass strict base/gold checks (8 OTP, 15 control); 36 need investigation; Phoenix #2974 remains quarantined. 28 gold runs pass strict checks, including 5 with unresolved base compilation behavior. Separately, 47 match the official evaluator passing-test list; 19 of these still have failed tests/nonzero exit and fail our stricter gold rule. These are validation criteria differences, not agent scores. Only 4 original pairs have both members strictly validated. Total recorded test-phase wall time ~37.1 minutes excluding pulls. Reports: VALIDATION_RESULTS.md, validation_summary.json, findings/validation-triage.md. No paid model calls; no new exclusions, cap changes, or expectation rewrites. Next: settle/document baseline compilation handling and upstream-vs-strict grading, then investigate runtime compatibility/distributed-node setup on native amd64.


Broadway #95 integration update (20 Oct 2026): a separately versioned readiness
repair is documented, but actual grader integration remains on hold. Empty
patches have 19 failures in both orders; reference seed 42 misses an
acknowledgement in the separate no-batcher shutdown test, while seed 7 passes
101 checks. No final selection or paid calls. See
`findings/broadway-repairs/REPORT.md` and `grader-results-v1.json`.


20 Oct 2026, Broadway #95 follow-up: a diagnostic no-batcher readiness check
passes its target, but the seed-42 reference now fails incomplete-batch shutdown;
seed 7 passes. Preserve the hold for broader shutdown variability. Additional
repair remains diagnostic only. See findings/broadway-repairs/REPORT.md.

20 Oct 2026, Broadway #95 trace: captured an incomplete-batch failure where the
terminator exits without sending drain instructions. Source sends an async
trap-exit request immediately before supervisor shutdown, with no completion
handshake. Strong evidence of a production shutdown race; readiness patches
are not a demonstrated root-cause fix. #95 stays on hold. See the Broadway
report and trace-analysis-v3.json. No production fix or paid calls.

20 Oct 2026, Broadway shutdown fix: synchronous terminator readiness handshake
plus already-dead supervisor handling passes the reference's 101 checks at
seeds 42, 7 and 123 without readiness warm-ups. Base retains identical 19
failures. Focused regression fails before/passes after. Saved as a separately
versioned production diagnostic, findings/broadway-repairs/95-handshake-v2.patch.
Old grader manifest remains on hold pending a new integration version. No paid calls.

20 Oct 2026, Broadway #95 grader v2 verified: applies a hashed production shutdown
repair before candidate patches, without readiness workarounds. Empty fixes
have exactly 19 failures and reference fixes pass 101 checks at seeds 42 and 7.
Eight grader/parser unit tests pass. Future agent checkout must include the same
repair. No final sample promotion, paid calls, commits or pushes. See
findings/broadway-repairs/GRADER_V2.md. This is a progress-commit checkpoint.
