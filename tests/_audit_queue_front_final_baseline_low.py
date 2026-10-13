"""Independent readonly query-only native/adapter/private trace/rejected API baselines."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,tracemalloc,time
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from app import create_app
from app.config import Config
from app.adapters.queue_adapter import QueueAdapter
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService
from app.domain.sequential import tad_cola as raw
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-front-final-baseline-low';N=E/'native';N.mkdir(exist_ok=True)
CASES=[('empty',[]),('single',[17]),('fifo',[17,9,3]),('duplicate',[7,7]),('minus1',[-1]),('minus1-front',[-1,17]),('minus1-rear',[17,-1]),('bounds',[-2147483648,0,2147483647]),('bounds-reverse',[2147483647,0,-2147483648])];PRIVATE=[('front-only',[19]),('rear-only',[19])];METHODS=['frente','final']
class Q(Config):
 TESTING=True
 SESSION_CACHE_DIR=str(E/'private-API-sessions')
app=create_app(Q);downloads=[]
for kind,ext in [('source','c'),('header','h')]:
 r=app.test_client().get('/help/source/queue/'+kind);assert r.status_code==200 and r.data==(R/('docs/tads_C/tad_cola.'+ext)).read_bytes();(N/('tad_cola.'+ext)).write_bytes(r.data);downloads.append({'kind':kind,'HTTP':200,'SHA':hashlib.sha256(r.data).hexdigest()})
source=(N/'tad_cola.c').read_text(encoding='utf-8-sig');front='int cola_frente(struct Cola q) {\n    if (q.delante != NULL)\n        return q.delante->nro;\n    else\n        return -1;\n}';rear='int cola_final(struct Cola q) {\n    return q.atras == NULL ? -1 : q.atras->nro;\n}';assert front in source and rear in source
front_p='int cola_frente(struct Cola q) {\n    qa_entry("frente",q);\n    if (qa_condition("frente",q,q.delante != NULL))\n        return qa_return("frente",q,q.delante->nro);\n    else\n        return qa_return("frente",q,-1);\n}';rear_p='int cola_final(struct Cola q) {\n    qa_entry("final",q);\n    return qa_return("final",q,qa_condition("final",q,q.atras == NULL) ? -1 : q.atras->nro);\n}';(N/'instrumented.c').write_text(source.replace(front,front_p).replace(rear,rear_p),encoding='utf-8');(N/'hooks.h').write_text('struct Cola;\nvoid qa_entry(const char*,struct Cola);\nint qa_condition(const char*,struct Cola,int);\nint qa_return(const char*,struct Cola,int);\n',encoding='utf-8')
driver=r"""#include <assert.h>
#include <stdio.h>
#include <limits.h>
#include <string.h>
#include "tad_cola.h"
_Static_assert(_Generic(&cola_frente,int(*)(struct Cola):1,default:0),"front by-value signature");
_Static_assert(_Generic(&cola_final,int(*)(struct Cola):1,default:0),"final by-value signature");
static struct NodoCola*nodes;static int count,fixture,sample_id;
static int id(struct NodoCola*p){if(!p)return -1;for(int i=0;i<count;i++)if(p==&nodes[i])return i;assert(0);return -1;}
static void event(const char*method,struct Cola q,const char*phase,int condition,int result,int written){
 _Static_assert(_Generic(q,struct Cola:1,default:0),"q is struct value, not pointer or const");
 printf("{\"method\":\"%s\",\"fixture\":%d,\"sample\":%d,\"phase\":\"%s\",\"condition\":%d,\"result\":%d,\"written\":%d,\"front_id\":%d,\"rear_id\":%d,\"nodes\":[",method,fixture,sample_id,phase,condition,result,written,id(q.delante),id(q.atras));
 for(int i=0;i<count;i++){if(i)putchar(',');printf("{\"id\":%d,\"nro\":%d,\"next_id\":%d}",i,nodes[i].nro,id(nodes[i].sgte));}puts("]}");
}
void qa_entry(const char*m,struct Cola q){event(m,q,"entry",-1,0,0);}
int qa_condition(const char*m,struct Cola q,int c){event(m,q,"condition",c,0,0);return c;}
int qa_return(const char*m,struct Cola q,int v){event(m,q,"return",-1,v,1);return v;}
static void query(struct Cola q,const char*method){
 struct Cola saved=q;int values[8];struct NodoCola*links[8];for(int i=0;i<count;i++){values[i]=nodes[i].nro;links[i]=nodes[i].sgte;}
 int expected=strcmp(method,"frente")==0?(q.delante?q.delante->nro:-1):(q.atras?q.atras->nro:-1);
 int result=strcmp(method,"frente")==0?cola_frente(q):cola_final(q);assert(result==expected&&q.delante==saved.delante&&q.atras==saved.atras);
 for(int i=0;i<count;i++){assert(nodes[i].nro==values[i]&&nodes[i].sgte==links[i]);}
 sample_id++;
}
static void both(struct Cola q){query(q,"frente");query(q,"frente");query(q,"final");query(q,"final");fixture++;}
int main(void){
"""
for name,values in CASES+PRIVATE:
 if not values:driver+='nodes=NULL;count=0;{struct Cola q={NULL,NULL};both(q);}\n';continue
 driver+=' {struct NodoCola fixture_nodes['+str(len(values))+'];nodes=fixture_nodes;count='+str(len(values))+';\n'
 for i,v in enumerate(values):
  literal='INT_MIN' if v==-2147483648 else 'INT_MAX' if v==2147483647 else str(v);link='&fixture_nodes['+str(i+1)+']' if i+1<len(values) else 'NULL';driver+=f'fixture_nodes[{i}].nro={literal};fixture_nodes[{i}].sgte={link};\n'
 head='NULL' if name=='rear-only' else '&fixture_nodes[0]';tail='NULL' if name=='front-only' else '&fixture_nodes['+str(len(values)-1)+']';driver+=f'struct Cola q={{{head},{tail}}};both(q);}}\n'
driver+='return 0;}\n';(N/'driver.c').write_text(driver,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for i,cmd in enumerate([flags+['-include',str(N/'hooks.h'),'-c',str(N/'instrumented.c'),'-o',str(N/'cola.o')],flags+[str(N/'driver.c'),str(N/'cola.o'),'-o',str(N/'driver.exe')]]):
 r=subprocess.run(cmd,capture_output=True,text=True);(N/f'compile-{i}.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
r=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(r.stdout,encoding='utf-8');(N/'stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr;native=[json.loads(x) for x in r.stdout.splitlines()];assert len(native)==132
rows=[];private_rows=[];resources=[]
for fi,(name,values) in enumerate(CASES+PRIVATE):
 head=None;tail=None
 for v in reversed(values):head=raw.NodoCola(v,head);tail=head if tail is None else tail
 q=raw.Cola(None if name=='rear-only' else head,None if name=='front-only' else tail)
 for method in METHODS:
  ns=[x for x in native if x['fixture']==fi and x['method']==method];f=getattr(raw,'cola_'+method,None);raw_out=[]
  for _ in range(2):raw_out.append(f(q) if callable(f) else 'missing raw function')
  private_rows.append({'method':method,'case':name,'fixture':fi,'private_inconsistent_roots':name in ['front-only','rear-only'],'native':ns,'native_result':ns[2]['result'],'raw_outputs':raw_out})
  if name in ['front-only','rear-only']:continue
  a=QueueAdapter()
  for v in values:a.execute('encolar',{'value':v})
  state=a.to_visual_state();node=a._structure._cola.delante;before=[];root=(id(a._structure._cola),id(a._structure._cola.delante),id(a._structure._cola.atras),a._structure._tamano)
  while node:before.append((id(node),node.nro,id(node.sgte)));node=node.sgte
  outputs=[];traces=[]
  for repeat in range(2):
   try:outputs.append({'result':a.execute(method,{})['result']})
   except Exception as error:outputs.append({'exception':type(error).__name__})
   assert a.to_visual_state()==state
   tracemalloc.start();start=time.perf_counter();t=ExecutionTraceService.build_trace(structure_id='queue',operation_name=method,payload={},didactic_data=StructureService._didactic_content('queue'),before_state=state,after_state=state,success=bool(values),message='private adapter query',mutates=False,console_events=[]);JSONsize=len(json.dumps(t,ensure_ascii=False).encode('utf-8'));elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();traces.append(t);resources.append({'method':method,'case':name,'repeat':repeat+1,'scope':'private_trace_build_Cextract_JSON_noHTTPsession','peak_bytes':peak,'JSON_bytes':JSONsize,'seconds':elapsed})
  after=[];node=a._structure._cola.delante
  while node:after.append((id(node),node.nro,id(node.sgte)));node=node.sgte
  assert after==before and root==(id(a._structure._cola),id(a._structure._cola.delante),id(a._structure._cola.atras),a._structure._tamano)
  client=app.test_client()
  for v in values:assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
  from unittest.mock import patch
  original=QueueAdapter.execute;queries=[]
  def observe(self,op,payload):
   if op in METHODS:queries.append(op)
   return original(self,op,payload)
  rejected=[]
  with patch.object(QueueAdapter,'execute',observe):
   tracemalloc.start();start=time.perf_counter()
   for repeat in range(2):
    r=client.post('/sequential/queue/operate',json={'operation':method,'payload':{}});data=r.get_json();assert r.status_code==400 and not data['success'] and data['visual_state']==state;assert not any(x['operation'] in METHODS for x in data['history']);rejected.append({'HTTP':400,'data':data})
   elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();resources.append({'method':method,'case':name,'scope':'two_rejected_HTTP_POSTs_session_replay_serialization','peak_bytes':peak,'JSON_bytes':len(r.data),'seconds':elapsed})
   assert client.get('/sequential/queue').status_code==200 and client.get('/sequential/queue').status_code==200;assert queries==[]
  conditions=[s['pedagogy']['condition'] for s in traces[0]['steps'] if s['pedagogy'].get('condition') is not None]
  rows.append({'method':method,'case':name,'values_FIFO':values,'native':ns,'native_result':ns[2]['result'],'adapter_outputs':outputs,'root_nodes_links_count_readonly':True,'visual':state,'private_traces':traces,'condition_outcome_native_equal':len(conditions)==1 and conditions[0]['result']==bool(ns[1]['condition']),'condition_substitution':conditions[0].get('substituted') if conditions else None,'rejected':rejected,'public_query_dispatch_POST_GET':0,'query_journal':0,'not_registered':not any(x['name']==method for x in a.get_supported_operations())})
summary={}
for method in METHODS:
 summary[method]={}
 for scope in ['private_trace_build_Cextract_JSON_noHTTPsession','two_rejected_HTTP_POSTs_session_replay_serialization']:
  rr=[x for x in resources if x['method']==method and x['scope']==scope];summary[method][scope]={'samples':len(rr),'max_python_peak_bytes':max(x['peak_bytes'] for x in rr),'max_JSON_bytes':max(x['JSON_bytes'] for x in rr),'max_seconds':max(x['seconds'] for x in rr)}
for filename,data in [('report.json',rows),('raw-private-report.json',private_rows),('downloads.json',downloads),('resources.json',{'samples':resources,'by_method_scope':summary,'limits':'Two methods independently, private trace vs rejected API distinct; fixturesfinite including C17privateinconsistentroots outsidepublicAPI. No successqueryAPI/RSS/browser/unboundedhistory/SLA/OOM/sanitizer guarantee.'})]:
 (E/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Native independently each22queries66events22conditions=44/132/44; rawfront11cases matches,rawfinalabsent; adapterprivateeach18calls/9casesreadonly; APIeach18reject400/POSTGETtarget0/nojournal; productunchanged')
