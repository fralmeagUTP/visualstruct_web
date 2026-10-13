"""LOW baseline: actual RBT insert field writes/calls/conditions, not UI signoff."""
from pathlib import Path
import os,re,json,hashlib,subprocess,shutil
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
CASES=[([],0),([],-2147483648),([],2147483647),([10],5),([10],15),([10],10),([30,20],10),([10,20],30),([30,10],20),([10,30],20),([10,5,15],1),([10,5,15],20),([20,10,30,5,15,25,35],1),([20,10,30,5,15,25,35],40),(list(range(1,8)),8),(list(range(7,0,-1)),0),(list(range(1,16)),16),(list(range(15,0,-1)),0),([0,-2147483648],2147483647),([0,-2147483648,2147483647],-2147483648)]
CASES=[{'seed':s,'value':v,'mode':'normal'} for s,v in CASES]+[{'seed':s,'value':v,'mode':m} for m in ['malloc_failure','NULL_reference'] for s,v in [([],7),([10,5,15],7)]]
FUNCTIONS=['rbt_abuelo','rbt_tio','rbt_rotar_dcha','rbt_rotar_izda',*[f'rbt_insercion_caso{i}' for i in range(1,6)],'rbt_insertar']
HELPER=r'''
#include <stdarg.h>
#include <string.h>
typedef struct {const char*name;int kind,value,initialized;}AuditVar;
typedef struct {AuditVar par[8],local[12];int np,nl;}AuditScope;
static AuditScope audit_scopes[128];static const char*audit_expression="";static char audit_output[8192];static int audit_output_len;
static void audit_var(int which,const char*name,int kind,int value,int initialized);

static RBT audit_nodes[128],*audit_root;static int audit_flags[128],audit_count,audit_depth=-1,audit_case,audit_active,audit_fail,audit_attempts,audit_serial;static const char*audit_functions[128];static int audit_invocations[128];
static int audit_id(RBT n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(RBT n){if(!n)return;int i=audit_count++;audit_nodes[i]=n;audit_flags[i]=31;audit_register(n->izq);audit_register(n->der);}
static void audit_enter(const char*fn){if(!audit_active)return;audit_depth++;audit_functions[audit_depth]=fn;audit_invocations[audit_depth]=++audit_serial;audit_scopes[audit_depth]=(AuditScope){0};}
static void audit_exit(void){if(audit_active)audit_depth--;}
static void audit_var(int which,const char*name,int kind,int value,int initialized){if(!audit_active)return;AuditScope*s=&audit_scopes[audit_depth];AuditVar*vars=which?s->local:s->par;int *count=which?&s->nl:&s->np;for(int i=0;i<*count;i++)if(!strcmp(vars[i].name,name)){vars[i]=(AuditVar){name,kind,value,initialized};return;}vars[(*count)++]=(AuditVar){name,kind,value,initialized};}
static void audit_variables(AuditVar*vars,int count){printf("{");for(int i=0;i<count;i++){AuditVar*v=&vars[i];printf("%s\"%s\":{\"kind\":%d,\"value\":%d,\"initialized\":%d}",i?",":"",v->name,v->kind,v->value,v->initialized);}printf("}");}
static void audit_emit(int line,const char*fn,const char*phase,int result){if(!audit_active)return;if(!strcmp(phase,"before")){audit_output_len=0;audit_output[0]=0;}
 printf("AUDIT {\"case\":%d,\"line\":%d,\"function\":\"%s\",\"phase\":\"%s\",\"result\":%d,\"root\":%d,\"allocation_attempts\":%d,\"frames\":[",audit_case,line,fn,phase,result,audit_id(*audit_root),audit_attempts);
 for(int d=0;d<=audit_depth;d++){printf("%s{\"function\":\"%s\",\"invocation\":%d,\"parameters\":",d?",":"",audit_functions[d],audit_invocations[d]);audit_variables(audit_scopes[d].par,audit_scopes[d].np);printf(",\"locals\":");audit_variables(audit_scopes[d].local,audit_scopes[d].nl);printf("}");}printf("],\"expression\":\"%s\",\"stdout_hex\":\"",audit_expression);for(int k=0;k<audit_output_len;k++)printf("%02x",(unsigned char)audit_output[k]);printf("\",\"heap\":[");audit_expression="";
 for(int i=0;i<audit_count;i++){RBT n=audit_nodes[i];int f=audit_flags[i];printf("%s{\"id\":%d,\"initialized\":%d,\"value\":",i?",":"",i+1,f);if(f&1)printf("%d",n->nro);else printf("null");printf(",\"left\":");if(f&2)printf("%d",audit_id(n->izq));else printf("null");printf(",\"right\":");if(f&4)printf("%d",audit_id(n->der));else printf("null");printf(",\"parent\":");if(f&8)printf("%d",audit_id(n->padre));else printf("null");printf(",\"color\":");if(f&16)printf("\"%s\"",n->rbt_color==ROJO?"RED":"BLACK");else printf("null");printf("}");}puts("]}");}
static int audit_condition(int line,const char*fn,const char*expression,int result){audit_expression=expression;audit_emit(line,fn,"condition",!!result);return result;}
static RBT audit_return_ptr(int line,const char*fn,RBT n){if(audit_active){audit_emit(line,fn,"return",audit_id(n));audit_exit();}return n;}
static RBT audit_allocate(size_t size){if(!audit_active)return malloc(size);audit_attempts++;if(audit_fail)return NULL;RBT p=malloc(size);if(p){int i=audit_count++;audit_nodes[i]=p;audit_flags[i]=0;}return p;}
static void audit_init(RBT n,int flags){if(audit_active)audit_flags[audit_id(n)-1]|=flags;}
static int audit_operand(int line,const char*fn,const char*expression,int result){audit_expression=expression;audit_emit(line,fn,"operand",!!result);return result;}
static int audit_printf(const char*fmt,...){va_list ap,cp;va_start(ap,fmt);va_copy(cp,ap);if(audit_active){int room=(int)sizeof audit_output-audit_output_len;int n=vsnprintf(audit_output+audit_output_len,(size_t)room,fmt,cp);if(n>0)audit_output_len+=n<room?n:room-1;}va_end(cp);int result=vprintf(fmt,ap);va_end(ap);return result;}
'''

