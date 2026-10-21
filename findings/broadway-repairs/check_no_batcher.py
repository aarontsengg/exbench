"""Compare a readiness fixture for no-batcher shutdown; no scoring promotion."""
import difflib,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads((ROOT/'evaluation_variants/plataformatec__broadway-95--integration-v1.json').read_text())
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']==v['upstream_instance_id'])
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)/'test/broadway_test.exs';p.parent.mkdir();p.write_bytes((HERE/'95-original-test.exs').read_bytes())
 td=''.join('diff --git '+s for s in t['test_patch'].split('diff --git ')[1:] if s.startswith('a/test/broadway_test.exs '))
 subprocess.run(['git','apply','-'],input=td,text=True,cwd=temp,check=True);before=p.read_text()
 subprocess.run(['git','apply','-'],input=(ROOT/v['shared_patch']['path']).read_text(),text=True,cwd=temp,check=True)
 a,b=p.read_text().split('  describe "pipeline without batchers"',1);b,c=b.split('  describe "put_batcher"',1)
 needle='      Process.flag(:trap_exit, true)\n'
 assert b.count(needle)==1
 b=b.replace(needle,needle+'\n      async_push_messages(producer, [:ready_before_suspend])\n      assert_receive {:ack, _, [%{data: :ready_before_suspend}], []}\n')
 after=a+'  describe "pipeline without batchers"'+b+'  describe "put_batcher"'+c
 patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/test/broadway_test.exs',tofile='b/test/broadway_test.exs'))
pp=HERE/'95-no-batcher-readiness-v2.patch';pp.write_text(patch)
v.update(variant_id='plataformatec__broadway-95--no-batcher-diagnostic-v2',status='diagnostic_only',shared_patch={'path':str(pp.relative_to(ROOT)),'sha256':sha(pp.read_bytes())})
vp=HERE/'no-batcher-diagnostic-v2.json';vp.write_text(json.dumps(v,indent=2)+'\n')
out=ROOT/'validation_runs/broadway-no-batcher-v2';out.mkdir(exist_ok=False)
(out/'empty.patch').write_text('');(out/'reference.patch').write_text(t['patch'])
r={'complete':False,'model_calls':0,'variant_sha256':sha(vp.read_bytes()),'runs':{}}
for seed in [42,7]:
 for phase in ['empty','reference']:
  key=f'{seed}-{phase}';dest=out/key;print(key,'started',flush=True)
  subprocess.run([sys.executable,str(ROOT/'grade_patch.py'),'--variant',str(vp.relative_to(ROOT)),'--patch',str(out/(phase+'.patch')),'--output',str(dest),'--seed',str(seed)],cwd=ROOT,check=True)
  raw=(dest/'result.json').read_bytes();r['runs'][key]={'result':json.loads(raw),'result_sha256':sha(raw)}
  (out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
r['complete']=True
for p in [out/'report.json',HERE/'no-batcher-results-v2.json']:p.write_text(json.dumps(r,indent=2)+'\n')
