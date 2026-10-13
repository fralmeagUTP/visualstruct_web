"""Independent retained native observations versus live Hash statement frames."""
from pathlib import Path
import json
import pytest
from app import create_app
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-create-insert-baseline-low/native'
CASES=['create_three','insert_empty','collision_load_gt_one','update_head','update_middle','update_tail','negative_extremes','cap17_collision']

def compare_native(native,frames):
    frames=[f for f in frames if f['event_type']!='caller_recreate']
    native=[n for n in native if n['token']!='initial']
    assert [f['event_type'] for f in frames]==[n['token'] for n in native]
    initial_comps=native[0]['comparisons'];initial_hash=native[0]['hash_calls']
    observed_match = False
    for n,f in zip(native,frames):
        if n['token']=='key_compare' and n['condition']:observed_match=True
        assert f['pedagogy']['chain']['found']==observed_match
        d=f['debug']
        assert d['root']['capacity']==n['capacity'],n['token']
        assert d['root']['size']==n['size'],n['token']
        assert bool(d['root']['bucket_pointer'])==bool(n['bucket_pointer'])
        assert d['bucket_initialization']==[b['initialized'] for b in n['buckets']]
        assert d['condition_result']==n['condition']
        assert d['indice']==n['indice']
        assert d['i']==n['i']
        assert d['return_status']==n['return_status']
        assert d['comparisons']==n['comparisons']-initial_comps
        assert d['hash_calls']==n['hash_calls']-initial_hash
        for metric in ('link_writes','value_writes','key_writes','count_writes','allocations'):
            assert d[metric]==n[metric]-native[0][metric]
        assert d['allocation_attempts']==n['attempts']-native[0]['attempts']
        ids={obj['id']:obj.get('key') for obj in n['heap'] if obj['kind']==2}
        symbols={obj['id']:obj.get('key') for obj in d['heap']}
        for name in ('actual','nuevo'):
            # Identity equality/NULL plus keys; physical pointer bytes are not a contract.
            assert bool(d[name])==bool(n[name])
            if n[name]:assert symbols[d[name]]==ids[n[name]]
        nh=sorted((x['initialized_mask'],x.get('key'),x.get('value'),ids.get(x.get('next'))) for x in n['heap'] if x['kind']==2)
        dh=sorted((x['initialized_mask'],x.get('key'),x.get('value'),symbols.get(x.get('next'))) for x in d['heap'])
        assert dh==nh,n['token']
        nb=[[(x['key'],x['value']) for x in b['chain']] for b in n['buckets']]
        fb=[[(x['key'],x['value']) for x in b['entries']] for b in f['state_after']['buckets']]
        assert nb==fb,n['token']
        assert not f['console']

@pytest.mark.parametrize('case',CASES)
def test_hash_live_statement_frames_match_independent_native(case):
    app=create_app();app.config.update(TESTING=True);client=app.test_client()
    saved=json.loads((BASE/(case+'.json')).read_text(encoding='utf-8'))
    for item in saved['responses']:
        data=client.post('/hash/hash_table/operate',json={'operation':item['operation'],'payload':item['payload']}).get_json()
        assert data['success']
        operation_id=0 if item['operation']=='create_table' else saved['responses'].index(item)
        observations=[n for n in saved['native'] if n['operation']==operation_id]
        compare_native(observations,data['execution_trace']['steps'])
        assert data['visual_state']==item['data']['visual_state']
        assert data['execution_trace']['steps'][-1]['pedagogy']['cost']['comparisons']==item['value_comparisons']
        assert data['execution_trace']['steps'][-1]['pedagogy']['cost']['hash_evaluations']==item['hash_evaluations']

def test_hash_invalid_input_is_public_rejection_not_c_execution():
    app=create_app();app.config.update(TESTING=True);client=app.test_client()
    for op,payload in [('create_table',{'capacity':0}),('insert',{'key':'text','value':1}),('insert',{'key':2147483648,'value':1})]:
        data=client.post('/hash/hash_table/operate',json={'operation':op,'payload':payload}).get_json()
        assert not data['success']
        assert [f['event_type'] for f in data['execution_trace']['steps']]==['input_rejected']
        assert not data['execution_trace']['mutates']

@pytest.mark.parametrize('case,updates',[(20,False),(21,True)])
def test_hash_malloc_null_and_existing_update_match_native(case,updates):
    rows=[json.loads(line) for line in (BASE/'native.jsonl').read_text(encoding='utf-8').splitlines()]
    app=create_app();app.config.update(TESTING=True);client=app.test_client()
    client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
    if updates:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':1,'value':10}})
    response=client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':1,'value':99 if updates else 10,'simulate_allocation_failure':True}})
    data=response.get_json();assert data['success']==updates
    compare_native([r for r in rows if r['case']==case and r['operation']==(2 if updates else 1)],data['execution_trace']['steps'])
    assert all(not frame['console'] for frame in data['execution_trace']['steps'])

def test_hash_download_repeated_calls_reload_and_reset(client):
    for op,p in [('create_table',{'capacity':3}),('insert',{'key':1,'value':10}),('insert',{'key':1,'value':10})]:
        data=client.post('/hash/hash_table/operate',json={'operation':op,'payload':p}).get_json()
        assert data['success']
    response=client.get('/help/source/hash_table/main');assert response.status_code==200
    assert response.data==data['main_c'].encode()
    assert response.data.count(b'th_insertar(&tabla, 1, 10)')==2
    html=client.get('/hash/hash_table').data.decode()
    assert '"execution_trace"' in html and '"hash_calls": 1' in html
    client.post('/hash/hash_table/reset')
    assert '"execution_trace"' not in client.get('/hash/hash_table').data.decode()

def test_hash_unpublished_heap_fields_scopes_and_pending_count(client):
    client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
    data=client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':1,'value':10}}).get_json()
    steps=data['execution_trace']['steps'];by_token={f['event_type']:f for f in steps}
    for token,mask in [('node_allocate',0),('node_key_write',1),('node_value_write',3),('node_next_write',7)]:
        frame=by_token[token]
        assert frame['debug']['heap'][0]['initialized_mask']==mask
        assert not any(b['entries'] for b in frame['state_after']['buckets'])
    assert by_token['index_call']['debug']['variables']['indice']=={'type':'int','initialized':False,'value':None}
    assert by_token['raw_modulo']['debug']['call_stack']==['th_insertar','th_indice']
    assert by_token['insert_return']['debug']['variables']=={}
    published=by_token['head_publish'];assert published['state_after']['metadata']['size']==0
    assert published['pedagogy']['invariant']['count_update_pending']
    assert not published['pedagogy']['invariant']['count_consistent']
    assert by_token['size_increment']['state_after']['metadata']['size']==1
    assert by_token['size_increment']['pedagogy']['invariant']['count_consistent']
