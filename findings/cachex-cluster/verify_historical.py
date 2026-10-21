"""Verify saved historical comparison evidence without rewriting upstream results."""
import hashlib
import json
from pathlib import Path
from audit_identities import parse
ROOT = Path(__file__).resolve().parents[2]
folder = ROOT / 'validation_runs/cachex-historical-perf'
report = json.loads((folder / 'report.json').read_text())
assert report['complete']
summary = {'model_calls': 0, 'sample_changed': False, 'date': '2026-10-20', 'tasks': {}}
for ident, task in report['tasks'].items():
    runs = {}
    manifest = folder / ident / 'dependency-hashes.json'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == task['dependencies_manifest_sha256']
    assert hashlib.sha256((folder / ident / 'built.mix.lock').read_bytes()).hexdigest() == task['mix_lock_sha256']
    assert set(task['runs']) == {'42-base','42-gold','7-base','7-gold'}
    for key, run in task['runs'].items():
        path = folder / ident / (key + '.log')
        data = path.read_bytes(); assert hashlib.sha256(data).hexdigest() == run['log_sha256']
        if 'tests' in run:
            rows = parse(data.decode()); assert rows == run['tests']
            failed = [r for r in rows if r['status'] != 'PASSED']
            runs[key] = {'raw_test_count': len(rows), 'failed': failed, 'exit_code': run['exit_code'], 'log_sha256': run['log_sha256']}
        else:
            assert 'record :warmer does not have the key: :async' in data.decode()
            assert key.endswith('base') and ident.endswith('-294') and run['exit_code'] != 0
            runs[key] = {'base_compilation_failure': 'missing warmer async field', 'exit_code': run['exit_code'], 'log_sha256': run['log_sha256']}
    for seed in [42, 7]:
        gold = runs[f'{seed}-gold']
        assert gold['exit_code'] == 0 and not gold['failed']
        assert gold['raw_test_count'] == (194 if ident.endswith('-292') else 195)
        if ident.endswith('-292'):
            assert [(r['module'],r['test']) for r in runs[f'{seed}-base']['failed']] == [('Cachex.Services.CourierTest','gracefully handling crashes inside tasks')]
            assert runs[f'{seed}-base']['raw_test_count'] == 194
    assert task['runs']['42-gold']['tests'] == task['runs']['7-gold']['tests']
    summary['tasks'][ident] = {'runtime': task['runtime_version'], 'image_id':task['image_id'], 'runs':runs,
                              'build_log_sha256': hashlib.sha256((folder / ident / 'build.log').read_bytes()).hexdigest()}
    print(ident)
    for key, run in runs.items(): print(key, run.get('raw_test_count','compile failure'), 'failures:',len(run.get('failed',[])), 'exit:',run['exit_code'])
summary['report_sha256'] = hashlib.sha256((folder / 'report.json').read_bytes()).hexdigest()
(ROOT / 'findings/cachex-cluster/historical-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
