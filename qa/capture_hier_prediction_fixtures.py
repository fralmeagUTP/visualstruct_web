"""Real decision frames for each hierarchical structure."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.hierarchical_structure_service import HierarchicalStructureService as H
cases=[]
for kind,values in [('abb',[10,5]),('avl',[30,20,10]),('red_black',[30,20,10]),('binary_heap',[30,20,10])]:
 history=[dict(operation='insertar',payload={'value':value}) for value in values[:-1]]
 result=H.execute_operation(structure_id=kind,operation_name='insertar',payload={'value':values[-1]},history=history)
 assert result['success']
 cases.append(dict(structure=kind,trace=dict(steps=[{'pedagogy':step['pedagogy']} for step in result['execution_trace']['steps']])))
(ROOT/'qa/hier_prediction_fixtures.json').write_text(json.dumps(cases,ensure_ascii=False))
