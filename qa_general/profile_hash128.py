import json,resource,time
from app import create_app
from app.domain.hash.snapshot_pool import expand_hash_trace
app=create_app();app.config['TESTING']=True;c=app.test_client()
for op,p in [('create_table',{'capacity':128}),('keys',{}),('stats',{}),('insert',{'key':-2147483648,'value':2147483647}),('get',{'key':-2147483648}),('values',{}),('stats',{})]:
 t=time.time();r=c.post('/hash/hash_table/operate',json={'operation':op,'payload':p})
 print('END',op,r.status_code,len(r.data),time.time()-t,resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,flush=True)
 assert r.status_code==200 and len(r.data)<12_000_000
 if op=='keys':
  wire=r.get_json()['execution_trace'];logical=expand_hash_trace(wire)
  with open('qa_general/hash-codec128-fixture.json','w') as f:json.dump({'wire':wire,'events':[s['event_type'] for s in logical['steps']],'final_state':logical['final_state']},f)
  del logical,wire
 del r
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<400*1024
