"""New versions for additional fixture races; preserve integration-v1 evidence."""
import difflib,hashlib,json,re,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
for n in [171,290,335,380]:
 v=json.loads((ROOT/f'evaluation_variants/commanded__commanded-{n}--integration-v1.json').read_text())
 t=next(t for t in tasks if t['instance_id']==v['upstream_instance_id'])
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp)
  context=ROOT/(f'validation_runs/commanded-other-historical-v2/{n}/context/test' if n!=380 else 'validation_runs/commanded-380-historical/context/test')
  shutil.copytree(context,tmp/'test')
  subprocess.run(['git','apply','-'],cwd=tmp,input=t['test_patch'],text=True,check=True)
  before={str(p.relative_to(tmp)):p.read_text() for p in (tmp/'test').rglob('*') if p.is_file()}
  if v.get('shared_patch'):
   subprocess.run(['git','apply','-'],cwd=tmp,input=(ROOT/v['shared_patch']['path']).read_text(),text=True,check=True)
  if n==171:
   file=tmp/'test/subscriptions/subscriptions_test.exs';s=file.read_text();first,rest=s.split('  describe "notify subscribers"',1)
   pattern=r'(:ok = Subscriptions.ack_event\("([^"]+)", :strong, %RecordedEvent\{stream_id: "([^"]+)", stream_version: (\d+)\}\))'
   first,count=re.subn(pattern,lambda m:m[1]+f'\n      assert :ok = Subscriptions.wait_for("{m[3]}", {m[4]}, consistency: ["{m[2]}"])',first)
   assert count==4
   file.write_text(first+'  describe "notify subscribers"'+rest)
  elif n==290:
   file=tmp/'test/process_managers/process_manager_idle_timeout_test.exs';s=file.read_text()
   old='      :ok = ExampleRouter.dispatch(%Stop{aggregate_uuid: aggregate_uuid})\n\n      ref = Process.monitor(instance)'
   assert s.count(old)==2
   s=s.replace(old,'      ref = Process.monitor(instance)\n\n      :ok = ExampleRouter.dispatch(%Stop{aggregate_uuid: aggregate_uuid})')
   file.write_text(s)
  elif n==335:
   file=tmp/'test/event/event_handler_subscription_test.exs';s=file.read_text()
   needle='    assert_receive {:subscribed, ^subscription}\n'
   assert s.count(needle)==1
   s=s.replace(needle,needle+'\n    %{subscription_ref: ref} = :sys.get_state(pid)\n    assert is_reference(ref)\n')
   file.write_text(s)
  else:
   repairs=(ROOT/'evaluation_variants/repairs/commanded-335-v2.patch').read_text()
   subprocess.run(['git','apply','-'],cwd=tmp,input=repairs,text=True,check=True)
  patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),(tmp/p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p,a in sorted(before.items()) if a!=(tmp/p).read_text())
 path=f'evaluation_variants/repairs/commanded-{n}-v2.patch';(ROOT/path).write_text(patch)
 v['variant_id']=v['upstream_instance_id']+'--integration-v2';v['shared_patch']={'path':path,'sha256':hashlib.sha256(patch.encode()).hexdigest()}
 v['notes']+=' '+('Wait for named handler acknowledgement before asserting subscription state; no timeout increases.' if n==171 else ('Install monitor before Stop dispatch to avoid missing normal shutdown.' if n==290 else ('Wait for event-handler subscription monitor before testing shutdown.' if n==335 else 'Synchronize reset completion and subscription monitor setup as in #335.')))
 (ROOT/'evaluation_variants'/(v['variant_id']+'.json')).write_text(json.dumps(v,indent=2)+'\n')
