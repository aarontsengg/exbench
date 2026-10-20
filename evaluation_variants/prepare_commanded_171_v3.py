"""Isolate both #171 adapter fixtures after a reproduced local-registry collision."""
import difflib,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v=json.loads((ROOT/'evaluation_variants/commanded__commanded-171--integration-v2.json').read_text())
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']==v['upstream_instance_id'])
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);shutil.copytree(ROOT/'validation_runs/commanded-other-historical-v2/171/context/test',tmp/'test')
 subprocess.run(['git','apply','-'],cwd=tmp,input=t['test_patch'],text=True,check=True)
 before={str(p.relative_to(tmp)):p.read_text() for p in (tmp/'test').rglob('*') if p.is_file()}
 subprocess.run(['git','apply','-'],cwd=tmp,input=(ROOT/v['shared_patch']['path']).read_text(),text=True,check=True)
 for kind in ['local','phoenix']:
  file=tmp/f'test/pubsub/{kind}_pubsub_test.exs';s=file.read_text()
  assert s.count('  setup do\n')==1
  s=s.replace('  setup do\n','  setup do\n    Application.stop(:commanded)\n')
  if kind=='local':
   s=s.replace('{:ok, _pid} = Supervisor.start_link','{:ok, pid} = Supervisor.start_link')
   s=s.replace('    on_exit(fn ->','    Process.unlink(pid)\n\n    on_exit(fn ->\n      Supervisor.stop(pid)')
  file.write_text(s)
 file=tmp/'test/subscriptions/subscriptions_test.exs';s=file.read_text()
 needle='    {:ok, _} = Application.ensure_all_started(:commanded)'
 assert s.count(needle)==1
 s=s.replace(needle,'    Application.stop(:commanded)\n'+needle)
 file.write_text(s)
 patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),(tmp/p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p,a in sorted(before.items()) if a!=(tmp/p).read_text())
p='evaluation_variants/repairs/commanded-171-v3.patch';(ROOT/p).write_text(patch)
v['variant_id']='commanded__commanded-171--integration-v3';v['shared_patch']={'path':p,'sha256':hashlib.sha256(patch.encode()).hexdigest()};v['notes']+=' Isolate both local and Phoenix PubSub test supervisors and synchronously clean up both.'
(ROOT/'evaluation_variants'/(v['variant_id']+'.json')).write_text(json.dumps(v,indent=2)+'\n')
