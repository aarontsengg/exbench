"""Isolated issue reproduction, not a replacement benchmark test."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DOCKER = '/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH'] = str(Path(DOCKER).parent) + os.pathsep + os.environ.get('PATH', '')
task = next(t for t in json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
            if t['instance_id'] == 'derekkraan__curl_req-53')
prior = json.loads((ROOT / 'findings/curl-req-53-diagnostic.json').read_text())
expected_image = prior['items'][0]['image_id']
out = ROOT / 'validation_runs/curl-req-53-issue-probe'
out.mkdir(parents=True, exist_ok=False)
report = {'instance_id': task['instance_id'], 'model_calls': 0,
          'test_patch_applied': False, 'setup_patch_applied': False,
          'erl_flags': '+JMsingle true', 'phases': {},
          'probe_sha256': hashlib.sha256((HERE / 'check.exs').read_bytes()).hexdigest()}
pulled = False
try:
    available = subprocess.run([DOCKER, 'image', 'inspect', task['image_name']], capture_output=True, timeout=30)
    if available.returncode:
        print('Downloading task image', flush=True)
        with (out / 'pull.log').open('w') as log:
            subprocess.run([DOCKER, 'pull', '--platform', 'linux/amd64', task['image_name']],
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=600)
        pulled = True
    image = json.loads(subprocess.check_output([DOCKER, 'image', 'inspect', task['image_name']], timeout=30))[0]
    assert image['Id'] == expected_image, 'Image differs from prior diagnostic'
    report['image_id'] = image['Id']
    report['repo_digests'] = image['RepoDigests']
    report['base_commit'] = task['base_commit']
    report['reference_patch_sha256'] = hashlib.sha256(task['patch'].encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='exbench-curl-probe-') as tmp:
        Path(tmp, 'gold.patch').write_text(task['patch'])
        Path(tmp, 'check.exs').write_bytes((HERE / 'check.exs').read_bytes())
        for phase in ('base', 'gold'):
            name = 'exbench-probe-' + uuid.uuid4().hex[:16]
            script = ['set -e', f'test "$(git rev-parse HEAD)" = {task["base_commit"]}', 'git reset --hard HEAD']
            if phase == 'gold':
                script.append('git apply --recount --ignore-space-change --whitespace=nowarn /probe/gold.patch')
            script.append('MIX_ENV=dev mix run /probe/check.exs')
            print(phase + ' probe started', flush=True)
            try:
                with (out / (phase + '.log')).open('w') as log:
                    result = subprocess.run([DOCKER, 'run', '--rm', '--name', name,
                        '--platform', 'linux/amd64', '--network', 'none',
                        '-e', 'ERL_FLAGS=+JMsingle true', '-v', tmp + ':/probe:ro',
                        '-w', '/curl_req', image['Id'], '/bin/bash', '-c', '\n'.join(script)],
                        stdout=log, stderr=subprocess.STDOUT, timeout=300)
            finally:
                subprocess.run([DOCKER, 'rm', '-f', name], capture_output=True, timeout=30)
            data = (out / (phase + '.log')).read_bytes()
            markers = [line for line in data.decode(errors='replace').splitlines() if line.startswith('EXBENCH_')]
            report['phases'][phase] = {'exit_code': result.returncode, 'markers': markers,
                'log_sha256': hashlib.sha256(data).hexdigest()}
            print(phase, result.returncode, markers, flush=True)
finally:
    if pulled:
        cleanup = subprocess.run([DOCKER, 'image', 'rm', task['image_name']], capture_output=True, timeout=60)
        report['image_release_exit_code'] = cleanup.returncode
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
