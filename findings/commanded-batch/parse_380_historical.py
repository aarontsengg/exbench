"""Explicit old-ExUnit log adapter; preserves upstream parser results separately."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def parse(text):
 results={}
 for raw in text.splitlines():
  line=raw.strip()
  # Only completed timed lines, never a bare started-test line.
  m=re.fullmatch(r'\*\s+test\s+(.+?)\s+\([0-9]+(?:\.[0-9]+)?ms\)',line)
  if m:results.setdefault(m[1],'PASSED')
  m=re.fullmatch(r'\d+\)\s+test\s+(.+?)\s+\([^)]+\)',line)
  if m:results[m[1]]='FAILED'
 return results
# Meaningful cases: interrupted tests are absent; failure overrides completion
# regardless of ordering; CR progress output is supported.
assert parse('* test unfinished')=={}
assert parse('* test ok\r* test ok (0.2ms)')=={'ok':'PASSED'}
assert parse('* test bad (1ms)\n 1) test bad (Example)')=={'bad':'FAILED'}
assert parse('1) test bad (Example)\n* test bad (1ms)')=={'bad':'FAILED'}
assert parse('* doctest thing (1ms)')=={}
if __name__=='__main__':
 out=ROOT/'validation_runs/commanded-380-historical'
 r=json.loads((out/'report.json').read_text())
 t=next(t for t in json.loads((ROOT/'validation_inputs/tasks.json').read_text()) if t['instance_id']==r['instance_id'])
 expected=set(t['FAIL_TO_PASS']+t['PASS_TO_PASS'])
 for phase,v in r['phases'].items():
  data=(out/(phase+'.log')).read_bytes();assert hashlib.sha256(data).hexdigest()==v['log_sha256']
  text=data.decode(errors='replace');assert 'EXBENCH_TEST_START_' in text
  parsed=parse(text.split('EXBENCH_TEST_START_',1)[1]);passed=sorted(k for k,s in parsed.items() if s=='PASSED');failed=sorted(k for k,s in parsed.items() if s=='FAILED')
  v['historical_parser']={'passed':passed,'failed':failed,'missing_upstream_ids':sorted(expected-set(parsed)),'extra_ids':sorted(set(parsed)-expected),'raw_summary':re.findall(r'\d+ tests, \d+ failures?',text)}
  print(phase,len(passed),failed,'extra',v['historical_parser']['extra_ids'],'missing',v['historical_parser']['missing_upstream_ids'])
 b,g=(r['phases'][p]['historical_parser'] for p in ['base','gold'])
 r['historical_transition_verified']=b['failed']==sorted(t['FAIL_TO_PASS']) and not g['failed'] and set(g['passed'])==set(b['passed'])|set(t['FAIL_TO_PASS']) and r['phases']['gold']['exit_code']==0
 r['historical_parser_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (ROOT/'findings/commanded-batch/380-historical-result.json').write_text(json.dumps(r,indent=2)+'\n')
