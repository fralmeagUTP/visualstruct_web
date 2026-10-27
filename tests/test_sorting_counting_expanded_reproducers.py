"""Reproducers for admitted Counting inputs outside fixture cutoff; no weakening."""
import pytest
from app import create_app
@pytest.mark.parametrize('values',[[5,4,3,2,1],[0,5],[0,16,8,0,16,4,12,8],[2]*80,[0,1000]])
def test_admitted_counting_input_has_instruction_fidelity(values):
    c=create_app().test_client();assert c.post('/api/ordenamiento/create-array',json={'values':values}).get_json()['success']
    d=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'}).get_json();assert d['success'] and d['visual_state']['items']==sorted(values)
    trace=d['execution_trace']
    if trace.get('schema')=='counting-paged-trace/v1':
        assert trace['step_count']>0 and trace['manifest']['lossless'] and trace['manifest']['page_url']
        first=c.get(trace['manifest']['page_url']+'?start=0&limit=64').get_json()['steps'];last=c.get(trace['manifest']['page_url']+f"?start={trace['step_count']-2}&limit=2").get_json()['steps']
        assert all('instruction_event' in frame['debug'] for frame in first+last)
        assert any(any(f['function']=='obtener_minimo_maximo' for f in frame['pedagogy']['call_stack']) for frame in first)
        assert any(frame['state_after']['trace_token']=='count_free' for frame in last)
    else:
        assert all('instruction_event' in s['debug'] for s in trace['steps'])
        assert any(any(f['function']=='obtener_minimo_maximo' for f in s['pedagogy']['call_stack']) for s in trace['steps'])
        assert any(s['state_after']['trace_token']=='count_free' for s in trace['steps'])
