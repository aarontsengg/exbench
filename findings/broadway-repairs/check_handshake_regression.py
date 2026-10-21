"""Versioned production diagnostic: synchronize terminator readiness.

Keeps only v1 test compatibility repairs; no warm-up or trace patches.
"""
import difflib,hashlib,importlib.util,json,os,subprocess,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
sha=lambda b:hashlib.sha256(b).hexdigest()
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']=='plataformatec__broadway-95')
image=json.loads((HERE/'results-v1.json').read_text())['tasks'][t['instance_id']]['image_id']
before=(HERE/'95-terminator.ex').read_text()
after=before.replace('GenServer.cast(terminator, :trap_exit)','GenServer.call(terminator, :trap_exit)').replace('def handle_cast(:trap_exit, state) do','def handle_call(:trap_exit, _from, state) do').replace('    {:noreply, state}\n  end\n\n  @impl true\n  def handle_info','    {:reply, :ok, state}\n  end\n\n  @impl true\n  def handle_info')
assert before!=after and 'def handle_cast(:trap_exit' not in after
repair=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/lib/broadway/terminator.ex',tofile='b/lib/broadway/terminator.ex'))
(HERE/'95-handshake-v1.patch').write_text(repair)
regression='''ExUnit.start()
defmodule TerminatorHandshakeTest do
  use ExUnit.Case
  test "trap_exit returns only after exit trapping is enabled" do
    {:ok, pid} = Broadway.Terminator.start_link([producers: [], first: [], last: []], [])
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
'''
(HERE/'handshake_test_v2.exs').write_text(regression)
out=ROOT/'validation_runs/broadway-handshake-regression-v2';out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('parser',HERE/'parse_trace.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
report={'complete':False,'model_calls':0,'diagnostic_only':True,'image_id':image,'base_commit':t['base_commit'],'runs':{}}
with tempfile.TemporaryDirectory() as temp:
 temp=Path(temp)
 for name,content in [('gold.patch',t['patch']),('tests.patch',t['test_patch']),('fixture.patch',(HERE/'95-repair-v1.patch').read_text()),('handshake.patch',repair),('handshake_test.exs',regression)]: (temp/name).write_text(content)
 report['input_hashes']={p.name:sha(p.read_bytes()) for p in temp.iterdir()}
 cases=[('regression-old',False,False,None),('regression-fixed',True,False,None)]
 for key,fixed,gold,seed in cases:
  name='exbench-handshake-'+uuid.uuid4().hex[:10]
  commands=['set -e',f'test "$(git rev-parse HEAD)" = {t["base_commit"]}']
  if gold:commands+=['git apply /patches/gold.patch']
  if fixed:commands+=['git apply /patches/handshake.patch']
  if seed is None:commands+=['cp /patches/handshake_test.exs test/handshake_test.exs', 'mix test test/handshake_test.exs --trace --max-cases 1 --seed 42']
  else:commands+=['git apply /patches/tests.patch','git apply /patches/fixture.patch',f'mix test --trace --max-cases 1 --seed {seed}']
  code=None;print(key,'started',flush=True)
  try:
   with (out/(key+'.log')).open('w') as log:
    code=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','none','-e','ERL_FLAGS=+JMsingle true','-v',str(temp)+':/patches:ro','-w','/broadway',image,'bash','-c','\n'.join(commands)],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
  except subprocess.TimeoutExpired:pass
  finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
  raw=(out/(key+'.log')).read_bytes();r={'exit_code':code,'log_sha256':sha(raw)}
  try:r['tests']=parser.parse(raw.decode())
  except ValueError as e:r['parse_error']=str(e)
  report['runs'][key]=r;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
  print(key,code,[x['test'] for x in r.get('tests',[]) if x['status']!='PASSED'],flush=True)
report['complete']=True
for p in [out/'report.json',HERE/'handshake-regression-results-v2.json']:p.write_text(json.dumps(report,indent=2)+'\n')
