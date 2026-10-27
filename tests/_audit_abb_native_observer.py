"""Risk-based ABB native observer, instrumenting copies of real downloaded C.

No C algorithm replacement: a small statement parser wraps conditions/returns and
adds post-statement observations while retaining source coordinates. No installs.
"""
from pathlib import Path
import os,sys,re,json,subprocess,hashlib,collections
R=Path(os.environ.get('AUDIT_REPO',r'D:\MisProyectos\Web_VisualEstruct'));sys.path.insert(0,str(R))
from app import create_app
from app.services.c_code_service import CCodeService
from app.adapters.abb_adapter import ABBAdapter
D=Path(os.environ.get('AUDIT_OUTPUT_ROOT',str(Path(__file__).parent/'abb-native-low-output')));D.mkdir(parents=True,exist_ok=True)
app=create_app();client=app.test_client()
raw=client.get('/help/source/abb/source').data;header=client.get('/help/source/abb/header').data
assert raw==(R/'docs/tads_C/tad_abb.c').read_bytes();assert header==(R/'docs/tads_C/tad_abb.h').read_bytes()
(D/'tad_abb.c').write_bytes(raw);(D/'tad_abb.h').write_bytes(header)
data=CCodeService.get_structure_data('abb');source=raw.decode('utf-8-sig');source+='\n'+data['operations']['contar_hojas']+'\n'+data['operations']['validar']+'\n'
sources=source.splitlines();clean=re.sub(r'/\*.*?\*/|//[^\n]*',lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),source,flags=re.S)
token_pattern=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_]\w*|\d+|==|!=|<=|>=|->|&&|\|\||\+\+|--|\+=|-=|[^\s]')
tokens=[(m.group(),clean.count('\n',0,m.start())+1,m.start(),m.end()) for m in token_pattern.finditer(clean)]
helper=r'''
#include <stdarg.h>
#include <stdint.h>
static ABBNodo *audit_nodes[128];static int audit_live[128],audit_mask[128],audit_left[128],audit_right[128],audit_root_id,audit_count,audit_depth=-1,audit_case,audit_active;
static const char *audit_function[128];static int audit_alias[128][3],audit_arg[128],audit_low[128],audit_high[128];static int audit_local_state[128][2],audit_local_value[128][2];static int audit_operand_state[128][2],audit_operand_value[128][2];static char audit_console[8192];static int audit_console_size;
static int audit_id(const ABBNodo*p){if(!p)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_nodes[i]==p)return i+1;return -1;}
static void audit_register(ABBNodo*p){if(p){int i=audit_count++;audit_nodes[i]=p;audit_live[i]=1;audit_mask[i]=0;}}
static void audit_mark(ABBNodo*p,int mask){int id=audit_id(p);if(id>0){audit_mask[id-1]|=mask;if(mask&2)audit_left[id-1]=audit_id(p->izquierdo);if(mask&4)audit_right[id-1]=audit_id(p->derecho);}}
static void audit_enter(const char*fn,ABBNodo*nodo,int arg,int low,int high){audit_depth++;audit_operand_state[audit_depth][0]=audit_operand_state[audit_depth][1]=0;audit_local_state[audit_depth][0]=audit_local_state[audit_depth][1]=0;audit_function[audit_depth]=fn;audit_alias[audit_depth][0]=audit_id(nodo);audit_alias[audit_depth][1]=-2;audit_alias[audit_depth][2]=-2;audit_arg[audit_depth]=arg;audit_low[audit_depth]=low;audit_high[audit_depth]=high;}
static void audit_retire(int id){if(id>0){audit_live[id-1]=0;if(audit_root_id==id)audit_root_id=-100-id;for(int f=0;f<=audit_depth;f++)for(int k=0;k<3;k++)if(audit_alias[f][k]==id)audit_alias[f][k]=-100-id;}}
static int audit_printf(const char*fmt,...){va_list args;va_start(args,fmt);int n=vsnprintf(audit_console+audit_console_size,sizeof(audit_console)-(size_t)audit_console_size,fmt,args);va_end(args);audit_console_size+=n;return n;}
static void audit_emit(int line,const char*phase,int result){if(!audit_active)return;
 printf("AUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"root\":%d,\"frames\":[",audit_case,line,phase,result,audit_root_id);
 for(int f=0;f<=audit_depth;f++){if(f)printf(",");printf("{\"function\":\"%s\",\"nodo\":%d,\"nuevo\":%d,\"temp\":%d,\"arg\":%d,\"low\":%d,\"high\":%d,\"height_locals\":[[%d,%d],[%d,%d]],\"leaf_operands\":[[%d,%d],[%d,%d]]}",audit_function[f],audit_alias[f][0],audit_alias[f][1],audit_alias[f][2],audit_arg[f],audit_low[f],audit_high[f],audit_local_state[f][0],audit_local_state[f][0]==2?audit_local_value[f][0]:0,audit_local_state[f][1],audit_local_state[f][1]==2?audit_local_value[f][1]:0,audit_operand_state[f][0],audit_operand_state[f][0]==2?audit_operand_value[f][0]:0,audit_operand_state[f][1],audit_operand_state[f][1]==2?audit_operand_value[f][1]:0);}
 printf("],\"nodes\":[");int printed=0;
 for(int i=0;i<audit_count;i++)if(audit_live[i]){if(printed++)printf(",");ABBNodo*p=audit_nodes[i];printf("{\"id\":%d,\"mask\":%d,\"value\":%d,\"left\":%d,\"right\":%d}",i+1,audit_mask[i],audit_mask[i]&1?p->valor:0,audit_mask[i]&2?audit_left[i]:-2,audit_mask[i]&4?audit_right[i]:-2);}
 printf("],\"console_hex\":\"");for(int i=0;i<audit_console_size;i++)printf("%02x",(unsigned char)audit_console[i]);printf("\"}\n");
}
static int audit_condition(int line,int value){audit_emit(line,"condition",value);return value;}
/* Observer-only wrapper: each operand call remains indeterminately sequenced
   relative to the other; original pure C helper and sum are not reordered. */
int abb_contarHojas(ABBNodo* nodo);
static int audit_leaf_operand(ABBNodo*nodo,int line,int side){
 int parent=audit_depth;audit_operand_state[parent][side]=1;
 audit_emit(line,side==0?"call_left":"call_right",-2);
 int result=abb_contarHojas(nodo);
 audit_operand_state[parent][side]=2;audit_operand_value[parent][side]=result;
 audit_emit(line,side==0?"operand_left":"operand_right",result);return result;
}

'''
class Parser:
 def __init__(self,ts,fn,typ):self.t=ts;self.i=0;self.fn=fn;self.typ=typ
 def take(self):v=self.t[self.i];self.i+=1;return v
 def expression(self):
  assert self.take()[0]=='(';depth=1;parts=[]
  while depth:
   t=self.take()[0]
   if t=='(':depth+=1
   if t==')':depth-=1
   if depth:parts.append(t)
  return ' '.join(parts)
 def body(self):return '{'+self.statement()+'}'
 def statement(self):
  text,line,*_=self.take()
  if text=='{':
   out=[]
   while self.t[self.i][0]!='}':out.append(self.statement())
   self.take();return '{\n'+'\n'.join(out)+'\n}'
  if text in {'if','while'}:
   expr=self.expression();out=text+'(audit_condition('+str(line)+',('+expr+')))'+self.body()
   if text=='if' and self.i<len(self.t) and self.t[self.i][0]=='else':self.take();out+='else'+self.body()
   return out
  assert text!='for','Visible ABB functions have no for loops'
  parts=[text];depth=0
  while parts[-1]!=';' or depth:
   t=self.take()[0];parts.append(t)
   if t=='(':depth+=1
   elif t==')':depth-=1
  statement=' '.join(parts);expr=' '.join(parts[1:-1]);emit=f'audit_emit({line},"after",-2);'
  if text=='return':
   if not expr:return f'audit_emit({line},"return",-2);audit_depth--;return;'
   if self.fn=='abb_altura' and 'altIzq > altDer' in expr:expr=expr.replace('altIzq > altDer',f'audit_condition({line},altIzq > altDer)')
   if self.fn=='abb_contarHojas' and 'abb_contarHojas' in expr:
    expr=expr.replace('abb_contarHojas ( nodo -> izquierdo )',f'audit_leaf_operand(nodo->izquierdo,{line},0)').replace('abb_contarHojas ( nodo -> derecho )',f'audit_leaf_operand(nodo->derecho,{line},1)')
   native_result='audit_id(audit_result)' if '*' in self.typ else 'audit_result'
   prefix=f'audit_emit({line},"call",-2);' if self.fn=='abb_buscar' and re.search(r'\babb_buscar\s*\(',expr) else ''
   return '{'+prefix+self.typ+' audit_result='+expr+';'+f'audit_emit({line},"return",{native_result});audit_depth--;return audit_result;'+'}'
  if statement.startswith('free ('):
   return '{int audit_freed=audit_id(nodo);'+statement+'audit_retire(audit_freed);'+emit+'}'
  if self.fn=='abb_altura' and text=='int':
   name=parts[1];slot={'altIzq':0,'altDer':1}[name];initializer=' '.join(parts[3:-1])
   return f'int {name}=(audit_local_state[audit_depth][{slot}]=1,audit_emit({line},"call",-2),{initializer});audit_local_value[audit_depth][{slot}]={name};audit_local_state[audit_depth][{slot}]=2;'+emit
  out=[]
  if re.search(r'\babb_\w+\s*\(',statement):out.append(f'audit_emit({line},"call",-2);')
  out.append(statement)
  if 'malloc (' in statement:out.append('audit_register(nuevo);')
  for name,slot in [('nodo',0),('nuevo',1),('temp',2)]:
   if re.match(r'(?:ABBNodo\s*\*\s*)?'+name+r'\s*=',statement):out.append(f'audit_alias[audit_depth][{slot}]=audit_id({name});')
  for field,mask in [('valor',1),('izquierdo',2),('derecho',4)]:
   if re.match(r'nuevo\s*->\s*'+field+r'\s*=',statement):out.append(f'audit_mark(nuevo,{mask});')
   if re.match(r'nodo\s*->\s*'+field+r'\s*=',statement):out.append(f'audit_mark(nodo,{mask});')
  if 'nuevo -> izquierdo = nuevo -> derecho = NULL' in statement:out.append('audit_mark(nuevo,6);')
  out.append(emit);return ''.join(out)

