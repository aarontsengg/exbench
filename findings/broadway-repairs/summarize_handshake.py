"""Verify suite inventories and normalize singular standalone-test summaries."""
import hashlib,importlib.util,json,re
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=importlib.util.spec_from_file_location('parser',H/'parse_trace.py');parser=importlib.util.module_from_spec(s);s.loader.exec_module(parser)
r=json.loads((H/'handshake-results-v2.json').read_text());assert r['complete']
summary={'complete':True,'model_calls':0,'evidence_sha256':hashlib.sha256((H/'handshake-results-v2.json').read_bytes()).hexdigest(),'runs':{}}
for key,item in r['runs'].items():
 log=(R/'validation_runs/broadway-handshake-v2'/(key+'.log')).read_bytes()
 assert hashlib.sha256(log).hexdigest()==item['log_sha256']
 text=log.decode()
 text=re.sub(r'^1 test, (\d+) failures?$',r'1 tests, \1 failures',text,flags=re.M)
 rows=parser.parse(text)
 failures=[x for x in rows if x['status']!='PASSED']
 summary['runs'][key]={'exit_code':item['exit_code'],'total':len(rows),'failures':failures,'log_sha256':item['log_sha256']}
 if key.startswith('regression'):
  assert len(rows)==1
  assert len(failures)==(1 if key.endswith('old') else 0)
 else:
  assert len(rows)==101
  assert len(failures)==(19 if key.endswith('base') else 0)
  assert item['exit_code']==(2 if key.endswith('base') else 0)
base=[r['runs'][f'{seed}-base']['tests'] for seed in [42,7,123]]
assert base[0]==base[1]==base[2]
(H/'handshake-summary-v2.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified: regression fails before / passes after; 3 identical 19-failure baselines; 3 references pass 101 checks.')
