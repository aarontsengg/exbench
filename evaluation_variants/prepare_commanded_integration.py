"""Prepare explicit integration candidates; verification status is not inferred."""
import difflib,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
parser='findings/commanded-batch/parse_qualified_historical.py'
sha=lambda b:hashlib.sha256(b).hexdigest()
for n in [139,171,290,335,380]:
 t=next(t for t in tasks if t['instance_id']==f'commanded__commanded-{n}')
 if n in [139,171]:
  q=json.loads((ROOT/'findings/commanded-batch/qualified-results.json').read_text())['tasks'][str(n)]
  rows=q['runs']['42-base']['tests']
 elif n in [290,335]:
  q=json.loads((ROOT/'findings/commanded-batch/remaining-three-fixtures-results.json').read_text())['tasks'][str(n)]
  rows=q['runs']['42-base']['tests']
 else:
  q=json.loads((ROOT/'findings/commanded-batch/remaining-three-results.json').read_text())['tasks'][str(n)]
  rows=q['runs']['42-base']['tests']
 prior=json.loads((ROOT/f'findings/commanded-batch/{n}-historical-result.json').read_text())
 fixture=None
 if n!=380:
  previous={139:'139-fixture-startup-audit-seed42.patch',171:'171-fixture-startup-audit-seed42.patch',290:'290-isolated-pubsub.patch',335:'335-subscription-barrier.patch'}[n]
  content=(ROOT/'findings/commanded-batch'/previous).read_text()
  if n in [139,335]:
   context=ROOT/f'validation_runs/commanded-other-historical-v2/{n}/context'
   with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp);shutil.copytree(context/'test',tmp/'test')
    subprocess.run(['git','apply','-'],cwd=tmp,input=t['test_patch'],text=True,check=True)
    before={str(p.relative_to(tmp)):p.read_text() for p in (tmp/'test').rglob('*') if p.is_file()}
    subprocess.run(['git','apply','-'],cwd=tmp,input=content,text=True,check=True)
    if n==139:
     paths=['test/aggregates/aggregate_lifespan_test.exs','test/commands/routing_commands_test.exs']
     import re
     for p in paths:
      file=tmp/p;s=file.read_text()
      s,count=re.subn(r'assert_raise ArgumentError, "[^"\n]+", fn ->','assert_raise ArgumentError, fn ->',s)
      assert count==(1 if 'lifespan' in p else 2)
      file.write_text(s)
    else:
     file=tmp/'test/event/handle_event_test.exs';s=file.read_text()
     # Both reset tests must publish only after reset completes.
     needle='      send(handler, :reset)\n'
     assert s.count(needle)==2
     s=s.replace(needle,needle+'\n      # Same-sender system request runs after reset/resubscription completes.\n      :sys.get_state(handler)\n')
     file.write_text(s)
    content=''
    for p,a in sorted(before.items()):
     b=(tmp/p).read_text()
     if a!=b:content+=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+p,tofile='b/'+p))
  path=f'evaluation_variants/repairs/commanded-{n}.patch'
  (ROOT/path).write_text(content);fixture={'path':path,'sha256':sha(content.encode())}
 v={'variant_id':t['instance_id']+'--integration-v1','upstream_instance_id':t['instance_id'],'status':'candidate_pending_integration_checks','selected_for_final_sample':False,
 'dataset':json.loads((ROOT/'dataset_config.json').read_text()),'base_commit':t['base_commit'],'image_id':prior['image_id'],
 'platform':'linux/amd64','network':'none','start_epmd':True,'shared_patch':fixture,
 'parser':{'path':parser,'sha256':sha((ROOT/parser).read_bytes()),'identity':['module','test'],'requires_serial_trace':True},
 'test_patch_sha256':sha(t['test_patch'].encode()),'reference_patch_sha256':sha(t['patch'].encode()),'prompt_fields':['problem_statement','interface'],
 'variant_expected':{k:[{'module':r['module'],'test':r['test']} for r in rows if r['status']==status] for k,status in [('FAIL_TO_PASS','FAILED'),('PASS_TO_PASS','PASSED')]},
 'raw_test_count':len(rows),'notes':{139:'Assert documented ArgumentError conditions, not unspecified wording; corrected invalid handler fixture.',171:'Retain prior fixtures; intermittent causation timeout remains under investigation.',290:'Retain isolated PubSub fixture; no assertion changes.',335:'Subscription monitor barrier plus completion barrier after reset; unchanged behavioral assertions.',380:'Historical environment only; unchanged tests.'}[n]}
 (ROOT/'evaluation_variants'/(v['variant_id']+'.json')).write_text(json.dumps(v,indent=2)+'\n')
