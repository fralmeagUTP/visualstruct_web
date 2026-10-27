"""Current15/boundary16 and trusted legacy history; no C semantics altered."""
from copy import deepcopy
import pytest
from app import create_app
from app.config import Config
from app.adapters.graph_adapter import GraphAdapter
from app.services.graph_structure_service import GraphStructureService as S
from app.services.session_service import SESSION_KEY
from app.domain.graph.educational_capacity import MAX_VERTICES,GraphCapacityError
from app.domain.graph.snapshot_pool import expand_graph_trace


def history(count, *, legacy=False):
    records=[{'operation':'create_graph','payload':{'directed':False}},
        *[{'operation':'insert_vertex','payload':{'vertex':v}} for v in range(1,count+1)]]
    return records if legacy else [dict(record, source_contract='graph-book/v1') for record in records]

@pytest.fixture
def private_client(tmp_path):
    class PrivateConfig(Config):
        TESTING=True;SECRET_KEY='capacity-private';SESSION_CACHE_DIR=str(tmp_path/'sessions')
    return create_app(PrivateConfig).test_client()

def seed(client,h):
    with client.session_transaction() as session:session[SESSION_KEY]={'graph::graph':h}

def stored(client):
    with client.session_transaction() as session:
        record=session[SESSION_KEY]['graph::graph']
        return deepcopy(record['history'] if isinstance(record,dict) else record)

@pytest.mark.parametrize('operation,payload',[
    ('insert_vertex',{'vertex':16}),('insert_edge',{'origin':15,'target':16,'weight':1}),
    ('insert_edge',{'origin':16,'target':16,'weight':1}),
    ('insert_edge',{'origin':16,'target':17,'weight':1}),
    ('generate_random_graph',{'vertices_count':16})])
def test_16_HTTP_rejection_preserves_entire_state_history_seed_and_zero_C(private_client,operation,payload):
    h=history(15);seed(private_client,h);before=S.get_view_model('graph',h)['visual_state'];original=deepcopy(payload)
    response=private_client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})
    assert response.status_code==400;data=response.get_json();assert '15' in data['message']
    assert data['visual_state']==before and data['history']==h and stored(private_client)==h
    assert payload==original and 'seed' not in payload
    trace=expand_graph_trace(data['execution_trace']);assert not trace['execution_started'] and trace['C_instruction_events']==[]
    assert all(not step['pedagogy'].get('instruction_event',{}).get('C_executed',False) for step in trace['steps'])

@pytest.mark.parametrize('operation,payload',[
    ('insert_vertex',{'vertex':2147483647}),
    ('insert_edge',{'origin':14,'target':2147483647,'weight':1}),
    ('insert_edge',{'origin':2147483647,'target':2147483647,'weight':1})])
def test_fifteenth_vertex_admission_count_is_not_identifier_range(private_client,operation,payload):
    from app.domain.graph.educational_capacity import check_capacity
    from app.adapters.base_adapter import BaseAdapter
    h=history(14);seed(private_client,h)
    adapter=S._rebuild_adapter('graph',h)[0]
    before=deepcopy(adapter.to_visual_state())
    check_capacity(adapter.graph,operation,payload,adapter._require_vertex,BaseAdapter._require_int)
    assert adapter.to_visual_state()==before and stored(private_client)==h


def test_generator15_admitted_16_rejected_validation_without_generation():
    from app.domain.graph.educational_capacity import check_capacity
    from app.adapters.base_adapter import BaseAdapter
    a=GraphAdapter();payload={'vertices_count':15,'seed':123};before=deepcopy(a.to_visual_state())
    check_capacity(a.graph,'generate_random_graph',payload,a._require_vertex,BaseAdapter._require_int)
    assert a.to_visual_state()==before
    rejected={'vertices_count':16}
    with pytest.raises(GraphCapacityError):a.execute('generate_random_graph',rejected)
    assert a.to_visual_state()==before and rejected=={'vertices_count':16}


def test_legacy16_reloads_reads_and_downloads_without_truncation_then_reduces(private_client):
    h=history(16,legacy=True);seed(private_client,h)
    _assert_legacy_suspended(private_client,h)


def _assert_legacy_suspended(client,h):
    model=S.get_view_model('graph',h)
    assert model['history']==h
    assert 'suspendido' in S.history_issue(h)
    assert not model['visual_state'].get('nodes')
    assert client.get('/graph/graph/construccion').status_code==200
    assert stored(client)==h
    for operation,payload in [('list_vertices',{}),('run_bfs',{'start':1}),('remove_vertex',{'vertex':16})]:
        response=client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})
        assert response.status_code==400
        assert response.get_json()['history']==h and stored(client)==h
        assert response.get_json()['execution_trace'] is None
    # No canonical main may silently claim to reconstruct the suspended graph.
    main=client.get('/help/source/graph/main')
    assert main.status_code==409
    assert 'grafo_insertar_vertice(g,' not in main.get_data(as_text=True)
    assert stored(client)==h


def test_comparator16_rejects_before_copying_graph():
    graph=S.get_view_model('graph',history(16))['visual_state']
    with pytest.raises(ValueError,match='15'):S.compare_algorithms('bfs-dfs',graph,start=1)


def test_legacy_seeded_generator31_retains_every_node_and_complete_main(private_client):
    h=[{'operation':'generate_random_graph','payload':{'vertices_count':16,'seed':17}}]
    seed(private_client,h);_assert_legacy_suspended(private_client,h)


def test_capacity_metadata_and_help_use_current15():
    from app.services.graph_help_service import GraphHelpService
    assert MAX_VERTICES==15
    model=S.get_view_model('graph',history(8))
    assert model['max_vertices']==15
    generator=next(o for o in model['operations'] if o['name']=='generate_random_graph')
    assert '15' in generator['inputs'][0]['label']
    assert '15 vértices' in GraphHelpService._MODULE_HELP['tips'][0]
    assert 'históricos de otro contrato' in GraphHelpService._MODULE_HELP['tips'][0]
