"""Smoke-test the shared grader with empty and reference submissions; no agents."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'validation_runs/cachex-grader';out.mkdir(exist_ok=False)
tasks=json.loads((ROOT/'validation_inputs/tasks.json').read_text())
report={'model_calls':0,'seed':42,'complete':False,'tasks':{}}
for n in [292,294]:
    ident=f'whitfin__cachex-{n}';task=next(t for t in tasks if t['instance_id']==ident)
    variant=f'evaluation_variants/{ident}--historical-integration-v1.json'
    manifest=json.loads((ROOT/variant).read_text())
    assert hashlib.sha256(task['patch'].encode()).hexdigest()==manifest['reference_patch_sha256']
    folder=out/ident;folder.mkdir()
    (folder/'empty.patch').write_text('')
    reference=''.join('diff --git '+b for b in task['patch'].split('diff --git ')[1:] if b.startswith('a/lib/'))
    assert reference
    (folder/'reference.patch').write_text(reference)
    report['tasks'][ident]={}
    for phase in ['empty','reference']:
        dest=folder/phase
        print(ident,phase,'started',flush=True)
        subprocess.run([sys.executable,str(ROOT/'grade_patch.py'),'--variant',variant,'--patch',str(folder/(phase+'.patch')),'--seed','42','--output',str(dest)],cwd=ROOT,check=True)
        raw=(dest/'result.json').read_bytes();result=json.loads(raw)
        assert result['candidate_sha256']==hashlib.sha256((folder/(phase+'.patch')).read_bytes()).hexdigest()
        if phase=='reference':
            assert result['resolved'] and result['exit_code']==0
            assert len(result['tests'])==manifest['raw_test_count']
        else:
            assert not result['resolved'] and result['exit_code']!=0
            if n==292:
                assert result['failed']==[['Cachex.Services.CourierTest','gracefully handling crashes inside tasks']]
                assert not result['missing'] and not result['unexpected']
            else:
                assert 'record :warmer does not have the key: :async' in (dest/'test.log').read_text()
        report['tasks'][ident][phase]={'result':result,'result_sha256':hashlib.sha256(raw).hexdigest(),'path':str((dest/'result.json').relative_to(ROOT))}
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
report['complete']=True
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'findings/cachex-cluster/grader-results.json').write_text(json.dumps(report,indent=2)+'\n')
