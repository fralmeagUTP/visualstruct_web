from pathlib import Path
import os,sys,re,json,subprocess,collections,hashlib
W=Path(os.environ.get('AUDIT_OUTPUT_ROOT',str(Path(__file__).parent)));R=Path(os.environ.get('AUDIT_REPO',r'D:\MisProyectos\Web_VisualEstruct'));D=W/'audit-evidence/native-sublist-visible';D.mkdir(parents=True,exist_ok=True)
os.environ['SESSION_CACHE_DIR']=str(W/'sublist-native-session');sys.path.insert(0,str(R));from app import create_app
client=create_app().test_client();raw=client.get('/help/source/sublist/source').data;source=raw.decode('utf-8-sig').replace('\r\n','\n');assert 'sublista_insertar_padre_final' in source
(D/'downloaded.c').write_bytes(raw);(D/'tad_sublista.h').write_bytes(client.get('/help/source/sublist/header').data)
functions={'insertar_padre':'sublista_insertar_padre_final','insertar_hijo':'sublista_insertar_hijo','eliminar_padre':'sublista_eliminar_padre_primero','eliminar_hijo':'sublista_eliminar_hijo','hijos_de':'sublista_obtener_hijos','limpiar':'sublista_destruir'}
seed=[(7,[3,3,5]),(8,[]),(9,[6,7])];cases=[]
for op,args in [('insertar_padre',[{'parent':7}]),('insertar_hijo',[{'parent':7,'child':3},{'parent':8,'child':4},{'parent':99,'child':4}]),('eliminar_padre',[{'parent':7},{'parent':8},{'parent':9},{'parent':99}]),('eliminar_hijo',[{'parent':7,'child':3},{'parent':7,'child':5},{'parent':7,'child':99},{'parent':8,'child':3},{'parent':99,'child':3}]),('hijos_de',[{'parent':7},{'parent':8},{'parent':99}]),('limpiar',[{}])]:
 for payload in args:cases.append({'operation':op,'seed':seed,'payload':payload})
