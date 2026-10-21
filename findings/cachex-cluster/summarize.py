"""Preserve the epmd diagnostic separately from original validation results."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
report_path = ROOT / 'validation_runs/cachex-epmd/report.json'
current = json.loads(report_path.read_text())
assert current['complete']
original = json.loads((ROOT / 'validation_runs/remaining-56/report.json').read_text())
tasks = json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
summary = {'date': '2026-10-19', 'model_calls': 0,
           'change': 'Start epmd before tests in both phases; retain original JIT override',
           'sample_changed': False, 'tasks': {}}
for item in current['items']:
    assert 'error' not in item, item
    old = next(t for t in original['items'] if t['instance_id'] == item['instance_id'])
    assert item['image_id'] == old['image_id'], 'Image changed: comparison confounded'
    task = next(t for t in tasks if t['instance_id'] == item['instance_id'])
    entry = {'image_id': item['image_id'], 'original': {}, 'epmd': {},
             'source_sha256': {k: hashlib.sha256(task[k].encode()).hexdigest()
                               for k in ['patch', 'test_patch', 'interface']}}
    for label, data in [('original', old), ('epmd', item)]:
        for phase, result in data['phases'].items():
            log = ROOT / result['log']
            text = log.read_text()
            entry[label][phase] = {**result, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
                                  'raw_summaries': re.findall(r'^.*\d+ tests?, \d+ failures?.*$', text, re.MULTILINE),
                                  'not_alive_mentions': text.count(':not_alive'),
                                  'econnrefused_mentions': text.count('econnrefused')}
    summary['tasks'][item['instance_id']] = entry
    for phase, result in item['phases'].items():
        print(item['instance_id'], phase, 'passed', len(result['passed']),
              'failed', len(result['failed']), 'exit', result['exit_code'], 'strict', result['ok'])
summary['report_sha256'] = hashlib.sha256(report_path.read_bytes()).hexdigest()
(ROOT / 'findings/cachex-cluster/epmd-results.json').write_text(json.dumps(summary, indent=2) + '\n')
