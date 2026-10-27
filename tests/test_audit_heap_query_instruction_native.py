"""Independent native C observations for the two visible heap queries."""
from _instruction_context_contract import context_stack
from pathlib import Path
import json,subprocess,shutil
import pytest
from app import create_app
from app.services.c_code_service import CCodeService

SEEDS=[([],0),([7],0),([7,-1,7,0],0),(list(range(20,-1,-1)),0),(list(range(20,-1,-1)),18)]
CASES=[(op,seed,pops) for op in ['raiz','a_lista'] for seed,pops in SEEDS]

HELPER=r'''
static MonticuloBinario *audit_m;
static int audit_case,audit_active,audit_caller,audit_callee,audit_aliases;
static int q_state,q,buf_state,used_state,used,ok_state,ok,a_state,a,ci_present,ci,ii_present,ii;
static int out_initialized,out_value,copied,allocations,frees,retired_count;
static int retired_values[128];static int *audit_buffer;
static void audit_emit(int line,const char *scope,const char *phase,int result){
 if(!audit_active)return;
 printf("AUDIT {\"case\":%d,\"line\":%d,\"scope\":\"%s\",\"phase\":\"%s\",\"result\":%d,\"caller\":%d,\"callee\":%d,\"aliases\":%d,\"quantity\":%d,\"capacity\":%d,\"q_state\":%d,\"q\":%d,\"buffer_state\":%d,\"used_state\":%d,\"used\":%d,\"ok_state\":%d,\"ok\":%d,\"a_state\":%d,\"a\":%d,\"ci_present\":%d,\"ci\":%d,\"ii_present\":%d,\"ii\":%d,\"output_initialized\":%d,\"output\":%d,\"copied\":%d,\"allocations\":%d,\"frees\":%d,\"array\":[",audit_case,line,scope,phase,result,audit_caller,audit_callee,audit_aliases,audit_m->cantidad,audit_m->capacidad,q_state,q,buf_state,used_state,used,ok_state,ok,a_state,a,ci_present,ci,ii_present,ii,out_initialized,out_value,copied,allocations,frees);
 for(int i=0;i<audit_m->cantidad;i++)printf("%s%d",i?",":"",audit_m->datos[i]);
 printf("],\"destination\":[");
 if(buf_state==2)for(int i=0;i<q;i++){if(i)printf(",");if(i<copied)printf("%d",audit_buffer[i]);else printf("null");}
 printf("],\"retired\":[");for(int i=0;i<retired_count;i++)printf("%s%d",i?",":"",retired_values[i]);printf("]}\n");
}
static int audit_condition(int line,const char *scope,const char *phase,int result){audit_emit(line,scope,phase,result);return result;}
static int audit_copy_condition(int line,int value,int index){ci=index;ci_present=value;audit_emit(line,"copy","condition",value);return value;}
static int audit_caller_condition(int line,int value,int index){ii=index;ii_present=value;audit_emit(line,"caller","loop_condition",value);return value;}
'''

