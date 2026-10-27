"""Bellman-Ford history repair: no historical dispatch, exact repeated successes, failures and mark isolation."""
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
def test_repeated_successes_reload_without_dispatch(end,monkeypatch):
 h=build();calls=[];old=GraphAdapter.execute
 def spy(self,op,p):
  if op=='run_bellman_ford':calls.append(copy.deepcopy(p))
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 for n in range(3):
  d=S.execute_operation('graph','run_bellman_ford',{'start':1,'end':end},h);assert d['success'];h=d['history'];assert sum(x['operation']=='run_bellman_ford' for x in h)==n+1
  for _ in range(2):
   view=S.get_view_model('graph',h);assert view['history']==h
   assert all('mark_effect' not in x for x in h if x['operation']=='run_bellman_ford')
 assert calls==[{'start':1,'end':end}]*3
@pytest.mark.parametrize('payload',[{'start':999,'end':2},{'start':1},{'start':'bad','end':2},{'start':1,'end':'bad'}])
def test_failures_do_not_append(payload):
 h=S.execute_operation('graph','run_bellman_ford',{'start':1,'end':2},build())['history'];old=copy.deepcopy(h)
 d=S.execute_operation('graph','run_bellman_ford',payload,h);assert not d['success'];assert d['history']==old;assert S.get_view_model('graph',d['history'])['history']==old

def test_negative_mutation_and_cycle_preserve_successful_queries():
 h=S.execute_operation('graph','run_bellman_ford',{'start':1,'end':2},build())['history']
 h=S.execute_operation('graph','insert_edge',{'origin':2,'target':1,'weight':-4},h)['history']
 d=S.execute_operation('graph','run_bellman_ford',{'start':1,'end':2},h)
 assert not d['success'] and d['result']['has_negative_cycle']
 assert d['history']==h
 assert sum(x['operation']=='run_bellman_ford' for x in d['history'])==1
 assert S.get_view_model('graph',d['history'])['history']==d['history']

def test_shared_mark_effects_survive_nonmarking_queries(monkeypatch):
 h=build();d=S.execute_operation('graph','run_dfs',{'start':1},h);assert [n['marked'] for n in d['visual_state']['nodes']]==[1,1];h=d['history'];calls=[];old=GraphAdapter.execute
 def spy(self,op,p):
  if op in ['run_bfs','run_dfs','run_bellman_ford']:calls.append(op)
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 for _ in range(2):
  d=S.execute_operation('graph','run_bellman_ford',{'start':1,'end':2},h);assert d['success'];assert [n['marked'] for n in d['visual_state']['nodes']]==[1,1];h=d['history']
  for _ in range(2):assert [n['marked'] for n in S.get_view_model('graph',h)['visual_state']['nodes']]==[1,1]
 d=S.execute_operation('graph','run_dfs',{'start':2},h);assert [n['marked'] for n in d['execution_trace']['steps'][0]['state_snapshot']['nodes']]==[1,1]
 assert {n['id']:n['marked'] for n in S.get_view_model('graph',d['history'])['visual_state']['nodes']}=={'1':0,'2':1};assert calls==['run_bellman_ford','run_bellman_ford','run_dfs']
