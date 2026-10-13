"""LOW independent selected C search events and live Hash query baseline."""
from pathlib import Path
import json,subprocess,shutil,sys
sys.path.insert(0,str(Path.cwd()))
from app import create_app
ROOT=Path.cwd();E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-get-contains-baseline-low';N=E/'native';N.mkdir(exist_ok=True);sys.stdout.reconfigure(encoding='utf-8')
CASES=[('empty',3,[],[1]),('chain',3,[(1,10),(4,40),(7,70)],[7,4,1,10]),('negative',3,[(-1,-10),(-4,-40),(-6,-60)],[-1,-4,-6,-9]),('extremes',3,[(-2147483648,2147483647),(2147483647,-2147483648)],[-2147483648,2147483647,0])]
PREFIX=r'''#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "tad_tabla_hash.h"
static int active,case_id,query_id,comparisons,hash_calls,output_initialized;static int*output;static const char*operation;
static void emit(const char*token,int condition,int status){if(!active)return;printf("{\"case\":%d,\"query\":%d,\"operation\":\"%s\",\"token\":\"%s\",\"condition\":",case_id,query_id,operation,token);if(condition<0)printf("null");else printf(condition?"true":"false");printf(",\"return\":");if(status<0)printf("null");else printf(status?"true":"false");printf(",\"output_initialized\":%s,\"output\":",output_initialized?"true":"false");if(output_initialized&&output)printf("%d",*output);else printf("null");printf(",\"comparisons\":%d,\"hash_calls\":%d}\n",comparisons,hash_calls);}
'''
SEARCH=r'''bool th_buscar(const TablaHash*tabla,int clave,int*valor){
 output=valor;emit("search_entry",-1,-1);
 bool invalid=!tabla||!tabla->buckets||tabla->capacidad<=0||!valor;emit("search_guard",invalid,-1);if(invalid){emit("search_return",-1,0);return false;}
 emit("index_call",-1,-1);int indice=th_indice(tabla,clave);if(active)hash_calls++;emit("index_assigned",-1,-1);
 THNodo*actual=tabla->buckets[indice];emit("actual_init",-1,-1);
 while(1){emit("search_test",actual!=NULL,-1);if(!actual)break;if(active)comparisons++;emit("key_compare",actual->clave==clave,-1);
 if(actual->clave==clave){*valor=actual->valor;output_initialized=1;emit("output_write",-1,-1);emit("search_return",-1,1);return true;}actual=actual->siguiente;emit("actual_advance",-1,-1);}
 emit("search_return",-1,0);return false;
}'''
CONTAINS=r'''bool th_contiene(const TablaHash*tabla,int clave){
 output=NULL;output_initialized=0;emit("contains_entry",-1,-1);int dummy_valor;emit("dummy_declared",-1,-1);emit("search_call",-1,-1);
 bool result=th_buscar(tabla,clave,&dummy_valor);emit("contains_return",-1,result);output=NULL;return result;
}'''
def replace(s,signature,new):
 a=s.index(signature);start=s.index('{',a);depth=0
 for pos in range(start,len(s)):
  if s[pos]=='{':depth+=1
  elif s[pos]=='}':
   depth-=1
   if depth==0:return s[:a]+new+s[pos+1:]
 raise AssertionError(signature)
INDEX=r'''int th_indice(const TablaHash*tabla,int clave){
 emit("index_entry",-1,-1);bool invalid=!tabla||tabla->capacidad<=0;emit("index_guard",invalid,-1);if(invalid)return -1;
 int indice=clave%tabla->capacidad;emit("raw_modulo",-1,-1);emit("negative_modulo_guard",indice<0,-1);
 if(indice<0){indice+=tabla->capacidad;emit("normalize_modulo",-1,-1);}emit("index_return",-1,-1);return indice;
}'''
source=(ROOT/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8');source=replace(source,'bool th_buscar(',SEARCH);source=replace(source,'bool th_contiene(',CONTAINS);source=replace(source,'int th_indice(',INDEX)
def literal(v):return '(-2147483647-1)' if v==-2147483648 else str(v)
main='\nint main(void){'
for cid,(name,cap,pairs,keys) in enumerate(CASES):
 main+='{TablaHash t={0};active=0;th_inicializar(&t,'+str(cap)+');if(!t.buckets)return 1;'
 for k,v in pairs:main+='if(!th_insertar(&t,'+literal(k)+','+literal(v)+'))return 2;'
 for qid,k in enumerate(keys):
  for op in ['get','contains']:
   main+='case_id='+str(cid)+';query_id='+str(qid)+';operation="'+op+'";comparisons=hash_calls=0;active=1;'
   if op=='get':main+='{int sentinel=123456789;output=&sentinel;output_initialized=1;(void)th_buscar(&t,'+literal(k)+',&sentinel);output=NULL;}'
   else:main+='(void)th_contiene(&t,'+literal(k)+');'
 main+='active=0;th_destruir(&t);}'
main+='return 0;}'
(N/'observed.c').write_text(PREFIX+source+main,encoding='utf-8');shutil.copyfile(ROOT/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h');r=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'observed.c'),'-o',str(N/'observed.exe')],capture_output=True,text=True);(N/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr;r=subprocess.run([str(N/'observed.exe')],capture_output=True,text=True);(N/'native.jsonl').write_text(r.stdout,encoding='utf-8');assert r.returncode==0;rows=[json.loads(line) for line in r.stdout.splitlines()]
app=create_app();app.config.update(TESTING=True);report=[]
for cid,(name,cap,pairs,keys) in enumerate(CASES):
 c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':cap}})
 for k,v in pairs:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 for qid,k in enumerate(keys):
  for op in ['get','contains']:
   response=c.post('/hash/hash_table/operate',json={'operation':op,'payload':{'key':k}});data=response.get_json();native=[row for row in rows if row['case']==cid and row['query']==qid and row['operation']==op];last=native[-1];expected=(last['output'] if last['return'] else None) if op=='get' else last['return'];assert data['result']==expected
   trace=data['execution_trace'];report.append({'case':name,'operation':op,'key':k,'status':response.status_code,'result':data['result'],'native_result':last['return'],'native_output':last['output'],'native_comparisons':last['comparisons'],'native_hash_calls':last['hash_calls'],'API_cost':trace['steps'][-1]['pedagogy']['cost'],'API_debug_present':any('debug' in f for f in trace['steps']),'normalization_frames':sum('indice += tabla->capacidad' in f['line_text'] for f in trace['steps']),'native_normalization_frames':sum(row['token']=='normalize_modulo' for row in native),'expected_normalization':k<0 and abs(k)%cap!=0,'data':data,'native':native})
(E/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'queries':len(report),'results_match_native':True,'get_absent_200':sum(r['operation']=='get' and r['native_result'] is False and r['status']==200 for r in report),'false_normalization':sum(r['normalization_frames']>0 and not r['expected_normalization'] for r in report),'queries_with_debug':sum(r['API_debug_present'] for r in report)}))