functions=[]
for m in re.finditer(r'\b(ABBNodo\s*\*|void|int)\s*(abb_\w+)\s*\(([^)]*)\)\s*\{',clean):
 typ,fn,params=m.group(1,2,3)
 if fn in {'abb_mostrarArbol','abb_contarNiveles'}:continue # downloadable public-only functions, not visible operations
 start=next(i for i,t in enumerate(tokens) if t[2]==m.end()-1);depth=0;end=start
 for j in range(start,len(tokens)):
  if tokens[j][0]=='{':depth+=1
  if tokens[j][0]=='}':depth-=1
  if depth==0:end=j;break
 parser=Parser(tokens[start:end+1],fn,typ);body=parser.statement();assert parser.i==len(parser.t)
 arg='valor' if re.search(r'\bvalor\b',params) else '0';low='minimo' if fn=='abb_validar_rango' else '0';high='maximo' if fn=='abb_validar_rango' else '0'
 entry=f'audit_enter("{fn}",nodo,{arg},{low},{high});audit_emit({tokens[start][1]},"enter",-2);'
 body='{'+entry+body[1:-1]+(f'audit_emit({tokens[end][1]},"return",-2);audit_depth--;' if typ=='void' else '')+'}'
 functions.append((m.start(),tokens[end][3],clean[m.start():m.end()-1]+body))
