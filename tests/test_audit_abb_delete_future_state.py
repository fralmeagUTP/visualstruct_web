"""Focused negative regression: child entry cannot contain its future deletion."""
import json,os,sys
from pathlib import Path
r=Path(r'D:\MisProyectos\Web_VisualEstruct');sys.path.insert(0,str(r))
from app import create_app

from scripts.published_test_inputs import audit_input_path
def test_recursive_child_entry_preserves_native_pre_call_successor():
 review=json.loads((audit_input_path(Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-abb-delete-baseline-low/abb-delete-native-low/review.json')).read_text(encoding='utf-8'))
 meta=review['cases'][8]
 client=create_app().test_client()
 for value in meta['seed']:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 data=client.post('/hierarchical/abb/operate',json={'operation':'eliminar','payload':meta['payload']}).json
 assert data['success']
 line='nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);'
 event=next(row['native'] for row in review['rows'] if row['native']['case']==8 and row['native']['phase']=='call' and row['source_line']==line)
 nodes={n['id']:n for n in event['nodes']}
 def tree(identity):
  if not identity:return None
  n=nodes[identity];return {'value':n['value'],'left':tree(n['left']),'right':tree(n['right'])}
 steps=data['execution_trace']['steps'];index=next(i for i,s in enumerate(steps) if s['line_text'].strip()==line)
 child=steps[index+1];assert child['line_text'].strip()=='ABBNodo* abb_eliminar(ABBNodo* nodo, int valor) {'
 assert child['state_snapshot']['root']==tree(event['root']), 'Child entry leaks future successor deletion before its instructions execute'