CHECK=r'''
static int audit_valid(RBT n,RBT parent,long long lo,long long hi){if(!n)return 1;if(n->padre!=parent||n->nro<=lo||n->nro>=hi||(n->rbt_color!=ROJO&&n->rbt_color!=NEGRO))return -999;if(n->rbt_color==ROJO&&((n->izq&&n->izq->rbt_color==ROJO)||(n->der&&n->der->rbt_color==ROJO)))return -999;int l=audit_valid(n->izq,n,lo,n->nro),rr=audit_valid(n->der,n,n->nro,hi);if(l<0||rr!=l)return -999;return l+(n->rbt_color==NEGRO);}
static void audit_tree(RBT n){if(!n){printf("null");return;}printf("{\"value\":%d,\"color\":\"%s\",\"left\":",n->nro,n->rbt_color==ROJO?"RED":"BLACK");audit_tree(n->izq);printf(",\"right\":");audit_tree(n->der);printf("}");}
'''
def plain(s):
 # Preserve offsets/newlines while blanking comments and string literals for scope parsing.
 return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),s,flags=re.S)
def split_expression(expr):
 expr=expr.strip()
 while expr.startswith('('):
  depth=0;end=-1
  for i,c in enumerate(expr):
   depth+=int(c=='(')-int(c==')')
   if depth==0:end=i;break
  if end!=len(expr)-1:break
  expr=expr[1:-1].strip()
 for op in ['||','&&']:
  depth=0;parts=[];start=0;i=0
  while i<len(expr)-1:
   depth+=int(expr[i]=='(')-int(expr[i]==')')
   if depth==0 and expr[i:i+2]==op:parts.append(expr[start:i]);start=i+2;i+=2;continue
   i+=1
  if parts:return op,[*parts,expr[start:]]
 return None,[expr]
