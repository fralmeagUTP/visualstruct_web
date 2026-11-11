"""Current30/boundary31 and trusted legacy history; no C semantics altered."""
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
    ('insert_vertex',{'vertex':31}),('insert_edge',{'origin':30,'target':31,'weight':1}),
    ('insert_edge',{'origin':31,'target':31,'weight':1}),
    ('insert_edge',{'origin':31,'target':32,'weight':1}),
    ('generate_random_graph',{'vertices_count':31})])
def test_31_HTTP_rejection_preserves_entire_state_history_seed_and_zero_C(private_client,operation,payload):
    h=history(30);seed(private_client,h);before=S.get_view_model('graph',h)['visual_state'];original=deepcopy(payload)
    response=private_client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})
    assert response.status_code==400;data=response.get_json();assert '30' in data['message']
    assert data['visual_state']==before and data['history']==h and stored(private_client)==h
    assert payload==original and 'seed' not in payload
    trace=expand_graph_trace(data['execution_trace']);assert not trace['execution_started'] and trace['C_instruction_events']==[]
    assert all(not step['pedagogy'].get('instruction_event',{}).get('C_executed',False) for step in trace['steps'])

@pytest.mark.parametrize('operation,payload',[
    ('insert_vertex',{'vertex':2147483647}),
    ('insert_edge',{'origin':29,'target':2147483647,'weight':1}),
    ('insert_edge',{'origin':2147483647,'target':2147483647,'weight':1})])
def test_thirtieth_vertex_admission_count_is_not_identifier_range(private_client,operation,payload):
    from app.domain.graph.educational_capacity import check_capacity
    from app.adapters.base_adapter import BaseAdapter
    h=history(29);seed(private_client,h)
    adapter=S._rebuild_adapter('graph',h)[0]
    before=deepcopy(adapter.to_visual_state())
    check_capacity(adapter.graph,operation,payload,adapter._require_vertex,BaseAdapter._require_int)
    assert adapter.to_visual_state()==before and stored(private_client)==h


def test_generator30_admitted_31_rejected_validation_without_generation():
    from app.domain.graph.educational_capacity import check_capacity
    from app.adapters.base_adapter import BaseAdapter
    a=GraphAdapter();payload={'vertices_count':30,'seed':123};before=deepcopy(a.to_visual_state())
    check_capacity(a.graph,'generate_random_graph',payload,a._require_vertex,BaseAdapter._require_int)
    assert a.to_visual_state()==before
    rejected={'vertices_count':31}
    with pytest.raises(GraphCapacityError):a.execute('generate_random_graph',rejected)
    assert a.to_visual_state()==before and rejected=={'vertices_count':31}


def test_legacy31_reloads_reads_and_downloads_without_truncation_then_reduces(private_client):
    h=history(31,legacy=True);seed(private_client,h)
    _assert_legacy_suspended(private_client,h)


def _assert_legacy_suspended(client,h):
    model=S.get_view_model('graph',h)
    assert model['history']==h
    assert 'suspendido' in S.history_issue(h)
    assert not model['visual_state'].get('nodes')
    assert client.get('/graph/graph/construccion').status_code==200
    assert stored(client)==h
    for operation,payload in [('list_vertices',{}),('run_bfs',{'start':1}),('remove_vertex',{'vertex':31})]:
        response=client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})
        assert response.status_code==400
        assert response.get_json()['history']==h and stored(client)==h
        assert response.get_json()['execution_trace'] is None
    # No canonical main may silently claim to reconstruct the suspended graph.
    main=client.get('/help/source/graph/main')
    assert main.status_code==409
    assert 'grafo_insertar_vertice(g,' not in main.get_data(as_text=True)
    assert stored(client)==h


def test_comparator31_rejects_before_copying_graph():
    graph=S.get_view_model('graph',history(31))['visual_state']
    with pytest.raises(ValueError,match='30'):S.compare_algorithms('bfs-dfs',graph,start=1)


def test_legacy_seeded_generator31_retains_every_node_and_complete_main(private_client):
    h=[{'operation':'generate_random_graph','payload':{'vertices_count':31,'seed':32}}]
    seed(private_client,h);_assert_legacy_suspended(private_client,h)


def test_capacity_metadata_and_help_use_current30():
    from app.services.graph_help_service import GraphHelpService
    assert MAX_VERTICES==30
    model=S.get_view_model('graph',history(8))
    assert model['max_vertices']==30
    generator=next(o for o in model['operations'] if o['name']=='generate_random_graph')
    assert '30' in generator['inputs'][0]['label']
    assert '30 vértices' in GraphHelpService._MODULE_HELP['tips'][0]
    assert 'históricos de otro contrato' in GraphHelpService._MODULE_HELP['tips'][0]


def test_thirtieth_vertex_actually_executes_in_normal_mode(private_client):
    h=history(29);seed(private_client,h)
    response=private_client.post('/graph/graph/operate',json={'operation':'insert_vertex','payload':{'vertex':30},'execution_mode':'normal'})
    assert response.status_code==200
    data=response.get_json()
    assert len(data['visual_state']['nodes'])==30
    assert len(stored(private_client))==len(h)+1


def test_comparison_accepts_30_and_more_than_300_edges_before_execution(monkeypatch):
    from app.domain.graph.educational_capacity import MAX_COMPARISON_EDGES
    assert MAX_COMPARISON_EDGES==900
    class ExecutionReached(Exception):pass
    monkeypatch.setattr(GraphAdapter,'execute',lambda *args,**kwargs:(_ for _ in ()).throw(ExecutionReached()))
    graph={'nodes':[{'id':i} for i in range(30)],'edges':[{'source':i,'target':j,'weight':1} for i in range(30) for j in range(i+1,30)]}
    with pytest.raises(ExecutionReached):S.compare_algorithms('bfs-dfs',graph,start=0)
    graph['edges']=[{'source':0,'target':1,'weight':1}]*901
    with pytest.raises(ValueError,match='900'):S.compare_algorithms('bfs-dfs',graph,start=0)
