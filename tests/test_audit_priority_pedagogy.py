"""Regression of native-reviewed priority queue instruction pedagogy."""
import pytest

def _assert_priority_release(step, priorities):
 selected=min(range(len(priorities)),key=lambda i:priorities[i]);identity=f'N{selected+1}'
 frame=step['pedagogy'];memory=frame['dequeue_memory'];retired=memory['retired']
 assert step['state_after']['objetivo']==identity
 assert len(retired)==1 and retired[0]['id']==identity and retired[0]['freed'] is True and retired[0]['alive'] is False
 assert 'fields' not in retired[0]
 assert retired[0]['historical_fields']=={'valor':10*(selected+1),'prioridad':priorities[selected],'sgte':f'N{selected+2}' if selected+1<len(priorities) else None}
 assert frame['heap_transition']['freed']==retired
 expected_ids={f'N{i+1}' for i in range(len(priorities)) if i!=selected}
 assert len(memory['heap'])==len(expected_ids) and {n['id'] for n in memory['heap']}==expected_ids
 assert frame['heap_objects']==memory['heap'] and frame['heap_transition']['after']==memory['heap']
 expected_aliases={name for name in ['actual','prev','objetivo','objetivoPrev'] if step['state_snapshot'].get(name)==identity}
 pointers={p['name']:p for p in memory['pointers']}
 assert frame['pointers']==memory['pointers'] and frame['variables']==memory['variables']
 assert len(memory['pointers'])==len(pointers)
 variables={v['name']:v for v in memory['variables']}
 assert {x['name'] for x in memory['invalid_aliases']}==expected_aliases
 assert all(x['historical_id']==identity and x['usable'] is False for x in memory['invalid_aliases'])
 assert 'objetivo' in expected_aliases
 for name in expected_aliases:
  p=pointers[name]
  assert p['target']==identity and p['historical_id']==identity and p['valid'] is False and p['dangling'] is True
  assert step['state_after'][name]==identity
  assert variables[name]['value']==identity and variables[name]['valid'] is False and variables[name]['dangling'] is True
 assert memory['outputs']=={'value':10*(selected+1),'priority':priorities[selected],'value_written':True,'priority_written':True}
 assert [x['value'] for x in step['state_after']['items']]==[10*(i+1) for i in range(len(priorities)) if i!=selected]
 assert step['state_after']['cantidad']==len(priorities)

@pytest.mark.parametrize('priorities',[[1,2,3],[3,1,2],[3,2,1],[1,1,2],[3,1,1],[4,3,1],[1],[]])
@pytest.mark.parametrize('operation',['desencolar','frente'])
def test_native_reviewed_priority_instruction_state_and_conditions(client,priorities,operation):
 for i,priority in enumerate(priorities):
  assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':10*(i+1),'priority':priority}}).get_json()['success']
 data=client.post('/sequential/priority_queue/operate',json={'operation':operation,'payload':{}}).get_json();steps=data['execution_trace']['steps']
 guard=next(s for s in steps if s['line_text'].strip().startswith('if (cola == NULL'))
 assert not guard['pedagogy']['condition']['substituted'].startswith('NULL == NULL')
 assert guard['pedagogy']['condition']['result']==(not priorities)
 if not priorities:return
 selected=min(range(len(priorities)),key=lambda i:priorities[i])
 assert data['result']==10*(selected+1)
 for s in steps:
  line=s['line_text'].strip();before=s['state_snapshot'];after=s['state_after']
  if line=='if (actual->prioridad < objetivo->prioridad) {':
   actual=int(before['actual'][1:])-1;goal=int(before['objetivo'][1:])-1
   assert s['pedagogy']['condition']['result']==(priorities[actual]<priorities[goal])
  if operation=='frente' and line=='objetivo = cola->delante;':assert after['objetivo']=='N1'
  if operation=='frente' and line=='actual = cola->delante->sgte;':assert after['actual']==('N2' if len(priorities)>1 else 'NULL')
  if line in ['cola->delante = objetivo->sgte;','objetivoPrev->sgte = objetivo->sgte;']:
   assert after['actual']=='NULL' and after['prev']==f'N{len(priorities)}'
   assert after['objetivo']==f'N{selected+1}'
   assert after['objetivoPrev']==('NULL' if selected==0 else f'N{selected}')
   assert s['pedagogy']['heap_transition']['freed']==[]
  if line=='free(objetivo);':
   _assert_priority_release(s,priorities)
 if operation=='desencolar' and selected==0:
  condition=next(s for s in steps if s['line_text'].strip()=='if (cola->delante == NULL) {')
  assert condition['pedagogy']['condition']['result']==(len(priorities)==1)

@pytest.mark.parametrize('case',['front','interior','rear','equal-front','equal-interior','several-updates','single'])
@pytest.mark.parametrize('mutation',[None,'wrong_ID','still_live','usable_alias'])
def test_priority_release_rejects_corrupted_historical_identity(case,mutation):
 from pathlib import Path
 import json
 from copy import deepcopy
 report=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-desencolar-instructions-medium/API-report.json'
 row=next(r for r in json.loads(report.read_text(encoding='utf-8')) if r['case']==case)
 step=deepcopy(next(s for s in row['data']['execution_trace']['steps'] if s['line_text'].strip()=='free(objetivo);'))
 priorities=row['priorities'];selected=min(range(len(priorities)),key=lambda i:priorities[i]);identity=f'N{selected+1}';m=step['pedagogy']['dequeue_memory']
 if mutation=='wrong_ID':m['retired'][0]['id']='wrong_ID'
 elif mutation=='still_live':
  live={'id':identity,'alive':True,'freed':False,'fields':deepcopy(m['retired'][0]['historical_fields'])}
  m['heap'].append(live);step['pedagogy']['heap_objects']=deepcopy(m['heap']);step['pedagogy']['heap_transition']['after']=deepcopy(m['heap'])
 elif mutation=='usable_alias':
  aliases=[p for p in m['pointers'] if p['name'] in ['actual','prev','objetivo','objetivoPrev'] and step['state_snapshot'].get(p['name'])==identity]
  target=next((p for p in aliases if p['name']=='prev'),next(p for p in aliases if p['name']=='objetivo'))
  target['valid']=True;target['dangling']=False
  step['pedagogy']['pointers']=deepcopy(m['pointers'])
  for v in m['variables']:
   if v['name']==target['name']:v['valid']=True;v['dangling']=False
  step['pedagogy']['variables']=deepcopy(m['variables'])
 if mutation is None:_assert_priority_release(step,priorities)
 else:
  with pytest.raises(AssertionError):_assert_priority_release(step,priorities)
