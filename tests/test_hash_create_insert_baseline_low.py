"""Live regressions: approved Hash H1 baseline; no xfail."""
import pytest
from app import create_app
@pytest.fixture
def client():
    app=create_app();app.config.update(TESTING=True)
    return app.test_client()
def create(client):
    return client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}}).get_json()
def test_hash_successful_creation_never_executes_allocation_error_branch(client):
    data=create(client)
    assert data['success']
    assert not any('tabla->capacidad = 0' in frame['line_text'] for frame in data['execution_trace']['steps'])
def test_hash_creation_pedagogy_uses_requested_capacity(client):
    data=create(client)
    assert data['execution_trace']['steps'][-1]['pedagogy']['hash']['capacity']==3
def test_hash_collision_load_above_one_preserves_capacity(client):
    create(client)
    for key in (1,4,7,10):
        data=client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':key,'value':key*10}}).get_json()
        assert data['success']
    metadata=data['visual_state']['metadata']
    assert metadata['capacity']==3
    assert metadata['size']==4
    assert metadata['load_factor']>1
