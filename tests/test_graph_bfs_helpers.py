"""Native BFS allocation/ownership and complete canonical helper event contracts."""
import pytest
from _book_traversal_oracle import CASES,native_cases,recorded_call,compare_native,assert_recorded_instruction_contract

@pytest.fixture(scope='module')
def bfs_helpers(tmp_path_factory):
    return native_cases('bfs',tmp_path_factory.mktemp('canonical-bfs-helpers'),initial_mark=7)

@pytest.mark.parametrize('case',range(10))
def test_bfs_real_helper_instruction_effects(bfs_helpers,case):
    record=CASES[case];marks={vertex:7 for vertex in record['vertices']}
    for run in range(record.get('repeat',1)):
        result,trace=recorded_call('bfs',record,marks)
        compare_native(result,bfs_helpers['rows'][case,run])
        assert_recorded_instruction_contract(result,trace)
        events=result['events']
        assert any(event['function']=='preparar' for event in events)
        if result['status']==0:
            assert any(event['function']=='liberar_trabajo' for event in events)
            assert any(event['function']=='publicar_marcas' for event in events)
        if result['status']==2:
            assert result['graph_after']['marks']==marks
        # The current C uses its own index queue, not a fictitious tad_cola call.
        assert not any((event['function'] or '').startswith('cola_') for event in events)
        marks=result['graph_after']['marks']
