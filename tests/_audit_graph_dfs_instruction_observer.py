"""Actual downloaded DFS instruction observations, finite normal allocation."""
from pathlib import Path
import os,sys,re,json,subprocess,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from app import create_app
from _audit_rbt_insert_native_observer import plain
from _audit_graph_bfs_native_observer import CASES
NAMES=['grafo_dfs','grafo_dfs_recursivo','grafo_agregar_recorrido','grafo_existe_vertice','grafo_desmarcar','grafo_marcar_vertice','grafo_marcado_vertice','grafo_sucesores']
HELPER=r"""
static void *audit_ptrs[4096];static int audit_live[4096],audit_kind[4096],audit_bits[4096],audit_count,audit_active,audit_alloc,audit_freed,audit_case,audit_run;
static Grafo audit_graph;static ListaVertice *audit_head;
struct AuditFrame{const char*fn;int id,param,has_param,headref,count;const char*names[20];int vals[20];};
static struct AuditFrame audit_frames[128];static int audit_depth,audit_frame_id;
static int audit_id(void*p){if(!p)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_ptrs[i]==p)return i+1;exit(90);}
static void audit_local(const char*name,int val){struct AuditFrame*f=&audit_frames[audit_depth-1];for(int i=0;i<f->count;i++)if(!strcmp(f->names[i],name)){f->vals[i]=val;return;}int i=f->count++;f->names[i]=name;f->vals[i]=val;}
static void audit_drop(const char*name){struct AuditFrame*f=&audit_frames[audit_depth-1];for(int i=0;i<f->count;i++)if(!strcmp(f->names[i],name)){for(int j=i+1;j<f->count;j++){f->names[j-1]=f->names[j];f->vals[j-1]=f->vals[j];}f->count--;return;}}
static void audit_heap(void*p,int kind,int bits){int id=audit_id(p);if(id){audit_kind[id-1]=kind;audit_bits[id-1]|=bits;}}
void*audit_malloc(size_t n){void*p=malloc(n);if(p){if(audit_count==4096)exit(91);audit_ptrs[audit_count]=p;audit_kind[audit_count]=0;audit_bits[audit_count]=0;audit_live[audit_count++]=1;if(audit_active)audit_alloc++;}return p;}
void audit_free(void*p){if(p){int id=audit_id(p);audit_live[id-1]=0;if(audit_active)audit_freed++;}free(p);}
static void audit_emit(int line,const char*phase,int result){if(!audit_active)return;
 struct AuditFrame*f=&audit_frames[audit_depth-1];printf("OBS {\"case\":%d,\"run\":%d,\"line\":%d,\"function\":\"%s\",\"phase\":\"%s\",\"result\":%d,\"allocations\":%d,\"frees\":%d,\"head\":%d,\"frames\":[",audit_case,audit_run,line,f->fn,phase,result,audit_alloc,audit_freed,audit_head?audit_id(*audit_head):-2);
 for(int j=0;j<audit_depth;j++){struct AuditFrame*q=&audit_frames[j];printf("%s{\"function\":\"%s\",\"id\":%d,\"has_param\":%d,\"param\":%d,\"headref\":%d,\"locals\":{",j?",":"",q->fn,q->id,q->has_param,q->param,q->headref);for(int k=0;k<q->count;k++)printf("%s\"%s\":%d",k?",":"",q->names[k],q->vals[k]);printf("}}");}printf("],\"heap\":[");int first=1;
 for(int j=0;j<audit_count;j++){if(!audit_live[j]||!audit_kind[j])continue;int kind=audit_kind[j],bits=audit_bits[j];printf("%s{\"id\":%d,\"kind\":%d,\"bits\":%d",first?"":",",j+1,kind,bits);first=0;
  if(kind==4){ListaArco n=audit_ptrs[j];printf(",\"origin\":%d,\"target\":%d,\"next\":%d",n->origen,n->destino,audit_id(n->sig));}else{ListaVertice n=audit_ptrs[j];if(bits&1)printf(",\"value\":%d",n->dato);if(bits&2)printf(",\"mark\":%d",n->marcado);if(bits&4)printf(",\"next\":%d",audit_id(n->sig));}printf("}");}puts("]}");
}
static void audit_enter(const char*fn,int line,int param,int has_param,int headref){if(!audit_active)return;if(audit_depth==128)exit(92);struct AuditFrame*f=&audit_frames[audit_depth++];memset(f,0,sizeof(*f));f->fn=fn;f->id=++audit_frame_id;f->param=param;f->has_param=has_param;f->headref=headref;audit_emit(line,"enter",-2);}
static void audit_leave(int line,int result){audit_emit(line,"return",result);if(audit_active)audit_depth--;}
static int audit_test(int line,int result){audit_emit(line,"condition",!!result);return result;}
#define malloc audit_malloc
#define free audit_free
"""

