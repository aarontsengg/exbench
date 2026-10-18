FROM elixir@sha256:8a3685973e61c536c7bef045b1a32b2783296a004c4f7c8470e57783612677e3
ENV MIX_ENV=test
WORKDIR /commanded
COPY . .
RUN mix archive.install /commanded/hex.ez --force
RUN mix local.rebar --force
RUN cp mix.lock /tmp/original.mix.lock && mix deps.get && cp mix.lock /tmp/resolved.mix.lock && elixir verify_lock.exs && cp /tmp/original.mix.lock mix.lock
RUN mix deps.compile
