"""Compare unchanged vs explicit application startup, with identical seed/images."""
import argparse, difflib, hashlib, json, os, re, subprocess, tempfile, uuid
from pathlib import Path
from parse_380_historical import parse
ROOT = Path(__file__).resolve().parents[2]
D = '/Applications/Docker.app/Contents/Resources/bin/docker'
os.environ['PATH'] = str(Path(D).parent) + os.pathsep + os.environ.get('PATH', '')
args = argparse.ArgumentParser()
args.add_argument('--cleanup-only', action='store_true')
args.add_argument('--audited', action='store_true')
args.add_argument('--seed', type=int, default=42)
args = args.parse_args()
if args.cleanup_only and args.audited:
    raise SystemExit('Choose cleanup-only or audited')
suffix = f'-audit-seed{args.seed}' if args.audited else ('-cleanup' if args.cleanup_only else '')
if args.seed != 42 and not args.audited:
    raise SystemExit('Non-default seeds require --audited')
test_command = f'mix test --trace --max-cases 1 --seed {args.seed}'
OUT = ROOT / ('validation_runs/commanded-fixture-diagnostic' + suffix)
OUT.mkdir(exist_ok=True)
if (OUT / 'report.json').exists():
    raise SystemExit('Preserving existing report; choose another output directory')
tasks = json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
report = {'test_command': test_command, 'seed': args.seed, 'model_calls': 0, 'diagnostic_only': True, 'tasks': {}}
for number in ([171] if args.cleanup_only else [139, 171]):
    task = next(t for t in tasks if t['instance_id'] == f'commanded__commanded-{number}')
    previous = json.loads((ROOT / f'findings/commanded-batch/{number}-historical-result.json').read_text())
    image = previous['image_id']
    subprocess.run([D, 'image', 'inspect', image], check=True, stdout=subprocess.DEVNULL, timeout=30)
    context = ROOT / f'validation_runs/commanded-other-historical-v2/{number}/context'
    paths = ['test/subscriptions/subscriptions_test.exs']
    if number == 139:
        paths.append('test/pubsub/local_pubsub_test.exs')
    patch = ''
    for path in paths:
        before = (context / path).read_text()
        needle = '    Subscriptions.reset()' if 'subscriptions_test' in path else '    Application.put_env(:commanded, :pubsub, :local)'
        replacement = ('    {:ok, _} = Application.ensure_all_started(:commanded)\n' + needle) if 'subscriptions_test' in path else (needle + '\n    {:ok, _} = Application.ensure_all_started(:commanded)')
        assert before.count(needle) == 1
        after = before.replace(needle, replacement)
        patch += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    if number == 171 and (args.cleanup_only or args.audited):
        path = 'test/pubsub/phoenix_pubsub_test.exs'
        before = (context / path).read_text()
        after = before.replace('{:ok, _pid} = Supervisor.start_link', '{:ok, pid} = Supervisor.start_link')
        after = after.replace('    on_exit(fn ->', '    Process.unlink(pid)\n\n    on_exit(fn ->\n      Supervisor.stop(pid)')
        assert after != before
        patch += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    if args.audited and number == 139:
        path = 'test/aggregates/aggregate_lifespan_test.exs'
        with tempfile.TemporaryDirectory(prefix='exbench-test-source-') as temp:
            target = Path(temp, path)
            target.parent.mkdir(parents=True)
            target.write_text((context / path).read_text())
            subprocess.run(['git', 'apply', '--include=' + path, '-'], input=task['test_patch'], text=True, cwd=temp, check=True)
            before = target.read_text()
        needle = '              to: BankAccount,\n              lifespan: BankAccountLifespan,'
        assert before.count(needle) == 1
        after = before.replace(needle, '              to: Commanded.ExampleDomain.OpenAccountHandler,\n              aggregate: BankAccount,\n              lifespan: BankAccountLifespan,')
        patch += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    (ROOT / f'findings/commanded-batch/{number}-fixture-startup{suffix}.patch').write_text(patch)
    result = {'image_id': image, 'base_commit': task['base_commit'], 'fixture_patch_sha256': hashlib.sha256(patch.encode()).hexdigest(), 'runs': {}}
    report['tasks'][str(number)] = result
    with tempfile.TemporaryDirectory(prefix='exbench-fixture-') as tmp:
        for name, content in [('gold.patch', task['patch']), ('tests.patch', task['test_patch']), ('fixture.patch', patch)]:
            Path(tmp, name).write_text(content)
        for variant in (['startup'] if (args.cleanup_only or args.audited) else ['unchanged', 'startup']):
            for phase in ['base', 'gold']:
                key = variant + '-' + phase
                name = 'exbench-fixture-' + uuid.uuid4().hex[:12]
                marker = 'EXBENCH_TEST_START_' + uuid.uuid4().hex
                commands = ['set -e']
                if phase == 'gold':
                    commands.append('git apply --recount --ignore-space-change --whitespace=nowarn /patches/gold.patch')
                commands.append('git apply --recount --ignore-space-change --whitespace=nowarn /patches/tests.patch')
                if variant == 'startup':
                    commands.append('git apply --check /patches/fixture.patch')
                    commands.append('git apply /patches/fixture.patch')
                commands += ['epmd -daemon', 'elixir --version', 'echo ' + marker, test_command]
                log_path = OUT / f'{number}-{key}.log'
                code, timed_out = None, False
                print(number, key, 'started', flush=True)
                try:
                    with log_path.open('w') as log:
                        try:
                            code = subprocess.run([D, 'run', '--rm', '--name', name, '--platform', 'linux/amd64', '--network', 'none', '-v', tmp + ':/patches:ro', '-w', '/commanded', image, 'bash', '-c', '\n'.join(commands)], stdout=log, stderr=subprocess.STDOUT, timeout=300).returncode
                        except subprocess.TimeoutExpired:
                            timed_out = True
                finally:
                    subprocess.run([D, 'rm', '-f', name], capture_output=True, timeout=30)
                data = log_path.read_bytes()
                text = data.decode(errors='replace')
                parsed = parse(text.split(marker, 1)[1]) if marker in text else {}
                entry = {'exit_code': code, 'timed_out': timed_out, 'test_started': marker in text, 'raw_summary': re.findall(r'\d+ tests, \d+ failures?', text), 'passed': sorted(k for k, v in parsed.items() if v == 'PASSED'), 'failed': sorted(k for k, v in parsed.items() if v == 'FAILED'), 'log_sha256': hashlib.sha256(data).hexdigest()}
                result['runs'][key] = entry
                (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
                print(number, key, entry['raw_summary'], entry['failed'], flush=True)
report['complete'] = True
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
(ROOT / ('findings/commanded-batch/fixture-startup' + suffix + '-result.json')).write_text(json.dumps(report, indent=2) + '\n')
