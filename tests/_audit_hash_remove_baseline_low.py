"""Selected independent C remove observations; no product implementation changes."""
from pathlib import Path
import json,subprocess,shutil,sys
R=Path.cwd();sys.path.insert(0,str(R));from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-remove-baseline-low';N=E/'native';N.mkdir(exist_ok=True);sys.stdout.reconfigure(encoding='utf-8')
CASES=[('empty',[],[1,1]),('head',[(1,10),(4,40),(7,70),(10,100)],[10,10,7,4,1]),('middle',[(1,10),(4,40),(7,70),(10,100)],[7,4,10,1]),('tail',[(1,10),(4,40),(7,70),(10,100)],[1,4,7,10]),('negative',[(-1,-10),(-4,-40),(-6,-60)],[-6,-4,-1,-9]),('extremes',[(-2147483648,2147483647),(2147483647,-2147483648)],[-2147483648,2147483647,-2147483648,0])]
PREFIX=r'''#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "tad_tabla_hash.h"
static int cid,qid,active,comparisons,frees;
static void emit(const char*token,const TablaHash*t,const THNodo*a,const THNodo*p,int indice,int condition,int status){if(!active)return;
printf("{\"case\":%d,\"query\":%d,\"token\":\"%s\",\"index\":%d,\"condition\":%d,\"status\":%d,\"comparisons\":%d,\"frees\":%d,\"size\":%d,\"actual_key\":",cid,qid,token,indice,condition,status,comparisons,frees,t->cantidad);if(a)printf("%d",a->clave);else printf("null");printf(",\"previous_key\":");if(p)printf("%d",p->clave);else printf("null");printf(",\"buckets\":[");for(int i=0;i<t->capacidad;i++){if(i)printf(",");printf("[");int first=1;for(THNodo*n=t->buckets[i];n;n=n->siguiente){if(!first)printf(",");first=0;printf("[%d,%d]",n->clave,n->valor);}printf("]");}printf("]}\n");}
'''
REMOVE=r'''bool th_eliminar(TablaHash *tabla, int clave) {
 emit("remove_entry",tabla,NULL,NULL,-1,-1,-1);
 bool invalid=!tabla||!tabla->buckets||tabla->capacidad<=0;emit("remove_guard",tabla,NULL,NULL,-1,invalid,-1);if(invalid){emit("remove_return",tabla,NULL,NULL,-1,-1,0);return false;}
 emit("index_call",tabla,NULL,NULL,-1,-1,-1);int indice=th_indice(tabla,clave);emit("index_assigned",tabla,NULL,NULL,indice,-1,-1);
 THNodo*actual=tabla->buckets[indice];emit("actual_init",tabla,actual,NULL,indice,-1,-1);
 THNodo*anterior=NULL;emit("previous_init",tabla,actual,anterior,indice,-1,-1);
 while(1){emit("search_test",tabla,actual,anterior,indice,actual!=NULL,-1);if(!actual)break;comparisons++;emit("key_compare",tabla,actual,anterior,indice,actual->clave==clave,-1);
 if(actual->clave==clave){emit("previous_guard",tabla,actual,anterior,indice,anterior==NULL,-1);
 if(anterior==NULL){tabla->buckets[indice]=actual->siguiente;emit("bucket_link",tabla,actual,anterior,indice,-1,-1);}else{anterior->siguiente=actual->siguiente;emit("previous_link",tabla,actual,anterior,indice,-1,-1);}
 free(actual);frees++;emit("node_free",tabla,NULL,anterior,indice,-1,-1);
 tabla->cantidad--;emit("count_decrement",tabla,NULL,anterior,indice,-1,-1);emit("remove_return",tabla,NULL,anterior,indice,-1,1);return true;}
 anterior=actual;emit("previous_assign",tabla,actual,anterior,indice,-1,-1);actual=actual->siguiente;emit("actual_advance",tabla,actual,anterior,indice,-1,-1);}
 emit("remove_return",tabla,NULL,anterior,indice,-1,0);return false;
}'''
def replace(s,signature,new):
 a=s.index(signature);start=s.index('{',a);depth=0
 for pos in range(start,len(s)):
  if s[pos]=='{':depth+=1
  elif s[pos]=='}':
   depth-=1
   if depth==0:return s[:a]+new+s[pos+1:]
 raise AssertionError(signature)
def lit(v):return '(-2147483647-1)' if v==-2147483648 else str(v)
source=(R/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8-sig');source=replace(source,'bool th_eliminar(',REMOVE);main='\nint main(void){'
for ci,(name,pairs,keys) in enumerate(CASES):
 main+='{TablaHash t={0};active=0;th_inicializar(&t,3);if(!t.buckets)return 1;'
 for k,v in pairs:main+='if(!th_insertar(&t,'+lit(k)+','+lit(v)+'))return 2;'
 for qi,k in enumerate(keys):main+='cid='+str(ci)+';qid='+str(qi)+';comparisons=frees=0;active=1;(void)th_eliminar(&t,'+lit(k)+');'
 main+='active=0;th_destruir(&t);}'
main+='return 0;}'
(N/'observed.c').write_text(PREFIX+source+main,encoding='utf-8');shutil.copyfile(R/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h');r=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'observed.c'),'-o',str(N/'observed.exe')],capture_output=True,text=True);(N/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr;r=subprocess.run([str(N/'observed.exe')],capture_output=True,text=True);(N/'native.jsonl').write_text(r.stdout,encoding='utf-8');assert r.returncode==0;rows=[json.loads(s) for s in r.stdout.splitlines()]
app=create_app();app.config['TESTING']=True;report=[]
for ci,(name,pairs,keys) in enumerate(CASES):
 c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
 for k,v in pairs:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 for qi,k in enumerate(keys):
  r=c.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':k}});d=r.get_json();native=[row for row in rows if row['case']==ci and row['query']==qi];last=native[-1];buckets=[[[e['key'],e['value']] for e in b['entries']] for b in d['visual_state']['buckets']];assert d['result']==bool(last['status']) and buckets==last['buckets'] and d['visual_state']['metadata']['size']==last['size'];frames=d['execution_trace']['steps'];report.append({'case':name,'key':k,'status':r.status_code,'native':native,'data':d,'results_state_match':True,'native_events':len(native),'API_frames':len(frames),'API_debug':any('debug' in f for f in frames),'API_events':[f['event_type'] for f in frames]})
(E/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'operations':len(report),'native_events':len(rows),'deletion_frees':sum(r['native'][-1]['frees'] for r in report),'result_state_matches':len(report),'debug_frames_cases':sum(r['API_debug'] for r in report),'sequence_matches':sum(r['API_events']==[n['token'] for n in r['native']] for r in report)}))
