"""Bounded historical-runtime diagnostics for the remaining four Commanded tasks."""
import concurrent.futures,hashlib,importlib.util,json,os,re,subprocess,tarfile,time,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
D='/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH']=str(Path(D).parent)+os.pathsep+os.environ.get('PATH','')
SPECS={139:('1.5.3','20.2','0.20.6','1.5.0'),171:('1.5.3','20.2','0.20.6','1.5.0'),290:('1.8.0','21.2','2.0.6','1.8.0'),335:('1.9.4','22.0','2.0.6','1.8.0')}
OUT=ROOT/'validation_runs/commanded-other-historical-v2';OUT.mkdir(parents=True,exist_ok=True)
TASKS=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
spec=importlib.util.spec_from_file_location('old_parser',HERE/'parse_380_historical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,log,timeout=600):
 with log.open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout,check=True)
def download(url,path):
 with urllib.request.urlopen(url,timeout=90) as src:path.write_bytes(src.read())
def prepare_image(version):
 log=OUT/('pull-'+version+'.log');print('pull',version,flush=True)
 run([D,'pull','--platform','linux/amd64','elixir:'+version],log)
 i=json.loads(subprocess.check_output([D,'image','inspect','elixir:'+version],timeout=30))[0]
 return i
images={}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(prepare_image,v):v for v in sorted({v[0] for v in SPECS.values()})}
 for f,v in futures.items():
  try:images[v]=f.result()
  except Exception as e:images[v]={'error':str(e)}
for number,(version,ci_otp,hexversion,hexbuild) in SPECS.items():
 task=next(t for t in TASKS if t['instance_id']==f'commanded__commanded-{number}')
 out=OUT/str(number);out.mkdir(exist_ok=True)
 if (out/'report.json').exists():print('preserving existing',number,flush=True);continue
 report={'instance_id':task['instance_id'],'base_commit':task['base_commit'],'historical_ci_elixir':version,'historical_ci_otp':ci_otp,'platform':'linux/amd64','model_calls':0,'phases':{},'complete':False}
 try:
  image=images[version]
  if 'error' in image:raise RuntimeError(image['error'])
  report['base_image_id']=image['Id'];report['base_repo_digests']=image['RepoDigests']
  source_url=f"https://codeload.github.com/commanded/commanded/tar.gz/{task['base_commit']}"
  download(source_url,out/'source.tar.gz');report['source_url']=source_url;report['source_sha256']=sha(out/'source.tar.gz')
  context=out/'context';context.mkdir(exist_ok=True)
  with tarfile.open(out/'source.tar.gz') as archive:
   for member in archive.getmembers():
    parts=Path(member.name).parts[1:]
    if not parts:continue
    if member.issym() or member.islnk():raise ValueError('Unexpected archive link')
    member.name=str(Path(*parts));archive.extract(member,context,filter='data')
  report['lock_sha256']=sha(context/'mix.lock')
  assert (context/'mix.lock').read_bytes()==(HERE/task['instance_id']/'mix.lock').read_bytes()
  hexurl=f'https://repo.hex.pm/installs/{hexbuild}/hex-{hexversion}.ez'
  download(hexurl,context/'hex.ez');report['hex_url']=hexurl;report['hex_sha256']=sha(context/'hex.ez')
  (context/'verify_lock.exs').write_text('''{before, _} = Code.eval_file("/tmp/original.mix.lock")
{after_lock, _} = Code.eval_file("mix.lock")
identity = fn lock -> Enum.into(lock, %{}, fn {key, value} ->
  # Preserve registry, package, exact version, and package checksum.
  {{to_string(key)}, value |> Tuple.to_list() |> Enum.take(4)}
end) end
unless identity.(before) == identity.(after_lock), do: raise("Dependency identity changed")
IO.puts("LOCKED_PACKAGE_IDENTITIES_UNCHANGED")
''')
  dockerfile=f'''FROM {image['RepoDigests'][0]}
ENV MIX_ENV=test
WORKDIR /commanded
COPY . .
RUN mix archive.install /commanded/hex.ez --force
RUN mix local.rebar --force
RUN cp mix.lock /tmp/original.mix.lock && mix deps.get && cp mix.lock /tmp/resolved.mix.lock && elixir verify_lock.exs && cp /tmp/original.mix.lock mix.lock
RUN mix deps.compile
'''
  (context/'Dockerfile').write_text(dockerfile)
  tag=f'exbench-commanded-{number}-historical:v1'
  print(number,'build',flush=True)
  run([D,'build','--platform','linux/amd64','--progress','plain','-t',tag,str(context)],out/'build.log')
  built=json.loads(subprocess.check_output([D,'image','inspect',tag],timeout=30))[0];report['image_id']=built['Id']
  report['runtime']=subprocess.check_output([D,'run','--rm','--platform','linux/amd64','--network','none',built['Id'],'sh','-c','elixir --version; cat /usr/local/lib/erlang/releases/*/OTP_VERSION'],timeout=60).decode()
  patches=out/'patches';patches.mkdir(exist_ok=True)
  (patches/'gold.patch').write_text(task['patch']);(patches/'tests.patch').write_text(task['test_patch'])
  cmds=task['install_config']['test_cmd'];cmds=[cmds] if isinstance(cmds,str) else cmds
  for phase in ['base','gold']:
   name='exbench-old-'+uuid.uuid4().hex[:12];marker='EXBENCH_TEST_START_'+uuid.uuid4().hex
   lines=['set -e']
   if phase=='gold':lines+=['git apply --recount --ignore-space-change --whitespace=nowarn /patches/gold.patch']
   lines+=['git apply --recount --ignore-space-change --whitespace=nowarn /patches/tests.patch','epmd -daemon','echo '+marker]+cmds
   print(number,phase,'started',flush=True);started=time.monotonic();code=None;timeout=False
   try:
    with (out/(phase+'.log')).open('w') as log:
     try:code=subprocess.run([D,'run','--rm','--name',name,'--platform','linux/amd64','--network','none','-v',str(patches)+':/patches:ro',built['Id'],'bash','-c','\n'.join(lines)],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
     except subprocess.TimeoutExpired:timeout=True
   finally:subprocess.run([D,'rm','-f',name],capture_output=True,timeout=30)
   text=(out/(phase+'.log')).read_text(errors='replace');parsed=m.parse(text.split(marker,1)[1]) if marker in text else {}
   report['phases'][phase]={'exit_code':code,'timed_out':timeout,'test_started':marker in text,'passed':sorted(k for k,v in parsed.items() if v=='PASSED'),'failed':sorted(k for k,v in parsed.items() if v=='FAILED'),'raw_summary':re.findall(r'\d+ tests, \d+ failures?',text),'log_sha256':sha(out/(phase+'.log')),'seconds':round(time.monotonic()-started,2)}
   print(number,phase,code,report['phases'][phase]['raw_summary'],flush=True)
  report['complete']=True
 except Exception as e:
  report['error']=str(e);print(number,'blocked',str(e),flush=True)
 finally:
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
