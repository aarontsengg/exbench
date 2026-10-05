"""Snapshot public GitHub repository identities; no credentials or model calls."""
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent.parent
repos = sorted(json.loads((root / 'elixir_profile.json').read_text())['tasks_per_repository'])

def check(repo):
    url = f'https://api.github.com/repos/{repo}'
    record = {'dataset_repo': repo, 'source_url': url}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'ExBench-repository-audit', 'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
            record.update(status='verified', resolved_url=response.url,
                          github_repository_id=data['id'], full_name=data['full_name'],
                          fork=data['fork'], archived=data['archived'],
                          parent_id=(data.get('parent') or {}).get('id'),
                          parent_name=(data.get('parent') or {}).get('full_name'),
                          source_id=(data.get('source') or {}).get('id'))
    except (urllib.error.URLError, TimeoutError) as error:
        record.update(status='unresolved', error=str(error))
    return record

with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(check, repos))
output = {'checked_at': datetime.now(timezone.utc).isoformat(), 'repositories': records}
(root / 'repository_audit/github_identities.json').write_text(json.dumps(output, indent=2) + '\n')
for record in records:
    if record['status'] != 'verified' or record['dataset_repo'].lower() != record.get('full_name', '').lower() or record.get('fork'):
        print(json.dumps(record))
print('Verified:', sum(r['status'] == 'verified' for r in records), '/', len(records))
