"""Native per-instruction observer versus Rojo-Negro query projection."""
from pathlib import Path
import json
import pytest
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from _audit_rbt_query_native_observer import observe
SEEDS=[[],[10],[10,5,15],[-2147483648,0,2147483647]]
CASES=[(seed,op,seed[-1] if seed else 99) for seed in SEEDS for op in ['inorden','altura','validar','buscar']]+[(seed,'buscar',99) for seed in SEEDS[1:]]
NUMERIC={'dato','tieneMin','minimo','tieneMax','maximo','altIzq','altDer','bhIzq','bhDer'}
def pointer(n):return 'NULL' if n==0 else 'N'+str(n)
def match(trace,events):
 steps=trace['steps'];assert len(steps)==len(events),(len(steps),len(events))
 for step,event in zip(steps,events):
  ped=step['pedagogy'];state=ped['memory_state'];assert step['line_index']+1==event['line'],(step['line_text'],event);assert ped['instruction_event']['phase']==event['phase']
  expected=[{'function':f['function'],'id':f['id'],'parameters':{k:v if k in NUMERIC else pointer(v) for k,v in f['parameters'].items()},'locals':{k:v if k in NUMERIC or isinstance(v,str) else pointer(v) for k,v in f['locals'].items()}} for f in event['frames']]
  actual=[{k:f[k] for k in ['function','id','parameters','locals']} for f in state['tree_frames']];assert actual==expected,(step['line_text'],actual,expected)
  assert state['console_stdout']==bytes.fromhex(event['stdout_hex']).decode('utf-8')
  assert [{k:n[k] for k in ['id','value','left','right','parent','color']} for n in state['heap_nodes']]==[{**n,'id':pointer(n['id']),'left':pointer(n['left']),'right':pointer(n['right']),'parent':pointer(n['parent'])} for n in event['heap']]
  assert state['wrapper_result'] is None if not event['wrapper_set'] else state['wrapper_result']==('void' if trace['operation_name']=='inorden' else pointer(event['wrapper']) if trace['operation_name']=='buscar' else event['wrapper'])
  if event['phase'] in ['condition','operand']:assert ped['instruction_event']['condition']==bool(event['result'])
  if event['phase']=='return':assert ped['return_propagation']['value']==('void' if trace['operation_name']=='inorden' else pointer(event['result']) if trace['operation_name']=='buscar' else event['result'])
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'];assert state['root']==steps[0]['state_snapshot']['root']
 for a,b in zip(steps,steps[1:]):assert a['state_after']==b['state_snapshot']
@pytest.fixture(scope='session')
def rbt_query_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('rbt-native-query');client=create_app().test_client();raw=client.get('/help/source/red_black/source').data;header=client.get('/help/source/red_black/header').data;r=Path(__file__).resolve().parents[1]
 assert raw==(r/'docs/tads_C/tad_rojo_negro.c').read_bytes() and header==(r/'docs/tads_C/tad_rojo_negro.h').read_bytes();results=[]
 for case,(seed,op,value) in enumerate(CASES):
  history=[{'operation':'insertar','payload':{'value':v}} for v in seed];data=S.execute_operation('red_black',op,{'value':value} if op=='buscar' else {},history);assert data['success'];trace=data['execution_trace'];events=observe(trace['source_code'],op,seed,value,raw,header,out/('case'+str(case)));results.append({'case':case,'seed':seed,'operation':op,'value':value,'data':data,'events':events});print('RBT native observed',case,op,len(events),flush=True)
 (out/'native-query-review.json').write_text(json.dumps({'cases':len(results),'events':sum(len(x['events']) for x in results),'records':results},indent=2));return results
@pytest.mark.parametrize('case',range(len(CASES)))
def test_rbt_query_instruction_native_agreement(rbt_query_native,case):
 record=rbt_query_native[case];match(record['data']['execution_trace'],record['events'])
