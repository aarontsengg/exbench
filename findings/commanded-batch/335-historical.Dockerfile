FROM elixir@sha256:cb516ce947492652e06781081f431c68808544e613df141e60574bd7e2ab366b
ENV MIX_ENV=test
WORKDIR /commanded
COPY . .
RUN mix archive.install /commanded/hex.ez --force
RUN mix local.rebar --force
RUN cp mix.lock /tmp/original.mix.lock && mix deps.get && cp mix.lock /tmp/resolved.mix.lock && elixir verify_lock.exs && cp /tmp/original.mix.lock mix.lock
RUN mix deps.compile
