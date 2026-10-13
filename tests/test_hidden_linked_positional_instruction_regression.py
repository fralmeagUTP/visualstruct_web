"""Focal HTTP instructions vs independent C17 observers; private cache only."""
from pathlib import Path
import json,re,subprocess,os
import pytest
from app import create_app
from app.config import Config
ROOT=Path(__file__).resolve().parents[1]
CASES=[('before-head','insertar_posicion',[],{'position':1,'value':9}),('before-inner','insertar_posicion',[4,5,6],{'position':2,'value':9}),('before-tail','insertar_posicion',[4,5,6],{'position':3,'value':9}),('before-append','insertar_posicion',[4,5,6],{'position':4,'value':9}),('before-outside','insertar_posicion',[4,5,6],{'position':5,'value':9}),('relative-before','insertar_elemento',[4,5,6],{'position':2,'relative':-1,'value':9}),('relative-after','insertar_elemento',[4,5,6],{'position':2,'relative':0,'value':9}),('after-outside','insertar_elemento',[4,5,6],{'position':4,'relative':0,'value':9}),('delete-head','eliminar_posicion',[4,5,6],{'position':1}),('delete-inner','eliminar_posicion',[4,5,6],{'position':2}),('delete-tail','eliminar_posicion',[4,5,6],{'position':3})]

def source_function(text,name):
 start=text.index(('int ' if name=='lista_eliminar_posicion' else 'Tlista ' if name=='CrearNodoLista' else 'void ')+name+'(')
 return text[start:text.index('\n}',start)+2]

