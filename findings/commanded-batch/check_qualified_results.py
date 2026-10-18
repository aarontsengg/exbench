"""Check all eight audited logs without rerunning tests or modifying old evidence."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from parse_qualified_historical import parse

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
report = {'parser_sha256': hashlib.sha256((HERE / 'parse_qualified_historical.py').read_bytes()).hexdigest(), 'tasks': {}}
for number in ['139', '171']:
    runs = {}
    for seed in [42, 7]:
        old = json.loads((HERE / f'fixture-startup-audit-seed{seed}-result.json').read_text())
        assert old['complete']
        for phase in ['base', 'gold']:
            rel = f'validation_runs/commanded-fixture-diagnostic-audit-seed{seed}/{number}-startup-{phase}.log'
            data = (ROOT / rel).read_bytes()
            evidence = old['tasks'][number]['runs']['startup-' + phase]
            assert hashlib.sha256(data).hexdigest() == evidence['log_sha256']
            assert evidence['test_started'] and not evidence['timed_out']
            rows = parse(data.decode().split('EXBENCH_TEST_START_', 1)[1])
            runs[f'{seed}-{phase}'] = {'log': rel, 'sha256': evidence['log_sha256'], 'exit_code': evidence['exit_code'], 'tests': rows}
    for phase in ['base', 'gold']:
        assert runs['42-' + phase]['tests'] == runs['7-' + phase]['tests']
    base, gold = runs['42-base']['tests'], runs['42-gold']['tests']
    assert [(r['module'], r['test']) for r in base] == [(r['module'], r['test']) for r in gold]
    assert all(r['status'] == 'PASSED' for r in gold)
    assert all(runs[f'{s}-gold']['exit_code'] == 0 for s in [42, 7])
    assert all(runs[f'{s}-base']['exit_code'] in [1, 2] for s in [42, 7])
    groups = defaultdict(list)
    for row in gold:
        groups[row['test']].append(row['module'])
    collisions = {name: modules for name, modules in groups.items() if len(modules) > 1}
    failed = [r for r in base if r['status'] == 'FAILED']
    report['tasks'][number] = {'count': len(gold), 'base_failed': failed, 'collisions': collisions, 'seeds_agree': True, 'runs': runs}
    print(number, 'tests:', len(gold), 'base failures:', len(failed), 'collisions:', json.dumps(collisions))
(HERE / 'qualified-results.json').write_text(json.dumps(report, indent=2) + '\n')

# Version the qualified inventory separately; preserve the recorded v1 artifact.
variant_path = ROOT / 'evaluation_variants/commanded__commanded-171--historical-fixtures-v1.json'
v = json.loads(variant_path.read_text())
for evidence in v['evidence']:
    assert hashlib.sha256((ROOT / evidence['path']).read_bytes()).hexdigest() == evidence['sha256']
assert hashlib.sha256((ROOT / v['shared_patch']['path']).read_bytes()).hexdigest() == v['shared_patch']['sha256']
v['variant_id'] = 'commanded__commanded-171--historical-fixtures-v2'
v['supersedes'] = {'path': str(variant_path.relative_to(ROOT)), 'sha256': hashlib.sha256(variant_path.read_bytes()).hexdigest()}
v['parser'] = {'path': 'findings/commanded-batch/parse_qualified_historical.py', 'sha256': report['parser_sha256'], 'identity': ['module', 'test'], 'requires_serial_trace': True}
rows = report['tasks']['171']['runs']['42-base']['tests']
v['variant_expected'] = {
    key: [{'module': r['module'], 'test': r['test']} for r in rows if r['status'] == status]
    for key, status in [('FAIL_TO_PASS', 'FAILED'), ('PASS_TO_PASS', 'PASSED')]
}
assert v['variant_expected']['FAIL_TO_PASS'] == [{'module': 'Commanded.Commands.DispatchConsistencyTest', 'test': 'process manager consistency should successfully dispatch command'}]
v['qualified_evidence'] = {'path': 'findings/commanded-batch/qualified-results.json', 'sha256': hashlib.sha256((HERE / 'qualified-results.json').read_bytes()).hexdigest()}
v['expectation_review']['identity_upgrade'] = 'All 202 module/test identities recovered; same inventory and statuses across both seeds. Historical name-only comparison lists retained as provenance.'
v['limitations'] = [x for x in v['limitations'] if not x.startswith('Unqualified parser')]
v['limitations'].append('Qualified diagnostic parser requires serial old-ExUnit trace output and matching suite totals; agent grader integration remains pending.')
(ROOT / 'evaluation_variants' / (v['variant_id'] + '.json')).write_text(json.dumps(v, indent=2) + '\n')
print('Recorded v2: 201 qualified PASS_TO_PASS IDs and 1 qualified FAIL_TO_PASS ID.')
