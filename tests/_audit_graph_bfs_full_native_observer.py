"""LOW actual-C BFS boundaries; not a full typed-helper/UI conformance claim."""
from pathlib import Path
import os,sys,re,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph import tad_grafo as G
from _audit_rbt_insert_native_observer import plain
CASES=[
 {'name':'empty','vertices':[],'edges':[],'start':0},
 {'name':'singleton_minus_one','vertices':[-1],'edges':[],'start':-1},
 {'name':'missing_start','vertices':[1,2],'edges':[[1,2]],'start':99},
 {'name':'branch','vertices':[1,2,3,4],'edges':[[1,2],[1,3],[2,4]],'start':1},
 {'name':'disconnected','vertices':[1,2,3,4],'edges':[[1,2],[3,4]],'start':1},
 {'name':'cycle','vertices':[1,2,3],'edges':[[1,2],[2,3],[3,1]],'start':1},
 {'name':'diamond','vertices':[1,2,3,4],'edges':[[1,2],[1,3],[2,4],[3,4]],'start':1},
 {'name':'negative_cycle','vertices':[-2,-1,0,5],'edges':[[-2,-1],[-1,0],[0,-2]],'start':-2},
 {'name':'signed_extrema','vertices':[-2147483648,-1,2147483647],'edges':[[-2147483648,-1],[-1,2147483647]],'start':-2147483648},
 {'name':'repeat','vertices':[1,2,3,4],'edges':[[1,2],[1,3],[2,4]],'start':1,'repeat':2},
]

def instrument_helpers(source,queue=False):
 rows=source.splitlines();names={'cola_encolar','cola_desencolar'} if queue else {'grafo_desmarcar','grafo_marcar_vertice','grafo_marcado_vertice','grafo_sucesores'}
 for fn in names:
  begin=next(i for i,row in enumerate(rows) if re.match(r'\s*(?:void|int|Grafo|ListaVertice)\s+'+fn+r'\s*\(',row));depth=0;end=None
  for j in range(begin,len(rows)):
   depth+=rows[j].count('{')-rows[j].count('}')
   if j>begin and depth==0:end=j;break
  assert end is not None
  # All substitutions preserve original line numbers and evaluate expressions once.
  for j in range(begin,end+1):
   raw=rows[j];row=plain(raw).split('//',1)[0].strip();line=j+1
   hook=lambda phase,result='-2':f'audit_helper_emit("{fn}",{line},"{phase}",{result});'
   if j==begin:rows[j]=raw.replace('{','{ '+hook('enter'),1);continue
   if j==end:
    if fn=='cola_encolar':rows[j]=raw.replace('}',hook('return')+' }',1)
    continue
   if not row or row in ['{','}','} else {']:continue
   if row.startswith(('if (','while (')):
    start=raw.index('(');nest=0
    for k in range(start,len(raw)):
     nest+=int(raw[k]=='(')-int(raw[k]==')')
     if nest==0:stop=k;break
    expr=raw[start+1:stop];rows[j]=raw[:start+1]+f'audit_helper_test("{fn}",{line},({expr}))'+raw[stop:];continue
   if row=='break;':rows[j]=raw.replace('break;',hook('break')+' break;');continue
   if row.startswith('return '):
    expr=row[7:].rstrip(';');typ='Grafo' if fn in ['grafo_desmarcar','grafo_marcar_vertice'] else 'ListaVertice' if fn=='grafo_sucesores' else 'int';result='audit_result' if typ=='int' else '-2'
    rows[j]=raw.replace(row,'{ '+typ+' audit_result = '+expr+'; '+hook('return',result)+' return audit_result; }');continue
   if row=='return;':rows[j]=raw.replace(row,hook('return')+' return;');continue
   if row.endswith(';'):
    # Do not execute diagnostic printf paths in the normal-allocation baseline.
    phase='free' if row.startswith('free(') else 'allocate' if 'malloc' in row else 'statement'
    if not row.startswith('printf('):rows[j]=raw.split('//',1)[0]+' '+hook(phase)+(' //'+raw.split('//',1)[1] if '//' in raw else '')
 return '\n'.join(rows)+'\n'