def instrument(source):
 masked=plain(source);edits=[]
 for fn in NAMES:
  m=re.search(r'(?:static\s+)?(?:void|int|Grafo|ListaVertice)\s+'+fn+r'\s*\([^;]+?\)\s*\{',masked);assert m,fn
  a=m.end();z=a;depth=1
  while depth:depth+=(masked[z]=='{')-(masked[z]=='}');z+=1
  body=source[a:z-1];mask=masked[a:z-1]
  def line(pos):return source.count('\n',0,a+pos)+1
  param='inicio' if fn=='grafo_dfs' else 'actual' if fn=='grafo_dfs_recursivo' else 'x' if fn in ['grafo_existe_vertice','grafo_marcar_vertice','grafo_marcado_vertice','grafo_sucesores'] else '0'
  entry=f'audit_enter("{fn}",{source.count(chr(10),0,m.start())+1},{param},{int(param!="0")},{int(fn in ["grafo_dfs_recursivo","grafo_agregar_recorrido"])});'
  if fn=='grafo_dfs':entry='audit_graph=g;audit_head=NULL;'+entry
  if fn=='grafo_agregar_recorrido':entry+='audit_local("nuevo",audit_id(nuevo));'
  edits.append((a,a,entry))
  for c in re.finditer(r'\b(?:if|while)\s*\(',mask):
   x=c.end();end=x;d=1
   while d:d+=(mask[end]=='(')-(mask[end]==')');end+=1
   edits.append((a+x,a+end-1,f'audit_test({line(c.start())},!!({body[x:end-1]}))'))
  statements={
   'ListaVertice k=g.v;':('audit_local("k",audit_id(k));',True),
   'ListaVertice k = g.v;':('audit_local("k",audit_id(k));',True),
   'k=k->sig;':('audit_local("k",audit_id(k));',False),
   'k = k->sig;':('audit_local("k",audit_id(k));',False),
   'k->marcado = 0;':('',False),'k->marcado = 1;':('',False),
   'g = grafo_desmarcar(g);':('',False),'g = grafo_marcar_vertice(g, actual);':('',False),
   'ListaArco k = g.a;':('audit_local("k",audit_id(k));',True),
   'ListaVertice ver = NULL, nuevo;':('audit_local("ver",0);audit_local("nuevo",-2);',True),
   'nuevo = (ListaVertice)malloc(sizeof(struct NodoV));':('audit_local("nuevo",audit_id(nuevo));audit_heap(nuevo,2,0);',False),
   'nuevo->sig = ver;':('audit_heap(nuevo,2,4);',False),'nuevo->dato = k->destino;':('audit_heap(nuevo,2,1);',False),'nuevo->marcado = 0;':('audit_heap(nuevo,2,2);',False),'ver = nuevo;':('audit_local("ver",audit_id(ver));',False),
   'ListaVertice ultimo;':('audit_local("ultimo",-2);',True),
   'nuevo->sig = NULL;':('audit_heap(nuevo,1,4);',False),
   '*recorrido = nuevo;':('',False),'ultimo = *recorrido;':('audit_local("ultimo",audit_id(ultimo));',False),'ultimo = ultimo->sig;':('audit_local("ultimo",audit_id(ultimo));',False),'ultimo->sig = nuevo;':('',False),
   'ListaVertice recorrido = NULL;':('audit_head=&recorrido;audit_local("recorrido",0);',True),
   'ListaVertice tmp = (ListaVertice) malloc(sizeof(struct NodoV));':('audit_local("tmp",audit_id(tmp));audit_heap(tmp,1,0);',True),
   'tmp->dato = actual;':('audit_heap(tmp,1,1);',False),'tmp->marcado = 0;':('audit_heap(tmp,1,2);',False),
   'grafo_agregar_recorrido(recorrido, tmp);':('',False),'ListaVertice suces = grafo_sucesores(g, actual);':('audit_local("suces",audit_id(suces));',True),
   'grafo_dfs_recursivo(g, suces->dato, recorrido);':('',False),'grafo_dfs_recursivo(g, inicio, &recorrido);':('',False),
   'ListaVertice temp = suces;':('audit_local("temp",audit_id(temp));',True),'suces = suces->sig;':('audit_local("suces",audit_id(suces));',False),'free(temp);':('',False),
  }
  for stmt,(cache,decl) in statements.items():
   for c in re.finditer(re.escape(stmt),mask):
    # Cache explicit shared-head assignment in root frame without reading its C local later.
    code=body[c.start():c.end()];phase='allocate' if 'malloc' in stmt else 'free' if stmt.startswith('free') else 'statement';hook=cache+f'audit_emit({line(c.start())},"{phase}",-2);'
    if stmt=='free(temp);':hook+='audit_drop("temp");'
    if stmt=='*recorrido = nuevo;':hook='audit_frames[0].vals[0]=audit_id(*recorrido);'+hook
    if decl:edits.append((a+c.end(),a+c.end(),hook))
    else:edits.append((a+c.start(),a+c.end(),'{'+code+hook+'}'))
  for c in re.finditer(r'\bbreak;',mask):edits.append((a+c.start(),a+c.end(),'{audit_emit('+str(line(c.start()))+',"break",-2);break;}'))
  for c in re.finditer(r'\breturn(?:\s+(NULL|g|ver|recorrido|0|1|k->marcado))?;',mask):
   expr=c.group(1);returnval=expr if expr in ['0','1','k->marcado'] else 'audit_id('+expr+')' if expr in ['NULL','ver','recorrido'] else '-2';code=body[c.start():c.end()];edits.append((a+c.start(),a+c.end(),'{audit_leave('+str(line(c.start()))+','+returnval+');'+('audit_head=NULL;' if fn=='grafo_dfs' else '')+code+'}'))
  if fn in ['grafo_agregar_recorrido','grafo_dfs_recursivo']:edits.append((z-1,z-1,f'audit_leave({source.count(chr(10),0,z-1)+1},-2);'))
 last=-1
 for x,y,_ in sorted(edits):assert x>=last,(x,last);last=y
 for x,y,s in sorted(edits,reverse=True):source=source[:x]+s+source[y:]
 return source.replace('} Grafo;','} Grafo;\n'+HELPER,1)

