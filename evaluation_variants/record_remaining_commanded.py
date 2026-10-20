"""Record reviewed historical variants only after both seed checks pass."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TASKS=json.loads((ROOT/'validation_inputs/tasks.json').read_text())

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def main():
 for n,count in [(290,212),(380,360)]:
  evidence='findings/commanded-batch/remaining-three'+('-fixtures' if n!=380 else '')+'-results.json'
  report=json.loads((ROOT/evidence).read_text());assert report['complete']
  item=report['tasks'][str(n)]
  task=next(t for t in TASKS if t['instance_id']==f'commanded__commanded-{n}')
  parser='findings/commanded-batch/parse_qualified_historical.py'
  assert report['parser_sha256']==sha(parser)
  assert item['base_commit']==task['base_commit']
  for field,key in [('test_patch','test_patch_sha256'),('patch','reference_patch_sha256')]:
   assert hashlib.sha256(task[field].encode()).hexdigest()==item[key]
  for seed in [42,7]:
   for phase in ['base','gold']:
    run=item['runs'][f'{seed}-{phase}']
    assert 'error' not in run and sha(run['log'])==run['log_sha256']
    assert len(run['tests'])==count
    assert run['exit_code'] in ([0] if phase=='gold' else [1,2])
    assert run['tests']==item['runs'][f'42-{phase}']['tests']
  base=item['runs']['42-base']['tests'];gold=item['runs']['42-gold']['tests']
  assert all(r['status']=='PASSED' for r in gold)
  assert [(r['module'],r['test']) for r in base]==[(r['module'],r['test']) for r in gold]
  expected=set(task['FAIL_TO_PASS'])
  moved=[]
  if n==335:
   moved=['process manager subscription should monitor subscription and terminate process manager on shutdown']
   expected-=set(moved)
  failed=[r for r in base if r['status']=='FAILED']
  assert {r['test'] for r in failed}==expected
  if 'fixture' in item:assert sha(item['fixture']['path'])==item['fixture']['sha256']
  variant={'variant_id':task['instance_id']+'--historical-reviewed-v1','upstream_instance_id':task['instance_id'],
   'dataset':json.loads((ROOT/'dataset_config.json').read_text()),'status':'two_seed_diagnostic_transition_verified',
   'selected_for_final_sample':False,'image_id':item['image_id'],'base_commit':item['base_commit'],
   'platform':'linux/amd64','network':'none','start_epmd':True,'shared_patch':item.get('fixture'),
   'parser':{'path':parser,'sha256':sha(parser),'identity':['module','test'],'requires_serial_trace':True},
   'prompt_fields':['problem_statement','interface'],'interface_sha256':hashlib.sha256(task['interface'].encode()).hexdigest(),
   'upstream_expected':{k:task[k] for k in ['FAIL_TO_PASS','PASS_TO_PASS']},
   'variant_expected':{k:[{'module':r['module'],'test':r['test']} for r in base if r['status']==status] for k,status in [('FAIL_TO_PASS','FAILED'),('PASS_TO_PASS','PASSED')]},
   'moved_to_regression_after_fixture_review':moved,'raw_test_count':count,
   'evidence':{'path':evidence,'sha256':sha(evidence)},'audit':'findings/commanded-batch/REMAINING_THREE_AUDIT.md',
   'limitations':['Post-hoc historical runtime variant, not unchanged upstream validation.','Two seed runs under amd64 emulation do not establish a flakiness rate.','Failure assertions reviewed; retained complete regression inventory not exhaustively audited for fairness.','Local patch grader currently supports #171 only; this variant is not yet integrated.']}
  if n==290:variant['limitations'].append('Explicit-stop tests install monitors after stop dispatch; possible race not observed in these repaired runs.')
  if n==335:variant['limitations'].append('Most failures exercise documented process_instance return-contract changes; not 18 independent empty-list behavior checks.')
  (ROOT/'evaluation_variants'/(variant['variant_id']+'.json')).write_text(json.dumps(variant,indent=2)+'\n')
  print(n,count,'tests,',len(failed),'reviewed transitions')

if __name__=='__main__':main()
