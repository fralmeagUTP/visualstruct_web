"""Only seven new defined native priority front gaps; no old8seeds rerun."""
from pathlib import Path
import sys,json,re,subprocess,shutil
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8');E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-front-baseline-low';N=E/'new-native-gaps';N.mkdir(exist_ok=True)
for ext in ['c','h']:shutil.copyfile(E/('current-tad_cola_prioridad.'+ext),N/('tad_cola_prioridad.'+ext))
C=(N/'tad_cola_prioridad.c').read_text(encoding='utf-8-sig');start=C.index('bool cp_frente(');openbrace=C.index('{',start);depth=1;end=openbrace+1
while depth:depth+=(C[end]=='{')-(C[end]=='}');end+=1
body=C[openbrace+1:end-1];result=['qa_event("entry",cola,-1);'];names=['actual','prev','objetivo','objetivoPrev']
for raw in body.splitlines():
 line=raw.strip();indent=raw[:len(raw)-len(raw.lstrip())]
 if not line or line in ['}','} else {','{']:result.append(raw);continue
 decl=re.fullmatch(r'const CPNodo \*(\w+);',line);quoted=json.dumps(line,ensure_ascii=True)
 if decl:result += [raw,indent+f'_Static_assert(_Generic({decl[1]},const CPNodo*:1,default:0),"const CPNodo pointer type");',indent+f'qa_event({quoted},cola,-1);'];continue
 cond=re.fullmatch(r'(if|while) \((.*)\) \{',line)
 if cond:result.append(indent+f'{cond[1]} (qa_test({quoted},({cond[2]}),cola)) {{');continue
 if line.startswith('return '):result.append(indent+f'qa_result({"0" if line=="return false;" else "1"});qa_event({quoted},cola,-1);');result.append(raw);continue
 result.append(raw)
 for idx,name in enumerate(names):
  if re.match(re.escape(name)+r'\s*=',line):result.append(indent+f'qa_alias({idx},{name});')
 if line=='*valor = objetivo->valor;':result.append(indent+'qa_value_written();')
 if line=='*prioridad = objetivo->prioridad;':result.append(indent+'qa_priority_written();')
 result.append(indent+f'qa_event({quoted},cola,-1);')
