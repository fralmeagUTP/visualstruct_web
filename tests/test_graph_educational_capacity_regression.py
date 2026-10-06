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


def history(count):
    return [{'operation':'create_graph','payload':{'directed':False}},
        *[{'operation':'insert_vertex','payload':{'vertex':v}} for v in range(1,count+1)]]

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
    h=history(16);seed(private_client,h);before=S.get_view_model('graph',h)
    assert len(before['visual_state']['nodes'])==16 and before['history']==h
    page=private_client.get('/graph/graph/construccion');assert page.status_code==200
    assert stored(private_client)==h
    main=private_client.get('/help/source/graph/main');assert main.status_code==200
    assert main.data.decode('utf-8')==before['main_c']
    query=private_client.post('/graph/graph/operate',json={'operation':'list_vertices','payload':{}})
    assert query.status_code==200 and query.get_json()['history']==h
    old=S.get_view_model('graph',h)['visual_state']
    denied=private_client.post('/graph/graph/operate',json={'operation':'run_bfs','payload':{'start':1}})
    assert denied.status_code==400 and denied.get_json()['visual_state']==old and stored(private_client)==h
    removed=private_client.post('/graph/graph/operate',json={'operation':'remove_vertex','payload':{'vertex':16}})
    assert removed.status_code==200 and len(removed.get_json()['visual_state']['nodes'])==15
    now=removed.get_json()['history'];assert now[:len(h)]==h and stored(private_client)==now
    assert S._rebuild_adapter('graph',now)[0]._enforce_educational_limit is True


def test_comparator16_rejects_before_copying_graph():
    graph=S.get_view_model('graph',history(16))['visual_state']
    with pytest.raises(ValueError,match='15'):S.compare_algorithms('bfs-dfs',graph,start=1)


def test_legacy_seeded_generator31_retains_every_node_and_complete_main(private_client):
    h=[{'operation':'generate_random_graph','payload':{'vertices_count':16,'seed':17}}]
    seed(private_client,h);model=S.get_view_model('graph',h)
    assert len(model['visual_state']['nodes'])==16 and model['history']==h
    response=private_client.get('/help/source/graph/main');assert response.status_code==200
    assert response.data.decode('utf-8')==model['main_c']
    assert model['main_c'].count('g = grafo_insertar_vertice(g, ')==16
    assert stored(private_client)==h


def test_capacity_metadata_and_help_use_current15():
    from app.services.graph_help_service import GraphHelpService
    assert MAX_VERTICES==15
    model=S.get_view_model('graph',history(8))
    assert model['max_vertices']==15
    generator=next(o for o in model['operations'] if o['name']=='generate_random_graph')
    assert '15' in generator['inputs'][0]['label']
    assert '15 vertices' in GraphHelpService._MODULE_HELP['tips'][0]
    assert 'superen15' in GraphHelpService._MODULE_HELP['tips'][0]
