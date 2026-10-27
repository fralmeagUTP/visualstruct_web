"""Real C helper conditions and effects, without reusing Python-model events."""
from pathlib import Path
import pytest
from test_graph_bfs_instruction import case_trace
from _audit_graph_bfs_full_native_observer import observe,CASES

@pytest.fixture(scope='module')
def bfs_helpers(tmp_path_factory):
    out=tmp_path_factory.mktemp('bfs-helpers-parent')/'observed';r=observe(out)
    r['_graph']=(out/'tad_grafo.c').read_text(encoding='utf-8').splitlines();r['_queue']=(out/'tad_cola.c').read_text(encoding='utf-8').splitlines();return r

@pytest.mark.parametrize('case',range(10))
def test_bfs_real_helper_instruction_effects(bfs_helpers,case):
    report=bfs_helpers;c=CASES[case];lastmarks=None
    for run in range(2 if c.get('repeat') else 1):
        trace=case_trace(c,lastmarks);events=[e for e in report['events'] if e['case']==case and e['run']==run]
        projected=[s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase'] not in ['call','scope_exit','caller','operand']]
        assert len(projected)==len(events),(case,run,len(projected),len(events))
        for s,e in zip(projected,events):
            ped=s['pedagogy'];st=ped['memory_state'];ev=ped['instruction_event'];phase={'control':'break','statement':'allocate' if 'malloc' in s['line_text'] else 'statement'}.get(e['phase'],e['phase'])
            assert (ev['function'],ev['phase'])==(e['function'],phase),(s['line_text'],e)
            rows=report['_queue'] if e['function'].startswith('cola_') else report['_graph']
            assert s['line_text'].strip()==rows[e['line']-1].strip()
            assert [n['value'] for n in st['queue_nodes']]==[n['value'] for n in e['queue']]
            assert [(n['vertex'],n['mark']) for n in st['graph_marks']]==[(n['vertex'],n['mark']) for n in e['graph_marks']]
            assert [n['value'] for n in st['result_nodes']]==e['returned_list']
            assert [n['value'] for n in st['successor_nodes']]==e['successors']
            assert (st['allocations'],st['frees'])==(e['allocations'],e['frees'])
            if ped['condition']:assert ped['condition']['result']==bool(e['result'])
            stack=ped['call_stack'];assert stack[-1]['function']==e['function']
            assert stack[-1]['scope_status']==('terminado (retorno)' if phase=='return' else 'activo')
            if phase=='return' and e['function'] in ['cola_desencolar','grafo_marcado_vertice']:assert stack[-1]['return_value']==e['result']
        lastmarks={n['vertex']:n['mark'] for n in events[-1]['graph_marks']}
        print('BFS real helpers',case,run,len(events),'events verified',flush=True)