instrumented=source
for a,z,body in reversed(functions):instrumented=instrumented[:a]+body+instrumented[z:]
first=min(a for a,z,b in functions);instrumented=instrumented[:first]+helper+'\n#define printf audit_printf\n'+instrumented[first:]
instrumented+='\n#undef printf\n'
cases=[]
def add(op,seed,values):
 for value in values:cases.append({'operation':op,'seed':seed,'payload':{} if value is None else {'value':value}})
add('insertar',[],[7]);add('insertar',[10,5,15],[3,7,18,5]);add('insertar',[10,5,3],[1])
add('buscar',[],[7]);add('buscar',[7],[7,3]);add('buscar',[10,5,15,3,7],[7,6])
add('eliminar',[],[7]);add('eliminar',[7],[7,9]);add('eliminar',[10,5,15],[5,15,10]);add('eliminar',[10,5,3],[5]);add('eliminar',[10,5,7],[5]);add('eliminar',[10,5,20,15,25,12,17,13],[10,20]);add('eliminar',[10,5,15],[99])
for op in ['minimo','maximo','altura','contar_hojas','inorden','preorden','postorden','validar','limpiar']:
 for seed in [[],[7],[10,5,15,3,7,12,18]]:add(op,seed,[None])
add('altura',[1,2,3,4],[None]);add('validar',[-2147483648],[None]);add('validar',[2147483647],[None])
if os.environ.get('AUDIT_ABB_CLEAR_SKEW_CASES')=='1':
 add('limpiar',[1,2,3,4],[None]);add('limpiar',[4,3,2,1],[None])
