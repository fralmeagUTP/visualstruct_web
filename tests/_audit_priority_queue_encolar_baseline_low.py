"""Safe native priority enqueue observer; fields read only after their stores."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,time,tracemalloc
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-encolar-baseline-low';N=E/'native';N.mkdir(exist_ok=True)
app=create_app();app.config['TESTING']=True;c=app.test_client();downloads={}
for kind,ext in [('source','c'),('header','h')]:
 r=c.get('/help/source/priority_queue/'+kind);assert r.status_code==200 and r.data==(R/('docs/tads_C/tad_cola_prioridad.'+ext)).read_bytes();(N/('tad_cola_prioridad.'+ext)).write_bytes(r.data);downloads[kind]={'HTTP':200,'sha256':hashlib.sha256(r.data).hexdigest()}
downloads['main_HTTP_status']=c.get('/help/source/priority_queue/main').status_code
C=(N/'tad_cola_prioridad.c').read_text(encoding='utf-8-sig');a=C.index('static CPNodo *cp_crear_nodo(');b=C.index('\n}',a)+2;body=C[a:b]
h=body.replace('{\n','{\n    qa_helper_scope(1);qa_event("helper_entry",NULL,-1);\n',1).replace('    if (nuevo == NULL) {','    qa_capture(nuevo,1);qa_event("helper_new_allocated",NULL,-1);\n    if (qa_guard("helper_allocation_guard",NULL,nuevo == NULL)) {').replace('return NULL;','qa_event("helper_return_NULL",NULL,-1);qa_helper_scope(0);qa_event("helper_exit",NULL,-1);return NULL;').replace('nuevo->valor = valor;','nuevo->valor = valor;qa_field(nuevo,1);qa_event("value_assigned",NULL,-1);').replace('nuevo->prioridad = prioridad;','nuevo->prioridad = prioridad;qa_field(nuevo,2);qa_event("priority_assigned",NULL,-1);').replace('nuevo->sgte = NULL;','nuevo->sgte = NULL;qa_field(nuevo,4);qa_event("link_assigned",NULL,-1);').replace('return nuevo;','qa_event("helper_return",NULL,-1);qa_helper_scope(0);qa_event("helper_exit",NULL,-1);return nuevo;')
C=C[:a]+h+C[b:];a=C.index('bool cp_encolar(');b=C.index('\n}',a)+2;body=C[a:b]
h=body.replace('{\n','{\n    qa_event("entry",cola,-1);\n',1).replace('CPNodo *nuevo;','CPNodo *nuevo;qa_event("new_declared",cola,-1);').replace('if (cola == NULL) {','if (qa_guard("root_guard",cola,cola == NULL)) {').replace('nuevo = cp_crear_nodo(valor, prioridad);','qa_event("helper_call",cola,-1);nuevo = cp_crear_nodo(valor, prioridad);qa_capture(nuevo,0);qa_event("parent_new_assigned",cola,-1);').replace('if (nuevo == NULL) {','if (qa_guard("parent_allocation_guard",cola,nuevo == NULL)) {').replace('if (cola->delante == NULL) {','if (qa_guard("empty_guard",cola,cola->delante == NULL)) {').replace('cola->delante = nuevo;','cola->delante = nuevo;qa_event("front_assigned",cola,-1);').replace('cola->atras->sgte = nuevo;','cola->atras->sgte = nuevo;qa_event("rear_next_assigned",cola,-1);').replace('cola->atras = nuevo;','cola->atras = nuevo;qa_event("rear_assigned",cola,-1);').replace('cola->cantidad++;','cola->cantidad++;qa_event("count_incremented",cola,-1);').replace('return false;','qa_event("return_false",cola,-1);return false;').replace('return true;','qa_event("return_true",cola,-1);return true;')
(N/'instrumented.c').write_text(C[:a]+h+C[b:],encoding='utf-8')
(N/'hooks.h').write_text('#include "tad_cola_prioridad.h"\n#include <stddef.h>\nvoid qa_event(const char*,ColaPrioridad*,int);int qa_guard(const char*,ColaPrioridad*,int);void qa_capture(void*,int);void qa_field(void*,int);void qa_helper_scope(int);void*qa_malloc(size_t);void qa_free(void*);\n',encoding='utf-8')
DRIVER=r"""
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include "tad_cola_prioridad.h"
struct cp_nodo {int valor;int prioridad;struct cp_nodo*sgte;};
_Static_assert(_Generic(&cp_encolar,bool(*)(ColaPrioridad*,int,int):1,default:0),"public signature");
static void*objects[64];static int live[64],mask[64],used,allocs,frees,active,sid,fail_next,parent_init,parent_id,helper_init,helper_id,helper_scope,param_value,param_priority;static ColaPrioridad*root;
static int id(void*p){if(!p)return -1;for(int i=0;i<used;i++)if(live[i]&&objects[i]==p)return i;assert(0);return -1;}
void qa_helper_scope(int state){if(active){helper_scope=state;if(state){helper_init=0;helper_id=-1;}}}
void qa_capture(void*p,int helper){if(!active)return;if(helper){helper_init=1;helper_id=id(p);}else{parent_init=1;parent_id=id(p);}}
void qa_field(void*p,int bit){mask[id(p)]|=bit;}
void qa_event(const char*event,ColaPrioridad*p,int condition){if(!active)return;(void)p;
 printf("{\"sample\":%d,\"event\":\"%s\",\"condition\":%d,\"value_parameter\":%d,\"priority_parameter\":%d,\"root_NULL\":%d,\"parent_new_initialized\":%d,\"parent_new_id\":%d,\"helper_active\":%d,\"helper_new_initialized\":%d,\"helper_new_id\":%d,\"front_id\":%d,\"rear_id\":%d,\"quantity\":%d,\"root_items\":[",sid,event,condition,param_value,param_priority,root==NULL,parent_init,parent_init?parent_id:-1,helper_scope,helper_init,helper_init?helper_id:-1,root?id(root->delante):-1,root?id(root->atras):-1,root?root->cantidad:0);
 struct cp_nodo*n=root?root->delante:NULL;int comma=0,index=0,out=-1,best=0;while(n){assert(mask[id(n)]==7);if(comma++)putchar(',');printf("{\"value\":%d,\"priority\":%d}",n->valor,n->prioridad);if(out==-1||n->prioridad<best){out=index;best=n->prioridad;}index++;n=n->sgte;}printf("],\"out_index\":%d,\"live\":[",out);comma=0;
 for(int i=0;i<used;i++){if(live[i]){if(comma++)putchar(',');struct cp_nodo*n=objects[i];printf("{\"id\":%d,\"mask\":%d,\"value\":",i,mask[i]);if(mask[i]&1)printf("%d",n->valor);else fputs("null",stdout);fputs(",\"priority\":",stdout);if(mask[i]&2)printf("%d",n->prioridad);else fputs("null",stdout);fputs(",\"next_id\":",stdout);if(mask[i]&4)printf("%d",id(n->sgte));else fputs("null",stdout);putchar('}');}}
 puts("]}");}
