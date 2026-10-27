"""LOW consolidation checks for actual C parameter values and helper scopes."""
def test_hash_creation_parameter_not_overwritten_by_struct_capacity(client):
    data=client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}}).get_json()
    frame=next(f for f in data['execution_trace']['steps'] if f['event_type']=='init_entry')
    assert frame['debug']['variables']['capacidad']['value']==3
    assert frame['debug']['root']['capacity']==0
    assert frame['pedagogy']['variables']['capacidad']==3

def test_hash_index_helper_has_const_scoped_table_parameter(client):
    client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
    data=client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':-1,'value':10}}).get_json()
    frame=next(f for f in data['execution_trace']['steps'] if f['event_type']=='index_entry')
    assert 'const TablaHash *tabla' in data['execution_trace']['source_code']
    assert frame['debug']['call_stack']==['th_insertar','th_indice']
    parameter=frame['debug']['variables']['th_indice.tabla']
    assert parameter=={'type':'const TablaHash *','initialized':True,'value':'&tabla'}
