"""Bounded unchanged-assertion repetitions of #171's causation test module."""
import hashlib,json,os,subprocess,tempfile,uuid,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
v=json.loads((ROOT/'evaluation_variants/commanded__commanded-171--historical-fixtures-v2.json').read_text())
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']==v['upstream_instance_id'])
spec=importlib.util.spec_from_file_location('parser',ROOT/v['parser']['path']);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
assert hashlib.sha256((ROOT/v['parser']['path']).read_bytes()).hexdigest()==v['parser']['sha256']
fixture=(ROOT/v['shared_patch']['path']).read_bytes()
assert hashlib.sha256(fixture).hexdigest()==v['shared_patch']['sha256']
out=ROOT/'validation_runs/171-timeout-repeats';out.mkdir(exist_ok=False)
report={'image_id':v['image_id'],'model_calls':0,'assertions_changed':False,'runs':[]}
with tempfile.TemporaryDirectory(prefix='exbench-repeat-') as tmp:
 Path(tmp,'tests.patch').write_text(t['test_patch']);Path(tmp,'fixture.patch').write_bytes(fixture)
 gold=''.join('diff --git '+b for b in t['patch'].split('diff --git ') if b.startswith('a/lib/'))
 Path(tmp,'gold.patch').write_text(gold)
 for phase in ['base','gold']:
  for seed in [42,7,123]:
   name='exbench-repeat-'+uuid.uuid4().hex[:12];marker='EXBENCH_TEST_START_'+uuid.uuid4().hex
   command=f'mix test test/commands/correlation_causation_test.exs --trace --max-cases 1 --seed {seed}'
   lines=['set -e']+(['git apply /patches/gold.patch'] if phase=='gold' else [])+['git apply /patches/tests.patch','git apply /patches/fixture.patch','epmd -daemon','echo '+marker,command]
   log=out/f'{phase}-{seed}.log';run={'phase':phase,'seed':seed,'command':command,'log':str(log.relative_to(ROOT))}
   print(phase,seed,'started',flush=True)
   try:
    with log.open('w') as f:
     p=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','none','-v',tmp+':/patches:ro','-w','/commanded',v['image_id'],'bash','-c','\n'.join(lines)],stdout=f,stderr=subprocess.STDOUT,timeout=180)
    run['exit_code']=p.returncode
    txt=log.read_text();run['tests']=parser.parse(txt.split(marker,1)[1])
   except (subprocess.TimeoutExpired,ValueError,IndexError) as e:run['error']=str(e)
   finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
   run['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();report['runs'].append(run)
   (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
   print(phase,seed,run.get('exit_code'),[r['test'] for r in run.get('tests',[]) if r['status']=='FAILED'],run.get('error',''),flush=True)
report['complete']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'findings/grader/timeout-repeats.json').write_text(json.dumps(report,indent=2)+'\n')
