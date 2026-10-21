"""Reparse all saved Broadway logs including doctests; preserve original reports."""
import hashlib,json
from pathlib import Path
from parse_trace import parse
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
source=json.loads((HERE/'results-v1.json').read_text());assert source['complete']
result={'model_calls':0,'sample_changed':False,'tasks':{}}
for ident,t in source['tasks'].items():
 n=ident.rsplit('-',1)[1];runs={}
 for key,r in t['runs'].items():
  path=ROOT/f'validation_runs/broadway-repairs-v1/{n}/{key}.log';b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==r['log_sha256']
  rows=parse(b.decode());runs[key]={'exit_code':r['exit_code'],'tests':rows,'log_sha256':r['log_sha256']}
  print(ident,key,len(rows),'tests including doctests;',sum(x['status']=='FAILED' for x in rows),'failures')
 result['tasks'][ident]={'runs':runs,'image_id':t['image_id'],'repair_sha256':t['repair_sha256']}
result['source_report_sha256']=hashlib.sha256((HERE/'results-v1.json').read_bytes()).hexdigest()
(HERE/'qualified-results-v1.json').write_text(json.dumps(result,indent=2)+'\n')