if os.environ.get('AUDIT_ABB_LEAF_SKEW_CASES')=='1':
 add('contar_hojas',[1,2,3,4],[None]);add('contar_hojas',[4,3,2,1],[None])
if os.environ.get('AUDIT_ABB_HEIGHT_LEFT_CASE')=='1':add('altura',[4,3,2,1],[None])
if os.environ.get('AUDIT_ABB_OPERATION'):cases=[c for c in cases if c['operation'] in os.environ['AUDIT_ABB_OPERATION'].split(',')]
opfn={'insertar':'abb_insertar','buscar':'abb_buscar','eliminar':'abb_eliminar','minimo':'abb_encontrarMinimo','maximo':'abb_encontrarMaximo','altura':'abb_altura','contar_hojas':'abb_contarHojas','inorden':'abb_inorden','preorden':'abb_preorden','postorden':'abb_postorden','validar':'abb_validar_rango','limpiar':'abb_liberarArbol'}
main=['int main(void){ABBNodo*root=NULL;']
for index,c in enumerate(cases):
 main+=['audit_active=0;root=NULL;audit_count=0;audit_depth=-1;audit_console_size=0;']
 main+=[f'root=abb_insertar(root,{value});' for value in c['seed']]
 main+=[f'audit_root_id=audit_id(root);audit_active=1;audit_case={index};']
 op=c['operation'];fn=opfn[op];params='root'+(','+str(c['payload']['value']) if c['payload'] else '')
 if op=='validar':params+=',(-2147483647-1),2147483647'
 if op in {'insertar','eliminar'}:main+=[f'root={fn}({params});', 'audit_root_id=audit_id(root);audit_emit(0,"caller",audit_root_id);']
 elif op=='limpiar':main+=[f'{fn}({params});audit_emit(0,"clear_caller_resume",-2);root=NULL;audit_root_id=0;audit_emit(0,"caller",0);']
 elif op in {'buscar','minimo','maximo'}:main+=[f'ABBNodo*result_{index}={fn}({params});audit_emit(0,"caller",audit_id(result_{index}));']
 elif op in {'altura','contar_hojas','validar'}:main+=[f'int result_{index}={fn}({params});audit_emit(0,"caller",result_{index});']
 else:main+=[f'{fn}({params});audit_emit(0,"caller",0);']
 main+=['audit_active=0;abb_liberarArbol(root);']
