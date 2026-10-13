"""Real query baseline defects under the existing approved H1 contract."""
def test_hash_get_absent_obeys_existing_400_contract(client):
    client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
    response=client.post('/hash/hash_table/operate',json={'operation':'get','payload':{'key':10}})
    assert response.status_code==400
    assert response.get_json()['success'] is False

def test_hash_negative_zero_remainder_skips_normalization(client):
    client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
    client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':-6,'value':60}})
    for op in ['get','contains']:
        data=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{'key':-6}}).get_json()
        assert not any('indice += tabla->capacidad' in f['line_text'] for f in data['execution_trace']['steps'])

def test_hash_queries_expose_instruction_scopes(client):
    for op in ['get','contains']:
        data=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{'key':1}}).get_json()
        assert any(f.get('debug',{}).get('scopes') for f in data['execution_trace']['steps'])
