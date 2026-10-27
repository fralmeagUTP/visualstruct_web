"""Independent Mostrar oracles only; product remains unchanged."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil,io,contextlib,tracemalloc,time
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8');E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-queue-show-baseline-low'
from app import create_app
from app.config import Config
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService
from app.domain.sequential import tad_pila as S,tad_cola as Q
from app.adapters.stack_adapter import StackAdapter
from app.adapters.queue_adapter import QueueAdapter
CASES=[('empty',[]),('single',[17]),('multiple',[17,9,3]),('duplicate',[7,7]),('minus1',[-1]),('minus1-front',[-1,17]),('minus1-rear',[17,-1]),('bounds',[-2147483648,0,2147483647]),('bounds-reverse',[2147483647,0,-2147483648])]
class C(Config):
 TESTING=True
 SESSION_CACHE_DIR=str(E/'private-sessions')
app=create_app(C);downloads=[];reports=[];resources=[]
for sid,stem,typ in [('stack','pila','NodoPila'),('queue','cola','NodoCola')]:
 N=E/('native-'+sid);N.mkdir(exist_ok=True);fixtures=CASES+([('front-only',[19]),('rear-only',[19])] if sid=='queue' else [])
 for kind,ext in [('source','c'),('header','h')]:
  r=app.test_client().get('/help/source/'+sid+'/'+kind);assert r.status_code==200 and r.data==(R/'docs/tads_C'/('tad_'+stem+'.'+ext)).read_bytes();(N/('tad_'+stem+'.'+ext)).write_bytes(r.data);downloads.append({'structure':sid,'kind':kind,'HTTP':200,'SHA256':hashlib.sha256(r.data).hexdigest()})
 source=(N/('tad_'+stem+'.c')).read_text(encoding='utf-8-sig');signature='void '+stem+'_mostrar('+('ptrPila p' if sid=='stack' else 'struct Cola q')+')';at=source.index(signature);opening=source.index('{',at);level=1;end=opening+1
 while level:
  level+=(source[end]=='{')-(source[end]=='}');end+=1
 body=source[at:end];(N/'original-function.txt').write_text(body,encoding='utf-8')
 instrument=body.replace('{','{\n    qa_entry('+('p, NULL, &p' if sid=='stack' else 'q.delante, q.atras, &q')+');',1)
 decl='ptrPila aux = p;' if sid=='stack' else 'struct NodoCola *aux = q.delante;';instrument=instrument.replace(decl,decl+'\n    qa_event("declare",aux,1,-1);')
 instrument=instrument.replace('if (aux == NULL)', 'if (qa_condition("if",aux,aux == NULL))').replace('while (aux != NULL)', 'while (qa_condition("while",aux,aux != NULL))')
 instrument=instrument.replace('printf(', 'qa_printf(').replace('aux = aux->sgte;', 'aux = aux->sgte;\n        qa_event("advance",aux,1,-1);')
 instrument=instrument.replace('return;', 'qa_event("return",aux,1,-1);\n        return;');instrument=instrument[:-1]+'    qa_event("end",aux,1,-1);\n}';(N/'instrumented.c').write_text(source[:at]+instrument+source[end:],encoding='utf-8')
 hook='struct '+typ+';\nvoid qa_entry(struct '+typ+'*,struct '+typ+'*,void*);\nvoid qa_event(const char*,struct '+typ+'*,int,int);\nint qa_condition(const char*,struct '+typ+'*,int);\nvoid qa_printf(const char*,...);\n';(N/'hooks.h').write_text(hook,encoding='utf-8')
 driver=r"""#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include "HEADER"
