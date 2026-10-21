"""Capture Erlang message/exit traces for #95 incomplete-batch shutdown."""
import difflib,hashlib,json,os,subprocess,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads((HERE/'no-batcher-diagnostic-v2.json').read_text())
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']==v['upstream_instance_id'])
out=ROOT/'validation_runs/broadway-shutdown-trace-v1';out.mkdir(exist_ok=False)
with tempfile.TemporaryDirectory() as temp:
 temp=Path(temp);p=temp/'test/broadway_test.exs';p.parent.mkdir();p.write_bytes((HERE/'95-original-test.exs').read_bytes())
 td=''.join('diff --git '+s for s in t['test_patch'].split('diff --git ')[1:] if s.startswith('a/test/broadway_test.exs '))
 for patch in [td,(ROOT/v['shared_patch']['path']).read_text()]:
  subprocess.run(['git','apply','-'],input=patch,text=True,cwd=temp,check=True)
 before=p.read_text()
 needle='''    test "shutting down broadway waits until all events are processed even on incomplete batches",
         %{broadway: broadway} do
'''
 inject='''      # Diagnostic tracing only; no waits or readiness messages before shutdown.
      {:registered_name, registered} = Process.info(broadway, :registered_name)
      prefix = Atom.to_string(registered) <> "."
      targets = for name <- Process.registered(),
                    name == registered or String.starts_with?(Atom.to_string(name), prefix),
                    pid = Process.whereis(name), do: {name, pid}
      trace_path = System.fetch_env!("EXBENCH_TRACE_FILE")
      {:ok, device} = File.open(trace_path, [:write])
      IO.write(device, "TARGETS " <> inspect([{ :test, self()} | targets], limit: :infinity) <> "\\n")
      tracer = spawn(fn ->
        loop = fn loop ->
          receive do
            {:finish, caller} -> File.close(device); send(caller, :trace_saved)
            event ->
              IO.write(device, inspect(event, limit: :infinity, printable_limit: :infinity, width: :infinity) <> "\\n")
              loop.(loop)
          end
        end
        loop.(loop)
      end)
      traced = [self() | Enum.map(targets, &elem(&1, 1))]
      Enum.each(traced, &:erlang.trace(&1, true, [:send, :receive, :procs, :monotonic_timestamp, {:tracer, tracer}]))
      on_exit(fn ->
        Enum.each(traced, fn pid ->
          if Process.alive?(pid), do: :erlang.trace(pid, false, [:all])
        end)
        delivered = :erlang.trace_delivered(:all)
        receive do {:trace_delivered, :all, ^delivered} -> :ok end
        send(tracer, {:finish, self()})
        receive do :trace_saved -> :ok after 5000 -> raise "trace flush failed" end
      end)
'''
 assert before.count(needle)==1
 after=before.replace(needle,needle+inject)
 diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/test/broadway_test.exs',tofile='b/test/broadway_test.exs'))
 (HERE/'95-trace-only.patch').write_text(diff)
 for name,content in [('gold',t['patch']),('tests',t['test_patch']),('fixture',(ROOT/v['shared_patch']['path']).read_text()),('trace',diff)]:
  (temp/(name+'.patch')).write_text(content)
 report={'complete':False,'model_calls':0,'image_id':v['image_id'],'base_commit':t['base_commit'],'patch_hashes':{p.name:sha(p.read_bytes()) for p in temp.glob('*.patch')},'runs':{}}
 for run in range(1,4):
  name='exbench-trace-'+uuid.uuid4().hex[:10];folder=out/str(run);folder.mkdir()
  cmds=['set -e',f'test "$(git rev-parse HEAD)" = {t["base_commit"]}']+['git apply /patches/'+n+'.patch' for n in ['gold','tests','fixture','trace']]+['epmd -daemon','mix test --trace --max-cases 1 --seed 42']
  print('trace run',run,'started',flush=True)
  code=None
  try:
   with (folder/'test.log').open('w') as log:
    code=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','none','-e','ERL_FLAGS=+JMsingle true','-e','EXBENCH_TRACE_FILE=/evidence/events.log','-v',str(temp)+':/patches:ro','-v',str(folder)+':/evidence','-w','/broadway',v['image_id'],'bash','-c','\n'.join(cmds)],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
  except subprocess.TimeoutExpired:pass
  finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
  report['runs'][str(run)]={'exit_code':code,'files':{p.name:sha(p.read_bytes()) for p in folder.iterdir()}}
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(run,code,flush=True)
 report['complete']=True
 for path in [out/'report.json',HERE/'trace-results-v1.json']:path.write_text(json.dumps(report,indent=2)+'\n')
