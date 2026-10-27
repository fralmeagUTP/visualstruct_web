"""Independent actual-C observations for Heap destroy/reinitialize, including OOM."""
from pathlib import Path
import json,shutil,subprocess
import pytest
from app import create_app
from app.services.c_code_service import CCodeService

CASES=[(seed,repeats,fail) for fail in [False,True] for seed,repeats in [([],1),([7],1),(list(range(21)),1),([7,-1,7],2)]]
HELPER=r'''
static int active,case_id,iteration,failure,depth,stack[4],ref,live1,live2,generation;
static int objective_state,objective,new_state,new_capacity,temp_state,temp_ref;
static int original_count,original[64];
static void audit_emit(const char *scope,const char *text,const char *phase,const MonticuloBinario *m,int condition,int result){
 if(!active)return;
 printf("AUDIT {\"case\":%d,\"iteration\":%d,\"scope\":\"%s\",\"text\":\"%s\",\"phase\":\"%s\",\"condition\":%d,\"result\":%d,\"quantity\":%d,\"capacity\":%d,\"reference\":%d,\"live1\":%d,\"live2\":%d,\"generation\":%d,\"objective_state\":%d,\"objective\":%d,\"new_state\":%d,\"new_capacity\":%d,\"temp_state\":%d,\"temp_ref\":%d,\"stack\":[",case_id,iteration,scope,text,phase,condition,result,m->cantidad,m->capacidad,ref,live1,live2,generation,objective_state,objective,new_state,new_capacity,temp_state,temp_ref);
 for(int i=0;i<depth;i++){printf("%s%d",i?",":"",stack[i]);}printf("],\"array\":[");
 if(live1 && ref==1){for(int i=0;i<original_count;i++){printf("%s%d",i?",":"",original[i]);}}printf("]}\n");
}
static void audit_enter(int frame){stack[depth++]=frame;}
static void audit_leave(int frame){depth--;if(frame==2)objective_state=0;if(frame==3){new_state=0;temp_state=0;}}
static int audit_condition(const char *scope,const char *text,const MonticuloBinario *m,int value){audit_emit(scope,text,"condition",m,value,-2);return value;}
static void *audit_realloc(void *p,size_t n){if(active && failure)return NULL;void *out=realloc(p,n);if(active && out){live2=1;generation++;}return out;}
'''

