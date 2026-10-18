FROM elixir@sha256:846a4741100318653895ed1ac8d9fdd102ca7cfce1f6b85d6e1448512a8c613f
ENV MIX_ENV=test
WORKDIR /commanded
COPY . .
RUN mix archive.install /commanded/hex.ez --force
RUN mix local.rebar --force
RUN cp mix.lock /tmp/original.mix.lock && mix deps.get && cmp mix.lock /tmp/original.mix.lock
RUN mix deps.compile
