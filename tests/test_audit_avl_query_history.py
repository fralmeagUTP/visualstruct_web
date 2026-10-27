"""Successful queries persist, while reconstruction does not dispatch queries."""
from collections import Counter
from unittest.mock import patch
import pytest
from app.adapters.avl_adapter import AVLAdapter
from app.services.hierarchical_structure_service import HierarchicalStructureService

@pytest.mark.parametrize('operation,payload,expected',[('buscar',{'value':'0005'},True),('minimo',{},5),('maximo',{},15),('altura',{},2),('inorden',{},[5,10,15]),('validar',{},True)])
def test_avl_queries_repeat_reload_and_failures_do_not_reexecute(client,operation,payload,expected):
 for v in [10,5,15]:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 original=AVLAdapter.execute;counts=Counter()
 def observe(adapter,name,data):
  counts[name]+=1;return original(adapter,name,data)
 with patch.object(AVLAdapter,'execute',autospec=True,side_effect=observe):
  for count in [1,2]:
   data=client.post('/hierarchical/avl/operate',json={'operation':operation,'payload':payload}).json
   assert data['success'] and data['result']==expected and counts[operation]==count
   assert [h for h in data['history'] if h['operation']==operation]==[{'operation':operation,'payload':payload}]*count
  assert client.get('/hierarchical/avl').status_code==200 and counts[operation]==2
  failed=client.post('/hierarchical/avl/operate',json={'operation':'eliminar','payload':{'value':99}})
  assert failed.status_code==400 and not failed.json['success'] and counts[operation]==2 and len(failed.json['history'])==5
  malformed=client.post('/hierarchical/avl/operate',json={'operation':'buscar','payload':{'value':'bad'}})
  assert malformed.status_code==400 and len(malformed.json['history'])==5
  before=counts[operation];third=client.post('/hierarchical/avl/operate',json={'operation':operation,'payload':payload}).json
  assert third['success'] and third['result']==expected and counts[operation]==before+1 and len(third['history'])==6

def test_avl_empty_extrema_and_malformed_stored_query_not_executed(client):
 for operation in ['minimo','maximo']:
  response=client.post('/hierarchical/avl/operate',json={'operation':operation,'payload':{}})
  assert response.status_code==400 and not response.json['success'] and response.json['history']==[]
 with patch.object(AVLAdapter,'execute',autospec=True) as execute:
  adapter,history=HierarchicalStructureService._rebuild_adapter('avl',[{'operation':'buscar','payload':{'value':'bad'}},{'operation':'altura','payload':{}}])
  assert history==[{'operation':'altura','payload':{}}] and adapter.to_visual_state()['root'] is None
  execute.assert_not_called()

def test_avl_guide_explains_main_helpers_and_reload_contract(client):
 text=client.get('/help/hierarchical/avl').data.decode('utf-8')
 assert 'recargar conserva esas consultas sin ejecutarlas otra vez' in text and 'no son exportaciones del C/H descargable' in text and 'no certifica el FE almacenado' in text
