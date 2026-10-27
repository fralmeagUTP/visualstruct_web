from pathlib import Path
import sys,json,re,subprocess,shutil,urllib.request,faulthandler
faulthandler.enable();
r=Path(r'D:\MisProyectos\Web_VisualEstruct');sys.path[:0]=[str(r),str(r/'tests')]
from app import create_app
from test_audit_avl_rotation_repair import build_probe,run_probe,invariant
w=Path(__file__).parent;o=w/'avl-delete-baseline-low';o.mkdir(exist_ok=True)
for kind,ext in [('source','c'),('header','h')]:
 raw=create_app().test_client().get('/help/source/avl/'+kind).data;assert raw==(r/'docs/tads_C'/('tad_avl.'+ext)).read_bytes();(o/('tad_avl.'+ext)).write_bytes(raw)
source=(o/'tad_avl.c').read_text(encoding='utf-8-sig');clean=re.sub(r'/\*.*?\*/|//[^\n]*',lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),source,flags=re.S)
tok=re.compile(r'"(?:\\.|[^"\\])*"|[A-Za-z_]\w*|\d+|==|!=|<=|>=|->|&&|\|\||\+\+|--|\+=|-=|[^\s]');tokens=[(m.group(),clean.count('\n',0,m.start())+1,m.start(),m.end()) for m in tok.finditer(clean)]
HELPER=r'''
static AVL registry[256];static int live[256],count,depth=-1,serial,active,case_id;static AVL *root_ref;
static const char*names[]={"z","s","padre","child","L","R","A","B","C","tmp","feL","feR","altIzq","altDer"};
typedef struct{const char*fn;int id,ref,node,x,state[14],values[14];}Frame;static Frame frames[128];
static int ident(AVL p){if(!p)return 0;for(int i=0;i<count;i++)if(live[i]&&registry[i]==p)return i+1;return -1;}
static void *audit_malloc(size_t n){void*p=malloc(n);if(p){registry[count]=p;live[count++]=1;}return p;}
static void enter(const char*fn,int ref,AVL node,int x){depth++;frames[depth]=(Frame){.fn=fn,.id=++serial,.ref=ref,.node=ident(node),.x=x};}
static void local(const char*name,int value,int state){for(int i=0;i<14;i++)if(!strcmp(name,names[i])){frames[depth].state[i]=state;frames[depth].values[i]=value;}}
static void emit(int line,const char*phase,int result){if(!active)return;
 printf("AUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"root\":%d,\"frames\":[",case_id,line,phase,result,ident(*root_ref));
 for(int f=0;f<=depth;f++){Frame v=frames[f];printf("%s{\"id\":%d,\"function\":\"%s\",\"ref\":%d,\"node\":%d,\"x\":%d,\"locals\":{",f?",":"",v.id,v.fn,v.ref,v.node,v.x);int printed=0;for(int k=0;k<14;k++)if(v.state[k]){printf("%s\"%s\":",printed++?",":"",names[k]);if(v.state[k]==1)printf("\"sin inicializar\"");else printf("%d",v.values[k]);}printf("}}");}
 printf("],\"nodes\":[");int printed=0;for(int i=0;i<count;i++)if(live[i]){AVL n=registry[i];printf("%s{\"id\":%d,\"value\":%d,\"fe\":%d,\"left\":%d,\"right\":%d,\"parent\":%d}",printed++?",":"",i+1,n->nro,n->FE,ident(n->izq),ident(n->der),ident(n->padre));}printf("],\"freed_ids\":[");printed=0;for(int i=0;i<count;i++)if(!live[i])printf("%s%d",printed++?",":"",i+1);printf("]}\n");}
static int condition(int line,int result){emit(line,"condition",result);return result;}
static void audit_free(AVL p){int id=ident(p);if(id>0)live[id-1]=0;free(p);}
'''
POINTERS=['z','s','padre','child','L','R','A','B','C'];NUMERIC=['tmp','feL','feR','altIzq','altDer']
FUNCTIONS=['avl_eliminar','rebalancearTrasEliminar','avl_buscar','avl_minimo','avl_altura','avl_RSD','avl_RSI','avl_RDD','avl_RDI']
class Parser:
 def __init__(self,t,fn,ret):self.t=t;self.i=0;self.fn=fn;self.ret=ret;self.scopes=[]
 def take(self):v=self.t[self.i];self.i+=1;return v
 def expression(self):
  assert self.take()[0]=='(';d=1;p=[]
  while d:
   t=self.take()[0];d+=int(t=='(')-int(t==')')
   if d:p.append(t)
  return ' '.join(p)
 def condition_expr(self,expr,line):
  # Short-circuit operands are separately observable without evaluating the skipped operand.
  if ' && ' in expr: return ' && '.join(f'condition({line},!!({p}))' for p in expr.split(' && '))
  if ' || ' in expr:return ' || '.join(f'condition({line},!!({p}))' for p in expr.split(' || '))
  return f'condition({line},!!({expr}))'
 def statement(self):
  text,line,*_=self.take()
  if text=='{':
   self.scopes.append([]);out=[]
   while self.t[self.i][0]!='}':out.append(self.statement())
   closing=self.take();decls=self.scopes.pop();clear=''.join('local(\"'+n+'\",0,0);' for n in decls) if self.scopes else '';clear+=('emit('+str(closing[1])+',\"scope_exit\",-2);') if clear else '';return '{\n'+'\n'.join(out)+'\n'+clear+'}'
  if text in ['if','while']:
   expr=self.expression();out=text+'('+self.condition_expr(expr,line)+'){'+self.statement()+'}'
   if text=='if' and self.i<len(self.t) and self.t[self.i][0]=='else':self.take();out+='else{'+self.statement()+'}'
   return out
  parts=[text];d=0
  while parts[-1]!=';' or d:
   t=self.take()[0];parts.append(t);d+=int(t=='(')-int(t==')')
  if text in ['AVL','int'] and parts[1] in POINTERS+NUMERIC:self.scopes[-1].append(parts[1])
  st=' '.join(parts);expr=' '.join(parts[1:-1]);calls=any(re.search(r'\b'+fn+r'\s*\(',st) for fn in FUNCTIONS);prefix='';post=''
  st=st.replace('( z -> izq ) ?', '( condition('+str(line)+',!!(z -> izq)) ) ?')
  for guard in ['B -> FE < 0','A -> FE > 0','B -> FE > 0','A -> FE < 0','altIzq > altDer','z -> izq','L','R']:
   st=re.sub(r'(?<![\w])'+re.escape(guard)+r'\s*\?',f'condition({line},!!({guard})) ?',st)
  if text=='return':
   if self.ret=='void':return f'{{emit({line},"return",-2);depth--;return;}}'
   # Evaluate the canonical return expression once, then log without declaring a fake product local.
   if calls:prefix=f'emit({line},"call",-2);'
   expr=st[len('return '):-1].strip();kind='ident(audit_result)' if self.ret=='AVL' else 'audit_result'
   return '{'+prefix+self.ret+' audit_result='+expr+f';emit({line},"return",{kind});depth--;return audit_result;'+'}'
  for name in POINTERS+NUMERIC:
   if re.match(r'(?:AVL|int)\s+'+name+r'\s*=',st) and calls:prefix+=f'local("{name}",0,1);'
   if re.match(r'(?:(?:AVL|int)\s+)?'+name+r'\s*=',st):post+=f'local("{name}",'+('ident('+name+')' if name in POINTERS else name)+',2);'
  if self.fn in ['avl_minimo','rebalancearTrasEliminar'] and re.match(r'nodo\s*=',st):post+='frames[depth].node=ident(nodo);'
  if calls:prefix+=f'emit({line},"call",-2);'
  if st.startswith('free ('):prefix+=f'emit({line},"call",-2);';st=st.replace('free (','audit_free (');post+=f'emit({line},"free",frames[depth].values[0]);'
  return prefix+st+post+f'emit({line},"after",-2);'
