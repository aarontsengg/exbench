"""Record a repaired-production variant, preserving the held original variant."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'findings/broadway-repairs'
sha=lambda b:hashlib.sha256(b).hexdigest()
ref=lambda p:{'path':p,'sha256':sha((ROOT/p).read_bytes())}
r=json.loads((H/'handshake-results-v2.json').read_text());assert r['complete']
t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']=='plataformatec__broadway-95')
assert r['base_commit']==t['base_commit']
assert r['input_hashes']['gold.patch']==sha(t['patch'].encode())
assert r['input_hashes']['tests.patch']==sha(t['test_patch'].encode())
assert r['input_hashes']['handshake.patch']==sha((H/'95-handshake-v2.patch').read_bytes())
assert r['input_hashes']['fixture.patch']==sha((H/'95-repair-v1.patch').read_bytes())
base=r['runs']['42-base']['tests'];gold=r['runs']['42-gold']['tests']
for seed in [42,7,123]:
 assert r['runs'][f'{seed}-base']['tests']==base
 assert r['runs'][f'{seed}-gold']['tests']==gold
 assert r['runs'][f'{seed}-gold']['exit_code']==0
assert len(base)==len(gold)==101 and all(x['status']=='PASSED' for x in gold)
assert {(x['module'],x['test']) for x in base}=={(x['module'],x['test']) for x in gold}
v=json.loads((ROOT/'evaluation_variants/plataformatec__broadway-95--integration-v1.json').read_text())
v.update(variant_id='plataformatec__broadway-95--integration-v2',status='candidate_pending_integration_checks',baseline_category='repaired_production_behavioral_transition',
 production_patch=ref('findings/broadway-repairs/95-handshake-v2.patch'),
 shared_patch=ref('findings/broadway-repairs/95-repair-v1.patch'),
 evidence=[ref('findings/broadway-repairs/handshake-results-v2.json'),ref('findings/broadway-repairs/handshake-summary-v2.json')],
 variant_expected={key:[{'module':x['module'],'test':x['test']} for x in base if x['status']==status] for key,status in [('FAIL_TO_PASS','FAILED'),('PASS_TO_PASS','PASSED')]},
 notes='Production shutdown handshake and already-dead-supervisor repair applied BEFORE candidate patches. V1 test compatibility repairs only; no readiness warm-ups or trace instrumentation. Separate from unmodified upstream benchmark. Future agents must receive the repaired checkout and task issue/interface. Original sample eligibility unchanged. Candidate overlap conflicts are setup failures, not scored agent failures.')
assert len(v['variant_expected']['FAIL_TO_PASS'])==19
(ROOT/'evaluation_variants'/ (v['variant_id']+'.json')).write_text(json.dumps(v,indent=2)+'\n')
print(v['variant_id'])
