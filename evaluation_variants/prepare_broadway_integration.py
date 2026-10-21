import json,hashlib,difflib,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]; H=R/'findings/broadway-repairs'
sha=lambda b:hashlib.sha256(b).hexdigest()
ref=lambda p:{'path':p,'sha256':sha((R/p).read_bytes())}
t=next(t for t in json.load(open('validation_inputs/tasks.json')) if t['instance_id']=='plataformatec__broadway-95')
e=json.loads((H/'cancellation-results-v2.json').read_text())
b=e['runs']['42-base']['tests'];g=e['runs']['42-gold']['tests']
assert b==e['runs']['7-base']['tests'] and g==e['runs']['7-gold']['tests']
assert len(g)==101 and all(x['status']=='PASSED' for x in g)
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)/'test/broadway_test.exs';p.parent.mkdir();p.write_bytes((H/'95-original-test.exs').read_bytes())
 patch=''.join('diff --git '+s for s in t['test_patch'].split('diff --git ')[1:] if s.startswith('a/test/broadway_test.exs '))
 subprocess.run(['git','apply','-'],input=patch,text=True,cwd=temp,check=True)
 before=p.read_text()
 for f in ['95-repair-v1.patch','95-readiness-v2.patch']:
  subprocess.run(['git','apply','-'],input=(H/f).read_text(),text=True,cwd=temp,check=True)
 diff=''.join(difflib.unified_diff(before.splitlines(True),p.read_text().splitlines(True),fromfile='a/test/broadway_test.exs',tofile='b/test/broadway_test.exs'))
 (R/'evaluation_variants/repairs/broadway-95-v1.patch').write_text(diff)
v={'variant_id':t['instance_id']+'--integration-v1','upstream_instance_id':t['instance_id'],'status':'candidate_pending_integration_checks','selected_for_final_sample':False,'dataset':json.load(open('dataset_config.json')),'base_commit':t['base_commit'],'image_id':e['image_id'],'workdir':'/broadway','include_distributed':False,'platform':'linux/amd64','network':'none','start_epmd':True,'erl_flags_override':'+JMsingle true','shared_patch':ref('evaluation_variants/repairs/broadway-95-v1.patch'),'parser':ref('findings/broadway-repairs/parse_trace.py'),'parser_dependencies':[ref('findings/cachex-cluster/audit_identities.py'),ref('findings/commanded-batch/parse_qualified_historical.py')],'evidence':[ref('findings/broadway-repairs/cancellation-results-v2.json')],'baseline_category':'versioned_behavioral_transition','test_patch_sha256':sha(t['test_patch'].encode()),'reference_patch_sha256':sha(t['patch'].encode()),'interface_sha256':sha(t['interface'].encode()),'prompt_fields':['problem_statement','interface'],'variant_expected':{k:[{'module':r['module'],'test':r['test']} for r in b if r['status']==s] for k,s in [('FAIL_TO_PASS','FAILED'),('PASS_TO_PASS','PASSED')]},'raw_test_count':101,'notes':'Versioned fixture synchronization: cancellation after successful full-batch acknowledgement, not immediate startup/shutdown coverage. Also retains v1 exception-type and trap-exit repairs. Observed 19 baseline failures include an additional specified test_messages/3 failure. Upstream lists and final sample unchanged.'}
(R/'evaluation_variants'/ (v['variant_id']+'.json')).write_text(json.dumps(v,indent=2)+'\n')