int qa_guard(const char*event,ColaPrioridad*p,int condition){qa_event(event,p,condition);return condition;}
void*qa_malloc(size_t size){qa_event("allocator_enter",root,-1);if(active&&fail_next){fail_next=0;qa_event("allocator_NULL_return",root,-1);return NULL;}void*p=malloc(size);assert(p&&used<64);objects[used]=p;live[used]=1;mask[used++]=0;allocs++;qa_event("allocator_success_return",root,-1);return p;}
void qa_free(void*p){if(!p)return;int i=id(p);live[i]=0;objects[i]=NULL;mask[i]=0;frees++;free(p);}
static void sample(ColaPrioridad*p,int v,int priority,int fault){root=p;param_value=v;param_priority=priority;parent_init=helper_init=helper_scope=0;parent_id=helper_id=-1;fail_next=fault;active=1;bool result=cp_encolar(p,v,priority);active=0;assert(result==(p!=NULL&&!fault));sid++;root=NULL;}
"""
CASES=[('empty',[],(9,3)),('single',[(7,2)],(-1,-1)),('duplicate',[(7,1)],(7,1)),('bounds',[(2147483647,2147483647),(-1,-1)],(-2147483648,-2147483648))]
literal=lambda v:'INT_MIN' if v==-2147483648 else 'INT_MAX' if v==2147483647 else str(v)
main='int main(void){'
for name,seeds,(value,priority) in CASES:
 main+='{ColaPrioridad cp;cp_inicializar(&cp);'
 for v,p in seeds:main+=f'assert(cp_encolar(&cp,{literal(v)},{literal(p)}));'
 main+=f'sample(&cp,{literal(value)},{literal(priority)},0);sample(&cp,{literal(value)},{literal(priority)},0);sample(&cp,{literal(value)},{literal(priority)},1);cp_vaciar(&cp);}}'
main+='sample(NULL,9,3,0);{ColaPrioridad cp;cp_inicializar(&cp);sample(&cp,9,3,1);assert(!cp.delante&&!cp.atras&&cp.cantidad==0);}assert(allocs==frees);for(int i=0;i<used;i++)assert(!live[i]);fprintf(stderr,"OWNERSHIP %d %d 0\\n",allocs,frees);return 0;}'
(N/'driver.c').write_text(DRIVER+main,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for cmd,log in [(flags+['-include',str(N/'hooks.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'instrumented.c'),'-o',str(N/'priority.o')],'compile-source.log'),(flags+[str(N/'driver.c'),str(N/'priority.o'),'-o',str(N/'driver.exe')],'compile-driver.log')]:
 p=subprocess.run(cmd,capture_output=True,text=True);(N/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(p.stdout,encoding='utf-8');(N/'stderr.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr;native=[json.loads(x) for x in p.stdout.splitlines()];(E/'native-report.json').write_text(json.dumps(native,indent=2),encoding='utf-8');(E/'downloads.json').write_text(json.dumps(downloads,indent=2),encoding='utf-8')
rows=[];sid=0;resource=[]
for case,seeds,(value,priority) in CASES:
 c=app.test_client()
 for v,pr in seeds:assert c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':v,'priority':pr}}).get_json()['success']
 for repeat in [1,2]:
  tracemalloc.start();start=time.perf_counter();r=c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':value,'priority':priority}});elapsed=time.perf_counter()-start;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();d=r.get_json();assert r.status_code==200 and d['success'];ns=[n for n in native if n['sample']==sid];assert d['visual_state']['items']==ns[-1]['root_items'] and d['visual_state']['out_index']==ns[-1]['out_index'];matches=[]
  for token,line in [('helper_new_allocated','CPNodo *nuevo = (CPNodo *)malloc(sizeof(CPNodo));'),('value_assigned','nuevo->valor = valor;'),('priority_assigned','nuevo->prioridad = prioridad;'),('link_assigned','nuevo->sgte = NULL;'),('helper_return','return nuevo;'),('front_assigned','cola->delante = nuevo;') if ns[0]['front_id']==-1 else ('rear_next_assigned','cola->atras->sgte = nuevo;'),('rear_assigned','cola->atras = nuevo;'),('count_incremented','cola->cantidad++;'),('return_true','return true;')]:
   n=next(n for n in ns if n['event']==token);f=next(f for f in d['execution_trace']['steps'] if f['line_text'].strip()==line);st=f['state_after'];ptr={p['name']:p['target'] for p in f['pedagogy']['pointers']};label=lambda i:'NULL' if i==-1 else f'N{[h["id"] for h in ns[-1]["live"]].index(i)+1}';matches.append({'event':token,'root_items_match':st['items']==n['root_items'],'quantity_match':st.get('cantidad')==n['quantity'],'quantity_trace':st.get('cantidad'),'quantity_C':n['quantity'],'front_match':ptr.get('delante')==label(n['front_id']),'rear_match':ptr.get('atras')==label(n['rear_id']),'heap_count_match':len(f['pedagogy']['heap_objects'])==len(n['live']),'native_event':n})
  rows.append({'case':case,'seeds':seeds,'value':value,'priority':priority,'repeat':repeat,'native_sample':sid,'native_events':ns,'observations':matches,'final_fifo_and_stable_priority_match':True,'data':d});resource.append({'case':case,'repeat':repeat,'python_peak_bytes':peak,'python_current_bytes':current,'response_bytes':len(r.data),'elapsed_instrumented_seconds':elapsed,'frames':len(d['execution_trace']['steps'])});sid+=1
 sid+=1
(E/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');resources={'calls':resource,'max_python_peak_bytes':max(x['python_peak_bytes'] for x in resource),'max_response_bytes':max(x['response_bytes'] for x in resource),'max_instrumented_seconds':max(x['elapsed_instrumented_seconds'] for x in resource),'limitations':'tracemalloc Python only includes instrumented Flask/session/serialization; no RSS/browser/Cheap/depth/history/OOM/SLA claim;8 finite target API samples, seed setup excluded'};(E/'resources.json').write_text(json.dumps(resources,indent=2),encoding='utf-8');print(json.dumps({'native_calls':len({n['sample'] for n in native}),'events':len(native),'conditions':sum(n['condition']!=-1 for n in native),'ownership':p.stderr.strip(),'target_API_calls':8,'observations':sum(len(r['observations']) for r in rows),'observation_divergences':{key:sum(not o[key] for r in rows for o in r['observations']) for key in ['root_items_match','quantity_match','front_match','rear_match','heap_count_match']},'resources':resources}))
