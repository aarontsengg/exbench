FROM elixir@sha256:5e30eddef98da6e9009006c09d6c119b6973c1d40c4d9584ec13e785ae6ce439
ENV MIX_ENV=test
WORKDIR /commanded
COPY . .
RUN mix archive.install /commanded/hex.ez --force
RUN mix local.rebar --force
RUN cp mix.lock /tmp/original.mix.lock && mix deps.get && cp mix.lock /tmp/resolved.mix.lock && elixir verify_lock.exs && cp /tmp/original.mix.lock mix.lock
RUN mix deps.compile
