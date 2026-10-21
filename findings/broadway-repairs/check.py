"""Versioned diagnostic repairs for Broadway test wording and exit handling."""
import difflib,hashlib,importlib.util,json,os,subprocess,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
D='/Applications/Docker.app/Contents/Resources/bin/docker';os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
out=ROOT/'validation_runs/broadway-repairs-v1';out.mkdir(exist_ok=False)
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text());old=json.loads((ROOT/'validation_runs/remaining-56/report.json').read_text())
spec=importlib.util.spec_from_file_location('parser',HERE/'parse_trace.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
sha=lambda b:hashlib.sha256(b).hexdigest()
report={'model_calls':0,'complete':False,'test_repairs_version':1,'tasks':{}}
for n in [40,95]:
 ident=f'plataformatec__broadway-{n}';task=next(t for t in tasks if t['instance_id']==ident);prior=next(x for x in old['items'] if x['instance_id']==ident)
 folder=out/str(n);folder.mkdir()
 with tempfile.TemporaryDirectory() as temp:
  temp=Path(temp);p=temp/'test/broadway_test.exs';p.parent.mkdir(parents=True);p.write_bytes((HERE/f'{n}-original-test.exs').read_bytes())
  testdiff=''.join('diff --git '+b for b in task['test_patch'].split('diff --git ')[1:] if b.startswith('a/test/broadway_test.exs '))
  subprocess.run(['git','apply','-'],cwd=temp,input=testdiff,text=True,check=True)
  before=p.read_text();after=before
  wording=f'[error] ** (UndefinedFunctionError) function Unknown.ack/{2 if n==40 else 3} is undefined'
  assert after.count(wording)==2
  after=after.replace(wording,'[error] ** (UndefinedFunctionError)')
  if n==95:
   a,b=after.split('  describe "pipeline without batchers"',1);b,c=b.split('  describe "put_batcher"',1)
   needle='      # We suspend the producer to make sure that it doesn\'t process the messages early on'
   assert b.count(needle)==1
   b=b.replace(needle,'      Process.flag(:trap_exit, true)\n\n'+needle)
   needle='      assert_receive {:ack, _, [%{data: 4}], []}'
   assert b.count(needle)==1
   b=b.replace(needle,needle+'\n      assert_receive {:EXIT, ^broadway, :shutdown}')
   after=a+'  describe "pipeline without batchers"'+b+'  describe "put_batcher"'+c
  repair=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/test/broadway_test.exs',tofile='b/test/broadway_test.exs'))
  (HERE/f'{n}-repair-v1.patch').write_text(repair)
 with (folder/'pull.log').open('w') as log:
  subprocess.run([D,'pull','--platform','linux/amd64',prior['repo_digests'][0]],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
 image=json.loads(subprocess.check_output([D,'image','inspect',prior['repo_digests'][0]]))[0];assert image['Id']==prior['image_id']
 entry={'image_id':image['Id'],'base_commit':task['base_commit'],'repair_sha256':sha(repair.encode()),'patch_sha256':sha(task['patch'].encode()),'test_patch_sha256':sha(task['test_patch'].encode()),'source_test_sha256':sha((HERE/f'{n}-original-test.exs').read_bytes()),'runs':{}};report['tasks'][ident]=entry
 with tempfile.TemporaryDirectory(prefix='exbench-broadway-') as temp:
  Path(temp,'gold.patch').write_text(task['patch']);Path(temp,'tests.patch').write_text(task['test_patch']);Path(temp,'repair.patch').write_text(repair)
  for seed in [42,7]:
   for phase in ['base','gold']:
    key=f'{seed}-{phase}';name='exbench-broadway-'+uuid.uuid4().hex[:10];commands=['set -e',f'test "$(git rev-parse HEAD)" = {task["base_commit"]}']
    if phase=='gold':commands.append('git apply /patches/gold.patch')
    commands+=['git apply /patches/tests.patch','git apply /patches/repair.patch',f'mix test --trace --max-cases 1 --seed {seed}']
    print(n,key,'started',flush=True);code=None;start=time.monotonic()
    try:
     with (folder/(key+'.log')).open('w') as log:
      code=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','host','-e','ERL_FLAGS=+JMsingle true','-v',temp+':/patches:ro','-w','/broadway',image['Id'],'bash','-c','\n'.join(commands)],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
    except subprocess.TimeoutExpired:pass
    finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
    log=(folder/(key+'.log')).read_bytes();r={'exit_code':code,'seconds':round(time.monotonic()-start,2),'log_sha256':sha(log)}
    try:r['tests']=parser.parse(log.decode())
    except ValueError as e:r['parse_error']=str(e)
    entry['runs'][key]=r;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(n,key,code,[r['test'] for r in r.get('tests',[]) if r['status']!='PASSED'],flush=True)
report['complete']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'results-v1.json').write_text(json.dumps(report,indent=2)+'\n')
