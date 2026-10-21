"""Record separate Cachex variants; do not infer baseline outcomes for #294."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def ref(path):
    return {'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
evidence_path = 'findings/cachex-cluster/historical-results.json'
evidence = json.loads((ROOT/evidence_path).read_text())
assert evidence['complete']
for task in json.loads((ROOT/'validation_inputs/tasks.json').read_text()):
    ident = task['instance_id']
    if ident not in evidence['tasks']: continue
    record = evidence['tasks'][ident]
    assert record['base_commit'] == task['base_commit']
    for field in ['patch','test_patch']:
        assert record[field+'_sha256'] == hashlib.sha256(task[field].encode()).hexdigest()
    gold = record['runs']['42-gold']['tests']
    assert gold == record['runs']['7-gold']['tests']
    assert all(r['status']=='PASSED' for r in gold)
    if ident.endswith('-292'):
        base = record['runs']['42-base']['tests']
        assert base == record['runs']['7-base']['tests']
        expected = {key: [{'module':r['module'],'test':r['test']} for r in base if r['status']==status]
                    for key,status in [('FAIL_TO_PASS','FAILED'),('PASS_TO_PASS','PASSED')]}
        category = 'behavioral_transition_verified'
    else:
        expected = {'REQUIRED_PASS': [{'module':r['module'],'test':r['test']} for r in gold]}
        category = 'expected_api_compile_failure_candidate'
    variant = {'variant_id': ident+'--historical-integration-v1', 'upstream_instance_id':ident,
               'status':'candidate_pending_integration_checks','selected_for_final_sample':False,
               'dataset':json.loads((ROOT/'dataset_config.json').read_text()),
               'base_commit':task['base_commit'],'image_id':record['image_id'],
               'workdir':'/cachex','include_distributed':False,'platform':'linux/amd64',
               'network':'none','start_epmd':True,'erl_flags_in_image':'+JPperf true',
               'parser':ref('findings/cachex-cluster/audit_identities.py'),
               'parser_dependencies':[ref('findings/commanded-batch/parse_qualified_historical.py')],
               'evidence':[ref(evidence_path)],'baseline_category':category,
               'test_patch_sha256':record['test_patch_sha256'],'reference_patch_sha256':record['patch_sha256'],
               'prompt_fields':['problem_statement','interface'],'interface_sha256':hashlib.sha256(task['interface'].encode()).hexdigest(),
               'variant_expected':expected,'raw_test_count':len(gold),
               'notes':'Unchanged upstream tests. REQUIRED_PASS is a gold inventory, not a claim about individual baseline transitions. No final sample or original validation changes.'}
    path=ROOT/'evaluation_variants'/(variant['variant_id']+'.json')
    path.write_text(json.dumps(variant,indent=2)+'\n')
    print(path.name, category, len(gold))
