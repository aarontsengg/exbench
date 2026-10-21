"""Compare pinned Cachex tasks/dependencies on the historical CI runtime family."""
import hashlib
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from audit_identities import parse
ROOT = Path(__file__).resolve().parents[2]
D = '/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH'] = str(Path(D).parent) + os.pathsep + os.environ.get('PATH', '')
cli = argparse.ArgumentParser()
cli.add_argument('--output', default='validation_runs/cachex-historical-perf')
args = cli.parse_args()
out = ROOT / args.output
out.mkdir(exist_ok=False)
old = json.loads((ROOT / 'validation_runs/cachex-epmd/report.json').read_text())
runtime = json.loads(subprocess.check_output([D, 'image', 'inspect', 'elixir:1.13.4-otp-24']))[0]
report = {'model_calls': 0, 'runtime_image_id': runtime['Id'], 'runtime_repo_digests': runtime['RepoDigests'], 'platform': 'linux/amd64', 'erl_flags': '+JPperf true', 'complete': False, 'tasks': {}}
sha = lambda b: hashlib.sha256(b).hexdigest()
def save():
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
def checked(cmd, log=None, timeout=600):
    return subprocess.run(cmd, check=True, stdout=log, stderr=subprocess.STDOUT if log else None, timeout=timeout)
def tree_hash(path):
    return {str(p.relative_to(path)): sha(p.read_bytes()) for p in sorted(path.rglob('*')) if p.is_file() and '.git' not in p.parts and '_build' not in p.parts}
for task in json.loads((ROOT / 'validation_inputs/tasks.json').read_text()):
    if task['instance_id'] not in ['whitfin__cachex-292', 'whitfin__cachex-294']: continue
    ident = task['instance_id']; folder = out / ident; folder.mkdir()
    original = next(t for t in old['items'] if t['instance_id'] == ident)
    digest = original['repo_digests'][0]
    print(ident, 'fetching original dependency/source snapshot', flush=True)
    with (folder / 'pull.log').open('w') as log: checked([D, 'pull', '--platform', 'linux/amd64', digest], log)
    image = json.loads(subprocess.check_output([D, 'image', 'inspect', digest]))[0]
    assert image['Id'] == original['image_id']
    container = subprocess.check_output([D, 'create', '--platform', 'linux/amd64', image['Id']]).decode().strip()
    context = folder / 'context'; context.mkdir()
    try:
        checked([D, 'cp', container + ':/cachex/.', str(context)])
    finally:
        checked([D, 'rm', container])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=context).decode().strip()
    assert commit == task['base_commit']
    # Remove only generated build artifacts copied into this new diagnostic directory.
    if (context / '_build').exists(): shutil.rmtree(context / '_build')
    for build in list((context / 'deps').glob('*/_build')):
        shutil.rmtree(build)
    lock_hash = sha((context / 'mix.lock').read_bytes())
    dependency_hashes = tree_hash(context / 'deps')
    (folder / 'dependency-hashes.json').write_text(json.dumps(dependency_hashes, indent=2) + '\n')
    dockerfile = f'''FROM {runtime['RepoDigests'][0]}
ENV MIX_ENV=test
ENV ERL_FLAGS="+JPperf true"
WORKDIR /cachex
COPY . .
RUN mix local.hex --force && mix local.rebar --force
RUN cp mix.lock /tmp/cachex-original.lock && mix deps.compile && cmp mix.lock /tmp/cachex-original.lock
'''
    (context / 'Dockerfile').write_text(dockerfile)
    entry = {'original_image_id': image['Id'], 'base_commit': commit, 'mix_lock_sha256': lock_hash,
             'dependencies_manifest_sha256': sha((folder / 'dependency-hashes.json').read_bytes()),
             'dockerfile': dockerfile, 'patch_sha256': sha(task['patch'].encode()), 'test_patch_sha256': sha(task['test_patch'].encode()), 'runs': {}}
    report['tasks'][ident] = entry; save()
    tag = 'exbench-cachex-' + ident.rsplit('-', 1)[1] + '-historical:v1'
    print(ident, 'building historical image', flush=True)
    with (folder / 'build.log').open('w') as log:
        checked([D, 'build', '--platform', 'linux/amd64', '-t', tag, str(context)], log, 900)
    built = json.loads(subprocess.check_output([D, 'image', 'inspect', tag]))[0]
    entry['image_id'] = built['Id']
    entry['runtime_version'] = subprocess.check_output([D, 'run', '--rm', '--platform', 'linux/amd64', '--network', 'none', built['Id'], 'elixir', '--version']).decode()
    # Check build retained every captured dependency file and lock contents.
    probe = subprocess.check_output([D, 'create', '--platform', 'linux/amd64', built['Id']]).decode().strip()
    try:
        checkdir = folder / 'built-dependencies'; checkdir.mkdir()
        checked([D, 'cp', probe + ':/cachex/deps/.', str(checkdir)])
        checked([D, 'cp', probe + ':/cachex/mix.lock', str(folder / 'built.mix.lock')])
        assert sha((folder / 'built.mix.lock').read_bytes()) == lock_hash
        for p, h in dependency_hashes.items(): assert sha((checkdir / p).read_bytes()) == h, p
    finally: checked([D, 'rm', probe])
    save()
    with tempfile.TemporaryDirectory(prefix='exbench-cachex-') as temp:
        Path(temp, 'gold.patch').write_text(task['patch']); Path(temp, 'tests.patch').write_text(task['test_patch'])
        for seed in [42, 7]:
            for phase in ['base', 'gold']:
                key = f'{seed}-{phase}'; name = 'exbench-cachex-' + uuid.uuid4().hex[:12]
                script = ['set -e']
                if phase == 'gold': script.append('git apply /patches/gold.patch')
                script += ['git apply /patches/tests.patch', 'epmd -daemon', f'mix test --trace --max-cases 1 --seed {seed}']
                print(ident, key, 'started', flush=True)
                start = time.monotonic(); code = None
                try:
                    with (folder / (key + '.log')).open('w') as log:
                        code = subprocess.run([D, 'run', '--rm', '--name', name, '--platform', 'linux/amd64', '--network', 'none', '-v', temp + ':/patches:ro', built['Id'], 'bash', '-c', '\n'.join(script)], stdout=log, stderr=subprocess.STDOUT, timeout=300).returncode
                except subprocess.TimeoutExpired: pass
                finally: subprocess.run([D, 'rm', '-f', name], capture_output=True, timeout=30)
                log = folder / (key + '.log'); result = {'exit_code': code, 'seconds': round(time.monotonic()-start, 2), 'log_sha256': sha(log.read_bytes())}
                try: result['tests'] = parse(log.read_text())
                except ValueError as error: result['parse_error'] = str(error)
                entry['runs'][key] = result; save()
                print(ident, key, 'exit', code, 'failures', [r['test'] for r in result.get('tests', []) if r['status'] != 'PASSED'], flush=True)
report['complete'] = True; save()
(ROOT / 'findings/cachex-cluster/historical-results.json').write_text(json.dumps(report, indent=2) + '\n')
