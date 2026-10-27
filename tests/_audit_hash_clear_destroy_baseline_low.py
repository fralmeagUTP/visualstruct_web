"""Real C free order/final roots, no reads of retired pointer values."""
from pathlib import Path
import json,sys,subprocess,shutil
R=Path.cwd();sys.path.insert(0,str(R));from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-clear-destroy-baseline-low';N=E/'native';N.mkdir(exist_ok=True)
CASES=[('empty',3,[]),('collision',3,[(1,10),(4,40),(7,70)]),('sparse',7,[(-7,70),(7,70),(14,-14),(2,2)]),('destroyed',3,[(1,1),(4,4)])]
HEADER='#include <stddef.h>\nvoid *qa_malloc(size_t);\nvoid qa_free(void*);\n'
DRIVER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "tad_tabla_hash.h"
static void*objects[512];static int alive[512],kind[512],used,allocs,frees,phase,cid,operation,new_bucket;
void *qa_malloc(size_t size){void*p=malloc(size);assert(p);assert(used<512);objects[used]=p;alive[used]=1;kind[used]=new_bucket?1:2;new_bucket=0;used++;allocs++;return p;}
void qa_free(void*p){if(!p)return;int found=-1;for(int j=0;j<used;j++){if(alive[j]&&objects[j]==p){found=j;break;}}assert(found>=0);int key=kind[found]==2?((THNodo*)p)->clave:0;
 printf("{\"event\":\"free\",\"case\":%d,\"operation\":%d,\"phase\":%d,\"object\":%d,\"kind\":\"%s\",\"key_before_free\":%d}\n",cid,operation,phase,found,kind[found]==1?"bucket_array":"node",key);
 alive[found]=0;objects[found]=NULL;frees++;free(p);}
static void sample(TablaHash*t,int repeat){phase=repeat;int before=frees;if(operation==0)th_vaciar(t);else th_destruir(t);
 int live=0;for(int j=0;j<used;j++)live+=alive[j];int initialized_null=1;if(t->buckets){for(int i=0;i<t->capacidad;i++)initialized_null&=t->buckets[i]==NULL;}
 printf("{\"event\":\"result\",\"case\":%d,\"operation\":%d,\"repeat\":%d,\"capacity\":%d,\"size\":%d,\"buckets_null\":%s,\"all_live_bucket_slots_null\":%s,\"frees_this_call\":%d,\"live_objects\":%d}\n",cid,operation,repeat,t->capacidad,t->cantidad,t->buckets?"false":"true",initialized_null?"true":"false",frees-before,live);}
'''
main='int main(void){'
for case,(name,cap,pairs) in enumerate(CASES):
 for op in [0,1]:
  main+=f'{{cid={case};operation={op};phase=0;TablaHash t={{0}};new_bucket=1;th_inicializar(&t,{cap});'
  for k,v in pairs:main+=f'assert(th_insertar(&t,{k},{v}));'
  if name=='destroyed':main+='th_destruir(&t);'
  main+='sample(&t,1);sample(&t,2);phase=3;th_destruir(&t);}'
main+=r'phase=4;th_vaciar(NULL);th_destruir(NULL);{TablaHash t={0};th_vaciar(&t);th_destruir(&t);assert(!t.buckets&&!t.capacidad&&!t.cantidad);}assert(allocs==frees);for(int j=0;j<used;j++)assert(!alive[j]);printf("{\"event\":\"ownership\",\"allocations\":%d,\"frees\":%d,\"live\":0}\n",allocs,frees);return 0;}'
(N/'driver.c').write_text(DRIVER+main,encoding='utf-8');(N/'ownership.h').write_text(HEADER,encoding='utf-8')
for ext in ['c','h']:shutil.copyfile(R/('docs/tads_C/tad_tabla_hash.'+ext),N/('tad_tabla_hash.'+ext))
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for command,log in [(flags+['-include',str(N/'ownership.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'tad_tabla_hash.c'),'-o',str(N/'hash.o')],'hash-compile.log'),(flags+[str(N/'driver.c'),str(N/'hash.o'),'-o',str(N/'driver.exe')],'driver-compile.log')]:
 p=subprocess.run(command,capture_output=True,text=True);(N/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(p.stdout,encoding='utf-8');assert p.returncode==0,p.stderr;native=[json.loads(x) for x in p.stdout.splitlines()];results=[x for x in native if x['event']=='result'];assert len(results)==16
app=create_app();app.config['TESTING']=True;report=[];D=E/'callers';D.mkdir(exist_ok=True)
for cid,(case,cap,pairs) in enumerate(CASES):
 for op_index,op in enumerate(['clear','destroy_table']):
  c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':cap}})
  for k,v in pairs:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
  if case=='destroyed':c.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
  for repeat in [1,2]:
   d=c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json();n=next(x for x in results if x['case']==cid and x['operation']==op_index and x['repeat']==repeat);assert d['success'];state=d['execution_trace']['final_state'];assert state['metadata']['capacity']==n['capacity'] and state['metadata']['size']==n['size'] and not any(b['entries'] for b in state['buckets']);events=[x for x in native if x['event']=='free' and x['case']==cid and x['operation']==op_index and x['phase']==repeat];report.append({'case':case,'operation':op,'repeat':repeat,'created_capacity':cap,'pairs':pairs,'native':n,'free_order':events,'data':d})
  main=c.get('/help/source/hash_table/main').data;(D/(case+'-'+op+'.c')).write_bytes(main);assert c.get('/help/source/hash_table/main').data==main
(E/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(E/'native-report.json').write_text(json.dumps(native,indent=2),encoding='utf-8');print(json.dumps({'API_C_final_results':16,'native_case_paths':8,'native_ownership':native[-1],'target_first_free_events':sum(len(r['free_order']) for r in report),'guards_NULL_zero':4,'instruction_fidelity':False}))