@pytest.fixture(scope='module')
def heap_query_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('heap-query-native');client=create_app().test_client();raw=client.get('/help/source/binary_heap/source').data;header=client.get('/help/source/binary_heap/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes();(out/('tad_monticulo_binario.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig').replace('\r\n','\n');snippets={name:CCodeService._extract_function_with_comment(source,name) for name in ['monticulo_raiz','monticulo_cantidad','monticulo_copiar_valores']};fragment=CCodeService.get_structure_data('binary_heap')['operations']['a_lista']
 rootcaller='bool ejecutar_raiz(MonticuloBinario *m, int *resultado) {\n    bool ok = monticulo_raiz(m, resultado);\n    return ok;\n}'
 copycaller='int ejecutar_a_lista(MonticuloBinario *m) {\n'+'\n'.join('    '+l for l in fragment.replace('&monticulo','m').splitlines())+'\n    return EXIT_SUCCESS;\n}'
 originals={'root':snippets['monticulo_raiz'],'count':snippets['monticulo_cantidad'],'copy':snippets['monticulo_copiar_valores']};callers={'raiz':rootcaller,'a_lista':copycaller}
 def number(scope,text,op=None):
  code=callers[op] if scope=='caller' else originals[scope];return next(i+1 for i,l in enumerate(code.splitlines()) if l.strip()==text)
 def log(scope,text,phase,result='-2',op=None):return f'audit_emit({number(scope,text,op)},"{scope}","{phase}",{result});'
 def body(scope):
  code=originals[scope];signature={'root':'bool monticulo_raiz(','count':'int monticulo_cantidad(','copy':'int monticulo_copiar_valores('}[scope];return code[code.index(signature):]
 bodies={}
 for scope in ['root','count','copy']:
  code=body(scope);entry=code.splitlines()[0].strip();tag={'root':1,'count':2,'copy':3}[scope]
  aliases='m==audit_m && resultado!=NULL' if scope=='root' else 'm==audit_m' if scope=='count' else 'm==audit_m && capacidad==q && ((buf_state==2 && destino==audit_buffer)||(buf_state==1 && destino==NULL))'
  code=code.replace('{',f'{{audit_callee={tag};audit_aliases=({aliases});'+log(scope,entry,'enter'),1)
  guard={'root':'if (m == NULL || m->cantidad == 0 || resultado == NULL) return false;','count':'if (m == NULL) return 0;','copy':'if (m == NULL || destino == NULL || capacidad <= 0) return 0;'}[scope]
  expression={'root':'m == NULL || m->cantidad == 0 || resultado == NULL','count':'m == NULL','copy':'m == NULL || destino == NULL || capacidad <= 0'}[scope]
  ret='false' if scope=='root' else '0'
  code=code.replace(guard,f'if(audit_condition({number(scope,guard)},"{scope}","condition",{expression})){{'+log(scope,guard,'return','0')+f'audit_callee=0;return {ret};'+'}')
  if scope=='root':
   text='*resultado = m->datos[0];';code=code.replace(text,text+'out_initialized=1;out_value=*resultado;'+log(scope,text,'assignment'))
   text='return true;';code=code.replace(text,log(scope,text,'return','1')+'audit_callee=0;'+text)
  elif scope=='count':
   text='return m->cantidad;';code=code.replace(text,log(scope,text,'return','m->cantidad')+'audit_callee=0;'+text)
  else:
   text='int a_copiar = m->cantidad < capacidad ? m->cantidad : capacidad;';code=code.replace(text,text+'a_state=1;a=a_copiar;'+log(scope,text,'assignment','m->cantidad < capacidad'))
   loop='for (int i = 0; i < a_copiar; i++) {'
   code=code.replace(loop,'{int i=0;ci_present=1;ci=0;'+log(scope,loop,'loop_init')+f'for (;audit_copy_condition({number(scope,loop)},i<a_copiar,i);i++,ci=i,'+log(scope,loop,'loop_increment').rstrip(';')+') {')
   text='destino[i] = m->datos[i];';code=code.replace(text,text+'copied=i+1;'+log(scope,text,'assignment'))
   code=code.replace('    }\n    return a_copiar;','    }}\n    return a_copiar;')
   text='return a_copiar;';code=code.replace(text,log(scope,text,'return','a_copiar')+'audit_callee=0;'+text)
  bodies[scope]=code
 # Observe actual downloaded functions; insertion/preparation and destruction are uninstrumented.
 for scope in ['root','count','copy']:
  old=body(scope);assert old in source;source=source.replace(old,bodies[scope],1)
 source=source.replace(bodies['root'],HELPER+bodies['root'],1)
 instrumented_callers={}
 for op,caller in callers.items():
  entry=caller.splitlines()[0];caller=caller.replace('{','{audit_caller=1;'+log('caller',entry,'enter',op=op),1)
  if op=='raiz':
   text='bool ok = monticulo_raiz(m, resultado);';caller=caller.replace(text,'ok_state=1;'+log('caller',text,'call',op=op)+text+'ok_state=2;audit_callee=0;ok_state=2;ok=(int)ok;'+log('caller',text,'resume',op=op))
   # The native ok local shadows the observer slot; explicitly copy it using a distinct global name below.
   caller=caller.replace('ok=(int)ok;','audit_ok_value=(int)ok;')
   text='return ok;';caller=caller.replace(text,log('caller',text,'return','ok',op)+'audit_caller=0;'+text)
  else:
   text='int cantidad = monticulo_cantidad(m);';caller=caller.replace(text,'q_state=1;'+log('caller',text,'call',op=op)+text+'q_state=2;q=cantidad;'+log('caller',text,'resume',op=op))
   text='int *buffer = cantidad > 0 ? malloc((size_t)cantidad * sizeof *buffer) : NULL;';caller=caller.replace(text,text+'if(cantidad>0 && !buffer)return 9;buf_state=buffer?2:1;audit_buffer=buffer;allocations+=(buffer!=NULL);'+f'audit_emit({number("caller",text,op)},"caller",cantidad?"allocation":"assignment",cantidad>0);')
   guard='if (cantidad > 0 && buffer == NULL) {';caller=caller.replace(guard,f'if(audit_condition({number("caller",guard,op)},"caller","condition",cantidad>0 && buffer==NULL))'+' {')
   text='int usados = monticulo_copiar_valores(m, buffer, cantidad);';caller=caller.replace(text,'used_state=1;'+log('caller',text,'call',op=op)+text+'used_state=2;used=usados;'+log('caller',text,'resume',op=op))
   loop='for (int i = 0; i < usados; i++) {';caller=caller.replace(loop,'{int i=0;ii_present=1;ii=0;'+log('caller',loop,'loop_init',op=op)+f'for(;audit_caller_condition({number("caller",loop,op)},i<usados,i);i++,ii=i,'+log('caller',loop,'loop_increment',op=op).rstrip(';')+') {')
   caller=caller.replace('    }\n    free(buffer);','    }}\n    free(buffer);')
   text='free(buffer);';caller=caller.replace(text,'if(buf_state==2){retired_count=used;for(int j=0;j<used;j++)retired_values[j]=buffer[j];}'+text+'if(buf_state==2){buf_state=3;frees++;}'+log('caller',text,'free',op=op))
   text='return EXIT_SUCCESS;';caller=caller.replace(text,log('caller',text,'return','0',op)+'audit_caller=0;'+text)
  instrumented_callers[op]=caller
 # Observer ok slot has a distinct name from the actual caller variable.
 source=source.replace('ok_state,ok,','ok_state,audit_ok_value,').replace('used_state,used,ok_state,ok,a_state','used_state,used,ok_state,audit_ok_value,a_state')
 main='\nint main(void){MonticuloBinario m;int output,status;\nif(monticulo_cantidad(NULL)!=0)return 7;\n'
 for case,(op,seed,pops) in enumerate(CASES):
  main+='audit_active=0;monticulo_inicializar(&m,MONTICULO_MIN,16);'+''.join(f'if(!monticulo_insertar(&m,{v}))return 2;' for v in seed)
  main+=''.join('if(!monticulo_extraer_raiz(&m,&output))return 3;' for _ in range(pops))
  main+='audit_m=&m;q_state=q=buf_state=used_state=used=ok_state=audit_ok_value=a_state=a=ci_present=ci=ii_present=ii=out_initialized=out_value=copied=allocations=frees=retired_count=audit_caller=audit_callee=audit_aliases=0;audit_buffer=NULL;'
  main+=f'audit_case={case};audit_active=1;status='+('ejecutar_raiz(&m,&output);' if op=='raiz' else 'ejecutar_a_lista(&m);')+'audit_active=0;'
  main+='if(status!=(m.cantidad>0))return 4;if(status && output!=m.datos[0])return 5;' if op=='raiz' else 'if(status!=0 || allocations!=(m.cantidad>0) || allocations!=frees)return 6;'
  main+='monticulo_destruir(&m);\n'
 main+='return 0;}'
 program=source+'\n'+instrumented_callers['raiz']+'\n'+instrumented_callers['a_lista']+main;(out/'instrumented.c').write_text(program,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 for e in events:
  op=CASES[e['case']][0];e['source_line']=(callers[op] if e['scope']=='caller' else originals[e['scope']]).splitlines()[e['line']-1].strip()
 report={'events':events,'cases':[{'operation':op,'seed':seed,'pops':pops} for op,seed,pops in CASES],'callers':callers,'originals':originals,'raw_count_NULL_verified':True,'limits':['Native actual allocation success is observed; separate prior injected-copy-failure test covers failure contract.','Allocator internals are not interpreted; capacity20/40 observed after preparation, not inferred from size.','Small valid product min-heaps only; prior raw-copy boundary program coverage remains separate.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def prepare(client,seed,pops):
 for value in seed:assert client.post('/hierarchical/binary_heap/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 for _ in range(pops):assert client.post('/hierarchical/binary_heap/operate',json={'operation':'extraer_raiz','payload':{}}).json['success']

def matched(trace,events):
 assert len(trace['steps'])==len(events)
 for step,event in zip(trace['steps'],events):
  assert step['line_text'].strip()==event['source_line'];assert step['pedagogy']['instruction_event']['scope']==event['scope'];assert step['pedagogy']['instruction_event']['phase']==event['phase'];yield step,event

@pytest.mark.parametrize('case',range(10))
def test_heap_query_instruction_matches_real_c(heap_query_native,case):
 client=create_app().test_client();op,seed,pops=CASES[case];prepare(client,seed,pops);response=client.post('/hierarchical/binary_heap/operate',json={'operation':op,'payload':{}});data=response.json
 assert data['success']==(op=='a_lista' or len(seed)>pops)
 trace=data['execution_trace'];events=[e for e in heap_query_native['events'] if e['case']==case];initial=trace['steps'][0]['state_snapshot'];assert initial.get('heap_query_model'), 'Baseline lacks scalar/destination/scope model'
 for step,event in matched(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if event['phase']=='return' else ped['memory_state']
  assert state['array']==event['array'] and state['size']==event['quantity'] and state['capacity']==event['capacity'];assert state['root']==initial['root'] and state['console_stdout']==''
  assert bool(state['query_frames'])==bool(event['caller']);assert len(state['query_frames'])==event['caller']+bool(event['callee'])
  if event['callee']:assert event['aliases']==1
  byid={f['id']:f for f in state['query_frames']};caller=byid.get('caller');callee=byid.get({'1':'root','2':'count','3':'copy'}.get(str(event['callee'])))
  if caller:
   expected={}
   if op=='raiz':
    if event['ok_state']:expected['ok']='sin inicializar' if event['ok_state']==1 else bool(event['ok'])
   else:
    if event['q_state']:expected['cantidad']='sin inicializar' if event['q_state']==1 else event['q']
    if event['buffer_state']:expected['buffer']={1:'NULL',2:'B1',3:'B1 [valor indeterminado; identidad historica]'}[event['buffer_state']]
    if event['used_state']:expected['usados']='sin inicializar' if event['used_state']==1 else event['used']
    if event['ii_present']:expected['i']=event['ii']
   assert caller['locals']==expected
  if callee:
   assert callee['parameters']['m']=='M1'
   if event['callee']==1:assert callee['parameters']['resultado']=='&salida'
   if event['callee']==3:
    assert callee['parameters']=={'m':'M1','destino':'B1' if event['q'] else 'NULL','capacidad':event['q']}
    assert callee['locals']==({**({'a_copiar':event['a']} if event['a_state'] else {}),**({'i':event['ci']} if event['ci_present'] else {})})
  actual=ped['memory_state'];assert actual['caller_output']['initialized']==bool(event['output_initialized']);assert actual['caller_output']['value']==(event['output'] if event['output_initialized'] else None)
  assert actual['active_copy_index']==(event['ci'] if event['source_line']=='destino[i] = m->datos[i];' else 0 if event['source_line']=='*resultado = m->datos[0];' else None)
  destination=actual['destination'];assert bool(destination)==(event['buffer_state']==2)
  if destination:assert [c['value'] for c in destination['cells']]==event['destination'] and [c['initialized'] for c in destination['cells']]==[i<event['copied'] for i in range(event['q'])]
  assert ([c['value'] for c in actual['retired_destination']['cells']] if actual['retired_destination'] else [])==event['retired']
  if event['phase'] in {'condition','loop_condition'}:assert ped['condition']['result']==bool(event['result'])
  if '?' in event['source_line']:assert ped['condition']['result']==bool(event['result'])
  if event['phase']=='return':
   assert context_stack(ped)[-1]['scope_status']=='terminado (contexto del retorno)' and ped['return_propagation']['value']==event['result']
   if event['scope']=='caller':assert not actual['query_frames'] and actual['wrapper_status']==event['result']
  if event['phase']=='free':assert len(ped['memory']['freed_objects'])==int(event['frees']>0)
 assert not initial['query_frames'] and initial['observed_result'] is None and not initial['caller_output']['initialized']
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_heap_query_native_observer_coverage(heap_query_native):
 events=heap_query_native['events'];assert {e['capacity'] for e in events}=={20,40}
 assert any(e['quantity']==3 and e['capacity']==40 for e in events)
 assert {e['result'] for e in events if e['phase']=='condition' and e['scope']=='root'}=={0,1}
 assert {e['result'] for e in events if e['phase']=='condition' and e['scope']=='copy'}=={0,1}
 assert all(e['allocations']==e['frees'] for e in events if e['phase']=='return' and e['scope']=='caller' and CASES[e['case']][0]=='a_lista')

def test_heap_interpreted_query_null_guards_and_default_capacity():
 from app.domain.hierarchical.tad_monticulo_binario import MonticuloBinario,monticulo_inicializar,monticulo_raiz,monticulo_cantidad,monticulo_copiar_valores,monticulo_insertar
 output=[9876];assert not monticulo_raiz(None,output) and output==[9876]
 assert monticulo_cantidad(None)==0 and monticulo_copiar_valores(None,output,1)==0 and output==[9876]
 heap=MonticuloBinario();monticulo_inicializar(heap,0,0);assert heap.capacidad==10
 assert not monticulo_raiz(heap,output) and output==[9876]
 monticulo_insertar(heap,-1);assert not monticulo_raiz(heap,None);assert monticulo_raiz(heap,output) and output==[-1]