patched=C[:openbrace+1]+'\n'+'\n'.join(result)+'\n'+C[end-1:];(N/'instrumented.c').write_text(patched,encoding='utf-8');(N/'hooks.h').write_text('#include <stddef.h>\n#include <stdbool.h>\n#include "tad_cola_prioridad.h"\nvoid qa_event(const char*,const ColaPrioridad*,int);bool qa_test(const char*,bool,const ColaPrioridad*);void qa_alias(int,const CPNodo*);void qa_result(int);void qa_value_written(void);void qa_priority_written(void);void*qa_malloc(size_t);void qa_free(void*);\n',encoding='utf-8')
DRIVER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include "tad_cola_prioridad.h"
_Static_assert(_Generic(&cp_frente,bool(*)(const ColaPrioridad*,int*,int*):1,default:0),"bool/output-pointer signature");
static void*objects[64];static int alive[64],used,allocs,frees,active,sid,aliases[4],defined[4],value_written,priority_written,ret=-1;static int *value_ptr,*priority_ptr;
static int id(const void*p){if(!p)return -1;for(int i=0;i<used;i++)if(alive[i]&&objects[i]==p)return i;assert(0);return -1;}
static void string(const char*s){putchar('"');for(;*s;s++){if(*s=='"'||*s=='\\')putchar('\\');putchar(*s);}putchar('"');}
void qa_event(const char*line,const ColaPrioridad*q,int cond){if(!active)return;printf("{\"sample\":%d,\"line\":",sid);string(line);printf(",\"condition\":%d,\"root_NULL\":%d,\"front\":%d,\"rear\":%d,\"count\":%d,\"value_ptr_NULL\":%d,\"priority_ptr_NULL\":%d,\"outputs_initialized\":true,\"value_written\":%d,\"priority_written\":%d,\"return\":%d,\"output_value\":",cond,q==NULL,q?id(q->delante):-1,q?id(q->atras):-1,q?q->cantidad:0,value_ptr==NULL,priority_ptr==NULL,value_written,priority_written,ret);if(value_ptr)printf("%d",*value_ptr);else fputs("null",stdout);fputs(",\"output_priority\":",stdout);if(priority_ptr)printf("%d",*priority_ptr);else fputs("null",stdout);fputs(",\"aliases\":[",stdout);for(int i=0;i<4;i++){if(i)putchar(',');if(defined[i])printf("%d",aliases[i]);else fputs("null",stdout);}fputs("],\"heap\":[",stdout);int comma=0;for(int i=0;i<used;i++)if(alive[i]){if(comma++)putchar(',');CPNodo*n=objects[i];printf("{\"id\":%d,\"value\":%d,\"priority\":%d,\"next\":%d}",i,n->valor,n->prioridad,id(n->sgte));}fputs("],\"items\":[",stdout);comma=0;for(CPNodo*n=q?q->delante:NULL;n;n=n->sgte){assert(id(n)>=0);if(comma++)putchar(',');printf("[%d,%d]",n->valor,n->prioridad);}puts("]}");}
bool qa_test(const char*l,bool v,const ColaPrioridad*q){qa_event(l,q,v);return v;}void qa_alias(int i,const CPNodo*p){aliases[i]=id(p);defined[i]=1;}void qa_result(int n){ret=n;}void qa_value_written(void){value_written=1;}void qa_priority_written(void){priority_written=1;}
void*qa_malloc(size_t n){void*p=malloc(n);assert(p&&used<64);objects[used]=p;alive[used++]=1;allocs++;return p;}void qa_free(void*p){if(!p)return;int j=id(p);alive[j]=0;objects[j]=NULL;frees++;free(p);}
static void sample(ColaPrioridad*q,int*v,int*p){for(int i=0;i<4;i++){defined[i]=0;aliases[i]=-1;}value_written=priority_written=0;ret=-1;value_ptr=v;priority_ptr=p;active=1;bool result=cp_frente(q,v,p);active=0;assert((int)result==ret);sid++;value_ptr=priority_ptr=NULL;}
int main(void){int v=-999,p=-888;sample(NULL,&v,&p);{ColaPrioridad q;cp_inicializar(&q);sample(&q,&v,&p);}for(int mode=0;mode<3;mode++){ColaPrioridad q;cp_inicializar(&q);assert(cp_encolar(&q,17,7));v=-999;p=-888;sample(&q,mode==0||mode==2?NULL:&v,mode==1||mode==2?NULL:&p);cp_vaciar(&q);} {ColaPrioridad q;cp_inicializar(&q);assert(cp_encolar(&q,INT_MAX,INT_MAX));assert(cp_encolar(&q,INT_MIN,INT_MIN));sample(&q,&v,&p);cp_vaciar(&q);} {ColaPrioridad q;cp_inicializar(&q);assert(cp_encolar(&q,-1,-1));sample(&q,&v,&p);cp_vaciar(&q);}assert(allocs==frees);for(int i=0;i<used;i++)assert(!alive[i]);fprintf(stderr,"OWNERSHIP %d %d 0\n",allocs,frees);return 0;}
'''
shape_start=C.index('struct cp_nodo {');shape=C[shape_start:C.index('};',shape_start)+2];DRIVER=DRIVER.replace('#include \"tad_cola_prioridad.h\"','#include \"tad_cola_prioridad.h\"\n'+shape)
(N/'driver.c').write_text(DRIVER,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for cmd,name in [(flags+['-I',str(N),'-include',str(N/'hooks.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'instrumented.c'),'-o',str(N/'priority.o')],'compile-source.log'),(flags+['-I',str(N),str(N/'driver.c'),str(N/'priority.o'),'-o',str(N/'driver.exe')],'compile-driver.log')]:
 p=subprocess.run(cmd,capture_output=True);(N/name).write_bytes(p.stdout+p.stderr);assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True);(N/'events.jsonl').write_bytes(p.stdout);(N/'stderr.log').write_bytes(p.stderr);assert p.returncode==0,p.stderr;events=[json.loads(x) for x in p.stdout.decode('utf-8').splitlines()]
from app.domain.sequential import tad_cola_prioridad as native_py
cases=[('root_NULL',None,False,False),('empty',[],False,False),('value_NULL',[(17,7)],True,False),('priority_NULL',[(17,7)],False,True),('both_NULL',[(17,7)],True,True),('extremes',[(2147483647,2147483647),(-2147483648,-2147483648)],False,False),('minus1',[(-1,-1)],False,False)];report=[]
for sid,(name,seeds,no_v,no_p) in enumerate(cases):
 q=None if seeds is None else native_py.ColaPrioridad();v=None if no_v else [-999];pr=None if no_p else [-888]
 for value,priority in seeds or []:native_py.cp_encolar(q,value,priority)
 if name=='counter_zero':q.cantidad=0
 try:retval=native_py.cp_frente(q,v,pr);error=None
 except Exception as ex:retval=None;error=type(ex).__name__+': '+str(ex)
 last=[x for x in events if x['sample']==sid][-1];items=[];node=q.delante if q else None
 while node:items.append([node.valor,node.prioridad]);node=node.sgte
 expected={'return':bool(last['return']),'items':last['items'],'count':last['count'],'value':last['output_value'],'priority':last['output_priority']};actual={'return':retval,'items':items,'count':q.cantidad if q else 0,'value':v[0] if v else None,'priority':pr[0] if pr else None};report.append({'case':name,'native_final':expected,'python_final':actual,'python_error':error,'same':not error and expected==actual,'fixture_label':'Defined inconsistent zero counter with live node, raw C/Python only, not valid public-API queue' if name=='counter_zero' else 'private guard or consistent int fixture'})
(E/'new-native-gap-report.json').write_text(json.dumps({'calls':7,'events':len(events),'conditions':sum(x['condition']!=-1 for x in events),'ownership':p.stderr.decode('utf-8').strip(),'signature_types_C17':True,'no_old8seeds_rerun':True,'cases':report,'safe':'initialized caller output sentinels; unevaluated _Generic for uninitialized local types; saved IDs before free, registry cleared before actual free, no evaluation of dangling pointers/no UB/realOOM/sanitizer. Counterzero labelled inconsistent raw fixture only.'},indent=2)+'\n',encoding='utf-8');print('newnative7 events',len(events),'conditions',sum(x['condition']!=-1 for x in events),'Python divergences',[x['case'] for x in report if not x['same']])
