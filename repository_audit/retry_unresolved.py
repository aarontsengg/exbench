"""Retry unresolved identities without discarding successful audit records."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

path = Path(__file__).with_name('github_identities.json')
audit = json.loads(path.read_text())
for record in audit['repositories']:
    if record['status'] == 'verified':
        continue
    try:
        request = urllib.request.Request(record['source_url'], headers={'User-Agent': 'ExBench-repository-audit'})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
            record.update(status='verified', resolved_url=response.url,
                          github_repository_id=data['id'], full_name=data['full_name'],
                          fork=data['fork'], archived=data['archived'],
                          parent_id=(data.get('parent') or {}).get('id'),
                          parent_name=(data.get('parent') or {}).get('full_name'),
                          source_id=(data.get('source') or {}).get('id'),
                          checked_at=datetime.now(timezone.utc).isoformat())
            record.pop('error', None)
    except Exception as error:
        record['error'] = str(error)
    path.write_text(json.dumps(audit, indent=2) + '\n')
    print(record['dataset_repo'], record['status'], record.get('full_name', record.get('error')), flush=True)
