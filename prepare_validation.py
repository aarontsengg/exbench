"""Export pinned task rows for reference validation. Never calls a model."""
import hashlib
import argparse
import json
import shutil
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--diagnostic-ids', nargs='+', help='Export only these non-excluded draft tasks; does not finalize sample')
    args = cli.parse_args()
    config = json.loads((ROOT / 'dataset_config.json').read_text())
    sample = json.loads((ROOT / 'candidate_pairs.json').read_text())
    parquet = ROOT / 'train.parquet'
    if parquet.stat().st_size != config['size_bytes'] or digest(parquet) != config['sha256']:
        raise ValueError('Dataset does not match pinned bytes')
    if (sample['dataset'], sample['revision'], sample['dataset_sha256']) != (
        config['dataset'], config['revision'], config['sha256']
    ):
        raise ValueError('Sample and dataset configuration differ')
    lock = json.loads((ROOT / 'harness_config.json').read_text())
    for name, expected in lock['files_sha256'].items():
        if digest(ROOT / 'third_party/swe-rebench-v2' / name) != expected:
            raise ValueError(f'Upstream source changed: {name}')
    ids = [p[g]['instance_id'] for p in sample['pairs'] for g in ('otp', 'control')]
    exclusions = json.loads((ROOT / 'sample_exclusions.json').read_text())
    excluded = sorted(set(ids) & set(exclusions))
    if excluded and not args.diagnostic_ids:
        raise ValueError(f'Sample contains excluded tasks; resolve sample before export: {excluded}')
    if len(ids) != 60 or len(set(ids)) != 60:
        raise ValueError('Expected 60 distinct selected tasks')
    if args.diagnostic_ids:
        requested = args.diagnostic_ids
        if len(requested) != len(set(requested)) or not set(requested) <= set(ids) or set(requested) & set(exclusions):
            raise ValueError('Diagnostic IDs must be unique, selected and non-excluded')
        ids = requested
    rows = pq.read_table(parquet, filters=[('instance_id', 'in', ids)]).to_pylist()
    by_id = {r['instance_id']: r for r in rows}
    if set(by_id) != set(ids):
        raise ValueError('Some selected tasks missing from source')
    for row in rows:
        for field in ('image_name', 'base_commit', 'patch', 'test_patch', 'FAIL_TO_PASS'):
            if not row[field]:
                raise ValueError(f"{row['instance_id']}: missing {field}")
        if row['install_config']['log_parser'] != 'parse_log_elixir':
            raise ValueError(f"Unexpected parser for {row['instance_id']}")
    out = ROOT / 'validation_inputs'
    out.mkdir(exist_ok=True)
    # First matched pair: one OTP and one control. Fixed by saved sample order.
    exports = [('diagnostic.json', ids)] if args.diagnostic_ids else [('tasks.json', ids), ('smoke.json', ids[:2])]
    for name, chosen in exports:
        (out / name).write_text(json.dumps([by_id[i] for i in chosen], indent=2) + '\n')
    manifest = {
        'dataset_revision': config['revision'],
        'sample_sha256': digest(ROOT / 'candidate_pairs.json'),
        'harness_revision': lock['revision'],
        'task_count': len(ids), 'smoke_ids': ids[:2],
        'input_sha256': {name: digest(out / name) for name, _ in exports},
        'purpose': 'diagnostic subset; not finalized sample' if args.diagnostic_ids else 'sample validation',
        'docker_cli_available': shutil.which('docker') is not None,
        'runtime_validation_started': False,
        'warning': 'Evaluator-only inputs contain reference solutions; never provide them to agents.',
    }
    manifest_name = 'diagnostic_manifest.json' if args.diagnostic_ids else 'validation_manifest.json'
    (ROOT / manifest_name).write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Prepared {len(ids)} reference tasks: {manifest_name}')
    print('Docker CLI available:', manifest['docker_cli_available'])


if __name__ == '__main__':
    main()
