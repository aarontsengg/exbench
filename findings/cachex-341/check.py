"""Repeat unchanged #341 suites on the original immutable image; no model calls."""
import hashlib, importlib.util, json, os, subprocess, tempfile, time, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
out=ROOT/'validation_runs/cachex-341-repeat';out.mkdir(exist_ok=False)
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']=='whitfin__cachex-341')
old=next(x for x in json.loads((ROOT/'validation_runs/remaining-56/report.json').read_text())['items'] if x['instance_id']==t['instance_id'])
spec=importlib.util.spec_from_file_location('parser',ROOT/'findings/cachex-cluster/audit_identities.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
sha=lambda b:hashlib.sha256(b).hexdigest()
with (out/'pull.log').open('w') as log:
 subprocess.run([D,'pull','--platform','linux/amd64',old['repo_digests'][0]],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
image=json.loads(subprocess.check_output([D,'image','inspect',old['repo_digests'][0]]))[0]
assert image['Id']==old['image_id']
report={'task':t['instance_id'],'image_id':image['Id'],'model_calls':0,'complete':False,'erl_flags':'+JMsingle true','network':'host','start_epmd':False,'runs':{},'source':{k:t[k] for k in ['base_commit','problem_statement','interface']},'patch_hashes':{k:sha(t[k].encode()) for k in ['patch','test_patch']}}
with tempfile.TemporaryDirectory(prefix='exbench-cachex341-') as temp:
 Path(temp,'gold.patch').write_text(t['patch']);Path(temp,'tests.patch').write_text(t['test_patch'])
 for seed in [42,7]:
  for phase in ['base','gold']:
   key=f'{seed}-{phase}';name='exbench-cachex341-'+uuid.uuid4().hex[:10]
   commands=['set -e',f'test "$(git rev-parse HEAD)" = {t["base_commit"]}']
   if phase=='gold':commands.append('git apply /patches/gold.patch')
   commands+=['git apply /patches/tests.patch',f'mix test --trace --max-cases 1 --seed {seed}']
   print(key,'started',flush=True);code=None;start=time.monotonic()
   try:
    with (out/(key+'.log')).open('w') as log:
     code=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','host','-e','ERL_FLAGS=+JMsingle true','-v',temp+':/patches:ro','-w','/cachex',image['Id'],'bash','-c','\n'.join(commands)],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
   except subprocess.TimeoutExpired:pass
   finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
   data=(out/(key+'.log')).read_bytes();r={'exit_code':code,'log_sha256':sha(data),'seconds':round(time.monotonic()-start,2)}
   try:r['tests']=parser.parse(data.decode())
   except ValueError as e:r['parse_error']=str(e)
   report['runs'][key]=r
   (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
   print(key,code,[x['test'] for x in r.get('tests',[]) if x['status']!='PASSED'],flush=True)
report['complete']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'findings/cachex-341/repeat-results.json').write_text(json.dumps(report,indent=2)+'\n')
