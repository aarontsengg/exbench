"""Verify the latest local controls; preserve definitions and earlier failures."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
choices={139:('','v1'),171:('-final-171','v3'),290:('-followups','v2'),335:('-followups','v2'),380:('-final-380','v3')}
summary={'date':'2026-10-19','model_calls':0,'selected_for_final_sample':False,'tasks':{},'known_caveat':'The historical #171 deposit timeout has not been causally explained; repaired fixture checks do not prove absence of all intermittent failures.'}
for n,(suffix,version) in choices.items():
 path=f'findings/grader/all-commanded-integration{suffix}.json';report=json.loads((ROOT/path).read_text());assert report['complete']
 variant=f'evaluation_variants/commanded__commanded-{n}--integration-{version}.json'
 v=json.loads((ROOT/variant).read_text());vh=hashlib.sha256((ROOT/variant).read_bytes()).hexdigest()
 task=next(t for t in tasks if t['instance_id']==v['upstream_instance_id'])
 assert hashlib.sha256(task['patch'].encode()).hexdigest()==v['reference_patch_sha256']
 reference=''.join('diff --git '+b for b in task['patch'].split('diff --git ') if b.startswith('a/lib/'))
 assert set(report['tasks'][str(n)])=={'42-empty','42-reference','7-empty','7-reference'}
 expected={(r['module'],r['test']) for r in v['variant_expected']['FAIL_TO_PASS']}
 inventories={}
 for key,entry in report['tasks'][str(n)].items():
  data=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==entry['sha256']
  r=json.loads(data);assert r==entry['result'] and r['variant_sha256']==vh
  submitted=reference if key.endswith('reference') else ''
  assert r['candidate_sha256']==hashlib.sha256(submitted.encode()).hexdigest()
  log=(ROOT/entry['path']).parent/'test.log';assert hashlib.sha256(log.read_bytes()).hexdigest()==r['log_sha256']
  assert len(r['tests'])==v['raw_test_count']
  assert not r['missing'] and not r['unexpected']
  if key.endswith('reference'):assert r['resolved'] and not r['failed'] and r['exit_code']==0
  else:assert not r['resolved'] and set(map(tuple,r['failed']))==expected and r['exit_code'] in [1,2]
  phase=key.split('-',1)[1]
  if phase in inventories:assert inventories[phase]==r['tests']
  inventories[phase]=r['tests']
 summary['tasks'][str(n)]={'variant':variant,'sha256':vh,'tests':v['raw_test_count'],'expected_base_failures':len(expected),'gold_failures':0,'seeds':[42,7],'status':'local_controls_verified','evidence':{'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}}
 print(n,'verified',v['raw_test_count'],'tests;',len(expected),'expected base failures')
(ROOT/'findings/grader/commanded-integration-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
