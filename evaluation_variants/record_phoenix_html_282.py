"""Record one reviewed repair variant; never modify upstream inputs or sampling."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = 'phoenixframework__phoenix_html-282'
# Reviewed individually in findings/phoenix-html-282-runtime-audit.md.
ADDED_PASS_TO_PASS = [
    'date_select/4', 'date_select/4 with form',
    'datetime_select/4', 'datetime_select/4 with form',
    'does not escape safe expressions',
]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    task = next(t for t in json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
                if t['instance_id'] == TASK_ID)
    evidence_path = 'findings/phoenix-html-282-compatibility-result.json'
    evidence = json.loads((ROOT / evidence_path).read_text())
    item = evidence['items'][0]
    patch = 'findings/phoenix-html-282-compatibility.patch'
    assert item['instance_id'] == TASK_ID and evidence['complete']
    assert evidence['shared_setup_patch']['sha256'] == sha(patch)
    ftp = set(task['FAIL_TO_PASS'])
    ptp = set(task['PASS_TO_PASS'])
    additions = set(ADDED_PASS_TO_PASS)
    assert ftp == {'content_tag'} and not additions & (ftp | ptp)
    effective_ptp = ptp | additions
    base, gold = (item['phases'][phase] for phase in ('base', 'gold'))
    for phase in (base, gold):
        assert phase['test_started'] and not phase['timed_out']
        assert sha(phase['log']) == phase['log_sha256']
    assert base['exit_code'] in (1, 2) and gold['exit_code'] == 0
    assert set(base['failed']) == ftp and set(base['passed']) == effective_ptp
    assert not gold['failed'] and set(gold['passed']) == ftp | effective_ptp
    variant = {
        'variant_id': TASK_ID + '--compatibility-v1',
        'upstream_instance_id': TASK_ID,
        'dataset': json.loads((ROOT / 'dataset_config.json').read_text()),
        'status': 'recorded_repaired_transition_verified',
        'selected_for_final_sample': False,
        'image_id': item['image_id'], 'base_commit': task['base_commit'],
        'harness_revision': evidence['harness_revision'],
        'platform': evidence['platform'], 'erl_flags_override': evidence['erl_flags_override'],
        'shared_patch': {'path': patch, 'sha256': sha(patch)},
        'upstream_expected': {'FAIL_TO_PASS': sorted(ftp), 'PASS_TO_PASS': sorted(ptp)},
        'variant_expected': {'FAIL_TO_PASS': sorted(ftp), 'PASS_TO_PASS': sorted(effective_ptp)},
        'added_pass_to_pass': ADDED_PASS_TO_PASS,
        'evidence': {'path': evidence_path, 'sha256': sha(evidence_path)},
        'limitations': [
            'Post-hoc diagnostic repair, not unchanged-upstream validation.',
            'Selector year is fixed to 2020 in library code for this variant.',
            'Single recorded run per phase; no flakiness assessment.',
            'Counts use upstream parsed IDs, not every raw ExUnit case.',
            'Agent runner does not yet apply this variant.',
        ],
    }
    target = ROOT / 'evaluation_variants' / (variant['variant_id'] + '.json')
    target.write_text(json.dumps(variant, indent=2) + '\n')
    print('Verified repaired variant: base 149 passing / 1 failing; gold 150 passing / 0 failing.')


if __name__ == '__main__':
    main()
