# Base compilation audit

Reviewed 2026-10-14 using the pinned rows in `validation_inputs/tasks.json`
and existing `validation_runs/remaining-56/<instance_id>.{base,gold}.log`.
This is a static causal review of recorded runs; no new container runs or model calls.
All five gold runs pass the existing strict gold checks. None establishes the
recorded individual FAIL_TO_PASS transitions because base compilation stops first.
Original validation statuses, sample membership, and grading rules are unchanged.

## elixir-plug__plug-1245 — unrelated changes block the baseline

- Issue: a router match using a functional plug (`to: :foo`) incorrectly calls `:foo.init/1`.
- Base: `test/plug/session_test.exs` cannot compile because `get_resp_cookies/1` is undefined.
- Test patch migrates many cookie assertions to `get_resp_cookies/1` and `get_cookies/1`.
- Reference patch adds those accessors in `lib/plug/conn.ex`, alongside the router fix and other changes.
- Interpretation: the observed baseline failure is not a reproduction of the reported router bug. A correct router-only fix could still fail these unrelated requirements.
- Recommendation: hold out of scoring pending an issue-to-test scope audit. Do not automatically accept it merely because gold passes; no new exclusion has been applied.

## derekkraan__curl_req-53 — test support configuration crosses patch boundaries

- Issue: `from_curl/1` builds a request without the options registered by `Req.new/0`.
- Base: `use CurlReq.Case` cannot compile because that module is not loaded.
- Test patch introduces `test/case.ex` and `test/assertions.ex` and changes the tests to use them.
- Reference `mix.exs` separately adds `elixirc_paths: elixirc_paths(Mix.env())`, with test paths `["lib", "test"]`.
- Interpretation: test-helper compilation configuration needed by the test patch is carried in the reference patch. The observed failure does not yet exercise request options.
- Next diagnostic: apply only this test compilation configuration to the base, leave production code unchanged, and rerun. Record it as an explicit evaluation adaptation, separately from the original result. This rerun has not been performed.

### CurlReq diagnostic completed

Applied only the reference patch's `mix.exs` section to base, followed by the original test patch. Production files were unchanged. Gold used the original full reference and test patches. Used the same immutable image as the first run and the existing explicit `ERL_FLAGS="+JMsingle true"` override.

- Base now compiles: 79 parsed tests pass, 1 fails, exit 2. All 40 doctests also pass.
- Gold: 80 parsed tests pass, no failures, exit 0; all 40 doctests also pass.
- The only failing test is `from_curl redirect and compression is false by default`; execution fails at `assert_redirect(false)` with `Expected redirect set to false`.
- Upstream records 80 FAIL_TO_PASS and zero PASS_TO_PASS. After isolating test setup, 79 of those expected failures already pass. The strict original partition therefore still does not validate.
- This demonstrates a real default-behavior difference, but does not establish coverage of the issue's `Req.merge(receive_timeout: 15_000)` registration failure. Do not promote the task into the validated sample or rewrite its expectations automatically.

Evidence: `findings/curl-req-53-test-setup.patch` and `findings/curl-req-53-diagnostic.json` (image identity, patch/report/log hashes, parsed results). Raw logs remain under ignored `validation_runs/curl-req-53-setup/`. No paid model calls. The downloaded image was released after the run.

Reproduce after preparing a one-task diagnostic export:

```sh
.venv/bin/python prepare_validation.py --diagnostic-ids derekkraan__curl_req-53
.harness-venv/bin/python validate_reference.py --input validation_inputs/diagnostic.json --manifest diagnostic_manifest.json --output validation_runs/curl-req-53-setup-rerun --timeout 300 --erl-flags '+JMsingle true' --base-setup-patch findings/curl-req-53-test-setup.patch --pull-missing --release-pulled-images
```

## general-cbic__poolex-59 — tests depend on a new internal representation

- Issue: distinguish checkout timeout from a timeout raised inside a worker operation.
- Base: `test/support/some_waiting_callers_impl.ex` cannot expand the missing `Poolex.Caller` struct.
- Reference patch creates `lib/poolex/caller.ex`; test support now pattern-matches `%Poolex.Caller{from: {pid, _tag}}` instead of the old representation.
- Test patch also checks `{:error, :checkout_timeout}`, `Poolex.CheckoutTimeoutError`, and a separately wrapped worker runtime timeout. Those assertions are relevant to the issue.
- Interpretation: relevant behavioral tests exist, but compilation is coupled to the reference implementation's new struct. Missing struct alone does not prove the behavioral bug was reproduced.
- Recommendation: keep pending; determine whether the supplied agent interface explicitly requires that representation before accepting the task under a compilation-failure policy.

