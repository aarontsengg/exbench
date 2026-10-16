# Failure triage — 14 October 2026

Observed log signatures, not proven root causes. No tasks were automatically excluded or tests edited.

## phoenixframework__phoenix-2974

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test flash is persisted when status is a redirect (Phoenix.Controller.FlashTest)
     test/phoenix/controller/flash_test.exs:12
     ** (UndefinedFunctionError) function :crypto.hmac/3 is undefined or private, use crypto:mac/4 instead
     code: for status <- 300..308 do
     stacktrace:
       (crypto 5.4.2.3) :crypto.hmac(:sha256, "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh", <<121, 97, 100, 97, 121, 97, 100, 97, 0, 0, 0, 1>>)
       (plug 1.6.0) lib/plug/crypto/key_generator.ex:66: Plug.Crypto.KeyGenerator.generate/7
       (plug 1.6.0) lib/plug/crypto/key_generator.ex:52: Plug.Crypto.KeyGenerator.with_cache/3
       (plug 1.6.0) lib/plug/session/cookie.ex:110: Plug.Session.COOKIE.put/4
  2) test flash writes to session when it is empty and a previous session exists (Phoenix.Controller.FlashTest)
     test/phoenix/controller/flash_test.exs:45
     ** (UndefinedFunctionError) function :crypto.hmac/3 is undefined or private, use crypto:mac/4 instead
     code: |> send_resp(302, "ok")
     stacktrace:
       (crypto 5.4.2.3) :crypto.hmac(:sha256, "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh", <<121, 97, 100, 97, 121, 97, 100, 97, 0, 0, 0, 1>>)
       (plug 1.6.0) lib/plug/crypto/key_generator.ex:66: Plug.Crypto.KeyGenerator.generate/7
       (plug 1.6.0) lib/plug/crypto/key_generator.ex:52: Plug.Crypto.KeyGenerator.with_cache/3
       (plug 1.6.0) lib/plug/session/cookie.ex:110: Plug.Session.COOKIE.put/4
```

Full log: validation_runs/smoke-single-map/phoenixframework__phoenix-2974.gold.log

## phoenixframework__phoenix_html-282

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test does not escape safe expressions (Phoenix.HTML.EngineTest)
     test/phoenix_html/engine_test.exs:31
     ** (ArgumentError) invalid runtime value for option :line in quote, got: nil
     code: assert eval("Safe <%= {:safe, \"<value>\"} %>") == "Safe <value>"
     stacktrace:
       (elixir 1.16.3) src/elixir_quote.erl:244: :elixir_quote.validate_runtime/2
       (phoenix_html 2.13.3) lib/phoenix_html/engine.ex:98: Phoenix.HTML.Engine.to_safe/2
       (phoenix_html 2.13.3) lib/phoenix_html/engine.ex:62: Phoenix.HTML.Engine.handle_expr/3
       (eex 1.16.3) lib/eex/compiler.ex:333: EEx.Compiler.generate_buffer/4
  2) test datetime_select/4 (Phoenix.HTML.FormTest)
     test/phoenix_html/form_test.exs:1213
     Assertion with =~ failed
     code:  assert content =~ ~s"<option value=\"2020\" selected>2020</option>"
     left:  "<select id=\"search_datetime_year\" name=\"search[datetime][year]\"><option value=\"2021\">2021</option><option value=\"2022\">2022</option><option value=\"2023\">2023</option><option value=\"2024\">2024</option><option value=\"2025\">2025</option><option value=\"2026\">2026</option><op
     right: "<option value=\"2020\" selected>2020</option>"
     stacktrace:
       test/phoenix_html/form_test.exs:1235: (test)

```

Full log: validation_runs/batch-02/phoenixframework__phoenix_html-282.gold.log