@pytest.fixture(scope='module')
def focal(tmp_path_factory):
 out=Path(os.environ.get('HIDDEN_TRACE_OUT',str(tmp_path_factory.mktemp('hidden-traces'))));out.mkdir(parents=True,exist_ok=True)
 class QA(Config):
  TESTING=True
  SECRET_KEY='private-focal-hidden'
  SESSION_CACHE_DIR=str(out/'private-cache')
  SESSION_CACHE_THRESHOLD=0
 app=create_app(QA);assert Path(app.config['SESSION_CACHELIB']._path).resolve().is_relative_to(out.resolve());responses=[]
 for label,op,seed,payload in CASES:
  client=app.test_client()
  for v in seed:assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':v}}).get_json()['success']
  response=client.post('/sequential/linked_list/operate',json={'operation':op,'payload':payload});assert response.status_code==200
  data=response.get_json();assert data['success'];responses.append(data)
  (out/(label+'-HTTP.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 c=ROOT/'docs/tads_C/tad_lista.c';source=c.read_text(encoding='utf-8-sig').replace('\r\n','\n');modified=source
 # Observe expressions exactly once. Heap observer never reads fields before initialization or after free.
 for name in ['CrearNodoLista','lista_insertar_elemento','lista_eliminar_posicion']:
  original=source_function(modified,name);new=[]
  for line in original.splitlines():
   t=line.strip()
   if not t or t.startswith(('/*','* ','*/','//')):new.append(line);continue
   token=json.dumps(t)
   if t.startswith(('Tlista CrearNodoLista(','void lista_insertar_elemento(','int lista_eliminar_posicion(')):
    new.append(line);new.append('audit_emit('+token+',-1);');continue
   if t.startswith('while (actual != NULL'):
    new.append('while (actual != NULL && indice < posicion) { anterior=actual;actual=actual->sgte;indice++; audit_emit('+token+',1); } audit_emit('+token+',0);');continue
   if t.startswith('if (anterior == NULL)'):
    new.append('{int yes=anterior==NULL;if(yes)*lista=actual->sgte;else anterior->sgte=actual->sgte;audit_emit('+token+',yes);}');continue
   if t.startswith(('if (','while (')):
    if t.endswith('{'):
     m=re.match(r'(\s*(?:if|while)\s*\()(.*)(\)\s*\{)',line);assert m,t
     new.append(m[1]+'audit_condition('+token+',('+m[2]+'))'+m[3]);continue
    if 'return 0;' in t:
     expr=t[t.index('(')+1:t.index(')')];new.append('if (audit_condition('+token+',('+expr+'))) {audit_emit('+token+',-1);return 0;}');continue
   if t.startswith('return'):
    new.append('audit_emit('+token+',-1);'+line);continue
   new.append(line)
   if t.endswith(';'):
    if t=='q->nro = valor;':new.append('audit_mark(q,1);')
    if t=='q->sgte = NULL;':new.append('audit_mark(q,2);')
    new.append('audit_emit('+token+',-1);')
  modified=modified.replace(original,'\n'.join(new))
 helpers=r'''
static Tlista slots[128];static int live[128],mask[128],used,enabled,case_id;static Tlista *owner;
static int id(Tlista p){if(!p)return 0;for(int i=0;i<used;i++)if(live[i]&&slots[i]==p)return i+1;return -1;}
static void *audit_malloc(size_t n){void *p=malloc(n);if(p){slots[used]=p;live[used]=1;mask[used++]=0;}return p;}
static void audit_free(void *p){int i=id(p);if(i>0)live[i-1]=0;free(p);}
static void audit_mark(Tlista p,int bit){int i=id(p);if(i>0)mask[i-1]|=bit;}
static void quote(const char *s){putchar('"');for(;*s;s++){if(*s=='"'||*s=='\\')putchar('\\');putchar(*s);}putchar('"');}
static void audit_emit(const char *line,int cond){if(!enabled)return;printf("OBS {\"case\":%d,\"line\":",case_id);quote(line);printf(",\"condition\":%d,\"head\":%d,\"heap\":[",cond,id(*owner));int comma=0;for(int i=0;i<used;i++)if(live[i]){if(comma++)putchar(',');printf("{\"id\":%d,\"value\":",i+1);if(mask[i]&1)printf("%d",slots[i]->nro);else printf("null");printf(",\"next\":");if(mask[i]&2)printf("%d",id(slots[i]->sgte));else printf("null");printf("}");}puts("]}");}
static int audit_condition(const char *s,int c){audit_emit(s,c);return c;}
'''
 point=modified.index('\n',modified.index('typedef struct NodoLista* Tlista;'))+1
 modified=modified[:point]+helpers+'\n#define malloc audit_malloc\n#define free audit_free\n'+modified[point:]
 # This caller is the existing JS positional translation, with observers appended only.
 main=['int main(void){']
 for idx,(_,op,seed,p) in enumerate(CASES):
  main+=['{Tlista lista=NULL;owner=&lista;enabled=0;used=0;']
  main+=['lista_insertar_final(&lista,'+str(v)+');' for v in seed]
  main+=['for(int k=0;k<used;k++)mask[k]=3;',f'case_id={idx};enabled=1;', 'audit_emit("void caller_compatibilidad(void) {",-1);']
  def add(code,line):main.append(code+' audit_emit('+json.dumps(line)+',-1);')
  pos=p['position'];before=op=='insertar_posicion' or p.get('relative',0)<0
  if op=='eliminar_posicion':
   add('int eliminado;','int eliminado;');main+=['audit_emit("(void)lista_eliminar_posicion(&lista, posicion_ui - 1, &eliminado);",-1);',f'(void)lista_eliminar_posicion(&lista,{pos-1},&eliminado);']
  elif before and pos!=1:
   add('Tlista *enlace=&lista;','Tlista *enlace = &lista;');add('int posicion=1;','int posicion = 1;')
   main+=['while(audit_condition("while (posicion < posicion_ui && *enlace != NULL) {",posicion<'+str(pos)+'&&*enlace!=NULL)){']
   add('enlace=&(*enlace)->sgte;','enlace = &(*enlace)->sgte;');add('posicion++;','posicion++;')
   main+=['}', 'if(audit_condition("if (posicion == posicion_ui) lista_insertar_elemento(enlace, valor_ui, 1);",posicion=='+str(pos)+')) lista_insertar_elemento(enlace,'+str(p['value'])+',1);']
  else:
   main+=['audit_emit("lista_insertar_elemento(&lista, valor_ui, posicion_ui);",-1);',f"lista_insertar_elemento(&lista,{p['value']},{pos});"]
  main+=['audit_emit("}",-1);enabled=0;lista_limpiar(&lista);for(int k=0;k<used;k++)if(live[k])return 2;}']
 main+=['return 0;}'];modified+='\n'+'\n'.join(main)
 native=out/'instruction-observer.c';native.write_text(modified,encoding='utf-8');exe=out/'instruction-observer.exe'
 command=['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(native),'-o',str(exe)]
 build=subprocess.run(command,capture_output=True,text=True);(out/'native-compile.log').write_text(build.stdout+build.stderr,encoding='utf-8');assert build.returncode==0,build.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True);(out/'native-execution.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stderr
 records=[json.loads(l[4:]) for l in run.stdout.splitlines() if l.startswith('OBS ')]
 (out/'native-report.json').write_text(json.dumps({'command':command,'compile_exit':build.returncode,'run_exit':run.returncode,'records':records},indent=2),encoding='utf-8')
 return out,app,responses,records

@pytest.mark.parametrize('case_index',range(len(CASES)),ids=[c[0] for c in CASES])
def test_hidden_HTTP_instructions_match_native(focal,case_index):
 out,app,responses,records=focal;steps=responses[case_index]['execution_trace']['steps'];expected=[r for r in records if r['case']==case_index]
 assert len(steps)==len(expected),([s['line_text'].strip() for s in steps],expected)
 for step,n in zip(steps,expected):
  assert step['line_text'].strip()==n['line']
  assert step['condition_result']==(None if n['condition']==-1 else bool(n['condition']))
  state=step['pedagogy']['memory_state']
  def ptr(v):return None if v=='sin inicializar' else 0 if v=='NULL' else int(v[1:])
  assert ptr(state['head'])==n['head']
  actual=[{'id':ptr(h['id']),'value':None if h['value']=='sin inicializar' else h['value'],'next':ptr(h['next'])} for h in state['heap_nodes']]
  assert actual==n['heap'],(step['line_text'],actual,n['heap'])
  if step is not steps[-1]:assert step['state_after']==state
  else:assert step['state_after']==responses[case_index]['visual_state']
  if step['event_type']=='return':
   assert all(c['function']!=step['function_name'] for c in step['pedagogy']['call_stack'])
   assert step['pedagogy']['scopes'][0]['state']=='ended'
  assert all(v['scope']==step['function_name'] for v in step['pedagogy']['variables'])

@pytest.mark.parametrize('operation,payload',[('insertar_posicion',{'position':0,'value':9}),('insertar_elemento',{'position':2,'relative':3,'value':9}),('eliminar_posicion',{'position':8})])
def test_hidden_validation_has_no_C_execution(focal,operation,payload):
 _,app,_,_=focal;client=app.test_client();data=client.post('/sequential/linked_list/operate',json={'operation':operation,'payload':payload}).get_json()
 assert not data['success'] and not data['history'] and not data['execution_trace']['steps']
 assert data['execution_trace']['execution_started'] is False
