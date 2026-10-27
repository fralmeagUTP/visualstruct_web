"""Successful leaf history survives reload without being reexecuted."""
from unittest.mock import patch
import pytest
from app.domain.hierarchical import tad_wrappers

@pytest.mark.parametrize('seed,expected',[([],0),([7],1),([10,5,15,3,7,12,18],4)])
def test_leaf_history_repeats_persist_and_rebuild_does_not_execute_queries(client,seed,expected):
 for value in seed:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 original=tad_wrappers.ABB.contar_hojas
 with patch.object(tad_wrappers.ABB,'contar_hojas',autospec=True,side_effect=original) as observed:
  for count in range(1,4):
   data=client.post('/hierarchical/abb/operate',json={'operation':'contar_hojas','payload':{}}).json
   assert data['success'] and data['result']==expected and observed.call_count==count
   assert len([x for x in data['history'] if x['operation']=='contar_hojas'])==count
  assert client.get('/hierarchical/abb').status_code==200 and observed.call_count==3
  failed=client.post('/hierarchical/abb/operate',json={'operation':'eliminar','payload':{'value':99}})
  assert failed.status_code==400 and not failed.json['success'] and observed.call_count==3
  assert len(failed.json['history'])==len(seed)+3
  fourth=client.post('/hierarchical/abb/operate',json={'operation':'contar_hojas','payload':{}}).json
  assert fourth['success'] and fourth['result']==expected and observed.call_count==4
  assert len(fourth['history'])==len(seed)+4
