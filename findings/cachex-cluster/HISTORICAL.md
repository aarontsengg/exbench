# Cachex historical-runtime comparison — 20 October 2026

Both tasks pass their full reference suites at seeds 42 and 7 without changing
production code, test assertions, or timeout tolerances.

| Task | Original code, both seeds | Reference fix, both seeds |
| --- | --- | --- |
| #292 | 194 tests; courier error-handling test fails | 194 tests; zero failures |
| #294 | Compilation fails on missing warmer `async` field | 195 tests; zero failures |

## Environment and controls

Used Elixir 1.13.4 / OTP 24 (ERTS 12.3.2.17), matching the major/minor runtime
family in the pinned repository CI. This does not claim the exact patch version
used in a historical CI run. Runtime base digest:
`sha256:b2dd884afe7e49dc75e3ed58d3cf07ee4a1f201e6c2a3af860d6817de8de46e3`.

For each task, copied source and dependencies from the original benchmark image
by immutable digest and checked the source HEAD against the pinned base commit.
Recompiled dependencies under the historical runtime without resolving newer
versions. Verified all captured dependency file hashes and the unchanged lockfile
after the build. Both tasks have lockfile SHA-256
`742c85779e39fd83904ed72a1d6d6363cbbbe3f39e62bc328d0a3e26f4ef4c2d`.
Generated build artifacts were removed only from newly copied diagnostic contexts.

Tests run in fresh linux/amd64 containers with networking disabled, epmd started,
serial trace output and explicit seeds. The original reference and test patches
are applied unchanged. No compatibility changes to library or test code were
added. The module-qualified parser recovers every raw test identity.

## Emulation caveat and failed builds

The first image build segfaulted before running tests. A retry using the modern
run's `+JMsingle true` flag failed because OTP 24 does not recognize it. Both logs
are preserved under `validation_runs/cachex-historical/` and
`validation_runs/cachex-historical-jit/`.

A runtime-only probe succeeded with `+JPperf true`; the final build and tests use
that flag. OTP 24 documents this profiling option in its
[runtime manual](https://www2.erlang.org/documentation/doc-12.1/erts-12.1/doc/pdf/erts-12.1.pdf).
It differs from the modern runs' `+JMsingle true`. Together with the different
runtime/build tools and explicitly controlled test ordering, this means the
comparison supports environment sensitivity, not attribution to one exact VM
change. Tests still run under emulation, not native amd64 hardware.

## Interpretation

The fixed-memory-size assertions and TTL assertion pass in this environment;
their earlier failures remain valid observations. Two successful seeds are not
proof that a timing-sensitive suite can never flake.

#292 now has a reproducible original/reference behavioral transition under this
versioned environment. #294 has an explained missing-API compilation failure:
the supplied interface explicitly requires `async`. It is a candidate for the
separate expected-API category, not an observed set of individual baseline test
failures. Neither result automatically changes upstream validation totals,
sample membership, policy entries, or the agent grader.

## Evidence and reproduction

- `historical-results.json`: image identities, source/patch/dependency hashes,
  Dockerfiles, runtime output, full qualified results and log hashes.
- `historical-summary.json`: checked outcomes and build-log hashes.
- `run_historical.py`: builds and runs the comparison; requires Docker/network
  access for setup and a new output directory. The retained original/historical
  images allow follow-up work without repeated downloads.
- `verify_historical.py`: verifies saved logs, dependency-manifest and lock hashes,
  exact expected outcomes, raw counts and identical gold inventories across seeds.

Raw logs and copied dependencies remain ignored under
`validation_runs/cachex-historical-perf/`. No model calls, commits, or pushes.

Next: register separately named Cachex evaluation variants and integrate them
into the patch grader, preserving #294's different baseline category.
