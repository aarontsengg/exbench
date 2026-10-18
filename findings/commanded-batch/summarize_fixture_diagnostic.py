"""Verify saved logs and compare diagnostic results to upstream expectations."""
import argparse, hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
up = ROOT / 'third_party/swe-rebench-v2'
lock = json.loads((ROOT / 'harness_config.json').read_text())
for path, digest in lock['files_sha256'].items():
    assert hashlib.sha256((up / path).read_bytes()).hexdigest() == digest
spec = importlib.util.spec_from_file_location('upstream_eval', up / 'scripts/eval.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)
norm = ev._normalize_test_name
tasks = json.loads((ROOT / 'validation_inputs/tasks.json').read_text())
args = argparse.ArgumentParser()
args.add_argument('--audit', action='store_true')
args = args.parse_args()
for suffix in (['-audit-seed42', '-audit-seed7'] if args.audit else ['', '-cleanup']):
    out = ROOT / ('validation_runs/commanded-fixture-diagnostic' + suffix)
    r = json.loads((out / 'report.json').read_text())
    assert r['complete']
    r['test_command'] = f"mix test --trace --max-cases 1 --seed {r['seed']}"
    r['historical_parser_sha256'] = hashlib.sha256((Path(__file__).parent / 'parse_380_historical.py').read_bytes()).hexdigest()
    for number, result in r['tasks'].items():
        t = next(t for t in tasks if t['instance_id'] == f'commanded__commanded-{number}')
        result['original_test_command'] = t['install_config']['test_cmd']
        for field in ['patch', 'test_patch']:
            result[field + '_sha256'] = hashlib.sha256(t[field].encode()).hexdigest()
        for key, run in result['runs'].items():
            assert hashlib.sha256((out / f'{number}-{key}.log').read_bytes()).hexdigest() == run['log_sha256']
        b, g = (result['runs']['startup-' + phase] for phase in ['base', 'gold'])
        bp, bf, gp, gf = [set(map(norm, x)) for x in [b['passed'], b['failed'], g['passed'], g['failed']]]
        ftp, ptp = set(map(norm, t['FAIL_TO_PASS'])), set(map(norm, t['PASS_TO_PASS']))
        result['comparison'] = {
            'expected_failures_already_passing_base': sorted(ftp & bp),
            'unexpected_base_failures': sorted(bf - ftp),
            'missing_gold_expected_ids': sorted((ftp | ptp) - gp),
            'extra_gold_passing_ids': sorted(gp - (ftp | ptp)),
            'observed_full_transition': b['exit_code'] in [1, 2] and g['exit_code'] == 0 and not b['timed_out'] and not g['timed_out'] and not gf and gp == bp | bf,
            'upstream_failure_partition_matches': bf == ftp,
        }
        print(number, suffix, 'base failures', len(bf), 'gold failures', len(gf), 'already passing', len(ftp & bp), 'unexpected', len(bf - ftp), 'extra gold', len(gp - (ftp | ptp)))
    (ROOT / ('findings/commanded-batch/fixture-startup' + suffix + '-result.json')).write_text(json.dumps(r, indent=2) + '\n')
