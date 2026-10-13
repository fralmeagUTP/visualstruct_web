"""Independent native C observations for the two visible circular insertions."""
import collections,json,re,shutil,subprocess
from pathlib import Path
import pytest
from app import create_app
CASES=[(op,seed) for op in ['insertar_inicio','insertar_final'] for seed in [[],[7],[7,8,9],[7,7,9]]]
@pytest.fixture(scope='module')
def circular_native(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: native circular fidelity unverified')
 d=tmp_path_factory.mktemp('circular_native');client=create_app().test_client();response=client.get('/help/source/circular_list/source');assert response.status_code==200;source=response.data.decode('utf-8-sig').replace('\r\n','\n');(d/'downloaded.c').write_text(source,encoding='utf-8');header=client.get('/help/source/circular_list/header');assert header.status_code==200;(d/'tad_lista_circular.h').write_bytes(header.data)
 helper=r'''
static ListaCircular *audit_root;
static LCirNodo *audit_nodes[32];
static int audit_values[32],audit_nexts[32],audit_count,audit_case,audit_active,audit_new=-2,audit_node=-2;
static int audit_id(LCirNodo *p){if(p==NULL)return 0;for(int i=0;i<audit_count;i++)if(audit_nodes[i]==p)return i+1;return -1;}
static void audit_emit(const char *fn,const char *line,int condition){
 if(!audit_active)return;
 printf("AUDIT {\"case\":%d,\"function\":\"%s\",\"line\":\"%s\",\"condition\":%d,\"head\":%d,\"tail\":%d,\"cantidad\":%d,\"nuevo\":%d,\"nodo\":%d,\"nodes\":[",audit_case,fn,line,condition,audit_id(audit_root->cabeza),audit_id(audit_root->cola),audit_root->cantidad,audit_new,audit_node);
 for(int i=0;i<audit_count;i++){
  if(i){printf(",");}printf("{\"id\":%d,\"value\":",i+1);
  if(audit_values[i])printf("%d",audit_nodes[i]->valor);else printf("\"sin inicializar\"");
  printf(",\"next\":");if(audit_nexts[i])printf("%d",audit_id(audit_nodes[i]->sgte));else printf("-2");printf("}");
 }
 printf("],\"reachable\":[");LCirNodo *p=audit_root->cabeza;int seen[32]={0},count=0;
 while(p!=NULL){int id=audit_id(p);if(id<1||id>32||seen[id-1])break;seen[id-1]=1;if(count++)printf(",");printf("%d",id);if(!audit_nexts[id-1])break;p=p->sgte;}
 printf("]}\n");
}
'''
 modified=source
 for fn,signature in [('lcir_insertar_inicio','bool lcir_insertar_inicio('),('lcir_insertar_final','bool lcir_insertar_final('),('lcir_crear_nodo','static LCirNodo *lcir_crear_nodo(')]:
  a=modified.index(signature);z=modified.index('\n}',a)+2;out=[]
  for line in modified[a:z].splitlines():
   text=line.strip();lit=json.dumps(text);emit='audit_emit('+json.dumps(fn)+','+lit
   if text.startswith('if ('):
    expr=re.search(r'if \((.*)\)',text).group(1);out.append(emit+',('+expr+'));')
   if text.startswith('return '):
    out.append(emit+',-1);')
    if fn=='lcir_crear_nodo':out.append('audit_node=-2;')
   out.append(line)
   if 'malloc(sizeof(LCirNodo))' in text:out.append('if(audit_active && nodo!=NULL){audit_nodes[audit_count]=nodo;audit_values[audit_count]=0;audit_nexts[audit_count]=0;audit_count++;audit_node=audit_id(nodo);}')
   if text=='nodo->valor = valor;':out.append('if(audit_active)audit_values[audit_id(nodo)-1]=1;')
   if text=='nodo->sgte = NULL;':out.append('if(audit_active)audit_nexts[audit_id(nodo)-1]=1;')
   if text=='nuevo = lcir_crear_nodo(valor);':out.append('if(audit_active)audit_new=audit_id(nuevo);')
   if text.endswith(';') and not text.startswith(('return ','LCirNodo *nuevo;')):out.append(emit+',-1);')
  modified=modified[:a]+'\n'.join(out)+modified[z:]
 at=modified.index('static LCirNodo *lcir_crear_nodo(');modified=modified[:at]+helper+'\n'+modified[at:];main=['int main(void){']
 for index,(op,seed) in enumerate(CASES):
  main+=['{ListaCircular lista;lcir_inicializar(&lista);audit_active=0;']+[f'lcir_insertar_final(&lista,{v});' for v in seed]
  main+=['audit_count=0;audit_root=&lista;LCirNodo *p=lista.cabeza;if(p!=NULL){do{audit_nodes[audit_count]=p;audit_values[audit_count]=1;audit_nexts[audit_count]=1;audit_count++;p=p->sgte;}while(p!=lista.cabeza);}audit_new=audit_node=-2;']
  main+=[f'audit_case={index};audit_active=1;lcir_{op}(&lista,11);audit_active=0;lcir_destruir(&lista);}}']
 main+=['return 0;}'];(d/'instrumented.c').write_text(modified+'\n'+'\n'.join(main),encoding='utf-8');exe=d/'oracle.exe'
 build=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(d/'instrumented.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;(d/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(line[6:]) for line in run.stdout.splitlines() if line.startswith('AUDIT ')];(d/'native-events.json').write_text(json.dumps(events,indent=2),encoding='utf-8');assert len(events)==112
 return events,d

def pointer(value):return 'NULL' if value==0 else 'sin inicializar' if value==-2 else f'N{value}'

@pytest.mark.parametrize('case,operation,seed',[(i,op,seed) for i,(op,seed) in enumerate(CASES)])
def test_circular_insertions_native_heap_alias_quantity_and_scope(client,circular_native,case,operation,seed):
 events,d=circular_native
 for value in seed:assert client.post('/sequential/circular_list/operate',json={'operation':'insertar_final','payload':{'value':value}}).get_json()['success']
 data=client.post('/sequential/circular_list/operate',json={'operation':operation,'payload':{'value':11}}).get_json();assert data['success'];steps=data['execution_trace']['steps'];lookup=collections.defaultdict(collections.deque)
 for step in steps:lookup[step['line_text'].strip()].append(step)
 rows=[]
 for native in [e for e in events if e['case']==case]:
  assert lookup[native['line']],native['line'];step=lookup[native['line']].popleft()
  matches=[i for i,line in enumerate(data['execution_trace']['source_code'].splitlines()) if line.strip()==native['line']]
  expected_index=matches[-1] if seed and native['function']!='lcir_crear_nodo' else matches[0]
  assert step['line_index']==expected_index,(native['line'],step['line_index'],expected_index)
  before=step['state_snapshot'];after=step['state_after'];observed=before if native['line'].startswith(('if ','return ')) else after
  assert observed['cabeza']==pointer(native['head']);assert observed['cola']==pointer(native['tail']);assert observed['cantidad']==native['cantidad'];assert observed['size']==native['cantidad']
  ids=[pointer(x) for x in native['reachable']];assert observed['node_ids']==ids;assert observed['reachable_count']==len(ids)
  expected=[{'id':pointer(x['id']),'value':x['value'],'next':pointer(x['next']),'status':'linked' if pointer(x['id']) in ids else 'temporary'} for x in native['nodes']];assert observed['heap_nodes']==expected
  assert observed['items']==[{'value':next(n['value'] for n in expected if n['id']==node)} for node in ids]
  for name in ['nuevo','nodo']:
   if native[name]==-2:assert name not in observed
   else:assert observed[name]==pointer(native[name])
  assert observed['active_function']==native['function']
  stack=step['pedagogy']['call_stack'];assert stack[0]['function']=='lcir_'+operation and stack[0]['parameters']['lista']=='&lc'
  if after.get('active_function')=='lcir_crear_nodo':assert stack[-1]['function']=='lcir_crear_nodo' and stack[-1]['parameters']=={'valor':11}
  if native['line']=='nuevo = lcir_crear_nodo(valor);':assert before['heap_nodes']==after['heap_nodes'] and 'nuevo' not in before
  if native['condition']!=-1:
   assert step['pedagogy']['condition']['result']==bool(native['condition'])
   substituted=step['pedagogy']['condition']['substituted'];assert 'None' not in substituted and "'N" not in substituted
   if native['line']=='if (lista == NULL) {':assert '&lc' in substituted
  assert not step.get('console',[]);assert not step['pedagogy']['heap_transition']['freed']
  if native['line']=='return nodo;':assert 'nodo' not in after and step['pedagogy']['pointers'][next(i for i,x in enumerate(step['pedagogy']['pointers']) if x['name']=='nodo')]['target']=='fuera de ámbito'
  rows.append({'native':native,'step':step})
 assert steps[-1]['state_after']==data['visual_state'];projection=steps[-1]['pedagogy']['memory_state'];assert projection['items']==data['visual_state']['items'];assert 'nuevo' not in projection and 'nodo' not in projection
 (d/f'comparison-{case}.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
