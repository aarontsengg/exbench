# ExBench: goals, log, results, open questions

Working name: **ExBench** (placeholder) Started: 15 Sep 2026

## Goal

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
2. ⬜ **Profile** (`scripts/profile_elixir.py`). The key output is the number of clean OTP tasks after the per-repo cap, which needs to be ≥ 30\. Also pin the dataset revision and language label.  
3. ⬜ **Check the tags by hand.** Read about 20 tasks tagged OTP and about 20 tagged control, confirm the regex tags are right, then adjust `exbench/constructs.py` and re-run step 2 if not.  
4. ⬜ **Sample** (`scripts/sample_v0.py`). Produces 30 matched pairs, then check the balance table.  
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
