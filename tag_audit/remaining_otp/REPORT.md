# Review of the remaining 25 OTP candidates

Reviewed on 2026-09-21. All 25 previously unreviewed exact-A automatic OTP candidates were reviewed against their complete reference patches and issue descriptions from the local pinned dataset. Results: **16 OTP, 9 control, 0 newly uncertain**. No paid model calls or upstream task execution. These are assistant judgments, not independent human validation.

Dataset: `nebius/SWE-rebench-V2` at `475dd5e8703bb5fb22dd3c60b5d038b019eba1e0`. Parquet SHA-256: `0e0bf9355f892ad74ae98d4e1c404f39fd6654a8e351ee3e6ab162e4a64cd3ad`.

## Rule and scope

Count substantive process communication, lifecycle, supervision, identity/addressing, timing or cross-process failure behavior. Exclude documentation, formatting, API relocation and ordinary data/configuration changes inside process-hosting modules. Process-local bookkeeping alone is excluded. Payload-only additions that leave coordination behavior unchanged are also excluded. Mixed patches qualify when a substantive OTP change exists anywhere, but this does not establish that the reported issue requires OTP reasoning.

The boundary-sensitive control decisions are Commanded-334 (domain UUID exposed via process dictionary), Kino-208 (extra source metadata in startup/update payloads), NewRelic-67 (log backend), and Cachex-360 (internal message rename). Their reasons explicitly describe the interpretation. Cachex-292 qualifies because it changes asynchronous exception transport and reraising, not only metadata formatting. These boundaries should be kept fixed when reviewing future tasks.

This is a targeted completion audit, not an additional random sample. Do not combine its disagreement rate with the original random 40-task audit. Semantic control labels do not automatically satisfy the original stricter no-marker-anywhere eligibility rule.

## Updated exact-A profile

| Label | Count |
|---|---:|
| otp | 38 |
| borderline | 2 |
| control | 258 |
| uncertain | 1 |

**15 OTP repository strings; cap-four OTP capacity: 29; unreviewed OTP candidates: 0.** The prior uncertain Absinthe-944 remains uncertain. The two prior borderline candidates remain unchanged.

Capacity fell from 34 to 29 as follows. Counts use literal upstream repository strings; renames/forks have not been consolidated.

| Repository | Before OTP count | After OTP count | Before capped slots | After capped slots |
|---|---:|---:|---:|---:|
| commanded/commanded | 11 | 10 | 4 | 4 |
| derekkraan/curl_req | 1 | 0 | 1 | 0 |
| general-CbIC/poolex | 6 | 5 | 4 | 4 |
| livebook-dev/kino | 3 | 1 | 3 | 1 |
| newrelic/elixir_agent | 5 | 2 | 4 | 2 |
| whitfin/cachex | 7 | 6 | 4 | 4 |

29 is an OTP-only upper bound, not 29 matched pairs. Matching on difficulty/patch size, sharing the repo cap across both groups, repository canonicalization and reference-patch execution can reduce it. Do not change labels merely to reach 30.

## Decisions and evidence

### livebook-dev__kino-310: control

Adds Kino.Shorts convenience wrappers and documentation. Process.sleep/Process.info occur in examples; Kino.Process is also a documentation reference. No substantive process coordination or lifecycle behavior changes.

Evidence: [livebook-dev__kino-310.patch:100](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/livebook-dev__kino-310.patch:100)

```diff
-        Process.sleep(50)
```

Evidence: [livebook-dev__kino-310.patch:110](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/livebook-dev__kino-310.patch:110)

```diff
-      data = Process.info(self())
```

### general-cbic__poolex-35: otp

Replaces global queue-implementation settings with per-pool settings, introduces a shared ETS settings table, and threads pool identity through busy/idle worker and waiting-caller operations. This changes how concurrent pool instances manage their workers and callers, rather than merely validating an option.

Evidence: [general-cbic__poolex-35.patch:171](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-35.patch:171)

```diff
+    :ok = Settings.init()
```

Evidence: [general-cbic__poolex-35.patch:177](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-35.patch:177)

```diff
+      busy_workers_state: BusyWorkers.init(pool_id, busy_workers_impl),
```

### commanded__commanded-334: control

Exposes the existing domain process-manager UUID through process-local storage: initialization puts :process_uuid and identity/0 reads it. Registration, routing, acknowledgement and lifecycle behavior stay the same; snapshot_uuid is a rename. Under the existing rule excluding process-local bookkeeping alone, this is control, despite the identity API name.

Evidence: [commanded__commanded-334.patch:62](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-334.patch:62)

```diff
+  def identity, do: Process.get(:process_uuid)
```

Evidence: [commanded__commanded-334.patch:84](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-334.patch:84)

```diff
+    Process.put(:process_uuid, process_uuid)
```

