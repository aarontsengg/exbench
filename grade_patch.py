"""Local patch grader for versioned Commanded variants (no model calls).

This first integration accepts production lib/ changes only. It is not an agent
execution harness; prompts, model execution, and final sampling remain separate.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent
VARIANT = 'evaluation_variants/commanded__commanded-171--integration-v3.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def assess(rows, expected, exit_code):
    actual = {(r['module'], r['test']): r['status'] for r in rows}
    required = {(r['module'], r['test']) for group in expected.values() for r in group}
    if len(actual) != len(rows):
        raise ValueError('Duplicate qualified test identity')
    missing = sorted(required - actual.keys())
    extra = sorted(actual.keys() - required)
    failed = sorted(k for k, status in actual.items() if status != 'PASSED')
    return {'resolved': exit_code == 0 and not (missing or extra or failed),
            'missing': missing, 'unexpected': extra, 'failed': failed}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--patch', required=True)
    cli.add_argument('--output', required=True)
    cli.add_argument('--variant', default=VARIANT)
    cli.add_argument('--seed', type=int, default=42)
    args = cli.parse_args()
    variant_path = ROOT / args.variant
    v = json.loads(variant_path.read_text())
    task = next(t for t in json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
                if t['instance_id'] == v['upstream_instance_id'])
    evidence_refs = v.get('evidence', [])
    if isinstance(evidence_refs, dict):
        evidence_refs = [evidence_refs]
    references = [v['parser'], *evidence_refs]
    for key in ['shared_patch', 'qualified_evidence']:
        if v.get(key): references.append(v[key])
    for item in references:
        assert sha((ROOT / item['path']).read_bytes()) == item['sha256'], item['path']
    assert task['base_commit'] == v['base_commit']
    expected_hash = v.get('test_patch_sha256')
    if expected_hash is None:
        evidence = json.loads((ROOT / evidence_refs[0]['path']).read_text())['tasks']['171']
        expected_hash = evidence['test_patch_sha256']
    assert sha(task['test_patch'].encode()) == expected_hash
    identities = [(r['module'], r['test']) for group in v['variant_expected'].values() for r in group]
    assert identities and len(set(identities)) == len(identities) == v['raw_test_count']
    patch = Path(args.patch).read_bytes()
    if patch.strip():
        stat = subprocess.run(['git', 'apply', '--numstat', '-z', '-'], input=patch,
                              check=True, capture_output=True).stdout
        paths = [record.split(b'\t', 2)[2].decode() for record in stat.split(b'\0') if record]
        if not paths or any(not p.startswith('lib/') or '..' in Path(p).parts for p in paths):
            raise ValueError('This prototype accepts lib/ changes only; evaluation/setup files are protected')
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    docker = '/Applications/Docker.app/Contents/Resources/bin/docker'
    os.environ['PATH'] = str(Path(docker).parent) + os.pathsep + os.environ.get('PATH', '')
    subprocess.run([docker, 'image', 'inspect', v['image_id']], check=True, capture_output=True, timeout=30)
    spec = importlib.util.spec_from_file_location('qualified_parser', ROOT / v['parser']['path'])
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    result = {'variant_id': v['variant_id'], 'variant_sha256': sha(variant_path.read_bytes()),
              'candidate_sha256': sha(patch), 'image_id': v['image_id'], 'model_calls': 0,
              'resolved': False, 'status': 'started', 'seed': args.seed, 'timeout_seconds': 300}
    name = 'exbench-grade-' + uuid.uuid4().hex[:12]
    marker = 'EXBENCH_TEST_START_' + uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix='exbench-grade-') as tmp:
        Path(tmp, 'candidate.patch').write_bytes(patch)
        Path(tmp, 'tests.patch').write_text(task['test_patch'])
        if v.get('shared_patch'):
            Path(tmp, 'fixture.patch').write_bytes((ROOT / v['shared_patch']['path']).read_bytes())
        commands = ['set -e']
        if patch.strip():
            commands += ['git apply --check /patches/candidate.patch', 'git apply /patches/candidate.patch']
        commands += ['git apply /patches/tests.patch']
        if v.get('shared_patch'):
            commands.append('git apply /patches/fixture.patch')
        commands += ['epmd -daemon', 'echo ' + marker, f'mix test --trace --include distributed --max-cases 1 --seed {args.seed}']
        result['test_command'] = commands[-1]
        try:
            with (out / 'test.log').open('w') as log:
                run = subprocess.run([docker, 'run', '--rm', '--name', name, '--platform', 'linux/amd64',
                                      '--network', 'none', '-v', tmp + ':/patches:ro', '-w', '/commanded',
                                      v['image_id'], 'bash', '-c', '\n'.join(commands)],
                                     stdout=log, stderr=subprocess.STDOUT, timeout=300)
            result['exit_code'] = run.returncode
            text = (out / 'test.log').read_text()
            if marker not in text:
                result['status'] = 'setup_failed'
            else:
                try:
                    rows = parser.parse(text.split(marker, 1)[1])
                    result.update(assess(rows, v['variant_expected'], run.returncode))
                    result['tests'] = rows
                    result['status'] = 'passed' if result['resolved'] else 'tests_failed'
                except ValueError as error:
                    result['status'] = 'invalid_or_incomplete_test_output'
                    result['error'] = str(error)
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
        finally:
            subprocess.run([docker, 'rm', '-f', name], capture_output=True, timeout=30)
    result['log_sha256'] = sha((out / 'test.log').read_bytes())
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'resolved', 'candidate_sha256']}))


if __name__ == '__main__':
    main()