HELPER=r'''
#include <stddef.h>
static void *audit_ptrs[4096];static int audit_live[4096],audit_count,audit_active,audit_alloc,audit_freed,audit_case,audit_run;
static Grafo audit_graph;static struct Cola*audit_q;static ListaVertice*audit_rec;static ListaVertice audit_suces;
static int audit_v,audit_actual,audit_actual_init,audit_existe,audit_tmp,audit_tmp_bits,audit_temp;
static int audit_id(void*p){if(!p)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_ptrs[i]==p)return i+1;return -1;}
void*audit_malloc(size_t n){void*p=malloc(n);if(p){if(audit_count>=4096)exit(90);audit_ptrs[audit_count]=p;audit_live[audit_count++]=1;if(audit_active)audit_alloc++;}return p;}
void audit_free(void*p){if(p){int id=audit_id(p);if(id<=0)exit(91);audit_live[id-1]=0;if(audit_active)audit_freed++;}free(p);}
static void audit_list(ListaVertice n){printf("[");int first=1;while(n){printf("%s%d",first?"":",",n->dato);first=0;n=n->sig;}printf("]");}
static const char*audit_function="grafo_bfs";
static void audit_emit(int line,const char*phase,int result){
 printf("OBS {\"case\":%d,\"run\":%d,\"line\":%d,\"phase\":\"%s\",\"function\":\"%s\",\"result\":%d,\"allocations\":%d,\"frees\":%d,\"graph_marks\":[",audit_case,audit_run,line,phase,audit_function,result,audit_alloc,audit_freed);
 int first=1;for(ListaVertice v=audit_graph.v;v;v=v->sig){printf("%s{\"id\":%d,\"vertex\":%d,\"mark\":%d}",first?"":",",audit_id(v),v->dato,v->marcado);first=0;}printf("],\"queue\":[");
 first=1;if(audit_q){for(struct NodoCola*n=audit_q->delante;n;n=n->sgte){printf("%s{\"id\":%d,\"value\":%d}",first?"":",",audit_id(n),n->nro);first=0;}}printf("],\"returned_list\":");audit_list(audit_rec?*audit_rec:NULL);
 printf(",\"successors\":");audit_list(audit_suces);printf(",\"cursor_id\":%d,\"actual_initialized\":%d,\"actual\":%d,\"existe\":%d,\"tmp_id\":%d,\"tmp_initialized_fields\":%d,\"temp_cached_id\":%d,\"temp_live\":%d}\n",audit_v,audit_actual_init,audit_actual,audit_existe,audit_tmp,audit_tmp_bits,audit_temp,audit_temp>0?audit_live[audit_temp-1]:0);
}
static int audit_condition(int line,int result){audit_emit(line,"condition",!!result);return result;}
void audit_helper_emit(const char*fn,int line,const char*phase,int result){if(audit_active){audit_function=fn;audit_emit(line,phase,result);audit_function="grafo_bfs";}}
int audit_helper_test(const char*fn,int line,int result){audit_helper_emit(fn,line,"condition",result);return result;}
#define malloc audit_malloc
#define free audit_free
'''
def instrument(source):
 masked=plain(source);m=re.search(r'ListaVertice grafo_bfs\([^;]+?\)\s*\{',masked);assert m
 a=m.end();z=a;depth=1
 while depth:
  depth+=(masked[z]=='{')-(masked[z]=='}');z+=1
 body=source[a:z-1];mask=masked[a:z-1];edits=[]
 def line(pos):return source.count('\n',0,a+pos)+1
 for c in re.finditer(r'\b(?:if|while)\s*\(',mask):
  x=c.end();end=x;d=1
  while d:d+=(mask[end]=='(')-(mask[end]==')');end+=1
  edits.append((x,end-1,f'audit_condition({line(c.start())},!!({body[x:end-1]}))'))
 statements={
 'g = grafo_desmarcar(g);':'audit_graph=g;',
 'struct Cola cola = {NULL, NULL};':'audit_q=&cola;',
 'ListaVertice recorrido = NULL;':'audit_rec=&recorrido;',
 'ListaVertice ultimo = NULL;':'',
 'ListaVertice v = g.v;':'audit_v=audit_id(v);',
 'int existe = 0;':'audit_existe=existe;',
 'existe = 1;':'audit_existe=existe;',
 'v = v->sig;':'audit_v=audit_id(v);',
 'cola_encolar(&cola, inicio);':'',
 'g = grafo_marcar_vertice(g, inicio);':'audit_graph=g;',
 'int actual = cola_desencolar(&cola);':'audit_actual=actual;audit_actual_init=1;',
 'ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));':'audit_tmp=audit_id(tmp);audit_tmp_bits=0;',
 'tmp->dato = actual;':'audit_tmp_bits|=1;',
 'tmp->marcado = 0;':'audit_tmp_bits|=2;',
 'tmp->sig = NULL;':'audit_tmp_bits|=4;',
 'recorrido = tmp;':'', 'ultimo->sig = tmp;':'','ultimo = tmp;':'',
 'ListaVertice suces = grafo_sucesores(g, actual);':'audit_suces=suces;',
 'cola_encolar(&cola, suces->dato);':'',
 'g = grafo_marcar_vertice(g, suces->dato);':'audit_graph=g;',
 'ListaVertice temp = suces;':'audit_temp=audit_id(temp);',
 'suces = suces->sig;':'audit_suces=suces;',
 'free(temp);':'',
 }
 for stmt,cache in statements.items():
  for c in re.finditer(re.escape(stmt),body):
   if stmt=='recorrido = tmp;' and re.search(r'ListaVertice\s+$',body[:c.start()]):continue
   phase='free' if stmt.startswith('free') else 'statement'
   edits.append((c.start(),c.end(),'{'+stmt+cache+f'audit_emit({line(c.start())},"{phase}",-2);'+'}')) if not stmt.startswith(('struct Cola','ListaVertice ','int actual','int existe')) else edits.append((c.end(),c.end(),cache+f'audit_emit({line(c.start())},"{phase}",-2);'))
 # Declarations retain their original scope; controlled non-declarations remain one statement.
 for c in re.finditer(r'\breturn\s+(NULL|recorrido);',mask):
  expr=c.group(1);edits.append((c.start(),c.end(),'{audit_emit('+str(line(c.start()))+',"return",audit_id('+expr+'));audit_q=NULL;audit_rec=NULL;audit_suces=NULL;return '+expr+';}'))
 for c in re.finditer(r'\b(?:break|continue);',mask):edits.append((c.start(),c.end(),'{audit_emit('+str(line(c.start()))+',"control",-2);'+c.group()+'}'))
 last=-1
 for x,y,_ in sorted(edits):assert x>=last,(x,last);last=y
 for x,y,text in sorted(edits,reverse=True):body=body[:x]+text+body[y:]
 entry='audit_graph=g;audit_q=NULL;audit_rec=NULL;audit_suces=NULL;audit_v=0;audit_actual=0;audit_actual_init=0;audit_existe=0;audit_tmp=0;audit_tmp_bits=0;audit_temp=0;audit_emit('+str(source.count('\n',0,m.start())+1)+',"enter",-2);'
 source=source[:a]+entry+body+source[z-1:]
 anchor='} Grafo;';assert source.count(anchor)==1;return source.replace(anchor,anchor+'\n'+HELPER)