### phoenixframework__phoenix-2974: otp

Mixed patch: beyond the reported generator/fallback issue, it changes endpoint child startup order and socket pool lookup/ownership. Pool startup now uses endpoint-specific configuration and supervisor PIDs rather than the previous globally named lookup. Substantive supervision/identity changes qualify the reference patch, but are not evidence that the main issue itself requires OTP.

Evidence: [phoenixframework__phoenix-2974.patch:380](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/phoenixframework__phoenix-2974.patch:380)

```diff
+      case PoolSupervisor.start_child(socket.endpoint, socket.handler, key, args) do
```

Evidence: [phoenixframework__phoenix-2974.patch:620](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/phoenixframework__phoenix-2974.patch:620)

```diff
diff --git a/lib/phoenix/socket/pool_supervisor.ex b/lib/phoenix/socket/pool_supervisor.ex
```

### phoenixframework__phoenix-2721: otp

Changes executable application templates to generate modern supervisor child specifications, with a compatibility branch for older Elixir. These templates determine generated application startup; the changes are not just prose mentioning Supervisor.

Evidence: [phoenixframework__phoenix-2721.patch:102](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/phoenixframework__phoenix-2721.patch:102)

```diff
+      supervisor(<%= app_module %>.Repo, []),
```

Evidence: [phoenixframework__phoenix-2721.patch:80](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/phoenixframework__phoenix-2721.patch:80)

```diff
+    # See https://hexdocs.pm/elixir/Supervisor.html
```

### newrelic__elixir_agent-67: control

Adds a configurable Logger output backend and a handle_cast branch for the existing log request. The request protocol, reply behavior and lifecycle remain unchanged; the change concerns the destination/format of log output.

Evidence: [newrelic__elixir_agent-67.patch:29](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-67.patch:29)

```diff
+    Logger.log(level, "new_relic_agent - " <> message)
```

Evidence: [newrelic__elixir_agent-67.patch:28](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-67.patch:28)

```diff
+  def handle_cast({:log, level, message}, %{io_device: Logger} = state) do
```

### general-cbic__poolex-54: otp

Changes worker restart policy and pool recovery after worker death, including DOWN handling, waiting callers and replacement workers. This directly changes monitoring, failure recovery and allocation behavior.

Evidence: [general-cbic__poolex-54.patch:11](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-54.patch:11)

```diff
+      restart: :temporary
```

Evidence: [general-cbic__poolex-54.patch:58](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-54.patch:58)

```diff
+        {:DOWN, monitoring_reference, _process, dead_process_pid, _reason},
```

### newrelic__elixir_agent-37: otp

Conditionally installs or removes the Erlang error_logger report handler during supervisor initialization. This changes event-handler registration/lifecycle based on the feature setting, beyond formatting reported errors.

Evidence: [newrelic__elixir_agent-37.patch:34](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-37.patch:34)

```diff
-    :error_logger.add_report_handler(NewRelic.Error.ErrorHandler)
```

Evidence: [newrelic__elixir_agent-37.patch:33](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-37.patch:33)

```diff
-    :error_logger.delete_report_handler(NewRelic.Error.ErrorHandler)
```

### commanded__commanded-335: otp

Handles an empty interested-process list by acknowledging the event and continuing. Changes process-manager routing and failure/acknowledgement behavior so an empty routing result does not strand processing.

Evidence: [commanded__commanded-335.patch:217](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-335.patch:217)

```diff
+          ack_and_continue(event, state)
```

Evidence: [commanded__commanded-335.patch:216](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-335.patch:216)

```diff
+        {:start, []} ->
```

### derekkraan__curl_req-32: control

Adds HTTP User-Agent handling to curl generation/parsing. Agent refers to an HTTP header, not an Elixir Agent process. The functional change is HTTP command/header construction.

Evidence: [derekkraan__curl_req-32.patch:15](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/derekkraan__curl_req-32.patch:15)

```diff
+- [BREAKING]: User Agent is encoded in the user agent flag (`--user-agent`/`-A`) instead of a generic header ([#32](https://github.com/derekkraan/curl_req/pull/32))
```

Evidence: [derekkraan__curl_req-32.patch:15](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/derekkraan__curl_req-32.patch:15)

```diff
+- [BREAKING]: User Agent is encoded in the user agent flag (`--user-agent`/`-A`) instead of a generic header ([#32](https://github.com/derekkraan/curl_req/pull/32))
```

### livebook-dev__kino-208: control

Mixed UI/source-data patch: adds nested tree rendering and source chunks. The SmartCell init_ack tuple gains a chunks field and its receiver is updated, while update messages carry the same extra metadata. Acknowledgement timing, process startup/failure paths and message destination are unchanged. Treats a payload-only extension as data handling, not an OTP coordination change.

