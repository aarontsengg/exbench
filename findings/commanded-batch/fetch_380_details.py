import concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
here=Path(__file__).resolve().parent
paths=['lib/commanded/aggregates/aggregate.ex','lib/commanded/subscriptions.ex','lib/commanded/application.ex','lib/commanded/application/supervisor.ex','test/application/application_test.exs','test/aggregates/aggregate_lifespan_test.exs','test/subscriptions/subscriptions_test.exs','test/serialization/json_decoder_test.exs','lib/commanded/serialization/json_serializer.ex']
def fetch(path):
 url='https://raw.githubusercontent.com/commanded/commanded/4a6df4a3fc3e318805574ca9cab5cef0a83617e3/'+path
 try:
  data=urllib.request.urlopen(url,timeout=45).read();p=here/'commanded__commanded-380'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  return {'path':path,'url':url,'sha256':hashlib.sha256(data).hexdigest()}
 except Exception as e:return {'path':path,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(fetch,paths))
(here/'380-detail-sources.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows: print(r['path'],r.get('error','saved'))
