import concurrent.futures,json,urllib.request,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
tasks=[t for t in json.load(open(root/'validation_inputs/tasks.json')) if 'commanded' in t['instance_id']]
def fetch(pair):
 t,path=pair
 url=f"https://raw.githubusercontent.com/commanded/commanded/{t['base_commit']}/{path}"
 try:
  data=urllib.request.urlopen(url,timeout=45).read()
  dest=Path(__file__).parent/t['instance_id']/path
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  return {'task':t['instance_id'],'path':path,'url':url,'sha256':hashlib.sha256(data).hexdigest()}
 except Exception as e:return {'task':t['instance_id'],'path':path,'url':url,'error':str(e)}
paths=['.travis.yml','mix.exs','mix.lock','test/subscriptions/distributed_subscriptions_test.exs']
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: results=list(pool.map(fetch,[(t,p) for t in tasks for p in paths]))
(Path(__file__).parent/'sources.json').write_text(json.dumps(results,indent=2)+'\n')
for x in results:print(x['task'],x['path'],x.get('error','saved'))
