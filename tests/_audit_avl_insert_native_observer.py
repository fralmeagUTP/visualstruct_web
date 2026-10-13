from pathlib import Path
import sys,json,re,subprocess,shutil,urllib.request,collections
r=Path(r'D:\MisProyectos\Web_VisualEstruct');sys.path.insert(0,str(r));from app import create_app
w=Path(__file__).parent;o=w/'avl-insert-baseline-low';o.mkdir(exist_ok=True)
for kind,suffix in [('source','c'),('header','h')]:
 raw=create_app().test_client().get('/help/source/avl/'+kind).data;assert raw==(r/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(o/('tad_avl.'+suffix)).write_bytes(raw)
source=(o/'tad_avl.c').read_text(encoding='utf-8-sig');lines=source.splitlines();clean=re.sub(r'/\*.*?\*/|//[^\n]*',lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),source,flags=re.S)
token_pattern=re.compile(r'"(?:\\.|[^"\\])*"|[A-Za-z_]\w*|\d+|==|!=|<=|>=|->|&&|\|\||\+\+|--|\+=|-=|[^\s]');tokens=[(m.group(),clean.count('\n',0,m.start())+1,m.start(),m.end()) for m in token_pattern.finditer(clean)]
HELPER=r'''
static AVL nodes[256];static int masks[256],count,depth=-1,serial,active,case_id,fail_malloc;static AVL *root_ref;
static const char*names[]={"padre","actual","nuevo","n","A","B","C"};
typedef struct {const char*fn;int id,ref,node,x,states[7],aliases[7];} Frame;static Frame frames[64];
static int ident(AVL p){if(!p)return 0;for(int i=0;i<count;i++)if(nodes[i]==p)return i+1;return -1;}
static void *audit_malloc(size_t size){if(fail_malloc){fail_malloc=0;return NULL;}void*p=malloc(size);if(p){nodes[count]=p;masks[count++]=0;}return p;}
static void mark(AVL p,int mask){int i=ident(p);if(i>0)masks[i-1]|=mask;}
static void enter(const char*fn,int ref,AVL node,int x){depth++;frames[depth]=(Frame){.fn=fn,.id=++serial,.ref=ref,.node=ident(node),.x=x};}
static void alias(const char*name,AVL p){for(int k=0;k<7;k++)if(!strcmp(names[k],name)){frames[depth].states[k]=2;frames[depth].aliases[k]=ident(p);}}
static void uninit(const char*name){for(int k=0;k<7;k++)if(!strcmp(names[k],name))frames[depth].states[k]=1;}
static void emit(int line,const char*phase,int result){if(!active)return;
 printf("AUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"root\":%d,\"frames\":[",case_id,line,phase,result,ident(*root_ref));
 for(int f=0;f<=depth;f++){Frame v=frames[f];printf("%s{\"id\":%d,\"function\":\"%s\",\"ref\":%d,\"node\":%d,\"x\":%d,\"locals\":{",f?",":"",v.id,v.fn,v.ref,v.node,v.x);int printed=0;for(int k=0;k<7;k++)if(v.states[k]){printf("%s\"%s\":",printed++?",":"",names[k]);if(v.states[k]==1)printf("\"sin inicializar\"");else printf("%d",v.aliases[k]);}printf("}}");}
 printf("],\"nodes\":[");for(int i=0;i<count;i++){AVL n=nodes[i];int m=masks[i];printf("%s{\"id\":%d,\"mask\":%d,\"value\":%d,\"fe\":%d,\"left\":%d,\"right\":%d,\"parent\":%d}",i?",":"",i+1,m,m&1?n->nro:0,m&2?n->FE:0,m&4?ident(n->izq):-2,m&8?ident(n->der):-2,m&16?ident(n->padre):-2);}printf("]}\n");}
static int condition(int line,int result){emit(line,"condition",result);return result;}
'''
class Parser:
 def __init__(self,ts,fn):self.t=ts;self.i=0;self.fn=fn
 def take(self):v=self.t[self.i];self.i+=1;return v
 def expression(self):
  assert self.take()[0]=='(';d=1;p=[]
  while d:
   t=self.take()[0];d+=int(t=='(')-int(t==')')
   if d:p.append(t)
  return ' '.join(p)
 def statement(self):
  text,line,*_=self.take()
  if text=='{':
   out=[]
   while self.t[self.i][0]!='}':out.append(self.statement())
   self.take();return '{\n'+'\n'.join(out)+'\n}'
  if text in ['if','while']:
   expr=self.expression();out=text+f'(condition({line},!!({expr})))'+'{'+self.statement()+'}'
   if text=='if' and self.i<len(self.t) and self.t[self.i][0]=='else':self.take();out+='else{'+self.statement()+'}'
   return out
  parts=[text];d=0
  while parts[-1]!=';' or d:
   t=self.take()[0];parts.append(t);d+=int(t=='(')-int(t==')')
  st=' '.join(parts)
  if text=='return':return f'{{emit({line},"return",-2);depth--;return;}}'
  if text=='break':return f'{{emit({line},"break",-2);break;}}'
  prefix='';post=''
  for expr in ['B -> FE < 0','A -> FE > 0','B -> FE > 0','A -> FE < 0']:
   if expr in st:st=st.replace(expr,f'condition({line},({expr}))')
  if 'malloc (' in st:prefix=f'uninit("nuevo");emit({line},"call",-2);';st=st.replace('malloc (','audit_malloc (')
  if re.match(r'avl_R(?:SD|SI|DD|DI)\s*\(',st):prefix+=f'emit({line},"call",-2);'
  if st.startswith('AVL padre = NULL , actual = * raiz'):post+='alias("padre",padre);alias("actual",actual);'
  for name in ['padre','actual','nuevo','n','A','B','C']:
   if re.match(r'(?:AVL\s+)?'+name+r'\s*=',st):post+=f'alias("{name}",{name});'
  for field,mask in [('nro',1),('FE',2),('izq',4),('der',8),('padre',16)]:
   if re.match(r'\w+\s*->\s*'+field+r'\s*=',st):post+=f'mark({parts[0]},{mask});'
  if 'nuevo -> izq = nuevo -> der = NULL' in st:post+='mark(nuevo,12);'
  return prefix+st+post+f'emit({line},"after",-2);'