def cstring(expr):return json.dumps(' '.join(expr.split()))
def observed_expression(expr,line,compound=False):
 op,parts=split_expression(expr)
 if op:return '('+(' '+op+' ').join(observed_expression(x,line,True) for x in parts)+')'
 return f'audit_operand({line},__func__,{cstring(parts[0])},!!({parts[0]}))' if compound else parts[0]
def native_value(name):return name if name=='dato' else f'({name}?-2:0)' if name in ['arbol','r'] else f'audit_id({name})'
def record_local(name,initialized=True):return f'if(audit_active){{audit_var(1,"{name}",{0 if name=="dato" else 1},{native_value(name) if initialized else 0},{int(initialized)});}}'
def instrument(source):
 masked=plain(source);changes=[]
 for fn in FUNCTIONS:
  m=re.search(r'^(RBT|void)\s+'+fn+r'\([^;]*?\)\s*\{',masked,re.M);assert m,fn;start=m.end();depth=1;end=start
  while depth:
   if masked[end]=='{':depth+=1
   if masked[end]=='}':depth-=1
   end+=1
  body=source[start:end-1];bodymask=masked[start:end-1];updates=[]
  def line(pos):return source.count('\n',0,start+pos)+1
  # Evaluate each original full condition once; short-circuit operand events remain outside this LOW baseline.
  for c in re.finditer(r'\b(?:if|while)\s*\(',bodymask):
   a=c.end();z=a;d=1
   while d:
    if bodymask[z]=='(':d+=1
    if bodymask[z]==')':d-=1
    z+=1
   updates.append((a,z-1,f'audit_condition({line(c.start())},__func__,{cstring(body[a:z-1])},!!({observed_expression(body[a:z-1],line(c.start()))}))'))
  # Exact actual statements, preserving an unbraced controlled statement as one block.
  statements={
   'actual = malloc(sizeof(struct nodoRBT));':('allocate','actual = audit_allocate(sizeof(struct nodoRBT));'),
   'actual->nro = dato;':('initialize','actual->nro = dato; audit_init(actual,1);'),
   'actual->izq = actual->der = NULL;':('initialize','actual->izq = actual->der = NULL; audit_init(actual,6);'),
   'actual->padre = padre;':('initialize','actual->padre = padre; audit_init(actual,8);'),
   'actual->rbt_color = ROJO;':('initialize','actual->rbt_color = ROJO; audit_init(actual,16);'),
  }
  for stmt in ['padre = actual;','actual = actual->izq;','actual = actual->der;','*arbol = actual;','padre->izq = actual;','padre->der = actual;','padre->der = B;','padre->izq = B;','*r = B;','A->izq = C;','B->der = A;','A->der = C;','B->izq = A;','A->padre = B;','C->padre = A;','B->padre = padre;','n->padre->rbt_color = NEGRO;','a->rbt_color = ROJO;','t->rbt_color = NEGRO;','n->rbt_color = NEGRO;','a = rbt_abuelo(n);','nuevo_n = n->izq;','nuevo_n = n->der;']:
   statements[stmt]=('recolor' if 'rbt_color' in stmt else 'link' if ('->' in stmt or stmt.startswith('*')) and not stmt.startswith(('actual =','nuevo_n =','a =')) else 'local',stmt)
  for stmt,(phase,replacement) in statements.items():
   for match in re.finditer(re.escape(stmt),bodymask):
    if stmt=='a = rbt_abuelo(n);':continue
    if re.search(r'\bRBT\s+$',bodymask[:match.start()]):continue
    local=stmt.split(' =',1)[0] if stmt.split(' =',1)[0] in ['actual','padre','nuevo_n'] else None
    updates.append((match.start(),match.end(),'{ '+replacement+(record_local(local) if local else '')+f' audit_emit({line(match.start())},__func__,"{phase}",-2); '+'}'))
  for match in re.finditer(r'\brbt_(?:insercion_caso[1-5]|rotar_dcha|rotar_izda)\([^;]*\);',bodymask):
   text=body[match.start():match.end()];n=line(match.start());updates.append((match.start(),match.end(),f'{{ audit_emit({n},__func__,"call",-2); '+text+f' audit_emit({n},__func__,"resume",-2); }}'))
  for match in re.finditer(r'\breturn\s*([^;]*);',bodymask):
   expr=body[match.start(1):match.end(1)].strip();n=line(match.start());replacement=f'return audit_return_ptr({n},__func__,{expr});' if expr else f'{{ audit_emit({n},__func__,"return",-2); audit_exit(); return; }}';updates.append((match.start(),match.end(),replacement))
  printf='printf("\\tEl numero ha sido insertado\\n");';idx=body.find(printf)
  if idx>=0:updates.append((idx,idx+len(printf),printf.replace('printf(','audit_printf(')+f'audit_emit({line(idx)},__func__,"printf",-2);'))
  # Cache declaration scope before borrowed initializer call; never read uninitialized locals.
  for match in re.finditer(r'\bRBT\s+(padre|actual|A|B|C|a|t|nuevo_n)\s*=\s*([^;]+);',bodymask):
   name=match.group(1);expr=body[match.start(2):match.end(2)];number=line(match.start());text=body[match.start():match.end()]
   if 'rbt_abuelo(' in expr or 'rbt_tio(' in expr:
    updates.append((match.start(),match.end(),record_local(name,False)+f'audit_emit({number},__func__,"call",-2);'+text+record_local(name)+f'audit_emit({number},__func__,"local",-2);'))
   else:updates.append((match.end(),match.end(),record_local(name)+f'audit_emit({number},__func__,"local",-2);'))
  for match in re.finditer(r'\ba = rbt_abuelo\(n\);',bodymask):
   if re.search(r'\bRBT\s+$',bodymask[:match.start()]):continue
   number=line(match.start());text=body[match.start():match.end()];updates.append((match.start(),match.end(),f'audit_emit({number},__func__,"call",-2);'+text+record_local('a')+f'audit_emit({number},__func__,"local",-2);'))
  for match in re.finditer(r'\bRBT a;',bodymask):updates.append((match.end(),match.end(),record_local('a',False)+f'audit_emit({line(match.start())},__func__,"declaration",-2);'))
  last=-1
  for a,z,repl in sorted(updates):assert a>=last,(fn,a,last);last=z
  for a,z,repl in sorted(updates,reverse=True):body=body[:a]+repl+body[z:]
  pars=['arbol','dato'] if fn=='rbt_insertar' else ['r','nodoRBT'] if fn in ['rbt_rotar_dcha','rbt_rotar_izda'] else ['n','arbol'] if fn.startswith('rbt_insercion_') else ['n']
  entry='if(audit_active){audit_enter(__func__);'+''.join(f'audit_var(0,"{name}",{0 if name=="dato" else 2 if name in ["arbol","r"] else 1},{native_value(name)},1);' for name in pars)+f'audit_emit({source.count(chr(10),0,m.start())+1},__func__,"enter",-2);'+'}'
  tail=f'audit_emit({source.count(chr(10),0,end-1)+1},__func__,"return",-2);audit_exit();' if m.group(1)=='void' else ''
  changes.append((start,end-1,entry+body+tail))
 for a,z,text in sorted(changes,reverse=True):source=source[:a]+text+source[z:]
 anchor='typedef struct nodoRBT *RBT;';assert source.count(anchor)==1;return source.replace(anchor,anchor+'\n'+HELPER)
