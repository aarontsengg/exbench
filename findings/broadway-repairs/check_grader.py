"""Verify Broadway's versioned grader with empty/reference fixes, no models."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ident='plataformatec__broadway-95'
variant='evaluation_variants/'+ident+'--integration-v1.json'
v=json.loads((ROOT/variant).read_text())
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']==ident)
assert hashlib.sha256(t['patch'].encode()).hexdigest()==v['reference_patch_sha256']
out=ROOT/'validation_runs/broadway-grader-v1';out.mkdir(exist_ok=False)
(out/'empty.patch').write_text('');(out/'reference.patch').write_text(t['patch'])
r={'complete':False,'model_calls':0,'variant':variant,'runs':{}}
for seed in [42,7]:
 for phase in ['empty','reference']:
  key=f'{seed}-{phase}';dest=out/key
  print(key,'started',flush=True)
  subprocess.run([sys.executable,str(ROOT/'grade_patch.py'),'--variant',variant,'--patch',str(out/(phase+'.patch')),'--output',str(dest),'--seed',str(seed)],cwd=ROOT,check=True)
  raw=(dest/'result.json').read_bytes();result=json.loads(raw)
  r['runs'][key]={'result':result,'result_sha256':hashlib.sha256(raw).hexdigest()}
  (out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
r['complete']=True
r['integration_passed']=all(x['result']['resolved']==k.endswith('reference') for k,x in r['runs'].items())
for p in [out/'report.json',ROOT/'findings/broadway-repairs/grader-results-v1.json']:
 p.write_text(json.dumps(r,indent=2)+'\n')
