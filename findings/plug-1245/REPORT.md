# Plug #1245 scope audit — 19 October 2026

Decision: **keep on hold for scoring**. This is a static review of the pinned
task and existing logs, not a new runtime check or sample exclusion.

## What the task asks for

The issue asks `Plug.Router` to accept a local function in `match ..., to: :foo`
instead of treating `:foo` as a module and invoking `:foo.init/1`.
The reference router change implements that distinction. The test patch adds
`matches to a function plug` and `matches to a function plug with options`,
checking both the response and supplied options/private data. Those checks
directly address the issue.

## Correction to the earlier audit

The supplemental interface explicitly documents `Plug.Conn.get_cookies/1`,
`Plug.Conn.get_resp_cookies/1`, and the test adapter's connection builder.
Therefore the missing cookie accessor that blocks baseline compilation is
specified under our issue-plus-interface protocol. It is unrelated to routing,
but it is not an unstated requirement. A router-only implementation would not
meet the entire supplied specification.

This resolves the missing-API naming concern, but not the full task's eligibility.
We do not add it to the reviewed compilation-failure category yet.

## Remaining mismatch

The test patch also adds `Plug.SSL.configure/1` requirements, notably support for
`:certs_keys` and relative certificate paths inside that option. The reference
patch adds `normalize_certs_keys_ssl_files/1` and changes missing-key validation
to accept `:certs_keys`. Neither the issue nor the complete supplemental interface
specifies this SSL behavior.

These are additional implementation requirements, not merely assertions that
existing behavior stays working. For example, the added SSL test expects
`configure([:inet6, certs_keys: [%{key: "abcdef", cert: "ghijkl"}]])` to succeed;
the old validation shown in the reference diff requires top-level key and cert
options instead. This is source-level evidence, not a newly observed test run.

The upstream partition lists 517 FAIL_TO_PASS and 37 PASS_TO_PASS names. Baseline
compilation prevents observing those individual transitions. The existing gold
suite passes, which alone does not resolve the specification mismatch.

## Consequence

Do not treat the original task as ready for agent scoring. A future repair must
explicitly settle task scope and verify original/reference behavior; silently
dropping SSL tests or adding their implementation to baseline would change the
evaluation. No tests, production code, policy category, or sample membership
were changed by this audit.

`scope-audit.json` contains the complete supplied issue/interface, relevant
router/SSL diff excerpts, full patch hashes, and original log hashes. No model
calls or containers were run.
