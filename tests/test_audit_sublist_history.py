from app.services.structure_service import StructureService

def test_sublist_query_history_reload_avoids_reexecution_and_filters_invalid_queries(monkeypatch):
 cls=StructureService.get_structure('sublist')['adapter'];old=cls.execute;calls=[]
 def observed(self,op,payload):calls.append(op);return old(self,op,payload)
 monkeypatch.setattr(cls,'execute',observed);history=[]
 for op,payload in [('insertar_padre',{'parent':7}),('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3}),('insertar_hijo',{'parent':7,'child':3})]:
  result=StructureService.execute_operation('sublist',op,payload,history);assert result['success'];history=result['history']
 for _ in range(2):
  calls.clear();result=StructureService.execute_operation('sublist','hijos_de',{'parent':7},history);assert result['success'] and result['result']==[3,3];assert calls.count('hijos_de')==1;history=result['history']
 calls.clear();model=StructureService.get_view_model('sublist',history);assert model['history']==history and 'hijos_de' not in calls
 bad=history+[{'operation':'hijos_de','payload':{'parent':'abc'}},{'operation':'hijos_de','payload':{}}];assert StructureService.get_view_model('sublist',bad)['history']==history
 for payload in [{'parent':99},{'parent':'abc'},{}]:
  failure=StructureService.execute_operation('sublist','hijos_de',payload,history);assert not failure['success'] and failure['history']==history
 assert model['visual_state']['items'][0]['children']==[3,3]
