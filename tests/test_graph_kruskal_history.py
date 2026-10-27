"""Canonical graph-book/v1 replay, retained C failures and mark isolation."""
import copy
import pytest
from app.adapters.graph_adapter import GraphAdapter
from app.services.graph_structure_service import GraphStructureService as S

def build(empty=False):
 h=S.execute_operation('graph','create_graph',{'directed':False},[])['history']
 if not empty:
  for op,p in [('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':1,'target':2,'weight':-3})]:h=S.execute_operation('graph',op,p,h)['history']
 return h
@pytest.mark.parametrize('empty',[True,False])
def test_repeated_success_with_canonical_replay(empty,monkeypatch):
 h=build(empty);old=GraphAdapter.execute;calls=[]
 def spy(self,op,p):
  if op=='run_kruskal':calls.append(op)
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 for i in range(3):
  d=S.execute_operation('graph','run_kruskal',{},h);assert d['success'] is (not empty);assert d['c_status']==(2 if empty else 0);h=d['history'];assert sum(x['operation']=='run_kruskal' for x in h)==i+1
  for _ in range(2):assert S.get_view_model('graph',h)['history']==h
 assert len(calls)>3 and set(calls)=={'run_kruskal'}
 assert all('mark_effect' not in x for x in h if x['operation']=='run_kruskal')

def test_empty_directed_c_failure_retained():
 h=S.execute_operation('graph','create_graph',{'directed':True},[])['history'];before=copy.deepcopy(h)
 d=S.execute_operation('graph','run_kruskal',{},h);assert not d['success'] and d['c_status']==2 and d['history'][:-1]==before
 assert S.get_view_model('graph',d['history'])['history']==d['history']

def test_past_kruskal_replayed_before_mutation(monkeypatch):
 h=S.execute_operation('graph','run_kruskal',{},build())['history']
 h=S.execute_operation('graph','remove_vertex',{'vertex':1},h)['history'];old=GraphAdapter.execute;calls=[]
 def spy(self,op,p):
  if op=='run_kruskal': calls.append(op)
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 assert S.get_view_model('graph',h)['history']==h

 # Canonical replay re-executes the query before applying the later deletion.
 assert calls==['run_kruskal']
