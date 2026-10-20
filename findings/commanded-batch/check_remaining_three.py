"""Repeat remaining Commanded historical tasks with qualified test identities."""
import argparse,hashlib,json,os,subprocess,tempfile,uuid
from pathlib import Path
from parse_qualified_historical import parse
ROOT=Path(__file__).resolve().parents[2]
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
cli=argparse.ArgumentParser();cli.add_argument('--fixtures',action='store_true');args=cli.parse_args()
suffix='-fixtures' if args.fixtures else ''
out=ROOT/('validation_runs/commanded-remaining-three'+suffix);out.mkdir(exist_ok=False)
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
report={'model_calls':0,'production_repairs':False,'fixture_repairs':args.fixtures,'tasks':{},'parser_sha256':hashlib.sha256(Path(__file__).with_name('parse_qualified_historical.py').read_bytes()).hexdigest()}
for number in ([290,335] if args.fixtures else [290,335,380]):
 task=next(t for t in tasks if t['instance_id']==f'commanded__commanded-{number}')
 prior=json.loads((ROOT/f'findings/commanded-batch/{number}-historical-result.json').read_text())
 image=prior['image_id']
 item={'base_commit':task['base_commit'],'image_id':image,'test_patch_sha256':hashlib.sha256(task['test_patch'].encode()).hexdigest(),'reference_patch_sha256':hashlib.sha256(task['patch'].encode()).hexdigest(),'runs':{}}
 report['tasks'][str(number)]=item
 with tempfile.TemporaryDirectory(prefix='exbench-three-') as tmp:
  Path(tmp,'gold.patch').write_text(task['patch']);Path(tmp,'tests.patch').write_text(task['test_patch'])
  if args.fixtures:
   fixture=ROOT/('findings/commanded-batch/290-isolated-pubsub.patch' if number==290 else 'findings/commanded-batch/335-subscription-barrier.patch')
   Path(tmp,'fixture.patch').write_bytes(fixture.read_bytes())
   item['fixture']={'path':str(fixture.relative_to(ROOT)),'sha256':hashlib.sha256(fixture.read_bytes()).hexdigest()}
  for seed in [42,7]:
   for phase in ['base','gold']:
    name='exbench-three-'+uuid.uuid4().hex[:12];marker='EXBENCH_TEST_START_'+uuid.uuid4().hex
    command=f'mix test --trace --include distributed --max-cases 1 --seed {seed}'
    lines=['set -e']+(['git apply --recount --ignore-space-change --whitespace=nowarn /patches/gold.patch'] if phase=='gold' else [])+['git apply --recount --ignore-space-change --whitespace=nowarn /patches/tests.patch','epmd -daemon','echo '+marker,command]
    if args.fixtures:lines.insert(-3,'git apply /patches/fixture.patch')
    log=out/f'{number}-{seed}-{phase}.log';run={'command':command,'log':str(log.relative_to(ROOT))}
    print(number,seed,phase,'started',flush=True)
    try:
     with log.open('w') as f:
      p=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','none','-v',tmp+':/patches:ro','-w','/commanded',image,'bash','-c','\n'.join(lines)],stdout=f,stderr=subprocess.STDOUT,timeout=300)
     run['exit_code']=p.returncode
     text=log.read_text();run['tests']=parse(text.split(marker,1)[1])
    except (subprocess.TimeoutExpired,ValueError,IndexError) as e:run['error']=str(e)
    finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
    run['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();item['runs'][f'{seed}-{phase}']=run
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(number,seed,phase,run.get('exit_code'),'tests',len(run.get('tests',[])),'failures',[r['test'] for r in run.get('tests',[]) if r['status']=='FAILED'],'error',run.get('error',''),flush=True)
report['complete']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/('findings/commanded-batch/remaining-three'+suffix+'-results.json')).write_text(json.dumps(report,indent=2)+'\n')
