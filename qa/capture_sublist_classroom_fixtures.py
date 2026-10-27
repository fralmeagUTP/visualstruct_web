"""Real query snapshots for compact Sublist renderer regression tests."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.structure_service import StructureService
history=[{'operation':'insertar_padre','payload':{'parent':10}},{'operation':'insertar_hijo','payload':{'parent':10,'child':3}},{'operation':'insertar_hijo','payload':{'parent':10,'child':4}}]
result=StructureService.execute_operation(structure_id='sublist',operation_name='hijos_de',payload={'parent':10},history=history)
assert result['success']
frames=[step['state_snapshot'] for step in result['execution_trace']['steps']]
(ROOT/'qa/sublist_classroom_fixtures.json').write_text(json.dumps(frames,ensure_ascii=False))
print('Captured',len(frames),'real Sublist frames')