def observe(out):
 out=Path(out);out.mkdir(exist_ok=False);os.environ['SESSION_CACHE_DIR']=str(out/'session-cache');client=create_app().test_client();hashes={}
 for sid,filename in [('graph','tad_grafo'),('queue','tad_cola')]:
  for ext,part in [('c','source'),('h','header')]:
   raw=client.get('/help/source/'+sid+'/'+part).data;assert raw==(ROOT/'docs/tads_C'/(filename+'.'+ext)).read_bytes(),(sid,ext);(out/(filename+'.'+ext)).write_bytes(raw);hashes[filename+'.'+ext]=hashlib.sha256(raw).hexdigest()
 source=(out/'tad_grafo.c').read_text(encoding='utf-8-sig');queue=(out/'tad_cola.c').read_text(encoding='utf-8-sig')
 qprefix='#include <stdlib.h>\nextern void*audit_malloc(size_t);\nextern void audit_free(void*);\nextern void audit_helper_emit(const char*,int,const char*,int);\nextern int audit_helper_test(const char*,int,int);\n#define malloc audit_malloc\n#define free audit_free\n'
 (out/'queue-observed.c').write_text(qprefix+instrument_helpers(queue,queue=True),encoding='utf-8')
 main='\nint main(void){\n'
 for case,c in enumerate(CASES):
  main+='{audit_active=0;Grafo g=grafo_crear();'+''.join(f'g=grafo_insertar_vertice(g,{v});' for v in c['vertices'])+''.join(f'g=grafo_insertar_arco(g,{u},{v},1);' for u,v in c['edges'])
  for run in range(c.get('repeat',1)):
   main+=f'audit_case={case};audit_run={run};audit_alloc=0;audit_freed=0;audit_active=1;ListaVertice rec{run}=grafo_bfs(g,{c["start"]});audit_active=0;printf("RESULT {case} {run} ");audit_list(rec{run});puts("");while(rec{run}){{ListaVertice n=rec{run};rec{run}=n->sig;free(n);}}'
  main+='while(g.v){ListaVertice n=g.v;g.v=n->sig;free(n);}while(g.a){ListaArco n=g.a;g.a=n->sig;free(n);}}\n'
 main+='for(int i=0;i<audit_count;i++){if(audit_live[i]){return 92;}} return 0;}'
 (out/'observed.c').write_text(instrument(instrument_helpers(source))+main,encoding='utf-8')
 cmd=[shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),str(out/'queue-observed.c'),'-o',str(out/'observed.exe')];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0 and not p.stderr,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);(out/'stdout.log').write_text(p.stdout,encoding='utf-8');assert p.returncode==0,(p.returncode,p.stderr)
 events=[json.loads(x[4:]) for x in p.stdout.splitlines() if x.startswith('OBS ')];outputs={(int(m.group(1)),int(m.group(2))):json.loads(m.group(3)) for m in re.finditer(r'^RESULT (\d+) (\d+) (.*)$',p.stdout,re.M)};cases=[]
 for case,c in enumerate(CASES):
  history=[{'operation':'create_graph','payload':{'directed':True}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in c['vertices']],*[{'operation':'insert_edge','payload':{'origin':u,'target':v,'weight':1}} for u,v in c['edges']]]
  data=S.execute_operation('graph','run_bfs',{'start':c['start']},history);g=G.grafo_crear()
  for v in c['vertices']:g=G.grafo_insertar_vertice(g,v)
  for u,v in c['edges']:g=G.grafo_insertar_arco(g,u,v,1)
  raw=G.grafo_bfs(g,c['start']);rawvalues=[]
  while raw:rawvalues.append(raw.dato);raw=raw.sig
  expected=outputs[case,0];assert rawvalues==expected,(case,rawvalues,expected)
  if c['start'] in c['vertices']:assert data['success'] and data['result']==expected,(case,data['result'],expected)
  else:assert not data['success'] and expected==[]
  if c.get('repeat'):assert outputs[case,0]==outputs[case,1]
  trace=data['execution_trace'];cases.append({**c,'case':case,'native_order':expected,'backend_success':data['success'],'backend_order':data.get('result'),'native_events':sum(e['case']==case for e in events),'native_final_marks':[e['graph_marks'] for e in events if e['case']==case and e['phase']=='return'],'python_domain_marks':g._marcas,'bfs_persisted':any(h['operation']=='run_bfs' for h in data['history']),'trace_steps':len(trace['steps']),'source_definitions':re.findall(r'^(?:static\s+)?(?:Grafo|ListaVertice|void|int)\s+(\w+)\s*\(',trace['source_code'],re.M),'scope_frames':sorted({f.get('function') for s in trace['steps'] for f in s['pedagogy'].get('call_stack',[])}),'all_steps_memory_state':all('memory_state' in s['pedagogy'] for s in trace['steps'])})
 report={'cases':cases,'events':events,'native_events':len(events),'native_runs':len(outputs),'source_hashes':hashes,'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'strict_c17':True,'caller_cleanup_live_allocations':0,'limits':['LOW BFS boundaries only; no typed helper-frame or per-operand instrumentation.','Queue/result/marks/lifetimes independently observed after actual statements; cached IDs never inspect freed pointers.','No malloc-failure injection; normal finite graphs only.','Backend endpoints agree, but marks/history/trace distinctions remain findings, not full conformance.','No both-view/replay or all-path closure claimed.']};(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'cases':len(cases),'native_runs':len(outputs),'events':len(events),'out':str(out)}),flush=True);return report
if __name__=='__main__':observe(os.environ['AUDIT_OUTPUT_DIR'])
