"""Record the audited historical variant; do not alter upstream grading/sample."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = 'commanded__commanded-171'
# Reviewed against the issue, assertion, and reference patch in TEST_ALIGNMENT_AUDIT.md.
FAIL_TO_PASS = ['process manager consistency should successfully dispatch command']


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    task = next(t for t in json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
                if t['instance_id'] == TASK_ID)
    parser_path = 'findings/commanded-batch/parse_380_historical.py'
    spec = importlib.util.spec_from_file_location('historical_parser', ROOT / parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    evidence = []
    inventory = None
    image = None
    patch_hash = None
    for seed in (42, 7):
        path = f'findings/commanded-batch/fixture-startup-audit-seed{seed}-result.json'
        report = json.loads((ROOT / path).read_text())
        assert report['complete'] and report['seed'] == seed
        assert report['historical_parser_sha256'] == sha(parser_path)
        item = report['tasks']['171']
        assert item['base_commit'] == task['base_commit']
        for field in ('patch', 'test_patch'):
            assert item[field + '_sha256'] == hashlib.sha256(task[field].encode()).hexdigest()
        fixture = f'findings/commanded-batch/171-fixture-startup-audit-seed{seed}.patch'
        assert item['fixture_patch_sha256'] == sha(fixture)
        if image is not None:
            assert image == item['image_id'] and patch_hash == sha(fixture)
        image, patch_hash = item['image_id'], sha(fixture)
        for phase in ('base', 'gold'):
            run = item['runs']['startup-' + phase]
            log = f'validation_runs/commanded-fixture-diagnostic-audit-seed{seed}/171-startup-{phase}.log'
            assert run['test_started'] and not run['timed_out']
            assert sha(log) == run['log_sha256']
            text = (ROOT / log).read_text()
            assert 'EXBENCH_TEST_START_' in text
            parsed = parser.parse(text.split('EXBENCH_TEST_START_', 1)[1])
            passed = sorted(k for k, status in parsed.items() if status == 'PASSED')
            failed = sorted(k for k, status in parsed.items() if status == 'FAILED')
            assert passed == run['passed'] and failed == run['failed']
            assert re.search(r'202 tests, ' + ('1 failure' if phase == 'base' else '0 failures'), text)
            if phase == 'base':
                assert run['exit_code'] in (1, 2) and failed == FAIL_TO_PASS
                if inventory is not None:
                    assert inventory == passed
                inventory = passed
            else:
                assert run['exit_code'] == 0 and not failed
                assert set(passed) == set(inventory) | set(FAIL_TO_PASS)
        evidence.append({'path': path, 'sha256': sha(path), 'seed': seed,
                         'command': report['test_command']})
    ftp, ptp = set(task['FAIL_TO_PASS']), set(task['PASS_TO_PASS'])
    variant = {
        'variant_id': TASK_ID + '--historical-fixtures-v1',
        'upstream_instance_id': TASK_ID,
        'dataset': json.loads((ROOT / 'dataset_config.json').read_text()),
        'status': 'diagnostic_transition_verified_pending_grader_integration',
        'selected_for_final_sample': False,
        'base_commit': task['base_commit'], 'image_id': image,
        'platform': 'linux/amd64', 'start_epmd': True, 'network': 'none',
        'shared_patch': {'path': 'findings/commanded-batch/171-fixture-startup-audit-seed42.patch', 'sha256': patch_hash},
        'patch_order': ['reference patch in gold only', 'upstream test patch', 'shared fixture patch'],
        'parser': {'path': parser_path, 'sha256': sha(parser_path), 'identity': 'unqualified test name'},
        'prompt_fields': ['problem_statement', 'interface'],
        'interface_sha256': hashlib.sha256(task['interface'].encode()).hexdigest(),
        'upstream_expected': {'FAIL_TO_PASS': sorted(ftp), 'PASS_TO_PASS': sorted(ptp)},
        'variant_expected': {'FAIL_TO_PASS': FAIL_TO_PASS, 'PASS_TO_PASS': inventory},
        'expectation_review': {
            'failure_basis': 'Explicit issue/assertion review, not automatic inference from failures.',
            'regression_basis': 'Entire observed base passing inventory retained, identical in both seeds; not individually reviewed for specification fairness.',
            'upstream_failures_now_regressions': sorted(ftp & set(inventory)),
            'additional_regression_ids': sorted(set(inventory) - ftp - ptp),
        },
        'raw_test_count': 202, 'evidence': evidence,
        'audit': {'path': 'findings/commanded-batch/TEST_ALIGNMENT_AUDIT.md', 'sha256': sha('findings/commanded-batch/TEST_ALIGNMENT_AUDIT.md')},
        'limitations': [
            'Post-hoc runtime and test-fixture repair, not unchanged-upstream validation.',
            'Two seeds on amd64 emulation; no native-amd64 validation or flakiness estimate.',
            'Unqualified parser merges same-named tests across modules; grader needs qualified identities before agent scoring.',
            'Agent runner does not yet consume this variant; no final eligibility implied.',
            'Complete regression inventory retained but not every assertion individually audited for fairness.',
        ],
    }
    target = ROOT / 'evaluation_variants' / (variant['variant_id'] + '.json')
    target.write_text(json.dumps(variant, indent=2) + '\n')
    print(f'Verified two seeds: base {len(inventory)} passing IDs / 1 failing; gold {len(inventory)+1} passing IDs. Raw count: 202.')


if __name__ == '__main__':
    main()
