"""Recorded sorted effects persist without rerunning historical algorithms."""
import copy
import pytest
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SORTING_ALGORITHMS
from app.services.sorting_structure_service import SortingStructureService as S

def execute(op,p,h):return S.execute_operation(structure_id='sorting_array',operation_name=op,payload=p,history=h)
@pytest.mark.parametrize('algorithm',[a['id'] for a in SORTING_ALGORITHMS])
def test_repeated_runs_persist_result_without_get_dispatch(algorithm,monkeypatch):
 h=execute('create_array',{'values':[3,-1,3,0]},[])['history'];calls=[];old=SortingAdapter.run
 def spy(self,mode,**kw):
  calls.append(self.to_visual_state()['items']);return old(self,mode,**kw)
 monkeypatch.setattr(SortingAdapter,'run',spy)
 for i in range(2):
  d=execute('run',{'mode':'fast','algorithm_id':algorithm},h);assert d['success'];h=d['history']
  assert sum(e['operation']=='run' for e in h)==i+1
  for _ in range(2):
   view=S.get_view_model('sorting_array',h);assert view['history']==h;assert view['visual_state']['items']==[-1,0,3,3];assert view['visual_state']['algorithm']==algorithm
 assert calls==[[3,-1,3,0],[-1,0,3,3]]
 d=execute('run',{'mode':'bad','algorithm_id':algorithm},h);assert not d['success'] and d['history']==h

@pytest.mark.parametrize('effect',[None,{}, {'schema':1,'input':[3,1],'output':[1,3]}, {'schema':1,'input':[3,2,1],'output':[1,2,2]}, {'schema':1,'input':[3,2,1],'output':[1,True,3]}])
def test_invalid_old_effects_not_replayed(effect,monkeypatch):
 h=execute('create_array',{'values':[3,2,1]},[])['history'];fake={'operation':'run','payload':{'mode':'fast','algorithm_id':'burbuja'},'array_effect':effect};original=copy.deepcopy(h)
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('historical dispatch'))
 view=S.get_view_model('sorting_array',h+[fake]);assert view['history']==original and view['visual_state']['items']==[3,2,1]

def test_step_uses_original_input_without_append():
 h=execute('create_array',{'values':[3,2,1]},[])['history'];run=execute('run',{'mode':'step_by_step','algorithm_id':'burbuja'},h);h=run['history']
 step=execute('step',{'direction':'next','cursor':-1,'algorithm_id':'burbuja'},h);assert step['success'] and step['history']==h
 assert step['execution_trace']['steps'][0]['state_snapshot']['items']==[3,2,1]
 assert S.get_view_model('sorting_array',h)['visual_state']['items']==[1,2,3]