#define NODE struct TYPE
static NODE *nodes,*front,*rear,*current_aux;
static int count,fixture,sample;
static void *caller_address;
static char output[4096];
static int identity(NODE *p) { if(p==NULL){return -1;} for(int i=0;i<count;i++){if(p==&nodes[i]){return i;}} assert(0);return -2; }
static void json_string(const char *s) { putchar('"');for(;*s;s++){if(*s=='\n'){printf("\\n");}else if(*s=='\t'){printf("\\t");}else if(*s=='"'||*s=='\\'){putchar('\\');putchar(*s);}else{putchar(*s);}}putchar('"'); }
void qa_event(const char *phase,NODE *aux,int initialized,int condition) {
 printf("{\"method\":\"METHOD\",\"fixture\":%d,\"sample\":%d,\"phase\":",fixture,sample);json_string(phase);
 printf(",\"aux_initialized\":%d,\"aux_id\":%d,\"condition\":%d,\"front_id\":%d,\"rear_id\":%d,\"console\":",initialized,initialized?identity(aux):-2,condition,identity(front),identity(rear));json_string(output);printf(",\"nodes\":[");
 for(int i=0;i<count;i++){if(i){putchar(',');}printf("{\"id\":%d,\"nro\":%d,\"next_id\":%d}",i,nodes[i].nro,identity(nodes[i].sgte));}printf("]}\n");current_aux=aux;
}
void qa_entry(NODE *f,NODE *r,void *parameter_address) {assert(f==front&&r==rear&&parameter_address!=caller_address);qa_event("entry",NULL,0,-1);}
int qa_condition(const char *phase,NODE *aux,int result) {qa_event(phase,aux,1,result);return result;}
void qa_printf(const char *format,...) {size_t n=strlen(output);va_list ap;va_start(ap,format);int written=vsnprintf(output+n,sizeof(output)-n,format,ap);va_end(ap);assert(written>=0&&(size_t)written<sizeof(output)-n);qa_event("printf",current_aux,1,-1);}
static void run(PARAM q) {
 int old_values[8];NODE *old_links[8];for(int i=0;i<count;i++){old_values[i]=nodes[i].nro;old_links[i]=nodes[i].sgte;}
 caller_address=&q;
 for(int repeat=0;repeat<2;repeat++){output[0]=0;current_aux=NULL;CALL;ASSERT_ROOTS;for(int i=0;i<count;i++){assert(nodes[i].nro==old_values[i]&&nodes[i].sgte==old_links[i]);}sample++;}
 caller_address=NULL;
}
int main(void) {
 _Static_assert(_Generic(&METHOD,void (*)(PARAM):1,default:0),"exact void byvalue signature");
""".replace('HEADER','tad_'+stem+'.h').replace('TYPE',typ).replace('METHOD',stem+'_mostrar').replace('PARAM','ptrPila' if sid=='stack' else 'struct Cola').replace('CALL',stem+'_mostrar(q)').replace('ASSERT_ROOTS','assert(q==front)' if sid=='stack' else 'assert(q.delante==front&&q.atras==rear)')
 for fi,(name,values) in enumerate(fixtures):
  driver+=' {fixture='+str(fi)+';count='+str(len(values))+';'
  if values:
   driver+='NODE fixture_nodes['+str(len(values))+'];nodes=fixture_nodes;'
   for ni,v in enumerate(values):
    literal='INT_MIN' if v==-2147483648 else 'INT_MAX' if v==2147483647 else str(v);link='&fixture_nodes['+str(ni+1)+']' if ni+1<len(values) else 'NULL';driver+=f'nodes[{ni}].nro={literal};nodes[{ni}].sgte={link};'
   driver+='front='+('NULL' if name=='rear-only' else '&nodes[0]')+';rear='+('NULL' if name=='front-only' else '&nodes['+str(len(values)-1)+']')+';'
  else:driver+='nodes=NULL;front=NULL;rear=NULL;'
  if sid=='stack':driver+='rear=NULL;'
  driver+=('ptrPila q=front;' if sid=='stack' else 'struct Cola q={front,rear};')+'run(q);}\n'
 driver+='return 0;}\n';(N/'driver.c').write_text(driver,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
 for label,cmd in [('source',flags+['-include',str(N/'hooks.h'),'-c',str(N/'instrumented.c'),'-o',str(N/'tad.o')]),('driver',flags+[str(N/'driver.c'),str(N/'tad.o'),'-o',str(N/'driver.exe')])]:
  r=subprocess.run(cmd,capture_output=True,text=True);(N/(label+'-compile.log')).write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
 r=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(r.stdout,encoding='utf-8');(N/'stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr;events=[json.loads(x) for x in r.stdout.splitlines()]
 for fi,(name,values) in enumerate(fixtures):
  ns=[x for x in events if x['fixture']==fi];native_outputs=[x['console'] for x in ns if x['phase'] in ['end','return']];assert len(native_outputs)==2 and native_outputs[0]==native_outputs[1];expected=('Pila vacia.\n' if not values else ''.join('\t'+str(v)+'\n' for v in values)) if sid=='stack' else 'Cola: '+''.join(str(v)+' ' for v in ([] if name=='rear-only' else values))+'\n';assert native_outputs==[expected]*2
  raw=S if sid=='stack' else Q;nodes=[getattr(raw,typ)(v) for v in values]
  for i,n in enumerate(nodes):n.sgte=nodes[i+1] if i+1<len(nodes) else None
  q=(nodes[0] if nodes else None) if sid=='stack' else Q.Cola(nodes[0] if nodes and name!='rear-only' else None,nodes[-1] if nodes and name!='front-only' else None)
  roots=(id(q),None,None) if sid=='stack' else (id(q),id(q.delante),id(q.atras));snap=[(id(n),n.nro,id(n.sgte)) for n in nodes];outs=[]
  for _ in range(2):
   buf=io.StringIO()
   with contextlib.redirect_stdout(buf):result=getattr(raw,stem+'_mostrar')(q)
   assert result is None;outs.append(buf.getvalue());assert [(id(n),n.nro,id(n.sgte)) for n in nodes]==snap;assert roots==((id(q),None,None) if sid=='stack' else (id(q),id(q.delante),id(q.atras)))
  record={'structure':sid,'method':stem+'_mostrar','case':name,'values_order':values,'native':ns,'native_outputs':native_outputs,'raw_outputs':outs,'raw_console_equal':outs==native_outputs,'raw_readonly':True,'raw_return':None,'private_inconsistent_roots':name in ['front-only','rear-only']}
  if not record['private_inconsistent_roots']:
   a=(StackAdapter if sid=='stack' else QueueAdapter)()
   for value in (list(reversed(values)) if sid=='stack' else values):a.execute('apilar' if sid=='stack' else 'encolar',{'value':value})
   state=a.to_visual_state();assert [x['value'] for x in state['items']]==values;record['visual']=state
   try:a.execute('mostrar',{});record['adapter_error']=None
   except Exception as error:record['adapter_error']=type(error).__name__
   tracemalloc.start();start=time.perf_counter();trace=ExecutionTraceService.build_trace(structure_id=sid,operation_name='mostrar',payload={},didactic_data=StructureService._didactic_content(sid),before_state=state,after_state=state,success=True,message='private C mostrar baseline',mutates=False,console_events=[]);peak=tracemalloc.get_traced_memory()[1];elapsed=time.perf_counter()-start;tracemalloc.stop();record['private_trace']=trace;resources.append({'method':record['method'],'case':name,'scope':'private_generic_trace_Cextract_JSON_noHTTPsession','peak_bytes':peak,'seconds':elapsed,'JSON_bytes':len(json.dumps(trace,ensure_ascii=False).encode('utf-8'))})
   client=app.test_client()
   for value in (list(reversed(values)) if sid=='stack' else values):assert client.post('/sequential/'+sid+'/operate',json={'operation':'apilar' if sid=='stack' else 'encolar','payload':{'value':value}}).get_json()['success']
   from unittest.mock import patch
   cls=StackAdapter if sid=='stack' else QueueAdapter;orig=cls.execute;target=[]
   def observe(self,op,payload):
    if op=='mostrar':target.append(op)
    return orig(self,op,payload)
   rejected=[]
   with patch.object(cls,'execute',observe):
    tracemalloc.start();start=time.perf_counter()
    for _ in range(2):
     r=client.post('/sequential/'+sid+'/operate',json={'operation':'mostrar','payload':{}});d=r.get_json();assert r.status_code==400 and not d['success'] and d['visual_state']==state;assert not any(x['operation']=='mostrar' for x in d['history']);rejected.append({'HTTP':400,'data':d})
    peak=tracemalloc.get_traced_memory()[1];elapsed=time.perf_counter()-start;tracemalloc.stop();resources.append({'method':record['method'],'case':name,'scope':'two_rejected_POSTs_session_replay_JSON','peak_bytes':peak,'seconds':elapsed,'JSON_bytes':len(r.data)});assert client.get('/sequential/'+sid).status_code==200 and client.get('/sequential/'+sid).status_code==200 and target==[]
   record.update(rejected=rejected,not_registered=not any(o['name']=='mostrar' for o in a.get_supported_operations()),POST_GET_target=0,journal_query=0)
  reports.append(record)
 summary={'method':stem+'_mostrar','calls':2*len(fixtures),'events':len(events),'conditions':sum(x['phase'] in ['if','while'] for x in events),'printf_events':sum(x['phase']=='printf' for x in events),'raw_equal_cases':sum(x['raw_console_equal'] for x in reports if x['structure']==sid),'raw_cases':len(fixtures)};(E/(sid+'-native-summary.json')).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(summary)
(E/'report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'downloads.json').write_text(json.dumps(downloads,indent=2)+'\n',encoding='utf-8');(E/'resources.json').write_text(json.dumps({'samples':resources,'limits':'Finite per-method/privategenerictraces vs rejected API; no acceptedquery/RSS/browsermemory/unboundedhistory/SLA/OOM/sanitizer proof.'},indent=2)+'\n',encoding='utf-8')
