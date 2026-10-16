"""Summarize recorded executions without treating setup failures as agent failures."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = [
    'validation_runs/smoke-single-map/report.json',
    'validation_runs/batch-02/report.json',
    'validation_runs/remaining-56/report.json',
]


def main():
    sample = json.loads((ROOT / 'candidate_pairs.json').read_text())
    selected = {p[g]['instance_id']: g for p in sample['pairs'] for g in ('otp', 'control')}
    exclusions = json.loads((ROOT / 'sample_exclusions.json').read_text())
    source_tasks = {t['instance_id']: t for t in json.loads((ROOT / 'validation_inputs/tasks.json').read_text())}
    policy_path = ROOT / 'validation_policy.json'
    policy = json.loads(policy_path.read_text())
    reviews = {r['instance_id']: r for r in policy['reviews']}
    if len(reviews) != len(policy['reviews']):
        raise ValueError('Duplicate compilation reviews')
    module_spec = importlib.util.spec_from_file_location('upstream_eval', ROOT / 'third_party/swe-rebench-v2/scripts/eval.py')
    evaluator = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(evaluator)
    latest = {}
    sources = []
    for name in REPORTS:
        path = ROOT / name
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        sources.append({'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'complete': data['complete']})
        for item in data['items']:
            latest[item['instance_id']] = (item, data, name)
    rows = []
    for instance_id, group in selected.items():
        row = {'instance_id': instance_id, 'group': group, 'status': 'untested'}
        if instance_id in latest:
            item, data, source = latest[instance_id]
            phases = item.get('phases', {})
            status = 'validated' if item.get('ok') else 'needs_investigation'
            if 'ok' not in item:
                status = 'in_progress'
            if instance_id in exclusions:
                status = 'quarantined'
            row.update(status=status, source=source, image_id=item.get('image_id'),
                       erl_flags_override=data.get('erl_flags_override'), error=item.get('error'))
            task = source_tasks[instance_id]
            expected = sorted(evaluator._normalize_test_name(n) for n in task['FAIL_TO_PASS'] + task['PASS_TO_PASS'])
            gold = phases.get('gold')
            row['upstream_gold_passed_list_match'] = bool(gold and sorted(gold['passed']) == expected)
            row['strict_gold_ok'] = bool(gold and gold['ok'])
            row['phases'] = {}
            for phase, result in phases.items():
                log_path = ROOT / result['log']
                text = log_path.read_text(errors='replace')
                hints = []
                if result['timed_out']:
                    hints.append('timeout')
                if not result['test_started']:
                    hints.append('setup_or_patch_failure')
                if 'Compilation error' in text or 'could not compile dependency' in text:
                    hints.append('compilation_error')
                if result['missing_expected']:
                    hints.append('expected_test_ids_missing')
                row['phases'][phase] = {
                    'ok': result['ok'], 'seconds': result['seconds'],
                    'exit_code': result['exit_code'], 'timed_out': result['timed_out'],
                    'passed_count': len(result['passed']), 'failed_count': len(result['failed']),
                    'missing_expected_count': len(result['missing_expected']),
                    'triage_hints': hints, 'log': result['log'],
                    'log_sha256': hashlib.sha256(log_path.read_bytes()).hexdigest(),
                }
        row['baseline_category'] = 'strict_transition_verified' if row['status'] == 'validated' else 'unresolved'
        if instance_id in reviews:
            review = reviews[instance_id]
            phases = row.get('phases', {})
            if (review['category'] != 'expected_api_compile_failure'
                    or row['status'] != 'needs_investigation'
                    or not row.get('strict_gold_ok')
                    or row.get('image_id') != review['image_id']
                    or hashlib.sha256(source_tasks[instance_id]['interface'].encode()).hexdigest() != review['interface_sha256']
                    or any(phases.get(p, {}).get('log_sha256') != review[p + '_log_sha256'] for p in ('base', 'gold'))
                    or 'compilation_error' not in phases.get('base', {}).get('triage_hints', [])
                    or phases['base']['timed_out']):
                raise ValueError(f'Compilation review evidence changed: {instance_id}')
            row['baseline_category'] = review['category']
            row['baseline_review_reason'] = review['reason']
        rows.append(row)
    counts = dict(Counter(r['status'] for r in rows))
    metrics = {
        'upstream_gold_passed_list_match': sum(r.get('upstream_gold_passed_list_match', False) for r in rows),
        'strict_gold_ok': sum(r.get('strict_gold_ok', False) for r in rows),
        'upstream_match_but_strict_gold_fails': sum(r.get('upstream_gold_passed_list_match', False) and not r.get('strict_gold_ok', False) for r in rows),
        'strict_validated_by_group': dict(Counter(r['group'] for r in rows if r['status'] == 'validated')),
    }
    good = {r['instance_id'] for r in rows if r['status'] == 'validated'}
    metrics['intact_strict_validated_pairs'] = sum(p['otp']['instance_id'] in good and p['control']['instance_id'] in good for p in sample['pairs'])
    metrics['expected_api_compile_failure_by_group'] = dict(Counter(r['group'] for r in rows if r['baseline_category'] == 'expected_api_compile_failure'))
    report = {'scope': '60-task draft; not final balanced sample', 'counts': counts,
              'metrics': metrics,
              'policy_sha256': hashlib.sha256(policy_path.read_bytes()).hexdigest(),
              'model_calls': 0, 'sources': sources, 'tasks': rows,
              'limitations': ['Validation applies to recorded amd64 emulation configuration.',
                              'Triage hints do not establish root cause; investigate logs.',
                              'No agent performance has been measured.']}
    (ROOT / 'validation_summary.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Reference validation results', '',
             'Scope: original 60-task draft. No model calls. Recorded amd64 emulation with explicit JIT override.', '',
             'Counts: ' + ', '.join(f'{k}: {v}' for k, v in counts.items()), '',
             'Upstream passing-list matches: ' + str(metrics['upstream_gold_passed_list_match']) +
             '; strict gold passes: ' + str(metrics['strict_gold_ok']) + '.', '',
             'Strict validation adds zero failed tests, successful gold exit, and exact base test outcomes. '
             'Upstream passing-list matching alone does not require these. These are different measures, not agent scores.', '',
             'Reviewed expected API compilation failures (separate from strict validation): ' + str(metrics['expected_api_compile_failure_by_group']) + '.', '',
             'This category requires the supplemental interface in future agent instructions. It does not verify individual base test outcomes or finalize sample eligibility. See VALIDATION_POLICY.md.', '',
             '| Task | Group | Status | Baseline category | Base / gold seconds |', '| --- | --- | --- | --- | --- |']
    for row in rows:
        phases = row.get('phases', {})
        timing = ' / '.join(str(phases.get(p, {}).get('seconds', '—')) for p in ('base', 'gold'))
        lines.append(f"| {row['instance_id']} | {row['group']} | {row['status']} | {row['baseline_category']} | {timing} |")
    lines += ['', 'Detailed evidence, image IDs and log hashes: validation_summary.json.',
              'Needs investigation is not an agent failure or automatic task exclusion.', '']
    (ROOT / 'VALIDATION_RESULTS.md').write_text('\n'.join(lines))
    print(counts)


if __name__ == '__main__':
    main()
