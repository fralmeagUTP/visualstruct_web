"""Small real trace fixtures for presentation-only metadata filtering."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.structure_service import StructureService as S
from app.services.hierarchical_structure_service import HierarchicalStructureService as H
from app.services.graph_structure_service import GraphStructureService as G
from app.services.hash_structure_service import HashStructureService as T
cases=[]
for prefix,kind,service,ops in [
 ('seq','linked_list',S,[('insertar_inicio',{'value':7}),('insertar_final',{'value':3}),('insertar_posicion',{'value':9,'position':2}),('buscar_elemento',{'value':3})]),
 ('hier','abb',H,[('insertar',{'value':7}),('insertar',{'value':3}),('buscar',{'value':3})]),
 ('graph','graph',G,[('create_graph',{'directed':False}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':1,'target':2,'weight':1})]),
 ('hash','hash_table',T,[('create_table',{'capacity':5}),('insert',{'key':7,'value':3}),('get',{'key':7})])]:
 history=[]
 for op,payload in ops:
  r=service.execute_operation(structure_id=kind,operation_name=op,payload=payload,history=history)
  assert r['success'],(kind,op,r['message'])
  trace=r.get('execution_trace') or {}
  frames=[step['pedagogy'] for step in trace.get('steps',[]) if step.get('pedagogy')]
  cases.append(dict(prefix=prefix,structure=kind,operation=op,frames=frames))
  history.append(dict(operation=op,payload=payload))
(ROOT/'qa/contextual_metadata_fixtures.json').write_text(json.dumps(cases,ensure_ascii=False))
print([(c['prefix'],c['operation'],len(c['frames'])) for c in cases])
