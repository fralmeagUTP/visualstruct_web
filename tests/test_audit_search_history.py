"""Successful searches are action history, not reconstruction mutations."""
import pytest
from app.services.structure_service import StructureService
@pytest.mark.parametrize('structure,search',[('linked_list','buscar_elemento'),('circular_list','buscar_posiciones')])
def test_search_history_retains_order_and_skips_search_reexecution(monkeypatch,structure,search):
 cls=StructureService.get_structure(structure)['adapter'];original=cls.execute;calls=[]
 def observed(self,operation,payload):calls.append((operation,dict(payload)));return original(self,operation,payload)
 monkeypatch.setattr(cls,'execute',observed);history=[]
 for value in [7,7,9]:
  result=StructureService.execute_operation(structure,'insertar_final',{'value':value},history);assert result['success'];history=result['history']
 for value,expected in [(7,[1,2]),(7,[1,2]),(99,[])]:
  calls.clear();result=StructureService.execute_operation(structure,search,{'value':value},history);assert result['success'] and result['result']==expected;assert sum(op==search for op,p in calls)==1;history=result['history']
 assert [row['operation'] for row in history]==['insertar_final']*3+[search]*3
 calls.clear();model=StructureService.get_view_model(structure,history);assert model['history']==history;assert [op for op,p in calls]==['insertar_final']*3;assert [x['value'] for x in model['visual_state']['items']]==[7,7,9]
 failure=StructureService.execute_operation(structure,search,{'value':'abc'},history);assert not failure['success'];assert failure['history']==history;assert failure['visual_state']==model['visual_state']

 calls.clear();invalid=history+[{'operation':search,'payload':{'value':'abc'}},{'operation':search,'payload':{}}];filtered=StructureService.get_view_model(structure,invalid);assert filtered['history']==history;assert all(op!=search for op,payload in calls)
