"""Fetch runtime and assertion sources at each pinned task base commit."""
import hashlib
import json
import urllib.request
import urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
results = []
for task in json.loads((ROOT / 'validation_inputs/tasks.json').read_text()):
    if task['instance_id'] not in ['whitfin__cachex-292', 'whitfin__cachex-294']:
        continue
    for path in ['.travis.yml', '.github/workflows/main.yml', '.github/workflows/ci.yml', 'mix.exs', 'mix.lock', 'test/cachex/actions/inspect_test.exs', 'test/cachex/actions/refresh_test.exs']:
        url = f"https://raw.githubusercontent.com/whitfin/cachex/{task['base_commit']}/{path}"
        entry = {'task': task['instance_id'], 'path': path, 'url': url}
        try:
            data = urllib.request.urlopen(url, timeout=30).read()
            dest = Path(__file__).parent / task['instance_id'] / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            entry['sha256'] = hashlib.sha256(data).hexdigest()
        except urllib.error.HTTPError as error:
            if error.code != 404: raise
            entry['status'] = 404
        results.append(entry)
        print(task['instance_id'], path, entry.get('status', 'saved'), flush=True)
(Path(__file__).parent / 'sources.json').write_text(json.dumps(results, indent=2) + '\n')
