"""Trace uses raw parents even when the NIL presentation hides their defect."""
from copy import deepcopy
from app.adapters.red_black_adapter import RedBlackAdapter
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from _audit_rbt_full_validator_baseline_low import build,snapshot

def test_rn_invalid_raw_parent_successful_query_and_trace(monkeypatch):
 adapter=RedBlackAdapter()
 for value in [10,5,15]:adapter.execute('insertar',{'value':value})
 root=adapter._structure._root_ref[0];root.izq.padre=None
 raw_nodes=[root,root.izq,root.der];before=snapshot(raw_nodes)
 history=[{'operation':'insertar','payload':{'value':v}} for v in [10,5,15]]
 monkeypatch.setattr(S,'_rebuild_adapter',staticmethod(lambda structure,entries:(adapter,deepcopy(entries))))
 data=S.execute_operation('red_black','validar',{},history)
 assert data['success'] and data['result'] is False
 assert data['history']==history+[{'operation':'validar','payload':{}}]
 assert snapshot(raw_nodes)==before
 steps=data['execution_trace']['steps'];assert steps[-1]['pedagogy']['memory_state']['wrapper_result']==0
 heap=steps[0]['state_snapshot']['heap_nodes'];assert heap[1]['parent']=='NULL'
 assert any('nodo->padre != padreEsperado' in s['line_text'] and s.get('condition_result') is True for s in steps)
 assert not any(f['function']=='rbt_validar_altura_negra' and f['parameters']['nodo']=='N3' for s in steps for f in s['pedagogy']['memory_state']['tree_frames'])
 assert all(not s['pedagogy']['memory']['allocated_objects'] and not s['pedagogy']['memory']['freed_objects'] for s in steps)
