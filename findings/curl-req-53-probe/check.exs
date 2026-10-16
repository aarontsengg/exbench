# Construct requests only; this does not send an HTTP request.
request = CurlReq.from_curl("curl https://example.com")
IO.puts("EXBENCH_OPTION_REGISTERED=#{MapSet.member?(request.registered_options, :receive_timeout)}")

try do
  merged = Req.merge(request, receive_timeout: 15_000)
  value = Req.Request.get_option(merged, :receive_timeout)
  IO.puts("EXBENCH_MERGE_OK=#{value}")
  if value != 15_000, do: System.halt(4)
rescue
  error in ArgumentError ->
    IO.puts("EXBENCH_ARGUMENT_ERROR=#{Exception.message(error)}")
    System.halt(3)
end
