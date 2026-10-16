"""Run base and gold checks in fresh containers; reuse the pinned upstream parser."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--input', default='validation_inputs/smoke.json')
    cli.add_argument('--manifest', default='validation_manifest.json')
    cli.add_argument('--output', default='validation_runs/smoke')
    cli.add_argument('--timeout', type=int, default=900)
    cli.add_argument('--erl-flags', default='', help='Explicit recorded runtime override for diagnostics')
    cli.add_argument('--base-setup-patch', help='Diagnostic only: apply this setup patch to base before tests; gold already includes setup')
    cli.add_argument('--shared-setup-patch', help='Diagnostic only: apply the same compatibility patch in both phases')
    cli.add_argument('--start-epmd', action='store_true', help='Diagnostic only: start Erlang port mapper before tests in both phases')
    cli.add_argument('--pull-missing', action='store_true')
    cli.add_argument('--release-pulled-images', action='store_true', help='Remove only images fetched by this invocation after testing')
    args = cli.parse_args()
    if args.timeout <= 0:
        cli.error('timeout must be positive')
    docker_dir = '/Applications/Docker.app/Contents/Resources/bin'
    if Path(docker_dir).exists():
        os.environ['PATH'] = docker_dir + os.pathsep + os.environ.get('PATH', '')
    docker = shutil.which('docker')
    if not docker:
        raise SystemExit('Docker CLI not found')
    subprocess.run([docker, 'version', '--format', '{{.Server.Version}}'],
                   check=True, capture_output=True, timeout=30)
    lock = json.loads((ROOT / 'harness_config.json').read_text())
    upstream = ROOT / 'third_party/swe-rebench-v2'
    for name, expected in lock['files_sha256'].items():
        if hashlib.sha256((upstream / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Upstream file changed: {name}')
    module_spec = importlib.util.spec_from_file_location('upstream_eval', upstream / 'scripts/eval.py')
    evaluator = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(evaluator)
    input_path = (ROOT / args.input).resolve()
    manifest = json.loads((ROOT / args.manifest).read_text())
    expected = manifest['input_sha256'].get(input_path.name)
    if not expected or hashlib.sha256(input_path.read_bytes()).hexdigest() != expected:
        raise ValueError('Input is not the pinned prepared export')
    if hashlib.sha256((ROOT / 'candidate_pairs.json').read_bytes()).hexdigest() != manifest['sample_sha256']:
        raise ValueError('Sample changed; regenerate validation inputs')
    tasks = json.loads(input_path.read_text())
    setup_patch = (ROOT / args.base_setup_patch).read_bytes() if args.base_setup_patch else None
    shared_patch = (ROOT / args.shared_setup_patch).read_bytes() if args.shared_setup_patch else None
    if shared_patch is not None and (len(tasks) != 1 or setup_patch is not None):
        raise ValueError('Shared diagnostic patch requires one task and no base-only patch')
    if setup_patch is not None and len(tasks) != 1:
        raise ValueError('A diagnostic setup patch requires exactly one task')
    exclusions = json.loads((ROOT / 'sample_exclusions.json').read_text())
    if any(t['instance_id'] in exclusions for t in tasks):
        raise ValueError('Validation input contains a quarantined task')
    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / 'report.json'
    if report_path.exists():
        raise ValueError('Output already has a report; choose a new output directory')
    report = {'harness_revision': lock['revision'], 'platform': 'linux/amd64',
              'input_sha256': expected, 'timeout_seconds_per_phase': args.timeout,
              'erl_flags_override': args.erl_flags,
              'model_calls': 0, 'complete': False, 'items': []}
    if args.start_epmd:
        report['diagnostic_only'] = True
        report['start_epmd'] = True
    if setup_patch is not None:
        report['diagnostic_only'] = True
        report['base_setup_patch'] = {'path': args.base_setup_patch,
                                     'sha256': hashlib.sha256(setup_patch).hexdigest()}
    if shared_patch is not None:
        report['diagnostic_only'] = True
        report['shared_setup_patch'] = {'path': args.shared_setup_patch,
                                       'sha256': hashlib.sha256(shared_patch).hexdigest()}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    for task in tasks:
        item = {'instance_id': task['instance_id'], 'image_name': task['image_name'], 'phases': {}}
        report['items'].append(item)
        pulled = False
        try:
            available = subprocess.run([docker, 'image', 'inspect', task['image_name']],
                                       capture_output=True, timeout=30)
            if available.returncode and args.pull_missing:
                print(f'{task["instance_id"]}: downloading image', flush=True)
                pull_log = out / f'{task["instance_id"]}.pull.log'
                with pull_log.open('w') as stream:
                    subprocess.run([docker, 'pull', '--platform', 'linux/amd64', task['image_name']],
                                   stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=600)
                pulled = True
            image = json.loads(subprocess.check_output(
                [docker, 'image', 'inspect', task['image_name']], timeout=30))[0]
            item['image_id'] = image['Id']
            item['repo_digests'] = image['RepoDigests']
            item['architecture'] = image['Architecture']
            parser = evaluator.get_parser(task['install_config']['log_parser'])
            commands = evaluator.normalize_command_list(task['install_config']['test_cmd'], 'test_cmd', task['instance_id'])
            normalize = evaluator._normalize_test_name
            ftp = {normalize(n) for n in task['FAIL_TO_PASS']}
            ptp = {normalize(n) for n in task['PASS_TO_PASS']}
            if not ftp or ftp & ptp:
                raise ValueError('Invalid expected-test partition')
            with tempfile.TemporaryDirectory(prefix='exbench-reference-') as tmp:
                patchdir = Path(tmp)
                (patchdir / 'gold.patch').write_text(task['patch'])
                (patchdir / 'tests.patch').write_text(task['test_patch'])
                if setup_patch is not None:
                    (patchdir / 'setup.patch').write_bytes(setup_patch)
                if shared_patch is not None:
                    (patchdir / 'shared.patch').write_bytes(shared_patch)
                for phase in ('base', 'gold'):
                    name = 'exbench-' + uuid.uuid4().hex[:16]
                    marker = 'EXBENCH_TEST_START_' + uuid.uuid4().hex
                    script = ['set -e', f'test "$(git rev-parse HEAD)" = {shlex.quote(task["base_commit"])}',
                              'git reset --hard HEAD']
                    if phase == 'gold':
                        script.append('git apply -v --3way --recount --ignore-space-change --whitespace=nowarn /patches/gold.patch')
                    elif setup_patch is not None:
                        script.append('git apply --check /patches/setup.patch')
                        script.append('git apply /patches/setup.patch')
                    if shared_patch is not None:
                        script.append('git apply --check /patches/shared.patch')
                        script.append('git apply /patches/shared.patch')
                    if args.start_epmd:
                        script.append('epmd -daemon')
                        script.append('epmd -names')
                    script += ['git apply -v --3way --recount --ignore-space-change --whitespace=nowarn /patches/tests.patch',
                               f'echo {marker}', *commands]
                    cmd = [docker, 'run', '--rm', '--name', name, '--platform', 'linux/amd64',
                           '--network', 'host', '-e', '_JAVA_OPTIONS=-Djava.net.preferIPv6Addresses=false',
                           '-v', f'{patchdir}:/patches:ro', '-w', '/' + task['repo'].split('/')[1],
                           image['Id'], '/bin/bash', '-c', '\n'.join(script)]
                    if args.erl_flags:
                        cmd[2:2] = ['-e', 'ERL_FLAGS=' + args.erl_flags]
                    print(f'{task["instance_id"]}: {phase} started', flush=True)
                    started = time.monotonic()
                    log = out / f'{task["instance_id"]}.{phase}.log'
                    timed_out = False
                    with log.open('w') as stream:
                        try:
                            completed = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, timeout=args.timeout)
                            code = completed.returncode
                        except subprocess.TimeoutExpired:
                            timed_out = True
                            code = None
                        finally:
                            # Only this invocation's uniquely named container.
                            subprocess.run([docker, 'rm', '-f', name], capture_output=True, timeout=30)
                    output = log.read_text(errors='replace')
                    test_started = marker in output
                    parsed = parser(output.split(marker, 1)[1]) if test_started else {}
                    parsed = {normalize(k): v for k, v in parsed.items()}
                    passed = {k for k, v in parsed.items() if v == 'PASSED'}
                    failed = {k for k, v in parsed.items() if v == 'FAILED'}
                    ok = (not timed_out and test_started and
                          ((code == 0 and passed == ftp | ptp and not failed) if phase == 'gold'
                           else (code == 2 or code == 1) and failed == ftp and passed == ptp))
                    result = {'exit_code': code, 'timed_out': timed_out, 'test_started': test_started,
                              'seconds': round(time.monotonic() - started, 2), 'ok': ok,
                              'passed': sorted(passed), 'failed': sorted(failed),
                              'missing_expected': sorted((ftp | ptp) - set(parsed)), 'log': str(log.relative_to(ROOT))}
                    item['phases'][phase] = result
                    report_path.write_text(json.dumps(report, indent=2) + '\n')
                    print(f'{task["instance_id"]}: {phase} ok={ok}, exit={code}, {result["seconds"]}s', flush=True)
            item['ok'] = all(p['ok'] for p in item['phases'].values())
        except Exception as exc:
            item['error'] = str(exc)
            item['ok'] = False
            print(f'{task["instance_id"]}: error: {exc}', flush=True)
        finally:
            if pulled and args.release_pulled_images:
                cleanup = subprocess.run([docker, 'image', 'rm', task['image_name']],
                                         capture_output=True, text=True, timeout=60)
                item['image_release_exit_code'] = cleanup.returncode
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    report['complete'] = True
    report['all_ok'] = all(item['ok'] for item in report['items'])
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('Report:', report_path)
    return 0 if report['all_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
