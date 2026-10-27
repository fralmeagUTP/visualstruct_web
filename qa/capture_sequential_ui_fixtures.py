"""Capture real frames for classroom layout/help/stdout regression tests."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.services.structure_service import StructureService
cases = []
for kind, operation, payload, history in [
    ('stack', 'apilar', {'value': 3}, [{'operation': 'apilar', 'payload': {'value': 7}}]),
    ('stack', 'limpiar', {}, [{'operation': 'apilar', 'payload': {'value': 7}}]),
    ('queue', 'desencolar', {}, []),
]:
    result = StructureService.execute_operation(structure_id=kind, operation_name=operation, payload=payload, history=history)
    cases.append(dict(structure=kind, operation=operation, message=result['message'], trace=result.get('execution_trace')))
(ROOT / 'qa/sequential_ui_fixtures.json').write_text(json.dumps(cases, ensure_ascii=False))
print('Captured', sum(len(case['trace']['steps']) for case in cases), 'real sequential frames')
