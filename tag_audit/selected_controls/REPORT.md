# Selected control audit

28 new static reviews: seven discussed with Aaron (two patches and five summaries), 21 assistant reviews. All are non-OTP under the application-process rubric. This is not independent human validation or test execution. Large embedded assets were skimmed; source logic was reviewed.

One sampling exclusion: Phoenix #4309 is primarily a JavaScript fix. Its control label remains; eligibility is recorded separately. Replaced by already-reviewed ash-project__ash-1853, the lexicographically first previously reviewed eligible control in the same bucket with repository capacity. The other 29 pairs remain unchanged.

Boundary: compiler validation, serialization, UI callbacks and payload changes do not count as OTP unless process/message/supervision behavior changes. Runtime version checks alone do not count.

## elixir-protobuf__protobuf-387 — control

Serialization/default handling and iodata changes. Removing an OTP-version System.halt guard in the conformance runner is runtime compatibility, not application process lifecycle or coordination.

## keathley__finch-47 — control

Accepts a URI struct in URL normalization. Pool documentation changes do not change pool workers or coordination. Historical repository lineage still needs verification.

## adobe__elixir-styler-205 — control

Adds list and word-sigil sorting controlled by styler comments. Zipper traversal halt is not process termination.

## phoenixframework__phoenix-3250 — control

Displays websocket and long-poll routes in CLI route listings; does not change transport execution.

## rrrene__credo-1152 — control

Corrects apply-call lint analysis for argument lists with a tail. AST list matching, not process execution.

## phoenixframework__phoenix-4309 — control

Changes JavaScript heartbeat timers, reconnect handling and browser event ordering; incidental Elixir float-to-param support and documentation. Non-OTP, but excluded from sample because the reported bug and primary fix are browser JavaScript, not Elixir.

## absinthe-graphql__absinthe-1155 — control

Converts ensure_compiled! ArgumentError into schema validation errors. OTP CI version updates are compatibility metadata, not process semantics.

## 100phlecs__tailwind_formatter-33 — control

Preserves quotes, list syntax and spacing while formatting Tailwind classes. String/AST formatting only.

## absinthe-graphql__absinthe-1005 — control

Supports evaluated descriptions and module attributes in schema notation, and removes repeatable-directive handling. Schema AST/introspection changes.

## adobe__elixir-styler-197 — control

Changes depiping of assignments and AST/comment line positions. Formatting only.

## elixir-gettext__gettext-239 — control

Filters compiled locale files and creates output directories. ParallelCompiler.async is unchanged context; no worker scheduling/lifecycle change.

## fika-lang__fika-34 — control

Adds map literal parsing, type checking and Erlang AST translation. Compiler data transformations, not OTP behavior.

## woylie__doggo-379 — control

Extracts CSS classes from component metadata, adds nested_classes callbacks and renames the CLI. UI metadata callbacks, not OTP callbacks.

## elixir-ecto__ecto-2348 — control

Reports applied migrations whose files are absent. Existing migration locking remains context rather than changed synchronization.

## elixir-plug__plug-990 — control

Extracts forwarded-header rewriting into Plug.RewriteOn. Host, port and scheme transformations; Plug init is not a GenServer callback.

## tallarium__reverse_proxy_plug-177 — control

Threads the updated Plug.Conn from read_body and accumulates request body chunks before the proxy request. Changes request-body IO/data flow, not an explicit BEAM message protocol or process lifecycle.

## derekkraan__curl_req-53 — control

Initializes requests via Req.new and registers request steps/options. Mention of receive_timeout concerns option recognition, not a changed process timeout protocol.

## elixir-ecto__ecto-4552 — control

Moves association validation to after_verify and uses ensure_loaded? instead of compile dependency checks; refactors schema generation. Compilation-phase ordering is treated as compiler behavior, not application OTP coordination.

## divvypayhq__absinthe_federation-109 — control

Adds federation directives and typed blueprint argument metadata. Traffic-related directive descriptions do not implement process routing or supervision.

## woylie__flop_phoenix-221 — control

Changes sort-arrow and aria-sort rendering for ordered columns. HEEx/UI generation.

## phoenixframework__phoenix_html-282 — control

Removes is_atom guards from content_tag so tag names can be converted with to_string. HTML construction, not process behavior.

## mhanberg__temple-243 — control

Renders foreign SVG/MathML void elements with closing slash while preserving HTML behavior. Markup generation.

## adobe__elixir-styler-155 — control

Expands aliases for directives moved earlier in the module. Macro.prewalk transforms AST; no process coordination.

## elixir-plug__plug-1245 — control

Supports function targets in router macros, plus cookie accessors, TLS option normalization and debugger presentation. Adapter message contract is documented but runtime messaging implementation is not changed. Broad mixed patch merits runtime/test-alignment checks.

## keathley__norm-41 — control

Handles predicate macro syntax without parentheses; AST/spec construction, not OTP callbacks.

## rrrene__credo-1095 — control

Groups alias directives per module in AST lint analysis instead of mixing modules. No process behavior.

## jeregrine__jsonapi-164 — control

Merges custom links into the non-pagination response. Response data transformation only.

## kraigie__nostrum-377 — control

Adds guild_id to role-create/update return tuples. Existing ETS operations remain unchanged; payload shape changes, not ownership or synchronization.
