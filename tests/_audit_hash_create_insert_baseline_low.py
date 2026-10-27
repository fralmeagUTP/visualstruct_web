"""Hash H1 LOW independent native statement/control observer and API baseline."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
ROOT=Path.cwd();sys.path.insert(0,str(ROOT))
from app import create_app
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-create-insert-baseline-low';N=E/'native';N.mkdir(exist_ok=True)
CASES={'create_three':(3,[]),'insert_empty':(3,[(1,10)]),'collision_load_gt_one':(3,[(1,10),(4,20),(7,30),(10,40)]),'update_head':(3,[(1,10),(4,20),(4,99)]),'update_middle':(3,[(1,10),(4,20),(7,30),(4,99)]),'update_tail':(3,[(1,10),(4,20),(7,30),(1,99)]),'negative_extremes':(3,[(-1,-10),(-4,-2147483648),(-2147483648,2147483647),(2147483647,0),(0,-1)]),'cap17_collision':(17,[(1,10),(18,20),(35,30),(52,40),(18,99)])}
PREFIX=r'''#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>
#include <assert.h>
#include "tad_tabla_hash.h"
static TablaHash *root;static int case_id,operation_id,init_active,insert_active,index_active;
static int have_index,have_actual,have_new,have_i,index_value,loop_i,input_key,input_value,input_capacity;
static THNodo *obs_actual,*obs_new;static unsigned char bucket_mask[64];
static void *objects[128];static int kinds[128],masks[128],live[128],used,allocations,frees,attempts,fail_at,alloc_kind;
static int comparisons,hash_calls,link_writes,value_writes,key_writes,count_writes;
static int identity(const void*p){if(!p)return 0;for(int i=used-1;i>=0;i--)if(live[i]&&objects[i]==p)return i+1;assert(0);return 0;}
static void *qa_malloc(size_t size){attempts++;if(fail_at&&attempts==fail_at)return NULL;void*p=malloc(size);if(p){assert(used<128);objects[used]=p;kinds[used]=alloc_kind;masks[used]=0;live[used++]=1;allocations++;}return p;}
static void qa_free(void*p){if(p){int id=identity(p);live[id-1]=0;frees++;}free(p);}
static void scalar(const char*name,int initialized,int value){printf(",\"%s\":",name);if(initialized)printf("%d",value);else printf("null");}
static void emit(const char*token,int condition,int status){
 printf("{\"case\":%d,\"operation\":%d,\"token\":\"%s\",\"condition\":",case_id,operation_id,token);if(condition<0)printf("null");else printf(condition?"true":"false");
 printf(",\"capacity\":%d,\"size\":%d,\"bucket_pointer\":%d,\"buckets\":[",root->capacidad,root->cantidad,identity(root->buckets));
 if(root->buckets){for(int i=0;i<root->capacidad;i++){if(i)printf(",");printf("{\"index\":%d,\"initialized\":%s,\"chain\":[",i,bucket_mask[i]?"true":"false");if(bucket_mask[i]){THNodo*p=root->buckets[i];int count=0;while(p){int id=identity(p);assert(masks[id-1]==7);if(count++)printf(",");assert(count<64);printf("{\"id\":%d,\"key\":%d,\"value\":%d,\"next\":%d}",id,p->clave,p->valor,identity(p->siguiente));p=p->siguiente;}}printf("]}");}}printf("]");
 printf(",\"heap\":[");int comma=0;for(int j=0;j<used;j++)if(live[j]){if(comma++)printf(",");printf("{\"id\":%d,\"kind\":%d,\"initialized_mask\":%d",j+1,kinds[j],masks[j]);if(kinds[j]==2){THNodo*p=objects[j];scalar("key",masks[j]&1,p&& (masks[j]&1)?p->clave:0);scalar("value",masks[j]&2,p&&(masks[j]&2)?p->valor:0);scalar("next",masks[j]&4,p&&(masks[j]&4)?identity(p->siguiente):0);}printf("}");}printf("]");
 printf(",\"init_active\":%s,\"insert_active\":%s,\"index_active\":%s",init_active?"true":"false",insert_active?"true":"false",index_active?"true":"false");scalar("indice",have_index,index_value);scalar("i",have_i,loop_i);scalar("actual",have_actual,insert_active&&have_actual?identity(obs_actual):0);scalar("nuevo",have_new,insert_active&&have_new?identity(obs_new):0);
 printf(",\"key\":%d,\"value\":%d,\"capacity_parameter\":%d,\"allocations\":%d,\"frees\":%d,\"live\":%d,\"attempts\":%d,\"comparisons\":%d,\"hash_calls\":%d,\"link_writes\":%d,\"value_writes\":%d,\"key_writes\":%d,\"count_writes\":%d",input_key,input_value,input_capacity,allocations,frees,allocations-frees,attempts,comparisons,hash_calls,link_writes,value_writes,key_writes,count_writes);scalar("return_status",status>=0,status);printf("}\n");
}
static int cond(const char*t,int value){if(!strcmp(t,"key_compare"))comparisons++;emit(t,value,-1);return value;}
#define INSERT_RETURN(v) do{insert_active=have_actual=have_new=have_index=0;obs_actual=obs_new=NULL;emit("insert_return",-1,(v));return(v);}while(0)
#define malloc qa_malloc
#define free qa_free
'''
INDEX=r'''int th_indice(const TablaHash *tabla, int clave) {
 index_active=1;hash_calls++;emit("index_entry",-1,-1);
 if(cond("index_guard",!tabla || tabla->capacidad<=0)){index_active=0;emit("index_return",-1,-1);return -1;}
 int indice=clave%tabla->capacidad;index_value=indice;have_index=1;emit("raw_modulo",-1,-1);
 if(cond("negative_modulo_guard",indice<0)){indice+=tabla->capacidad;index_value=indice;emit("normalize_modulo",-1,-1);}
 index_active=0;emit("index_return",-1,indice);return indice;
}'''
INIT=r'''void th_inicializar(TablaHash *tabla,int capacidad){
 init_active=1;emit("init_entry",-1,-1);
 if(cond("init_guard",!tabla || capacidad<=0)){init_active=0;emit("init_return",-1,-1);return;}
 tabla->capacidad=capacidad;emit("capacity_write",-1,-1);tabla->cantidad=0;count_writes++;emit("size_zero",-1,-1);
 alloc_kind=1;memset(bucket_mask,0,sizeof(bucket_mask));tabla->buckets=(THNodo**)malloc(capacidad*sizeof(THNodo*));emit("bucket_allocate",-1,-1);
 if(cond("bucket_allocation_guard",tabla->buckets!=NULL)){
  for(int i=0,unused=(loop_i=0,have_i=1,emit("bucket_loop_init",-1,-1),0);cond("bucket_loop_test",i<capacidad);i++,loop_i=i,emit("bucket_loop_increment",-1,-1)){
   (void)unused;tabla->buckets[i]=NULL;bucket_mask[i]=1;link_writes++;emit("bucket_null_write",-1,-1);
  }
  have_i=0;
 }else{tabla->capacidad=0;emit("allocation_error_capacity",-1,-1);}
 init_active=0;emit("init_return",-1,-1);
}'''
INSERT=r'''bool th_insertar(TablaHash *tabla,int clave,int valor){
 insert_active=1;have_index=have_actual=have_new=0;emit("insert_entry",-1,-1);
 if(cond("insert_guard",!tabla || !tabla->buckets || tabla->capacidad<=0))INSERT_RETURN(false);
 emit("index_call",-1,-1);int indice=th_indice(tabla,clave);index_value=indice;have_index=1;emit("index_assign",-1,-1);
 THNodo*actual=tabla->buckets[indice];obs_actual=actual;have_actual=1;emit("actual_init",-1,-1);
 while(cond("search_test",actual!=NULL)){
  if(cond("key_compare",actual->clave==clave)){actual->valor=valor;value_writes++;emit("update_value",-1,-1);INSERT_RETURN(true);}
  actual=actual->siguiente;obs_actual=actual;emit("actual_advance",-1,-1);
 }
 alloc_kind=2;THNodo*nuevo=(THNodo*)malloc(sizeof(THNodo));obs_new=nuevo;have_new=1;emit("node_allocate",-1,-1);
 if(cond("node_null_guard",!nuevo))INSERT_RETURN(false);
 nuevo->clave=clave;masks[identity(nuevo)-1]|=1;key_writes++;emit("node_key_write",-1,-1);
 nuevo->valor=valor;masks[identity(nuevo)-1]|=2;value_writes++;emit("node_value_write",-1,-1);
 nuevo->siguiente=tabla->buckets[indice];masks[identity(nuevo)-1]|=4;link_writes++;emit("node_next_write",-1,-1);
 tabla->buckets[indice]=nuevo;link_writes++;emit("head_publish",-1,-1);
 tabla->cantidad++;count_writes++;emit("size_increment",-1,-1);INSERT_RETURN(true);
}'''
source=(ROOT/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8')
def replace_function(source,signature,new):
 start=source.index(signature);begin=source.index('{',start);depth=0
 for i in range(begin,len(source)):
  if source[i]=='{':depth+=1
  if source[i]=='}':
   depth-=1
   if depth==0:return source[:start]+new+source[i+1:]
 raise AssertionError(signature)
for signature,new in [('int th_indice(',INDEX),('void th_inicializar(',INIT),('bool th_insertar(',INSERT)]:source=replace_function(source,signature,new)
setup=r'''
#undef malloc
#undef free
static void setup(TablaHash*t,int id,int fault){root=t;case_id=id;operation_id=0;init_active=insert_active=index_active=have_index=have_actual=have_new=have_i=0;obs_actual=obs_new=NULL;used=allocations=frees=attempts=comparisons=hash_calls=link_writes=value_writes=key_writes=count_writes=0;input_key=input_value=0;fail_at=fault;memset(live,0,sizeof(live));memset(bucket_mask,0,sizeof(bucket_mask));}
static void cleanup(void){have_index=have_actual=have_new=have_i=0;obs_actual=obs_new=NULL;th_destruir(root);emit("cleanup",-1,-1);assert(allocations==frees);}
'''
main='int main(void){_Static_assert(sizeof(int)==4,"int32");'
for id,(name,(cap,pairs)) in enumerate(CASES.items()):
 main+='{TablaHash t={0};setup(&t,'+str(id)+',0);input_capacity='+str(cap)+';emit("initial",-1,-1);th_inicializar(&t,'+str(cap)+');'
 for j,(key,value) in enumerate(pairs):main+='operation_id='+str(j+1)+';input_key='+str(key)+';input_value='+str(value)+';emit("initial",-1,-1);bool ok_'+str(j)+'=th_insertar(&t,input_key,input_value);assert(ok_'+str(j)+');'
 main+='operation_id=99;cleanup();}'
# Node NULL and failure marker on existing-key update; initializer NULL is C-only.
for id,cap,pairs,fault in [(20,3,[(1,10)],2),(21,3,[(1,10),(1,99)],3),(22,3,[],1)]:
 main+='{TablaHash t={0};setup(&t,'+str(id)+','+str(fault)+');input_capacity='+str(cap)+';emit("initial",-1,-1);th_inicializar(&t,'+str(cap)+');'
 for j,(key,value) in enumerate(pairs):main+='operation_id='+str(j+1)+';input_key='+str(key)+';input_value='+str(value)+';emit("initial",-1,-1);(void)th_insertar(&t,input_key,input_value);'
 main+='operation_id=99;cleanup();}'
main+='return 0;}'
(N/'observed.c').write_text(PREFIX+source+setup+main,encoding='utf-8');shutil.copyfile(ROOT/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h')
r=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'observed.c'),'-o',str(N/'observed.exe')],capture_output=True,text=True);(N/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
r=subprocess.run([str(N/'observed.exe')],capture_output=True,text=True);(N/'native.jsonl').write_text(r.stdout,encoding='utf-8');assert r.returncode==0,r.stderr;rows=[json.loads(s) for s in r.stdout.splitlines()]
app=create_app();app.testing=True;report=[]
for id,(name,(cap,pairs)) in enumerate(CASES.items()):
 c=app.test_client();responses=[]
 for op,operation,payload in [(0,'create_table',{'capacity':cap})]+[(i+1,'insert',{'key':k,'value':v}) for i,(k,v) in enumerate(pairs)]:
  response=c.post('/hash/hash_table/operate',json={'operation':operation,'payload':payload});d=response.get_json();assert response.status_code==200 and d['success'];native=[r for r in rows if r['case']==id and r['operation']==op];last=native[-1];actual=[[(e['key'],e['value']) for e in b['entries']] for b in d['visual_state']['buckets']];expected=[[(e['key'],e['value']) for e in b['chain']] for b in last['buckets']];assert actual==expected and d['visual_state']['metadata']['capacity']==last['capacity'] and d['visual_state']['metadata']['size']==last['size']
  cost=d['execution_trace']['steps'][-1]['pedagogy']['cost'];previous_native=next((r for r in native if r['token']=='initial'),native[0]);comps=last['comparisons']-previous_native['comparisons'];hashes=last['hash_calls']-previous_native['hash_calls'];responses.append(dict(operation=operation,payload=payload,data=d,native_events=len(native),API_frames=len(d['execution_trace']['steps']),value_comparisons=comps,hash_evaluations=hashes,API_cost=cost))
 cleanup_row=next(r for r in rows if r['case']==id and r['token']=='cleanup');(N/(name+'.json')).write_text(json.dumps(dict(native=[r for r in rows if r['case']==id],responses=responses,cleanup=cleanup_row),ensure_ascii=False,indent=2),encoding='utf-8');report.append(dict(case=name,operations=len(responses),endpoint_state_matches=True,native_events=sum(r['native_events'] for r in responses),API_frames=sum(r['API_frames'] for r in responses),allocations=cleanup_row['allocations'],frees=cleanup_row['frees'],live=cleanup_row['live'],metrics_match=all(r['API_cost']['comparisons']==r['value_comparisons'] and r['API_cost']['hash_evaluations']==r['hash_evaluations'] for r in responses)))
(N/'report.json').write_text(json.dumps(dict(cases=report,C_source_SHA=hashlib.sha256((ROOT/'docs/tads_C/tad_tabla_hash.c').read_bytes()).hexdigest(),C_header_SHA=hashlib.sha256((ROOT/'docs/tads_C/tad_tabla_hash.h').read_bytes()).hexdigest(),observer='Selected initialized heap/parameters/conditions/statement boundaries; initial caller zero C vs implicit17UI noted, no complete locals/type/prev fidelity claim',fault_case_ids=[20,21,22]),indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