functions=[]
pattern=r'\b(?:static\s+)?(void|AVL|int)\s+('+ '|'.join(FUNCTIONS)+r')\s*\(([^)]*)\)\s*\{'
for m in re.finditer(pattern,clean):
 fn=m.group(2);start=next(i for i,t in enumerate(tokens) if t[2]==m.end()-1);d=0
 for j in range(start,len(tokens)):
  d+=int(tokens[j][0]=='{')-int(tokens[j][0]=='}')
  if d==0:break
 p=Parser(tokens[start:j+1],fn,m.group(1));body=p.statement();assert p.i==len(p.t)
 args={'avl_eliminar':'raiz!=NULL,NULL,x','rebalancearTrasEliminar':'raiz!=NULL,nodo,0','avl_buscar':'0,raiz,x','avl_minimo':'0,nodo,0','avl_altura':'0,arbol,0'}.get(fn,'r!=NULL,nodo,0')
 entry=f'enter("{fn}",{args});emit({tokens[start][1]},"enter",-2);';exit=f'emit({tokens[j][1]},"return",-2);depth--;'
 body='{'+entry+body[1:-1]+(exit if m.group(1)=='void' else '')+'}';functions.append((m.start(),tokens[j][3],clean[m.start():m.end()-1]+body))
code=source
for a,z,body in reversed(functions):code=code[:a]+body+code[z:]
first=min(a for a,z,b in functions);code=code[:first]+'#include <string.h>\n'+HELPER+code[first:]
# Seed allocation is registered independently of instruction observation; no insertion suite repeated.
code=code.replace('malloc(sizeof(*nuevo))','audit_malloc(sizeof(*nuevo))')
PAIRS=[([],7),([10],99),([10],10),([10,5],10),([10,15],10),([10,5,15],5),([10,5,15],15),([20,10,30,35],20),([40,20,60,10,30,50,70,45,55],40),([4,2,5,1,3],5),([2,1,4,3,5],1),([5,2,6,4],6),([2,1,5,3],1),([50,30,70,20,40,60,80,10,25],40),([50,30,70,20,40,60,80,25],40),([0,-2147483648,2147483647],-2147483648),([0,-2147483648,2147483647],2147483647),([10,5,15],99)]
CASES=[{'seed':seed,'value':value} for seed,value in PAIRS]+[{'seed':[10,5,15],'value':10,'null_ref':True}]
main='\nint main(void){AVL root=NULL;'
for i,c in enumerate(CASES):
 main+='active=0;root=NULL;root_ref=&root;count=serial=0;depth=-1;'+''.join(f'avl_insertar(&root,{v});' for v in c['seed'])
 main+=f'case_id={i};active=1;emit(0,"initial",-2);avl_eliminar('+('NULL' if c.get('null_ref') else '&root')+f',{c["value"]});emit(0,"caller",-2);active=0;avl_liberarAVL(root);'
