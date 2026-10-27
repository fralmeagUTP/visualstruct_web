"""Finite original-C callbacks. Pointer validity is inferred without retired reads."""
from pathlib import Path
import json,sys,shutil,subprocess,re
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-clear-destroy-instructions-medium';N=E/'native-instructions';N.mkdir(exist_ok=True)
C=(R/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8-sig')
header='''#include "tad_tabla_hash.h"
void qa_event(const char*,TablaHash*,int,int);
int qa_guard(const char*,TablaHash*,int,int);
int qa_init(TablaHash*);
void qa_local(THNodo*,int);
void qa_slot(int);
void *qa_malloc(size_t);
void qa_free(void*);
'''
# Only insert hooks into the original two bodies. Conditions evaluated once.
def body(name):
 start=C.index('void '+name+'(');end=C.index('\n}',start)+2;return C[start:end]
a=body('th_vaciar');a=a.replace('{\n','{\n    qa_event("clear_entry",tabla,-1,-1);\n',1)
a=a.replace('if (!tabla || !tabla->buckets) return;','if (qa_guard("clear_guard",tabla,-1,!tabla || !tabla->buckets)) { qa_event("clear_return",tabla,-1,-1); return; }')
a=a.replace('for (int i = 0; i < tabla->capacidad; i++) {','for (int i = qa_init(tabla); qa_guard("bucket_guard",tabla,i,i < tabla->capacidad); i++, qa_event("bucket_increment",tabla,i,-1)) {')
a=a.replace('THNodo *actual = tabla->buckets[i];','THNodo *actual = tabla->buckets[i];\n        _Static_assert(_Generic(actual, THNodo*:1,default:0),"actual type");\n        qa_local(actual,0); qa_event("actual_declared",tabla,i,-1);')
a=a.replace('while (actual != NULL) {','while (qa_guard("chain_guard",tabla,i,actual != NULL)) {')
a=a.replace('THNodo *siguiente = actual->siguiente;','THNodo *siguiente = actual->siguiente;\n            _Static_assert(_Generic(siguiente, THNodo*:1,default:0),"next type");\n            qa_local(siguiente,1); qa_event("next_saved",tabla,i,-1);')
a=a.replace('free(actual);','free(actual); qa_event("node_free",tabla,i,-1);')
a=a.replace('actual = siguiente;','actual = siguiente; qa_local(actual,0); qa_event("actual_assigned",tabla,i,-1);')
a=a.replace('        }\n        tabla->buckets[i] = NULL;','            qa_event("iteration_exit",tabla,i,-1);\n        }\n        tabla->buckets[i] = NULL; qa_slot(i); qa_event("bucket_NULL_write",tabla,i,-1);')
a=a.replace('    }\n    tabla->cantidad = 0;','        qa_event("bucket_body_exit",tabla,i,-1);\n    }\n    qa_event("bucket_loop_exit",tabla,-1,-1);\n    tabla->cantidad = 0; qa_event("clear_count_zero",tabla,-1,-1);')
a=a[:-1]+'    qa_event("clear_return",tabla,-1,-1);\n}'
b=body('th_destruir');b=b.replace('{\n','{\n    qa_event("destroy_entry",tabla,-1,-1);\n',1)
b=b.replace('if (!tabla || !tabla->buckets) return;','if (qa_guard("destroy_guard",tabla,-1,!tabla || !tabla->buckets)) { qa_event("destroy_return",tabla,-1,-1); return; }')
b=b.replace('    th_vaciar(tabla);','    qa_event("clear_call",tabla,-1,-1); th_vaciar(tabla);')
for line,event in [('free(tabla->buckets);','bucket_array_free'),('tabla->buckets = NULL;','root_buckets_NULL'),('tabla->capacidad = 0;','root_capacity_zero'),('tabla->cantidad = 0;','destroy_count_zero')]: b=b.replace(line,line+' qa_event("'+event+'",tabla,-1,-1);')
b=b[:-1]+'    qa_event("destroy_return",tabla,-1,-1);\n}'
modified=C.replace(body('th_vaciar'),a).replace(body('th_destruir'),b)
(N/'instrumented.c').write_text(modified,encoding='utf-8');shutil.copyfile(R/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h');(N/'hooks.h').write_text(header,encoding='utf-8')
driver=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tad_tabla_hash.h"
_Static_assert(_Generic(&th_vaciar, void(*)(TablaHash*):1,default:0),"clear signature");
_Static_assert(_Generic(&th_destruir, void(*)(TablaHash*):1,default:0),"destroy signature");
static void*objects[512];static int alive[512],kind[512],used,allocs,frees,new_bucket;
static int recording,sample_id,cap0,array_alive,ptr_valid,slot_valid[64],actual_valid,actual_present,actual_key,saved_present,saved_key,has_actual,has_saved,count_pending,call_frees;
static TablaHash*root;
void *qa_malloc(size_t size){void*p=malloc(size);assert(p&&used<512);objects[used]=p;alive[used]=1;kind[used]=new_bucket?1:2;new_bucket=0;used++;allocs++;return p;}
void qa_free(void*p){if(!p)return;int found=-1;for(int j=0;j<used;j++)if(alive[j]&&objects[j]==p){found=j;break;}assert(found>=0);
 if(recording){call_frees++;if(kind[found]==1){ptr_valid=0;array_alive=0;for(int i=0;i<cap0;i++)slot_valid[i]=0;}
 else {assert(root&&ptr_valid&&array_alive);for(int i=0;i<cap0;i++)if(slot_valid[i]&&root->buckets[i]==p)slot_valid[i]=0;actual_valid=0;actual_present=0;count_pending=1;}}
 alive[found]=0;objects[found]=NULL;frees++;free(p);}
void qa_local(THNodo*p,int next){if(!recording)return;if(next){has_saved=1;saved_present=p!=NULL;saved_key=p?p->clave:0;}else {has_actual=1;actual_valid=1;actual_present=p!=NULL;actual_key=p?p->clave:0;}}
void qa_slot(int i){if(recording)slot_valid[i]=1;}
void qa_event(const char*event,TablaHash*t,int i,int cond){if(!recording)return;assert(t==root);
 if(!strcmp(event,"root_buckets_NULL"))ptr_valid=1;
 if(!strcmp(event,"iteration_exit"))has_saved=0;
 if(!strcmp(event,"bucket_body_exit"))has_actual=0;
 if(!strcmp(event,"clear_count_zero"))count_pending=0;
 printf("{\"sample\":%d,\"event\":\"%s\",\"condition\":%d,\"i\":%d,\"root_alive\":%d,\"capacity\":%d,\"size\":%d,\"array_alive\":%d,\"pointer_valid\":%d,\"pointer_NULL\":%d,\"count_pending\":%d,\"frees\":%d,\"has_actual\":%d,\"actual_valid\":%d,\"actual_present\":%d,\"actual_key\":%d,\"has_saved\":%d,\"saved_present\":%d,\"saved_key\":%d,\"slots\":[",sample_id,event,cond,i,t!=NULL,t?t->capacidad:0,t?t->cantidad:0,array_alive,ptr_valid,ptr_valid&&t?t->buckets==NULL:1,count_pending,call_frees,has_actual,actual_valid,actual_present,actual_key,has_saved,saved_present,saved_key);
 for(int j=0;j<cap0;j++){if(j)putchar(',');printf("{\"valid\":%d,\"key\":",slot_valid[j]);if(array_alive&&slot_valid[j]&&t->buckets[j])printf("%d",t->buckets[j]->clave);else fputs("null",stdout);putchar('}');}
 fputs("],\"live_keys\":[",stdout);int comma=0;for(int j=0;j<used;j++)if(alive[j]&&kind[j]==2){if(comma++)putchar(',');printf("%d",((THNodo*)objects[j])->clave);}puts("]}");}
int qa_guard(const char*e,TablaHash*t,int i,int value){qa_event(e,t,i,value);return value;}
int qa_init(TablaHash*t){qa_event("bucket_init",t,0,-1);return 0;}
static void sample(TablaHash*t,int op){root=t;cap0=t?t->capacidad:0;assert(cap0<64);array_alive=t&&t->buckets;ptr_valid=1;for(int i=0;i<cap0;i++)slot_valid[i]=1;has_actual=has_saved=actual_present=saved_present=count_pending=call_frees=0;actual_valid=1;recording=1;if(op)th_destruir(t);else th_vaciar(t);recording=0;sample_id++;}
'''
CASES=[('empty',3,[]),('collision',3,[(1,10),(4,40),(7,70)]),('sparse',7,[(-7,70),(7,70),(14,-14),(2,2)]),('destroyed',3,[(1,1),(4,4)])]
main='int main(void){'
for name,cap,pairs in CASES:
 for op in [0,1]:
  main+=f'{{TablaHash t={{0}};new_bucket=1;th_inicializar(&t,{cap});'
  for k,v in pairs:main+=f'assert(th_insertar(&t,{k},{v}));'
  if name=='destroyed':main+='th_destruir(&t);'
  main+=f'sample(&t,{op});sample(&t,{op});th_destruir(&t);}}'
for op in [0,1]:
 main+=' {TablaHash t={0};new_bucket=1;th_inicializar(&t,3);assert(th_insertar(&t,1,10));assert(th_insertar(&t,4,40));assert(th_insertar(&t,7,70));'
 main+=f'sample(&t,{op});'
 if op:main+='new_bucket=1;th_inicializar(&t,5);'
 main+=f'assert(th_insertar(&t,8,80));sample(&t,{op});th_destruir(&t);}}'
main+='sample(NULL,0);sample(NULL,1);{TablaHash t={0};sample(&t,0);sample(&t,1);}assert(allocs==frees);for(int j=0;j<used;j++)assert(!alive[j]);return 0;}'
(N/'driver.c').write_text(driver+main,encoding='utf-8')
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for cmd,log in [(flags+['-include',str(N/'hooks.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'instrumented.c'),'-o',str(N/'hash.o')],'compile-hash.log'),(flags+[str(N/'driver.c'),str(N/'hash.o'),'-o',str(N/'driver.exe')],'compile-driver.log')]:
 p=subprocess.run(cmd,capture_output=True,text=True);(N/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(p.stdout,encoding='utf-8');(N/'stderr.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
native=[json.loads(x) for x in p.stdout.splitlines()]
from app import create_app
from app.domain.hash.clear_destroy_instruction import build_hash_clear_destroy_trace
from app.services.c_code_service import CCodeService
app=create_app();app.config['TESTING']=True;traces=[]
for name,cap,pairs in CASES:
 for op in ['clear','destroy_table']:
  c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':cap}})
  for k,v in pairs:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
  if name=='destroyed':c.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
  for repeat in [1,2]:traces.append(c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace'])
for op in ['clear','destroy_table']:
 c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
 for k,v in [(1,10),(4,40),(7,70)]:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 traces.append(c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace'])
 if op=='destroy_table':c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':5}})
 c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':8,'value':80}})
 traces.append(c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace'])
# raw NULL table and zero-table guards use identical extracted source and zero state.
c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}});c.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
for null_table in [True,False]:
 for op in ['clear','destroy_table']:
  t=c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace']
  traces.append(build_hash_clear_destroy_trace(operation_name=op,payload={},source_code=t['source_code'],code_title=t['code_title'],before_state=t['final_state'],after_state=t['final_state'],success=True,message='',null_table=null_table))
comparisons=[]
for sid,t in enumerate(traces):
 ns=[x for x in native if x['sample']==sid];frames=t['steps'];assert [x['event'] for x in ns]==[x['debug']['token'] for x in frames],(sid,[x['event'] for x in ns],[x['debug']['token'] for x in frames])
 for n,f in zip(ns,frames):
  d=f['debug'];root=d['root'];arr=d['bucket_array'];assert n['capacity']==root['capacidad'] and n['size']==root['cantidad'],(sid,n,f)
  assert bool(n['root_alive'])==root['alive'] and bool(n['array_alive'])==arr['alive'] and bool(n['pointer_valid'])==root['buckets']['valid']
  assert bool(n['count_pending'])==d['count_write_pending'] and n['frees']==d['frees']
  assert n['condition']==(-1 if d['condition_result'] is None else int(d['condition_result']))
  live={h['id']:h for h in d['heap'] if h['alive']};assert sorted(n['live_keys'])==sorted(h['key'] for h in live.values())
  for nc,mc in zip(n['slots'],arr['cells']):
   assert bool(nc['valid'])==mc['valid'];assert nc['key']==(live[mc['value']]['key'] if mc['valid'] and mc['value'] is not None else None)
  actual=d['variables'].get('th_vaciar.actual');saved=[v for k,v in d['variables'].items() if k.endswith('.siguiente')]
  # C return hooks occur immediately before return; model removes callee scope at that event.
  if n['event'] not in ['clear_return','destroy_return']:
   assert bool(n['has_actual'])==bool(actual)
   if actual:
    assert bool(n['actual_valid'])==actual['valid']
    if actual['valid']:assert bool(n['actual_present'])==(actual['value'] is not None) and (not n['actual_present'] or n['actual_key']==live[actual['value']]['key'])
   assert bool(n['has_saved'])==bool(saved)
   if saved:assert bool(n['saved_present'])==(saved[0]['value'] is not None) and (not n['saved_present'] or n['saved_key']==live[saved[0]['value']]['key'])
 comparisons.append({'sample':sid,'frames':len(frames),'conditions':sum(x['condition']!=-1 for x in ns),'all_safe_snapshots_match':True})
(N/'comparison.json').write_text(json.dumps(comparisons,indent=2),encoding='utf-8');(N/'traces.json').write_text(json.dumps(traces),encoding='utf-8')
print(json.dumps({'samples':len(traces),'frames':len(native),'conditions':sum(x['condition']!=-1 for x in native),'limit':'semantic lifetime/masks; no padding or retired pointer reads; recreation first calls overlap core'}))