main+=['return 0;}'];(D/'instrumented.c').write_text(instrumented+'\n'+'\n'.join(main),encoding='utf-8')
build=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(D/'instrumented.c'),'-o',str(D/'oracle.exe')],capture_output=True,text=True,timeout=30);(D/'build.stderr.txt').write_text(build.stderr,encoding='utf-8');assert build.returncode==0,build.stderr
run=subprocess.run([str(D/'oracle.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr;(D/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(x[6:]) for x in run.stdout.splitlines() if x.startswith('AUDIT ')]
def tree(e,root=None):
 nodes={n['id']:n for n in e['nodes']};identity=e['root'] if root is None else root
 if identity<=0:return None
 n=nodes[identity];assert n['mask']==7
 return {'value':n['value'],'left':tree(e,n['left']),'right':tree(e,n['right'])}
reports=[];rows=[]
for i,c in enumerate(cases):
 client.post('/hierarchical/abb/reset')
 for value in c['seed']:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 actual=client.post('/hierarchical/abb/operate',json={'operation':c['operation'],'payload':c['payload']}).json
 ce=[e for e in events if e['case']==i];endpoint=ce[-1];assert endpoint['phase']=='caller';trace=actual['execution_trace'];lookup=collections.defaultdict(collections.deque)
 for s in trace['steps']:lookup[s['line_text'].strip()].append(s)
 for e in ce:
  if not e['line']:continue
  text=sources[e['line']-1].strip();step=lookup[text].popleft() if lookup[text] else None;issues=[]
  if step is None:issues.append('missing_instruction_occurrence')
  else:
   if e['phase'] in {'condition','call','return','enter'}:state=step['state_snapshot']
   else:state=step['state_after']
   if not state.get('heap_nodes'):issues.append('allocation_identity_and_recursive_aliases_not_represented')
   if e['phase']=='condition' and step.get('condition_result',(step.get('pedagogy',{}).get('condition') or {}).get('result'))!=bool(e['result']):issues.append('condition_result_requires_review')
   rows.append({'native':e,'source_line':text,'step':step,'issues':issues});continue
  rows.append({'native':e,'source_line':text,'step':step,'issues':issues})
 final_same=tree(endpoint)==actual['visual_state']['root'];result=None
 if actual['success'] and c['operation']=='buscar':result=(endpoint['result']>0)==actual.get('result')
 if actual['success'] and c['operation'] in {'altura','contar_hojas','validar'}:result=endpoint['result']==actual.get('result')
 if actual['success'] and c['operation'] in {'minimo','maximo'}:result=next(n['value'] for n in endpoint['nodes'] if n['id']==endpoint['result'])==actual.get('result')
 if actual['success'] and c['operation'] in {'inorden','preorden','postorden'}:result=[int(v) for v in bytes.fromhex(endpoint['console_hex']).decode().split()]==actual.get('result')
 reports.append({'case':i,**c,'api_success':actual['success'],'api_message':actual['message'],'native_events':len(ce),'final_tree_same':final_same,'result_same':result,'native_endpoint':endpoint,'caller_observations':[e for e in ce if not e['line']],'trace':trace})
report={'cases':reports,'rows':rows,'counts':dict(collections.Counter(z for r in rows for z in r['issues'])),'native_events':len(events),'visible_operations':[x['name'] for x in ABBAdapter().get_supported_operations()],'downloaded_sha256':hashlib.sha256(raw).hexdigest(),'header_sha256':hashlib.sha256(header).hexdigest(),'limits':['Baseline, not an instruction-fidelity pass certificate.','Contar hojas and validar use exact service-generated displayed C appended to downloaded source; these are absent from downloadable C/H.','No allocation failure injection. No sanitizer. No UI replay yet.','Registry observes only live initialized fields; freed aliases retained only as saved integer IDs.','Integer range validation uses displayed function with INT_MIN/INT_MAX bounds, so endpoint disagreement requires review.']}
(D/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'cases':len(cases),'native_events':len(events),'issues':report['counts'],'endpoint_disagreements':[x['case'] for x in reports if not x['final_tree_same'] or x['result_same'] is False]},ensure_ascii=True),flush=True)