for op in functions:cases.append({'operation':op,'seed':[],'payload':{'parent':7,'child':3} if op!='limpiar' else {}})
cases.append({'operation':'eliminar_padre','seed':[(7,[3]),(7,[4])],'payload':{'parent':7}})
helper=r'''
#include <stdint.h>
static Nodo **audit_root;
static void *audit_nodes[128];static int audit_type[128],audit_mask[128],audit_live[128],audit_count,audit_active,audit_case,audit_depth=-1,audit_freed,audit_return_bool=-2,audit_return_pointer=-2;
static int audit_alias[32][6],audit_owner[32];static const char *audit_fn[32];static int audit_used[32],audit_capacity[32],audit_written[1024];static int *audit_output;
static int audit_id(const void *p){if(!p)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_nodes[i]==p)return i+1;return -1;}
static void audit_register(void *p,int type){if(!p)return;int i=audit_count++;audit_nodes[i]=p;audit_type[i]=type;audit_mask[i]=0;audit_live[i]=1;}
static void audit_mark(void *p,int bit){int id=audit_id(p);if(id>0)audit_mask[id-1]|=bit;}
static void audit_enter(const char *fn){audit_depth++;audit_fn[audit_depth]=fn;audit_used[audit_depth]=-2;audit_capacity[audit_depth]=-2;audit_owner[audit_depth]=0;for(int i=0;i<6;i++)audit_alias[audit_depth][i]=-2;}
static void audit_leave(void){audit_depth--;}
static void audit_retire(int id){if(id<1)return;audit_live[id-1]=0;audit_freed=id;for(int f=0;f<=audit_depth;f++)for(int i=0;i<6;i++)if(audit_alias[f][i]==id)audit_alias[f][i]=-100-id;}
static void audit_emit(const char *fn,int offset,const char *line,int condition){
 if(!audit_active)return;
 printf("AUDIT {\"case\":%d,\"function\":\"%s\",\"offset\":%d,\"line\":\"%s\",\"condition\":%d,\"root\":%d,\"freed\":%d,\"depth\":%d,\"owner\":%d,\"child_root\":%d,\"return_value\":%d,\"return_pointer\":%d,\"aliases\":[",audit_case,fn,offset,line,condition,audit_id(*audit_root),audit_freed,audit_depth,audit_owner[audit_depth],audit_owner[audit_depth]>0?audit_id(((Nodo*)audit_nodes[audit_owner[audit_depth]-1])->sub):0,audit_return_bool,audit_return_pointer);
 for(int i=0;i<6;i++){if(i)printf(",");printf("%d",audit_alias[audit_depth][i]);}
 printf("],\"frames\":[");
 for(int f=0;f<=audit_depth;f++){if(f)printf(",");printf("{\"function\":\"%s\",\"owner\":%d,\"usados\":%d,\"capacidad\":%d,\"aliases\":[",audit_fn[f],audit_owner[f],audit_used[f],audit_capacity[f]);for(int i=0;i<6;i++){if(i)printf(",");printf("%d",audit_alias[f][i]);}printf("]}");}
 printf("],\"writes\":[");int writing=0;for(int i=0;i<1024;i++)if(audit_written[i]){if(writing++)printf(",");printf("{\"index\":%d,\"value\":%d}",i,audit_output[i]);}
 printf("],\"nodes\":[");int printed=0;
 for(int i=0;i<audit_count;i++)if(audit_live[i]){if(printed++)printf(",");int value=0,next=-2,sub=-2;
  if(audit_type[i]==1){Nodo*p=audit_nodes[i];if(audit_mask[i]&1)value=p->nro;if(audit_mask[i]&2)next=audit_id(p->sgte);if(audit_mask[i]&4)sub=audit_id(p->sub);}
  else{Sublista*p=audit_nodes[i];if(audit_mask[i]&1)value=p->nro;if(audit_mask[i]&2)next=audit_id(p->sgte);}
  printf("{\"id\":%d,\"type\":%d,\"mask\":%d,\"value\":%d,\"next\":%d,\"sub\":%d}",i+1,audit_type[i],audit_mask[i],value,next,sub);
 }printf("]}\n");
}
'''
# Only functions serving the six visible operations and their allocation/free/copy dependencies.
names=list(functions.values())+['crear_padre','crear_hijo','destruir_hijos','sublista_buscar_padre','sublista_insertar_hijo_final','sublista_eliminar_hijo_primero','sublista_copiar_hijos']
modified=source;slots={'nuevo':0,'actual':1,'anterior':2,'next':3,'padre':4,'hijo':5}
for fn in names:
 match=re.search(r'^(?:static )?(?:Nodo \*|Sublista \*|bool |void |int )'+fn+r'\(',modified,re.M);assert match,fn
 a=match.start();z=modified.index('\n}',a)+2;out=[]
 for offset,line in enumerate(modified[a:z].splitlines()):
  t=line.strip();emit='audit_emit('+json.dumps(fn)+','+str(offset)+','+json.dumps(t)
  if offset==0:
   out.extend([line,'audit_enter('+json.dumps(fn)+');']);
   if re.search(r'\((?:const )?Nodo \*padre[,)]',t):out.append('audit_alias[audit_depth][4]=audit_id(padre);')
   if fn in {'sublista_obtener_hijos','sublista_copiar_hijos'}:out.append('audit_capacity[audit_depth]=capacidad;')
   if fn=='destruir_hijos':out.append('for(int i=0;i<audit_count;i++)if(audit_live[i]&&audit_type[i]==1&&lista_hijos==&((Nodo*)audit_nodes[i])->sub)audit_owner[audit_depth]=i+1;')
   continue
  if t.startswith(('if (','while (')):
   m=re.match(r'(\s*(?:if|while)\s*\()(.*)(\)\s*\{)$',line);assert m,line
   out.append(m[1]+'('+emit+',('+m[2]+')),('+m[2]+'))'+m[3]);continue
  if t.startswith('return'):
   if fn in {'crear_padre','crear_hijo','sublista_insertar_padre_final'}:
    typ='Sublista *' if fn=='crear_hijo' else 'Nodo *'
    out.append('{'+typ+'audit_result='+t[7:-1]+';audit_return_pointer=audit_id(audit_result);'+emit+',-1);audit_leave();return audit_result;}')
    continue
   if fn=='sublista_insertar_hijo_final' or (fn=='sublista_insertar_hijo' and t=='return false;'):
    out.append('{bool audit_result='+t[7:-1]+';audit_return_bool=audit_result;'+emit+',-1);audit_leave();return audit_result;}')
    continue
   if fn in {'sublista_eliminar_padre_primero','sublista_copiar_hijos'}:
    typ='bool ' if fn=='sublista_eliminar_padre_primero' else 'int '
    out.append('{'+typ+'audit_result='+t[7:-1]+';audit_return_bool=audit_result;'+emit+',-1);audit_leave();return audit_result;}')
    continue
   if fn=='sublista_obtener_hijos':
    if t.startswith('return sublista_copiar_hijos('):out.append(emit+',-1);')
    out.append('{int audit_result='+t[7:-1]+';audit_return_bool=audit_result;'+emit+(',-4);' if t.startswith('return sublista_copiar_hijos(') else ',-1);')+'audit_leave();return audit_result;}')
    continue
   out.append(emit+',-1);')
   if t=='return;':out+=['audit_leave();',line]
   else:
    typ='Nodo *' if fn in ['crear_padre','sublista_insertar_padre_final','sublista_buscar_padre'] else 'Sublista *' if fn=='crear_hijo' else 'bool ' if fn.startswith(('sublista_insertar_hijo','sublista_eliminar')) else 'int '
    out+=['{'+typ+'audit_result='+t[7:-1]+';'+('audit_return_bool=audit_result;'+emit+',-4);' if fn in {'sublista_eliminar_hijo','sublista_insertar_hijo'} and t.startswith(('return sublista_eliminar_hijo_primero(','return sublista_insertar_hijo_final(')) else '')+'audit_leave();return audit_result;}']
   continue
  if offset==len(modified[a:z].splitlines())-1:
   if fn in {'destruir_hijos','sublista_destruir'}:out.append(emit+',-6);')
   out+=['audit_leave();',line];continue
  if t=='free(actual);':out+=['{int audit_free_id=audit_id(actual);',line,'audit_retire(audit_free_id);}',emit+',-1);'];continue
  if (fn in {'sublista_eliminar_hijo','sublista_obtener_hijos','sublista_insertar_hijo'} and t.startswith('Nodo *padre = sublista_buscar_padre(')) or (fn in {'sublista_eliminar_padre_primero','sublista_destruir'} and t=='destruir_hijos(&actual->sub);'):out.append(emit+',-3);')
  if t in {'nuevo = crear_padre(valor_padre);','nuevo = crear_hijo(valor_hijo);'}:out.append(emit+',-3);')
  out.append(line)
  if t in {'int usados = 0;','usados++;'}:out.append('audit_used[audit_depth]=usados;')
  if t=='destino[usados] = actual->nro;':out.append('audit_written[usados]=1;')
  if 'malloc(sizeof(' in t:out.append('audit_register(nuevo,'+('1' if fn=='crear_padre' else '2')+');')
  for name,slot in slots.items():
   if re.match(r'(?:(?:const )?(?:Nodo|Sublista)\s*\*\s*)?'+name+r'\s*=',t):out.append('audit_alias[audit_depth]['+str(slot)+']=audit_id('+name+');')
  for field,bit in [('nro',1),('sgte',2),('sub',4)]:
   if t.startswith('nuevo->'+field+' ='):out.append('audit_mark(nuevo,'+str(bit)+');')
  if t.endswith(';') and ('malloc(sizeof(' in t or not re.match(r'(?:Nodo|Sublista|const|int)\s',t) or (fn in {'sublista_eliminar_hijo','sublista_obtener_hijos','sublista_insertar_hijo'} and t.startswith('Nodo *padre = sublista_buscar_padre('))):out.append(emit+',-1);')
 modified=modified[:a]+'\n'.join(out)+modified[z:]
