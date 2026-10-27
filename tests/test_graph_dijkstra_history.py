"""Canonical graph-book/v1 replay, retained C failures and mark isolation."""
import copy
import pytest
from app.adapters.graph_adapter import GraphAdapter
from app.services.graph_structure_service import GraphStructureService as S
BASE=[('create_graph',{'directed':True}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':1,'target':2,'weight':3})]
def build():
 h=[]
 for op,p in BASE:
  d=S.execute_operation('graph',op,copy.deepcopy(p),h);assert d['success'];h=d['history']
 return h
@pytest.mark.parametrize('end',[1,2,999])
def test_repeated_successes_reload_with_canonical_replay(end,monkeypatch):
 h=build();calls=[];old=GraphAdapter.execute
 def spy(self,op,p):
  if op=='run_dijkstra':calls.append(copy.deepcopy(p))
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 for n in range(3):
  d=S.execute_operation('graph','run_dijkstra',{'start':1,'end':end},h);assert d['success'] is (end != 999);assert d.get('c_status') == (2 if end==999 else 0);h=d['history'];assert sum(x['operation']=='run_dijkstra' for x in h)==n+1
  for _ in range(2):
   view=S.get_view_model('graph',h);assert view['history']==h
   assert all('mark_effect' not in x for x in h if x['operation']=='run_dijkstra')
 assert len(calls)>3 and all(p=={'start':1,'end':end} for p in calls)
@pytest.mark.parametrize('payload',[{'start':999,'end':2},{'start':1},{'start':'bad','end':2},{'start':1,'end':'bad'}])
def test_c_failures_retained_and_host_rejections_do_not_append(payload):
 h=S.execute_operation('graph','run_dijkstra',{'start':1,'end':2},build())['history'];old=copy.deepcopy(h)
 d=S.execute_operation('graph','run_dijkstra',payload,h);assert not d['success'];expected=old if payload.get('start')!=999 else old+[d['history'][-1]];assert d['history']==expected;assert S.get_view_model('graph',d['history'])['history']==expected

def test_negative_mutation_preserves_past_success_only():
 h=S.execute_operation('graph','run_dijkstra',{'start':1,'end':2},build())['history']
 h=S.execute_operation('graph','insert_edge',{'origin':2,'target':1,'weight':-1},h)['history'];before=copy.deepcopy(h)
 d=S.execute_operation('graph','run_dijkstra',{'start':1,'end':2},h);assert not d['success'];assert d['history'][:-1]==before and d['c_status']==3
 view=S.get_view_model('graph',h);assert view['history']==before;assert sum(x['operation']=='run_dijkstra' for x in view['history'])==1
 assert [x['weight'] for x in view['visual_state']['edges'] if x['source']=='2' and x['target']=='1']==[-1]

def test_shared_mark_effects_survive_nonmarking_queries(monkeypatch):
 h=build();d=S.execute_operation('graph','run_dfs',{'start':1},h);assert [n['marked'] for n in d['visual_state']['nodes']]==[1,1];h=d['history'];calls=[];old=GraphAdapter.execute
 def spy(self,op,p):
  if op in ['run_bfs','run_dfs','run_dijkstra']:calls.append(op)
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 for _ in range(2):
  d=S.execute_operation('graph','run_dijkstra',{'start':1,'end':2},h);assert d['success'];assert [n['marked'] for n in d['visual_state']['nodes']]==[1,1];h=d['history']
  for _ in range(2):assert [n['marked'] for n in S.get_view_model('graph',h)['visual_state']['nodes']]==[1,1]
 d=S.execute_operation('graph','run_dfs',{'start':2},h);assert [n['marked'] for n in d['execution_trace']['steps'][0]['state_snapshot']['nodes']]==[1,1]
 assert {n['id']:n['marked'] for n in S.get_view_model('graph',d['history'])['visual_state']['nodes']}=={'1':0,'2':1};assert calls.count('run_dijkstra')>2 and calls.count('run_dfs')>1
