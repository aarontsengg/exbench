"""Local empty/reference integration checks for all five Commanded variants."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
cli=argparse.ArgumentParser();cli.add_argument('--followups',action='store_true');cli.add_argument('--final-171',action='store_true');cli.add_argument('--final-380',action='store_true');args=cli.parse_args()
suffix='-final-171' if args.final_171 else ('-followups' if args.followups else '')
if args.final_380: suffix='-final-380'
version='v3' if args.final_171 else ('v2' if args.followups else 'v1')
if args.final_380: version='v3'
out=ROOT/('validation_runs/all-commanded-integration'+suffix);out.mkdir(exist_ok=False)
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
report={'model_calls':0,'tasks':{}}
for n in ([380] if args.final_380 else ([171] if args.final_171 else ([171,290,335,380] if args.followups else [139,171,290,335,380]))):
 t=next(t for t in tasks if t['instance_id']==f'commanded__commanded-{n}')
 folder=out/str(n);folder.mkdir()
 (folder/'empty.patch').write_text('')
 (folder/'reference.patch').write_text(''.join('diff --git '+b for b in t['patch'].split('diff --git ') if b.startswith('a/lib/')))
 runs={};report['tasks'][str(n)]=runs
 for seed in [42,7]:
  for phase in ['empty','reference']:
   target=folder/f'{seed}-{phase}'
   print(n,seed,phase,'started',flush=True)
   subprocess.run([sys.executable,str(ROOT/'grade_patch.py'),'--variant',f'evaluation_variants/commanded__commanded-{n}--integration-{version}.json','--seed',str(seed),'--patch',str(folder/(phase+'.patch')),'--output',str(target)],cwd=ROOT,check=True)
   data=(target/'result.json').read_bytes();r=json.loads(data)
   runs[f'{seed}-{phase}']={'path':str((target/'result.json').relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'result':r}
   (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
report['complete']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/('findings/grader/all-commanded-integration'+suffix+'.json')).write_text(json.dumps(report,indent=2)+'\n')