modified=modified.replace('static Nodo *crear_padre(',helper+'\nstatic Nodo *crear_padre(',1)
main=['int main(void){']
for index,c in enumerate(cases):
 main+=['{Nodo*lista=NULL;audit_root=&lista;audit_count=0;audit_active=0;']
 for parent,children in c['seed']:
  main+=['{Nodo*seed_parent=sublista_insertar_padre_final(&lista,'+str(parent)+');(void)seed_parent;']+[f'sublista_insertar_hijo(lista,{parent},{v});' for v in children]+['}']
 args={'insertar_padre':'&lista,'+str(c['payload']['parent']) if c['operation']=='insertar_padre' else '', 'insertar_hijo':'lista,'+str(c['payload'].get('parent',0))+','+str(c['payload'].get('child',0)), 'eliminar_padre':'&lista,'+str(c['payload'].get('parent',0)), 'eliminar_hijo':'lista,'+str(c['payload'].get('parent',0))+','+str(c['payload'].get('child',0)), 'hijos_de':'lista,'+str(c['payload'].get('parent',0))+',output,1024','limpiar':'&lista'}[c['operation']]
 main+=['int output[1024]={0};audit_output=output;for(int i=0;i<1024;i++)audit_written[i]=0;audit_freed=0;audit_return_bool=-2;audit_return_pointer=-2;',f'audit_case={index};audit_active=1;'+functions[c['operation']]+'('+args+');','audit_active=0;sublista_destruir(&lista);}']
