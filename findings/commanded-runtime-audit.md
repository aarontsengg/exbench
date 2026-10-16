# Commanded runtime investigation — 2026-10-15

Inspected existing base/gold logs for all five selected Commanded tasks. No
containers were rerun, and no code, expectations, or eligibility were changed.
Evidence paths and hashes are recorded in `commanded-runtime-audit.json`.

| Task | Gold failed IDs | Confirmed shared failure |
| --- | ---: | --- |
| commanded__commanded-139 | 92 | Phoenix PubSub calls missing `:pg2.create/1` |
| commanded__commanded-171 | 22 | Phoenix PubSub calls missing `:pg2.create/1` |
| commanded__commanded-290 | 28 | Phoenix PubSub calls missing `:pg2.create/1` |
| commanded__commanded-335 | 9 | Phoenix PubSub calls missing `:pg2.create/1` |
| commanded__commanded-380 | 5 | Distributed node startup reports `:nodistribution` and connection refused |

The first four contain actual UndefinedFunctionError crash traces, not merely
compiler warnings. The traces point to Phoenix.PubSub.PG2Server.init/1 in
phoenix_pubsub 1.0.2 (#139/#171), 1.1.1 (#290), and 1.1.2 (#335).
Erlang's official OTP 24 removal notes confirm removal of pg2:
https://www.erlang.org/docs/24/general_info/removed.html

This establishes a runtime/dependency incompatibility affecting all four tasks.
It does not establish that every failed test is caused by it. Gold also reports
other failures, including serialization, application configuration, and aggregate
lifespan behavior. Cascading process shutdown can obscure independent failures.

#380 is a different case: its distributed subscription setup cannot start
`manager@127.0.0.1`; the log reports `Protocol 'inet_tcp': register/listen error:
econnrefused`. Missing/unavailable epmd is a plausible hypothesis, not verified.
Other gold failures remain, so fixing node startup alone would not establish
whole-suite validity.

## Next experiments

For #380, inspect the distributed test setup and epmd availability, then compare
an unchanged baseline with an explicitly recorded epmd-startup adjustment in both
base and gold. Keep remaining failures visible.

For the four pg2 tasks, inspect their historical CI runtime requirements before
choosing a compatible Elixir/Erlang pair and rebuilding dependencies. Test one
representative task first. Do not simply substitute pg for pg2 or implement a
shim: modifying process-group semantics could change the OTP behavior being
measured. A historical-runtime rebuild would be a separate evaluation variant,
with pinned image/runtime/dependencies, not the original upstream environment.

No paid model calls. Original strict validation counts remain unchanged.