functions=[]
for m in re.finditer(r'\bvoid\s+(avl_insertar|avl_RSD|avl_RSI|avl_RDD|avl_RDI)\s*\(([^)]*)\)\s*\{',clean):
 fn=m.group(1);start=next(i for i,t in enumerate(tokens) if t[2]==m.end()-1);d=0
 for j in range(start,len(tokens)):
  d+=int(tokens[j][0]=='{')-int(tokens[j][0]=='}')
  if d==0:break
 p=Parser(tokens[start:j+1],fn);body=p.statement();assert p.i==len(p.t)
 args='raiz!=NULL,NULL,x' if fn=='avl_insertar' else 'r!=NULL,nodo,0';entry=f'enter("{fn}",{args});emit({tokens[start][1]},"enter",-2);'
 body='{'+entry+body[1:-1]+f'emit({tokens[j][1]},"return",-2);depth--;'+ '}';functions.append((m.start(),tokens[j][3],clean[m.start():m.end()-1]+body))
code=source
for a,z,body in reversed(functions):code=code[:a]+body+code[z:]
first=min(a for a,z,b in functions);code=code[:first]+'#include <string.h>\n'+HELPER+code[first:]
CASES=[{'seed':s,'value':v} for s,v in [([],7),([10],5),([10,5,15],7),([30,20],10),([10,20],30),([30,10],20),([10,30],20),([50,30,70,20,40,60,80,35],37),([1,2,3,4,6,0,8,7],5),([10,5,15],5),([0],-2147483648),([0,-2147483648],2147483647)]]
CASES+=[{'seed':[],'value':7,'fail_malloc':True},{'seed':[10,5],'value':7,'fail_malloc':True},{'seed':[10],'value':7,'null_ref':True}]
main='\nint main(void){AVL root=NULL;'
for i,c in enumerate(CASES):
 main+='active=0;root=NULL;root_ref=&root;count=serial=fail_malloc=0;depth=-1;'+''.join(f'avl_insertar(&root,{v});' for v in c['seed'])
 main+=f'case_id={i};active=1;emit(0,"initial",-2);fail_malloc={int(c.get("fail_malloc",False))};avl_insertar('+('NULL' if c.get('null_ref') else '&root')+f',{c["value"]});emit(0,"caller",-2);active=0;avl_liberarAVL(root);'
main+='return 0;}'
(o/'instrumented.c').write_text(code+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(o/'instrumented.c'),'-o',str(o/'oracle.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
run=subprocess.run([str(o/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;(o/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')];client=create_app().test_client();rows=[]
for i,c in enumerate(CASES):
 if c.get('fail_malloc') or c.get('null_ref'):rows.append({'case':i,**c,'native_only':True});continue
 client.post('/hierarchical/avl/operate',json={'operation':'limpiar','payload':{}})
 for v in c['seed']:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 data=client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':c['value']}}).json;trace=data['execution_trace'];es=[e for e in events if e['case']==i];rows.append({'case':i,**c,'api_success':data['success'],'trace':trace,'native_events':len(es),'rotations':[e['frames'][-1]['function'] for e in es if e['phase']=='enter' and e['frames'][-1]['function']!='avl_insertar'],'trace_steps':len(trace['steps']),'steps_with_native_frames':sum(bool(s.get('pedagogy',{}).get('memory_state',{}).get('tree_frames')) for s in trace['steps'])})
report={'cases':rows,'events':events,'limits':['Baseline only, not instruction/UI pass certificate.','Test-only malloc-failure and NULL-root-reference cases are not API features.','Only initialized fields read, masks retain malloc indeterminate-state distinctions.','C returns void on duplicate; API may reject without executing C.','Existing closed native-prefix invariants reused, not repeated as a fullsuite.']};(o/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'cases':len(CASES),'native_events':len(events),'rows':[{k:v for k,v in x.items() if k!='trace'} for x in rows]}),flush=True)