Evidence: [livebook-dev__kino-208.patch:340](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/livebook-dev__kino-208.patch:340)

```diff
-    :proc_lib.init_ack({:ok, self(), source, init_opts})
```

Evidence: [livebook-dev__kino-208.patch:356](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/livebook-dev__kino-208.patch:356)

```diff
+       %{chunks: chunks, reevaluate: state.reevaluate_on_change}}
```

### newrelic__elixir_agent-503: control

Generalizes distributed-tracing context/header handling beyond HTTP. The changed arguments carry trace metadata through existing transaction paths; no new monitoring, supervision or process-lifecycle protocol is introduced.

Evidence: [newrelic__elixir_agent-503.patch:1](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-503.patch:1)

```diff
diff --git a/lib/new_relic.ex b/lib/new_relic.ex
```

Evidence: [newrelic__elixir_agent-503.patch:55](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-503.patch:55)

```diff
-  If multiple transactions are started in the same Process, you must
```

### whitfin__cachex-360: control

Refactors cache entry fields and query/match specifications. The Janitor message is consistently renamed from :ttl_check to :purge at send and receive sites; its scheduling behavior is unchanged. A callback/message rename alone does not establish an OTP semantic change.

Evidence: [whitfin__cachex-360.patch:730](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/whitfin__cachex-360.patch:730)

```diff
-  def handle_info(:ttl_check, {cache(name: name), _last}) do
```

Evidence: [whitfin__cachex-360.patch:210](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/whitfin__cachex-360.patch:210)

```diff
-        false -> Cachex.del(cache, key, const(:purge_override))
```

### commanded__commanded-121: otp

Introduces aggregate snapshot restoration and snapshot requests within the GenServer lifecycle, with timeout handling and explicit stopping. State recovery and asynchronous snapshot handling are substantive process behavior.

Evidence: [commanded__commanded-121.patch:9](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-121.patch:9)

```diff
+- Aggregate state snapshots ([#121](https://github.com/commanded/commanded/pull/121)).
```

Evidence: [commanded__commanded-121.patch:346](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-121.patch:346)

```diff
+    GenServer.stop(via_name(aggregate_module, aggregate_uuid))
```

### slashdotdash__commanded-102: otp

Applies aggregate identity prefixes early enough for dispatch/registration and strong-consistency waiting to use the same identity. Changes process addressing and acknowledgement coordination, fixing consistency timeouts.

Evidence: [slashdotdash__commanded-102.patch:11](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/slashdotdash__commanded-102.patch:11)

```diff
+- Adding a prefix to the aggregate in the router breaks the strong consistency of command dispatch ([#101](https://github.com/slashdotdash/commanded/issues/101)).
```

Evidence: [slashdotdash__commanded-102.patch:11](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/slashdotdash__commanded-102.patch:11)

```diff
+- Adding a prefix to the aggregate in the router breaks the strong consistency of command dispatch ([#101](https://github.com/slashdotdash/commanded/issues/101)).
```

### newrelic__elixir_agent-483: control

Fixes tracing timestamp/attribute data and guards missing Finch tracing context. Process dictionary access supplies instrumentation metadata; no new process monitoring, scheduling, supervision or cross-process failure protocol is added. Sleep examples do not establish OTP behavior.

Evidence: [newrelic__elixir_agent-483.patch:9](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-483.patch:9)

```diff
-    Process.sleep(:rand.uniform(50))
```

Evidence: [newrelic__elixir_agent-483.patch:36](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-483.patch:36)

```diff
+        %{system_time: start_time},
```

### whitfin__cachex-294: otp

Adds asynchronous warming at initialization: an option queues :cachex_warmer to self instead of running the warming callback inline. This changes startup blocking and when the worker performs work.

Evidence: [whitfin__cachex-294.patch:90](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/whitfin__cachex-294.patch:90)

```diff
+          send(self(), :cachex_warmer)
```

Evidence: [whitfin__cachex-294.patch:47](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/whitfin__cachex-294.patch:47)

```diff
+            async: boolean
```

### kraigie__nostrum-369: otp

Mixed patch: the user cache becomes a supervised component and ETS creation moves into supervisor initialization. That changes table ownership/lifetime and application startup, independently of other message-component edits.

Evidence: [kraigie__nostrum-369.patch:77](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/kraigie__nostrum-369.patch:77)

```diff
+  ## Supervisor callbacks
```

Evidence: [kraigie__nostrum-369.patch:9](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/kraigie__nostrum-369.patch:9)

```diff
-    :ets.new(:users, [:set, :public, :named_table])
```

### commanded__commanded-139: otp

Changes aggregate after-event lifecycle handling, including stop/hibernate/timeout decisions and snapshot interactions. The new stop branch returns an OTP stop tuple and affects whether the aggregate process remains alive.

