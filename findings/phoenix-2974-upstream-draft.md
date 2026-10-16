# Draft: Phoenix 2974 issue/test alignment and local reproduction concerns

Not submitted. Dataset nebius/SWE-rebench-V2, revision 475dd5e8703bb5fb22dd3c60b5d038b019eba1e0.
Instance phoenixframework__phoenix-2974; base ed584eeacf061acda6e3432c67c8cc4c6d52636c.

The issue concerns Ecto-dependent FallbackController generation with schema generation disabled. The reference patch includes a relevant guard on schema.generate? in priv/templates/phx.gen.json/fallback_controller.ex, alongside unrelated changes. The test patch changes context alias assertions, config cleanup assertions and origin logging. FAIL_TO_PASS contains only `to_param for binaries`; PASS_TO_PASS is empty.

In our local base and gold runs, the designated test passes on base. Both suites also fail with `unexpected EEx.Engine state: {:safe, ""}` in test/phoenix/view_test.exs. We therefore cannot validate this task as supplied in our environment. We have not established the dataset-construction cause.

Environment: Apple silicon, Docker Desktop, linux/amd64 image under emulation. ERL_FLAGS=+JMsingle true is an explicitly recorded diagnostic override. Initial runs without this override stalled during compilation. Image digest and summary in smoke_results.json; official evaluator/parser revision c71902a8cf8d2b725f63d51f199f4d3e56f68d2d. Native amd64 reproduction remains outstanding.

Before submitting: attach minimal standalone reproduction commands and relevant log excerpts, verify the test identity directly, and preferably reproduce on native amd64. Ask maintainers whether the designated tests/patch association can be checked. Keep runtime compatibility separate from the alignment concern.
