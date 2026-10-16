# Reference validation results

Scope: original 60-task draft. No model calls. Recorded amd64 emulation with explicit JIT override.

Counts: quarantined: 1, validated: 23, needs_investigation: 36

Upstream passing-list matches: 47; strict gold passes: 28.

Strict validation adds zero failed tests, successful gold exit, and exact base test outcomes. Upstream passing-list matching alone does not require these. These are different measures, not agent scores.

Reviewed expected API compilation failures (separate from strict validation): {'otp': 3}.

This category requires the supplemental interface in future agent instructions. It does not verify individual base test outcomes or finalize sample eligibility. See VALIDATION_POLICY.md.

| Task | Group | Status | Baseline category | Base / gold seconds |
| --- | --- | --- | --- | --- |
| phoenixframework__phoenix-2974 | otp | quarantined | unresolved | 20.33 / 16.05 |
| elixir-protobuf__protobuf-387 | control | validated | strict_transition_verified | 30.65 / 29.65 |
| absinthe-graphql__absinthe-1336 | otp | validated | strict_transition_verified | 16.98 / 14.02 |
| phoenixframework__phoenix_html-282 | control | needs_investigation | unresolved | 1.63 / 1.73 |
| general-cbic__poolex-35 | otp | validated | strict_transition_verified | 3.75 / 2.65 |
| divvypayhq__absinthe_federation-109 | control | validated | strict_transition_verified | 7.25 / 6.79 |
| plataformatec__broadway-95 | otp | needs_investigation | unresolved | 3.55 / 3.46 |
| elixir-plug__plug-1245 | control | needs_investigation | unresolved | 4.18 / 6.29 |
| commanded__commanded-139 | otp | needs_investigation | unresolved | 5.37 / 4.7 |
| absinthe-graphql__absinthe-1005 | control | needs_investigation | unresolved | 5.89 / 13.43 |
| commanded__commanded-290 | otp | needs_investigation | unresolved | 9.53 / 9.9 |
| absinthe-graphql__absinthe-1155 | control | needs_investigation | unresolved | 1.53 / 12.45 |
| commanded__commanded-335 | otp | needs_investigation | unresolved | 26.84 / 18.07 |
| adobe__elixir-styler-197 | control | validated | strict_transition_verified | 4.61 / 4.24 |
| coryodaniel__bonny-156 | otp | needs_investigation | unresolved | 1.37 / 1.23 |
| adobe__elixir-styler-205 | control | validated | strict_transition_verified | 4.1 / 4.41 |
| fika-lang__fika-77 | otp | needs_investigation | unresolved | 2.19 / 3.05 |
| derekkraan__curl_req-53 | control | needs_investigation | unresolved | 9.66 / 7.72 |
| general-cbic__poolex-15 | otp | validated | strict_transition_verified | 6.74 / 6.88 |
| elixir-ecto__ecto-4552 | control | validated | strict_transition_verified | 15.02 / 15.25 |
| general-cbic__poolex-54 | otp | validated | strict_transition_verified | 3.89 / 3.5 |
| elixir-plug__plug-990 | control | needs_investigation | unresolved | 10.6 / 12.85 |
| general-cbic__poolex-59 | otp | needs_investigation | expected_api_compile_failure | 3.18 / 5.29 |
| fika-lang__fika-14 | control | validated | strict_transition_verified | 3.87 / 18.02 |
| kraigie__nostrum-369 | otp | validated | strict_transition_verified | 50.41 / 57.07 |
| fika-lang__fika-34 | control | validated | strict_transition_verified | 3.76 / 5.82 |
| newrelic__elixir_agent-84 | otp | needs_investigation | unresolved | 6.86 / 41.36 |
| mhanberg__temple-243 | control | validated | strict_transition_verified | 10.41 / 7.84 |
| phoenixframework__phoenix-2721 | otp | needs_investigation | unresolved | 5.61 / 6.47 |
| phoenixframework__phoenix-3250 | control | needs_investigation | unresolved | 27.49 / 25.96 |
| plataformatec__broadway-31 | otp | needs_investigation | expected_api_compile_failure | 2.25 / 4.68 |
| ash-project__ash-1853 | control | needs_investigation | unresolved | 104.47 / 123.76 |
| whitfin__cachex-341 | otp | needs_investigation | unresolved | 10.02 / 57.34 |
| woylie__doggo-379 | control | validated | strict_transition_verified | 72.78 / 80.07 |
| commanded__commanded-171 | otp | needs_investigation | unresolved | 12.17 / 11.49 |
| 100phlecs__tailwind_formatter-33 | control | validated | strict_transition_verified | 14.56 / 14.77 |
| commanded__commanded-380 | otp | needs_investigation | unresolved | 36.96 / 31.65 |
| adobe__elixir-styler-155 | control | validated | strict_transition_verified | 8.37 / 7.79 |
| edgurgel__mimic-47 | otp | validated | strict_transition_verified | 4.08 / 3.47 |
| elixir-ecto__ecto-2348 | control | needs_investigation | unresolved | 13.61 / 13.71 |
| elixir-protobuf__protobuf-164 | otp | needs_investigation | unresolved | 16.66 / 16.32 |
| elixir-gettext__gettext-239 | control | needs_investigation | unresolved | 5.56 / 5.08 |
| general-cbic__poolex-127 | otp | needs_investigation | unresolved | 8.1 / 11.44 |
| jeregrine__jsonapi-164 | control | needs_investigation | unresolved | 24.14 / 25.91 |
| livebook-dev__kino-231 | otp | needs_investigation | unresolved | 13.35 / 12.87 |
| keathley__finch-47 | control | validated | strict_transition_verified | 38.72 / 30.71 |
| newrelic__elixir_agent-37 | otp | needs_investigation | unresolved | 33.45 / 32.34 |
| keathley__norm-41 | control | needs_investigation | unresolved | 19.18 / 19.74 |
| plataformatec__broadway-40 | otp | needs_investigation | unresolved | 3.87 / 3.52 |
| kraigie__nostrum-377 | control | validated | strict_transition_verified | 27.63 / 27.05 |
| quantum-elixir__quantum-core-454 | otp | validated | strict_transition_verified | 48.25 / 47.77 |
| phoenixframework__phoenix_html-263 | control | needs_investigation | unresolved | 1.86 / 1.62 |
| whitfin__cachex-292 | otp | needs_investigation | unresolved | 10.06 / 9.92 |
| rrrene__credo-1095 | control | needs_investigation | unresolved | 24.8 / 25.38 |
| whitfin__cachex-294 | otp | needs_investigation | unresolved | 7.93 / 10.46 |
| rrrene__credo-1152 | control | needs_investigation | unresolved | 12.47 / 12.3 |
| whitfin__cachex-343 | otp | needs_investigation | expected_api_compile_failure | 8.54 / 55.19 |
| tallarium__reverse_proxy_plug-177 | control | validated | strict_transition_verified | 39.41 / 43.27 |
| whitfin__cachex-348 | otp | validated | strict_transition_verified | 54.88 / 54.41 |
| woylie__flop_phoenix-221 | control | validated | strict_transition_verified | 39.27 / 40.13 |

Detailed evidence, image IDs and log hashes: validation_summary.json.
Needs investigation is not an agent failure or automatic task exclusion.
