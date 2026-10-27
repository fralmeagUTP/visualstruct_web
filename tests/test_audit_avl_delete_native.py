"""Independent current downloaded-C deletion observations, not a model-derived oracle."""
from pathlib import Path
import sys,json,subprocess
from copy import deepcopy
import pytest
from app.adapters.avl_adapter import AVLAdapter
from app.domain.hierarchical.avl_delete_instruction import build_avl_delete_trace
from app.services.trace.engine import TraceEngine
from test_audit_avl_insert_native import mapping
def native_pairs(trace,events,rawlines):
 selected=[s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']!='caller_enter'][1:]
 actual,expected=len(selected),len(events)-1
 assert actual==expected, 'Native/model boundary count: '+str(actual)+' vs '+str(expected)
 return list(zip(selected,events[1:]))
NUMERIC={'tmp','feL','feR','altIzq','altDer'}
@pytest.fixture(scope='module')
def avl_delete_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-delete-native');script=Path(__file__).with_name('_audit_avl_delete_native_observer.py').read_text(encoding='utf-8').replace("r=Path(r'D:\\MisProyectos\\Web_VisualEstruct')","r=Path("+repr(str(Path(__file__).resolve().parents[1]))+")").replace("o=w/'avl-delete-baseline-low'","o=Path("+repr(str(out))+')');(out/'observer.py').write_text(script,encoding='utf-8');run=subprocess.run([sys.executable,'-u',str(out/'observer.py')],capture_output=True,text=True,encoding='utf-8',timeout=90);(out/'observer.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr;d=json.loads((out/'review.json').read_text(encoding='utf-8'));assert len(d['events'])==1913;d['source_lines']=(out/'tad_avl.c').read_text(encoding='utf-8-sig').splitlines();return d
def fixture(case,d):
 c=d['cases'][case];a=AVLAdapter()
 for v in c['seed']:a.execute('insertar',{'value':v})
 before=a.to_visual_state();after=deepcopy(before)
 if not c.get('null_ref') and c['value'] in c['seed']:a.execute('eliminar',{'value':c['value']});after=a.to_visual_state()
 trace=build_avl_delete_trace({'payload':{'value':c['value']},'success':True},before,after,null_ref=c.get('null_ref',False));return trace,before,after
def check(step,e,ids,base,rawlines,shownlines):
 p=step['pedagogy'];phase=p['instruction_event']['phase'];assert phase==e['phase'];state=step['state_snapshot'] if phase=='return' else p['memory_state']
 if e['line']:
  assert step['line_text'].strip()==rawlines[e['line']-1].strip();fn=e['frames'][-1]['function'];rawstart=next(i for i,l in enumerate(rawlines) if (' '+fn+'(') in l and l.rstrip().endswith('{'));shownstart=next(i for i,l in enumerate(shownlines) if (' '+fn+'(') in l and l.rstrip().endswith('{'));assert step['line_index']-shownstart==e['line']-1-rawstart
 assert state['head']==ids[e['root']];expected=[{'id':ids[n['id']],'value':n['value'],'balance_factor':n['fe'],'left':ids[n['left']],'right':ids[n['right']],'parent':ids[n['parent']]} for n in e['nodes']];assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id']);assert [n['id'] for n in state['freed_nodes']]==[ids[i] for i in e['freed_ids']]
 assert len(state['tree_frames'])==len(e['frames'])
 for f,n in zip(state['tree_frames'],e['frames']):
  assert f['function']==n['function'] and f['id']=='F'+str(n['id']-base);assert f['locals']=={k:ids[v] if k not in NUMERIC and isinstance(v,int) else v for k,v in n['locals'].items()}
  fn=n['function'];params=({'raiz':'&raiz' if n['ref'] else 'NULL','x':n['x']} if fn=='avl_eliminar' else {'raiz':'&raiz' if n['ref'] else 'NULL','nodo':ids[n['node']]} if fn=='rebalancearTrasEliminar' else {'raiz':ids[n['node']],'x':n['x']} if fn=='avl_buscar' else {'nodo':ids[n['node']]} if fn=='avl_minimo' else {'arbol':ids[n['node']]} if fn=='avl_altura' else {'r':'&raiz' if n['ref'] else 'NULL','nodo':ids[n['node']]});assert f['parameters']==params
 if phase=='condition':assert step['condition_result']==bool(e['result'])
 if phase=='return':
  fn=e['frames'][-1]['function'];result=ids[e['result']] if fn in ['avl_buscar','avl_minimo'] else e['result'] if fn=='avl_altura' else 'void';assert p['instruction_event']['return']==result and len(p['memory_state']['tree_frames'])==len(e['frames'])-1
 if phase=='free':assert [n['id'] for n in p['memory']['freed_objects']]==[ids[e['result']]]
 else:assert not p['memory']['freed_objects']
 assert not p['memory']['allocated_objects'] and state['console_stdout']==''
@pytest.mark.parametrize('case',range(19))
def test_avl_delete_each_native_instruction(avl_delete_native,case):
 d=avl_delete_native;trace,before,after=fixture(case,d);TraceEngine.validate_legacy_trace({**trace,'structure_id':'avl','final_state':after});events=[e for e in d['events'] if e['case']==case];ids=mapping(events);base=events[1]['frames'][0]['id']-1
 for step,e in native_pairs(trace,events,d['source_lines']):check(step,e,ids,base,d['source_lines'],trace['source_code'].splitlines())
 assert trace['steps'][-1]['state_after']==after
 if case in [0,1,17,18]:assert trace['steps'][-1]['pedagogy']['memory_state']['root']==before['root']

@pytest.mark.parametrize('seed,target',[([],7),([10],99),([10,5,15],99)])
def test_avl_delete_api_rejection_does_not_invoke_C(seed,target):
 from app import create_app
 client=create_app().test_client()
 for v in seed:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 before=client.get('/hierarchical/avl').status_code;assert before==200
 response=client.post('/hierarchical/avl/operate',json={'operation':'eliminar','payload':{'value':target}});assert response.status_code==400;data=response.json;assert not data['success'];trace=data['execution_trace'];assert trace['application_precondition_rejected'] and len(trace['steps'])==1
 step=trace['steps'][0];p=step['pedagogy'];assert step['state_snapshot']==step['state_after']==data['visual_state'];assert step['line_index']==0 and 'antes de invocar avl_eliminar' in step['line_text'];assert p['instruction_event']['C_invoked'] is False and not p['call_stack'] and not p['variables'];assert not p['memory']['allocated_objects'] and not p['memory']['freed_objects'];TraceEngine.validate_legacy_trace(trace)
