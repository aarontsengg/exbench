ExUnit.start()
defmodule TerminatorHandshakeTest do
  use ExUnit.Case
  test "trap_exit returns only after exit trapping is enabled" do
    {:ok, pid} = Broadway.Terminator.start_link(producers: [], first: [], last: [])
    :ok = :sys.suspend(pid)
    parent = self()
    caller = Task.async(fn ->
      send(parent, :calling)
      Broadway.Terminator.trap_exit(pid)
    end)
    try do
      assert_receive :calling
      assert Task.yield(caller, 100) == nil
    after
      :sys.resume(pid)
    end
    assert Task.await(caller) == :ok
    assert Process.info(pid, :trap_exit) == {:trap_exit, true}
    GenServer.stop(pid)
  end
end