## plataformatec__broadway-31 — expected missing API

- Issue explicitly requests the producers/processors/batchers API revision, replacing publishers.
- Base: the test's Forwarder cannot compile calls to `put_batcher/2`.
- Reference patch renames `Broadway.Message.put_publisher/2` to `put_batcher/2`; tests use the new name and updated batcher configuration.
- Interpretation: the compilation failure is directly consistent with testing an API that the task asks to introduce.
- Recommendation: eligible for consideration under a documented expected-compilation-failure category. Do not claim that all 80 recorded FAIL_TO_PASS tests were individually observed failing.

## whitfin__cachex-343 — expected API change, naming caveat

- Issue asks to configure warmer startup blocking per cache and explicitly anticipates a breaking change; proposed names are marked work in progress.
- Base: `test/cachex/warmer_test.exs` fails because record `:warmer` lacks key `:required`.
- Reference patch replaces the warmer record's `async` option with `required`; tests use `required: false` for nonblocking startup and both values in hook tests.
- Interpretation: compilation failure is consistent with the requested configuration change. However, the exact `required` record API is more specific than the issue's tentative design.
- Recommendation: candidate for expected-compilation-failure handling, conditional on checking the agent-visible interface supplies the required API. Do not equate a missing record field with independently observed behavioral failures.

## Supplemental interface review — 2026-10-14

Read the pinned dataset's `interface` field for Poolex #59 and Cachex #343. Saved source text and SHA-256 hashes in `findings/base-compilation-interfaces.json` (also includes Broadway #31 for follow-up).

- Poolex explicitly specifies `Poolex.Caller` in `lib/poolex/caller.ex`, with `from :: GenServer.from()` and `reference :: reference()`, replacing the old plain tuple. It also specifies `Poolex.CheckoutTimeoutError` and the new timeout return values. This resolves the concern that the required struct is entirely unstated, provided this interface text is included in the agent prompt.
- Cachex explicitly specifies `Cachex.Spec.warmer(... required: boolean \\ true ...)`, states that `required` replaces `async`, and explains startup blocking. This resolves the naming ambiguity in the issue, subject to the same prompt condition.
- Both are now plausible expected-missing-API compilation failures, alongside Broadway. This is an explanatory finding, not promotion to strict baseline validation. Individual FAIL_TO_PASS transitions remain unobserved.
- The agent runner is not yet integrated. We have not verified an actual agent prompt includes these fields. Before evaluating agents, explicitly choose and record whether to supply `problem_statement` plus `interface`, consistently across both groups. These supplemental specifications are more informative than the issue alone; describe that protocol in the write-up. Never include `patch` or `test_patch` in the agent prompt.

No containers, model calls, sample changes, or grading changes were made in this interface review.

## Policy consequence

Keep three claims distinct: gold passes; base cannot compile; specific expected tests demonstrably fail before the fix and pass after it. Only the first two are established here. Accepting expected missing-API compilation failures would be a new, explicitly documented eligibility category, not a retroactive assertion that strict baseline validation passed. Before running agents, apply any adopted policy consistently to both OTP and control tasks.

## CurlReq direct issue reproduction — 2026-10-14

Ran `findings/curl-req-53-probe/check.exs` against fresh base and gold containers using the same image ID as the previous diagnostic. Neither phase applied the benchmark test patch or test-helper setup overlay. Used `MIX_ENV=dev mix run`, with the recorded single-map JIT override. Networking was disabled; no HTTP request was sent.

| Observation | Original code | Reference-fixed code |
| --- | --- | --- |
| `:receive_timeout` registered | false | true |
| `Req.merge(request, receive_timeout: 15_000)` | ArgumentError: unknown option :receive_timeout | succeeds; option value 15000 |
| Probe exit | 3 (caught ArgumentError) | 0 |

This reproduces the stated bug and confirms the reference fix handles this example. It does not repair the upstream test partition or establish that the supplied benchmark tests detect the bug. Our focused check is a newly authored diagnostic, not an upstream test, and is not added to scoring. Original validation counts and sample membership remain unchanged.

Reproduction: `.harness-venv/bin/python findings/curl-req-53-probe/run.py` (requires prepared local task export and Docker; refuses an existing output directory). Tracked evidence: `findings/curl-req-53-probe/result.json`, including image identity, patch/probe/log hashes and exact result markers. Raw logs: `validation_runs/curl-req-53-issue-probe/`. No paid model calls.
