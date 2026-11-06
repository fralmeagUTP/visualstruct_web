"""Actual renderer dispatch covers six families without browser execution."""
import json, subprocess
from pathlib import Path
import pytest
from app import create_app
from app.config import Config
from e2e_sequential_render_contract import OBSERVER, assert_causal_render

@pytest.mark.parametrize('family,operations',[
 ('stack',['apilar','desapilar']),('queue',['encolar','desencolar']),
 ('priority_queue',['encolar','desencolar']),('linked_list',['insertar_inicio','eliminar_elemento']),
 ('circular_list',['insertar_final','eliminar_inicio']),('sublist',['insertar_padre','eliminar_padre']),
])
def test_actual_player_renderers_receive_exact_causal_state_and_memory(tmp_path,family,operations):
 class Local(Config):
  TESTING=True
  SESSION_CACHE_DIR=str(tmp_path/'session')
 traces=[]
 with create_app(Local).test_client() as client:
  for op in operations:
   response=client.post('/sequential/'+family+'/operate',json={'operation':op,'payload':{'value':9,'parent':9,'priority':1}})
   data=response.get_json();assert response.status_code==200 and data['success']
   traces.append({'family':family,'op':op,'trace':data['execution_trace']})
 path=tmp_path/'input.json';path.write_text(json.dumps({'observer':OBSERVER,'traces':traces}))
 root=Path(__file__).resolve().parents[1]
 run=subprocess.run(['node','qa/emit_e2e_sequential_renders.js',str(path)],cwd=root,capture_output=True,text=True,timeout=30)
 assert run.returncode==0,run.stderr
 rows=json.loads(run.stdout);lookup={t['op']:t['trace'] for t in traces}
 for row in rows:
  assert_causal_render(row['event'],lookup[row['op']],row['cursor'],family)
  for node in row['roots']:
   pointer=row['event']['memory']['root'][node['edge']] or 'NULL'
   assert node['count']==1 and node['value']==pointer and node['text'].endswith(pointer)
 assert len(rows)==sum(len(t['trace']['steps'])*4+2 for t in traces)
 if family in ['stack','queue','priority_queue']:
  # The previous observer wrapped only this generic function and therefore
  # missed the first actual draw entirely in these specialized paths.
  assert rows[0]['event']['renderer']!='renderVisualState'
 # Both visible representations receive identical bytes at each causal cursor.
 for op in operations:
  a=[r['event'] for r in rows if r['op']==op and r['view']=='current']
  b=[r['event'] for r in rows if r['op']==op and r['view']=='linked']
  assert a==b

@pytest.mark.parametrize('corruption',['values','memory','renderer'])
def test_projection_observer_rejects_changed_values_or_owned_memory(corruption):
 import copy
 from app.services.structure_service import StructureService
 data=StructureService.execute_operation('stack','apilar',{'value':9},[])
 trace=data['execution_trace'];step=trace['steps'][0]
 memory={**step['pedagogy']['push_memory'],'variables':[],'aux':None,'next':None,'call_stack':[]}
 event={'renderer':'renderStackPushState','state':copy.deepcopy(step['state_snapshot']),'memory':copy.deepcopy(memory)}
 assert_causal_render(event,trace,-1,'stack')
 if corruption=='values':event['state']['items']=[{'value':999}]
 elif corruption=='memory':event['memory']['root']['value']='invented-node'
 else:event['renderer']='renderVisualState'
 with pytest.raises(AssertionError):assert_causal_render(event,trace,-1,'stack')


def _seeded_trace(family, seed_operation, seed_payload, operation, payload):
 from app.services.structure_service import StructureService
 seed=StructureService.execute_operation(family,seed_operation,seed_payload,[])
 assert seed['success']
 result=StructureService.execute_operation(family,operation,payload,seed['history'])
 assert result['success']
 return result['execution_trace']


@pytest.mark.parametrize('field',['head','heap_node_link','missing_head','cantidad'])
def test_projection_cannot_forge_shared_root_links_count_or_omit_keys(field):
 import copy
 family='circular_list' if field=='cantidad' else 'linked_list'
 trace=_seeded_trace(family,'insertar_final',{'value':9},'insertar_final',{'value':8})
 projected=trace['steps'][0]['pedagogy']['memory_state']
 if field=='head':projected['head']='FORGED_ROOT'
 elif field=='heap_node_link':projected['heap_nodes'][0]['next']='FORGED_NEXT'
 elif field=='missing_head':del projected['head']
 else:projected['cantidad']=999
 # Both trace metadata and the observed render contain the corruption. Only
 # the independent canonical snapshot can reject this, not view==projection.
 event={'renderer':'renderVisualState','state':copy.deepcopy(projected),'memory':None}
 with pytest.raises(AssertionError):assert_causal_render(event,trace,0,family)


@pytest.mark.parametrize('corruption',[
 'other_index','intermediate_index','other_operation','not_return','wrong_function',
 'not_successful_return','wrong_canonical_index','different_previous_snapshot',
 'different_initial_count','different_retired_node','missing_retired_node',
 'retired_still_alive','wrong_historical_fields','wrong_final_root','wrong_output',
])
def test_retained_out_index_exception_rejects_unrelated_or_incoherent_state(corruption):
 import copy
 trace=_seeded_trace('priority_queue','encolar',{'value':9,'priority':1},'desencolar',{})
 cursor=len(trace['steps'])-2 if corruption=='intermediate_index' else len(trace['steps'])-1
 step=trace['steps'][cursor];projected=step['pedagogy']['memory_state']
 memory=step['pedagogy']['dequeue_memory']
 if corruption in {'other_index','intermediate_index'}:projected['out_index']=1
 elif corruption=='other_operation':trace['operation_name']='encolar'
 elif corruption=='not_return':step['event_type']='counter'
 elif corruption=='wrong_function':step['function_name']='cp_encolar'
 elif corruption=='not_successful_return':step['line_text']='return false;'
 elif corruption=='wrong_canonical_index':step['state_after']['out_index']=1
 elif corruption=='different_previous_snapshot':trace['steps'][cursor-1]['state_after']['out_index']=1
 elif corruption=='different_initial_count':trace['steps'][0]['state_snapshot']['size']=2
 elif corruption=='different_retired_node':memory['retired'][0]['id']='FORGED_RETIRED'
 elif corruption=='missing_retired_node':memory['retired']=[]
 elif corruption=='retired_still_alive':memory['retired'][0]['alive']=True
 elif corruption=='wrong_historical_fields':memory['retired'][0]['historical_fields']['valor']=999
 elif corruption=='wrong_final_root':memory['root']['front']='FORGED_ROOT'
 else:memory['outputs']['value']=999
 event={'renderer':'renderPriorityQueueDequeueState','state':copy.deepcopy(projected),'memory':copy.deepcopy(memory)}
 with pytest.raises(AssertionError):assert_causal_render(event,trace,cursor,'priority_queue')
