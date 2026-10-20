"""Adapt monitor synchronization to #380's nested Subscription struct."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'evaluation_variants/commanded__commanded-380--integration-v2.json'
variant = json.loads(source.read_text())
patch = (ROOT / variant['shared_patch']['path']).read_text()
old = '%{subscription_ref: ref} = :sys.get_state(pid)'
assert patch.count(old) == 2
patch = patch.replace(old, '%{subscription: %{subscription_ref: ref}} = :sys.get_state(pid)')
path = 'evaluation_variants/repairs/commanded-380-v3.patch'
(ROOT / path).write_text(patch)
variant['variant_id'] = 'commanded__commanded-380--integration-v3'
variant['shared_patch'] = {'path': path, 'sha256': hashlib.sha256(patch.encode()).hexdigest()}
variant['notes'] += ' Monitor references reside in the nested Subscription struct in this revision; v3 corrects the v2 helper pattern.'
(ROOT / 'evaluation_variants' / (variant['variant_id'] + '.json')).write_text(json.dumps(variant, indent=2) + '\n')