main+='return 0;}';(o/'instrumented.c').write_text(code+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(o/'instrumented.c'),'-o',str(o/'oracle.exe')],capture_output=True,text=True,timeout=30);(o/'compile.stderr').write_text(build.stderr,encoding='utf-8');assert build.returncode==0,build.stderr
run=subprocess.run([str(o/'oracle.exe')],capture_output=True,text=True,timeout=15);assert run.returncode==0,run.stderr;(o/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')];rows=[]
print('Native instrumentation compiled and executed',len(events),'events; compiling unchanged-C crosscheck',flush=True)
probe=build_probe(o/'canonical-crosscheck');tapes=[[('I',v) for v in c['seed']]+[('G' if c.get('null_ref') else 'D',c['value'])] for c in CASES];raw=run_probe(probe,tapes)
for i,c in enumerate(CASES):
 es=[e for e in events if e['case']==i];end=es[-1];canonical=[e for e in raw if e['case']==i][-1];errors,tree=invariant(canonical);assert not errors,(i,errors);assert end['root']==canonical['root'] and end['nodes']==canonical['nodes'] and end['freed_ids']==canonical['freed_ids'],i
 old={n['id']:n for n in es[0]['nodes']};victim=next((n['id'] for n in old.values() if n['value']==c['value']),None)
 if c.get('null_ref'):victim=None
 if victim and old[victim]['left'] and old[victim]['right']:
  victim=old[victim]['right']
  while old[victim]['left']:victim=old[victim]['left']
 assert end['freed_ids']==([victim] if victim else []);assert len(end['nodes'])==len(old)-int(victim is not None)
 data=None
 if data:assert data['visual_state']['root']==tree
 trace=data['execution_trace'] if data else None
 rows.append({'case':i,**c,'canonical_endpoint_equal':True,'independent_invariants':True,'expected_free_id':victim,'native_events':len(es),'rotations':[e['frames'][-1]['function'] for e in es if e['phase']=='enter' and e['frames'][-1]['function'].startswith('avl_R')],'api_success':data['success'] if data else None,'trace':trace,'trace_steps':len(trace['steps']) if trace else None,'trace_native_frames':sum(bool(s.get('pedagogy',{}).get('memory_state',{}).get('tree_frames')) for s in trace['steps']) if trace else None})
 print('Endpoint/invariant/backend verified case',i,flush=True)
assert {'avl_RSD','avl_RSI','avl_RDD','avl_RDI'}.issubset({fn for row in rows for fn in row['rotations']})
report={'cases':rows,'events':events,'native_events':len(events),'limits':['Baseline, not instructional UI pass certificate.','C subtraction operand order unspecified: compiler-selected legal pure height-call order recorded, not mandated.','All freed pointers retire from registry before free; freed local aliases retained as integer IDs only; freed storage never read.','NULL-ref test-only. API rejects missing targets independently of raw C void no-op.','Finite recorded paths, not malformed pointers/cycles/sanitizers or all paths.']};(o/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows),'native_events':len(events),'rows':[{k:v for k,v in x.items() if k!='trace'} for x in rows]}),flush=True)
