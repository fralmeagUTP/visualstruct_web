"""Finite safe queue dequeue native/API baseline, no product changes."""
from pathlib import Path
import json,sys,subprocess,shutil,hashlib,re,os,time,tracemalloc
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-desencolar-baseline-low';N=E/'native';N.mkdir(exist_ok=True)
os.environ['SESSION_CACHE_DIR']=str(E/'private-sessions')
from app import create_app
app=create_app();app.config['TESTING']=True;client=app.test_client();downloads={}
for kind,ext in [('source','c'),('header','h')]:
 response=client.get('/help/source/queue/'+kind);assert response.status_code==200;data=response.data;assert data==(R/('docs/tads_C/tad_cola.'+ext)).read_bytes();(N/('tad_cola.'+ext)).write_bytes(data);downloads[kind]={'HTTP':200,'sha256':hashlib.sha256(data).hexdigest()}
C=(N/'tad_cola.c').read_text(encoding='utf-8-sig');start=C.index('int cola_desencolar(');end=C.index('\n}',start)+2;body=C[start:end]
patched=body.replace('{\n','{\n qa_event("entry",q,-1);\n',1).replace('if (q == NULL || q->delante == NULL) {','if (qa_guard("root_guard",q,q == NULL || q->delante == NULL)) {').replace('printf("Cola vacía. No se puede desencolar.\\n");','printf("Cola vacía. No se puede desencolar.\\n");qa_event("error_printf",q,-1);').replace('return -1;','qa_result(-1);qa_event("return_error",q,-1);return -1;').replace('struct NodoCola *aux = q->delante;','struct NodoCola *aux = q->delante;\n _Static_assert(_Generic(aux,struct NodoCola*:1,default:0),"aux type");qa_aux(aux);qa_event("aux_assigned",q,-1);').replace('int num = aux->nro;','int num = aux->nro;\n _Static_assert(_Generic(num,int:1,default:0),"num type");qa_num(num);qa_event("num_assigned",q,-1);').replace('q->delante = aux->sgte;','q->delante = aux->sgte;qa_event("front_assigned",q,-1);').replace('if (q->delante == NULL) {','if (qa_guard("last_guard",q,q->delante == NULL)) {').replace('q->atras = NULL;','q->atras = NULL;qa_event("rear_cleared",q,-1);').replace('free(aux);','qa_event("free_enter",q,-1);free(aux);qa_event("free_return",q,-1);').replace('return num;','qa_result(num);qa_event("return_num",q,-1);return num;').replace('printf(','qa_printf(')
(N/'instrumented.c').write_text(C[:start]+patched+C[end:],encoding='utf-8')
(N/'hooks.h').write_text('#include <stddef.h>\nstruct Cola;struct NodoCola;\nvoid qa_event(const char*,struct Cola*,int);int qa_guard(const char*,struct Cola*,int);void qa_aux(struct NodoCola*);void qa_num(int);void qa_result(int);void*qa_malloc(size_t);void qa_free(void*);int qa_printf(const char*,...);\n',encoding='utf-8')
DRIVER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <limits.h>
#include "tad_cola.h"
_Static_assert(_Generic(&cola_desencolar,int(*)(struct Cola*):1,default:0),"dequeue signature");
static void*objects[64];static int live[64],used,allocs,frees,active,sid,aux_init,aux_id,aux_live,num_init,num_value,result_init,result_value;static char console[256];
static int id(void*p){if(!p)return -1;for(int i=0;i<used;i++)if(live[i]&&objects[i]==p)return i;assert(0);return -1;}
static void string(const char*s){putchar('"');for(;*s;s++){if(*s=='\n')fputs("\\n",stdout);else if(*s=='"')fputs("\\\"",stdout);else if(*s=='\\')fputs("\\\\",stdout);else putchar(*s);}putchar('"');}
void qa_event(const char*ev,struct Cola*q,int cond){if(!active)return;printf("{\"sample\":%d,\"event\":\"%s\",\"condition\":%d,\"root_NULL\":%d,\"front\":%d,\"rear\":%d,\"aux_initialized\":%d,\"aux_id\":%d,\"aux_alive\":%d,\"num_initialized\":%d,\"num\":%d,\"result_initialized\":%d,\"result\":%d,\"values\":[",sid,ev,cond,q==NULL,q?id(q->delante):-1,q?id(q->atras):-1,aux_init,aux_id,aux_live,num_init,num_value,result_init,result_value);struct NodoCola*n=q?q->delante:NULL;int comma=0;while(n){assert(id(n)>=0);if(comma++)putchar(',');printf("%d",n->nro);n=n->sgte;}fputs("],\"heap\":[",stdout);comma=0;for(int i=0;i<used;i++)if(live[i]){if(comma++)putchar(',');struct NodoCola*t=objects[i];printf("{\"id\":%d,\"value\":%d,\"next\":%d}",i,t->nro,id(t->sgte));}fputs("],\"console\":",stdout);string(console);puts("}");}
int qa_guard(const char*e,struct Cola*q,int v){qa_event(e,q,v);return v;}void qa_aux(struct NodoCola*p){aux_init=1;aux_id=id(p);aux_live=1;}void qa_num(int n){num_init=1;num_value=n;}void qa_result(int n){result_init=1;result_value=n;}
void*qa_malloc(size_t n){void*p=malloc(n);assert(p&&used<64);objects[used]=p;live[used++]=1;allocs++;return p;}
void qa_free(void*p){if(!p)return;int i=id(p);live[i]=0;objects[i]=NULL;if(active&&i==aux_id)aux_live=0;frees++;free(p);}
int qa_printf(const char*fmt,...){va_list args;va_start(args,fmt);int n=vsnprintf(console,sizeof(console),fmt,args);va_end(args);return n;}
static void sample(struct Cola*q){aux_init=num_init=result_init=aux_live=0;aux_id=-1;num_value=result_value=0;console[0]=0;active=1;int result=cola_desencolar(q);active=0;assert(result_init&&result==result_value);sid++;}
'''
CASES=[('null',None),('empty',[]),('single',[-1]),('multi',[7,-1]),('duplicate',[7,7]),('bounds',[-2147483648,2147483647])]
main='int main(void){'
for name,seeds in CASES:
 if seeds is None:main+='sample(NULL);sample(NULL);';continue
 main+='{struct Cola q={NULL,NULL};'
 for v in seeds:main+=f'cola_encolar(&q,{"INT_MIN" if v==-2147483648 else "INT_MAX" if v==2147483647 else v});'
 main+='sample(&q);sample(&q);cola_vaciar(&q);}'
main+='assert(allocs==frees);for(int i=0;i<used;i++)assert(!live[i]);fprintf(stderr,"OWNERSHIP %d %d 0\\n",allocs,frees);return 0;}'
(N/'driver.c').write_text(DRIVER+main,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for cmd,log in [(flags+['-include',str(N/'hooks.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'instrumented.c'),'-o',str(N/'cola.o')],'compile-source.log'),(flags+[str(N/'driver.c'),str(N/'cola.o'),'-o',str(N/'driver.exe')],'compile-driver.log')]:
 p=subprocess.run(cmd,capture_output=True);(N/log).write_bytes(p.stdout+p.stderr);assert p.returncode==0,p.stderr.decode(errors='replace')
p=subprocess.run([str(N/'driver.exe')],capture_output=True);(N/'events.jsonl').write_bytes(p.stdout);(N/'stderr.log').write_bytes(p.stderr);assert p.returncode==0,p.stderr
native=[json.loads(x) for x in p.stdout.decode('utf-8').splitlines()];report=[];resources=[]
for ci,(name,seeds) in enumerate(CASES):
 if seeds is None:continue
 client=app.test_client()
 for v in seeds:assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
 for repeat in [1,2]:
  tracemalloc.start();starttime=time.perf_counter();resp=client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}});elapsed=time.perf_counter()-starttime;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();d=resp.get_json();events=[x for x in native if x['sample']==ci*2+repeat-1];resources.append({'case':name,'repeat':repeat,'python_peak_bytes':peak,'response_bytes':len(resp.data),'seconds_instrumented':elapsed});report.append({'case':name,'repeat':repeat,'HTTP':resp.status_code,'native':events,'data':d})
(E/'API-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');(E/'resources.json').write_text(json.dumps({'calls':resources,'max_python_peak_bytes':max(x['python_peak_bytes'] for x in resources),'max_response_bytes':max(x['response_bytes'] for x in resources),'limits':'10 finite API tracemalloc samples including Flask/session/serialization, not RSS/browser/C heap/universal/OOM/leak/SLA'},indent=2),encoding='utf-8');(E/'native-summary.json').write_text(json.dumps({'calls':12,'events':len(native),'conditions':sum(x['condition']!=-1 for x in native),'signature_types_C17':True,'ownership':p.stderr.decode('utf-8').strip(),'downloads':downloads,'safe_observation':'Registry cleared before actual free; post-free only saved ID/liveness, no freed pointer evaluation or field reads; initialized locals only; consistent seed queues; no real OOM/UB/sanitizer claim'},indent=2),encoding='utf-8');print('native',len(native),'conditions',sum(x['condition']!=-1 for x in native),'API',len(report))
