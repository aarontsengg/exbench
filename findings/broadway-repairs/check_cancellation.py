"""Diagnostic only: establish a working pipeline before testing cancellation.

Preserves v1 evidence and applies the same additional test patch to base/gold.
"""
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOCKER = '/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH'] = str(Path(DOCKER).parent) + os.pathsep + os.environ.get('PATH', '')
sha = lambda data: hashlib.sha256(data).hexdigest()


def main():
    task = next(t for t in json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
                if t['instance_id'] == 'plataformatec__broadway-95')
    previous = json.loads((HERE / 'results-v1.json').read_text())['tasks'][task['instance_id']]
    image = previous['image_id']
    subprocess.run([DOCKER, 'image', 'inspect', image], check=True, capture_output=True, timeout=30)
    out = ROOT / 'validation_runs/broadway-cancellation-v2'
    out.mkdir(exist_ok=False)
    spec = importlib.util.spec_from_file_location('broadway_parser', HERE / 'parse_trace.py')
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    with tempfile.TemporaryDirectory(prefix='exbench-cancellation-') as temporary:
        temp = Path(temporary)
        source = temp / 'test/broadway_test.exs'
        source.parent.mkdir()
        source.write_bytes((HERE / '95-original-test.exs').read_bytes())
        testdiff = ''.join('diff --git ' + block for block in task['test_patch'].split('diff --git ')[1:]
                           if block.startswith('a/test/broadway_test.exs '))
        for patch in [testdiff, (HERE / '95-repair-v1.patch').read_text()]:
            subprocess.run(['git', 'apply', '-'], cwd=temp, input=patch, text=True, check=True)
        before = source.read_text()
        needle = '''    test "shutting down broadway cancels producers and waits for messages sent during cancellation",
         %{broadway: broadway} do
      Process.exit(broadway, :shutdown)'''
        replacement = '''    test "shutting down broadway cancels producers and waits for messages sent during cancellation",
         %{broadway: broadway, producer: producer} do
      # Establish end-to-end readiness without calling the task's new API.
      async_push_messages(producer, [:ready_1, :ready_2, :ready_3, :ready_4])
      assert_receive {:ack, _, [%{data: :ready_1}, %{data: :ready_2},
                               %{data: :ready_3}, %{data: :ready_4}], []}
      Process.exit(broadway, :shutdown)'''
        assert before.count(needle) == 1
        after = before.replace(needle, replacement)
        repair = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                             fromfile='a/test/broadway_test.exs', tofile='b/test/broadway_test.exs'))
        (HERE / '95-readiness-v2.patch').write_text(repair)
        for name, content in [('gold', task['patch']), ('tests', task['test_patch']),
                              ('repair', (HERE / '95-repair-v1.patch').read_text()), ('readiness', repair)]:
            (temp / (name + '.patch')).write_text(content)
        report = {'complete': False, 'model_calls': 0, 'diagnostic_only': True,
                  'image_id': image, 'base_commit': task['base_commit'],
                  'patch_hashes': {p.name: sha(p.read_bytes()) for p in temp.glob('*.patch')}, 'runs': {}}
        for seed in [42, 7]:
            for phase in ['base', 'gold']:
                key = f'{seed}-{phase}'
                name = 'exbench-cancellation-' + uuid.uuid4().hex[:10]
                commands = ['set -e', f'test "$(git rev-parse HEAD)" = {task["base_commit"]}']
                if phase == 'gold':
                    commands.append('git apply /patches/gold.patch')
                commands += ['git apply /patches/tests.patch', 'git apply /patches/repair.patch',
                             'git apply /patches/readiness.patch', f'mix test --trace --max-cases 1 --seed {seed}']
                print(key, 'started', flush=True)
                start = time.monotonic()
                code = None
                try:
                    with (out / (key + '.log')).open('w') as log:
                        code = subprocess.run([DOCKER, 'run', '--rm', '--name', name,
                            '--platform', 'linux/amd64', '--network', 'host', '-e', 'ERL_FLAGS=+JMsingle true',
                            '-v', str(temp) + ':/patches:ro', '-w', '/broadway', image,
                            'bash', '-c', '\n'.join(commands)], stdout=log, stderr=subprocess.STDOUT,
                            timeout=300).returncode
                except subprocess.TimeoutExpired:
                    pass
                finally:
                    subprocess.run([DOCKER, 'rm', '-f', name], capture_output=True, timeout=30)
                log = (out / (key + '.log')).read_bytes()
                result = {'exit_code': code, 'seconds': round(time.monotonic() - start, 2),
                          'log_sha256': sha(log)}
                try:
                    result['tests'] = parser.parse(log.decode())
                except ValueError as error:
                    result['parse_error'] = str(error)
                report['runs'][key] = result
                (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
                print(key, code, [t['test'] for t in result.get('tests', []) if t['status'] != 'PASSED'], flush=True)
        report['complete'] = True
        for path in [out / 'report.json', HERE / 'cancellation-results-v2.json']:
            path.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
