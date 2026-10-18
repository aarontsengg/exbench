{before, _} = Code.eval_file("/tmp/original.mix.lock")
{after_lock, _} = Code.eval_file("mix.lock")
identity = fn lock -> Enum.into(lock, %{}, fn {key, value} ->
  # Preserve registry, package, exact version, and package checksum.
  {{to_string(key)}, value |> Tuple.to_list() |> Enum.take(4)}
end) end
unless identity.(before) == identity.(after_lock), do: raise("Dependency identity changed")
IO.puts("LOCKED_PACKAGE_IDENTITIES_UNCHANGED")