Evidence: [commanded__commanded-139.patch:147](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-139.patch:147)

```diff
+        {:stop, :normal, reply, state}
```

Evidence: [commanded__commanded-139.patch:9](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-139.patch:9)

```diff
+- Replace aggregate lifespan `after_command/1` callback with `after_event/1` ([#139](https://github.com/commanded/commanded/issues/139)).
```

### coryodaniel__bonny-156: otp

Adds a named Agent-backed event recorder as a supervised child. Agent.get/update maintain the event cache across calls; this introduces a new process, state ownership and supervised lifecycle to support Kubernetes events.

Evidence: [coryodaniel__bonny-156.patch:857](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/coryodaniel__bonny-156.patch:857)

```diff
+    Agent.start_link(fn -> %{conn: conn} end, name: name)
```

Evidence: [coryodaniel__bonny-156.patch:673](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/coryodaniel__bonny-156.patch:673)

```diff
+          {Bonny.EventRecorder, name: __MODULE__.EventRecorder, conn: conn()}
```

### general-cbic__poolex-59: otp

Separates worker checkout timeout from execution timeout and adds reference-based checkout cancellation. Changes pending-caller removal, monitor cleanup and worker allocation to avoid leaked busy workers after a timeout.

Evidence: [general-cbic__poolex-59.patch:201](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-59.patch:201)

```diff
+    caller_reference = make_ref()
```

Evidence: [general-cbic__poolex-59.patch:239](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-59.patch:239)

```diff
+    {:noreply, WaitingCallers.remove_by_reference(state, caller_reference)}
```

### commanded__commanded-393: otp

Adds runtime initialization callbacks that determine handler/router names and child specifications before startup. Also changes subscription registry entries and strong-consistency filtering so runtime instances can be addressed correctly. This affects process identity, supervision and acknowledgement coordination.

Evidence: [commanded__commanded-393.patch:166](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-393.patch:166)

```diff
+          start: {Handler, :start_link, [application, name, __MODULE__, config]},
```

Evidence: [commanded__commanded-393.patch:501](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/commanded__commanded-393.patch:501)

```diff
+          Enum.member?(consistency, module) or Enum.member?(consistency, name)
```

### general-cbic__poolex-145: control

Moves the debug-info API into a private helper module while retaining the same GenServer.call and server behavior. The changed callback/module references are an API relocation, not changed concurrency semantics.

Evidence: [general-cbic__poolex-145.patch:54](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-145.patch:54)

```diff
-    GenServer.call(pool_id, :get_debug_info)
```

Evidence: [general-cbic__poolex-145.patch:11](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/general-cbic__poolex-145.patch:11)

```diff
+- Function `get_debug_info/1` moved from `Poolex` to `Poolex.Private.DebugInfo` (according to the [issue](https://github.com/general-CbIC/poolex/issues/140)).
```

### whitfin__cachex-292: otp

Captures the caller stack before dispatch, transports it to the asynchronous worker, combines it with the rescued worker stack and reraises an ExecutionError at the caller. This changes cross-process exception propagation/context rather than merely adding an unrelated Process keyword.

Evidence: [whitfin__cachex-292.patch:42](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/whitfin__cachex-292.patch:42)

```diff
+    do: service_call(cache, :courier, { :dispatch, key, task, local_stack() })
```

Evidence: [whitfin__cachex-292.patch:10](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/whitfin__cachex-292.patch:10)

```diff
+    do: reraise e, stack
```

### newrelic__elixir_agent-84: otp

Completes and cleans up traced transactions when the monitored process sends DOWN. It also untracks the transaction before launching the completion task, rather than inside it. These are substantive process-exit cleanup and ordering changes supporting non-web transactions.

Evidence: [newrelic__elixir_agent-84.patch:949](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-84.patch:949)

```diff
+    Transaction.Reporter.complete(pid)
```

Evidence: [newrelic__elixir_agent-84.patch:1026](/Users/aarontseng/Coding/exbench/tag_audit/remaining_otp/newrelic__elixir_agent-84.patch:1026)

```diff
+      AttrStore.untrack(__MODULE__, pid)
```

## Saved changes and verification

`reviews.json` and all 25 reference patches are saved beside this report. The profiler now loads this third review file. Existing reviews were retained. The JSON profile now includes a separate `review_adjusted_exact_a` section while preserving the original automatic counts.

Verified: the 25 IDs exactly cover the previously unreviewed exact-A automatic OTP set; no duplicate IDs; every saved patch equals its pinned-dataset patch and matches its SHA-256; evidence line references match; aggregate counts sum to 299; capacity independently recomputes to 29. The profiler also verified the dataset checksum and required schema fields. No task correctness/runtime tests were run.
