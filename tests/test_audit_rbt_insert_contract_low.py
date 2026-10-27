"""Signed int insertion rejection and final caller ownership are actual product contracts."""
from pathlib import Path
import pytest
from _application_rejection_contract import assert_unexecuted_input_rejection
from app.adapters.red_black_adapter import RedBlackAdapter
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from app.services.hierarchical_help_service import HierarchicalHelpService as H

@pytest.mark.parametrize('value',[-2147483649,2147483648,str(-2147483649),str(2147483648),10**30,-10**30])
def test_insert_outside_C_int_rejects_before_mutation_history_or_C(value):
 a=RedBlackAdapter();a.execute('insertar',{'value':10});before=a.to_visual_state()
 with pytest.raises(ValueError,match='-2147483648.*2147483647'):a.execute('insertar',{'value':value})
 assert a.to_visual_state()==before
 history=[{'operation':'insertar','payload':{'value':10}}];r=S.execute_operation('red_black','insertar',{'value':value},history)
 assert not r['success'] and r['history']==history and r['visual_state']==before
 assert_unexecuted_input_rejection(r)

@pytest.mark.parametrize('value',[-2147483648,2147483647,'-2147483648','+2147483647'])
def test_signed_C_int_bounds_are_preserved_exactly(value):
 r=S.execute_operation('red_black','insertar',{'value':value},[]);assert r['success'] and r['visual_state']['root']['value']==int(value)
 assert r['execution_trace']['steps'][-1]['pedagogy']['memory_state']['heap_nodes'][0]['value']==int(value)
 assert r['history']==[{'operation':'insertar','payload':{'value':value}}]

def test_old_invalid_history_is_excluded_without_truncating_or_redispatching_queries():
 history=[{'operation':'insertar','payload':{'value':10}},{'operation':'insertar','payload':{'value':2147483648}},{'operation':'altura','payload':{}}]
 a,valid=S._rebuild_adapter('red_black',history);assert valid==[history[0],history[2]] and a.to_visual_state()['size']==1 and a.to_visual_state()['root']['value']==10

def test_actual_help_and_manual_explain_range_and_owned_final_cleanup():
 h=H.get_structure_help('red_black');assert '-2147483648' in h['summary'] and '2147483647' in h['summary'] and 'sin truncar' in h['summary'] and 'caller' in h['summary'] and 'NULL' in h['pedagogy']['memory'] and 'sin reservas NIL' in h['pedagogy']['memory']
 manual=(Path(__file__).resolve().parents[1]/'docs/USER_GUIDE.md').read_text(encoding='utf-8');assert 'rbt_liberar(arbol); arbol = NULL;' in manual and '`-2147483648`' in manual and '`2147483647`' in manual