@pytest.fixture(scope='module')
def heap_clear_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('heap-clear-native');client=create_app().test_client();raw=client.get('/help/source/binary_heap/source').data;header=client.get('/help/source/binary_heap/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(out/('tad_monticulo_binario.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig').replace('\r\n','\n');originals={scope:CCodeService._extract_function_with_comment(source,name) for scope,name in [('destroy','monticulo_destruir'),('init','monticulo_inicializar'),('reserve','asegurar_capacidad')]}
 def body(scope):
  code=originals[scope];signature={'destroy':'void monticulo_destruir(','init':'void monticulo_inicializar(','reserve':'static bool asegurar_capacidad('}[scope];return code[code.index(signature):]
 def log(scope,text,phase,condition='-2',result='-2'):return 'audit_emit('+json.dumps(scope)+','+json.dumps(text)+','+json.dumps(phase)+',m,'+condition+','+result+');'
 def guard(scope,text,expression):return 'audit_condition('+json.dumps(scope)+','+json.dumps(text)+',m,'+expression+')'
 signatures={scope:body(scope).splitlines()[0] for scope in originals}
 for scope,frame in [('destroy',1),('init',2),('reserve',3)]:
  old=body(scope);new=old.replace('{','{audit_enter('+str(frame)+');'+log(scope,signatures[scope],'enter'),1)
  if scope=='destroy':
   for text,expression in [('if (m != NULL) {','m != NULL'),('if (m->datos) {','m->datos!=NULL')]:new=new.replace(text,'if('+guard(scope,text,expression)+'){',1)
   for text,extra in [('free(m->datos);','live1=0;ref=-1;'),('m->datos = NULL;','ref=0;'),('m->cantidad = 0;',''),('m->capacidad = 0;','')]:new=new.replace(text,text+extra+log(scope,text,'free' if text.startswith('free') else 'assignment'),1)
  elif scope=='init':
   text='int capacidad_objetivo;';new=new.replace(text,text+'objective_state=1;'+log(scope,text,'declaration'),1)
   text='if (m == NULL) return;';new=new.replace(text,'if('+guard(scope,text,'m==NULL')+')return;',1)
   for text,extra in [('m->tipo = tipo;',''),('m->cantidad = 0;',''),('m->capacidad = 0;',''),('m->datos = NULL;','ref=0;'),('capacidad_objetivo = (capacidad_inicial > 0) ? capacidad_inicial : MONTICULO_CAPACIDAD_POR_DEFECTO;','objective_state=2;objective=capacidad_objetivo;')]:
    new=new.replace(text,text+extra+log(scope,text,'assignment','capacidad_inicial>0' if text.startswith('capacidad_objetivo') else '-2'))
   text='if (!asegurar_capacidad(m, capacidad_objetivo)) {'
   new=new.replace(text,log(scope,text,'call')+'if('+guard(scope,text,'!asegurar_capacidad(m,capacidad_objetivo)')+'){',1)
  else:
   for text,extra in [('int nueva_capacidad;','new_state=1;'),('int *nuevos_datos;','temp_state=1;')]:new=new.replace(text,text+extra+log(scope,text,'declaration'),1)
   for text,expression in [('if (m == NULL || capacidad_objetivo <= 0) {','m==NULL||capacidad_objetivo<=0'),('if (m->capacidad >= capacidad_objetivo && m->datos != NULL) {','m->capacidad>=capacidad_objetivo&&m->datos!=NULL'),('while (nueva_capacidad < capacidad_objetivo) {','nueva_capacidad<capacidad_objetivo'),('if (nueva_capacidad > INT_MAX / 2) {','nueva_capacidad>INT_MAX/2'),('if (nuevos_datos == NULL) {','nuevos_datos==NULL')]:
    keyword='while' if text.startswith('while') else 'if';new=new.replace(text,keyword+'('+guard(scope,text,expression)+'){',1)
   for text,extra,phase,cond in [
    ('nueva_capacidad = (m->capacidad > 0) ? m->capacidad : MONTICULO_CAPACIDAD_POR_DEFECTO;','new_state=2;new_capacity=nueva_capacidad;','assignment','m->capacidad>0'),
    ('nueva_capacidad *= 2;','new_capacity=nueva_capacidad;','assignment','-2'),
    ('nuevos_datos = (int *)realloc(m->datos, sizeof(int) * (size_t)nueva_capacidad);','temp_state=2;temp_ref=nuevos_datos?2:0;','allocation','-2'),
    ('m->datos = nuevos_datos;','ref=2;','assignment','-2'),('m->capacidad = nueva_capacidad;','','assignment','-2')]:new=new.replace(text,text+extra+log(scope,text,phase,cond),1)
   # Only returns reached by the actual run emit; invalid/preallocated branches are retained.
   for status in ['true','false']:new=new.replace('return '+status+';','audit_leave(3);'+log(scope,'return '+status+';','return',result=status)+'return '+status+';')
  if scope!='reserve':new=new[:-1]+'audit_leave('+str(frame)+');'+log(scope,'}','return')+'}'
  source=source.replace(old,new,1)
 source=source.replace(signatures['reserve'],HELPER+'\n#define realloc audit_realloc\n'+signatures['reserve'],1)
 caller='void ejecutar_limpiar(MonticuloBinario *m) {\n    monticulo_destruir(m);\n    monticulo_inicializar(m, MONTICULO_MIN, 16);\n}'
 instrumented=caller.replace('{','{audit_enter(0);'+log('caller',caller.splitlines()[0],'enter'),1)
 for text in ['monticulo_destruir(m);','monticulo_inicializar(m, MONTICULO_MIN, 16);']:instrumented=instrumented.replace(text,log('caller',text,'call')+text+log('caller',text,'resume'))
 instrumented=instrumented[:-1]+'audit_leave(0);'+log('caller','}','return')+'}'
 main='\nint main(void){MonticuloBinario m;'
 for i,(seed,repeats,fail) in enumerate(CASES):
  main+='active=0;depth=0;monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join('monticulo_insertar(&m,'+str(v)+');' for v in seed)
  for repeat in range(repeats):
   main+=f'case_id={i};iteration={repeat};failure={int(fail)};live1=m.datos!=NULL;live2=0;ref=live1?1:0;generation=live1;objective_state=0;new_state=0;temp_state=0;original_count=m.cantidad;for(int i=0;i<original_count;i++)original[i]=m.datos[i];active=1;ejecutar_limpiar(&m);active=0;'
  main+='monticulo_destruir(&m);'
 # Raw NULL guards independently checked without observing uninitialized m fields.
 main+='active=0;monticulo_destruir(NULL);monticulo_inicializar(NULL,MONTICULO_MIN,16);return 0;}'
 (out/'instrumented.c').write_text(source+'\n'+instrumented+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 report={'cases':[{'seed':seed,'repeats':repeats,'fail':fail} for seed,repeats,fail in CASES],'events':events,'originals':originals,'caller':caller,'limits':['Allocator internals opaque; successful realloc and injected NULL observed.','No pointer read after free: saved symbolic ref/lifetime flags; cached logical prefix only.','NULL public guards executed independently without a display model.']}
 (out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def fail_init(m,tipo,capacity):
 m.tipo=tipo;m.datos=[];m.cantidad=0;m.capacidad=0

def fail_clear(self):
 from app.domain.hierarchical.tad_wrappers import monticulo_destruir
 tipo=self._m.tipo;monticulo_destruir(self._m);fail_init(self._m,tipo,16)

@pytest.mark.parametrize('case',range(8))
def test_heap_clear_matches_native(heap_clear_native,case,monkeypatch):
 client=create_app().test_client();seed,repeats,fail=CASES[case]
 for v in seed:assert client.post('/hierarchical/binary_heap/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 if fail:monkeypatch.setattr('app.domain.hierarchical.tad_wrappers.MonticuloBinario.limpiar',fail_clear)
 for iteration in range(repeats):
  data=client.post('/hierarchical/binary_heap/operate',json={'operation':'limpiar','payload':{}}).json;assert data['success'];trace=data['execution_trace']
  assert trace['steps'][0]['state_snapshot'].get('heap_clear_model')
  events=[e for e in heap_clear_native['events'] if e['case']==case and e['iteration']==iteration];assert len(trace['steps'])==len(events)
  for step,event in zip(trace['steps'],events):
   assert step['line_text'].strip()==event['text'];ped=step['pedagogy'];assert ped['instruction_event']['scope']==event['scope'] and ped['instruction_event']['phase']==event['phase']
   state=ped['memory_state'];assert state['array']==event['array'] and state['size']==event['quantity'] and state['capacity']==event['capacity']
   assert ped['invariant']['holds'] is None and ped['invariant']['name']=='Estado intermedio de vida de memoria' and not ped['invariant']['evidence_by_node_or_path']
   assert state['heap_data_reference']=={-1:'indeterminado (A1 historico)',0:'NULL',1:'A1',2:'A2'}[event['reference']]
   assert [f['id'] for f in state['query_frames']]==[{0:'caller',1:'destroy',2:'init',3:'reserve'}[f] for f in event['stack']]
   assert any(o['id']=='A1' and o['live'] for o in state['heap_allocations'])==bool(event['live1'])
   assert any(o['id']=='A2' and o['live'] for o in state['heap_allocations'])==bool(event['live2'])
   byid={f['id']:f for f in state['query_frames']}
   assert all(f['parameters']['m']=='M1' for f in state['query_frames'])
   if 'init' in byid:
    assert byid['init']['parameters']=={'m':'M1','tipo':0,'capacidad_inicial':16}
    assert byid['init']['locals']==({} if not event['objective_state'] else {'capacidad_objetivo':'sin inicializar' if event['objective_state']==1 else event['objective']})
   if 'reserve' in byid:
    assert byid['reserve']['parameters']=={'m':'M1','capacidad_objetivo':16}
    expected={}
    if event['new_state']:expected['nueva_capacidad']='sin inicializar' if event['new_state']==1 else event['new_capacity']
    if event['temp_state']:expected['nuevos_datos']='sin inicializar' if event['temp_state']==1 else 'A2' if event['temp_ref'] else 'NULL'
    assert byid['reserve']['locals']==expected
   if event['condition']!=-2:assert step['condition_result']==bool(event['condition'])
   if event['scope']=='reserve' and event['phase']=='return':assert ped['instruction_event']['return']==bool(event['result'])
   assert state['console_stdout']==''
  assert data['visual_state']['capacity']==(0 if fail else 20) and data['visual_state']['size']==0
  assert trace['steps'][-1]['state_after']==data['visual_state']

def test_heap_clear_actual_guide_documents_lifetimes_and_void_status():
 client=create_app().test_client();response=client.get('/help/hierarchical/binary_heap');assert response.status_code==200
 for text in ['Limpiar destruye el buffer previo aunque cantidad sea cero','El retorno void no anuncia el resultado de la reserva','retroceder','capacidad 0']:
  assert text.lower() in response.data.decode('utf-8').lower()
 for kind in ['source','header']:
  data=client.get('/help/source/binary_heap/'+kind).data.decode('utf-8-sig')
  if kind=='source':block=CCodeService._extract_function_with_comment(data,'monticulo_destruir')
  else:
   end=data.index('void monticulo_destruir(MonticuloBinario *m);');start=data.rfind('/**',0,end);assert start>=0;block=data[start:end]
  assert 'Si m es NULL no hace nada' in block and 'incluso con cantidad 0' in block and 'No modifica tipo' in block and 'Esta funcion no reinicializa' in block
