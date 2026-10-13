"""Visible Circular clear/reverse: actual downloaded native C instruction oracle."""
from pathlib import Path
import collections,json,re,shutil
import pytest
CASES=[(op,seed) for op in ['invertir','limpiar'] for seed in [[],[7],[7,8,9],[7,7,9]]]
@pytest.fixture(scope='module')
def native_clear_reverse(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable; fidelity unverified')
 tmp_path=tmp_path_factory.mktemp('native_clear_reverse')
 from pathlib import Path
 import os,sys,json,re,subprocess,collections,hashlib
 W=tmp_path;R=Path(r'D:\MisProyectos\Web_VisualEstruct');D=W/'native-circular-clear-reverse';D.mkdir(parents=True,exist_ok=True);os.environ['SESSION_CACHE_DIR']=str(W/'circular-five-native-session');sys.path.insert(0,str(R));from app import create_app
 client=create_app().test_client();raw=client.get('/help/source/circular_list/source').data;source=raw.decode('utf-8-sig').replace('\r\n','\n');(D/'downloaded.c').write_bytes(raw);(D/'tad_lista_circular.h').write_bytes(client.get('/help/source/circular_list/header').data)
 slots={'actual':0,'anterior':1,'prev':2,'curr':3,'next':4,'old_head':5}
 functions={'eliminar_inicio':'lcir_eliminar_inicio','eliminar_primero':'lcir_eliminar_primero','buscar_posiciones':'lcir_buscar_posiciones','invertir':'lcir_invertir','limpiar':'lcir_destruir'}
 cases=[]
 for op in ['eliminar_inicio','invertir','limpiar']:
  for seed in [[],[7],[7,8,9],[7,7,9]]:cases.append({'operation':op,'seed':seed,'payload':{}})
 for seed,value in [([],7),([7],7),([7],99),([7,8,9],7),([7,8,9],8),([7,8,9],9),([7,8,9],99),([7,7,9],7)]:cases.append({'operation':'eliminar_primero','seed':seed,'payload':{'value':value}})
 for seed,value in [([],7),([7],7),([7,8,9],8),([7,7,9],7),([7,8,9],99)]:cases.append({'operation':'buscar_posiciones','seed':seed,'payload':{'value':value}})
 cases=[case for case in cases if case['operation'] in {'limpiar','invertir'}]
 functions={'limpiar':'lcir_destruir','invertir':'lcir_invertir'}
 helper=r'''
 static ListaCircular *audit_root;
 static LCirNodo *audit_nodes[32];
 static int audit_live[32],audit_count,audit_case,audit_active,audit_alias[6],audit_found=-2,audit_pos=-2,audit_freed;
 static int audit_id(LCirNodo *p){if(p==NULL)return 0;for(int i=0;i<audit_count;i++){if(audit_live[i] && audit_nodes[i]==p)return i+1;}return -1;}
 static void audit_emit(const char *fn,int offset,const char *line,int condition){
  if(!audit_active)return;
  printf("AUDIT {\"case\":%d,\"function\":\"%s\",\"offset\":%d,\"line\":\"%s\",\"condition\":%d,\"head\":%d,\"tail\":%d,\"cantidad\":%d,\"freed\":%d,\"aliases\":[",audit_case,fn,offset,line,condition,audit_id(audit_root->cabeza),audit_id(audit_root->cola),audit_root->cantidad,audit_freed);
  for(int i=0;i<6;i++){if(i){printf(",");}printf("%d",audit_alias[i]);}
  printf("],\"encontrados\":%d,\"pos\":%d,\"nodes\":[",audit_found,audit_pos);int printed=0;
  for(int i=0;i<audit_count;i++){if(audit_live[i]){if(printed++){printf(",");}printf("{\"id\":%d,\"value\":%d,\"next\":%d}",i+1,audit_nodes[i]->valor,audit_id(audit_nodes[i]->sgte));}}
  printf("],\"reachable\":[");LCirNodo *p=audit_root->cabeza;int seen[32]={0},count=0;
  while(p!=NULL){int id=audit_id(p);if(id<1||id>32||seen[id-1])break;seen[id-1]=1;if(count++){printf(",");}printf("%d",id);p=p->sgte;}
  printf("]}\n");
 }
 static void audit_retire(int id){if(!audit_active || id<1)return;audit_live[id-1]=0;audit_freed=id;for(int i=0;i<6;i++){if(audit_alias[i]==id)audit_alias[i]=-100-id;}}
 '''
 modified=source
 for fn in functions.values():
  a=re.search(r'^(?:bool|void|int) '+fn+r'\(',modified,re.M).start();z=modified.index('\n}',a)+2;out=[]
  for offset,line in enumerate(modified[a:z].splitlines()):
   text=line.strip();emit='audit_emit('+json.dumps(fn)+','+str(offset)+','+json.dumps(text)
   if text.startswith(('if (','while (','} while (')):
    match=re.match(r'(\s*(?:if|while|}\s*while)\s*\()(.*)(\)\s*(?:\{|;)\s*)$',line)
    assert match,line
    out.append(match.group(1)+'('+emit+',('+match.group(2)+')),('+match.group(2)+'))'+match.group(3));continue
   if text=='free(actual);':out+=['if(audit_active){audit_freed=audit_id(actual);}',line,'audit_retire(audit_freed);',emit+',-1);'];continue
   if text.startswith('return '):out.append(emit+',-1);')
   out.append(line)
   for name,slot in slots.items():
    if re.match(re.escape(name)+r'\s*=',text):out.append('if(audit_active)audit_alias['+str(slot)+']=audit_id('+name+');')
   for name,state in [('encontrados','audit_found'),('pos','audit_pos')]:
    if re.match(r'(?:int\s+)?'+name+r'\s*(?:=|\+\+)',text):out.append('if(audit_active)'+state+'='+name+';')
   if text.endswith(';') and not text.startswith(('return ','LCirNodo *')):out.append(emit+',-1);')
  modified=modified[:a]+'\n'.join(out)+modified[z:]
 at=modified.index('static LCirNodo *lcir_crear_nodo(');modified=modified[:at]+helper+'\n'+modified[at:];main=['int main(void){']
 for index,case in enumerate(cases):
  main+=['{ListaCircular lista;lcir_inicializar(&lista);audit_active=0;']+[f'lcir_insertar_final(&lista,{v});' for v in case['seed']]
  main+=['audit_count=0;audit_root=&lista;LCirNodo *p=lista.cabeza;if(p!=NULL){do{audit_nodes[audit_count]=p;audit_live[audit_count]=1;audit_count++;p=p->sgte;}while(p!=lista.cabeza);}for(int k=0;k<6;k++){audit_alias[k]=-2;}audit_found=audit_pos=-2;audit_freed=0;']
  op=case['operation'];fn=functions[op];value=case['payload'].get('value');args='&lista'+(','+str(value) if value is not None else '')
  if op=='buscar_posiciones':main+=['int positions[32]={0};'];args+=',positions,'+str(max(1,len(case['seed'])))
  main+=[f'audit_case={index};audit_active=1;'+fn+'('+args+');','audit_active=0;lcir_destruir(&lista);}']
 main+=['return 0;}'];(D/'instrumented.c').write_text(modified+'\n'+'\n'.join(main),encoding='utf-8');exe=D/'oracle.exe';build=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(D/'instrumented.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15);assert run.returncode==0,run.stderr;(D/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(line[6:]) for line in run.stdout.splitlines() if line.startswith('AUDIT ')]
 assert len(events)==100
 return events,D

def ptr(n):return 'NULL' if n==0 else 'indeterminado (liberado)' if n<=-100 else f'N{n}'
@pytest.mark.parametrize('case,operation,seed',[(i,op,seed) for i,(op,seed) in enumerate(CASES)])
def test_circular_clear_reverse_native_identity_alias_heap_exact_line(client,native_clear_reverse,case,operation,seed):
 events,d=native_clear_reverse;client.post('/sequential/circular_list/reset')
 for value in seed:assert client.post('/sequential/circular_list/operate',json={'operation':'insertar_final','payload':{'value':value}}).get_json()['success']
 data=client.post('/sequential/circular_list/operate',json={'operation':operation,'payload':{}}).get_json();assert data['success'];expected=seed[::-1] if operation=='invertir' else [];assert [x['value'] for x in data['visual_state']['items']]==expected
 trace=data['execution_trace'];fn='lcir_invertir' if operation=='invertir' else 'lcir_destruir';start=next(i for i,line in enumerate(trace['source_code'].splitlines()) if line.startswith('void '+fn+'('));lookup=collections.defaultdict(collections.deque)
 for step in trace['steps']:lookup[step['line_text'].strip()].append(step)
 rows=[]
 for native in [e for e in events if e['case']==case]:
  assert lookup[native['line']],native;step=lookup[native['line']].popleft();assert step['line_index']==start+native['offset'];state=step['state_snapshot'] if native['line'].startswith(('if ','while ','} while ','return ')) else step['state_after'];ids=[ptr(n) for n in native['reachable']];nodes={ptr(n['id']):n for n in native['nodes']}
  assert state['cabeza']==ptr(native['head']) and state['cola']==ptr(native['tail']);assert state['cantidad']==state['size']==native['cantidad'];assert state['node_ids']==ids;assert [x['value'] for x in state['items']]==[nodes[n]['value'] for n in ids]
  assert state['heap_nodes']==[{'id':ptr(n['id']),'value':n['value'],'next':ptr(n['next']),'status':'linked' if ptr(n['id']) in ids else 'detached'} for n in native['nodes']]
  for slot,name in enumerate(['actual','anterior','prev','curr','next','old_head']):
   alias=native['aliases'][slot]
   if alias==-2:assert name not in state
   else:assert state[name]==ptr(alias),(operation,native['line'],name,state.get(name),ptr(alias))
  assert not step['console'];freed=step['pedagogy']['heap_transition']['freed'];assert [x['id'] for x in freed]==([ptr(native['freed'])] if native['line']=='free(actual);' else [])
  if native['condition']!=-1:assert step['pedagogy']['condition']['result']==bool(native['condition'])
  rows.append({'native':native,'step':step,'verified':True})
 last=trace['steps'][-1];assert last['line_text'].strip() in {'return;','}'};assert last['pedagogy']['call_stack'][0]['function']==fn;assert last['pedagogy']['call_stack'][0]['return'] is None;memory=last['pedagogy']['memory_state'];assert memory['scope_ended'];assert all(name not in memory for name in ['actual','prev','curr','next','old_head']);assert memory['items']==data['visual_state']['items']
 (d/f'case-{case}.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