def observe(out):
 out=Path(out);out.mkdir(exist_ok=False);os.environ['SESSION_CACHE_DIR']=str(out/'cache');client=create_app().test_client();hashes={}
 for sid,name in [('graph','tad_grafo'),('queue','tad_cola')]:
  for ext,part in [('c','source'),('h','header')]:
   resp=client.get('/help/source/'+sid+'/'+part);assert resp.status_code==200;raw=resp.data;assert raw==(ROOT/'docs/tads_C'/(name+'.'+ext)).read_bytes();(out/(name+'.'+ext)).write_bytes(raw);hashes[name+'.'+ext]=hashlib.sha256(raw).hexdigest()
 source=(out/'tad_grafo.c').read_text(encoding='utf-8-sig');main='\nint main(void){\n'
 for idx,c in enumerate(CASES):
  main+='{audit_active=0;Grafo g=grafo_crear();'+''.join(f'g=grafo_insertar_vertice(g,{v});' for v in c['vertices'])+''.join(f'g=grafo_insertar_arco(g,{a},{b},1);' for a,b in c['edges'])+'for(ListaVertice n=g.v;n;n=n->sig)audit_heap(n,3,7);for(ListaArco n=g.a;n;n=n->sig)audit_heap(n,4,7);'
  for run in range(c.get('repeat',1)):
   main+=f'audit_case={idx};audit_run={run};audit_depth=0;audit_frame_id=0;audit_alloc=0;audit_freed=0;audit_active=1;ListaVertice rec{run}=grafo_dfs(g,{c["start"]});audit_active=0;printf("RESULT {idx} {run} [");int first{run}=1;for(ListaVertice n=rec{run};n;n=n->sig){{printf("%s%d",first{run}?"":",",n->dato);first{run}=0;}}puts("]");while(rec{run}){{ListaVertice n=rec{run};rec{run}=n->sig;free(n);}}'
  main+='while(g.a){ListaArco n=g.a;g.a=n->sig;free(n);}while(g.v){ListaVertice n=g.v;g.v=n->sig;free(n);}}\n'
 main+='for(int i=0;i<audit_count;i++){if(audit_live[i]){return 93;}} return 0;}'
 (out/'observed.c').write_text(instrument(source)+main,encoding='utf-8')
 cmd=[shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),str(out/'tad_cola.c'),'-o',str(out/'observed.exe')];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0 and not p.stderr,p.stderr
 p=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=15);(out/'stdout.log').write_text(p.stdout,encoding='utf-8');assert p.returncode==0,(p.returncode,p.stderr)
 events=[json.loads(line[4:]) for line in p.stdout.splitlines() if line.startswith('OBS ')];outputs={(int(m[1]),int(m[2])):json.loads(m[3]) for m in re.finditer(r'^RESULT (\d+) (\d+) (.*)$',p.stdout,re.M)}
 report={'events':events,'outputs':[{ 'case':case,'run':run,'order':order} for (case,run),order in outputs.items()],'native_events':len(events),'native_runs':len(outputs),'source_hashes':hashes,'strict_c17':True,'live_after_caller_cleanup':0,'limits':['Normal allocation, finite max4vertex directed cases.','Pointer local IDs cached while live; historical cache never reads retired C pointers.','Heap fields read only after initialization bits, declarations remain in original scope.','Conditions evaluate original expression once; this observer adds no diagnostic branch re-evaluation.','No malloc failure injection, sanitizers or all-path claim.']}
 (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'events':len(events),'runs':len(outputs),'out':str(out)}),flush=True);return report
if __name__=='__main__':observe(os.environ['AUDIT_OUTPUT_DIR'])
