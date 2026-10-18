"""Run original task patches/tests in the separately built historical image."""
import hashlib,importlib.util,json,os,subprocess,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
out=ROOT/'validation_runs/commanded-380-historical'
if (out/'report.json').exists():raise SystemExit('Report exists; preserve previous results')
t=next(x for x in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if x['instance_id']=='commanded__commanded-380')
image=json.loads(subprocess.check_output([D,'image','inspect','exbench-commanded-380-historical:v1'],timeout=30))[0]
up=ROOT/'third_party/swe-rebench-v2';lock=json.loads((ROOT/'harness_config.json').read_text())
for f,h in lock['files_sha256'].items():assert hashlib.sha256((up/f).read_bytes()).hexdigest()==h
spec=importlib.util.spec_from_file_location('upstream_eval',up/'scripts/eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
parser=ev.get_parser(t['install_config']['log_parser']);norm=ev._normalize_test_name
report={'instance_id':t['instance_id'],'image_id':image['Id'],'base_image_digest':'sha256:846a4741100318653895ed1ac8d9fdd102ca7cfce1f6b85d6e1448512a8c613f','elixir':'1.10.2','otp':'22.3.2','historical_ci_otp':'22.0','exact_historical_ci_match':False,'platform':'linux/amd64','start_epmd':True,'erl_flags_override':None,'model_calls':0,'phases':{},'harness_revision':lock['revision'],'base_commit':t['base_commit']}
for path in ['source.tar.gz','context/mix.lock','context/hex.ez','context/Dockerfile','build.log']:report[path+'_sha256']=hashlib.sha256((out/path).read_bytes()).hexdigest()
assert (out/'context/mix.lock').read_bytes()==(ROOT/'findings/commanded-batch/commanded__commanded-380/mix.lock').read_bytes()
with tempfile.TemporaryDirectory(prefix='exbench-historical-') as tmp:
 for f,key in [('gold.patch','patch'),('tests.patch','test_patch')]:Path(tmp,f).write_text(t[key])
 for phase in ['base','gold']:
  name='exbench-historical-'+uuid.uuid4().hex[:12];marker='EXBENCH_TEST_START_'+uuid.uuid4().hex
  lines=['set -e']
  if phase=='gold':lines+=['git apply --recount --ignore-space-change --whitespace=nowarn /patches/gold.patch']
  lines+=['git apply --recount --ignore-space-change --whitespace=nowarn /patches/tests.patch','epmd -daemon','elixir --version','echo '+marker]+ev.normalize_command_list(t['install_config']['test_cmd'],'test_cmd',t['instance_id'])
  started=time.monotonic();code=None;timeout=False
  print(phase+' started',flush=True)
  try:
   with (out/(phase+'.log')).open('w') as log:
    try:code=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','none','-v',tmp+':/patches:ro','-w','/commanded',image['Id'],'bash','-c','\n'.join(lines)],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
    except subprocess.TimeoutExpired:timeout=True
  finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
  data=(out/(phase+'.log')).read_bytes();text=data.decode(errors='replace');parsed=parser(text.split(marker,1)[1]) if marker in text else {}
  passed=sorted(norm(k) for k,v in parsed.items() if v=='PASSED');failed=sorted(norm(k) for k,v in parsed.items() if v=='FAILED')
  ftp=set(map(norm,t['FAIL_TO_PASS']));ptp=set(map(norm,t['PASS_TO_PASS']))
  ok=not timeout and marker in text and ((code==0 and set(passed)==ftp|ptp and not failed) if phase=='gold' else code in (1,2) and set(failed)==ftp and set(passed)==ptp)
  report['phases'][phase]={'exit_code':code,'timed_out':timeout,'test_started':marker in text,'strict_ok':ok,'passed':passed,'failed':failed,'seconds':round(time.monotonic()-started,2),'log_sha256':hashlib.sha256(data).hexdigest()}
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(phase,code,len(passed),failed,flush=True)
report['complete']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