## plataformatec__broadway-95

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test pipeline without batchers shutting down broadway waits until all events are processed (BroadwayTest)
     test/broadway_test.exs:490
     ** (EXIT from #PID<0.1502.0>) shutdown

  * test shutdown shutting down broadway waits until all events are processed even on incomplete batches [L#1198]
  * test shutdown shutting down broadway waits until all events are processed even on incomplete batches (2.9ms) [L#1198]
  * test broadway configuration default context is :context_not_set [L#274]
  * test broadway configuration default context is :context_not_set (2.6ms) [L#274]
  * test broadway configuration default number of consumers is 1 per batcher [L#237]
  2) test batcher consumers do not crash on bad acknowledger (BroadwayTest)
     test/broadway_test.exs:1106
     Assertion with =~ failed
     code:  assert capture_log(fn ->
              Broadway.push_messages(broadway, [one, two, raise, three])
              ref = Broadway.test_messages(broadway, [1, 2, 3, 4], batch_mode: :bulk)
              assert_receive {:ack, ^ref, [%{data: 1}, %{data: 2}, %{data: 3}, %{data: 4}], []}
            end) =~ "[error] ** (UndefinedFunctionError) function Unknown.ack/3 is undefined"
     left:  "\n21:26:16.851 [error] ** (RuntimeError) Error raised\n\n21:26:16.853 [error] ** (UndefinedFunctionError) undefined function\n"
```

Full log: validation_runs/remaining-56/plataformatec__broadway-95.gold.log

## elixir-plug__plug-1245

Upstream gold passing-list match: True. Strict gold pass: True.

Evidence from base phase:
```text
== Compilation error in file test/plug/session_test.exs ==
** (CompileError) test/plug/session_test.exs: cannot compile module Plug.SessionTest (errors have been logged)

** (CompileError) test/plug/session_test.exs: cannot compile module Plug.SessionTest (errors have been logged)

```

Full log: validation_runs/remaining-56/elixir-plug__plug-1245.base.log

## commanded__commanded-139

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test tracker should list tracked processes (Commanded.PubSub.PhoenixPubSubTest)
     test/pubsub/phoenix_pubsub_test.exs:40
     ** (EXIT from #PID<0.3385.0>) shutdown: failed to start child: Phoenix.PubSub.PG2
         ** (EXIT) shutdown: failed to start child: Phoenix.PubSub.PG2Server
             ** (EXIT) an exception was raised:
                 ** (UndefinedFunctionError) function :pg2.create/1 is undefined or private
                     (kernel 9.2.4.10) :pg2.create({:phx, Commanded.PubSub.PhoenixPubSub})
                     (phoenix_pubsub 1.0.2) lib/phoenix/pubsub/pg2_server.ex:43: Phoenix.PubSub.PG2Server.init/1
                     (stdlib 5.2.3.5) gen_server.erl:980: :gen_server.init_it/2
  2) test pub/sub should receive broadcast message (Commanded.PubSub.PhoenixPubSubTest)
     test/pubsub/phoenix_pubsub_test.exs:31
     ** (EXIT from #PID<0.3396.0>) shutdown: failed to start child: Phoenix.PubSub.PG2
         ** (EXIT) shutdown: failed to start child: Phoenix.PubSub.PG2Server
             ** (EXIT) an exception was raised:
                 ** (UndefinedFunctionError) function :pg2.create/1 is undefined or private
                     (kernel 9.2.4.10) :pg2.create({:phx, Commanded.PubSub.PhoenixPubSub})
                     (phoenix_pubsub 1.0.2) lib/phoenix/pubsub/pg2_server.ex:43: Phoenix.PubSub.PG2Server.init/1
                     (stdlib 5.2.3.5) gen_server.erl:980: :gen_server.init_it/2
```

Full log: validation_runs/remaining-56/commanded__commanded-139.gold.log

## absinthe-graphql__absinthe-1005

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test import fields handles circular errors (Absinthe.Schema.Notation.ImportTest)
     test/absinthe/schema/notation/import_test.exs:141
     match (=) failed
     code:  assert {:error,
             [
               %Absinthe.Phase.Error{
                 extra: :bar,
                 locations: [%{line: _}],
                 message:
  2) test handle parse error when column not available (Absinthe.Phase.ParseTest)
     test/absinthe/phase/parse_test.exs:39
     Assertion with == failed
     code:  assert [
              %Absinthe.Phase.Error{
                extra: %{},
                locations: [%{column: 0, line: 4}],
                message: "syntax error before: ",
                phase: Absinthe.Phase.Parse
```

Full log: validation_runs/remaining-56/absinthe-graphql__absinthe-1005.gold.log

## commanded__commanded-290

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test should serialize value to JSON (Commanded.Serialization.JsonDecoderTest)
     test/serialization/json_decoder_test.exs:24
     Assertion with == failed
     code:  assert JsonSerializer.serialize(event) == @serialized_event_json
     left:  "{\"date\":\"2016-09-20T20:01:02\",\"name\":\"Ben\"}"
     right: "{\"name\":\"Ben\",\"date\":\"2016-09-20T20:01:02\"}"
     stacktrace:
       test/serialization/json_decoder_test.exs:27: (test)

  2) test register event handler should be registered (Commanded.SubscriptionsTest)
     test/subscriptions/subscriptions_test.exs:8
     Assertion with == failed
     code:  assert Subscriptions.all() == [{"handler3", self()}, {"handler1", self()}]
     left:  [{"handler1", #PID<0.3400.0>}, {"handler3", #PID<0.3400.0>}]
     right: [{"handler3", #PID<0.3400.0>}, {"handler1", #PID<0.3400.0>}]
     stacktrace:
       test/subscriptions/subscriptions_test.exs:13: (test)

```

Full log: validation_runs/remaining-56/commanded__commanded-290.gold.log

## absinthe-graphql__absinthe-1155

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test introspection of an input object type can introspect complex default_value (Absinthe.IntrospectionTest)
     test/absinthe/introspection_test.exs:279
     Assertion with == failed
     code:  assert clean(lhs) == clean(rhs)
     left:  %{
              data: %{
                "__schema" => %{
                  "queryType" => %{
                    "fields" => [
  2) test import fields handles circular errors (Absinthe.Schema.Notation.ImportTest)
     test/absinthe/schema/notation/import_test.exs:141
     match (=) failed
     code:  assert {:error,
             [
               %Absinthe.Phase.Error{
                 extra: :bar,
                 locations: [%{line: _}],
                 message:
```

Full log: validation_runs/remaining-56/absinthe-graphql__absinthe-1155.gold.log

## commanded__commanded-335

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test register event handler should be registered (Commanded.SubscriptionsTest)
     test/subscriptions/subscriptions_test.exs:14
     Assertion with == failed
     code:  assert Subscriptions.all(DefaultApp) == [{"handler3", self()}, {"handler1", self()}]
     left:  [{"handler1", #PID<0.4543.0>}, {"handler3", #PID<0.4543.0>}]
     right: [{"handler3", #PID<0.4543.0>}, {"handler1", #PID<0.4543.0>}]
     stacktrace:
       test/subscriptions/subscriptions_test.exs:19: (test)

  2) test should serialize value to JSON (Commanded.Serialization.JsonDecoderTest)
     test/serialization/json_decoder_test.exs:24
     Assertion with == failed
     code:  assert JsonSerializer.serialize(event) == @serialized_event_json
     left:  "{\"name\":\"Ben\",\"datetime\":\"2016-09-20T20:01:02Z\"}"
     right: "{\"datetime\":\"2016-09-20T20:01:02Z\",\"name\":\"Ben\"}"
     stacktrace:
       test/serialization/json_decoder_test.exs:28: (test)

```

Full log: validation_runs/remaining-56/commanded__commanded-335.gold.log

## coryodaniel__bonny-156

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
** (Mix) Can't continue due to errors on dependencies
```

Full log: validation_runs/remaining-56/coryodaniel__bonny-156.gold.log

## fika-lang__fika-77

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test match_case when lhs matches one of many in a union (Fika.Compiler.TypeChecker.MatchTest)
     test/fika/compiler/type_checker/match_test.exs:93
     Assertion with == failed
     code:  assert unmatched == [:b, :c]
     left:  [:c, :b]
     right: [:b, :c]
     stacktrace:
       test/fika/compiler/type_checker/match_test.exs:99: (test)

  2) test match_case for record with a union inside (Fika.Compiler.TypeChecker.MatchTest)
     test/fika/compiler/type_checker/match_test.exs:194
     Assertion with == failed
     code:  assert unmatched == [
              %T.Record{fields: [name: :String, id: :Int, x: :b]},
              %T.Record{fields: [name: :String, id: :Int, x: :c]}
            ]
     left:  [
              %Fika.Compiler.TypeChecker.Types.Record{
```

Full log: validation_runs/remaining-56/fika-lang__fika-77.gold.log

## derekkraan__curl_req-53

Upstream gold passing-list match: True. Strict gold pass: True.

Evidence from base phase:
```text
== Compilation error in file test/curl_req_test.exs ==
** (CompileError) test/curl_req_test.exs: cannot compile module CurlReqTest (errors have been logged)
    (elixir 1.16.3) expanding macro: Kernel.use/2
    test/curl_req_test.exs:2: CurlReqTest (module)
** (CompileError) test/curl_req_test.exs: cannot compile module CurlReqTest (errors have been logged)
    (elixir 1.16.3) expanding macro: Kernel.use/2
    test/curl_req_test.exs:2: CurlReqTest (module)
```

Full log: validation_runs/remaining-56/derekkraan__curl_req-53.base.log

## elixir-plug__plug-990

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
== Compilation error in file test/plug/session/cookie_test.exs ==
** (UndefinedFunctionError) function :crypto.hmac/3 is undefined or private, use crypto:mac/4 instead

** (UndefinedFunctionError) function :crypto.hmac/3 is undefined or private, use crypto:mac/4 instead

```

Full log: validation_runs/remaining-56/elixir-plug__plug-990.gold.log

## general-cbic__poolex-59

Upstream gold passing-list match: True. Strict gold pass: True.

Evidence from base phase:
```text
== Compilation error in file test/support/some_waiting_callers_impl.ex ==
** (CompileError) test/support/some_waiting_callers_impl.ex: cannot compile module SomeWaitingCallersImpl (errors have been logged)
    (elixir 1.16.3) src/elixir_fn.erl:17: anonymous fn/4 in :elixir_fn.expand/4
    (stdlib 5.2.3.5) lists.erl:1706: :lists.mapfoldl_1/3
    (elixir 1.16.3) src/elixir_fn.erl:23: :elixir_fn.expand/4
** (CompileError) test/support/some_waiting_callers_impl.ex: cannot compile module SomeWaitingCallersImpl (errors have been logged)
    (elixir 1.16.3) src/elixir_fn.erl:17: anonymous fn/4 in :elixir_fn.expand/4
    (stdlib 5.2.3.5) lists.erl:1706: :lists.mapfoldl_1/3
    (elixir 1.16.3) src/elixir_fn.erl:23: :elixir_fn.expand/4
```

Full log: validation_runs/remaining-56/general-cbic__poolex-59.base.log

## newrelic__elixir_agent-84

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test post a span event (SpanEventTest)
     test/span_event_test.exs:26
     ** (UndefinedFunctionError) function :ssl.cipher_suites/0 is undefined or private, use cipher_suites/2,3 instead
     code: Collector.Protocol.span_event(payload)
     stacktrace:
       (ssl 11.1.4.10) :ssl.cipher_suites()
       (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:78: :hackney_ssl.ciphers/0
       (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:70: :hackney_ssl.connect/4
       (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:247: :hackney_connect.do_connect/5
** (UndefinedFunctionError) function :ssl.cipher_suites/0 is undefined or private
    (ssl 11.1.4.10) :ssl.cipher_suites()
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:78: :hackney_ssl.ciphers/0
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:70: :hackney_ssl.connect/4
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:247: :hackney_connect.do_connect/5
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:37: :hackney_connect.connect/5
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney.erl:316: :hackney.request/5
    (httpoison 1.3.0) lib/httpoison/base.ex:632: HTTPoison.Base.request/9
    (new_relic_agent 1.6.2) lib/new_relic/harvest/collector/protocol.ex:48: NewRelic.Harvest.Collector.Protocol.issue_call/2
```

Full log: validation_runs/remaining-56/newrelic__elixir_agent-84.gold.log

## phoenixframework__phoenix-2721

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
== Compilation error in file test/phoenix/template_test.exs ==
** (RuntimeError) unexpected EEx.Engine state: {:safe, ""}. This typically means a bug or an outdated EEx.Engine or tool
    (eex 1.16.3) lib/eex/engine.ex:218: EEx.Engine.check_state!/1
    (eex 1.16.3) lib/eex/engine.ex:181: EEx.Engine.handle_text/3
    (eex 1.16.3) lib/eex/compiler.ex:321: EEx.Compiler.generate_buffer/4
    (phoenix 1.4.0-dev) lib/phoenix/template.ex:378: Phoenix.Template.compile/2
    (elixir 1.16.3) lib/enum.ex:1700: Enum."-map/2-lists^map/1-1-"/2
    (phoenix 1.4.0-dev) expanding macro: Phoenix.Template.__before_compile__/1
    test/phoenix/template_test.exs:55: Phoenix.TemplateTest.View (module)
** (RuntimeError) unexpected EEx.Engine state: {:safe, ""}. This typically means a bug or an outdated EEx.Engine or tool
    (eex 1.16.3) lib/eex/engine.ex:218: EEx.Engine.check_state!/1
    (eex 1.16.3) lib/eex/engine.ex:181: EEx.Engine.handle_text/3
    (eex 1.16.3) lib/eex/compiler.ex:321: EEx.Compiler.generate_buffer/4
    (phoenix 1.4.0-dev) lib/phoenix/template.ex:378: Phoenix.Template.compile/2
    (elixir 1.16.3) lib/enum.ex:1700: Enum."-map/2-lists^map/1-1-"/2
    (phoenix 1.4.0-dev) expanding macro: Phoenix.Template.__before_compile__/1
    test/phoenix/template_test.exs:55: Phoenix.TemplateTest.View (module)
```

Full log: validation_runs/remaining-56/phoenixframework__phoenix-2721.gold.log

## phoenixframework__phoenix-3250

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test encode!/1 encodes `Phoenix.Socket.Reply` as JSON (Phoenix.Socket.V1.JSONSerializerTest)
     test/phoenix/socket/v1_json_serializer_test.exs:29
     Assertion with == failed
     code:  assert encode!(@serializer, msg) == @v1_reply_json
     left:  "{\"ref\":\"null\",\"payload\":{\"status\":null,\"response\":null},\"topic\":\"t\",\"event\":\"phx_reply\"}"
     right: "{\"event\":\"phx_reply\",\"payload\":{\"response\":null,\"status\":null},\"ref\":\"null\",\"topic\":\"t\"}"
     stacktrace:
       test/phoenix/socket/v1_json_serializer_test.exs:31: (test)

  2) test fastlane!/1 encodes a broadcast into a message as JSON (Phoenix.Socket.V1.JSONSerializerTest)
     test/phoenix/socket/v1_json_serializer_test.exs:39
     Assertion with == failed
     code:  assert fastlane!(@serializer, msg) == @v1_fastlane_json
     left:  "{\"ref\":null,\"payload\":\"m\",\"topic\":\"t\",\"event\":\"e\"}"
     right: "{\"event\":\"e\",\"payload\":\"m\",\"ref\":null,\"topic\":\"t\"}"
     stacktrace:
       test/phoenix/socket/v1_json_serializer_test.exs:41: (test)

```

Full log: validation_runs/remaining-56/phoenixframework__phoenix-3250.gold.log

## plataformatec__broadway-31

Upstream gold passing-list match: True. Strict gold pass: True.

Evidence from base phase:
```text
== Compilation error in file test/broadway_test.exs ==
** (CompileError) test/broadway_test.exs: cannot compile module BroadwayTest.Forwarder (errors have been logged)

** (CompileError) test/broadway_test.exs: cannot compile module BroadwayTest.Forwarder (errors have been logged)

```

Full log: validation_runs/remaining-56/plataformatec__broadway-31.base.log

## ash-project__ash-1853

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test loads parent references work with no_attributes? true (Ash.Test.Actions.LoadTest)
     test/actions/load_test.exs:552
     ** (UndefinedFunctionError) function DateTime.shift/2 is undefined or private. Did you mean:

           * shift_zone/2
           * shift_zone/3
           * shift_zone!/2
           * shift_zone!/3

```

Full log: validation_runs/remaining-56/ash-project__ash-1853.gold.log

## whitfin__cachex-341

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test notifying a list of Hooks (Cachex.Services.InformantTest)
     test/cachex/services/informant_test.exs:68
     Expected the difference between 35746 and 25000 (10746) to be less than or equal to 10000
     code: assert_in_delta(time1, 25000, 10000)
     stacktrace:
       test/cachex/services/informant_test.exs:132: (test)

  * test broadcasting results to a list of hooks [L#25]
  * test broadcasting results to a list of hooks (221.8ms) [L#25]
```

Full log: validation_runs/remaining-56/whitfin__cachex-341.gold.log

## commanded__commanded-171

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test expire stream acks should expire stale acks (Commanded.SubscriptionsTest)
     test/subscriptions/subscriptions_test.exs:151
     ** (exit) exited in: GenServer.call(Commanded.Subscriptions, :reset, 5000)
         ** (EXIT) no process: the process is not alive or there's no process currently associated with the given name, possibly because its application isn't started
     stacktrace:
       (elixir 1.16.3) lib/gen_server.ex:1103: GenServer.call/3
       test/subscriptions/subscriptions_test.exs:1: Commanded.SubscriptionsTest.__ex_unit__/2

  * test register event handler should require all subscriptions to ack event [L#28]
  2) test register event handler should require all subscriptions to ack event (Commanded.SubscriptionsTest)
     test/subscriptions/subscriptions_test.exs:28
     ** (exit) exited in: GenServer.call(Commanded.Subscriptions, :reset, 5000)
         ** (EXIT) no process: the process is not alive or there's no process currently associated with the given name, possibly because its application isn't started
     stacktrace:
       (elixir 1.16.3) lib/gen_server.ex:1103: GenServer.call/3
       test/subscriptions/subscriptions_test.exs:1: Commanded.SubscriptionsTest.__ex_unit__/2

  * test expire stream acks should not expire fresh acks [L#163]
```

Full log: validation_runs/remaining-56/commanded__commanded-171.gold.log

## commanded__commanded-380

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test should serialize value to JSON (Commanded.Serialization.JsonDecoderTest)
     test/serialization/json_decoder_test.exs:24
     Assertion with == failed
     code:  assert JsonSerializer.serialize(event) == @serialized_event_json
     left:  "{\"name\":\"Ben\",\"datetime\":\"2016-09-20T20:01:02Z\"}"
     right: "{\"datetime\":\"2016-09-20T20:01:02Z\",\"name\":\"Ben\"}"
     stacktrace:
       test/serialization/json_decoder_test.exs:28: (test)

  2) test a Commanded application should fail to start unconfigured application (Commanded.ApplicationTest)
     test/application/application_test.exs:64
     Assertion failed, no matching message after 1000ms
     The process mailbox is empty.
     code: assert_receive {:EXIT, _pid,
            {%ArgumentError{
               message: "missing :event_store config for application Commanded.UnconfiguredApplication"
             }, _}}
     stacktrace:
```

Full log: validation_runs/remaining-56/commanded__commanded-380.gold.log

## elixir-ecto__ecto-2348

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test escape handles expressions and params (Ecto.Query.Builder.GroupByTest)
     test/ecto/query/builder/group_by_test.exs:10
     Assertion with == failed
     code:  assert {Macro.escape(
               quote do
                 [&0.y]
               end
             ),
             %{}} ==
  2) test fully_expand/2 with dynamic interpolation (Ecto.Query.Builder.DynamicTest)
     test/ecto/query/builder/dynamic_test.exs:30
     Assertion with == failed
     code:  assert Macro.to_string(expr) == "&0.foo() == ^0 and &0.bar() == ^1 or &0.baz() == ^2"
     left:  "(&0.foo() == ^0 and &0.bar() == ^1) or &0.baz() == ^2"
     right: "&0.foo() == ^0 and &0.bar() == ^1 or &0.baz() == ^2"
     stacktrace:
       test/ecto/query/builder/dynamic_test.exs:34: (test)

```

Full log: validation_runs/remaining-56/elixir-ecto__ecto-2348.gold.log

## elixir-protobuf__protobuf-164

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test maps non-string key is invalid (Protobuf.JSON.DecodeTest)
     test/protobuf/json/decode_test.exs:380
     Assertion with == failed
     code:  assert decode(data, Maps) == error(msg)
     left:  {:error,
             %Protobuf.JSON.DecodeError{
               message: "Field 'mapsi' has an invalid map key (string: ~c\"chars\")"
             }}
     right: {:error,
```

Full log: validation_runs/remaining-56/elixir-protobuf__protobuf-164.gold.log

## elixir-gettext__gettext-239

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test extracting and extracting with --merge (Mix.Tasks.Gettext.ExtractTest)
     test/mix/tasks/gettext.extract_test.exs:13
     Assertion with == failed
     code:  assert read_file("priv/gettext/it/LC_MESSAGES/my_domain.po") ==
              "#, elixir-format\n#: lib/other.ex:3\nmsgid \"other\"\nmsgstr \"\"\n"
     left:  ""
     right: "#, elixir-format\n#: lib/other.ex:3\nmsgid \"other\"\nmsgstr \"\"\n"
     stacktrace:
       test/mix/tasks/gettext.extract_test.exs:68: (test)
```

Full log: validation_runs/remaining-56/elixir-gettext__gettext-239.gold.log

## general-cbic__poolex-127

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test terminate process workers stop before the pool with reason :exit (PoolexTest)
     test/poolex_test.exs:585
     ** (MatchError) no match of right hand side value: {:messages, [{:DOWN, #Reference<0.1988731134.1066663938.97540>, :process, #PID<0.591.0>, :shutdown}, {:DOWN, #Reference<0.1988731134.1066663938.97539>, :process, #PID<0.590.0>, {:function_clause, [{Poolex, :handle_info, [{:EXIT, #PID<0.587.0>, 
     code: {:messages, [message_1, message_2, message_3]} = Process.info(self(), :messages)
     stacktrace:
       test/poolex_test.exs:602: (test)

  * test remove_idle_workers!/2 removes idle workers from pool [L#641]
  * test remove_idle_workers!/2 removes idle workers from pool (0.2ms) [L#641]
```

Full log: validation_runs/remaining-56/general-cbic__poolex-127.gold.log

## jeregrine__jsonapi-164

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test underscores dasherized data parameters (JSONAPI.UnderscoreParametersTest)
     test/jsonapi/plugs/underscore_parameters_test.exs:7
     match (=) failed
     code:  assert %Plug.Conn{
              params: %{
                "data" => %{
                  "attributes" => %{
                    "first_name" => "John",
                    "last_name" => "Cleese",
  2) test parse_include/2 turns an include string into a keyword list (JSONAPI.QueryParserTest)
     test/jsonapi/plugs/query_parser_test.exs:78
     Wrong message for ArgumentError
     expected:
       "argument error"
     actual:
       "errors were found at the given arguments:\n\n  * 1st argument: not an already existing atom\n"
     code: assert_raise ArgumentError, "argument error", fn ->
     stacktrace:
```

Full log: validation_runs/remaining-56/jeregrine__jsonapi-164.gold.log

## livebook-dev__kino-231

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test sorts maps by key (Kino.TreeTest)
     test/kino/tree_test.exs:104
     match (=) failed
     code:  assert %{
              content: "%{...}",
              expanded: %{prefix: "%{", suffix: "}"},
              children: [%{content: "bar: :baz,", children: nil}, %{content: "foo: :oof", children: nil}]
            } = plaintext_tree(%{foo: :oof, bar: :baz})
     left:  %{
  2) test supports sliceable data (Kino.DataTableTest)
     test/kino/data_table_test.exs:211
     match (=) failed
     code:  assert %{
              content: %{
                columns: [%{key: "0", label: ":x"}, %{key: "1", label: ":y"}],
                rows: [
                  %{fields: %{"0" => "1", "1" => "1"}},
                  %{fields: %{"0" => "2", "1" => "2"}},
```

Full log: validation_runs/remaining-56/livebook-dev__kino-231.gold.log

## newrelic__elixir_agent-37

Upstream gold passing-list match: False. Strict gold pass: False.

Evidence from gold phase:
```text
** (UndefinedFunctionError) function :ssl.cipher_suites/0 is undefined or private
    (ssl 11.1.4.10) :ssl.cipher_suites()
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:78: :hackney_ssl.ciphers/0
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:70: :hackney_ssl.connect/4
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:247: :hackney_connect.do_connect/5
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:37: :hackney_connect.connect/5
    (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney.erl:316: :hackney.request/5
    (httpoison 1.3.0) lib/httpoison/base.ex:632: HTTPoison.Base.request/9
    (new_relic_agent 1.0.3) lib/new_relic/harvest/collector/protocol.ex:48: NewRelic.Harvest.Collector.Protocol.issue_call/2
** (stop) exited in: GenServer.call(#PID<0.1079.0>, :send_harvest, 15000)
    ** (EXIT) an exception was raised:
        ** (UndefinedFunctionError) function :ssl.cipher_suites/0 is undefined or private
            (ssl 11.1.4.10) :ssl.cipher_suites()
            (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:78: :hackney_ssl.ciphers/0
            (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_ssl.erl:70: :hackney_ssl.connect/4
            (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:247: :hackney_connect.do_connect/5
            (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney_connect.erl:37: :hackney_connect.connect/5
            (hackney 1.13.0) /elixir_agent/deps/hackney/src/hackney.erl:316: :hackney.request/5
```

Full log: validation_runs/remaining-56/newrelic__elixir_agent-37.gold.log

## keathley__norm-41

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test bad contract (Norm.ContractTest)
     test/norm/contract_test.exs:41
     Wrong message for ArgumentError
     expected:
       ~r/got: `@contract\(foo\(n\)\)`/
     actual:
       "contract must be in the form `@contract function(arg :: spec) :: result_spec`, got: `@contract foo(n)`"
     code: assert_raise ArgumentError, ~r/got: `@contract\(foo\(n\)\)`/, fn ->
     stacktrace:
  2) test inspect single selection (Norm.SelectionTest)
     test/norm/selection_test.exs:196
     Assertion with == failed
     code:  assert inspect(selection(user_schema())) ==
              "#Norm.Selection<%{required: [:name, :email, :age], schema: #Norm.Schema<%{age: #Norm.Spec<is_integer() and &(&1 > 0)>, email: #Norm.Spec<is_binary() and &(&1 =~ ~r\"@\")>, name: #Norm.Spec<is_binary()>}>}>"
     left:  "#Norm.Selection<%{required: [:email, :age, :name], schema: #Norm.Schema<%{name: #Norm.Spec<is_binary()>, age: #Norm.Spec<is_integer() and &(&1 > 0)>, email: #Norm.Spec<is_binary() and &(&1 =~ ~r/@/)>}>}>"
     right: "#Norm.Selection<%{required: [:name, :email, :age], schema: #Norm.Schema<%{age: #Norm.Spec<is_integer() and &(&1 > 0)>, email: #Norm.Spec<is_binary() and &(&1 =~ ~r\"@\")>, name: #Norm.Spec<is_binary()>}>}>"
     stacktrace:
       test/norm/selection_test.exs:197: (test)
```

Full log: validation_runs/remaining-56/keathley__norm-41.gold.log

## plataformatec__broadway-40

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test processor - failed messages handling processors do not crash on bad acknowledger (BroadwayTest)
     test/broadway_test.exs:443
     Assertion with =~ failed
     code:  assert capture_log(fn ->
              Producer.push_messages(producer, [one, raise, four])
              assert_receive {:ack, [%{data: 1}, %{data: 4}], []}
            end) =~ "[error] ** (UndefinedFunctionError) function Unknown.ack/2 is undefined"
     left:  "\n01:23:53.105 [error] ** (RuntimeError) Error raised\n\n01:23:53.105 [error] ** (UndefinedFunctionError) undefined function\n"
     right: "[error] ** (UndefinedFunctionError) function Unknown.ack/2 is undefined"
  2) test batcher - failed messages handling consumers do not crash on bad acknowledger (BroadwayTest)
     test/broadway_test.exs:927
     Assertion with =~ failed
     code:  assert capture_log(fn ->
              Producer.push_messages(producer, [one, two, raise, three])
              push_messages(producer, [1, 2, 3, 4])
              assert_receive {:ack, [%{data: 1}, %{data: 2}, %{data: 3}, %{data: 4}], []}
            end) =~ "[error] ** (UndefinedFunctionError) function Unknown.ack/2 is undefined"
     left:  "\n01:23:53.118 [error] ** (RuntimeError) Error raised\n\n01:23:53.118 [error] ** (UndefinedFunctionError) undefined function\n"
```

Full log: validation_runs/remaining-56/plataformatec__broadway-40.gold.log

## phoenixframework__phoenix_html-263

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test does not escape safe expressions (Phoenix.HTML.EngineTest)
     test/phoenix_html/engine_test.exs:31
     ** (ArgumentError) invalid runtime value for option :line in quote, got: nil
     code: assert eval("Safe <%= {:safe, \"<value>\"} %>") == "Safe <value>"
     stacktrace:
       (elixir 1.16.3) src/elixir_quote.erl:244: :elixir_quote.validate_runtime/2
       (phoenix_html 2.13.3) lib/phoenix_html/engine.ex:98: Phoenix.HTML.Engine.to_safe/2
       (phoenix_html 2.13.3) lib/phoenix_html/engine.ex:62: Phoenix.HTML.Engine.handle_expr/3
       (eex 1.16.3) lib/eex/compiler.ex:333: EEx.Compiler.generate_buffer/4
  2) test date_select/4 with form (Phoenix.HTML.FormTest)
     test/phoenix_html/form_test.exs:1098
     Assertion with =~ failed
     code:  assert content =~ ~s"<option value=\"2020\" selected>2020</option>"
     left:  "<select id=\"search_datetime_year\" name=\"search[datetime][year]\"><option value=\"2021\">2021</option><option value=\"2022\">2022</option><option value=\"2023\">2023</option><option value=\"2024\">2024</option><option value=\"2025\">2025</option><option value=\"2026\">2026</option><op
     right: "<option value=\"2020\" selected>2020</option>"
     stacktrace:
       test/phoenix_html/form_test.exs:1103: (test)

```

Full log: validation_runs/remaining-56/phoenixframework__phoenix_html-263.gold.log

## whitfin__cachex-292

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test checking if a key exists in a cluster (Cachex.Actions.ExistsTest)
     test/cachex/actions/exists_test.exs:59
     ** (exit) :not_alive
     code: { cache, _nodes } = Helper.create_cache_cluster(2)
     stacktrace:
       (stdlib 5.2.3.5) slave.erl:199: :slave.start/5
       (local_cluster 1.2.1) lib/local_cluster.ex:61: anonymous fn/2 in LocalCluster.start_nodes/3
       (elixir 1.16.3) lib/enum.ex:4365: Enum.map/2
       (local_cluster 1.2.1) lib/local_cluster.ex:60: LocalCluster.start_nodes/3
  2) test setting a key to expire at a given time in a cluster (Cachex.Actions.ExpireAtTest)
     test/cachex/actions/expire_at_test.exs:74
     ** (exit) :not_alive
     code: { cache, _nodes } = Helper.create_cache_cluster(2)
     stacktrace:
       (stdlib 5.2.3.5) slave.erl:199: :slave.start/5
       (local_cluster 1.2.1) lib/local_cluster.ex:61: anonymous fn/2 in LocalCluster.start_nodes/3
       (elixir 1.16.3) lib/enum.ex:4365: Enum.map/2
       (local_cluster 1.2.1) lib/local_cluster.ex:60: LocalCluster.start_nodes/3
```

Full log: validation_runs/remaining-56/whitfin__cachex-292.gold.log

## rrrene__credo-1095

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test loads .credo.exs from ./config subdirs in ascending directories as well (Credo.ConfigFileTest)
     test/credo/config_file_test.exs:455
     Assertion with > failed, both sides are exactly equal
     code: assert config_subdir_count > 1
     left: 1
     stacktrace:
       test/credo/config_file_test.exs:463: (test)

  * test merge_checks works [L#202]
```

Full log: validation_runs/remaining-56/rrrene__credo-1095.gold.log

## whitfin__cachex-294

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test setting a key to expire at a given time in a cluster (Cachex.Actions.ExpireAtTest)
     test/cachex/actions/expire_at_test.exs:74
     ** (exit) :not_alive
     code: {cache, _nodes} = Helper.create_cache_cluster(2)
     stacktrace:
       (stdlib 5.2.3.5) slave.erl:199: :slave.start/5
       (local_cluster 1.2.1) lib/local_cluster.ex:61: anonymous fn/2 in LocalCluster.start_nodes/3
       (elixir 1.16.3) lib/enum.ex:4365: Enum.map/2
       (local_cluster 1.2.1) lib/local_cluster.ex:60: LocalCluster.start_nodes/3
  2) test adding new entries to a cache cluster (Cachex.Actions.PutTest)
     test/cachex/actions/put_test.exs:72
     ** (exit) :not_alive
     code: {cache, _nodes} = Helper.create_cache_cluster(2)
     stacktrace:
       (stdlib 5.2.3.5) slave.erl:199: :slave.start/5
       (local_cluster 1.2.1) lib/local_cluster.ex:61: anonymous fn/2 in LocalCluster.start_nodes/3
       (elixir 1.16.3) lib/enum.ex:4365: Enum.map/2
       (local_cluster 1.2.1) lib/local_cluster.ex:60: LocalCluster.start_nodes/3
```

Full log: validation_runs/remaining-56/whitfin__cachex-294.gold.log

## rrrene__credo-1152

Upstream gold passing-list match: True. Strict gold pass: False.

Evidence from gold phase:
```text
  1) test loads .credo.exs from ./config subdirs in ascending directories as well (Credo.ConfigFileTest)
     test/credo/config_file_test.exs:455
     Assertion with > failed, both sides are exactly equal
     code: assert config_subdir_count > 1
     left: 1
     stacktrace:
       test/credo/config_file_test.exs:462: (test)

  * test merge works in the other direction in reverse, NOT overwriting files[:excluded] [L#155]
```

Full log: validation_runs/remaining-56/rrrene__credo-1152.gold.log

## whitfin__cachex-343

Upstream gold passing-list match: True. Strict gold pass: True.

Evidence from base phase:
```text
== Compilation error in file test/cachex/warmer_test.exs ==
** (ArgumentError) record :warmer does not have the key: :required
    (elixir 1.16.3) lib/record.ex:423: Record.create/4
    (cachex 3.6.0) expanding macro: Cachex.Spec.warmer/1
    test/cachex/warmer_test.exs:54: Cachex.WarmerTest."test warmers which aren't blocking"/1
** (ArgumentError) record :warmer does not have the key: :required
    (elixir 1.16.3) lib/record.ex:423: Record.create/4
    (cachex 3.6.0) expanding macro: Cachex.Spec.warmer/1
    test/cachex/warmer_test.exs:54: Cachex.WarmerTest."test warmers which aren't blocking"/1
```

Full log: validation_runs/remaining-56/whitfin__cachex-343.base.log

