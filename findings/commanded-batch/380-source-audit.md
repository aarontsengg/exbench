# Commanded #380 remaining failures — source audit

Reviewed pinned base commit `4a6df4a3fc3e318805574ca9cab5cef0a83617e3`
and the reference patch on 2026-10-15. Source downloads and hashes are in
`380-detail-sources.json`; files are under `commanded__commanded-380/`.
No additional test run or code repair was performed in this review.

## 1. Aggregate lifespan: invalid callback return in unchanged code

`aggregate_lifespan_timeout/3` converts `:stop` into `{:stop, :normal}`.
The command handler stores it in `state.lifespan_timeout`. Snapshot handling
correctly recognizes this stop tuple. However, `handle_info({:events, events},
state)` reads that same field and unconditionally returns
`{:noreply, state, lifespan_timeout}` (aggregate.ex:278–291).

With the stop tuple, this becomes `{:noreply, state, {:stop, :normal}}`:
exactly the invalid return recorded in the failed run. Stop must instead be a
callback return such as `{:stop, reason, state}`, not a timeout value.
See https://www.erlang.org/docs/26/man/gen_server.html .

The relevant test dispatches an event with lifespan `:stop`, then expects normal
termination and a saved snapshot. The observed crash is consistent with an event
being handled while the stored lifespan is a stop tuple. Precise scheduling has
not been instrumented, and historical-runtime behavior has not been tested.

The reference patch changes only process_manager_instance.ex; it leaves this
aggregate handler unchanged. Thus this is a separate pre-existing code defect
exposed by our run, not simply a missing API or proof the reference task's fix
is wrong. Repairing it would change OTP lifecycle behavior and needs a distinct,
reviewed evaluation variant. Do not silently patch it to obtain a green suite.

## 2. Subscription order: assertion assumes ordering of an ETS set

`Commanded.Subscriptions.all/1` delegates to the registry, which returns
`:ets.tab2list()` from a table created with `:set`. Its documentation says only
"Get all registered subscriptions"; it does not promise sorting. The failure
shows the same two `{name, pid}` entries in opposite order.

This supports treating the assertion's ordering requirement as unjustified by
the inspected implementation/contract. A proposed diagnostic test repair would
compare sorted lists (preserving duplicates), not remove the test. Not applied.
Registry source was fetched separately from the same pinned commit, saved as
`commanded__commanded-380/lib/commanded/subscriptions_registry.ex`.

## 3. JSON order: exact serialization text asserted

json_decoder_test.exs:28 compares serialized JSON to a fixed string. The recorded
output and expected text contain the same name and datetime values, with reversed
key order. A diagnostic semantic comparison could decode both objects before
comparing, while preserving the separate decoding tests. No repair applied.

## 4. Application startup: exact cause remains unverified

application_test.exs:64 enables exit trapping, calls
`UnconfiguredApplication.start_link()` without checking its return, then expects
an EXIT message containing an ArgumentError. The recorded mailbox is empty.
Application.Supervisor.start_link delegates to Supervisor.start_link; its init
path builds the event-store configuration.

We still need to capture both the startup return value and mailbox to determine
whether this is an error-return-versus-exit-message assumption. The source and
empty-mailbox log alone do not establish that cause. Do not remove or weaken the
assertion before that probe.

## Outcome

The epmd repair remains demonstrated separately. Of the remaining four failures,
two concern ordering assumptions, one has a concrete invalid callback path, and
one requires a focused startup probe. Original validation status remains
unresolved. No model calls or changes to sample membership.

## Startup diagnostic completed — 2026-10-15

Reran base and gold with epmd enabled and a shared test-only diagnostic patch
that prints `UnconfiguredApplication.start_link()`'s return. The existing EXIT
assertion was retained without alteration. Both phases returned:

```elixir
{:error, {%ArgumentError{
  message: "missing :event_store config for application Commanded.UnconfiguredApplication"
}, stacktrace}}
```

Both still failed the expected EXIT-message assertion. Thus the application
rejects the missing configuration with the expected error, but the test expects
an additional message not received in this runtime. OTP 26's official
`gen_server:start_link` documentation states that when startup returns an error,
the process has terminated and any linked EXIT message has been consumed:
https://www.erlang.org/docs/26/man/gen_server.html#start_link-3

The observed failure is consistent with that documented startup contract. No
older-runtime comparison was performed, so this is not a claim to have measured
the exact historical behavior. A future compatibility variant could assert the
returned error and exact message rather than wait for an EXIT message.

Evidence: `380-startup-probe.patch`, `380-startup-result.json` (logs hashed), and
raw logs under `validation_runs/commanded-380-startup-probe/`. No scoring or
eligibility changes, no production-code edits, and no model calls.

## Assertion compatibility experiment — 2026-10-15

Applied `380-assertion-compatibility.patch` equally to base and gold, with epmd
startup and the same immutable image/runtime override. It changes only tests:
JSON is decoded before comparison, subscription lists are sorted before exact
comparison, and startup's returned error is checked with the same error type and
message. The lifecycle test and all production code were left unchanged apart
from the original reference fix in gold.

All three adjusted assertions passed in both phases. Gold now has 348 passing
parsed IDs and one failure: `aggregate lifespan should adhere to aggregate
lifespan after taking snapshot`. Base has 346 passing IDs and three failures:

- The same snapshot/lifespan failure.
- The intended process-manager error-callback failure.
- `aggregate lifespan should reopen the aggregate to execute command if it is
  stopped by the previous command`: a task expected success but received
  `{:error, :aggregate_execution_failed}`. This was not present in the previous
  base run and remains unexplained; scheduling dependence is a hypothesis, not
  a verified flakiness rate.

Both phases exit 2. The experiment supports the three assertion diagnoses but
does not establish a clean or stable evaluation variant. Do not add this task
to a validated sample. Remaining lifecycle behavior requires investigation;
changing it would be a production-code repair beyond these test adjustments.

Evidence: `380-assertion-compatibility-result.json` includes full parsed outcomes,
image identity and log hashes; raw logs are under
`validation_runs/commanded-380-assertion-compatibility/`.
No original expectation lists, sample entries, or strict summary counts changed.