def observe(out):
 out=Path(out);out.mkdir();client=create_app().test_client();root=Path(__file__).resolve().parents[1];raw=client.get('/help/source/red_black/source').data;header=client.get('/help/source/red_black/header').data
 for ext,data in [('c',raw),('h',header)]:assert data==(root/'docs/tads_C'/('tad_rojo_negro.'+ext)).read_bytes();(out/('tad_rojo_negro.'+ext)).write_bytes(data)
 source=raw.decode('utf-8-sig').replace('\r\n','\n');instrumented=instrument(source);main='\n'+CHECK+'\nint main(void){RBT root=NULL;audit_root=&root;\n'
 for case,meta in enumerate(CASES):
  seed=meta['seed'];value=meta['value'];mode=meta['mode'];main+='audit_active=0;audit_fail=0;root=NULL;'+''.join(f'rbt_insertar(&root,{v});' for v in seed)
  main+=f'audit_count=0;audit_register(root);audit_attempts=0;audit_depth=-1;audit_serial=0;audit_case={case};audit_fail={int(mode=="malloc_failure")};printf("BEGIN {case}\\n");audit_active=1;audit_emit(0,"main","before",-2);rbt_insertar({"NULL" if mode=="NULL_reference" else "&root"},{value});audit_emit(0,"main","after",-2);audit_active=0;'
  main+=f'if((root&&root->rbt_color!=NEGRO)||audit_valid(root,NULL,-2147483649LL,2147483648LL)<0||audit_depth!=-1)return 80;printf("END {case}\\nROOT {case} ");audit_tree(root);printf("\\n");rbt_liberar(root);root=NULL;\n'
 main+='return 0;}';(out/'instrumented.c').write_text(instrumented+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror'];build=subprocess.run([gcc,*flags,str(out/'instrumented.c'),'-o',str(out/'instrumented.exe')],capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(build.stderr);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(out/'instrumented.exe')],capture_output=True,text=True,timeout=10);(out/'stdout.log').write_text(run.stdout,encoding='utf-8');assert run.returncode==0,(run.returncode,run.stdout[-1000:],run.stderr)
 events=[json.loads(line[6:]) for line in run.stdout.splitlines() if line.startswith('AUDIT ')];trees={int(m.group(1)):json.loads(m.group(2)) for m in re.finditer(r'^ROOT (\d+) (.*)$',run.stdout,re.M)};results=[]
 for case,meta in enumerate(CASES):
  ev=[e for e in events if e['case']==case];chunk=run.stdout.split(f'BEGIN {case}\n',1)[1].split(f'END {case}\n',1)[0];stdout=''.join(line+'\n' for line in chunk.splitlines() if not line.startswith('AUDIT '));duplicate=meta['value'] in meta['seed'];inserted=meta['mode']=='normal' and not duplicate
  assert stdout==('\tEl numero ha sido insertado\n' if inserted else ''),(case,stdout)
  history=[{'operation':'insertar','payload':{'value':v}} for v in meta['seed']];data=S.execute_operation('red_black','insertar',{'value':meta['value']},history)
  if meta['mode']=='normal':assert data['success']==inserted and data['visual_state']['root']==trees[case],(case,data['visual_state'],trees[case])
  funcs=sorted({e['function'] for e in ev});trace=data.get('execution_trace') or {};steps=trace.get('steps') or []
  results.append({**meta,'case':case,'inserted':inserted,'native_events':len(ev),'native_functions':funcs,'native_root':trees[case],'operation_stdout':stdout,'allocation_attempts':ev[-1]['allocation_attempts'],'backend_contract_success':data['success'],'backend_endpoint_checked':meta['mode']=='normal','trace_steps':len(steps),'shown_function_definitions':re.findall(r'^(?:void|RBT)\s+(rbt_\w+)\s*\([^;]*\)\s*\{',trace.get('source_code',''),re.M),'trace_first_frame':steps[0].get('pedagogy',{}).get('call_stack',[]) if steps else [],'trace':trace})
 report={'cases':results,'events':events,'native_events':len(events),'function_counts':{f:sum(e['function']==f and e['phase']=='enter' for e in events) for f in FUNCTIONS},'native_fixture_invariants_verified':True,'native_documented_modes':['normal','duplicate','NULL_reference','malloc_failure'],'downloaded_sha256':hashlib.sha256(raw).hexdigest(),'header_sha256':hashlib.sha256(header).hexdigest(),'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'limits':['LOW observation baseline, not per-instruction UI signoff.','Native parameters/locals/borrowed returns and initialized-field masks recorded independently.','C itself selects each recorded short-circuit operand; instrumentation does not evaluate omitted operands.','Heap reads only initialized fields; completed chained initialization is one recorded event.','No native free during insertion; cleanup outside observed operation.','Malloc failure and NULL reference are raw C contracts, not exposed UI operations.','Independent final checker covers black-height and parents beyond the current limited Validar query.']}
 (out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'cases':len(results),'events':len(events),'functions':report['function_counts'],'path':str(out)}),flush=True);return report
if __name__=='__main__':observe(os.environ['AUDIT_OUTPUT_DIR'])
