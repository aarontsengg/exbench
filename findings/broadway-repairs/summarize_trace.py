"""Save compact, line-addressable trace evidence without changing raw logs."""
import hashlib,importlib.util,json,re
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
spec=importlib.util.spec_from_file_location('parser',H/'parse_trace.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
report={'model_calls':0,'runs':{},'caution':'Trace receive events do not prove callback completion. No production repair applied.'}
for n in [1,2,3]:
 p=R/f'validation_runs/broadway-shutdown-trace-v3/{n}'
 rows=parser.parse((p/'test.log').read_text());events=(p/'events.log').read_text().splitlines()
 report['runs'][str(n)]={'tests':len(rows),'failed':[x for x in rows if x['status']!='PASSED'],'trace_sha256':hashlib.sha256((p/'events.log').read_bytes()).hexdigest(),'test_log_sha256':hashlib.sha256((p/'test.log').read_bytes()).hexdigest()}
 if n==2:
  chosen=[(i+1,s) for i,s in enumerate(events) if ':trap_exit' in s or ('#PID<0.1566.0>' in s and any(k in s for k in [':register,',':exit,'])) or (':ack,' in s and ':send,' in s and ':test_finished' not in s)]
  report['failure_excerpt']=[{'line':i,'event':s} for i,s in chosen]
  report['failure_drain_signal_count']=sum(':prepare_for_draining' in s or ':never_resubscribe' in s or ':cancel_consumers' in s for s in events)
for name in ['95-server.ex','95-terminator.ex']:
 report[name+'_sha256']=hashlib.sha256((H/name).read_bytes()).hexdigest()
(H/'trace-analysis-v3.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:{'tests':v['tests'],'failures':len(v['failed'])} for k,v in report['runs'].items()}))
