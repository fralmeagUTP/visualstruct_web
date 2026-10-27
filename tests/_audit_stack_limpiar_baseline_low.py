"""LOW native limpiar baseline; original C plus safe observation hooks only."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-baseline-low';N=E/'native';N.mkdir(exist_ok=True);app=create_app();app.config['TESTING']=True;c=app.test_client();downloads={}
for kind,ext in [('source','c'),('header','h')]:
 r=c.get('/help/source/stack/'+kind);assert r.status_code==200;data=r.data;p=N/('tad_pila.'+ext);p.write_bytes(data);assert data==(R/('docs/tads_C/tad_pila.'+ext)).read_bytes();downloads[kind]={'HTTP':200,'sha256':hashlib.sha256(data).hexdigest(),'content_disposition':r.headers.get('Content-Disposition')}
C=(N/'tad_pila.c').read_text(encoding='utf-8-sig');start=C.index('void pila_destruir(');end=C.index('\n}',start)+2;body=C[start:end];patched=body.replace('{\n','{\n    qa_event("entry",p,-1);\n',1).replace('    ptrPila aux;','    ptrPila aux;\n    _Static_assert(_Generic(aux, ptrPila:1, default:0),"aux type");\n    qa_event("aux_declared",p,-1);').replace('if (p == NULL) {','if (qa_guard("root_guard",p,p == NULL)) {').replace('        return;','        qa_event("return",p,-1); return;').replace('while (*p != NULL) {','while (qa_guard("while_guard",p,*p != NULL)) {').replace('aux = *p;','aux = *p; qa_capture(aux); qa_event("aux_assigned",p,-1);').replace('*p = aux->sgte;','*p = aux->sgte; qa_event("root_assigned",p,-1);').replace('free(aux);','free(aux); qa_event("node_free",p,-1);');patched=patched[:-1]+'    qa_event("return",p,-1);\n}';(N/'instrumented.c').write_text(C[:start]+patched+C[end:],encoding='utf-8')
(N/'hooks.h').write_text('#include <stddef.h>\nstruct NodoPila;\nvoid qa_event(const char*,struct NodoPila**,int);\nint qa_guard(const char*,struct NodoPila**,int);\nvoid qa_capture(struct NodoPila*);\nvoid *qa_malloc(size_t);\nvoid qa_free(void*);\n',encoding='utf-8')
DRIVER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tad_pila.h"
_Static_assert(_Generic(&pila_destruir,void(*)(ptrPila*):1,default:0),"destructor signature");
static void*obj[64];static int alive[64],used,allocs,frees,active,sid,target_free,aux_init,aux_valid,aux_id;
static int id(void*p){if(!p)return -1;for(int j=0;j<used;j++)if(alive[j]&&obj[j]==p)return j;assert(0);return -1;}
void*qa_malloc(size_t size){void*p=malloc(size);assert(p&&used<64);obj[used]=p;alive[used++]=1;allocs++;return p;}
void qa_free(void*p){if(!p)return;int j=id(p);if(active){assert(aux_valid&&aux_id==j);aux_valid=aux_init=0;target_free++;}alive[j]=0;obj[j]=NULL;frees++;free(p);}
void qa_capture(ptrPila p){if(active){aux_init=aux_valid=1;aux_id=id(p);}}
void qa_event(const char*e,ptrPila*p,int condition){if(!active)return;
 printf("{\"sample\":%d,\"event\":\"%s\",\"condition\":%d,\"root_argument_NULL\":%d,\"aux_initialized\":%d,\"aux_valid\":%d,\"aux_id\":%d,\"frees\":%d,\"root_ids\":[",sid,e,condition,p==NULL,aux_init,aux_valid,aux_valid?aux_id:-1,target_free);
 ptrPila n=p?*p:NULL;int comma=0;while(n){if(comma++)putchar(',');int j=id(n);printf("%d",j);n=n->sgte;}fputs("],\"root_values\":[",stdout);n=p?*p:NULL;comma=0;while(n){assert(id(n)>=0);if(comma++)putchar(',');printf("%d",n->nro);n=n->sgte;}fputs("],\"live\":[",stdout);comma=0;for(int j=0;j<used;j++)if(alive[j]){if(comma++)putchar(',');ptrPila n=obj[j];printf("{\"id\":%d,\"value\":%d}",j,n->nro);}puts("]}");}
int qa_guard(const char*e,ptrPila*p,int value){qa_event(e,p,value);return value;}
static void sample(ptrPila*p){target_free=aux_init=aux_valid=0;aux_id=-1;active=1;pila_destruir(p);active=0;sid++;}
'''
CASES=[('empty',[]),('single',[-1]),('multi',[7,-2,7]),('reinsert',[7,-2,7])];main='int main(void){'
for name,values in CASES:
 main+='{ptrPila p=NULL;'
 for v in values:main+=f'pila_apilar(&p,{v});'
 main+='sample(&p);assert(p==NULL);'
 if name=='reinsert':main+='pila_apilar(&p,8);'
 main+='sample(&p);assert(p==NULL);pila_destruir(&p);}'
main+=r'sample(NULL);assert(allocs==frees);for(int j=0;j<used;j++)assert(!alive[j]);fprintf(stderr,"OWNERSHIP %d %d 0\n",allocs,frees);return 0;}'
(N/'driver.c').write_text(DRIVER+main,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for cmd,log in [(flags+['-include',str(N/'hooks.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'instrumented.c'),'-o',str(N/'pila.o')],'compile-source.log'),(flags+[str(N/'driver.c'),str(N/'pila.o'),'-o',str(N/'driver.exe')],'compile-driver.log')]:
 p=subprocess.run(cmd,capture_output=True,text=True);(N/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(p.stdout,encoding='utf-8');(N/'stderr.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr;native=[json.loads(x) for x in p.stdout.splitlines()];assert 'OWNERSHIP 8 8 0' in p.stderr
report=[];sid=0
for name,values in CASES:
 c=app.test_client()
 for v in values:assert c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':v}}).get_json()['success']
 for repeat in [1,2]:
  if name=='reinsert' and repeat==2:assert c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':8}}).get_json()['success']
  r=c.post('/sequential/stack/operate',json={'operation':'limpiar','payload':{}});d=r.get_json();assert r.status_code==200 and d['success'] and d['visual_state']['items']==[];events=[n for n in native if n['sample']==sid];matches=[]
  for token,line in [('aux_assigned','aux = *p;'),('root_assigned','*p = aux->sgte;'),('node_free','free(aux);')]:
   ns=[n for n in events if n['event']==token];fs=[f for f in d['execution_trace']['steps'] if f['line_text'].strip()==line];assert len(ns)==len(fs)
   for idx,(n,f) in enumerate(zip(ns,fs)):matches.append({'event':token,'iteration':idx,'C_values':n['root_values'],'trace_values':[x['value'] for x in f['state_after']['items']],'match':[x['value'] for x in f['state_after']['items']]==n['root_values']})
  report.append({'case':name,'initial_values':values,'repeat':repeat,'native_sample':sid,'native_events':events,'C_API_final_match':True,'instruction_comparison':matches,'data':d});sid+=1
(E/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(E/'native-report.json').write_text(json.dumps(native,indent=2),encoding='utf-8');(E/'downloads.json').write_text(json.dumps(downloads,indent=2),encoding='utf-8')
# This product exposes source/header only; no main download or main_c in sequential model.
(E/'caller-availability.json').write_text(json.dumps({'actual_UI_source_header':True,'main_HTTP_status':c.get('/help/source/stack/main').status_code,'sequential_main_generator_present':False,'QA_driver_is_not_product_main':True,'caller_fidelity_not_verified':True},indent=2),encoding='utf-8')
print(json.dumps({'C_calls':9,'C_events':len(native),'C_API_final_results':8,'statement_observations':sum(len(r['instruction_comparison']) for r in report),'statement_divergences':sum(not x['match'] for r in report for x in r['instruction_comparison']),'alloc_free_live':[8,8,0],'NULL_guard_safe':True,'new_unique_paths':'empty/single/multi,reinsert first call overlapsmulti'}))
