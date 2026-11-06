import resource,time
from app import create_app
app=create_app();app.config['TESTING']=True;c=app.test_client()
for op,p in [('create_table',{'capacity':64}),('keys',{}),('stats',{}),('insert',{'key':-2147483648,'value':2147483647}),('get',{'key':-2147483648}),('values',{}),('stats',{})]:
 print('START',op,resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,flush=True)
 t=time.time();r=c.post('/hash/hash_table/operate',json={'operation':op,'payload':p})
 print('END',op,r.status_code,len(r.data),time.time()-t,resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,flush=True)
 del r