main+=['return 0;}'];(D/'instrumented.c').write_text(modified+'\n'+'\n'.join(main),encoding='utf-8')
p=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(D/'instrumented.c'),'-o',str(D/'oracle.exe')],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr
p=subprocess.run([str(D/'oracle.exe')],capture_output=True,text=True,timeout=20);assert p.returncode==0,p.stderr;(D/'stdout.txt').write_text(p.stdout);events=[json.loads(x[6:]) for x in p.stdout.splitlines() if x.startswith('AUDIT ')];rows=[];endpoints=[]
def native_items(e):
 nodes={n['id']:n for n in e['nodes']};items=[];p=e['root'];seen=set()
 while p>0 and p not in seen:
  seen.add(p);n=nodes[p];children=[];h=n['sub'];hseen=set()
  while h>0 and h not in hseen:hseen.add(h);children.append(nodes[h]['value']);h=nodes[h]['next']
  items.append({'parent':n['value'],'children':children});p=n['next']
 return items
for index,c in enumerate(cases):
 client.post('/sequential/sublist/reset')
 for parent,children in c['seed']:
  assert client.post('/sequential/sublist/operate',json={'operation':'insertar_padre','payload':{'parent':parent}}).get_json()['success']
  for child in children:assert client.post('/sequential/sublist/operate',json={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).get_json()['success']
 data=client.post('/sequential/sublist/operate',json={'operation':c['operation'],'payload':c['payload']}).get_json();trace=data.get('execution_trace') or {};steps=trace.get('steps',[]);lookup=collections.defaultdict(collections.deque)
 for step in steps:lookup[step['line_text'].strip()].append(step)
 for e in [x for x in events if x['case']==index]:
  q=lookup[e['line']];step=q.popleft() if q else None;issues=[];state={}
  if step is None:issues.append('missing_instruction')
  else:
   state=step['state_snapshot'] if e['line'].startswith(('if ','while ','return ')) or e['condition'] in {-3,-6} else step['state_after']
   actual=[{'parent':x.get('parent'),'children':x.get('children',[])} for x in state.get('items',[])]
   if actual!=native_items(e):issues.append('reachable_parent_child_values')
   code=trace['source_code'].splitlines();start=next((i for i,x in enumerate(code) if re.match(r'(?:static )?(?:Nodo \*|Sublista \*|bool |void |int )'+e['function']+r'\(',x)),None)
   if start is None or step['line_index']!=start+e['offset']:issues.append('physical_line_or_call_scope')
   if e['condition']>=0 and step.get('pedagogy',{}).get('condition',{}).get('result')!=bool(e['condition']):issues.append('condition_result')
   if not state.get('heap_nodes') and e['nodes']:issues.append('full_heap_identity_not_represented')
  rows.append({'native':e,'issues':issues,'step':step})
 endpoints.append({'case':index,**c,'success':data['success'],'message':data.get('message'),'state':data.get('visual_state'),'trace_steps':len(steps)})
report={'scope':'Native comparison of six visible methods and required helpers; narrow child-removal planning fix applied; remaining differences are not a pass certificate.','cases':endpoints,'events':len(events),'counts':dict(collections.Counter(x for row in rows for x in row['issues'])),'rows':rows,'downloaded_sha256':hashlib.sha256(raw).hexdigest(),'limits':['Not a pass certificate. UI both views/replay not yet tested.','Masks prevent reading uninitialized fields; only live allocations dereferenced. Saved integer aliases invalidated at free.','Side-effect-free guard evaluated twice, same result. Source return observed before evaluating delegated return expression.','NULL top-level address and allocation failure not injected. Alias UI and copied buffer contents still require focused comparison.']};(D/'review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['cases','rows']}))



