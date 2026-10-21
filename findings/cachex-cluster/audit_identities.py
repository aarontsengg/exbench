"""Audit serial modern ExUnit traces using the strict qualified historical parser."""
import hashlib
import importlib.util
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser_path = ROOT / 'findings/commanded-batch/parse_qualified_historical.py'
spec = importlib.util.spec_from_file_location('qualified', parser_path)
qualified = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualified)

def parse(text):
    # Remove modern trace decorations only; retain module identities and timing.
    text = re.sub(r'^(\w+(?:\.\w+)*) \[test/[^\n]+\]$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'^(\s+\* test .+ \([0-9]+(?:\.[0-9]+)?ms\)) \[L#\d+\]$', r'\1', text, flags=re.MULTILINE)
    return qualified.parse(text)

if __name__ == '__main__':
    result = {'model_calls': 0, 'sample_changed': False, 'runs': {}}
    for name in ['whitfin__cachex-292.base', 'whitfin__cachex-292.gold', 'whitfin__cachex-294.gold']:
        path = ROOT / 'validation_runs/cachex-epmd' / (name + '.log')
        rows = parse(path.read_text())
        names = defaultdict(list)
        for row in rows:
            names[row['test']].append(row['module'])
        collisions = {name: modules for name, modules in names.items() if len(modules) > 1}
        result['runs'][name] = {'log_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                'tests': rows, 'collisions': collisions}
        print(name, len(rows), 'qualified tests;', len(collisions), 'colliding names')
        for name, modules in collisions.items(): print(' ', name, modules)
    result['parser_sha256'] = hashlib.sha256(parser_path.read_bytes()).hexdigest()
    result['adapter_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT / 'findings/cachex-cluster/qualified-results.json').write_text(json.dumps(result, indent=2) + '\n')
