# Targeted review of eight borderline tasks

AI-assisted review of reference patches and issue descriptions from the local pinned dataset. Only the eight requested tasks were reviewed. No task execution or paid model API calls. These targeted cases must not be folded into the random 40-task audit error rate. Original reviews.json and profiling code are unchanged; this report does not automatically apply overrides.

Rule: substantive process communication, lifecycle, identity, timing or failure behavior qualifies. Ordinary data/configuration changes within process-hosting modules do not automatically qualify.

## plataformatec__broadway-31: otp

Named processor configuration changes the generated process identity from Processor to Processor_#{key}, feeds demand settings into stage initialization, and passes processor_key into handle_message/3. This is a pipeline startup/identity and stage-callback contract change, beyond the publisher-to-batcher renaming.

Evidence: [plataformatec__broadway-31.patch, line 495](plataformatec__broadway-31.patch)

```elixir
process_name(broadway_name, "Processor_#{key}", index)
```

## elixir-protobuf__protobuf-164: otp

Adds Application.stop/1 cleanup that erases extension entries from persistent_term. Without cleanup, starting the application again encounters existing entries and raises. This directly fixes application stop/restart lifecycle; the unchanged Supervisor call is only contextual evidence.

Evidence: [elixir-protobuf__protobuf-164.patch, line 27](elixir-protobuf__protobuf-164.patch)

```elixir
def stop(_state)
```

## livebook-dev__kino-33: control

Adds struct support, Map.get access and underscore-column filtering. DynamicSupervisor.start_child and Process.monitor remain unchanged context; the added state flag controls presentation, not supervision or monitoring.

Evidence: [livebook-dev__kino-33.patch, line 83](livebook-dev__kino-33.patch)

```elixir
else: Enum.reject(columns, &underscored?(&1.key))
```

## plataformatec__broadway-95: otp

Adds batch_mode :flush to test messages and a batch delivery branch that flushes before the size threshold or timeout, cancels the timer and delivers the batch. Changes when downstream processing and acknowledgements occur, fixing missing timely test acknowledgements.

Evidence: [plataformatec__broadway-95.patch, line 96](plataformatec__broadway-95.patch)

```elixir
defp deliver_or_update_batch(batch_key, current, _pending_count, true
```

## quantum-elixir__quantum-core-454: otp

Replacing an active job now emits a delete event for the old job before adding the replacement, rather than only updating the map and emitting add. Active-to-inactive replacement also emits delete. These GenStage events coordinate scheduler state and prevent old schedules continuing to execute.

Evidence: [quantum-elixir__quantum-core-454.patch, line 45](quantum-elixir__quantum-core-454.patch)

```elixir
{:noreply, [{:delete, old_job}, {:add, job}]
```

## absinthe-graphql__absinthe-944: uncertain

The issue is enum-default validation, and most changes are schema logic. A separate hunk removes [module]-to-module normalization before Supervisor.start_link. That changes the initialization argument for list-form callers, but the patch alone does not establish whether this is a substantive supported lifecycle change or obsolete compatibility cleanup. Exclude pending inspection of the base initializer/callers; do not promote just because the file is a supervisor.

Evidence: [absinthe-graphql__absinthe-944.patch, line 148](absinthe-graphql__absinthe-944.patch)

```elixir
case pubsub do
```

## livebook-dev__kino-231: otp

Adds a Livebook-specific io_request to detect whether the caller group leader supports the Livebook protocol, then chooses Kino debugging or Macro.dbg fallback. This adds process-context-dependent I/O interaction; the existing helper uses Process.group_leader and Process.monitor.

Evidence: [livebook-dev__kino-231.patch, line 16](livebook-dev__kino-231.patch)

```elixir
match?({:ok, _}, io_request(:livebook_get_evaluation_file))
```

## quantum-elixir__quantum-core-523: control

Adds function_exported?(m, f, length(args)) validation and filters invalid configured jobs with a warning. This changes input eligibility, not scheduler delivery, supervision, timing or process failure handling. Supervisor references are unchanged context.

Evidence: [quantum-elixir__quantum-core-523.patch, line 55](quantum-elixir__quantum-core-523.patch)

```elixir
do: not function_exported?(m, f, length(args))
```

## Result

5 OTP, 2 control, 1 uncertain. If these five OTP decisions are applied to the reported baseline, cap-four capacity rises from 29 to 34: Broadway gains two slots (1 to 3), Protobuf one (0 to 1), Quantum one (0 to 1), and Kino one (2 to 3). This is arithmetic against the supplied baseline, not a rerun of the profiler. It remains an upper bound before remaining reviews, matching and runtime validation. The two controls are semantic labels and do not satisfy the original no-marker-anywhere control rule automatically.
