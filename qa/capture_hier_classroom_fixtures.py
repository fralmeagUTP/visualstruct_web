"""Capture ABB insertion frames for classroom renderer checks."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.hierarchical_structure_service import HierarchicalStructureService
result=HierarchicalStructureService.execute_operation(structure_id='abb',operation_name='insertar',payload={'value':5},history=[])
assert result['success']
(ROOT/'qa/hier_classroom_fixtures.json').write_text(json.dumps(result['execution_trace']['steps'],ensure_ascii=False))
history=[dict(operation='insertar',payload={'value':value}) for value in [10,5,15,12,18]]
result=HierarchicalStructureService.execute_operation(structure_id='abb',operation_name='eliminar',payload={'value':10},history=history)
assert result['success']
(ROOT/'qa/hier_delete_classroom_fixtures.json').write_text(json.dumps(result['execution_trace']['steps'],ensure_ascii=False))
result=HierarchicalStructureService.execute_operation(structure_id='red_black',operation_name='insertar',payload={'value':1},history=[dict(operation='insertar',payload={'value':value}) for value in [10,5,15]])
(ROOT/'qa/rn_classroom_fixture.json').write_text(json.dumps(result['execution_trace']['steps'][-1]['state_snapshot'],ensure_ascii=False))
result=HierarchicalStructureService.execute_operation(structure_id='binary_heap',operation_name='a_lista',payload={},history=history)
(ROOT/'qa/heap_classroom_fixtures.json').write_text(json.dumps(result['execution_trace']['steps'],ensure_ascii=False))
